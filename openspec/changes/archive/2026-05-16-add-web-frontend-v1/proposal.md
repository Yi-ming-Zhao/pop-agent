# Add Web v1 Frontend

## 为什么

Pop Agent already has a CLI, TUI, FastAPI-ready service surface, user configuration, run storage, and a multi-agent popular-science generation workflow. The next product step is a Web v1 interface that makes the same workflow visible as an editorial workspace: users can paste or upload source material, configure the target reader, watch the five-agent pipeline run, inspect the final article, and review run metadata, fact-check results, memory updates, and artifacts.

The authoritative design input for this change is the Claude Design handoff at:

```text
D:\bit\2_2\pop-agent file\design_handoff_pop_agent
```

That handoff is a high-fidelity prototype, not production code. The implementation must reproduce the visual language, layout, states, interaction model, and component behavior from the handoff using this repository's target frontend stack and build flow.

## 变更内容

- Add a Web v1 frontend matching the handoff's high-fidelity academic-editor design: warm paper surfaces, ruled lines, dense but calm information architecture, serif headings, sans body text, and monospace metadata.
- Provide a three-column single-screen workspace with left run navigation, central generation workspace, and right metadata panel.
- Support the complete Web v1 state machine: empty, filled, running, success, failed, and retry from failure.
- Support source-text and prompt-only input modes, generation parameters, output modality selection, runtime summary, and a primary generate action.
- Display real or mock-backed multi-agent progress stages: memory, Teacher, Student, Aggregator, Fact check, Editor, and Done.
- Display final text results in an article preview matching the prototype's editorial typography and actions.
- Include image and video modality entry points as placeholders only, preserving the handoff's locked/beta behavior.
- Provide settings and history overlays matching the handoff interaction surfaces.
- Integrate the Web frontend into the existing source install/build workflow so local users can build it through project commands.

## 非目标

- This change does not add real image or video generation backends. Image remains beta/placeholder and video remains coming soon.
- This change does not replace the CLI or TUI. Web v1 reuses the same service concepts and should not fork generation logic.
- This change does not directly copy the prototype's browser-Babel source into production unchanged.
- This change does not introduce a marketing landing page. The first screen must be the usable workspace.
- This change does not require a hosted cloud deployment target; local development and build are sufficient for v1.

## 设计来源约束

- The design handoff is the source of truth for layout, tokens, component surfaces, states, copy hierarchy, and animations.
- Visual implementation must preserve the handoff's three-column grid, fixed viewport shell, independent column scrolling, panel borders, button styles, run timeline, result article styling, settings modal, and history overlay.
- Implementation may adapt component boundaries and framework details to the production codebase, but visible behavior and hierarchy must remain faithful to the handoff.
- Any deviation from the handoff must be documented in `tasks.md` or in implementation notes with a reason.
