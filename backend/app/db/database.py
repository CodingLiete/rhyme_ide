import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    env_trouve = find_dotenv()
    raise ValueError(f"CRITIQUE : DATABASE_URL introuvable. Fichier .env détecté à : {env_trouve}")

# 1. Création du moteur asynchrone
engine = create_async_engine(DATABASE_URL, echo=False)

# 2. Configuration du générateur de sessions
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 3. Dépendance pour FastAPI
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session