import random


def roll_multiplier() -> float:
    """
    Честный, фиксированный шанс бонусного множителя ценности при выпадении предмета:
    x4 - 5%, x3 - 10%, x2 - 20%, x1 (без бонуса) - оставшиеся 65%.
    """
    roll = random.uniform(0, 100)
    if roll <= 5:
        return 4.0
    elif roll <= 15:       # 5 + 10
        return 3.0
    elif roll <= 35:       # 5 + 10 + 20
        return 2.0
    return 1.0
