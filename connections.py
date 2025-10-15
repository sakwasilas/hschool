from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os

DATABASE_URL = "postgresql://wifi_0aqg_user:UJbhFEzLazjs0usFRgxx5q0C8H4O6pwf@dpg-d3nno8idbo4c73d57oo0-a.oregon-postgres.render.com:5432/wifi_0aqg?sslmode=require"

engine = create_engine(DATABASE_URL, echo=True)
Session = scoped_session(sessionmaker(bind=engine))
SessionLocal = Session
Base = declarative_base()
