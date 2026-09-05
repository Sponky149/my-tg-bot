from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
 
engine = create_engine("sqlite:///game.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
 
 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    balance = Column(Float, default=100.0)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_daily_claim = Column(DateTime, nullable=True) 
 
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
 
 
Base.metadata.create_all(engine)
 
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
