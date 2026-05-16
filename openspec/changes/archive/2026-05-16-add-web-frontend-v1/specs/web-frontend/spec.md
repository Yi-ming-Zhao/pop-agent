# web-frontend 规格增量

## 新增需求

### Requirement: Web v1 Workspace Entry
The system MUST provide a Web v1 frontend workspace for Pop Agent that opens directly into the generation interface rather than a marketing or landing page.

#### Scenario: User opens the Web frontend
- **Given** the Web frontend is running locally
- **When** the user opens the Web app
- **Then** the system MUST show the Pop Agent three-column workspace
- **And** the first viewport MUST include the left run sidebar, central generation workspace, and right metadata panel
- **And** the interface MUST visually follow the Claude Design handoff's warm paper academic-editor design language

#### Scenario: Empty workspace is visible on first use
- **Given** no active run is selected
- **When** the workspace loads
- **Then** the main column MUST show the empty hero and five agent cards for Teacher, Student, Aggregator, Fact check, and Editor
- **And** the generation form MUST remain available below the empty hero

### Requirement: Handoff-Faithful Layout and Visual Tokens
The Web frontend MUST implement the high-fidelity design tokens and layout from the design handoff.

#### Scenario: Three-column layout is rendered
- **Given** the viewport is desktop sized
- **When** the Web app renders
- **Then** the system MUST use a fixed-height three-column layout with sidebar, main workspace, and meta panel
- **And** the page itself MUST NOT scroll
- **And** each column MUST scroll independently when its content overflows

#### Scenario: Design tokens are applied
- **Given** the Web app renders any workspace state
- **When** the user views the interface
- **Then** the system MUST use the handoff surface, text, line, accent, status, radius, and typography tokens
- **And** headings and article body MUST use the serif role
- **And** UI body text MUST use the sans role
- **And** labels, badges, run ids, timestamps, and technical metadata MUST use the mono role

#### Scenario: Density can be represented
- **Given** the app density is compact, normal, or comfy
- **When** the density mode changes
- **Then** the system MUST adjust padding and base font sizes through document-level styling
- **And** the layout MUST remain stable without overlapping text or controls

### Requirement: Sidebar Run Navigation
The Web frontend MUST provide a left sidebar matching the handoff's brand, run navigation, and footer structure.

#### Scenario: User searches run history
- **Given** the sidebar contains recent runs
- **When** the user enters text in the sidebar search box
- **Then** the run list MUST filter by run title, topic, audience, or run id
- **And** matching runs MUST remain grouped by date bucket

#### Scenario: User selects a run
- **Given** the sidebar displays multiple runs
- **When** the user selects a run row
- **Then** that run row MUST become active
- **And** the main workspace and meta panel MUST display the selected run's state and details

#### Scenario: User starts a new run
- **Given** the workspace is in any state
- **When** the user activates New Run
- **Then** the workspace MUST return to the empty/new-run form state

### Requirement: Input and Generation Parameters
The Web frontend MUST provide source-text and prompt-only inputs plus generation parameters from the handoff.

#### Scenario: User enters source text
- **Given** the source-text tab is active
- **When** the user types or pastes source material
- **Then** the textarea MUST accept the content
- **And** the character count MUST update
- **And** upload and paste affordances MUST be visible

#### Scenario: User switches to prompt-only mode
- **Given** the input block is visible
- **When** the user selects the prompt-only tab
- **Then** the system MUST show a shorter prompt textarea
- **And** the system MUST show the handoff's preview notice explaining that prompt-only is a preview entry until retrieval is wired

#### Scenario: User edits generation parameters
- **Given** the generation parameter block is visible
- **When** the user edits topic, audience, style, user id, or max iterations
- **Then** the generate bar summary MUST reflect the selected backend, model, iterations, and memory user id

### Requirement: Output Modality Selector
The Web frontend MUST expose Text, Image, and Video modality cards with the handoff's status semantics.

#### Scenario: Text modality is selected
- **Given** the user selects Text
- **When** the user starts generation
- **Then** the system MUST run or mock the text generation pipeline
- **And** the Text card MUST be marked READY

#### Scenario: Image modality is selected
- **Given** the user selects Image
- **When** the workspace displays modality details
- **Then** the Image card MUST be marked BETA or PLACEHOLDER
- **And** the system MUST NOT claim that real image generation is available

#### Scenario: Video modality is selected
- **Given** the user selects Video
- **When** the workspace displays modality details
- **Then** the Video card MUST be marked COMING SOON
- **And** the primary generation behavior MUST remain disabled or placeholder-only for video

### Requirement: Generation State Machine
The Web frontend MUST implement the handoff state machine for empty, filled, running, success, and failed states.

#### Scenario: Generation starts
- **Given** the user has entered valid source or prompt content
- **When** the user activates Generate
- **Then** the workspace MUST enter the running state
- **And** the main column MUST show a progress frame with run id, iteration count, elapsed time, and stop action
- **And** the meta panel MUST switch from runtime summary to run metadata

