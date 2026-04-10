# Night Shift QA Agent

This folder contains the orchestrator foundation for the overnight mobile QA system.

## Modules

- `night_shift.py`: central orchestrator loop
- `maestro_client.py`: UI capture and action execution
- `prd_loader.py`: chunks `Mobile_PRD.md` into reusable audit sections
- `screen_classifier.py`: maps UI content to PRD sections
- `llm_clients.py`: Navigator, Auditor, and Fixer CLI adapters
- `git_recovery.py`: creates fix branches and commits captured changes
- `supabase_reset.py`: optional hosted reset and seed runner
- `artifacts.py`: jsonl event log, run state, and summary writer

## Environment variables

- `QA_GEMINI_COMMAND`
- `QA_CLAUDE_COMMAND`
- `QA_CODEX_COMMAND`
- `QA_MAESTRO_COMMAND`
- `QA_ADB_COMMAND`
- `QA_EMULATOR_ID`
- `QA_APP_ID`
- `QA_APP_START_MODE`
- `QA_MOBILE_START_COMMAND`
- `QA_APP_LAUNCH_COMMAND`
- `QA_APP_STOP_COMMAND`
- `QA_METRO_PORT`
- `QA_LOOP_LIMIT`
- `QA_STEP_DELAY_SECONDS`
- `QA_IDLE_STALL_LIMIT`
- `QA_LOGCAT_LINES`
- `QA_ALLOW_NAVIGATOR`
- `QA_ALLOW_AUDITOR`
- `QA_ALLOW_FIXER`
- `QA_RESET_BEFORE_RUN`
- `QA_SUPABASE_RESET_COMMAND`
- `QA_SUPABASE_SEED_COMMAND`

## Run

From repo root:

```powershell
python -m qa_agent.main
```

Artifacts are written under `qa_agent/artifacts/run-*`.

## Startup modes

- `dev_client`: default. Starts Metro with `npx expo start --dev-client --clear --port <port>` if needed, then launches `com.facilitypro.mobile`.
- `expo_go`: starts Metro with `npx expo start --clear --port <port>` if needed, then launches Expo Go.
- `installed_app`: assumes no Metro is needed and launches the installed app package.

You can override the defaults with:

- `QA_MOBILE_START_COMMAND`
- `QA_APP_LAUNCH_COMMAND`
- `QA_APP_STOP_COMMAND`
