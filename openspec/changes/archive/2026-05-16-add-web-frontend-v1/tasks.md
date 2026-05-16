## 1. OpenSpec

- [x] 1.1 Create the Web v1 OpenSpec proposal, design, task list, and spec increment from the Claude Design handoff.
- [x] 1.2 Validate `add-web-frontend-v1` with `openspec-cn validate add-web-frontend-v1`.
- [x] 1.3 Review the proposal against the design handoff before implementation starts.

## 2. Frontend Project Setup

- [x] 2.1 Add a `web/` frontend project using the repository's zero-dependency static frontend approach for v1.
- [x] 2.2 Wire Web build commands into the existing `pnpm ui:build` and/or `python3 bootstrap.py ui-build` flow.
- [x] 2.3 Add local mock mode so Web v1 runs without API keys or network access.

## 3. Design System

- [x] 3.1 Implement global design tokens for color, typography, radius, spacing, density, and status colors from the handoff.
- [x] 3.2 Implement the fixed three-column app shell with independent column scrolling and sticky main header.
- [x] 3.3 Implement shared buttons, icon buttons, tabs, badges, form fields, modal shell, overlay shell, and status indicators.
- [x] 3.4 Preserve the handoff's restrained animation set: pulse, pulseRing, blink, fadeIn, and toastIn.

## 4. Sidebar

- [x] 4.1 Implement brand mark, product name, version subtitle, and New Run action.
- [x] 4.2 Implement searchable run list grouped by date bucket with active, hover, running, success, and failed states.
- [x] 4.3 Implement footer links for history, settings, docs, and local workspace user row.

## 5. Main Workspace

- [x] 5.1 Implement empty hero and five agent cards.
- [x] 5.2 Implement source-text and prompt-only input tabs, including upload/paste affordances and prompt-only preview notice.
- [x] 5.3 Implement generation parameter fields: topic, audience, style, user id, and max iterations.
- [x] 5.4 Implement output modality cards for Text, Image, and Video with ready/beta/coming-soon badges.
- [x] 5.5 Implement generate bar with runtime summary and primary action.
- [x] 5.6 Implement running progress frame with run id, iteration pill, stop/retry controls, student thinking card, timeline rows, and failed-stage error block.
- [x] 5.7 Implement success result tabs and article preview with metadata, synopsis, headings, paragraphs, annotations, blockquote, and actions.
- [x] 5.8 Implement image and video placeholder result surfaces without real backend calls.

## 6. Meta Panel

- [x] 6.1 Implement empty/filled meta panel with runtime, pipeline, and user memory summary.
- [x] 6.2 Implement running/success/failed run metadata panel with run id, backend, model, user, audience, and start time.
- [x] 6.3 Implement iteration rows with clarity segmented bars.
- [x] 6.4 Implement fact-check card states for pending, success with warnings, and failed/no result.
- [x] 6.5 Implement memory update cards and artifacts summary.

## 7. Overlays and Settings

- [x] 7.1 Implement settings modal with provider selection, API key, base URL, model, max iterations, clarity threshold, data directory, connection status, and save/test actions.
- [x] 7.2 Implement history overlay with search, table rows, status/backend/time columns, run selection, and close behavior.
- [x] 7.3 Implement Chinese/English UI string switching for interface chrome.

## 8. API and Data Integration

- [x] 8.1 Define Web client data contracts for runs, stages, iterations, memory updates, runtime, artifacts, and article blocks.
- [x] 8.2 Implement a mock client using the handoff seed data.
- [x] 8.3 Add API client seams for runtime summary, run list, run creation, progress events, run detail, settings save/test, and artifact retrieval.
- [x] 8.4 Connect available backend endpoints while preserving mock fallback for local demo and tests.

## 9. Tests and Verification

- [x] 9.1 Add tests for state transitions, modality locking, input validation, and mock client behavior.
- [x] 9.2 Add build verification for the Web app.
- [x] 9.3 Expose local preview and smoke-check empty/filled, running, success, failed, settings modal, and history overlay implementation paths.
- [x] 9.4 Update README with Web v1 local development, build, and mock-mode instructions.
