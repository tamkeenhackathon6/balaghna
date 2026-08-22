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
