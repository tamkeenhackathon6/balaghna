# BALIGHNA Demo Flow

Duration: 2-3 minutes. The demo uses approximate Syrian locations, centered visually on Damascus.

## 1. Citizen report and smart routing

1. Sign in as `citizen@example.com` with password `password`.
2. Open `إنشاء بلاغ جديد`.
3. Enter the following text:

   ```text
   في حفرة كبيرة بنص الشارع وعم تسبب خطر عالسيارات
   ```

4. Select `تحليل البلاغ`.
5. Explain the result:
   - نوع المشكلة: `حفر وطرق محلية`
   - الأولوية: `urgent` because the text contains a safety risk.
   - الجهة المختصة: `مديرية الخدمات المحلية`
   - سبب التوجيه: the complaint concerns a pothole and an immediate local daily service.
6. Choose `اعتماد الاقتراح`, set the governorate to `دمشق` or `ريف دمشق`, choose an approximate location, and submit the complaint.
7. Open the detail view to show the automatic routing event, current responsible entity, routing reason, and status.

## 2. Admin confirmation and workflow

1. Sign out and sign in as `admin@example.com` with password `password`.
2. Open `إدارة البلاغات`, then the new complaint.
3. Highlight `توجيه البلاغ`: current entity, routing reason, and analysis confidence.
4. Confirm the routing or choose a different official entity to demonstrate that admin review is final.
5. Change status to `in_progress`, then `resolved`.
6. Show the timeline, which records the automatic routing and every status change.

## 3. Map and charts

1. Open `خريطة البلاغات` from the admin dashboard.
2. Filter by priority or official entity and open a marker popup.
3. Return to the dashboard and show:
   - complaints by category
   - complaints by status
   - distribution by responsible official entity

## Optional second routing proof

Use the analysis button without submitting this text:

```text
يوجد بناء مخالف ضمن المنطقة السكنية
```

Expected result:

- نوع المشكلة: `مخالفة بناء`
- الجهة المختصة: `مديرية التنظيم والتخطيط العمراني`

This demonstrates that BALIGHNA does not send every complaint to the same entity.
