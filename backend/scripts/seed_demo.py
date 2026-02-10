"""
Seed demo data for local development (NO alcohol/cigarettes).
Owners: Shodiyor, Doniyor

Run:
  python -m scripts.seed_demo

Reset (delete seeded data first):
  $env:SEED_RESET="1"; python -m scripts.seed_demo   # PowerShell
"""
import os
import sys
import random
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.owner import Owner
from app.models.expense import Expense, PayerType
from app.models.employee import Employee, Advance
from app.models.company import Company, CompanyTransaction, TransactionDirection
from app.models.cashbox import Cashbox, DailyCashboxEntry


# ----------------------------
# CONFIG
# ----------------------------

CASHBOX_NAMES = [
    "cashbox_1_day",
    "cashbox_2_day",
    "cashbox_1_night",
    "cashbox_2_night",
]

DEMO_OWNERS = [
    ("Shodiyor", "#007AFF"),  # blue
    ("Doniyor", "#34C759"),   # green
]

DEMO_EMPLOYEES = [
    ("Azizbek S.", 4_500_000),
    ("Jasur A.", 3_800_000),
    ("Dilshod K.", 3_200_000),
    ("Nodir R.", 2_900_000),
]

DEMO_COMPANIES = [
    "Coca-Cola Distributor",
    "Nestle Supplier",
    "PepsiCo Partner",
    "Local Bakery",
    "Dairy Factory",
    "Household Supplier",
]

# No alcohol, no cigarettes categories:
EXPENSE_CATEGORIES = [
    "Аренда",
    "Коммуналка",
    "Интернет",
    "Транспорт",
    "Пакеты/упаковка",
    "Канцелярия",
    "Ремонт/хозяйственные",
    "Маркетинг/реклама",
    "Бонус сотрудникам",
    "Прочее",
]

EXPENSE_COMMENTS = [
    "Оплата по чеку",
    "Срочная покупка",
    "Сервис/обслуживание",
    "Расходные материалы",
    "Доставка",
    "Ежедневные расходы",
]

SEED_DAYS = 45  # generate last N days


# ----------------------------
# HELPERS
# ----------------------------

def d0(n: int) -> date:
    return date.today() - timedelta(days=n)


