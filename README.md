# BALIGHNA | بلّغنا

BALIGHNA is a smart public-service complaint management platform for the Ministry of Local Administration.

## Mission

Citizens can report public-service issues, and the platform routes each complaint to the most appropriate official administrative entity for follow-up and resolution.

## كيف يتم توجيه البلاغ؟

يتبع البلاغ مساراً واضحاً من لحظة الإرسال حتى الإغلاق:

المواطن يرسل البلاغ → يصنّف بلّغنا النص العربي محلياً → تُقترح الأولوية والجهة المسؤولة → يراجع المشرف التوجيه عند الحاجة → تتم المعالجة → يتابع المواطن النتيجة حتى الحل أو الإغلاق.

محرك التحليل في النسخة التجريبية محلي وحتمي ويعتمد على قواعد عربية وكلمات مفتاحية سورية شائعة. لا يستخدم خدمات مدفوعة أو نموذجاً عصبياً مدرباً. عند اعتماد المواطن للاقتراح، يحفظ النظام التصنيف والأولوية والجهة وسبب التوجيه وثقة تحليل استدلالية، ويستطيع المشرف تعديل التوجيه مع الاحتفاظ بسجل كامل للتغييرات.

## Official participating entities

The system is built around the official departments that must receive complaints:

1. **مديرية الخدمات المحلية**: النفايات، النظافة، الحدائق، الأرصفة، الإنارة، الحفر والخدمات اليومية.
2. **مديريات المجالس المحلية والإدارة المحلية**: أداء الوحدات الإدارية وشكاوى المواطنين المتعلقة بالإدارة المحلية.
3. **مديرية التخطيط والتنمية المحلية**: احتياجات المناطق، ترتيب أولويات المشاريع والتنمية المحلية.
4. **مديرية التنظيم والتخطيط العمراني**: التنظيم، البناء، المخططات واستعمالات الأراضي.
5. **مديرية الشؤون الفنية**: البنية التحتية، الصيانة الفنية، المشاريع ومتابعة التنفيذ.
6. **مديرية الشؤون المالية**: الموازنات، الرسوم، الإيرادات، النفقات والموارد المحلية.
7. **مديرية الرقابة والتفتيش**: المخالفات، التقصير الإداري ومتابعة أداء الجهات.
8. **المحافظات**: المشاكل العابرة للجهات أو الواقعة على مستوى المحافظة.
9. **مجالس المدن والبلديات والوحدات الإدارية**: التنفيذ المحلي المباشر والخدمات ضمن الوحدة الإدارية.

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
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.seed
.venv/bin/uvicorn app.main:app --reload
```

Then open:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/

Demo accounts:

- Citizen: `citizen@example.com` / `password`
- Admin: `admin@example.com` / `password`

## Project phase

This is the Phase 10 release candidate, with a complete citizen workflow, official admin routing, timeline/comments, interactive map, live dashboard charts, deterministic Arabic analysis, demo documentation, and final QA coverage.
