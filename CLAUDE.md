# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development commands

### Install dependencies
```bash
pip install -r requirements.txt
```

If you need to work on the checked-in frontend asset toolchain (Tailwind/PostCSS-related files), install the Node deps too:

```bash
npm install
```

`package.json` only contains frontend toolchain devDependencies; the Python app itself does not need `npm install` to run.

### Run the app locally
```bash
python main.py
python main.py --lan
python main.py --port 9000
python main.py --no-webview
```

### Build the Windows package
```bash
pip install pyinstaller
pyinstaller vancesender.spec
```

CI mirrors the same packaging flow in `.github/workflows/package-windows.yml` and smoke-tests the packaged app with `dist/VanceSender/VanceSender.exe --help`.

### Preview the static GitHub Pages docs
To mirror `.github/workflows/deploy-pages-docs.yml`, stage the generated `.site/` folder first:

```bash
rm -rf .site
mkdir -p .site/css .site/js
cp pages/index.html .site/index.html
cp pages/help.html .site/help.html
cp app/web/css/intro.css .site/css/intro.css
cp app/web/css/help.css .site/css/help.css
cp app/web/js/help.js .site/js/help.js
cp public-config.yaml .site/public-config.yaml
python -m http.server 8080 --directory .site
```

Then open:
- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/help.html`

### Tests, linting, and type checking
- `npm test` is only a placeholder script and currently exits with an error.
- No automated Python/JS test suite or lint command is checked into this repo, so there is no single-test command to run.
- `pyrightconfig.json` and `basedpyrightconfig.json` exist, but both hardcode `D:/gitbranch/VanceSender`; update those paths before relying on pyright in this checkout.
- Validation is mainly manual: run `python main.py`, exercise the affected UI/API flow, and use `/docs` to verify the live API surface.

## High-level architecture

### Runtime model
- `main.py` is the only entrypoint. It builds the FastAPI app, mounts `app/web` as static assets, serves `app/web/index.html` at `/`, and starts Uvicorn.
- The same backend can run in three modes: normal browser mode, embedded desktop mode via `pywebview`, and LAN mode (`--lan` / `server.lan_access`).
- Startup also initializes optional remote public-config announcements, desktop shell behavior, tray behavior, and the quick overlay.

### Paths and persistence
- `app/core/runtime_paths.py` separates read-only bundled assets from writable runtime data.
- In source mode, runtime files live in the repo.
- In frozen/PyInstaller mode, writable files move to `%LOCALAPPDATA%/VanceSender`.
- `app/core/config.py` owns YAML config loading/saving, default config merging, runtime directory creation, and seeding bundled presets into the writable preset directory.

### Backend structure
- `app/api/routes/__init__.py` registers all `/api/v1` route groups behind optional Bearer-token auth from `app/api/auth.py`.
- Route files are intentionally thin adapters:
  - `app/api/routes/sender.py`
  - `app/api/routes/presets.py`
  - `app/api/routes/ai.py`
  - `app/api/routes/settings.py`
  - `app/api/routes/stats.py`
  - `app/api/routes/medical.py`
- Most real behavior lives in `app/core/*`.

### Core subsystems
- `app/core/sender.py` is the Windows-specific FiveM sender. It uses Win32 `SendInput`, supports clipboard and typing modes, retries with different timing profiles, and refuses to send unless a FiveM window is foregrounded.
- `app/core/presets.py` stores presets as one JSON file per preset in the runtime `data/presets` directory, with preset ID validation and atomic writes.
- `app/core/ai_client.py` is the main AI abstraction for OpenAI-compatible providers and native Gemini. It handles provider resolution, client caching, retries, streaming, rewrite flows, and output parsing/post-processing.
- `app/core/ai_history.py` persists AI generation history; send history is separate and in-memory.
- `app/core/desktop_shell.py` and `app/core/quick_overlay.py` implement the pywebview desktop shell, tray integration, and floating quick-send overlay.
- `app/core/public_config.py`, `app/core/update_checker.py`, and `app/core/notifications.py` feed the home/settings UI with remote notices, update checks, and runtime notifications.
- EMS-specific logic is mostly data/service code under:
  - `app/core/medical_templates.py`
  - `app/core/medical_quick_phrases.py`
  - `app/core/medical_vitals_generator.py`
  - `app/core/medical_glossary.py`
  - `app/core/medical_combos.py`
  - `app/core/ai_conversation_tree.py`

### Frontend structure
- The frontend is plain HTML/CSS/JavaScript; there is no framework or bundler runtime.
- `app/web/index.html` is the main multi-panel shell for the packaged/local app.
- `app/web/js/app.js` is the main UI controller. It owns auth, navigation, onboarding, send/batch flows, preset CRUD interactions, AI generation/rewrite/history flows, settings, QR/LAN display, desktop titlebar behavior, and quick-panel mode.
- `app/web/js/medical.js` layers on the EMS workbench: current-case state, medical templates, glossary, quick phrases, vitals generation, SBAR generation, combo flows, and medical quick-send actions.
- `app/web/js/i18n.js` handles language switching; `app/web/js/help.js` powers the help pages.
- Styling is a mix of checked-in Tailwind output (`app/web/css/tailwind.css`) and handwritten CSS (`app/web/css/style.css`, `help.css`, `intro.css`, etc.). `tailwind.config.js` exists, but `package.json` does not define a build script for regenerating CSS.

### Static docs vs runtime UI
- `docs/API.md` is the hand-written API reference for the FastAPI app.
- `pages/` is a separate static GitHub Pages docs site (intro/help only). It does not expose live app behavior such as sending text, AI requests, or preset management.
- GitHub Pages deployment is built from a generated `.site/` directory that copies `pages/*` plus selected assets from `app/web`; previewing `pages/` directly will miss those copied assets.

## Project-specific conventions and gotchas
- Most user-facing copy, UI labels, and API docs are Chinese-first. Preserve that tone unless the task explicitly asks for different wording.
- The settings API intentionally masks secrets: tokens and provider API keys are represented as `*_set` flags rather than returned in plaintext.
- Bearer auth is optional but global: when `server.token` is non-empty, every `/api/v1/*` route is protected.
- Medical case state and several UI preferences are stored in browser `localStorage`; changing frontend behavior often means checking both API state and client-side persisted state.
- If you change route payloads, settings fields, or endpoint behavior, update `docs/API.md` too — it is detailed and manually maintained, not generated from OpenAPI.
