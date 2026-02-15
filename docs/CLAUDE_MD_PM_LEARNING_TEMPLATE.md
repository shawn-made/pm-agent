# CLAUDE.md Template Clause — PM Learning Log

Copy the section below into any future project's CLAUDE.md to ensure the agent maintains a PM Learning Log alongside development.

---

## PM Learning Log (Required)

Maintain a `docs/PM_LEARNING_LOG.md` file throughout development. This file helps the project owner (a PM, not an engineer) build technical fluency by documenting concepts in plain language.

### Rules for the PM Learning Log

1. **Update after every task**: When you complete a task that introduces a new technical concept, pattern, or term, add an entry to the PM Learning Log.

2. **Write for a PM audience**: Explain concepts in plain English. Avoid jargon without definition. Use analogies. Include "When to use this term" example sentences.

3. **Format for each entry**:
   ```
   **Term Name**
   [1-2 sentence plain-English explanation of what it is and why it matters to this project]

   *When to use this term*: "[Example sentence a PM could say in a meeting with an engineer]"
   ```

4. **Organize by category**: Group entries under headings like Architecture, Security, Data, Frontend, Backend, Testing, DevOps, etc.

5. **Don't duplicate**: Check if a concept is already documented before adding it. Update existing entries if the project context adds new nuance.

6. **Include project-specific context**: Don't just define "REST API" generically — explain how THIS project uses REST APIs and which endpoints matter.

### When to Update

- After completing each numbered task in TASKS.md
- When introducing a new library, pattern, or architectural decision
- When a debugging session reveals something non-obvious
- When you make a decision that a PM would want to understand the rationale for

### Initial Template

Create `docs/PM_LEARNING_LOG.md` during Task 1 (scaffolding) with this structure:

```markdown
# PM Technical Learning Log — [Project Name]

A running log of technical concepts, patterns, and vocabulary learned during development.

**Last Updated**: [date]

---

## Architecture & Design Patterns

## Data & Storage

## Security & Privacy

## Frontend

## Backend & API

## Testing

## Development Process

---

## How to Use This Document

1. Before a technical meeting: scan relevant sections to refresh terminology
2. During development: new concepts are added automatically by the agent
3. When explaining the project: use the "When to use this term" suggestions
```
