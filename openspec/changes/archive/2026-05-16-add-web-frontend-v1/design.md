# Design

## Source Material

This design is derived from the Claude Design handoff directory:

```text
D:\bit\2_2\pop-agent file\design_handoff_pop_agent
```

The handoff includes:

- `README.md`: design language, tokens, layout rules, states, behavior, data structures, and developer notes.
- `src/styles.css`: full token and component style reference.
- `src/app.jsx`: root composition, state machine, settings/history overlays, and demo state controls.
- `src/sidebar.jsx`: left navigation, run list, inline SVG icon set, and footer actions.
- `src/workspace.jsx`: empty state, input block, parameters, modality selector, generate bar, progress timeline, result article, and modality placeholders.
- `src/meta-panel.jsx`: right metadata panel, runtime summary, iterations, fact check, memory updates, artifacts, settings modal, and history overlay.
- `src/data.js`: seed data contracts for runs, stages, iterations, memory updates, runtime, article, and localized UI strings.

The prototype is a high-fidelity visual and interaction reference. It must be translated into production components rather than copied as browser-Babel prototype code.

## Frontend Architecture

Add a dedicated Web app under a `web/` project directory. Because the repository currently has no committed frontend dependency stack, Web v1 uses a zero-dependency static implementation (`index.html`, `styles.css`, and `app.js`) that can be built by the existing Node/Python bootstrap commands. The first production pass uses local mock data while preserving API-shaped boundaries, then connects to the real FastAPI daemon when `?api=real` is used.

Recommended module boundaries:

- `web/src/index.html`: static entrypoint.
- `web/src/styles.css`: design tokens, global layout, component styles, responsive rules, and animations.
- `web/src/app.js`: root shell, state machine, mock data, API seam, sidebar, workspace, meta panel, overlays, and event binding.
- `web/scripts/build.mjs`: Node static-asset build helper.
- `web/scripts/dev.mjs`: local static preview server.

## Visual System

The app must preserve these handoff tokens:

- Surface colors: `#F7F3E8`, `#FBF8EF`, `#FFFFFF`, `#FBFAF4`.
- Text colors: `#1B1813`, `#4D4839`, `#7A7464`, `#A8A28E`.
- Lines: `#E2DCC8`, `#C9C2AA`, `#ECE7D4`.
- Accent: `#1F3A5F`, with soft accent `#E6ECF3`.
- Status colors: success `#2C5E3E`, warning `#8A5A1A`, danger `#8E2A1F`, preview `#6B5A2E`, each with matching soft backgrounds.
- Typography roles: serif for product/editorial headings and article body, sans for UI body, mono for labels, badges, run ids, timestamps, and technical metadata.
- Radius: `4px` generally, `8px` only for modal surfaces.
- Density modes: `compact`, `normal`, and `comfy` through document-level CSS variables.

The UI must avoid decorative landing-page treatment. The Web v1 first viewport is the workspace itself.

## Layout

Use a fixed-height three-column shell:

```text
248px  minmax(0, 1fr)  320px
Sidebar Main workspace Meta panel
```

At narrower desktop widths, shrink to:

```text
220px  minmax(0, 1fr)  280px
```

The page itself must not scroll. Each column scrolls independently. The main header is sticky inside the main column.

## State Machine

Implement the visible state machine from the handoff:

```text
empty -> filled -> running -> success
                  failed -> running
any state -> empty through New Run
```

State behavior:

- `empty`: show empty hero, five agent cards, input blocks, parameters, modality selector, and generate bar.
- `filled`: show the form populated with source or prompt content and generation parameters.
- `running`: show progress frame, current stage, elapsed time, current iteration, stop action, student-thinking stream, and right meta panel in running mode.
- `success`: show article result tabs, text article preview, image/video placeholders, final run metadata, iterations, fact check, memory updates, and artifacts.
- `failed`: show progress frame with failed stage, error block, retry action, and right meta panel failure state.

## Data Contracts

The Web frontend should model these concepts from the handoff:

- `Run`: id, title, topic, audience, status, relative time, backend, and date bucket.
- `Stage`: stage id, display label, message, sub-message, duration, and timing.
- `Iteration`: round number, clarity, interest, must-fix count, nice-to-have count, and duration.
- `MemoryUpdate`: add/update operation, memory section, title, summary, tags, and confidence.
- `Runtime`: backend, model, base URL, data directory, max iterations, and clarity threshold.
- `Article`: title, synopsis, metadata, structured body blocks, annotations, and export actions.

Use mock fixtures only as a temporary local source. Component props and service functions should be shaped so real API data can replace fixtures without rewriting the UI.

## API Integration Direction

Web v1 should be built around a thin client API layer:

- Load runtime and configuration summary.
- List recent runs and grouped history.
- Create a text generation run from source or prompt input.
- Subscribe to progress events through SSE or polling if streaming is not yet available.
- Fetch final run details, article content, fact-check results, memory updates, and artifact paths.
- Save/test settings through existing user configuration semantics.

If backend endpoints are incomplete at implementation time, provide a local mock mode that uses the handoff seed data while keeping function names and response shapes API-like.

## Interaction Details

The implementation must include:

- New Run button with keyboard hint.
- Searchable grouped run list.
- Source-text tab and prompt-only preview tab.
- Upload/paste affordances for `.md`, `.txt`, and `.pdf` sources.
- Generation parameter fields for topic, audience, style, user id, and max iterations.
- Modality selector with Text ready, Image beta placeholder, and Video coming soon.
- Generate bar with backend, model, iteration, and memory summary.
- Timeline rows with done/current/pending/failed states.
- Running-state student thinking card.
- Result tabs for text/image/video.
- Article preview with editorial typography, synopsis, annotations, blockquote, and action bar.
- Right meta panel for runtime, pipeline, user memory, run metadata, iterations, fact check, memory updates, and artifacts.
- Settings modal with provider cards, API key, base URL, model, numeric parameters, data directory, connection status, and save/test actions.
- History overlay with search, rows, status, backend, time, selection, and close behavior.
- Chinese/English UI language switch for interface strings while generated article content can remain Chinese.

## Accessibility and Responsiveness

- Buttons, tabs, modals, and overlay rows must be keyboard reachable.
- Modal and history overlay must support escape-to-close and click-outside close.
- Interactive controls must expose labels or accessible names.
- Text must not overflow buttons, cards, panels, or the fixed column layout.
- Hover, active, disabled, focus, success, warning, and danger states must be visually distinct.
- The primary v1 target is desktop. Narrow desktop responsiveness must preserve the three-column shell down to the handoff breakpoint.

## Build and Verification

The frontend must be included in the project build path:

- `pnpm ui:build` or the existing `python3 bootstrap.py ui-build` must build the Web frontend.
- The repository test command must not require real API keys.
- Mock mode must run without network access.
- Visual verification should include at least one screenshot or manual check for empty/filled, running, success, failed, settings modal, and history overlay states.
