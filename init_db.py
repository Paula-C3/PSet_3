#!/usr/bin/env python
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DATABASE_URL", "postgresql://opscenter:opscenter_pass@db:5432/opscenter_db")

from backend.infrastructure.database import SessionLocal, Base, engine
from backend.infrastructure.models import UserModel
from backend.domain.enums import Role
from backend.infrastructure.auth import hash_password
import uuid

def init_database():
    max_retries = 30
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Intento {attempt + 1}/{max_retries} fallido, reintentando en {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"Error al conectar a la BD después de {max_retries} intentos: {e}")
                raise
    
    db = SessionLocal()
    
    try:
        existing_user = db.query(UserModel).filter(UserModel.email == "admin@test.com").first()
        
        if not existing_user:
            admin_user = UserModel(
                id=str(uuid.uuid4()),
                name="Admin",
                email="admin@test.com",
                hashed_password=hash_password("password"),
                role=Role.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Usuario de prueba creado: admin@test.com / password")
        else:
            print("Usuario de prueba ya existe")
    except Exception as e:
        print(f"Error al inicializar BD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

