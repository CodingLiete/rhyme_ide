import asyncio
import csv
import os
import sys
from dotenv import load_dotenv

# Ajout du répertoire racine au PYTHONPATH pour importer app.models
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.models.models import Lexicon

# Chargement du .env
load_dotenv(os.path.join(backend_dir, "..", ".env"))

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)

BATCH_SIZE = 10000
TSV_PATH = os.path.join(os.path.dirname(__file__), "Lexique383.tsv")

async def clean_and_seed_db():
    print("Début de l'analyse du fichier Lexique383...")
    
    # 1. Vérification si la table est déjà remplie (Sécurité)
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT COUNT(*) FROM lexicon"))
        count = result.scalar()
        if count > 0:
            print(f"La base de données contient déjà {count} mots. Annulation pour éviter les doublons.")
            return

    lexicon_batch = []
    total_inserted = 0

    # 2. Lecture et Parsing du TSV
    with open(TSV_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        
        for row in reader:
            # Extraction stricte des données utiles
            word = row.get("ortho", "").strip()
            phonetic = row.get("phon", "").strip()
            
            try:
                syllables = int(row.get("nbsyll", 0))
                frequency = float(row.get("freqlivres", 0.0))
            except ValueError:
                continue # Ignore les lignes avec des données corrompues
            
            # Filtre : On ignore les mots vides ou contenant des caractères complexes (optionnel)
            if not word or not phonetic or " " in word:
                continue
                
            lexicon_batch.append(
                Lexicon(word=word, phonetic=phonetic, syllables=syllables, frequency=frequency)
            )

            # 3. Insertion par lots (Batch Insert)
            if len(lexicon_batch) >= BATCH_SIZE:
                async with AsyncSession(engine) as session:
                    session.add_all(lexicon_batch)
                    await session.commit()
                
                total_inserted += len(lexicon_batch)
                print(f"Insérés : {total_inserted} mots...")
                lexicon_batch.clear() # On vide le lot actuel

    # Insertion des éléments restants (< BATCH_SIZE)
    if lexicon_batch:
        async with AsyncSession(engine) as session:
            session.add_all(lexicon_batch)
            await session.commit()
        total_inserted += len(lexicon_batch)

    print(f"Succès ! {total_inserted} entrées ajoutées au dictionnaire.")

if __name__ == "__main__":
    asyncio.run(clean_and_seed_db())