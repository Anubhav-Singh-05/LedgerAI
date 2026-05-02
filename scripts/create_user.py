from core.database import SessionLocal
from core.models import User

db = SessionLocal()

user = User(name="Anubhav")
db.add(user)
db.commit()

print("User created with ID:", user.id)

db.close()