def rand_money(min_uzs: int, max_uzs: int, step: int = 1000) -> int:
    """Random integer amount with rounding step."""
    if min_uzs > max_uzs:
        min_uzs, max_uzs = max_uzs, min_uzs
    v = random.randint(min_uzs // step, max_uzs // step) * step
    return int(v)


def get_or_create_by_name(db, model, name_field: str, name_value: str, **extra):
    q = db.query(model).filter(getattr(model, name_field) == name_value).first()
    if q:
        return q, False
    obj = model(**{name_field: name_value}, **extra)
    db.add(obj)
    return obj, True


# ----------------------------
# SEEDERS
# ----------------------------

def seed_cashboxes(db, reset: bool):
    # Ensure cashboxes exist (do not delete cashboxes themselves)
    cashboxes = []
    for name in CASHBOX_NAMES:
        cb, _ = get_or_create_by_name(db, Cashbox, "name", name)
        cashboxes.append(cb)

    db.flush()

    if reset:
        db.query(DailyCashboxEntry).delete()

    # Entries: day cashboxes usually bigger, night smaller. Add realistic variance.
    for i in range(SEED_DAYS):
        day = d0(i)

        # seasonality: weekends slightly higher
        weekday = day.weekday()  # 0..6
        weekend_boost = 1.15 if weekday in (5, 6) else 1.0

        for cb in cashboxes:
            is_day = "day" in cb.name
            base_min = 2_500_000 if is_day else 1_200_000
            base_max = 7_500_000 if is_day else 4_000_000

            amount = int(rand_money(base_min, base_max, step=5000) * weekend_boost)

            db.add(
                DailyCashboxEntry(
                    cashbox_id=cb.id,
                    date=day,
                    amount_uzs=Decimal(amount),
                    comment=f"Выручка {cb.name} ({'выходные' if weekend_boost > 1 else 'будни'})",
                )
            )


def seed_owners(db, reset: bool):
    if reset:
        db.query(Owner).delete()

    owners = []
    for name, color in DEMO_OWNERS:
        owner = db.query(Owner).filter(Owner.name == name).first()
        if not owner:
            owner = Owner(name=name, color_hex=color)
            db.add(owner)
        else:
            owner.color_hex = color
        owners.append(owner)

    db.flush()
    return owners


def seed_employees(db, reset: bool):
    if reset:
        db.query(Advance).delete()
        db.query(Employee).delete()

    employees = []
    for full_name, salary in DEMO_EMPLOYEES:
        emp = db.query(Employee).filter(Employee.full_name == full_name).first()
        if not emp:
            emp = Employee(full_name=full_name, monthly_salary_uzs=Decimal(salary), is_active=True)
            db.add(emp)
        else:
            emp.monthly_salary_uzs = Decimal(salary)
            emp.is_active = True
        employees.append(emp)

    db.flush()

    # Advances: some employees have advances 1-2 times
    for idx, emp in enumerate(employees):
        if idx % 2 == 0:
            db.add(
                Advance(
                    employee_id=emp.id,
                    date=d0(7 + idx),
                    amount_uzs=Decimal(rand_money(200_000, 900_000, 10_000)),
                    comment="Аванс (seed)",
                )
            )
        if idx % 3 == 0:
            db.add(
                Advance(
                    employee_id=emp.id,
                    date=d0(20 + idx),
                    amount_uzs=Decimal(rand_money(150_000, 600_000, 10_000)),
                    comment="Аванс 2 (seed)",
                )
            )


def seed_companies(db, reset: bool):
    if reset:
        db.query(CompanyTransaction).delete()
        db.query(Company).delete()

    companies = []
    for name in DEMO_COMPANIES:
        c = db.query(Company).filter(Company.name == name).first()
        if not c:
            c = Company(name=name, is_active=True)
            db.add(c)
        else:
            c.is_active = True
        companies.append(c)

    db.flush()

    # Transactions: OUT more frequent than IN (typical supplier payments)
    for i in range(SEED_DAYS):
        day = d0(i)

        # not every day has a company transaction
        if random.random() < 0.55:
            c = random.choice(companies)
            amount = rand_money(400_000, 6_500_000, 10_000)
            db.add(
                CompanyTransaction(
                    company_id=c.id,
                    date=day,
                    amount_uzs=Decimal(amount),
                    direction=TransactionDirection.OUT,
                    comment=f"Оплата поставщику ({c.name})",
                )
            )

        # sometimes IN (bonuses/returns)
        if random.random() < 0.18:
            c = random.choice(companies)
            amount = rand_money(100_000, 1_800_000, 10_000)
            db.add(
                CompanyTransaction(
                    company_id=c.id,
                    date=day,
                    amount_uzs=Decimal(amount),
                    direction=TransactionDirection.IN,
                    comment=f"Возврат/скидка/бонус ({c.name})",
                )
            )


def seed_expenses(db, owners: list[Owner], reset: bool):
    if reset:
        db.query(Expense).delete()

    # Expenses: 1..4 per day with realistic amounts
    for i in range(SEED_DAYS):
        day = d0(i)

        cnt = random.randint(1, 4)

        for _ in range(cnt):
            cat = random.choice(EXPENSE_CATEGORIES)

            # category-based ranges
            if cat == "Аренда":
                amount = rand_money(2_000_000, 8_000_000, 50_000)
            elif cat == "Коммуналка":
                amount = rand_money(150_000, 1_500_000, 10_000)
            elif cat == "Интернет":
                amount = rand_money(80_000, 300_000, 5_000)
            elif cat == "Транспорт":
                amount = rand_money(30_000, 250_000, 5_000)
            elif cat == "Пакеты/упаковка":
                amount = rand_money(40_000, 500_000, 5_000)
            elif cat == "Канцелярия":
                amount = rand_money(20_000, 200_000, 5_000)
            elif cat == "Ремонт/хозяйственные":
                amount = rand_money(50_000, 900_000, 10_000)
            elif cat == "Маркетинг/реклама":
                amount = rand_money(50_000, 700_000, 10_000)
            elif cat == "Бонус сотрудникам":
                amount = rand_money(100_000, 1_200_000, 10_000)
            else:
                amount = rand_money(20_000, 400_000, 5_000)

            comment = random.choice(EXPENSE_COMMENTS)

            # payer logic:
            # - mostly "other"
            # - sometimes owner pays
            payer_type = PayerType.other
            owner_id = None

            if owners and random.random() < 0.22:
                payer_type = PayerType.owner
                owner_id = random.choice(owners).id

            db.add(
                Expense(
                    date=day,
                    amount_uzs=Decimal(amount),
                    category=cat,
                    comment=comment,
                    payer_type=payer_type,
                    owner_id=owner_id,
                )
            )


def main():
    # Make seed deterministic if you want:
    # random.seed(42)

    reset = os.environ.get("SEED_RESET", "").strip() in ("1", "true", "True", "yes", "YES")
    db = SessionLocal()
    try:
        owners = seed_owners(db, reset=reset)
        seed_employees(db, reset=reset)
        seed_companies(db, reset=reset)
        seed_cashboxes(db, reset=reset)
        seed_expenses(db, owners=owners, reset=reset)

        db.commit()
        print("✅ Demo seed done (no alcohol/cigarettes)")
        print("Owners:", ", ".join([o.name for o in owners]))
        if reset:
            print("ℹ️ Reset mode was ON (SEED_RESET=1)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
