from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# =========================
# New Database URL for hschool
# =========================
DATABASE_URL = "postgresql://hschool_9y3l_user:j28UI9gAjgfVgmPMLXpC9RqBMtrVDYn5@dpg-d4dht03ipnbc73a31cgg-a.oregon-postgres.render.com:5432/hschool_9y3l?sslmode=require"


# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session
Session = scoped_session(sessionmaker(bind=engine))
SessionLocal = Session

# Base declarative class
Base = declarative_base()
