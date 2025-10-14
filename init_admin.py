from connections import SessionLocal
from models import User

# Create a database session
db = SessionLocal()

try:
   
    admin = db.query(User).filter_by(username="admin").first()

    if not admin:
       
        new_admin = User(username="admin", password="admin123")
        db.add(new_admin)
        db.commit()
        print("✅ Default admin created: username=admin, password=admin123")
    else:
        print("ℹ️ Admin already exists in the database")

except Exception as e:
    db.rollback()
    print("❌ Error:", e)

finally:
    db.close()
