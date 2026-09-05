from sqlalchemy.orm import Session
from database import User, InventoryItem
 
# сколько процентов от "стоимости" предмета игрок реально получает при продаже
# (меньше 100%, иначе можно было бы бесконечно открывать кейс -> продавать -> валюта из ничего
#  почти без потерь, что ломает баланс экономики)
SELL_RATE = 0.5
 
 
def sell_item(db: Session, user: User, inventory_item_id: int) -> dict:
    inv_item = db.query(InventoryItem).filter(
        InventoryItem.id == inventory_item_id,
        InventoryItem.user_id == user.id
    ).first()
 
    if not inv_item:
        raise ValueError("Этот предмет не найден в твоём инвентаре")
 
    item = inv_item.item
    payout = round(item.value * SELL_RATE, 2)
 
    user.balance += payout
    db.delete(inv_item)
    db.commit()
 
    return {
        "success": True,
        "sold_item": item.name,
        "payout": payout,
        "new_balance": user.balance,
    }
