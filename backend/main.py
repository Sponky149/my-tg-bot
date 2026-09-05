from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, User, Item
from auth import validate_init_data
from daily import open_daily_case, seconds_until_next_claim
from upgrade import perform_upgrade
from sell import sell_item
import json
 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
def get_current_user(x_init_data: str = Header(...), db: Session = Depends(get_db)) -> User:
    data = validate_init_data(x_init_data)
    if not data:
        raise HTTPException(401, "Неверная подпись initData")
 
    tg_user = json.loads(data["user"])
    user = db.query(User).filter(User.telegram_id == tg_user["id"]).first()
 
    if not user:
        user = User(telegram_id=tg_user["id"], username=tg_user.get("username"))
        db.add(user)
        db.commit()
        db.refresh(user)
 
    return user
 
 
@app.get("/api/profile")
def profile(user: User = Depends(get_current_user)):
    return {
        "balance": user.balance,
        "level": user.level,
        "exp": user.exp,
        "username": user.username,
    }
 
 
@app.get("/api/inventory")
def get_inventory(user: User = Depends(get_current_user)):
    items = []
    for inv in user.inventory:
        items.append({
            "inventory_item_id": inv.id,
            "item_id": inv.item.id,
            "name": inv.item.name,
            "rarity": inv.item.rarity,
            "value": inv.item.value,
        })
    return {"inventory": items}
 
 
@app.get("/api/items")
def get_all_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return {"items": [
        {"id": i.id, "name": i.name, "rarity": i.rarity, "value": i.value}
        for i in items
    ]}
 
 
@app.get("/api/daily/status")
def daily_status(user: User = Depends(get_current_user)):
    remaining = seconds_until_next_claim(user)
    return {"can_claim": remaining == 0, "seconds_left": remaining}
 
 
@app.post("/api/daily/open")
def daily_open(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        item = open_daily_case(db, user)
        return {"success": True, "item": {"name": item.name, "rarity": item.rarity}}
    except ValueError as e:
        raise HTTPException(400, str(e))
 
 
@app.post("/api/upgrade")
def upgrade_endpoint(
    inventory_item_id: int,
    target_item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = perform_upgrade(db, user, inventory_item_id, target_item_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
 
 
@app.post("/api/sell")
def sell_endpoint(
    inventory_item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = sell_item(db, user, inventory_item_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
