import sys
sys.path.append("backend")
 
from backend.database import SessionLocal, Item
 
db = SessionLocal()
 

existing = db.query(Item).count()
if existing > 0:
    print(f"В базе уже есть {existing} предметов, ничего не добавляю.")
else:
    items_data = [
        {"name": "Bombardiro Crocodilo", "rarity": "common", "value": 10},
        {"name": "Tralalero Tralala", "rarity": "rare", "value": 50},
        {"name": "Tung Tung Tung Sahur", "rarity": "epic", "value": 200},
        {"name": "Cappuccino Assassino", "rarity": "legendary", "value": 1000},
    ]
 
    for data in items_data:
        db.add(Item(**data))
 
    db.commit()
    print("База наполнена тестовыми предметами!")
 
db.close()
