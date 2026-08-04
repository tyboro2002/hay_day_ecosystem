// Global State Tracker
const machineInstances = [];
const MACHINE_SETTINGS_KEY = 'hayday_overnight_machine_settings_v1';
let skipNextAutoSave = false;
let currentTabId = 'tab-1h';

/* ==========================================================================
   1. STORAGE & PERSISTENCE HELPERS
   ========================================================================== */

function getSavedMachineSettingsRaw() {
    try {
        const value = localStorage.getItem(MACHINE_SETTINGS_KEY);
        if (value !== null) return value;
    } catch (error) {
        console.warn('localStorage unavailable, falling back to window.name:', error);
    }

    const prefix = MACHINE_SETTINGS_KEY + '=';
    const parts = String(window.name || '').split('\u001f').filter(Boolean);
    const match = parts.find(part => part.startsWith(prefix));
    return match ? match.slice(prefix.length) : null;
}

function setSavedMachineSettingsRaw(rawValue) {
    try {
        localStorage.setItem(MACHINE_SETTINGS_KEY, rawValue);
        return true;
    } catch (error) {
        console.warn('localStorage unavailable, falling back to window.name:', error);
    }

    const prefix = MACHINE_SETTINGS_KEY + '=';
    const parts = String(window.name || '').split('\u001f').filter(part => !part.startsWith(prefix));
    parts.push(prefix + rawValue);
    window.name = parts.join('\u001f');
    return false;
}

function clearSavedMachineSettingsRaw() {
    try {
        localStorage.removeItem(MACHINE_SETTINGS_KEY);
    } catch (error) {
        console.warn('localStorage unavailable, clearing window.name fallback:', error);
    }

    const prefix = MACHINE_SETTINGS_KEY + '=';
    const parts = String(window.name || '').split('\u001f').filter(part => part && !part.startsWith(prefix));
    window.name = parts.join('\u001f');
}

function serializeMachineSettings() {
    return machineInstances.map(m => ({
        id: m.id,
        selected: m.selected,
        slots: m.slots,
        mastery: m.mastery
    }));
}

function getActiveTabId() {
    const activeTab = document.querySelector('.tab-link.active');
    if (!activeTab) return currentTabId;

    const tabOnclick = activeTab.getAttribute('onclick') || '';
    const match = tabOnclick.match(/switchTab\([^,]+,\s*'([^']+)'\)/);
    return match ? match[1] : currentTabId;
}

function serializePortableMachineState() {
    const levelSlider = document.getElementById('overnightLevelRange');

    return {
        version: 1,
        activeTabId: getActiveTabId(),
        machines: serializeMachineSettings(),
        selectedLevel: levelSlider ? parseInt(levelSlider.value || '1', 10) : 1,
    };
}

function saveMachineSettings(silent = false) {
    try {
        const machineState = {
            version: 1,
            activeTabId: getActiveTabId(),
            machines: serializeMachineSettings(),
        };
        setSavedMachineSettingsRaw(JSON.stringify(machineState));
        if (!silent) {
            console.log('Saved machine settings.');
        }
    } catch (error) {
        console.warn('Could not save machine settings:', error);
    }
}

function applyMachineSettings(savedSettings) {
    if (!Array.isArray(savedSettings) || savedSettings.length === 0) return false;

    const settingsMap = new Map(savedSettings.map(entry => [entry.id, entry]));
    let appliedAny = false;

    machineInstances.forEach(state => {
        const saved = settingsMap.get(state.id);
        if (!saved) return;

        state.selected = !!saved.selected;
        state.slots = Math.min(Math.max(parseInt(saved.slots ?? state.slots, 10), state.minSlots), state.maxSlots);
        state.mastery = Math.max(0, Math.min(3, parseInt(saved.mastery ?? state.mastery, 10)));

        state.card.classList.toggle('selected', state.selected);
        state.starsContainer.classList.toggle('disabled-controls', !state.selected);
        state.slotsGrid.classList.toggle('disabled-controls', !state.selected);
        state.renderStars();
        state.renderSlots();
        appliedAny = true;
    });

    return appliedAny;
}

function loadMachineSettings() {
    try {
        const raw = getSavedMachineSettingsRaw();
        if (!raw) return false;

        const applied = applyPortableMachineState(JSON.parse(raw), { applyLevel: false });
        updateStrategyVisibility();
        if (applied) console.log('Loaded machine settings.');
        return applied;
    } catch (error) {
        console.warn('Could not load machine settings:', error);
        return false;
    }
}

