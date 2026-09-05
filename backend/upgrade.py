import random
from sqlalchemy.orm import Session
from database import User, Item, InventoryItem


def get_upgrade_chance(source_value: float, target_value: float) -> float:
    """Считает шанс успеха апгрейда в процентах (0-100)."""
    house_edge = 0.9
    raw_chance = (source_value / target_value) * house_edge
    chance = min(raw_chance, 0.95)
    return chance * 100


def perform_upgrade(db: Session, user: User, inventory_item_id: int, target_item_id: int) -> dict:
    inv_item = db.query(InventoryItem).filter(
        InventoryItem.id == inventory_item_id,
        InventoryItem.user_id == user.id
    ).first()

    if not inv_item:
        raise ValueError("Этот предмет не найден в твоём инвентаре")

    target_item = db.query(Item).filter(Item.id == target_item_id).first()
    if not target_item:
        raise ValueError("Целевой предмет не найден")

    source_item = inv_item.item

    if target_item.value <= source_item.value:
        raise ValueError("Целевой предмет должен быть дороже исходного")

    chance_percent = get_upgrade_chance(source_item.value, target_item.value)

    roll = random.uniform(0, 100)
    success = roll <= chance_percent

    db.delete(inv_item)

    if success:
        db.add(InventoryItem(user_id=user.id, item_id=target_item.id))

    user.upgrades_done = (user.upgrades_done or 0) + 1
    db.commit()

    return {
        "success": success,
        "chance_was": round(chance_percent, 1),
        "roll": round(roll, 1),
        "won_item": target_item.name if success else None,
        "lost_item": source_item.name,
    }
