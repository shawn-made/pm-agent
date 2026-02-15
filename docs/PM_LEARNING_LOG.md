# PM Technical Learning Log — VPMA Project

A running log of technical concepts, patterns, and vocabulary learned during VPMA development. Written in plain language for a PM audience. Use this to build fluency when discussing the project with engineers.

**Last Updated**: 2026-02-15

---

## Concepts Learned During Phase 0

### Architecture & Design Patterns

**Client-Server Architecture**
VPMA runs as two separate programs that talk to each other over HTTP. The frontend (React, port 3000) is the "client" — it shows the UI and sends requests. The backend (FastAPI, port 8000) is the "server" — it does the actual work (privacy, AI calls, storage). This separation means you could replace the frontend without touching the backend, or vice versa.

*When to use this term*: "We use a client-server architecture with the frontend and backend communicating over REST APIs."

**Abstract Interface / Factory Pattern**
Instead of writing code that directly calls Claude's API, we wrote a generic "LLM Client" interface that says "any AI provider must have a `call()` method." Then a factory function creates the right one based on settings. This means adding a new AI provider (like Ollama) only requires writing one new file — no changes to existing code.

*When to use this term*: "The LLM client uses a factory pattern with abstract interfaces, so swapping providers is a configuration change, not a code change."

**Middleware**
Code that runs automatically on every request before it reaches the main logic. VPMA uses CORS middleware to enforce that only the frontend at localhost:3000 can talk to the backend. Think of it as a security checkpoint at the building entrance — everyone goes through it, regardless of which floor they're visiting.

*When to use this term*: "CORS is handled at the middleware level — it's not something individual endpoints need to worry about."

### Privacy & Security

**PII (Personally Identifiable Information)**
Any data that could identify a specific person: names, email addresses, phone numbers, locations, company names. VPMA's core privacy feature is ensuring PII never reaches the AI model in its original form.

**Anonymization / Re-identification (Round-Trip)**
Anonymize: replace real names with tokens (`<PERSON_1>`). Re-identify: replace tokens back with real names. The "round-trip" test verifies that doing both operations returns the exact original text. This is the fundamental correctness guarantee of the privacy system.

*When to use this term*: "The privacy proxy guarantees round-trip fidelity — anonymize then re-identify returns the original text, verified by automated tests."

**NER (Named Entity Recognition)**
A machine learning technique where a model reads text and identifies entities — people, organizations, locations. VPMA uses spaCy's `en_core_web_sm` model for this. It's not 100% accurate (ML never is), which is why we layer it with regex patterns and user-defined terms.

*When to use this term*: "We use a three-layer PII detection pipeline: deterministic regex for structured patterns, spaCy NER for contextual name detection, and user-defined custom terms as a catch-all."

**Token Vault**
A database table that stores the mapping between anonymization tokens (`<PERSON_1>`) and real values ("John Smith"). The vault is global (not per-project) so the same person always gets the same token. This is what makes re-identification possible.

### Data & Storage

**SQLite**
A database engine that stores everything in a single file (vpma.db). No separate database server to install or manage. Perfect for local tools. The tradeoff: it doesn't support multiple simultaneous writers well, so it wouldn't scale to a multi-user cloud app without replacement (typically PostgreSQL).

*When to use this term*: "We chose SQLite for zero-setup local storage. If we go multi-user in Phase 4, we'd migrate to PostgreSQL."

**Schema Forward-Compatibility**
Every database table has a `project_id` column even though Phase 0 only supports one project. This means when we add multi-project support (Phase 2), we won't need to restructure the database — just start using different project IDs.

*When to use this term*: "The schema is forward-compatible for multi-project — we won't need a migration."

**Markdown as Content Storage**
Artifact content (the actual RAID logs, reports) lives as `.md` files on disk, not in the database. The database only stores metadata (when it was created, which project, file path). Benefits: files are human-readable, work with version control (git), and can be edited outside the app.

### Frontend

**React Components**
The UI is built from reusable building blocks called components. `TextInput` is a component. `SuggestionCard` is a component. Each one manages its own state and appearance. You compose them together to build pages.

*When to use this term*: "The suggestion cards are a reusable React component — we render one per suggestion returned from the backend."

**State Management**
How the frontend tracks what's happening right now — is data loading? Did the user type something? Which tab is active? In Phase 0, each component manages its own state (simple). Larger apps often use shared state management (Redux, Context) for data that multiple components need.

**Tailwind CSS (Utility-First Styling)**
Instead of writing custom CSS files, you apply small utility classes directly to HTML elements: `class="bg-white p-4 rounded-lg shadow"`. This means "white background, padding of 4 units, rounded corners, drop shadow." Fast to write, consistent across the app, easy to change.

### Backend & API

**REST API / Endpoints**
The backend exposes specific URLs that the frontend can call. Each URL does one thing:
- `POST /api/artifact-sync` — "Here's text, give me suggestions"
- `GET /api/settings` — "What are the current settings?"
- `PUT /api/settings` — "Update these settings"
- `GET /api/health` — "Is the backend running?"

*When to use this term*: "The main flow hits the artifact-sync endpoint, which orchestrates the full pipeline: classify, anonymize, call the LLM, re-identify, and return suggestions."

**Pydantic Models (Data Validation)**
Python classes that define the exact shape of data. If the frontend sends a request missing a required field, Pydantic rejects it before any business logic runs. Think of it as a form with required fields — you can't submit without filling them in.

**Async (Asynchronous)**
Code that can start a slow operation (like an API call to Claude) and do other work while waiting for the response. Without async, the backend would freeze during every AI call. With async, it can handle multiple requests simultaneously.

### Testing

**Unit Tests vs Integration Tests**
Unit tests check one small piece in isolation ("does the regex detect emails?"). Integration tests check the full pipeline ("does text input → anonymize → LLM → re-identify → display actually work end-to-end?"). Both are essential. VPMA has 174 backend unit tests and 22 integration tests.

**Mocking**
In tests, replacing a real dependency with a fake one. Instead of making actual API calls to Claude during tests (slow, costs money, requires API key), we "mock" the LLM client to return a pre-defined response. This makes tests fast, free, and deterministic.

*When to use this term*: "All LLM tests use mocked responses — we're testing our pipeline logic, not whether Claude's API is up."

**Test Coverage**
The percentage of code lines that are executed during tests. 80%+ coverage is generally considered good. It doesn't mean the code is bug-free, but it means most paths have been exercised.

### Development Process

**RALPH Loop**
The development methodology used for this project: Prompt (tell the AI what to build) → Review (check what it produced) → Test (run automated tests) → Refine (fix issues, iterate). Each task goes through this cycle.

**Linting**
Automated code style checking. `ruff` (backend) and `eslint` (frontend) scan code for style issues, potential bugs, and inconsistencies. Like a spell-checker for code. Running the linter after every change catches problems early.

**CORS (Cross-Origin Resource Sharing)**
A browser security feature that prevents a website at one URL from making requests to a different URL unless explicitly allowed. VPMA configures CORS to allow `localhost:3000` (frontend) to call `localhost:8000` (backend). Without this, the browser would block the requests.

---

## How to Use This Document

1. **Before a technical meeting**: Scan the relevant sections to refresh terminology
2. **During development**: Add new concepts as you encounter them
3. **When explaining the project**: Use the "When to use this term" suggestions
4. **For new projects**: Copy this file as a starting template and add project-specific concepts

---

## Template: Adding New Entries

```
**Term Name**
[1-2 sentence plain-English explanation of what it is and why it matters]

*When to use this term*: "[Example sentence you could say in a meeting with an engineer]"
```