function clearMachineSettings() {
    skipNextAutoSave = true;
    try {
        clearSavedMachineSettingsRaw();
    } catch (error) {
        console.warn('Could not clear machine settings:', error);
    }

    window.location.reload();
}

function exportMachineSettings() {
    try {
        const data = JSON.stringify(serializePortableMachineState(), null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = 'hayday_overnight_machine_state.json';
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        console.warn('Could not export machine state:', error);
    }
}

function importMachineSettings() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json,application/json';

    fileInput.addEventListener('change', () => {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = () => {
            try {
                const parsed = JSON.parse(String(reader.result || '{}'));
                applyPortableMachineState(parsed, { applyLevel: true });
                saveMachineSettings(true);
                console.log('Imported machine state.');
            } catch (error) {
                console.warn('Could not import machine state:', error);
            }
        };
        reader.readAsText(file);
    });

    fileInput.click();
}

/* ==========================================================================
   2. DOM & DYNAMIC RENDER ENGINE (DYNAMIC DOM SHELL)
   ========================================================================== */

function getDetailDir() {
    const dir = window.DETAIL_DIR || '.';
    return dir.endsWith('/') ? dir.slice(0, -1) : dir;
}

function hydrateAssets(container = document) {
    container.querySelectorAll("img[data-asset]").forEach(img => {
        const key = img.getAttribute("data-asset");
        if (window.ASSET_BANK && window.ASSET_BANK[key]) {
            img.src = window.ASSET_BANK[key];
        }
    });
}

