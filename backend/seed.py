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
        {"name": "La Grande", "rarity": "common", "value": 9, "image_url": "/images/la_grande.png"},
        {"name": "67", "rarity": "common", "value": 12, "image_url": "/images/sixty_seven.png"},
        {"name": "1 Cash", "rarity": "common", "value": 1, "is_daily_pool": True, "daily_weight": 50, "image_url": ""},
        {"name": "3 Cash", "rarity": "common", "value": 3, "is_daily_pool": True, "daily_weight": 25, "image_url": ""},
        {"name": "5 Cash", "rarity": "common", "value": 5, "is_daily_pool": True, "daily_weight": 10, "image_url": ""},
        {"name": "Bacuru and Egguru", "rarity": "common", "value": 15, "image_url": "/images/bacuru_and_egguru.png"},
        {"name": "Los Mobilis", "rarity": "common", "value": 18, "image_url": "/images/los_mobilis.png"},
        {"name": "Ketupat Kepat", "rarity": "common", "value": 19, "image_url": "/images/ketupat_kepat.png"},
        {"name": "Noodle Noodle Poodle", "rarity": "common", "value": 24, "image_url": "/images/noodle_noodle_poodle.png"},
        {"name": "Capitano Gullini", "rarity": "common", "value": 25, "image_url": "/images/capitano_gullini.png"},
        {"name": "Tic Tac Sahur", "rarity": "common", "value": 26, "image_url": "/images/tic_tac_sahur.png"},
        {"name": "Ketchuru and Musturu", "rarity": "common", "value": 29, "image_url": "/images/ketchuru_and_musturu.png"},
        {"name": "Los Mariachis", "rarity": "common", "value": 35, "image_url": "/images/los_mariachis.png"},
        {"name": "Coco and Mango", "rarity": "common", "value": 39, "image_url": "/images/coco_and_mango.png"},
        {"name": "Steakini Fattini", "rarity": "rare", "value": 49, "image_url": ""},
        {"name": "W or L", "rarity": "rare", "value": 65, "image_url": ""},
        {"name": "Gold Gold Gold", "rarity": "rare", "value": 55, "image_url": ""},
        {"name": "Jolly Jolly Sahur", "rarity": "rare", "value": 99, "image_url": ""},
        {"name": "Festive 67", "rarity": "rare", "value": 65, "image_url": ""},
        {"name": "Boppin Bunny", "rarity": "rare", "value": 119, "image_url": ""},
        {"name": "Cerberus", "rarity": "rare", "value": 75, "image_url": ""},
        {"name": "Sammyni Fattini", "rarity": "rare", "value": 70, "image_url": ""},
        {"name": "Money Money Bros", "rarity": "rare", "value": 105, "image_url": ""},
        {"name": "Spooky and Pumpky", "rarity": "rare", "value": 90, "image_url": ""},
        {"name": "Cash or Card", "rarity": "common", "value": 30, "image_url": ""},
        {"name": "Los Tacoritas", "rarity": "epic", "value": 249, "image_url": ""},
        {"name": "La Fuse Machine", "rarity": "epic", "value": 219, "image_url": ""},
        {"name": "Guest 666", "rarity": "epic", "value": 299, "image_url": ""},
        {"name": "Rubiko and Kubiko", "rarity": "epic", "value": 379, "image_url": ""},
        {"name": "Fortunu and Cashuru", "rarity": "epic", "value": 399, "image_url": ""},
        {"name": "La Supreme Combinasion", "rarity": "legendary", "value": 2999, "image_url": ""},
        {"name": "Griffin", "rarity": "legendary", "value": 4499, "image_url": ""},
        {"name": "Dragon Gingerini", "rarity": "legendary", "value": 5999, "image_url": ""},
        {"name": "Antonio", "rarity": "legendary", "value": 8499, "image_url": ""},
        {"name": "Skibidi Toilet", "rarity": "legendary", "value": 13999, "image_url": ""},
        {"name": "Rico Dinero", "rarity": "epic", "value": 250, "image_url": ""},
        {"name": "Rosey and Teddy", "rarity": "epic", "value": 220, "image_url": ""},
        {"name": "Capitano Moby", "rarity": "rare", "value": 45, "image_url": ""},
        {"name": "Tuff Toucan", "rarity": "rare", "value": 45, "image_url": ""},
        {"name": "Fragola La La La", "rarity": "rare", "value": 42, "image_url": ""},
        {"name": "La Taco Combinasion", "rarity": "common", "value": 30, "image_url": ""},
        {"name": "Burguro And Fryuro", "rarity": "common", "value": 27, "image_url": ""},
        {"name": "Garama and Madundung", "rarity": "common", "value": 25, "is_daily_pool": True, "daily_weight": 0.1, "image_url": ""},
        {"name": "John Doe", "rarity": "common", "value": 25, "image_url": ""},
        {"name": "Mariachi Corazoni", "rarity": "common", "value": 9, "image_url": ""},
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
        {"name": "Lucky Case", "price": 49, "image_url": "/images/Lucky.png", "item_names": [
            "Rico Dinero", "Rosey and Teddy", "Spooky and Pumpky", "Cerberus",
            "Sammyni Fattini", "Festive 67", "Capitano Moby", "Tuff Toucan",
            "Fragola La La La", "La Taco Combinasion", "Burguro And Fryuro",
            "Garama and Madundung", "John Doe"]},
        {"name": "Crazy Case", "price": 79, "image_url": "/images/crazy.png", "item_names": [
            "Los Mariachis", "Ketchuru and Musturu", "Noodle Noodle Poodle",
            "Gold Gold Gold", "Festive 67", "W or L",
            "Los Tacoritas", "Griffin"]},
        {"name": "Mystery Case", "price": 99, "image_url": "/images/mystery.png", "item_names": [
            "Los Mobilis", "Bacuru and Egguru", "Jolly Jolly Sahur",
            "Boppin Bunny", "Cerberus", "La Fuse Machine",
            "Fortunu and Cashuru", "Dragon Gingerini"]},
        {"name": "Rich Case", "price": 149, "image_url": "/images/rich.png", "item_names": [
            "Steakini Fattini", "Gold Gold Gold", "Sammyni Fattini",
            "Los Tacoritas", "Rubiko and Kubiko", "Guest 666",
            "Griffin", "Dragon Gingerini"]},
        {"name": "Legend Case", "price": 249, "image_url": "/images/legend.png", "item_names": [
            "Festive 67", "Cerberus", "La Fuse Machine",
            "Fortunu and Cashuru", "Guest 666", "Los Tacoritas",
            "Griffin", "Dragon Gingerini"]},
        {"name": "Guest Case", "price": 666, "image_url": "/images/guest.png", "item_names": [
            "Los Tacoritas", "La Fuse Machine", "Rubiko and Kubiko",
            "Fortunu and Cashuru", "Guest 666", "Griffin",
            "Dragon Gingerini", "Cerberus"]},
        {"name": "Case God", "price": 1000, "image_url": "/images/god.png", "item_names": [
            "Griffin", "Dragon Gingerini", "Los Tacoritas",
            "La Fuse Machine", "Rubiko and Kubiko", "Fortunu and Cashuru",
            "Guest 666", "Cerberus"]},
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
