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

def create_user_if_not_exists(db, name, email, password, role):
    existing = db.query(UserModel).filter(UserModel.email == email).first()
    if not existing:
        user = UserModel(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=role
        )
        db.add(user)
        print(f"Usuario creado: {email} / {password} ({role.value})")
    else:
        print(f"Usuario ya existe: {email}")

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
        create_user_if_not_exists(db, "Admin",      "admin@test.com",      "password", Role.ADMIN)
        create_user_if_not_exists(db, "Supervisor", "supervisor@test.com", "password", Role.SUPERVISOR)
        create_user_if_not_exists(db, "Operator",   "operator@test.com",   "password", Role.OPERATOR)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar BD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