function updateStrategyVisibility() {
    const tableBody = document.getElementById('strategy-table-body');
    const listContainer = document.getElementById('shopping-list-container');
    const profitDisplay = document.getElementById('display-total-profit');
    const siloDisplay = document.getElementById('display-silo-space');
    const barnDisplay = document.getElementById('display-barn-space');

    if (!tableBody || !listContainer) return;

    const currentLevel = document.getElementById('overnightLevelRange')?.value || "1";
    const tabData = (window.STRATEGY_DATA && window.STRATEGY_DATA[currentTabId]) || {};
    const levelRows = tabData[currentLevel] || [];

    const instanceMap = new Map();
    machineInstances.forEach(m => instanceMap.set(m.id, m));

    const coinSrc = (window.ASSET_BANK && window.ASSET_BANK['coin']) || '';
    const coinImgHtml = coinSrc ? `<img class="coin-icon" src="${coinSrc}" alt="coins">` : '';

    let panelTotalProfit = 0;
    const dynamicIngredients = {};
    let tableHtml = '';
    const detailDir = getDetailDir();

    levelRows.forEach(row => {
        if (row.type === 'fields') {
            const comboParts = (row.combination || []).map(item => {
                const cleanFilename = `${detailDir}/details_${item.name.toLowerCase().replace(/ /g, '_').replace(/-/g, '_')}.html`;
                const assetKey = item.name.toLowerCase().trim().replace(/ /g, '_');
                const imgSrc = (window.ASSET_BANK && window.ASSET_BANK[assetKey]) || '';
                const imgHtml = imgSrc ? `<img class="inline-item-img" src="${imgSrc}" alt="${item.name}">` : '';

                return `<a href="${cleanFilename}" class="item-link queue-pill">${imgHtml} ${item.count}x ${item.name}</a>`;
            });

            for (const [ingName, qty] of Object.entries(row.ingredients || {})) {
                dynamicIngredients[ingName] = (dynamicIngredients[ingName] || 0) + qty;
            }

            panelTotalProfit += row.profit;

            const fieldsImgSrc = (window.ASSET_BANK && window.ASSET_BANK['fields']) || '';
            const fieldsImgHtml = fieldsImgSrc ? `<img class="inline-machine-img" src="${fieldsImgSrc}" alt="Fields">` : '';

            tableHtml += `
                <tr>
                    <td class="source-cell">
                        <a href="${detailDir}/details_fields.html" class="machine-label-wrapper item-link">
                            ${fieldsImgHtml} <b>Fields</b>
                        </a>
                    </td>
                    <td><div class="queue-flex">${comboParts.join(' ')}</div></td>
                    <td style="color:#2ecc71; font-weight:bold; white-space:nowrap;">
                        ${row.profit > 0 ? '+' : ''}${row.profit.toLocaleString('en-US', { maximumFractionDigits: 0 })}${coinImgHtml}
                    </td>
                </tr>
            `;
        } else if (row.type === 'machine') {
            const mState = instanceMap.get(row.id);
            if (mState && mState.selected) {
                const starKey = mState.mastery === 1 ? "1_star" : `${mState.mastery}_stars`;
                const slotsMap = (row.mastery_map && row.mastery_map[starKey]) || {};

                let slotData = null;
                for (let s = mState.slots; s >= 1; s--) {
                    if (slotsMap[s]) {
                        slotData = slotsMap[s];
                        break;
                    }
                }

                const machineCleanFilename = `${detailDir}/details_${row.source.toLowerCase().replace(/ /g, '_').replace(/-/g, '_')}.html`;
                const assetKey = row.source.toLowerCase().trim().replace(/ /g, '_');
                const mImgSrc = (window.ASSET_BANK && window.ASSET_BANK[assetKey]) || '';
                const mImgHtml = mImgSrc ? `<img class="inline-machine-img" src="${mImgSrc}" alt="${row.source}">` : '';

                let queueHtml = '<i>No items match time constraint.</i>';
                let profitHtml = `0${coinImgHtml}`;

                if (slotData) {
                    const comboParts = (slotData.combination || []).map(item => {
                        const cleanFilename = `${detailDir}/details_${item.name.toLowerCase().replace(/ /g, '_').replace(/-/g, '_')}.html`;
                        const itemAssetKey = item.name.toLowerCase().trim().replace(/ /g, '_');
                        const imgSrc = (window.ASSET_BANK && window.ASSET_BANK[itemAssetKey]) || '';
                        const imgHtml = imgSrc ? `<img class="inline-item-img" src="${imgSrc}" alt="${item.name}">` : '';

                        return `<a href="${cleanFilename}" class="item-link queue-pill">${imgHtml} ${item.count}x ${item.name}</a>`;
                    });

                    queueHtml = comboParts.length > 0 ? comboParts.join(' ') : '<i>No item configuration fit in this window.</i>';
                    profitHtml = `${slotData.profit.toLocaleString('en-US', { maximumFractionDigits: 0 })}${coinImgHtml}`;

                    panelTotalProfit += slotData.profit;

                    for (const [ingName, qty] of Object.entries(slotData.ingredients || {})) {
                        dynamicIngredients[ingName] = (dynamicIngredients[ingName] || 0) + qty;
                    }
                }

                tableHtml += `
                    <tr>
                        <td class="source-cell">
                            <a href="${machineCleanFilename}" class="machine-label-wrapper item-link">
                                ${mImgHtml} <b>${row.name}</b>
                            </a>
                        </td>
                        <td><div class="queue-flex">${queueHtml}</div></td>
                        <td style="color:#2ecc71; font-weight:bold; white-space:nowrap;">${profitHtml}</td>
                    </tr>
                `;
            }
        }
    });

    tableBody.innerHTML = tableHtml || '<tr><td colspan="3">No unlocked machines available for this time window.</td></tr>';

    if (profitDisplay) {
        profitDisplay.innerHTML = `${panelTotalProfit.toLocaleString('en-US', { maximumFractionDigits: 0 })}${coinImgHtml}`;
    }

    let siloSpace = 0;
    let barnSpace = 0;
    const entries = Object.entries(dynamicIngredients).sort((a, b) => b[1] - a[1]);

    if (entries.length === 0) {
        listContainer.innerHTML = '<li>None (No raw items processed).</li>';
    } else {
        listContainer.innerHTML = entries.map(([ingName, qty]) => {
            const cleanFilename = `${detailDir}/details_${ingName.toLowerCase().replace(/ /g, '_').replace(/-/g, '_')}.html`;
            const assetKey = ingName.toLowerCase().trim().replace(/ /g, '_');
            const imgSrc = (window.ASSET_BANK && window.ASSET_BANK[assetKey]) || '';
            const imgHtml = imgSrc ? `<img class="inline-item-img" src="${imgSrc}" alt="${ingName}">` : '';

            return `<li><a href="${cleanFilename}" class="item-link">${imgHtml} <b>${qty}x</b> ${ingName}</a></li>`;
        }).join('');
    }

    for (const [ingName, qty] of entries) {
        if (window.SILO_ITEMS && window.SILO_ITEMS.has(ingName)) {
            siloSpace += qty;
        } else {
            barnSpace += qty;
        }
    }

    if (siloDisplay) siloDisplay.innerText = siloSpace.toLocaleString('en-US');
    if (barnDisplay) barnDisplay.innerText = barnSpace.toLocaleString('en-US');

    hydrateAssets();
}

