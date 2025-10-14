from connections import Base, engine
from models import User

Base.metadata.create_all(bind=engine)

print("Tables recreated with latest columns")