from pathlib import Path
from visualizers.helpers.templates import DISCLAIMER_FOOTER

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hay Day Multi-Farm Material Manager</title>
  <style>
    :root {{
      --bg-color: #18191a;
      --card-bg: #242526;
      --border-color: #3a3b3c;
      --text-color: #e4e6eb;
      --accent-color: #e67e22;
      --accent-hover: #d35400;
      --success-bg: #1b4332;
      --success-text: #2ecc71;
      --danger-bg: #4a151b;
      --danger-text: #e74c3c;
      --disabled-bg: #2d2f31;
    }}

    * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    body {{ background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; font-size: 13px; }}

    .container {{ max-width: 1450px; margin: 0 auto; }}
    h1 {{ color: var(--accent-color); margin-top: 0; text-align: center; }}

    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      background: var(--card-bg);
      padding: 15px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      margin-bottom: 20px;
      align-items: center;
      justify-content: space-between;
    }}

    .btn-group {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}

    button {{
      background-color: var(--accent-color);
      color: white;
      border: none;
      padding: 8px 14px;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
      transition: background 0.2s;
    }}
    button:hover {{ background-color: var(--accent-hover); }}
    button.secondary {{ background-color: #3a3b3c; color: var(--text-color); }}
    button.secondary:hover {{ background-color: #4e4f50; }}
    button.active-btn {{ background-color: #27ae60; color: white; }}
    button.active-btn:hover {{ background-color: #219653; }}
    button.danger {{ background-color: #c0392b; }}
    button.danger:hover {{ background-color: #a93226; }}

    input[type="number"], input[type="text"], select {{
      background-color: #18191a;
      border: 1px solid var(--border-color);
      color: var(--text-color);
      border-radius: 4px;
    }}
    input[type="text"], .padded {{
      padding: 8px 14px;
    }}

    .inline-edit {{
      field-sizing: content;
      min-width: 1.5ch;
      background-color: transparent !important;
      border: 1px solid transparent !important;
      color: var(--text-color) !important;
      border-radius: 4px;
      font-size: 13px;
      cursor: pointer;
      transition: background-color 0.2s, border-color 0.2s;
    }}

    .centered-edit {{
      text-align: center;
    }}

    .inline-edit:hover {{
      border: 1px dashed var(--border-color) !important;
    }}

    .inline-edit:focus {{
      background-color: #18191a !important;
      border: 1px solid var(--border-color) !important;
      outline: none;
      cursor: text;
      box-shadow: 0 0 0 2px rgba(230, 126, 34, 0.4);
    }}

    .limit-box, .active-farm-indicator {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: #18191a;
      padding: 6px 12px;
      border-radius: 4px;
      border: 1px solid var(--border-color);
    }}

    .table-container {{ overflow-x: auto; background: var(--card-bg); border-radius: 8px; border: 1px solid var(--border-color); }}
    table {{ width: 100%; border-collapse: collapse; text-align: center; white-space: nowrap; }}

    th, td {{ border: 1px solid var(--border-color); padding: 6px 8px; font-size: 12px; }}
    th {{ background-color: #2d2f31; font-weight: bold; }}

    .category-header {{ background-color: #33291e; color: var(--accent-color); font-size: 14px; font-weight: bold; }}
    .group-icon {{ max-height: 28px; max-width: 28px; object-fit: contain; vertical-align: middle; margin-right: 6px; }}
    .item-header {{ background-color: #1f2021; padding: 6px 8px; }}
    .item-icon {{ max-height: 32px; max-width: 32px; width: auto; height: auto; object-fit: contain; display: block; margin: 0 auto 4px auto; }}

    .item-header.clickable-buy {{
      cursor: pointer;
      transition: background-color 0.2s, color 0.2s;
      user-select: none;
    }}
    .item-header.clickable-buy:hover {{
      background-color: #383a3d !important;
      color: var(--accent-color);
    }}

    .collapse-btn {{
      background: rgba(255, 255, 255, 0.12);
      color: var(--accent-color);
      border: 1px solid var(--border-color);
      padding: 1px 7px;
      border-radius: 3px;
      font-size: 12px;
      cursor: pointer;
      margin-right: 8px;
      vertical-align: middle;
      font-weight: bold;
      transition: background 0.2s;
    }}
    .collapse-btn:hover {{
      background: rgba(230, 126, 34, 0.25);
    }}
    .cell-collapsed {{
      background-color: #212324;
      font-weight: bold;
      color: #aaa;
    }}

    .farm-row:hover {{ background-color: #2c2d2e; }}
    .main-farm-row {{ background-color: #342818 !important; }}
    .active-farm-row {{ outline: 1px solid #27ae60; }}

    .cell-locked {{ background-color: var(--disabled-bg); color: #666; font-style: italic; }}
    .cell-input {{ width: 60px; text-align: center; }}

    .badge {{ padding: 3px 8px; border-radius: 4px; font-weight: bold; display: inline-block; }}
    .badge-true {{ background-color: var(--success-bg); color: var(--success-text); border: 1px solid var(--success-text); }}
    .badge-false {{ background-color: var(--danger-bg); color: var(--danger-text); border: 1px solid var(--danger-text); }}
    .badge-warn {{ background-color: #5c3810; color: #f39c12; border: 1px solid #f39c12; }}

    /* Schedule Section */
    .schedule-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      margin-top: 20px;
    }}
    .schedule-header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 12px;
    }}
    .schedule-card h2 {{
      color: var(--accent-color);
      margin: 0;
      font-size: 15px;
    }}
    .schedule-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 15px;
      margin-top: 15px;
    }}
    .schedule-group {{
      background: #18191a;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 12px;
    }}
    .schedule-group h3 {{
      margin: 0 0 10px 0;
      color: var(--accent-color);
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .day-step {{
      background: #242526;
      border-left: 3px solid var(--accent-color);
      padding: 8px 12px;
      margin-bottom: 8px;
      border-radius: 0 4px 4px 0;
    }}
    .day-step h4 {{
      margin: 0 0 4px 0;
      font-size: 12px;
      color: #2ecc71;
    }}
    .day-step ul {{
      margin: 0;
      padding-left: 18px;
      color: var(--text-color);
      font-size: 12px;
    }}

    /* Help Section */
    .help-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      margin-top: 20px;
    }}
    .help-card h2 {{
      color: var(--accent-color);
      margin-top: 0;
      font-size: 15px;
    }}
    .help-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}
    .help-item {{
      background: #18191a;
      border: 1px solid var(--border-color);
      padding: 12px;
      border-radius: 6px;
    }}
    .help-item h4 {{
      margin: 0 0 6px 0;
      color: var(--accent-color);
      font-size: 13px;
    }}
    .help-item p {{
      margin: 0;
      color: #aaa;
      font-size: 12px;
      line-height: 1.4;
    }}

    .modal {{
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.7);
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }}
    .modal-content {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      width: 400px;
      max-width: 90%;
    }}
    .modal-content h3 {{ margin-top: 0; color: var(--accent-color); }}
    .form-group {{ margin-bottom: 12px; display: flex; flex-direction: column; gap: 4px; }}
    .form-group label {{ font-size: 12px; color: #aaa; }}
    .form-group input, .form-group select {{ width: 100%; }}

    .tag-main {{ background: var(--accent-color); color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px; margin-left: 4px; }}
    .tag-active {{ background: #27ae60; color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px; margin-left: 4px; }}

    /* Disclaimer Footer Styling */
    .sc-disclaimer-footer {{ margin-top: 40px; color: #666; font-size: 0.8rem; text-align: center; line-height: 1.4; }}
    .sc-disclaimer-footer a {{ color: #3498db; text-decoration: none; }}
    .sc-disclaimer-footer a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>

<div class="container">
  <h1>Hay Day Multi-Farm Inventory Ledger</h1>

  <div class="toolbar">
    <div class="btn-group">
      <button onclick="openAddFarmModal()">Add Farm</button>
      <button onclick="openTransferModal()">Transfer Items</button>
      <button class="secondary" onclick="exportJSON()">Export JSON</button>
      <button class="secondary" onclick="importJSON()">Import JSON</button>
      <button class="danger" onclick="resetData()">⚠️ Reset</button>
    </div>
    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
      <div class="active-farm-indicator">
        <span>Active Farm:</span>
        <strong id="activeFarmDisplay" style="color: #2ecc71;">🚜 None</strong>
      </div>
      <div class="limit-box">
        <label for="dailyUsedInput">Daily Bought / Used:</label>
        <input type="number" id="dailyUsedInput" value="0" min="0" max="89" style="width: 55px;" onchange="updateDailyUsed(this.value)">
        <span>/ 80 <small style="color: #aaa;">(Max 89)</small></span>
      </div>
    </div>
  </div>

  <div class="table-container">
    <table id="inventoryTable">
      <thead>
        <tr id="categoryHeaderRow"></tr>
        <tr id="itemHeaderRow"></tr>
      </thead>
      <tbody id="farmRows"></tbody>
      <tbody id="summaryRows"></tbody>
    </table>
  </div>

  <!-- Transfer Schedule Recommendations -->
  <div class="schedule-card">
    <div class="schedule-header-bar">
      <h2>📅 Suggested Transfer Schedules (Per Group)</h2>
      <div style="display: flex; align-items: center; gap: 8px;">
        <label for="strategySelect" style="font-size: 12px; color: #aaa;">Source Selection Strategy:</label>
        <select id="strategySelect" onchange="updateTransferStrategy(this.value)" style="padding: 4px 8px; font-size: 12px;">
          <option value="most">Most Item Stock First</option>
          <option value="least">Least Item Stock First</option>
          <option value="max_storage">Highest Storage Usage % First (Fullest)</option>
          <option value="min_storage">Lowest Storage Usage % First (Emptiest)</option>
          <option value="order">Farm List Order</option>
        </select>
      </div>
    </div>
    <div id="scheduleContainer" class="schedule-grid"></div>
  </div>

  <!-- Instructions Section -->
  <div class="help-card">
    <h2>How to Use This Ledger</h2>
    <div class="help-grid">
      <div class="help-item">
        <h4>1. Manage Farms & Active Farm</h4>
        <p>Click <b>Add Farm</b> to register baby farms. Click <b>★</b> to set your Main Farm. Click <b>🚜</b> to select your <b>Active Farm</b> (the farm you are currently playing on).</p>
      </div>
      <div class="help-item">
        <h4>2. Quick Buy Items</h4>
        <p>Click directly on any item column header to log purchases for your <b>Active Farm</b>. Note: Items bought only increment the <b>Daily Bought / Used</b> limit if bought on your <b>Main Farm</b>.</p>
      </div>
      <div class="help-item">
        <h4>3. Live Editing & Grouping</h4>
        <p>Click directly on any cell to edit numbers inline. Click the <b>[−]</b> or <b>[+]</b> button next to any category header to collapse or expand its columns.</p>
      </div>
      <div class="help-item">
        <h4>4. Target Quantities</h4>
        <p>Enter target numbers in the <b>Needed</b> row for each category. The ledger instantly calculates stock shortages and checks if requirements are met.</p>
      </div>
      <div class="help-item">
        <h4>5. Transfer Schedules & Source Deciders</h4>
        <p>Schedules specify exact source baby farms (e.g., <i>10x Planks from baby3</i>). Use the <b>Source Selection Strategy</b> toggle to choose whether baby farms with most/least stock or highest/lowest storage % are prioritized.</p>
      </div>
      <div class="help-item">
        <h4>6. Backup & Import</h4>
        <p>Use <b>Export JSON</b> to download a backup file of your ledger (including your strategy choice). Use <b>Import JSON</b> to load saved data, or <b>Reset</b> to clear local cache to defaults.</p>
      </div>
    </div>
  </div>

  {DISCLAIMER_FOOTER.format(path_prefix="")}
</div>

<!-- Modal: Add Farm -->
<div id="farmModal" class="modal">
  <div class="modal-content">
    <h3>Add New Farm</h3>
    <div class="form-group">
      <label>Farm Name</label>
      <input type="text" id="farmNameInput" placeholder="e.g., baby5">
    </div>
    <div class="form-group">
      <label>Level</label>
      <input type="number" class="padded" id="farmLevelInput" value="1" min="1">
    </div>
    <div class="form-group">
      <label>Max Storage</label>
      <input type="number" class="padded" id="farmMaxStorageInput" value="100" min="10">
    </div>
    <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:15px;">
      <button class="secondary" onclick="closeModal('farmModal')">Cancel</button>
      <button onclick="saveFarm()">Save Farm</button>
    </div>
  </div>
</div>

<!-- Modal: Transfer Items -->
<div id="transferModal" class="modal">
  <div class="modal-content">
    <h3>Transfer Item to Main Farm</h3>
    <div class="form-group">
      <label>Source Baby Farm</label>
      <select id="transferSourceSelect" onchange="populateTransferItems()"></select>
    </div>
    <div class="form-group">
      <label>Select Item</label>
      <select id="transferItemSelect"></select>
    </div>
    <div class="form-group">
      <label>Quantity (Max 10)</label>
      <input type="number" class="padded" id="transferQtyInput" value="1" min="1" max="10">
    </div>
    <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:15px;">
      <button class="secondary" onclick="closeModal('transferModal')">Cancel</button>
      <button onclick="executeTransfer()">Transfer</button>
    </div>
  </div>
</div>

<script>
  let appState = {{
    dailyUsed: 0,
    activeFarmId: null,
    transferStrategy: 'most',
    groups: [],
    items: [],
    farms: [],
    needed: {{}},
    collapsedGroups: {{}}
  }};

  async function fetchConfigDefaults() {{
    try {{
      const res = await fetch('ledger_config.json');
      if (!res.ok) throw new Error(`HTTP status ${{res.status}}`);
      const data = await res.json();
      return {{
        dailyUsed: data.daily_used !== undefined ? data.daily_used : (data.dailyUsed || 0),
        activeFarmId: data.activeFarmId || data.active_farm_id || null,
        transferStrategy: data.transferStrategy || data.transfer_strategy || 'most',
        groups: data.groups || [],
        items: data.items || [],
        farms: data.farms || [],
        needed: data.needed || {{}},
        collapsedGroups: data.collapsedGroups || {{}}
      }};
    }} catch (err) {{
      console.warn("Could not load ledger_config.json, using internal empty state.", err);
      return null;
    }}
  }}

  async function init() {{
    const saved = localStorage.getItem('hayday_ledger_data');
    if (saved) {{
      try {{
        appState = JSON.parse(saved);
      }} catch (e) {{
        console.error("Error parsing stored localStorage data:", e);
        const defaults = await fetchConfigDefaults();
        if (defaults) appState = defaults;
      }}
    }} else {{
      const defaults = await fetchConfigDefaults();
      if (defaults) appState = defaults;
    }}

    if (appState.dailyUsed === undefined) appState.dailyUsed = 0;
    if (!appState.transferStrategy) appState.transferStrategy = 'most';
    if (!appState.collapsedGroups) appState.collapsedGroups = {{}};

    if (!appState.activeFarmId && appState.farms && appState.farms.length) {{
      const main = appState.farms.find(f => f.isMain) || appState.farms[0];
      appState.activeFarmId = main.id;
    }}

    document.getElementById('dailyUsedInput').value = appState.dailyUsed;
    document.getElementById('strategySelect').value = appState.transferStrategy;
    render();
  }}

  function saveState() {{
    localStorage.setItem('hayday_ledger_data', JSON.stringify(appState));
    render();
  }}

  function toggleGroupCollapse(groupId) {{
    if (!appState.collapsedGroups) appState.collapsedGroups = {{}};
    appState.collapsedGroups[groupId] = !appState.collapsedGroups[groupId];
    saveState();
  }}

  function updateDailyUsed(val) {{
    appState.dailyUsed = Math.max(0, parseInt(val) || 0);
    saveState();
  }}

  function updateTransferStrategy(val) {{
    appState.transferStrategy = val;
    saveState();
  }}

  function setActiveFarm(farmId) {{
    appState.activeFarmId = farmId;
    saveState();
  }}

  function buyItemForActiveFarm(itemId) {{
    const activeFarm = appState.farms.find(f => f.id === appState.activeFarmId) || appState.farms.find(f => f.isMain) || appState.farms[0];
    const item = appState.items.find(i => i.id === itemId);

    if (!activeFarm || !item) return;

    if (activeFarm.level < item.min_level) {{
      alert(`Cannot buy ${{item.name}}! ${{activeFarm.name}} is Level ${{activeFarm.level}}, but ${{item.name}} requires Level ${{item.min_level}}.`);
      return;
    }}

    const val = prompt(`Buy Item for [${{activeFarm.name}}]\nItem: ${{item.name}}\nEnter quantity bought:`, "10");
    if (val === null) return;

    const qty = parseInt(val, 10);
    if (isNaN(qty) || qty <= 0) return;

    activeFarm.inventory[itemId] = (activeFarm.inventory[itemId] || 0) + qty;

    if (activeFarm.isMain) {{
      appState.dailyUsed = (appState.dailyUsed || 0) + qty;
    }}

    saveState();
  }}

  function render() {{
    if (!appState.farms || !appState.farms.length) return;
    const mainFarm = appState.farms.find(f => f.isMain) || appState.farms[0];
    let activeFarm = appState.farms.find(f => f.id === appState.activeFarmId);

    if (!activeFarm) {{
      activeFarm = mainFarm;
      appState.activeFarmId = mainFarm.id;
    }}

    document.getElementById('activeFarmDisplay').innerHTML = `🚜 ${{activeFarm.name}}`;
    document.getElementById('dailyUsedInput').value = appState.dailyUsed || 0;
    document.getElementById('strategySelect').value = appState.transferStrategy || 'most';

    let catHeaderHtml = '<th>Farm / Level</th>';
    let itemHeaderHtml = '<th>Name (Lvl)</th>';

    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const groupImg = group.image ? `<img src="${{group.image}}" class="group-icon" alt="${{group.name}}">` : '';
      const toggleBtn = `<button class="collapse-btn" onclick="toggleGroupCollapse('${{group.id}}')" title="${{isCollapsed ? 'Expand group' : 'Collapse group'}}">${{isCollapsed ? '+' : '−'}}</button>`;

      if (isCollapsed) {{
        catHeaderHtml += `<th colspan="1" class="category-header">${{toggleBtn}}${{groupImg}}${{group.name}}</th>`;
        itemHeaderHtml += `<th class="item-header">Total</th>`;
      }} else {{
        catHeaderHtml += `<th colspan="${{groupItems.length || 1}}" class="category-header">${{toggleBtn}}${{groupImg}}${{group.name}}</th>`;
        groupItems.forEach(item => {{
          const itemImg = item.image ? `<img src="${{item.image}}" class="item-icon" alt="${{item.name}}" onerror="this.style.display='none'">` : '';
          itemHeaderHtml += `<th class="item-header clickable-buy" 
                                onclick="buyItemForActiveFarm('${{item.id}}')" 
                                title="Click to buy '${{item.name}}' for ${{activeFarm.name}}">
                              ${{itemImg}}${{item.name}}<br><small>(Lvl ${{item.min_level}})</small>
                            </th>`;
        }});
      }}
    }});

    catHeaderHtml += '<th colspan="3" class="category-header">Stats</th><th>Actions</th>';
    itemHeaderHtml += '<th>Storage Used</th><th>Max Storage</th><th>Coins</th><th>Edit</th>';

    document.getElementById('categoryHeaderRow').innerHTML = catHeaderHtml;
    document.getElementById('itemHeaderRow').innerHTML = itemHeaderHtml;

    let farmRowsHtml = '';
    appState.farms.forEach(farm => {{
      let storageUsed = 0;
      let isMainRow = farm.isMain;
      let isActiveRow = (farm.id === appState.activeFarmId);

      farmRowsHtml += `<tr class="farm-row ${{isMainRow ? 'main-farm-row' : ''}} ${{isActiveRow ? 'active-farm-row' : ''}}">
        <td style="text-align:left;">
          <b>${{farm.name}}</b> 
          ${{isMainRow ? '<span class="tag-main">MAIN</span>' : ''}}
          ${{isActiveRow ? '<span class="tag-active">🚜 ACTIVE</span>' : ''}}<br>
          <small style="display: inline-flex; align-items: center; gap: 4px;">
            Lvl:
            <input type="number" 
                   class="inline-edit" 
                   value="${{farm.level}}" 
                   min="1" 
                   onchange="updateFarmLevel('${{farm.id}}', this.value)">
          </small>  
        </td>`;

      appState.groups.forEach(group => {{
        const groupItems = appState.items.filter(i => i.group === group.id);
        const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];

        if (isCollapsed) {{
          let groupTotal = 0;
          let anyUnlocked = false;
          groupItems.forEach(item => {{
            if (farm.level >= item.min_level) {{
              anyUnlocked = true;
              const qty = farm.inventory[item.id] || 0;
              groupTotal += qty;
              storageUsed += qty;
            }}
          }});

          if (anyUnlocked) {{
            farmRowsHtml += `<td class="cell-collapsed">${{groupTotal}}</td>`;
          }} else {{
            farmRowsHtml += `<td class="cell-locked">N/A</td>`;
          }}
        }} else {{
          groupItems.forEach(item => {{
            const isUnlocked = farm.level >= item.min_level;
            const qty = farm.inventory[item.id] || 0;
            if (isUnlocked) storageUsed += qty;

            farmRowsHtml += isUnlocked 
              ? `<td><input type="number" class="cell-input inline-edit centered-edit" value="${{qty}}" min="0" onchange="updateQty('${{farm.id}}', '${{item.id}}', this.value)"></td>`
              : `<td class="cell-locked">N/A</td>`;
          }});
        }}
      }});

      farmRowsHtml += `
        <td><b>${{storageUsed}}</b></td>
        <td><input type="number" class="cell-input inline-edit centered-edit" value="${{farm.maxStorage}}" min="0" onchange="updateFarmStorage('${{farm.id}}', this.value)"></td>
        <td><input type="number" class="inline-edit centered-edit" value="${{farm.coins}}" min="0" onchange="updateFarmCoins('${{farm.id}}', this.value)"></td>
        <td>
          <button class="${{isActiveRow ? 'active-btn' : 'secondary'}}" style="padding:2px 6px;" onclick="setActiveFarm('${{farm.id}}')" title="Set as Active playing farm">🚜</button>
          <button class="secondary" style="padding:2px 6px;" onclick="setMainFarm('${{farm.id}}')" title="Set as Main target farm">★</button>
          <button class="danger" style="padding:2px 6px;" onclick="deleteFarm('${{farm.id}}')" title="Delete farm">✕</button>
        </td>
      </tr>`;
    }});

    document.getElementById('farmRows').innerHTML = farmRowsHtml;
    renderSummaries(mainFarm);
    renderTransferSchedules(mainFarm);
  }}

  function hasTenStackInBabyFarm(groupItems) {{
    const babyFarms = appState.farms.filter(f => !f.isMain);
    return babyFarms.some(farm => {{
      return groupItems.some(item => (farm.inventory[item.id] || 0) >= 10);
    }});
  }}

  function renderSummaries(mainFarm) {{
    let summaryHtml = '';
    
    // Total Available Across All Farms
    summaryHtml += `<tr><td style="text-align:left;"><b>Total Stock</b></td>`;
    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
    
      if (isCollapsed) {{
        const totalGroupStock = groupItems.reduce((acc, item) => {{
          return acc + appState.farms.reduce((fAcc, f) => fAcc + (f.inventory[item.id] || 0), 0);
        }}, 0);
        summaryHtml += `<td class="cell-collapsed"><b>${{totalGroupStock}}</b></td>`;
      }} else {{
        groupItems.forEach(item => {{
          const totalItemStock = appState.farms.reduce((acc, f) => acc + (f.inventory[item.id] || 0), 0);
          summaryHtml += `<td><b>${{totalItemStock}}</b></td>`;
        }});
      }}
    }});
    summaryHtml += `<td colspan="4"></td></tr>`;

    // Row 1: Needed
    summaryHtml += `<tr><td style="text-align:left;"><b>Needed</b></td>`;
    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const neededVal = appState.needed[group.id] || 0;
      const colSpan = isCollapsed ? 1 : (groupItems.length || 1);
      summaryHtml += `<td colspan="${{colSpan}}">
        <input type="number" class="inline-edit centered-edit" value="${{neededVal}}" min="0" onchange="updateNeeded('${{group.id}}', this.value)">
      </td>`;
    }});

    const totalStorage = appState.farms.reduce((acc, f) => acc + calculateFarmStorage(f), 0);
    const totalMaxStorage = appState.farms.reduce((acc, f) => acc + (parseInt(f.maxStorage) || 0), 0);
    const totalCoins = appState.farms.reduce((acc, f) => acc + (parseInt(f.coins) || 0), 0);

    summaryHtml += `<td><b>${{totalStorage}}</b></td><td><b>${{totalMaxStorage}}</b></td><td><b>${{totalCoins}}</b></td><td></td></tr>`;

    // Row 2: Difference (Main)
    summaryHtml += `<tr><td style="text-align:left;"><b>Difference (Main)</b></td>`;
    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const neededVal = appState.needed[group.id] || 0;

      if (isCollapsed) {{
        const mainGroupTotal = groupItems.reduce((acc, item) => acc + (mainFarm.inventory[item.id] || 0), 0);
        const diff = mainGroupTotal - neededVal;
        summaryHtml += `<td style="color:${{diff >= 0 ? '#2ecc71' : '#e74c3c'}}"><b>${{diff}}</b></td>`;
      }} else {{
        groupItems.forEach(item => {{
          const mainQty = mainFarm.inventory[item.id] || 0;
          const diff = mainQty - neededVal;
          summaryHtml += `<td style="color:${{diff >= 0 ? '#2ecc71' : '#e74c3c'}}"><b>${{diff}}</b></td>`;
        }});
      }}
    }});
    summaryHtml += `<td colspan="4"></td></tr>`;

    // Row 3: Total Needed Extra
    summaryHtml += `<tr><td style="text-align:left;"><b>Total Needed Extra</b></td>`;
    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const neededVal = appState.needed[group.id] || 0;
      const totalGroupNeeded = groupItems.reduce((acc, item) => {{
        const mainQty = mainFarm.inventory[item.id] || 0;
        return acc + Math.max(0, neededVal - mainQty);
      }}, 0);
      const colSpan = isCollapsed ? 1 : (groupItems.length || 1);
      summaryHtml += `<td colspan="${{colSpan}}"><b>${{totalGroupNeeded}}</b></td>`;
    }});
    summaryHtml += `<td colspan="4"></td></tr>`;

    // Row 4: Possible? (Main)
    summaryHtml += `<tr><td style="text-align:left;"><b>Possible? (Main)</b></td>`;
    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const neededVal = appState.needed[group.id] || 0;
      const isPossibleMain = groupItems.every(item => (mainFarm.inventory[item.id] || 0) >= neededVal);
      const colSpan = isCollapsed ? 1 : (groupItems.length || 1);
      summaryHtml += `<td colspan="${{colSpan}}">
        <span class="badge ${{isPossibleMain ? 'badge-true' : 'badge-false'}}">${{isPossibleMain ? 'YES' : 'NO'}}</span>
      </td>`;
    }});
    summaryHtml += `<td colspan="4"></td></tr>`;

    // Row 5: Possible? (Total)
    summaryHtml += `<tr><td style="text-align:left;"><b>Possible? (Total)</b></td>`;
    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const neededVal = appState.needed[group.id] || 0;
      const isPossibleTotal = groupItems.every(item => {{
        const totalStockAcrossAllFarms = appState.farms.reduce((acc, f) => acc + (f.inventory[item.id] || 0), 0);
        return totalStockAcrossAllFarms >= neededVal;
      }});
      const colSpan = isCollapsed ? 1 : (groupItems.length || 1);
      summaryHtml += `<td colspan="${{colSpan}}">
        <span class="badge ${{isPossibleTotal ? 'badge-true' : 'badge-false'}}">${{isPossibleTotal ? 'YES' : 'NO'}}</span>
      </td>`;
    }});
    summaryHtml += `<td colspan="4"></td></tr>`;

    // Row 6: Pos in 1 Day?
    summaryHtml += `<tr><td style="text-align:left;"><b>Pos in 1 Day?</b></td>`;

    const used = appState.dailyUsed || 0;
    const standardCap = Math.max(0, 80 - used);
    const maxCap = used < 80 ? (89 - used) : 0;

    appState.groups.forEach(group => {{
      const groupItems = appState.items.filter(i => i.group === group.id);
      const isCollapsed = appState.collapsedGroups && appState.collapsedGroups[group.id];
      const neededVal = appState.needed[group.id] || 0;

      const totalGroupNeeded = groupItems.reduce((acc, item) => {{
        const mainQty = mainFarm.inventory[item.id] || 0;
        return acc + Math.max(0, neededVal - mainQty);
      }}, 0);

      const isPossibleTotal = groupItems.every(item => {{
        const totalStockAcrossAllFarms = appState.farms.reduce((acc, f) => acc + (f.inventory[item.id] || 0), 0);
        return totalStockAcrossAllFarms >= neededVal;
      }});

      let isPos1Day = false;

      if (isPossibleTotal) {{
        if (totalGroupNeeded <= standardCap) {{
          isPos1Day = true;
        }} else if (totalGroupNeeded <= maxCap) {{
          const has10Stack = hasTenStackInBabyFarm(groupItems);
          if (has10Stack) {{
            isPos1Day = true;
          }}
        }}
      }}

      const colSpan = isCollapsed ? 1 : (groupItems.length || 1);
      summaryHtml += `<td colspan="${{colSpan}}">
        <span class="badge ${{isPos1Day ? 'badge-true' : 'badge-false'}}">${{isPos1Day ? 'YES' : 'NO'}}</span>
      </td>`;
    }});
    summaryHtml += `<td colspan="4"></td></tr>`;

    document.getElementById('summaryRows').innerHTML = summaryHtml;
  }}

  /* Schedule Generator with Source Baby Farm Decider */
  function generateScheduleForGroup(group, mainFarm) {{
    const groupItems = appState.items.filter(i => i.group === group.id);
    const neededVal = appState.needed[group.id] || 0;
    const strategy = appState.transferStrategy || 'most';

    let rawTransfers = [];
    let stockShortageNote = [];

    groupItems.forEach(item => {{
      const mainQty = mainFarm.inventory[item.id] || 0;
      let neededExtra = Math.max(0, neededVal - mainQty);

      if (neededExtra > 0) {{
        let eligibleFarms = appState.farms
          .filter(f => !f.isMain && (f.inventory[item.id] || 0) > 0 && f.level >= item.min_level)
          .map(f => {{
            let used = calculateFarmStorage(f);
            let maxS = parseInt(f.maxStorage) || 1;
            return {{
              farmName: f.name,
              stock: f.inventory[item.id] || 0,
              storagePct: used / maxS
            }};
          }});

        const totalBabyStock = eligibleFarms.reduce((sum, f) => sum + f.stock, 0);

        if (totalBabyStock < neededExtra) {{
          stockShortageNote.push(`${{item.name}}: Need +${{neededExtra}}, but Baby farms only have ${{totalBabyStock}}`);
        }}

        // Apply Source Selection Strategy
        if (strategy === 'most') {{
          eligibleFarms.sort((a, b) => b.stock - a.stock);
        }} else if (strategy === 'least') {{
          eligibleFarms.sort((a, b) => a.stock - b.stock);
        }} else if (strategy === 'max_storage') {{
          eligibleFarms.sort((a, b) => b.storagePct - a.storagePct || b.stock - a.stock);
        }} else if (strategy === 'min_storage') {{
          eligibleFarms.sort((a, b) => a.storagePct - b.storagePct || b.stock - a.stock);
        }}

        let remNeeded = neededExtra;
        for (let ef of eligibleFarms) {{
          if (remNeeded <= 0) break;
          let takeQty = Math.min(remNeeded, ef.stock);
          if (takeQty > 0) {{
            rawTransfers.push({{
              sourceFarmName: ef.farmName,
              itemName: item.name,
              qty: takeQty
            }});
            remNeeded -= takeQty;
          }}
        }}
      }}
    }});

    if (rawTransfers.length === 0) {{
      if (stockShortageNote.length > 0) {{
        return {{ complete: false, text: "❌ Main farm needs items, but baby farms have 0 stock available.", shortage: stockShortageNote }};
      }}
      return {{ complete: true, text: "✅ Main farm already has all needed items for this group." }};
    }}

    let chunkedQueue = [];
    rawTransfers.forEach(t => {{
      let rem = t.qty;
      while (rem > 0) {{
        let chunk = Math.min(rem, 10);
        chunkedQueue.push({{ sourceFarmName: t.sourceFarmName, name: t.itemName, qty: chunk }});
        rem -= chunk;
      }}
    }});

    let currentDay = 1;
    let currentLimit = appState.dailyUsed || 0;
    let dayPlans = [];
    let dayTransfers = [];

    while (chunkedQueue.length > 0) {{
      if (currentLimit >= 80) {{
        if (dayTransfers.length > 0) {{
          dayPlans.push({{ day: currentDay, transfers: dayTransfers, endLimit: currentLimit }});
          dayTransfers = [];
        }}
        currentDay++;
        currentLimit = 0;
      }}

      let nextBatch = chunkedQueue[0];
      if (currentLimit < 80) {{
        dayTransfers.push(nextBatch);
        currentLimit += nextBatch.qty;
        chunkedQueue.shift();
      }} else {{
        if (dayTransfers.length > 0) {{
          dayPlans.push({{ day: currentDay, transfers: dayTransfers, endLimit: currentLimit }});
          dayTransfers = [];
        }}
        currentDay++;
        currentLimit = 0;
      }}
    }}

    if (dayTransfers.length > 0) {{
      dayPlans.push({{ day: currentDay, transfers: dayTransfers, endLimit: currentLimit }});
    }}

    return {{
      complete: false,
      plans: dayPlans,
      shortage: stockShortageNote
    }};
  }}

  function renderTransferSchedules(mainFarm) {{
    const container = document.getElementById('scheduleContainer');
    let html = '';

    appState.groups.forEach(group => {{
      const res = generateScheduleForGroup(group, mainFarm);
      const groupImg = group.image ? `<img src="${{group.image}}" class="group-icon" alt="${{group.name}}">` : '';

      html += `<div class="schedule-group">
        <h3><span>${{groupImg}}${{group.name}}</span></h3>`;

      if (res.complete) {{
        html += `<p style="color:#2ecc71; margin: 4px 0;">${{res.text}}</p>`;
      }} else {{
        if (res.shortage && res.shortage.length > 0) {{
          html += `<div style="margin-bottom:8px;"><span class="badge badge-warn">⚠️ Stock Shortage</span>`;
          res.shortage.forEach(s => html += `<div style="color:#f39c12; font-size:11px; margin-top:2px;">• ${{s}}</div>`);
          html += `</div>`;
        }}

        if (res.plans && res.plans.length > 0) {{
          res.plans.forEach(plan => {{
            let itemCounts = {{}};
            plan.transfers.forEach(t => {{
              let key = `${{t.sourceFarmName}}___${{t.name}}`;
              if (!itemCounts[key]) {{
                itemCounts[key] = {{ source: t.sourceFarmName, name: t.name, qty: 0 }};
              }}
              itemCounts[key].qty += t.qty;
            }});

            let transferSummary = Object.values(itemCounts)
              .map(item => `<li>Transfer <b>${{item.qty}}x ${{item.name}}</b> from <strong style="color:var(--accent-color);">${{item.source}}</strong></li>`)
              .join('');

            html += `<div class="day-step">
              <h4>Day ${{plan.day}} (Daily Limit Hit: ${{plan.endLimit}} / 80)</h4>
              <ul>${{transferSummary}}</ul>
            </div>`;
          }});
        }}
      }}

      html += `</div>`;
    }});

    container.innerHTML = html;
  }}

  function calculateFarmStorage(farm) {{
    let total = 0;
    appState.items.forEach(item => {{
      if (farm.level >= item.min_level) {{
        total += parseInt(farm.inventory[item.id] || 0);
      }}
    }});
    return total;
  }}

  function updateQty(farmId, itemId, val) {{
    const farm = appState.farms.find(f => f.id === farmId);
    if (farm) {{
      farm.inventory[itemId] = Math.max(0, parseInt(val) || 0);
      saveState();
    }}
  }}

  function updateFarmLevel(farmId, val) {{
    const farm = appState.farms.find(f => f.id === farmId);
    if (farm) {{
      farm.level = Math.max(1, parseInt(val) || 1);
      saveState();
    }}
  }}

  function updateFarmStorage(farmId, val) {{
    const farm = appState.farms.find(f => f.id === farmId);
    if (farm) {{
      farm.maxStorage = Math.max(0, parseInt(val) || 0);
      saveState();
    }}
  }}

  function updateFarmCoins(farmId, val) {{
    const farm = appState.farms.find(f => f.id === farmId);
    if (farm) {{
      farm.coins = Math.max(0, parseInt(val) || 0);
      saveState();
    }}
  }}

  function updateNeeded(groupId, val) {{
    appState.needed[groupId] = Math.max(0, parseInt(val) || 0);
    saveState();
  }}

  function setMainFarm(farmId) {{
    appState.farms.forEach(f => f.isMain = (f.id === farmId));
    saveState();
  }}

  function deleteFarm(farmId) {{
    if (appState.farms.length <= 1) return alert("Must keep at least one farm.");
    appState.farms = appState.farms.filter(f => f.id !== farmId);
    if (!appState.farms.some(f => f.isMain)) appState.farms[0].isMain = true;
    if (appState.activeFarmId === farmId) appState.activeFarmId = appState.farms[0].id;
    saveState();
  }}

  function openModal(id) {{ document.getElementById(id).style.display = 'flex'; }}
  function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}

  function openAddFarmModal() {{
    document.getElementById('farmNameInput').value = '';
    document.getElementById('farmLevelInput').value = '1';
    document.getElementById('farmMaxStorageInput').value = '100';
    openModal('farmModal');
  }}

  function saveFarm() {{
    const name = document.getElementById('farmNameInput').value.trim() || 'baby_new';
    const level = parseInt(document.getElementById('farmLevelInput').value) || 1;
    const maxStorage = parseInt(document.getElementById('farmMaxStorageInput').value) || 100;

    const newFarm = {{
      id: 'f_' + Date.now(),
      name: name,
      level: level,
      coins: 0,
      maxStorage: maxStorage,
      inventory: {{}}
    }};

    appState.farms.push(newFarm);
    closeModal('farmModal');
    saveState();
  }}

  function openTransferModal() {{
    const babyFarms = appState.farms.filter(f => !f.isMain);
    if (!babyFarms.length) return alert("No baby farms available.");

    document.getElementById('transferQtyInput').value = '1';

    const sourceSelect = document.getElementById('transferSourceSelect');
    sourceSelect.innerHTML = babyFarms.map(f => `<option value="${{f.id}}">${{f.name}} (Lvl ${{f.level}})</option>`).join('');
    populateTransferItems();
    openModal('transferModal');
  }}

  function populateTransferItems() {{
    const farmId = document.getElementById('transferSourceSelect').value;
    const farm = appState.farms.find(f => f.id === farmId);
    const itemSelect = document.getElementById('transferItemSelect');
    if (!farm) return;

    const availableItems = appState.items.filter(i => farm.level >= i.min_level && (farm.inventory[i.id] || 0) > 0);
    if (!availableItems.length) {{
      itemSelect.innerHTML = '<option value="">No stock available</option>';
      return;
    }}
    itemSelect.innerHTML = availableItems.map(i => `<option value="${{i.id}}">${{i.name}} (Stock: ${{farm.inventory[i.id]}})</option>`).join('');
  }}

  function executeTransfer() {{
    const sourceId = document.getElementById('transferSourceSelect').value;
    const itemId = document.getElementById('transferItemSelect').value;
    const qty = parseInt(document.getElementById('transferQtyInput').value) || 0;

    const sourceFarm = appState.farms.find(f => f.id === sourceId);
    const mainFarm = appState.farms.find(f => f.isMain);

    if (!sourceFarm || !mainFarm || !itemId || qty <= 0) return;

    if (qty > 10) {{
      return alert("You can only transfer a maximum of 10 items at a time.");
    }}

    const avail = sourceFarm.inventory[itemId] || 0;
    if (qty > avail) return alert("Transfer quantity exceeds available stock!");

    sourceFarm.inventory[itemId] -= qty;
    mainFarm.inventory[itemId] = (mainFarm.inventory[itemId] || 0) + qty;

    appState.dailyUsed = (appState.dailyUsed || 0) + qty;

    closeModal('transferModal');
    saveState();
  }}

  function exportJSON() {{
    // Explicitly package export state ensuring transferStrategy is present
    const payload = {{
      transferStrategy: appState.transferStrategy || 'most',
      dailyUsed: appState.dailyUsed || 0,
      activeFarmId: appState.activeFarmId,
      groups: appState.groups || [],
      items: appState.items || [],
      farms: appState.farms || [],
      needed: appState.needed || {{}},
      collapsedGroups: appState.collapsedGroups || {{}}
    }};

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `hayday_backup_${{new Date().toISOString().slice(0,10)}}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
  }}

  function importJSON() {{
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = e => {{
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = event => {{
        try {{
          const imported = JSON.parse(event.target.result);

          appState = {{
            ...imported,
            dailyUsed: imported.dailyUsed !== undefined ? imported.dailyUsed : (imported.daily_used || 0),
            transferStrategy: imported.transferStrategy || imported.transfer_strategy || 'most',
            collapsedGroups: imported.collapsedGroups || {{}}
          }};

          if (document.getElementById('strategySelect')) {{
            document.getElementById('strategySelect').value = appState.transferStrategy;
          }}

          saveState();
        }} catch (err) {{
          alert("Invalid Backup File");
        }}
      }};
      reader.readAsText(file);
    }};
    input.click();
  }}

  async function resetData() {{
    if (confirm("Reset local storage and re-read default settings from ledger_config.json?")) {{
      localStorage.removeItem('hayday_ledger_data');
      const defaults = await fetchConfigDefaults();
      if (defaults) {{
        appState = defaults;
      }}
      document.getElementById('dailyUsedInput').value = appState.dailyUsed || 0;
      document.getElementById('strategySelect').value = appState.transferStrategy || 'most';
      saveState();
    }}
  }}

  window.onload = init;
</script>
</body>
</html>
"""

def generate_ledger(output_path="docs/ledger.html"):
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"Successfully generated static HTML to '{output_path}'!")

if __name__ == "__main__":
    generate_ledger()