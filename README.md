# BALIGHNA | بلّغنا

BALIGHNA is a smart public-service complaint management platform for the Syrian local-administration context.

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

## Geographic scope

The MVP uses Syrian governorates only: دمشق، ريف دمشق، حلب، حمص، حماة، اللاذقية، طرطوس، إدلب، درعا، السويداء، القنيطرة، دير الزور، الرقة، والحسكة. Demo complaints are concentrated around Damascus and Rural Damascus, with additional examples across Syrian governorates. Map coordinates are approximate demo locations, not survey-grade measurements.

## Ministry identity and language

BALIGHNA is presented as a digital service of the Ministry of Local Administration and Environment, Syrian Arab Republic. The supplied ministry horizontal and vertical logo assets are used as the official identity; BALIGHNA remains the service name rather than a separate logo.

Arabic is the default language. Users can switch between Arabic (RTL) and English (LTR), with the selected language stored in the session. Statuses and priorities remain machine-readable database values and are translated centrally at display time.

The global design system is defined in `app/static/css/ministry-theme.css` and applied across public, authentication, citizen, and admin surfaces. The language selector remains available without logout and preserves the current page when safe.

Authenticated citizen and admin pages share a ministry header with a clickable logo that always returns to the public landing page. Logged-in visitors remain authenticated when viewing the landing page and are offered the dashboard that matches their role.

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

To reset the local development demo database after changing seed data, remove only `data/app.db` and rerun `.venv/bin/python -m app.seed`. Do not use this reset procedure against production data.

Then open:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/

Demo accounts:

- Citizen: `citizen@example.com` / `password`
- Ministry admin: `admin@molae.gov.sy` / `password`
- Directorate demo: `local-services@molae.gov.sy` / `password`
- Field employee demo: `emp001.local-services@molae.gov.sy` / `password`

All Ministry-domain account aliases are hackathon demo identities, not operational ministry email addresses.

## Operational workflow and privacy

BALIGHNA uses four roles: `citizen`, `ministry_admin`, `directorate_admin`, and `field_employee`. Smart routing selects the responsible official department; the directorate then assigns a field employee. The employee starts work, uploads completion evidence, and explicitly confirms completion, which moves the complaint to `resolved`.

Citizen registration requires a National ID and phone number. National IDs are encrypted for Ministry-only viewing and protected with an HMAC hash for duplicate detection. Directorate and field users never receive National ID values through their screens or scoped workflow routes.

Operational routes: Ministry `/admin`, directorate `/directorate`, employee `/employee`, and citizen `/citizen`.

## Project phase

This is the Phase 10 release candidate, with a complete citizen workflow, official admin routing, timeline/comments, interactive map, live dashboard charts, deterministic Arabic analysis, demo documentation, and final QA coverage.
