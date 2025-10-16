from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# =========================
# New Database URL for hschool
# =========================
DATABASE_URL = "postgresql://hschool_user:MxBBT8XJjKoM6ZZPwR4HvWbjWRfHvgUc@dpg-d3o99njipnbc73fq0am0-a.oregon-postgres.render.com:5432/hschool?sslmode=require"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session
Session = scoped_session(sessionmaker(bind=engine))
SessionLocal = Session

# Base declarative class
Base = declarative_base()
