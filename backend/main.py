import asyncio
import os
import json
from datetime import datetime
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

# ============================================================
# ТЕЛЕГРАМ-БОТ - работает ВНУТРИ этого же веб-сервера,
# чтобы уместиться в один бесплатный Web Service на Render
# ============================================================
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
    # запускаем бота "фоновой задачей" рядом с веб-сервером, не блокируя его
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
        "cases_opened": user.cases_opened or 0,
        "upgrades_done": user.upgrades_done or 0,
    }


@app.get("/api/profile/drops")
def profile_drops(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Лучший дроп за всё время + последние 10 дропов (кейсы + ежедневный бонус)."""
    from database import DropLog

    all_drops = db.query(DropLog).filter(DropLog.user_id == user.id).order_by(DropLog.created_at.desc()).all()

    best = None
    if all_drops:
        best_row = max(all_drops, key=lambda d: d.item_value)
        best = {"name": best_row.item_name, "rarity": best_row.item_rarity, "value": best_row.item_value}

    recent = [
        {"name": d.item_name, "rarity": d.item_rarity, "value": d.item_value, "source": d.source}
        for d in all_drops[:10]
    ]

    return {"best": best, "recent": recent}


@app.get("/api/drops/global")
def global_drops(db: Session = Depends(get_db)):
    """Лента последних дропов ВСЕХ игроков - для тикера на главном экране.
    Показывает только публичный юзернейм (или ID если юзернейма нет), без другой личной информации."""
    from database import DropLog

    rows = (
        db.query(DropLog, User)
        .join(User, DropLog.user_id == User.id)
        .order_by(DropLog.created_at.desc())
        .limit(20)
        .all()
    )

    result = []
    for drop, u in rows:
        display_name = u.username or f"id{u.telegram_id}"
        result.append({
            "name": drop.item_name,
            "rarity": drop.item_rarity,
            "value": drop.item_value,
            "player": display_name,
        })
    return {"drops": result}


@app.get("/api/drops/top24h")
def top_drop_24h(db: Session = Depends(get_db)):
    """Самый дорогой предмет, выпавший у ЛЮБОГО игрока за последние 24 часа."""
    from database import DropLog
    from datetime import timedelta

    since = datetime.utcnow() - timedelta(hours=24)
    row = (
        db.query(DropLog, User)
        .join(User, DropLog.user_id == User.id)
        .filter(DropLog.created_at >= since)
        .order_by(DropLog.item_value.desc())
        .first()
    )

    if not row:
        return {"top": None}

    drop, u = row
    display_name = u.username or f"id{u.telegram_id}"
    return {"top": {
        "name": drop.item_name,
        "rarity": drop.item_rarity,
        "value": drop.item_value,
        "player": display_name,
        "case_name": drop.case_name,
    }}


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
    from database import Case, CaseItem
    cases = db.query(Case).all()
    result = []
    for c in cases:
        item_count = db.query(CaseItem).filter(CaseItem.case_id == c.id).count()
        result.append({
            "id": c.id, "name": c.name, "price": c.price,
            "image_url": c.image_url, "item_count": item_count,
        })
    return {"cases": result}


@app.get("/api/cases/{case_id}/items")
def case_items_endpoint(case_id: int, db: Session = Depends(get_db)):
    """Возвращает список всех предметов внутри кейса (БЕЗ процента шанса -
    игроку это не показываем, шансы видны только тебе в backend/seed.py)."""
    from database import CaseItem, Item
    case_items = db.query(CaseItem).filter(CaseItem.case_id == case_id).all()

    result = []
    for ci in case_items:
        item = db.query(Item).get(ci.item_id)
        result.append({
            "name": item.name,
            "rarity": item.rarity,
            "value": item.value,
            "image_url": item.image_url,
        })
    # сортируем по цене - подороже сверху, для красоты
    result.sort(key=lambda x: -x["value"])
    return {"items": result}


@app.post("/api/cases/{case_id}/open")
def open_case_endpoint(
    case_id: int,
    quantity: int = 1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        items = open_case(db, user, case_id, quantity)
        return {
            "success": True,
            "items": [
                {"name": i.name, "rarity": i.rarity, "value": i.value, "image_url": i.image_url}
                for i in items
            ],
        }
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


# отдаём frontend (index.html и всё, что внутри папки frontend) с той же ссылки, что и API
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
