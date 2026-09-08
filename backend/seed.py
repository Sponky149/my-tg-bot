from database import SessionLocal, Item, Case, CaseItem

db = SessionLocal()

RARITY_WEIGHT = {
    "common": 70,
    "rare": 20,
    "epic": 8,
    "legendary": 2,
}

# ============================================================
# КАРТИНКИ - впиши сюда свои ссылки (см. инструкцию ниже).
# Если оставить пустую строку "" - будет показываться эмодзи по редкости,
# как сейчас. Как только впишешь ссылку - на фронте появится картинка.
# ============================================================

existing = db.query(Item).count()
if existing > 0:
    print(f"В базе уже есть {existing} предметов, пропускаю наполнение.")
    db.close()
else:
    items_data = [
        {"name": "Bombardiro Crocodilo", "rarity": "common", "value": 10, "image_url": ""},
        {"name": "Tung Tung Tung Sahur", "rarity": "common", "value": 15, "image_url": ""},
        {"name": "Ballerina Cappuccina", "rarity": "common", "value": 12, "image_url": ""},
        {"name": "Boneca Ambalabu", "rarity": "common", "value": 8, "image_url": ""},
        {"name": "Brr Brr Patapim", "rarity": "common", "value": 18, "image_url": ""},
        {"name": "Chimpanzini Bananini", "rarity": "common", "value": 14, "image_url": ""},
        {"name": "Lirili Larila", "rarity": "common", "value": 9, "image_url": ""},
        {"name": "Trippi Troppi", "rarity": "common", "value": 11, "image_url": ""},
        {"name": "Girafa Celestre", "rarity": "common", "value": 16, "image_url": ""},
        {"name": "Frigo Camelo", "rarity": "common", "value": 13, "image_url": ""},
        {"name": "Tralalero Tralala", "rarity": "rare", "value": 45, "image_url": ""},
        {"name": "Tric Trac Baraboom", "rarity": "rare", "value": 60, "image_url": ""},
        {"name": "Bobritto Bandito", "rarity": "rare", "value": 55, "image_url": ""},
        {"name": "U Din Din Din Dun", "rarity": "rare", "value": 70, "image_url": ""},
        {"name": "Espresso Signora", "rarity": "rare", "value": 50, "image_url": ""},
        {"name": "Piccione Macchina", "rarity": "rare", "value": 65, "image_url": ""},
        {"name": "Cocofanto Elefanto", "rarity": "rare", "value": 75, "image_url": ""},
        {"name": "Ta Ta Ta Sahur", "rarity": "rare", "value": 40, "image_url": ""},
        {"name": "Cappuccino Assassino", "rarity": "epic", "value": 250, "image_url": ""},
        {"name": "Garama and Madundung", "rarity": "epic", "value": 300, "image_url": ""},
        {"name": "Blueberrinni Octopusini", "rarity": "epic", "value": 220, "image_url": ""},
        {"name": "Trulimero Trulicina", "rarity": "epic", "value": 280, "image_url": ""},
        {"name": "La Vacca Saturno Saturnita", "rarity": "epic", "value": 350, "image_url": ""},
        {"name": "Odin Din Din Dun Boom", "rarity": "legendary", "value": 1200, "image_url": ""},
        {"name": "Los Tralaleritos", "rarity": "legendary", "value": 2000, "image_url": ""},
    ]

    items = {}
    for data in items_data:
        item = Item(**data)
        db.add(item)
        db.flush()
        items[data["name"]] = item

    db.commit()
    print(f"Добавлено предметов: {len(items)}")

    cases_data = [
        {"name": "Lucky Case", "price": 49, "image_url": "", "item_names": [
            "Bombardiro Crocodilo", "Tung Tung Tung Sahur", "Boneca Ambalabu",
            "Chimpanzini Bananini", "Lirili Larila", "Tralalero Tralala",
            "Ta Ta Ta Sahur", "Blueberrinni Octopusini"]},
        {"name": "Crazy Case", "price": 79, "image_url": "/images/crazy_case.jpg", "item_names": [
            "Brr Brr Patapim", "Girafa Celestre", "Frigo Camelo",
            "Bobritto Bandito", "Espresso Signora", "Tric Trac Baraboom",
            "Cappuccino Assassino", "Odin Din Din Dun Boom"]},
        {"name": "Mystery Case", "price": 99, "image_url": "/images/mystery_case.jpg", "item_names": [
            "Trippi Troppi", "Bombardiro Crocodilo", "U Din Din Din Dun",
            "Piccione Macchina", "Cocofanto Elefanto", "Garama and Madundung",
            "Trulimero Trulicina", "Los Tralaleritos"]},
        {"name": "Rich Case", "price": 149, "image_url": "/images/rich_case.jpg", "item_names": [
            "Tralalero Tralala", "Bobritto Bandito", "Ta Ta Ta Sahur",
            "Cappuccino Assassino", "Blueberrinni Octopusini", "La Vacca Saturno Saturnita",
            "Odin Din Din Dun Boom", "Los Tralaleritos"]},
        {"name": "Legend Case", "price": 249, "image_url": "/images/legend_case.jpg", "item_names": [
            "Espresso Signora", "Cocofanto Elefanto", "Garama and Madundung",
            "Trulimero Trulicina", "La Vacca Saturno Saturnita", "Cappuccino Assassino",
            "Odin Din Din Dun Boom", "Los Tralaleritos"]},
        {"name": "Guest Case", "price": 666, "image_url": "", "item_names": [
            "Cappuccino Assassino", "Garama and Madundung", "Blueberrinni Octopusini",
            "Trulimero Trulicina", "La Vacca Saturno Saturnita", "Odin Din Din Dun Boom",
            "Los Tralaleritos", "Cocofanto Elefanto"]},
        {"name": "Case God", "price": 1000, "image_url": "/images/god_case.jpg", "item_names": [
            "Odin Din Din Dun Boom", "Los Tralaleritos", "Cappuccino Assassino",
            "Garama and Madundung", "Blueberrinni Octopusini", "Trulimero Trulicina",
            "La Vacca Saturno Saturnita", "Cocofanto Elefanto"]},
    ]

    for c_data in cases_data:
        case = Case(name=c_data["name"], price=c_data["price"], image_url=c_data.get("image_url") or None)
        db.add(case)
        db.flush()
        for item_name in c_data["item_names"]:
            item = items[item_name]
            weight = RARITY_WEIGHT.get(item.rarity, 1)
            db.add(CaseItem(case_id=case.id, item_id=item.id, weight=weight))

    db.commit()
    print(f"Создано кейсов: {len(cases_data)}")
    db.close()
    print("Готово!")
