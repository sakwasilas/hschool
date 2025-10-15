from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# ✅ Updated PostgreSQL database URL (with SSL enabled)
DATABASE_URL = "postgresql://school_g9x1_user:VuaSxt0uTB1OD5wICwljmyi0AELhZuuj@dpg-d3nn1d1gv73c73cfopo0-a.oregon-postgres.render.com:5432/school_g9x1?sslmode=require"

# ✅ Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# ✅ Create session factory
Session = scoped_session(sessionmaker(bind=engine))
SessionLocal = Session

# ✅ Declare base class for models
Base = declarative_base()
