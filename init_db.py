import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from backend.infrastructure.database import SessionLocal, Base, engine
from backend.infrastructure.models import UserModel
from backend.domain.enums import Role
from backend.infrastructure.auth import get_password_hash
import uuid

def init_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        existing_user = db.query(UserModel).filter(UserModel.email == "admin@test.com").first()
        
        if not existing_user:
            admin_user = UserModel(
                id=str(uuid.uuid4()),
                name="Admin",
                email="admin@test.com",
                hashed_password=get_password_hash("password"),
                role=Role.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Usuario de prueba creado: admin@test.com / password")
        else:
            print("Usuario de prueba ya existe")
    
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
