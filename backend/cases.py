import random
from datetime import datetime
from sqlalchemy.orm import Session
from database import Case, CaseItem, Item, InventoryItem, User, DropLog


def open_case(db: Session, user: User, case_id: int) -> Item:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError("Кейс не найден")

    if user.balance < case.price:
        raise ValueError("Недостаточно валюты")

    user.balance -= case.price

    case_items = db.query(CaseItem).filter(CaseItem.case_id == case_id).all()
    if not case_items:
        raise ValueError("В этом кейсе пока нет предметов")

    items = [db.query(Item).get(ci.item_id) for ci in case_items]
    weights = [ci.weight for ci in case_items]

    won_item = random.choices(items, weights=weights, k=1)[0]

    db.add(InventoryItem(user_id=user.id, item_id=won_item.id))
    user.cases_opened = (user.cases_opened or 0) + 1
    db.add(DropLog(
        user_id=user.id, item_name=won_item.name, item_rarity=won_item.rarity,
        item_value=won_item.value, source="case", created_at=datetime.utcnow()
    ))
    db.commit()

    return won_item