/* ==========================================================================
   3. TAB AND LEVEL NAVIGATION
   ========================================================================== */

function applyTab(tabId) {
    if (!tabId) return;
    currentTabId = tabId;

    document.querySelectorAll('.tab-link').forEach(tab => {
        const tabOnclick = tab.getAttribute('onclick') || '';
        tab.classList.toggle('active', tabOnclick.includes(`'${tabId}'`));
    });
}

function switchTab(evt, tabId) {
    applyTab(tabId);
    updateStrategyVisibility();
}

function switchLevel(selectedLevel) {
    selectedLevel = selectedLevel.toString();
    const numLevel = parseInt(selectedLevel, 10);

    const displayLabel = document.getElementById("overnightLevelDisplay");
    if (displayLabel) displayLabel.innerText = "Lvl " + selectedLevel;

    document.querySelectorAll('.machine-card').forEach(card => {
        const minLvl = parseInt(card.getAttribute('data-min-level') || '1', 10);
        card.style.display = minLvl > numLevel ? 'none' : 'flex';
    });

    if (window.HayDayLevelFilterPersistence) {
        window.HayDayLevelFilterPersistence.writeStoredLevel(numLevel);
    }
    updateStrategyVisibility();
}

function applyPortableMachineState(portableState, options = { applyLevel: false }) {
    if (!portableState) return false;

    const machineList = Array.isArray(portableState) ? portableState : (portableState.machines || portableState.machineSettings || portableState.settings || []);
    const appliedAny = applyMachineSettings(machineList);

    if (options.applyLevel && portableState.selectedLevel !== undefined) {
        const levelSlider = document.getElementById('overnightLevelRange');
        if (levelSlider) {
            levelSlider.value = String(portableState.selectedLevel);
            switchLevel(levelSlider.value);
        }
    }

    if (portableState.activeTabId) {
        applyTab(portableState.activeTabId);
    }

    updateStrategyVisibility();
    return appliedAny;
}

function logMachineStateChange(action, machineState) {
    console.log(`State Changed [${action}]:`, getSelectedMachinesData());
    updateStrategyVisibility();
    saveMachineSettings(true);
}

/* ==========================================================================
   4. MACHINE CARDS AND CONFIGURATION BUILDER
   ========================================================================== */

