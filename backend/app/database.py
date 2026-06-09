from sqlmodel import create_engine, Session
from app.core.config import settings

# Usamos la URL tal cual viene del .env
engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session