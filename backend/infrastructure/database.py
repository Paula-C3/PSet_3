from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Puedes cambiar esto luego por variables de entorno
DATABASE_URL = "sqlite:///./test.db"
# Para PostgreSQL sería algo como:
# DATABASE_URL = "postgresql://user:password@localhost:5432/opscenter"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()