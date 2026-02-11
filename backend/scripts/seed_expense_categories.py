from app.database import SessionLocal
from app.models.expense_category import ExpenseCategory

CATEGORIES = [
    "Офис расход",
    "Аренда",
    "Камуналка",
    "Заправка",
    "IT",
    "Обед",
    "Ужин",
    "Карзлар",
    "Бошкалар",
]

db = SessionLocal()
try:
    for name in CATEGORIES:
        name = name.strip()
        exists = db.query(ExpenseCategory).filter(ExpenseCategory.name == name).first()
        if not exists:
            db.add(ExpenseCategory(name=name, is_active=True))
    db.commit()
    print("✅ expense categories seeded")
finally:
    db.close()
