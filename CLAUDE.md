# PillCheck

Camera-based medication adherence verifier. Full spec: [docs/PRD.md](docs/PRD.md).

## Guidelines
Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Structure

- [`backend/`](backend/) — FastAPI + SQLAlchemy(async) + Alembic, Postgres via Supabase. Conventions: [backend/CLAUDE.md](backend/CLAUDE.md).
- [`mobile/`](mobile/) — Expo + TypeScript + Expo Router, the React Native client. Conventions: [mobile/CLAUDE.md](mobile/CLAUDE.md).
- [`DECISIONS.md`](DECISIONS.md) — ADR log for stack/architecture choices (database, ORM, layering, mobile framework, state management).

**Adding or changing a feature (backend entity, endpoint, screen, or field)?** Use the `add-feature` skill — it's the ordered, cross-cutting checklist that keeps both projects' layering (router→service→repository on the backend, route→hook→apiClient on mobile) and SOLID boundaries consistent as the codebase grows. Don't improvise a different structure for a new feature; extend the existing one.

## Skills to use for this project

These ship with Claude Code by default (no install needed) and map to specific PRD phases (§14). Invoke by name when the matching work comes up — don't wait to be asked.

| Skill | Use for | PRD ref |
|---|---|---|
| `engineering:architecture` | ADRs for model/encoder/fusion choices (YOLO vs RT-DETR, ArcFace head, late-fusion weights) — feeds `DECISIONS.md` | §12, Q2 |
| `data:explore-data` | Profiling ePillID / C3PI / NDC sources before training | Phase 0, §11.1 |
| `data:validate-data` | Sanity-checking eval harness numbers before reporting (baseline reproduction, ePillID holdout) | Phase 0, §13 |
| `data:statistical-analysis` | Calibration, top-2 margin tuning, false-MATCH vs abstention trade-off | FR-4, §13 |
| `data:data-visualization` / `data:create-viz` | Eval report charts, confusion matrices, threshold curves | §13 |
| `data:build-dashboard` | Portfolio dashboard of success metrics | §13 |
| `engineering:debug` | Detector/segmentation/pipeline failures | Phase 2 |
| `design:accessibility-review` | WCAG 2.1 AA pass on the app UI | FR-8, §8 |
| `engineering:testing-strategy` | Test plan for the decision engine (safety-critical: MATCH/MISMATCH/CANNOT IDENTIFY) | FR-4 |
| `engineering:deploy-checklist` | Before shipping the Gradio demo or Android reference app | Phase 1/3 |
| `engineering:documentation` | README, eval reports, runbooks | §12 (repo infra) |
| `engineering:code-review` | Reviewing diffs before merge | ongoing |
| `engineering:tech-debt` | Periodic debt audit across phases | ongoing |
| `pytorch-patterns` | Training pipeline, model architecture, and data-loading patterns for the detector/encoder/OCR models | Phase 1/2, §12 |
| `add-feature` | Backend/mobile layering checklist for any new entity, endpoint, screen, or field | ongoing |
| `mobile-design-system` | Color palette, typography (Playfair Display/Inter), WCAG-safe pairings, and celestial-background usage for any mobile screen | FR-8, §8 |

Not pulled in: `fhir` / `clinical-trial-protocol-skill` (EHR integration is a v1 non-goal, §3), `mcp-builder`/`docx`/`pptx`/`sql-queries` (no MCP server, business docs, or SQL DB in this project's scope).