#### Scenario: Generation succeeds
- **Given** a run is in the running state
- **When** the run completes successfully
- **Then** the workspace MUST enter the success state
- **And** the result area MUST show text, image, and video tabs
- **And** the text tab MUST show the final article preview

#### Scenario: Generation fails
- **Given** a run is in the running state
- **When** a stage fails
- **Then** the workspace MUST enter the failed state
- **And** the failed timeline row MUST show a danger treatment and readable error block
- **And** the user MUST be able to retry from the failed state

### Requirement: Progress Timeline
The Web frontend MUST show multi-agent pipeline progress using the handoff timeline.

#### Scenario: User views a running run
- **Given** the run is running
- **When** the progress frame is visible
- **Then** timeline rows MUST show memory, Teacher, Student, Aggregator, Fact check, Editor, and Done stages
- **And** rows MUST distinguish done, current, pending, and failed states
- **And** the current stage MUST use the accent color and pulse animation

#### Scenario: Student thinking is streamed or mocked
- **Given** the run is running
- **When** student feedback is available
- **Then** the progress frame MUST show a Student thinking card
- **And** highlighted phrases and cursor animation MUST match the handoff behavior

### Requirement: Result Article Preview
The Web frontend MUST render final text results as an editorial article preview matching the handoff.

#### Scenario: User views successful text result
- **Given** a run completed successfully
- **When** the text result tab is active
- **Then** the article card MUST show metadata, title, synopsis, headings, paragraphs, annotations, blockquotes, and action buttons
- **And** article typography MUST use the handoff serif styling and line-height

#### Scenario: User views image or video result tabs
- **Given** a run completed successfully
- **When** the user selects Image or Video result tabs
- **Then** the system MUST show the corresponding placeholder surface
- **And** the placeholder MUST state the backend/artifact plan without invoking unavailable generation

### Requirement: Meta Panel
The Web frontend MUST provide the right-side metadata panel from the design handoff.

#### Scenario: User views an unstarted workspace
- **Given** the workspace is empty or filled
- **When** the meta panel renders
- **Then** it MUST show runtime configuration, pipeline stages, and user memory summary

#### Scenario: User views a running or completed run
- **Given** a run is running, successful, or failed
- **When** the meta panel renders
- **Then** it MUST show run id, backend, model, user, audience, started time, iterations, fact-check state, memory updates, and artifacts as applicable

#### Scenario: Iteration clarity is displayed
- **Given** iteration data is available
- **When** the iteration rows render
- **Then** each row MUST show clarity, interest, must-fix count, and a ten-segment clarity bar

### Requirement: Settings Modal
The Web frontend MUST provide a settings modal matching the handoff.

#### Scenario: User opens settings
- **Given** the user activates the settings control
- **When** the settings modal opens
- **Then** the modal MUST show provider cards for DeepSeek, OpenAI-compatible, and Mock
- **And** it MUST show API key, base URL, model, max iterations, clarity threshold, data directory, connection status, and cancel/save/test actions

#### Scenario: User closes settings
- **Given** the settings modal is open
- **When** the user presses Escape, clicks outside the modal, or activates close/cancel
- **Then** the modal MUST close without corrupting current workspace state

### Requirement: History Overlay
The Web frontend MUST provide a searchable history overlay matching the handoff.

#### Scenario: User opens history
- **Given** the user activates the history control
- **When** the history overlay opens
- **Then** the overlay MUST show a search box and run rows with title/run id, status, backend, and time columns

#### Scenario: User selects history row
- **Given** the history overlay is open
- **When** the user selects a run row
- **Then** the overlay MUST close
- **And** the selected run MUST become active in the workspace

### Requirement: Mock Mode and API Seams
The Web frontend MUST be able to run in mock mode while preserving API-shaped integration boundaries.

#### Scenario: No backend or API key is available
- **Given** no real API key or daemon is configured
- **When** the user runs the Web frontend in mock mode
- **Then** the app MUST render the full workspace and state transitions using local fixtures
- **And** it MUST NOT require network access

#### Scenario: Backend endpoints become available
- **Given** the backend exposes compatible endpoints
- **When** the Web client is configured for real mode
- **Then** run creation, progress, results, settings, and history MUST flow through the Web client API layer
- **And** UI components MUST not directly own backend-specific request logic

### Requirement: Web Build Integration
The Web frontend MUST be included in the repository build and verification flow.

#### Scenario: User builds the project
- **Given** the Web frontend exists
- **When** the user runs the project's UI build command
- **Then** the system MUST build the Web frontend without requiring real model credentials

#### Scenario: Tests run in CI or local development
- **Given** the repository tests are executed
- **When** no API key is configured
- **Then** Web frontend tests and mock-mode tests MUST still pass
