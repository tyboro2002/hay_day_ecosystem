python -m visualizers.graph

python -m visualizers.network



python -m calculators.profitability

python -m calculators.overnight_strategy

python -m exporters.csv_exporter

python -m game_data.game_data



for tests
    pytest -q tests
or for a specific test file
    pytest -q tests/test_game_data.py

for viewing the page use
    python -m http.server 8000
and go to
    http://localhost:8000/overnight_strategies.html
    http://localhost:8000/api/v2/index.json
