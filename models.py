from sqlalchemy import Column, String, Integer
from connections import Base

class User(Base):
    __tablename__ = "users"  # Table name in MySQL database

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    
