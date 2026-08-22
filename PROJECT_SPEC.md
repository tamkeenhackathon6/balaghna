# BALIGHNA Project Specification

## 1. Project identity

- English name: BALIGHNA
- Arabic name: بلّغنا
- Slogan: بلّغنا، والباقي علينا
- Purpose: smart management, follow-up, and routing of public-service complaints.

## 2. Core purpose

BALIGHNA receives public-service complaints from citizens, identifies the most relevant category, determines urgency and responsible administrative entity, routes the complaint to that entity, and tracks its progress until resolution.

## 3. Routing principle (core rule)

Complaints must ultimately be routed to one of the official participating entities.

Examples:

- garbage → مديرية الخدمات المحلية
- street light → مديرية الخدمات المحلية
- sidewalk → مديرية الخدمات المحلية
- pothole → مديرية الخدمات المحلية
- complaint about municipality performance → مديريات المجالس المحلية والإدارة المحلية
- development need / regional priority → مديرية التخطيط والتنمية المحلية
- building / zoning / land use → مديرية التنظيم والتخطيط العمراني
- infrastructure project / technical maintenance → مديرية الشؤون الفنية
- local budget / revenues / expenses → مديرية الشؤون المالية
- administrative violation / negligence → مديرية الرقابة والتفتيش
- cross-entity or governorate-wide problem → المحافظات
- direct local municipal execution → مجالس المدن والبلديات والوحدات الإدارية

This mapping is required for all future complaint-routing logic and will later be implemented by the smart routing/analyzer component.

## 4. Official participating entities

### 1. مديرية الخدمات المحلية
Responsibilities:
- النفايات
- النظافة
- الحدائق
- الأرصفة
- الإنارة
- الحفر
- الخدمات اليومية

### 2. مديريات المجالس المحلية والإدارة المحلية
Responsibilities:
- متابعة أداء الوحدات الإدارية
- شكاوى المواطنين المتعلقة بالإدارة المحلية
- متابعة المجالس المحلية

### 3. مديرية التخطيط والتنمية المحلية
Responsibilities:
- تحديد احتياجات المناطق
- ترتيب الأولويات
- متابعة المشاريع
- التنمية المحلية

### 4. مديرية التنظيم والتخطيط العمراني
Responsibilities:
- مشاكل التنظيم
- البناء
- الطرق المرتبطة بالتنظيم العمراني
- استعمالات الأراضي
- المخططات التنظيمية

### 5. مديرية الشؤون الفنية
Responsibilities:
- المشاريع الخدمية
- البنية التحتية
- الصيانة الفنية
- متابعة تنفيذ المشاريع

### 6. مديرية الشؤون المالية
Responsibilities:
- الموازنات المحلية
- الإيرادات
- النفقات
- متابعة الموارد
- القضايا المالية المحلية

### 7. مديرية الرقابة والتفتيش
Responsibilities:
- متابعة الشكاوى
- المخالفات
- مراقبة أداء الجهات المحلية
- التقصير الإداري

### 8. المحافظات
Responsibilities:
- استقبال ومتابعة المشاكل على مستوى المحافظة
- تنسيق الحلول بين الجهات
- المشاكل العابرة لأكثر من جهة

### 9. مجالس المدن والبلديات والوحدات الإدارية
Responsibilities:
- الجهة التنفيذية الأقرب للمواطن
- الخدمات اليومية المحلية
- تنفيذ أعمال الصيانة والخدمات
- معالجة المشاكل المباشرة ضمن الوحدة الإدارية

## 5. Architecture

Project structure:

- app/
  - main.py
  - config.py
  - database.py
  - models/
  - schemas/
  - routers/
  - services/
  - templates/
  - static/
  - seed.py
- data/
- requirements.txt
- .env.example
- README.md
- PROJECT_SPEC.md
- PROGRESS.md

The application uses:

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite
- Pydantic
- Jinja2
- Tailwind CSS
- Vanilla JavaScript

## 6. Database

Database path:

- data/app.db

ORM:

- SQLAlchemy ORM
- SQLite as the local database engine

Core tables include:

- users
- categories
- departments
- complaints
- comments
- complaint_updates

## 7. Roles

User roles:

- citizen
- admin

Authentication and authorization for Phase 2 use secure session-based access with hashed passwords. Public registration always creates a citizen account. Admin-only pages are protected and only visible to authenticated users with the admin role. Citizen users are denied access to admin-only functionality.

## 8. Complaint lifecycle

1. Citizen submits complaint.
2. Category is associated.
3. Priority is assigned.
4. Department is determined by routing rule.
5. Complaint is assigned and tracked.
6. Updates and comments are recorded.
7. Complaint is resolved and closed.

## 9. Statuses

- new
- assigned
- in_progress
- resolved
- closed

## 10. Priorities

- low
- medium
- high
- urgent

## 11. Department model and scope values

Department fields:

- id
- name
- slug
- description
- scope
- created_at
- updated_at

Scope values:

- directorate
- governorate
- local_unit

Suggested mappings:

- المحافظات → governorate
- مجالس المدن والبلديات والوحدات الإدارية → local_unit
- others → directorate

## 12. Complaint model fields

- id
- user_id
- category_id
- department_id
- title
- description
- address
- area
- governorate
- latitude
- longitude
- image_path
- priority
- status
- routing_reason
- routing_confidence
- assigned_at
- resolved_at
- created_at
- updated_at

## 13. Demo data

The seed process creates demo users and realistic Arabic complaints covering all major participating entities and routing scenarios.

## 14. Smart complaint analysis

BALIGHNA uses a local deterministic Arabic rule-based analyzer for the MVP. It normalizes common Arabic forms and Syrian colloquial wording, scores official routing groups by matched keywords and applies documented routing precedence.

The analyzer suggests an existing category, priority, one official participating entity, matched keywords, a heuristic confidence value, and a routing reason. It is not a trained neural network and does not call paid external APIs.

When a citizen accepts a suggestion, the server re-runs the local analysis before saving the complaint. The suggested official department, category, priority, routing reason, confidence, assignment timestamp, and an automatic-routing timeline event are saved. Admins retain authority to correct the assigned official entity, with previous routing history preserved.
