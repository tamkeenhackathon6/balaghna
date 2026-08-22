from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models.category import Category
from app.models.complaint import Complaint
from app.models.department import Department
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OFFICIAL_DEPARTMENTS = [
    {
        "name": "مديرية الخدمات المحلية",
        "slug": "services-local",
        "description": "النفايات، النظافة، الحدائق، الأرصفة، الإنارة، الحفر، والخدمات اليومية.",
        "scope": "directorate",
    },
    {
        "name": "مديريات المجالس المحلية والإدارة المحلية",
        "slug": "local-councils-admin",
        "description": "متابعة أداء الوحدات الإدارية، شكاوى المواطنين المتعلقة بالإدارة المحلية، ومتابعة المجالس المحلية.",
        "scope": "directorate",
    },
    {
        "name": "مديرية التخطيط والتنمية المحلية",
        "slug": "planning-local-development",
        "description": "تحديد احتياجات المناطق، ترتيب الأولويات، ومتابعة المشاريع والتنمية المحلية.",
        "scope": "directorate",
    },
    {
        "name": "مديرية التنظيم والتخطيط العمراني",
        "slug": "urban-planning",
        "description": "مشاكل التنظيم، البناء، الطرق المرتبطة بالتنظيم العمراني، استعمالات الأراضي، والمخططات التنظيمية.",
        "scope": "directorate",
    },
    {
        "name": "مديرية الشؤون الفنية",
        "slug": "technical-affairs",
        "description": "المشاريع الخدمية، البنية التحتية، الصيانة الفنية، ومتابعة تنفيذ المشاريع.",
        "scope": "directorate",
    },
    {
        "name": "مديرية الشؤون المالية",
        "slug": "financial-affairs",
        "description": "الموازنات المحلية، الإيرادات، النفقات، ومتابعة الموارد والقضايا المالية المحلية.",
        "scope": "directorate",
    },
    {
        "name": "مديرية الرقابة والتفتيش",
        "slug": "inspection-audit",
        "description": "متابعة الشكاوى، المخالفات، مراقبة أداء الجهات المحلية، والتقصير الإداري.",
        "scope": "directorate",
    },
    {
        "name": "المحافظات",
        "slug": "governorates",
        "description": "استقبال ومتابعة المشاكل على مستوى المحافظة، وتنسيق الحلول بين الجهات.",
        "scope": "governorate",
    },
    {
        "name": "مجالس المدن والبلديات والوحدات الإدارية",
        "slug": "municipal-local-units",
        "description": "الجهة التنفيذية الأقرب للمواطن، الخدمات اليومية المحلية، ومتابعة العيوب المباشرة داخل الوحدة الإدارية.",
        "scope": "local_unit",
    },
]

SEED_CATEGORIES = [
    ("نفايات ونظافة", "waste-sanitation", "القمامة والتراكم والبيئة"),
    ("حدائق", "parks", "المساحات الخضراء والحدائق العامة"),
    ("أرصفة", "sidewalks", "أرصفة وممرات المشاة"),
    ("إنارة", "lighting", "أعمدة الإنارة والأنوار العامة"),
    ("حفر وطرق محلية", "potholes-local-roads", "حفرة ومشكلات الطرق المحلية"),
    ("خدمات يومية", "daily-services", "الخدمات اليومية والعيوب التشغيلية"),
    ("شكوى على وحدة إدارية", "complaint-against-unit", "تدني الخدمة أو التأخر في الوحدة الإدارية"),
    ("أداء جهة محلية", "local-entity-performance", "أداء الجهة المحلية"),
    ("احتياجات منطقة", "area-needs", "احتياجات المنطقة والمشاريع اللازمة"),
    ("أولوية مشروع خدمي", "service-project-priority", "أولوية مشاريع الخدمات"),
    ("تنظيم عمراني", "urban-planning", "تنظيم عمراني ومخططات"),
    ("مخالفة بناء", "building-violation", "مخالفة بناء أو توسع غير مرخص"),
    ("استعمالات أراضٍ", "land-use", "استعمالات الأراضي"),
    ("طرق وتنظيم", "roads-urban-regulation", "طرق وتخطيط عام"),
    ("مشروع خدمي", "service-project", "مشروع خدمي يحتاج تنفيذ"),
    ("بنية تحتية", "infrastructure", "بنية تحتية وشبكات"),
    ("صيانة", "maintenance", "صيانة فنية ومشاكل تشغيلية"),
    ("موازنة محلية", "local-budget", "الموازنة والمالية المحلية"),
    ("إيرادات ونفقات", "revenues-expenses", "إيرادات ونفقات"),
    ("موارد محلية", "local-resources", "موارد محلية"),
    ("مخالفة إدارية", "administrative-violation", "مخالفة إدارية أو خرق أنظمة"),
    ("شكوى رقابية", "oversight-complaint", "شكوى رقابية أو متابعة"),
    ("تقصير جهة محلية", "local-entity-shortfall", "تقصير جهة محلية"),
    ("مشكلة على مستوى المحافظة", "governorate-level-problem", "مشكل على مستوى المحافظة"),
    ("مشكلة بلدية محلية", "municipal-local-problem", "مشكلة بلدية مباشرة"),
    ("أخرى", "other", "فئة أخرى غير مصنفة"),
]