function createMachineCard(config) {
    const container = document.getElementById("machines-container");
    if (!container) return;

    const isFirstInstance = config.id.endsWith('_1');

    const state = {
        id: config.id,
        assetKey: config.assetKey,
        name: config.name,
        minLevel: config.minLevel,
        selected: !!config.initialSelected,
        slots: Math.min(Math.max(config.currentSlots, config.minSlots), config.maxSlots),
        minSlots: config.minSlots,
        maxSlots: config.maxSlots,
        mastery: config.currentMastery || 0
    };

    const card = document.createElement('div');
    card.className = state.selected ? 'machine-card selected' : 'machine-card';
    card.setAttribute('data-min-level', config.minLevel);

    const imgSrc = (window.ASSET_BANK && window.ASSET_BANK[config.assetKey]) || "";
    const diamondImgSrc = (window.ASSET_BANK && window.ASSET_BANK["diamond"]) || "";

    card.innerHTML = `
        <h4>${config.name}</h4>
        <div class="lvl-tag">Unlocked Level ${config.minLevel}</div>
        <img ${imgSrc ? `src="${imgSrc}"` : ''} data-asset="${config.assetKey}" class="card-img" alt="${config.name}">
        <div class="mastery-stars-container ${state.selected ? '' : 'disabled-controls'}"></div>
        <div class="slots-grid ${state.selected ? '' : 'disabled-controls'}"></div>
    `;

    container.appendChild(card);
    const starsContainer = card.querySelector('.mastery-stars-container');
    const slotsGrid = card.querySelector('.slots-grid');

    function renderStars() {
        starsContainer.innerHTML = '';
        if (!isFirstInstance) return;

        for (let star = 1; star <= 3; star++) {
            const starSpan = document.createElement('span');
            starSpan.className = `star-btn ${star <= state.mastery ? 'active' : ''}`;
            starSpan.innerHTML = '★';
            starSpan.title = `Mastery Star ${star}`;

            starSpan.addEventListener('click', (e) => {
                e.stopPropagation();
                const newMastery = (state.mastery === star) ? star - 1 : star;

                // Sync mastery across all matching machine instances (e.g., Feed Mill #1 & #2)
                machineInstances.forEach(other => {
                    if (other.assetKey === state.assetKey) {
                        other.mastery = newMastery;
                        other.renderStars();
                    }
                });

                logMachineStateChange('Mastery Changed', state);
            });
            starsContainer.appendChild(starSpan);
        }
    }

    function renderSlots() {
        slotsGrid.innerHTML = '';

        for (let i = 0; i < state.slots; i++) {
            const tile = document.createElement('div');
            tile.className = 'slot-tile empty-slot';
            tile.innerText = 'EMPTY';
            tile.title = "Click to remove this slot";

            tile.addEventListener('click', (e) => {
                e.stopPropagation();
                if (state.slots > state.minSlots) {
                    state.slots--;
                    renderSlots();
                    logMachineStateChange('Slot Removed', state);
                }
            });

            slotsGrid.appendChild(tile);
        }

        if (state.slots < state.maxSlots) {
            const buyTile = document.createElement('div');
            buyTile.className = 'slot-tile buy-slot';

            buyTile.innerHTML = `<span style="font-size:10px; line-height:1;">+</span><img ${diamondImgSrc ? `src="${diamondImgSrc}"` : ''} class="buy-diamond-icon" data-asset="diamond" alt="diamond">`;
            buyTile.title = "Click to buy another slot";

            buyTile.addEventListener('click', (e) => {
                e.stopPropagation();
                if (state.slots < state.maxSlots) {
                    state.slots++;
                    renderSlots();
                    logMachineStateChange('Slot Purchased', state);
                }
            });

            slotsGrid.appendChild(buyTile);
        }

        if (typeof setupImageObserver === 'function') {
            setupImageObserver(slotsGrid);
        }
    }

    card.addEventListener('click', () => {
        state.selected = !state.selected;
        card.classList.toggle('selected', state.selected);
        starsContainer.classList.toggle('disabled-controls', !state.selected);
        slotsGrid.classList.toggle('disabled-controls', !state.selected);

        logMachineStateChange(state.selected ? 'Machine Enabled' : 'Machine Disabled', state);
    });

    renderStars();
    renderSlots();

    if (typeof setupImageObserver === 'function') {
        setupImageObserver(card);
    }

    state.card = card;
    state.starsContainer = starsContainer;
    state.slotsGrid = slotsGrid;
    state.renderStars = renderStars;
    state.renderSlots = renderSlots;
    machineInstances.push(state);
}

/* ==========================================================================
   5. EXPOSE FUNCTIONS TO GLOBAL SCOPE & INITIALIZATION
   ========================================================================== */

// FIX 2: Explicitly attach handlers to window scope for HTML inline calls
window.switchTab = switchTab;
window.switchLevel = switchLevel;
window.clearMachineSettings = clearMachineSettings;
window.exportMachineSettings = exportMachineSettings;
window.importMachineSettings = importMachineSettings;

document.addEventListener("DOMContentLoaded", function() {
    initMachineCards();
    hydrateAssets();
    loadMachineSettings();

    let slider = document.getElementById("overnightLevelRange");
    if (slider) {
        const initialLevel = window.HayDayLevelFilterPersistence
            ? window.HayDayLevelFilterPersistence.readStoredLevel(parseInt(slider.value || "1", 10), parseInt(slider.max || "1", 10))
            : parseInt(slider.value || "1", 10);
        slider.value = String(initialLevel);
        switchLevel(slider.value);
    }
});

window.addEventListener('beforeunload', () => {
    if (skipNextAutoSave) return;
    saveMachineSettings(true);
});

function initMachineCards() {
    const container = document.getElementById("machines-container");
    if (!container) return;

    container.innerHTML = "";
    if (Array.isArray(window.machineInstances)) {
        window.machineInstances.length = 0; // Clear existing references
    }

    if (Array.isArray(window.MACHINE_CONFIGS)) {
        window.MACHINE_CONFIGS.forEach(config => {
            if (typeof createMachineCard === 'function') {
                createMachineCard(config);
            }
        });
    }
}

// Attach to window so event listeners and DOM lifecycles can invoke it
window.initMachineCards = initMachineCards;