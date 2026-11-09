---
type: Task Runbook
id: TASK-004
title: CLI Command Runner & Localhost Streamlit Dashboard
description: "Implement terminal CLI commands (index, search-text, search-image) and an interactive Streamlit localhost web application with visual thumbnail result cards."
resource: repo://50_PROJECT/src/app.py
status: completed
assigned_profiles:
  - Frontend Developer
  - Backend Developer
change_ticket: null
dependencies:
  - TASK-000
  - TASK-001
  - TASK-002
  - TASK-003
eis_reference: "wiki/_specs/ID-104_EIS.md#4-cli--ui-specification"
affected_files:
  - "[CREATE] 50_PROJECT/src/cli.py"
  - "[CREATE] 50_PROJECT/src/app.py"
tags: [cli, streamlit, ui, frontend, search-dashboard]
generated:
  by: task-implementation-planner
  at: "2026-11-08T20:09:00-03:00"
---

# TASK-004: CLI Command Runner & Localhost Streamlit Dashboard

## GENERAL DESCRIPTION
Implement the dual user interface layer in `50_PROJECT/src/cli.py` (providing `index`, `search-text`, and `search-image` command line tools) and `50_PROJECT/src/app.py` (providing an interactive Streamlit localhost web application with thumbnail image previews, category filtering, and one-click USD file path copying) per [[ID-104_EIS.md#4-cli--ui-specification](wiki/_specs/ID-104_EIS.md#4-cli--ui-specification)].

## EXPECTED RESULT
Users can run terminal commands (`python src/cli.py search-text "table"`) and launch a local web browser interface (`streamlit run src/app.py`) displaying responsive visual cards for matching USD assets with similarity scores and exact/similar match badges per [[ID-104_EIS.md#42-streamlit-web-interface-apppy](wiki/_specs/ID-104_EIS.md#42-streamlit-web-interface-apppy)].

## CODE REFERENCE
- `[CREATE] 50_PROJECT/src/cli.py`: Implement CLI arguments parser and subcommands (`index`, `search-text`, `search-image`) per [[ID-104_EIS.md#41-cli-commands-clipy](wiki/_specs/ID-104_EIS.md#41-cli-commands-clipy)].
- `[CREATE] 50_PROJECT/src/app.py`: Implement Streamlit web dashboard with text bar, image drop zone, category sidebar, and grid result rendering per [[ID-104_EIS.md#42-streamlit-web-interface-apppy](wiki/_specs/ID-104_EIS.md#42-streamlit-web-interface-apppy)].

## VALIDATION CRITERIA
- `python 50_PROJECT/src/cli.py --help` exits cleanly with all subcommands displayed.
- Launching `streamlit run 50_PROJECT/src/app.py --server.headless=true` starts without exceptions on `localhost:8501`.

## RISKS
- Large image uploads in Streamlit UI; mitigated by automatic PIL downsampling before encoding.

## SUBSTEPS
1. Implement `50_PROJECT/src/cli.py` with `argparse` subcommands for indexing and search per [[ID-104_EIS.md#41-cli-commands-clipy](wiki/_specs/ID-104_EIS.md#41-cli-commands-clipy)].
2. Implement `50_PROJECT/src/app.py` with Streamlit controls, layout columns, image renderers, and copy path buttons per [[ID-104_EIS.md#42-streamlit-web-interface-apppy](wiki/_specs/ID-104_EIS.md#42-streamlit-web-interface-apppy)].
3. Validate CLI search execution against indexed assets.

