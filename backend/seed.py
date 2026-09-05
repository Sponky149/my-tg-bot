from database import SessionLocal, Item, Case, CaseItem
 
db = SessionLocal()
 
RARITY_WEIGHT = {
    "common": 70,
    "rare": 20,
    "epic": 8,
    "legendary": 2,
}
 
existing = db.query(Item).count()
if existing > 0:
    print(f"В базе уже есть {existing} предметов, пропускаю наполнение.")
    db.close()
else:
    items_data = [
        {"name": "Bombardiro Crocodilo", "rarity": "common", "value": 10},
        {"name": "Tung Tung Tung Sahur", "rarity": "common", "value": 15},
        {"name": "Ballerina Cappuccina", "rarity": "common", "value": 12},
        {"name": "Boneca Ambalabu", "rarity": "common", "value": 8},
        {"name": "Brr Brr Patapim", "rarity": "common", "value": 18},
        {"name": "Chimpanzini Bananini", "rarity": "common", "value": 14},
        {"name": "Lirili Larila", "rarity": "common", "value": 9},
        {"name": "Trippi Troppi", "rarity": "common", "value": 11},
        {"name": "Girafa Celestre", "rarity": "common", "value": 16},
        {"name": "Frigo Camelo", "rarity": "common", "value": 13},
        {"name": "Tralalero Tralala", "rarity": "rare", "value": 45},
        {"name": "Tric Trac Baraboom", "rarity": "rare", "value": 60},
        {"name": "Bobritto Bandito", "rarity": "rare", "value": 55},
        {"name": "U Din Din Din Dun", "rarity": "rare", "value": 70},
        {"name": "Espresso Signora", "rarity": "rare", "value": 50},
        {"name": "Piccione Macchina", "rarity": "rare", "value": 65},
        {"name": "Cocofanto Elefanto", "rarity": "rare", "value": 75},
        {"name": "Ta Ta Ta Sahur", "rarity": "rare", "value": 40},
        {"name": "Cappuccino Assassino", "rarity": "epic", "value": 250},
        {"name": "Garama and Madundung", "rarity": "epic", "value": 300},
        {"name": "Blueberrinni Octopusini", "rarity": "epic", "value": 220},
        {"name": "Trulimero Trulicina", "rarity": "epic", "value": 280},
        {"name": "La Vacca Saturno Saturnita", "rarity": "epic", "value": 350},
        {"name": "Odin Din Din Dun Boom", "rarity": "legendary", "value": 1200},
        {"name": "Los Tralaleritos", "rarity": "legendary", "value": 2000},
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
        {"name": "Lucky Case", "price": 49, "item_names": [
            "Bombardiro Crocodilo", "Tung Tung Tung Sahur", "Boneca Ambalabu",
            "Chimpanzini Bananini", "Lirili Larila", "Tralalero Tralala",
            "Ta Ta Ta Sahur", "Blueberrinni Octopusini"]},
        {"name": "Crazy Case", "price": 79, "item_names": [
            "Brr Brr Patapim", "Girafa Celestre", "Frigo Camelo",
            "Bobritto Bandito", "Espresso Signora", "Tric Trac Baraboom",
            "Cappuccino Assassino", "Odin Din Din Dun Boom"]},
        {"name": "Mystery Case", "price": 99, "item_names": [
            "Trippi Troppi", "Bombardiro Crocodilo", "U Din Din Din Dun",
            "Piccione Macchina", "Cocofanto Elefanto", "Garama and Madundung",
            "Trulimero Trulicina", "Los Tralaleritos"]},
        {"name": "Rich Case", "price": 149, "item_names": [
            "Tralalero Tralala", "Bobritto Bandito", "Ta Ta Ta Sahur",
            "Cappuccino Assassino", "Blueberrinni Octopusini", "La Vacca Saturno Saturnita",
            "Odin Din Din Dun Boom", "Los Tralaleritos"]},
        {"name": "Legend Case", "price": 249, "item_names": [
            "Espresso Signora", "Cocofanto Elefanto", "Garama and Madundung",
            "Trulimero Trulicina", "La Vacca Saturno Saturnita", "Cappuccino Assassino",
            "Odin Din Din Dun Boom", "Los Tralaleritos"]},
        {"name": "Guest Case", "price": 666, "item_names": [
            "Cappuccino Assassino", "Garama and Madundung", "Blueberrinni Octopusini",
            "Trulimero Trulicina", "La Vacca Saturno Saturnita", "Odin Din Din Dun Boom",
            "Los Tralaleritos", "Cocofanto Elefanto"]},
        {"name": "Case", "price": 1000, "item_names": [
            "Odin Din Din Dun Boom", "Los Tralaleritos", "Cappuccino Assassino",
            "Garama and Madundung", "Blueberrinni Octopusini", "Trulimero Trulicina",
            "La Vacca Saturno Saturnita", "Cocofanto Elefanto"]},
    ]
 
    for c_data in cases_data:
        case = Case(name=c_data["name"], price=c_data["price"])
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
