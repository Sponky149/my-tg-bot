import asyncio
import os
import json
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_db, User, Item
from auth import validate_init_data
from daily import open_daily_case, seconds_until_next_claim
from upgrade import perform_upgrade
from sell import sell_item
from cases import open_case
 
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
 
 
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🎮 ИГРАТЬ", web_app=WebAppInfo(url=WEBAPP_URL))
        ]]
    )
    await message.answer(
        "Добро пожаловать! Открывай ежедневный кейс и качай апгрейды 🧠",
        reply_markup=keyboard
    )
 
 
@app.on_event("startup")
async def start_bot_polling():
    
    asyncio.create_task(dp.start_polling(bot))
 
 
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
            "image_url": inv.item.image_url,
        })
    return {"inventory": items}
 
 
@app.get("/api/items")
def get_all_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return {"items": [
        {"id": i.id, "name": i.name, "rarity": i.rarity, "value": i.value, "image_url": i.image_url}
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
        return {"success": True, "item": {"name": item.name, "rarity": item.rarity, "value": item.value, "image_url": item.image_url}}
    except ValueError as e:
        raise HTTPException(400, str(e))
 
 
@app.get("/api/cases")
def list_cases(db: Session = Depends(get_db)):
    from database import Case
    cases = db.query(Case).all()
    return {"cases": [
        {"id": c.id, "name": c.name, "price": c.price, "image_url": c.image_url} for c in cases
    ]}
 
 
@app.get("/api/cases/{case_id}/items")
def case_items_endpoint(case_id: int, db: Session = Depends(get_db)):
    """Возвращает список всех предметов внутри кейса с их шансом выпадения (%)."""
    from database import CaseItem, Item
    case_items = db.query(CaseItem).filter(CaseItem.case_id == case_id).all()
    total_weight = sum(ci.weight for ci in case_items) or 1
 
    result = []
    for ci in case_items:
        item = db.query(Item).get(ci.item_id)
        result.append({
            "name": item.name,
            "rarity": item.rarity,
            "value": item.value,
            "image_url": item.image_url,
            "chance": round(ci.weight / total_weight * 100, 2),
        })
    
    result.sort(key=lambda x: -x["chance"])
    return {"items": result}
 
 
@app.post("/api/cases/{case_id}/open")
def open_case_endpoint(
    case_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        item = open_case(db, user, case_id)
        return {"success": True, "item": {"name": item.name, "rarity": item.rarity, "value": item.value, "image_url": item.image_url}}
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
 
 

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
