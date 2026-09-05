import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import User, Item, InventoryItem
 
DAILY_COOLDOWN_HOURS = 24
 

RARITY_WEIGHTS = {
    "common": 70,
    "rare": 20,
    "epic": 8,
    "legendary": 2,
}
 
 
def seconds_until_next_claim(user: User) -> int:
    
    if not user.last_daily_claim:
        return 0
    next_time = user.last_daily_claim + timedelta(hours=DAILY_COOLDOWN_HOURS)
    remaining = (next_time - datetime.utcnow()).total_seconds()
    return max(0, int(remaining))
 
 
def open_daily_case(db: Session, user: User) -> Item:
    remaining = seconds_until_next_claim(user)
    if remaining > 0:
        raise ValueError(f"Кейс ещё не доступен, подожди {remaining} сек.")
 
    items = db.query(Item).all()
    if not items:
        raise ValueError("В игре пока нет предметов")
 
    weights = [RARITY_WEIGHTS.get(i.rarity, 1) for i in items]
    won_item = random.choices(items, weights=weights, k=1)[0]
 
    db.add(InventoryItem(user_id=user.id, item_id=won_item.id))
    user.last_daily_claim = datetime.utcnow()
    db.commit()
 
    return won_item
 
