# poetry_dataset.py
# طبقة توافق قديمة: أي كود قديم يستورد POETRY_DATASET يستمر بالعمل،
# لكن المصدر الحقيقي الوحيد للبيانات الآن هو all_bahoor.py (ALL_BAHOOR).
# لا تعدّل هنا — عدّل all_bahoor.py فقط.

from all_bahoor import ALL_BAHOOR

POETRY_DATASET = {
    name: {
        'weight': d['weight'],
        'poets': d['poets'],
        'verses': d['verses'],
    }
    for name, d in ALL_BAHOOR.items()
}
