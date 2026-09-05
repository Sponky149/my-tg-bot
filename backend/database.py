import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Если задана DATABASE_URL (настоящая база на Render) - используем её.
# Если нет (локальная разработка на компьютере) - используем обычный файл SQLite.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render иногда отдаёт ссылку в старом формате "postgres://", а SQLAlchemy
    # требует "postgresql://" - подменяем префикс, если нужно.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine("sqlite:///game.db")

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    balance = Column(Float, default=300.0)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_daily_claim = Column(DateTime, nullable=True)
    cases_opened = Column(Integer, default=0)
    upgrades_done = Column(Integer, default=0)

    inventory = relationship("InventoryItem", back_populates="owner")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rarity = Column(String)
    value = Column(Float)
    image_url = Column(String, nullable=True)


class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    obtained_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="inventory")
    item = relationship("Item")


class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    image_url = Column(String, nullable=True)


class CaseItem(Base):
    __tablename__ = "case_items"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    weight = Column(Float)


class DropLog(Base):
    """Журнал всех выпадений (кейсы + ежедневный бонус) - нужен для
    'Последних дропов' и 'Лучшего дропа' в профиле."""
    __tablename__ = "drop_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    item_name = Column(String)
    item_rarity = Column(String)
    item_value = Column(Float)
    source = Column(String)  # "case" или "daily"
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
