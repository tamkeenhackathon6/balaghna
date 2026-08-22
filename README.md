# BALIGHNA | بلّغنا

BALIGHNA is a smart public-service complaint management platform for the Ministry of Local Administration.

## Mission

Citizens can report public-service issues, and the platform routes each complaint to the most appropriate official administrative entity for follow-up and resolution.

## Official participating entities

The system is built around the official departments that must receive complaints:

1. مديرية الخدمات المحلية
2. مديريات المجالس المحلية والإدارة المحلية
3. مديرية التخطيط والتنمية المحلية
4. مديرية التنظيم والتخطيط العمراني
5. مديرية الشؤون الفنية
6. مديرية الشؤون المالية
7. مديرية الرقابة والتفتيش
8. المحافظات
9. مجالس المدن والبلديات والوحدات الإدارية

This routing model is a core principle of BALIGHNA: complaints are not left unassigned; they are directed to the responsible entity based on category, issue type, and local administrative context.

## Tech stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite
- Pydantic
- Jinja2
- Tailwind CSS
- Vanilla JavaScript

## Run locally

```bash
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

Then open:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/

## Project phase

This is Phase 1, focused on foundational architecture, database, official entities, routing rules, and seeded demo data.
