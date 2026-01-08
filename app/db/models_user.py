from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # In a real production app, password should be hashed. 
    # For this demo, we will store it simply to speed up dev, 
    # BUT we strongly recommend using bcrypt/passlib in production.
    password = Column(String, nullable=False) 
    preferences = Column(String, nullable=True) # Comma-separated string of preferences

class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attraction_id = Column(Integer, nullable=False) # References Attraction.id
