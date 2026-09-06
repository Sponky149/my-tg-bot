import random
from datetime import datetime
from sqlalchemy.orm import Session
from database import Case, CaseItem, Item, InventoryItem, User, DropLog


def open_case(db: Session, user: User, case_id: int, quantity: int = 1) -> list[Item]:
    """Открывает кейс quantity раз подряд (одной транзакцией) и возвращает список выпавших предметов."""
    quantity = max(1, min(quantity, 10))  # разумный предел, чтобы не открывали по 1000 за раз

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError("Кейс не найден")

    total_price = case.price * quantity
    if user.balance < total_price:
        raise ValueError("Недостаточно монет")

    case_items = db.query(CaseItem).filter(CaseItem.case_id == case_id).all()
    if not case_items:
        raise ValueError("В этом кейсе пока нет предметов")

    items = [db.query(Item).get(ci.item_id) for ci in case_items]
    weights = [ci.weight for ci in case_items]

    user.balance -= total_price
    won_items = []

    for _ in range(quantity):
        won_item = random.choices(items, weights=weights, k=1)[0]
        won_items.append(won_item)
        db.add(InventoryItem(user_id=user.id, item_id=won_item.id))
        db.add(DropLog(
            user_id=user.id, item_name=won_item.name, item_rarity=won_item.rarity,
            item_value=won_item.value, source="case", created_at=datetime.utcnow()
        ))

    user.cases_opened = (user.cases_opened or 0) + quantity
    db.commit()

    return won_items