DEMO_COMPLAINTS = [
    {
        "title": "تراكم نفايات في أحد شوارع المزة",
        "description": "تراكمت النفايات في المزة منذ عدة أيام وبدأت تؤثر على السكان والمارة.",
        "address": "المزة، أوتوستراد المزة",
        "area": "المزة",
        "governorate": "دمشق",
        "latitude": 33.5058,
        "longitude": 36.2648,
        "category": "نفايات ونظافة",
        "priority": "high",
        "status": "new",
        "department": "مديرية الخدمات المحلية",
        "routing_reason": "تم التوجيه إلى مديرية الخدمات المحلية لأن البلاغ متعلق بتراكم النفايات والنظافة.",
        "routing_confidence": 0.96,
    },
    {
        "title": "عطل في عمود إنارة في الميدان",
        "description": "توقفت إنارة أحد الشوارع في الميدان، مما يهدد السلامة في المساء.",
        "address": "الميدان، شارع الزاهرة",
        "area": "الميدان",
        "governorate": "دمشق",
        "latitude": 33.4877,
        "longitude": 36.2934,
        "category": "إنارة",
        "priority": "high",
        "status": "assigned",
        "department": "مديرية الخدمات المحلية",
        "routing_reason": "تم التوجيه إلى مديرية الخدمات المحلية لأن البلاغ متعلق بإنارة عامة معطلة.",
        "routing_confidence": 0.92,
    },
    {
        "title": "حفرة كبيرة في الطريق في كفرسوسة",
        "description": "توجد حفرة عميقة في كفرسوسة تؤثر على حركة السيارات والمشاة قرب المدرسة.",
        "address": "كفرسوسة، الطريق الرئيسي",
        "area": "كفرسوسة",
        "governorate": "ريف دمشق",
        "latitude": 33.4868,
        "longitude": 36.3537,
        "category": "حفر وطرق محلية",
        "priority": "urgent",
        "status": "in_progress",
        "department": "مديرية الخدمات المحلية",
        "routing_reason": "تم التوجيه إلى مديرية الخدمات المحلية لأن البلاغ يتعلق بحفرة وطرق محلية تحتاج تدخل فوري.",
        "routing_confidence": 0.97,
    },
    {
        "title": "رصيف متضرر في ركن الدين",
        "description": "الرصيف مكسور في أكثر من موقع ويشكل خطرًا للمشاة.",
        "address": "ركن الدين، شارع سليم",
        "area": "ركن الدين",
        "governorate": "دمشق",
        "latitude": 33.5262,
        "longitude": 36.2845,
        "category": "أرصفة",
        "priority": "high",
        "status": "new",
        "department": "مديرية الخدمات المحلية",
        "routing_reason": "تم التوجيه إلى مديرية الخدمات المحلية لأن البلاغ متعلق برصيف متضرر يحتاج صيانة.",
        "routing_confidence": 0.91,
    },
    {
        "title": "تأخر الوحدة الإدارية في معالجة طلبات المقيمين",
        "description": "تأخر فريق الوحدة الإدارية في الرد على طلبات الصيانة ورفع العيوب في الحي.",
        "address": "جرمانا، شارع الوحدة",
        "area": "جرمانا",
        "governorate": "ريف دمشق",
        "latitude": 33.5301,
        "longitude": 36.3521,
        "category": "شكوى على وحدة إدارية",
        "priority": "medium",
        "status": "assigned",
        "department": "مديريات المجالس المحلية والإدارة المحلية",
        "routing_reason": "تم التوجيه إلى مديريات المجالس المحلية والإدارة المحلية لأن البلاغ يتعلق بأداء الوحدة الإدارية وتقصيرها في المتابعة.",
        "routing_confidence": 0.94,
    },
    {
        "title": "المنطقة تحتاج مشروع خدمياً جديداً بسبب النمو السكاني",
        "description": "ازداد عدد السكان في المنطقة دون زيادة في الخدمات الأساسية مثل المياه والحدائق.",
        "address": "صحنايا، الطريق العام",
        "area": "صحنايا",
        "governorate": "ريف دمشق",
        "latitude": 33.4697,
        "longitude": 36.2673,
        "category": "احتياجات منطقة",
        "priority": "high",
        "status": "new",
        "department": "مديرية التخطيط والتنمية المحلية",
        "routing_reason": "تم التوجيه إلى مديرية التخطيط والتنمية المحلية لأن البلاغ يصف احتياجاً من احتياجات المنطقة وتحديد أولويات المشاريع.",
        "routing_confidence": 0.9,
    },
    {
        "title": "أولوية مشروع خدمي لمجمع خدمية للباحثين",
        "description": "المنطقة تعاني من نقص في مرافق المرافق الخدمية، ويحتاج المشروع إلى دعم تنموي.",
        "address": "البرامكة، شارع الجامعة",
        "area": "البرامكة",
        "governorate": "دمشق",
        "latitude": 33.5148,
        "longitude": 36.2829,
        "category": "أولوية مشروع خدمي",
        "priority": "high",
        "status": "new",
        "department": "مديرية التخطيط والتنمية المحلية",
        "routing_reason": "تم التوجيه إلى مديرية التخطيط والتنمية المحلية لأن البلاغ يتعلق بأولوية مشروع خدمية وتنمية محلية.",
        "routing_confidence": 0.88,
    },
    {
        "title": "مخالفة بناء في أرض سكنية",
        "description": "تم بناء طابق إضافي دون تراخيص وفق الأنظمة المعتمدة.",
        "address": "ضاحية قدسيا، شارع البلدية",
        "area": "ضاحية قدسيا",
        "governorate": "ريف دمشق",
        "latitude": 33.5181,
        "longitude": 36.3446,
        "category": "مخالفة بناء",
        "priority": "high",
        "status": "assigned",
        "department": "مديرية التنظيم والتخطيط العمراني",
        "routing_reason": "تم التوجيه إلى مديرية التنظيم والتخطيط العمراني لأن البلاغ يتعلق بمخالفة بناء وتنظيم عمراني.",
        "routing_confidence": 0.96,
    },
    {
        "title": "استخدام أرض لغير الغرض المخصص",
        "description": "تستخدم أرض زراعية في المنطقة بشكل تجاري خلافاً للتخطيط المعتمد.",
        "address": "التل، الطريق العام",
        "area": "التل",
        "governorate": "ريف دمشق",
        "latitude": 33.5842,
        "longitude": 36.3308,
        "category": "استعمالات أراضٍ",
        "priority": "medium",
        "status": "new",
        "department": "مديرية التنظيم والتخطيط العمراني",
        "routing_reason": "تم التوجيه إلى مديرية التنظيم والتخطيط العمراني لأن البلاغ متعلق باستعمالات الأراضي وتخطيط العمران.",
        "routing_confidence": 0.9,
    },
    {
        "title": "تضرر شبكة البنية التحتية في الحي",
        "description": "تضررت شبكة المياه والأراضي المبطنة في القطاعات الرئيسية وتمت ملاحظة تسرب متكرر.",
        "address": "باب توما، شارع الأمين",
        "area": "باب توما",
        "governorate": "دمشق",
        "latitude": 33.5416,
        "longitude": 36.2937,
        "category": "بنية تحتية",
        "priority": "urgent",
        "status": "in_progress",
        "department": "مديرية الشؤون الفنية",
        "routing_reason": "تم التوجيه إلى مديرية الشؤون الفنية لأن البلاغ متعلق بضرر في البنية التحتية واحتياج إلى صيانة فنية.",
        "routing_confidence": 0.95,
    },
    {
        "title": "تلف في شبكة الصرف الصحي بموقع تجاري",
        "description": "تسرب مياه صرف صحي يؤثر على المارة ويجب معالجة فورية.",
        "address": "دوما، شارع الجلاء",
        "area": "دوما",
        "governorate": "ريف دمشق",
        "latitude": 33.5797,
        "longitude": 36.3728,
        "category": "صيانة",
        "priority": "urgent",
        "status": "assigned",
        "department": "مديرية الشؤون الفنية",
        "routing_reason": "تم التوجيه إلى مديرية الشؤون الفنية لأن البلاغ يتناول صيانة فنية في شبكة الصرف الصحي.",
        "routing_confidence": 0.94,
    },
    {
        "title": "شكوى مرتبطة برسوم محلية ومورد محلي",
        "description": "توجد ملاحظات على زيادة الرسوم المحلية وعدم شفافيتها في التنفيذ.",
        "address": "الشعلان، شارع بغداد",
        "area": "الشعلان",
        "governorate": "دمشق",
        "latitude": 33.5090,
        "longitude": 36.2860,
        "category": "إيرادات ونفقات",
        "priority": "medium",
        "status": "new",
        "department": "مديرية الشؤون المالية",
        "routing_reason": "تم التوجيه إلى مديرية الشؤون المالية لأن البلاغ يتعلق بموازنات محلية وإيرادات ونفقات.",
        "routing_confidence": 0.91,
    },
    {
        "title": "مطالبة بتحسين مراقبة الموارد المحلية",
        "description": "يوجد قلق بشأن عدم استخدام الموارد المحلية بالشكل الأمثل في المنطقة.",
        "address": "حرستا، شارع الثورة",
        "area": "حرستا",
        "governorate": "ريف دمشق",
        "latitude": 33.4952,
        "longitude": 36.3056,
        "category": "موارد محلية",
        "priority": "medium",
        "status": "new",
        "department": "مديرية الشؤون المالية",
        "routing_reason": "تم التوجيه إلى مديرية الشؤون المالية لأن البلاغ يتعلق بموارد محلية ومتابعة الإنفاق.",
        "routing_confidence": 0.86,
    },
    {
        "title": "تقصير جهة محلية في متابعة طلبات المياه",
        "description": "تم تسجيل عدد من طلبات المياه دون متابعة كافية من الجهة المحلية المعنية.",
        "address": "حي الناصرة",
        "area": "حي الناصرة",
        "governorate": "حلب",
        "latitude": 36.2021,
        "longitude": 37.1343,
        "category": "تقصير جهة محلية",
        "priority": "high",
        "status": "assigned",
        "department": "مديرية الرقابة والتفتيش",
        "routing_reason": "تم التوجيه إلى مديرية الرقابة والتفتيش لأن البلاغ يتعلق بتقصير جهة محلية ومتابعة الأداء.",
        "routing_confidence": 0.94,
    },
    {
        "title": "مخالفة إدارية في تقديم الخدمة",
        "description": "توجد مخالفة إدارية في التعامل مع الخدمات العامة وعدم الالتزام بالإجراءات.",
        "address": "مبنى البلدية المركزي",
        "area": "مركز البلدة",
        "governorate": "حمص",
        "latitude": 34.7324,
        "longitude": 36.7137,
        "category": "مخالفة إدارية",
        "priority": "medium",
        "status": "new",
        "department": "مديرية الرقابة والتفتيش",
        "routing_reason": "تم التوجيه إلى مديرية الرقابة والتفتيش لأن البلاغ يخص مخالفة إدارية ومتابعة الأداء.",
        "routing_confidence": 0.93,
    },
    {
        "title": "شكوى رقابية على أداء البلدية",
        "description": "تستفسر الأسرة عن ممارسات البلدية في التعامل مع طلبات الرفع والتشغيل.",
        "address": "مركز البلدية",
        "area": "المركز",
        "governorate": "حماة",
        "latitude": 35.1318,
        "longitude": 36.7578,
        "category": "شكوى رقابية",
        "priority": "high",
        "status": "assigned",
        "department": "مديرية الرقابة والتفتيش",
        "routing_reason": "تم التوجيه إلى مديرية الرقابة والتفتيش لأنها الجهة المختصة في متابعة الشكاوى الرقابية وأداء الجهات المحلية.",
        "routing_confidence": 0.9,
    },
    {
        "title": "مشكلة خدمية تشمل أكثر من بلدية وتحتاج تنسيقاً",
        "description": "تتجاوز المشكلة حدود دائرة واحدة وتحتاج تنسيقاً بين أكثر من جهة محلية.",
        "address": "منطقة الوصل بين البلديات",
        "area": "الحدود بين البلديات",
        "governorate": "اللاذقية",
        "latitude": 35.5224,
        "longitude": 35.7913,
        "category": "مشكلة على مستوى المحافظة",
        "priority": "urgent",
        "status": "in_progress",
        "department": "المحافظات",
        "routing_reason": "تم التوجيه إلى المحافظات لأن المشكلة تتجاوز حدود جهة واحدة وتحتاج تنسيقاً على مستوى المحافظة.",
        "routing_confidence": 0.97,
    },
    {
        "title": "تبرز مشكلة في الحديقة العامة في حي واحد",
        "description": "الحديقة بحاجة إلى صيانة مباشرة وتهيئة غير متوفرة في الوقت الحالي.",
        "address": "حديقة النخيل، حي النخيل",
        "area": "حي النخيل",
        "governorate": "طرطوس",
        "latitude": 34.8893,
        "longitude": 35.8867,
        "category": "حدائق",
        "priority": "medium",
        "status": "new",
        "department": "مجالس المدن والبلديات والوحدات الإدارية",
        "routing_reason": "تم التوجيه إلى مجالس المدن والبلديات والوحدات الإدارية لأن المشكلة مباشرة في حي محدد وتحتاج تنفيذ محلي.",
        "routing_confidence": 0.9,
    },
    {
        "title": "بلوك انقطاع مياه في حي الروضة",
        "description": "لا يوجد توفر كافي للمياه في أجزاء الحي وقد تم تقديم الطلب عدة مرات.",
        "address": "حي الروضة، شارع 9",
        "area": "حي الروضة",
        "governorate": "درعا",
        "latitude": 32.6189,
        "longitude": 36.1021,
        "category": "خدمات يومية",
        "priority": "high",
        "status": "assigned",
        "department": "مجالس المدن والبلديات والوحدات الإدارية",
        "routing_reason": "تم التوجيه إلى مجالس المدن والبلديات والوحدات الإدارية لأن البلاغ يتعلق بخدمة يومية مباشرة ضمن الوحدة الإدارية.",
        "routing_confidence": 0.93,
    },
    {
        "title": "تسرب في شبكة المياه في منطقة السكن",
        "description": "تسرب مستمر في شبكة المياه يسبب أضرارًا في المنازل القريبة.",
        "address": "حي السكن الجديد",
        "area": "السكن الجديد",
        "governorate": "السويداء",
        "latitude": 32.7094,
        "longitude": 36.5694,
        "category": "خدمات يومية",
        "priority": "urgent",
        "status": "in_progress",
        "department": "مجالس المدن والبلديات والوحدات الإدارية",
        "routing_reason": "تم التوجيه إلى مجالس المدن والبلديات والوحدات الإدارية لأن البلاغ يتطلب تنفيذًا محليًا سريعًا.",
        "routing_confidence": 0.92,
    },
    {
        "title": "تجاوزات في تنظيم الطريق داخل الحي",
        "description": "توجد أضرار في رصف الطريق بجانب أرصفة وأماكن انتظار غير مرتبة.",
        "address": "حي الفارسية",
        "area": "حي الفارسية",
        "governorate": "دير الزور",
        "latitude": 35.3364,
        "longitude": 40.1408,
        "category": "طرق وتنظيم",
        "priority": "medium",
        "status": "new",
        "department": "مديرية التنظيم والتخطيط العمراني",
        "routing_reason": "تم التوجيه إلى مديرية التنظيم والتخطيط العمراني لأن البلاغ يتعلق بالطرق والتنظيم العمراني.",
        "routing_confidence": 0.87,
    },
    {
        "title": "مشروع خدمي يحتاج تنفيذ سريع في الحي",
        "description": "الحارة تعاني من نقص في الخدمات الأساسية وهنا يطلب تنفيذ مشروع خدمية جديد.",
        "address": "حي المروج",
        "area": "حي المروج",
        "governorate": "الحسكة",
        "latitude": 36.5055,
        "longitude": 40.7465,
        "category": "مشروع خدمي",
        "priority": "high",
        "status": "assigned",
        "department": "مديرية التخطيط والتنمية المحلية",
        "routing_reason": "تم التوجيه إلى مديرية التخطيط والتنمية المحلية لأن البلاغ يخص مشروع خدمية يحتاج تنسيقاً وتنفيذًا.",
        "routing_confidence": 0.9,
    },
    {
        "title": "مشكلة بلدية محلية في صيانة الحديقة",
        "description": "الحديقة المحلية في الحي هي بحاجة إلى صيانة فورية من البلديّة.",
        "address": "حديقة الكرامة",
        "area": "المدينة",
        "governorate": "القنيطرة",
        "latitude": 33.1256,
        "longitude": 35.8233,
        "category": "مشكلة بلدية محلية",
        "priority": "medium",
        "status": "new",
        "department": "مجالس المدن والبلديات والوحدات الإدارية",
        "routing_reason": "تم التوجيه إلى مجالس المدن والبلديات والوحدات الإدارية لأن البلاغ مشكلة محلية مباشرة تحتاج التنفيذ المحلي.",
        "routing_confidence": 0.91,
    },
    {
        "title": "طلب للتنظيم في منطقة سكنية جديدة",
        "description": "المنطقة تعرف بالازدحام ومشكلات تنظيمية في الشوارع والإنارة.",
        "address": "حي الشروق",
        "area": "حي الشروق",
        "governorate": "إدلب",
        "latitude": 35.9306,
        "longitude": 36.6339,
        "category": "تنظيم عمراني",
        "priority": "medium",
        "status": "new",
        "department": "مديرية التنظيم والتخطيط العمراني",
        "routing_reason": "تم التوجيه إلى مديرية التنظيم والتخطيط العمراني لأن البلاغ يتعلق بالتنظيم العمراني.",
        "routing_confidence": 0.89,
    },
    {
        "title": "مشكلة في إضاءة الشوارع الداخلية",
        "description": "بعض الشوارع الداخلية لا تزال مظلمة، مما يعيق الحركة الليلة.",
        "address": "حي البلدة الجديدة",
        "area": "الحي الجديد",
        "governorate": "دمشق",
        "latitude": 33.5085,
        "longitude": 36.2703,
        "category": "إنارة",
        "priority": "high",
        "status": "new",
        "department": "مديرية الخدمات المحلية",
        "routing_reason": "تم التوجيه إلى مديرية الخدمات المحلية لأن البلاغ متعلق بإنارة عامة داخل حي سكني.",
        "routing_confidence": 0.93,
    },
    {
        "title": "طلب متابعـة الأداء الوحدوي في الحي",
        "description": "يتكرر التأخر في تنفيذ الطلبات المتعلقة بالأرصفة والحدائق.",
        "address": "حي النسيم",
        "area": "حي النسيم",
        "governorate": "ريف دمشق",
        "latitude": 33.5066,
        "longitude": 36.3186,
        "category": "أداء جهة محلية",
        "priority": "medium",
        "status": "assigned",
        "department": "مديريات المجالس المحلية والإدارة المحلية",
        "routing_reason": "تم التوجيه إلى مديريات المجالس المحلية والإدارة المحلية لأن البلاغ يتعلق بأداء الوحدة الإدارية ومتابعة الأعمال.",
        "routing_confidence": 0.91,
    },
    {
        "title": "مشكلة في إعداد موازنة الحي",
        "description": "توجد ملاحظات على الموازنة المحلية وعدم تناسبها مع الاحتياجات الحالية.",
        "address": "مركز المدينة",
        "area": "المركز",
        "governorate": "ريف دمشق",
        "latitude": 33.5217,
        "longitude": 36.3224,
        "category": "موازنة محلية",
        "priority": "medium",
        "status": "new",
        "department": "مديرية الشؤون المالية",
        "routing_reason": "تم التوجيه إلى مديرية الشؤون المالية لأنها الجهة المختصة في الموازنة المحلية والموارد المالية.",
        "routing_confidence": 0.88,
    },
]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def seed_data() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if db.query(Category).count() > 0 or db.query(Department).count() > 0:
            _ensure_workflow_accounts(db)
            return

        departments = [Department(**item) for item in OFFICIAL_DEPARTMENTS]
        db.add_all(departments)
        db.flush()

        for name, slug, description in SEED_CATEGORIES:
            db.add(Category(name=name, slug=slug, description=description))

        citizen = User(
            name="Citizen User",
            email="citizen@example.com",
            hashed_password=hash_password("password"),
            role="citizen",
        )
        admin = User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=hash_password("password"),
            role="admin",
        )
        db.add_all([citizen, admin])
        db.flush()

        department_lookup = {dept.name: dept for dept in departments}
        category_lookup = {
            category.name: category
            for category in db.execute(select(Category)).scalars().all()
        }

        complaint_items = []
        for item in DEMO_COMPLAINTS:
            dept_name = item.get("department")
            category_name = item.get("category")
            complaint_items.append(
                Complaint(
                    user_id=citizen.id,
                    category_id=category_lookup[category_name].id,
                    department_id=department_lookup.get(dept_name).id if dept_name in department_lookup else None,
                    title=item["title"],
                    description=item["description"],
                    address=item.get("address"),
                    area=item.get("area"),
                    governorate=item.get("governorate"),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    priority=item["priority"],
                    status=item["status"],
                    routing_reason=item.get("routing_reason"),
                    routing_confidence=item.get("routing_confidence"),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )

        db.add_all(complaint_items)
        db.commit()
        _ensure_workflow_accounts(db)
    finally:
        db.close()


def _ensure_workflow_accounts(db: Session) -> None:
    departments = {department.slug: department for department in db.query(Department).all()}
    existing_ministry = db.query(User).filter(User.email == "admin@molae.gov.sy").one_or_none()
    legacy_admin = db.query(User).filter(User.email == "admin@example.com").one_or_none()
    if legacy_admin and not existing_ministry:
        legacy_admin.email = "admin@molae.gov.sy"
        legacy_admin.name = "Ministry Demo Administrator"
        legacy_admin.role = "ministry_admin"
        existing_ministry = legacy_admin
    if not existing_ministry:
        db.add(User(name="Ministry Demo Administrator", email="admin@molae.gov.sy", hashed_password=hash_password("password"), role="ministry_admin"))

    aliases = {
        "services-local": "local-services", "local-councils-admin": "local-councils", "planning-local-development": "local-development",
        "urban-planning": "urban-planning", "technical-affairs": "technical-affairs", "financial-affairs": "financial-affairs",
        "inspection-audit": "inspection", "governorates": "governorates", "municipal-local-units": "municipalities",
    }
    for slug, alias in aliases.items():
        department = departments.get(slug)
        if not department:
            continue
        email = f"{alias}@molae.gov.sy"
        if not db.query(User).filter(User.email == email).one_or_none():
            db.add(User(name=f"{department.name} Administrator", email=email, hashed_password=hash_password("password"), role="directorate_admin", department_id=department.id))

    for slug in ("services-local", "technical-affairs", "urban-planning"):
        department = departments.get(slug)
        if not department:
            continue
        for index in range(1, 4):
            email = f"emp{index:03d}.{slug}@molae.gov.sy"
            if not db.query(User).filter(User.email == email).one_or_none():
                db.add(User(name=f"Field Employee {index}", email=email, hashed_password=hash_password("password"), role="field_employee", department_id=department.id, job_title="Field Service Employee"))
    db.commit()


if __name__ == "__main__":
    seed_data()
