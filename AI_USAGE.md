# AI Usage Notes

This project was initialized using a structured MVP plan focused on a stable foundation and official complaint-routing architecture.

Key decisions:

- Use FastAPI with SQLAlchemy ORM and SQLite for the hackathon MVP.
- Keep all entity routing logic aligned with the official departments in the spec.
- Seed realistic Arabic complaints to cover the main routing categories.
- Avoid over-engineering beyond the Phase 1 requirements.
- Keep the project simple enough to run locally within a short hackathon window.
- Use a local deterministic Arabic rule-based analyzer for complaint classification and official entity routing; it is not a trained neural network and uses no paid APIs.
- Normalize common Arabic forms and Syrian colloquial vocabulary, then score only the seeded official participating entities using documented routing precedence.

## Application AI

When configured locally, BALIGHNA uses Qwen3 4B through Ollama (`qwen3:4b`) for Arabic/Syrian-colloquial complaint category, priority, and official routing suggestions. Ollama receives only complaint text and optional area/governorate. All model output is validated against existing categories, valid priorities, and the official department allowlist; invalid or unavailable AI responses fall back to the local deterministic analyzer.

## Development assistance

GitHub Copilot was used as an implementation assistant during development for code, templates, tests, and documentation. The application routing logic itself is explicit, local, deterministic, and reviewable in `app/services/analyzer_service.py`; Copilot is not part of the runtime request path.
