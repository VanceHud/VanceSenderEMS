# AGENTS.md
Operational guide for coding agents working in `VanceSenderEMS`.

## Source of truth
- Primary repo-local instruction source: `CLAUDE.md`.
- This file is the concise agent-facing summary for this repo.

## Agent rule files present / absent
- Present: `CLAUDE.md`
- Present: `AGENTS.md` (this file)
- Absent: `.cursor/rules/**`
- Absent: `.cursorrules`
- Absent: `.github/copilot-instructions.md`
- Do not claim Cursor- or Copilot-specific rules exist unless those files are later added.

## Repository overview
- Backend: Python + FastAPI + Uvicorn
- Frontend: plain HTML/CSS/JavaScript, no framework runtime
- Packaging: PyInstaller Windows build
- Domain: FiveM EMS / 医疗 RP text sending, AI generation/rewrite, presets, desktop shell, medical helpers

## Key paths
- Entry point: `main.py`
- API routes: `app/api/routes/`
- API schemas: `app/api/schemas.py`
- Core logic: `app/core/`
- Main frontend shell: `app/web/index.html`
- Main frontend controller: `app/web/js/app.js`
- EMS frontend module: `app/web/js/medical.js`
- i18n strings: `app/web/js/i18n.js`
- Hand-maintained API docs: `docs/API.md`
- Static docs site: `pages/`
- Runtime API docs: `/docs`

## Setup commands
Install Python dependencies:
```bash
pip install -r requirements.txt
```
Install Node dependencies only when touching the frontend asset toolchain:
```bash
npm install
```
`package.json` only contains Tailwind/PostCSS devDependencies. The Python app does not need `npm install` for normal runtime work.

## Run commands
```bash
python main.py
python main.py --lan
python main.py --port 9000
python main.py --no-webview
```

## Build / packaging
```bash
pip install pyinstaller
pyinstaller vancesender.spec
```
CI mirrors this in `.github/workflows/package-windows.yml` and smoke-tests with:
```bash
dist/VanceSender/VanceSender.exe --help
```

## Static docs preview
Preview GitHub Pages docs by staging `.site/` first:
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
Then open `http://127.0.0.1:8080/` and `http://127.0.0.1:8080/help.html`.
Do not preview `pages/` directly and assume it matches deployment.

## Test / lint / typecheck reality
- `npm test` is a placeholder script and fails by design.
- No canonical automated Python test suite is checked into this repo.
- No canonical automated JS test suite is checked into this repo.
- No canonical lint command is checked into this repo.
- No supported single-test command exists today because there is no checked-in test runner or per-test harness.
- `npm test`: unusable for real validation
- `pytest`: not configured in-repo
- `unittest`: no documented test entrypoint
- JS linting: not configured
- Python linting: not configured

### Pyright caveat
`pyrightconfig.json` and `basedpyrightconfig.json` exist, but both hardcode `D:/gitbranch/VanceSender` paths. Do not present pyright as a turnkey validation step in this checkout unless you first update those paths.

## Preferred verification workflow
Because automation is minimal, validation is mainly manual:
1. Run `python main.py`.
2. Exercise the affected UI or API flow manually.
3. Check the live API surface in `/docs`.
4. If docs-site assets changed, preview `.site/` locally.
5. If packaging behavior changed, compare with `.github/workflows/package-windows.yml`.
When you cannot fully execute a path locally, say exactly what you verified and what remains unverified.

## Architecture guidance
### Backend
- `main.py` is the only entry point.
- `app/api/routes/*` should stay thin and focused on HTTP adaptation.
- Put business logic, persistence, runtime integration, and reusable helpers in `app/core/*`.
- Use `app/api/schemas.py` for request/response contracts.
- Bearer auth is optional but global when `server.token` is non-empty.

### Frontend
- Frontend is plain HTML/CSS/JS, not React/Vue/TypeScript.
- `app/web/js/app.js` is the main UI controller and owns much of the app state.
- `app/web/js/medical.js` contains EMS/medical workbench behavior.
- `app/web/js/i18n.js` owns translation strings and language switching.
- Several UI states are persisted in `localStorage`; check storage interactions when changing frontend behavior.

### Runtime / persistence
- `app/core/runtime_paths.py` separates bundled read-only assets from writable runtime data.
- In source mode, runtime files live in the repo.
- In frozen mode, writable files move under `%LOCALAPPDATA%/VanceSender`.
- Presets are stored one JSON file per preset in the runtime preset directory.

## Style guidelines
### General
- Match existing patterns before introducing new ones.
- Prefer minimal, scoped changes over broad refactors.
- Preserve Chinese-first user-facing copy unless the task explicitly asks otherwise.
- If you change API payloads, settings fields, or endpoint behavior, update `docs/API.md` in the same change.

### Python
- Follow existing module style with `from __future__ import annotations` where used.
- Use explicit type hints with modern syntax like `str | None`, `list[...]`, and `dict[str, Any]`.
- Keep imports grouped logically: stdlib, third-party, then local app imports.
- Prefer `snake_case` for functions/variables and `UPPER_CASE` for constants.
- Keep route handlers `async def` when they are part of the FastAPI route layer.
- Keep route files thin: validate input, call core logic, shape response.
- Use Pydantic models and `Field(...)` constraints for API contracts.

### Python error handling
- Use `HTTPException` for client-facing API errors in route handlers.
- At OS/runtime boundaries, defensive `except Exception` is acceptable only when returning a safe fallback, cleaning up resources, or notifying the user.
- Do not swallow errors silently in normal business logic.

### JavaScript / frontend
- This repo uses vanilla JS with large module files.
- Prefer `camelCase` for functions/locals and `UPPER_SNAKE_CASE` for constants such as storage keys.
- Follow the surrounding quote style and formatting in the file you edit.
- Reuse existing helpers and UI feedback patterns such as `showToast(...)`.
- Keep API access consistent with existing `API_BASE` and Bearer token patterns.
- Be careful with persisted browser state; changes may need migration or fallback behavior.

### Frontend error handling
- For API failures, surface useful feedback to the user.
- For non-critical browser storage paths, silent fallback is acceptable only when the current code already treats storage as best-effort.
- If ignoring an error intentionally, keep the reason obvious from nearby code or comments.

### CSS / HTML
- Preserve the current plain HTML structure and checked-in CSS approach.
- Styling is a mix of checked-in Tailwind output and handwritten CSS.
- Reuse existing design tokens/custom properties where possible.
- Avoid introducing a new frontend build/runtime dependency unless explicitly requested.

## Security and config gotchas
- Settings responses intentionally mask secrets; tokens and API keys are represented with `*_set` flags rather than plaintext.
- Do not expose stored secrets in new responses, logs, or UI.
- If LAN access is enabled without a token, the app treats that as a security risk.

## Agent working rules for this repo
- Do not invent test, lint, or typecheck commands that are not actually configured.
- Do not claim a single-test workflow exists unless one is added later.
- Do not migrate the frontend to a framework as part of unrelated work.
- Do not move business logic into route files just because it is convenient.
- Do not forget `docs/API.md` when API behavior changes.
- Do not assume runtime data lives in the repo when the app is running frozen.

## Good default workflow
1. Read `CLAUDE.md` and the relevant nearby module.
2. Identify whether the change belongs in `app/api/routes`, `app/core`, or `app/web`.
3. Make the smallest change that matches existing patterns.
4. Run `python main.py`.
5. Exercise the changed flow manually.
6. Verify `/docs` if API behavior changed.
7. Update `docs/API.md` when applicable.
When in doubt, optimize for accuracy and consistency with the current codebase, not generic framework best practices from other projects.
