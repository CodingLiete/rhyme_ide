from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.models import Lexicon
from app.db.database import get_session

router = APIRouter(prefix="/api/rhymes", tags=["Rhymes"])

@router.get("/multisyllabic/{target_word}", response_model=List[Lexicon])
async def get_multisyllabic_rhymes(
    target_word: str, 
    min_syllables: int = 2,
    session: AsyncSession = Depends(get_session)
):
    target_word_clean = target_word.lower().strip()
    
    query_target = select(Lexicon).where(Lexicon.word == target_word_clean)
    result_target = await session.execute(query_target)
    target_entry = result_target.scalars().first()
    
    if not target_entry:
        raise HTTPException(status_code=404, detail="Mot introuvable dans le lexique.")
        
    target_phonetic = target_entry.phonetic
    if len(target_phonetic) < min_syllables:
        raise HTTPException(status_code=400, detail="Mot trop court pour une rime multisyllabique.")

    # Extraction des N derniers phonèmes (Suffixe commun)
    suffix = target_phonetic[-min_syllables:]
    
    # Recherche des mots partageant ce suffixe exact
    query_rhymes = (
        select(Lexicon)
        .where(Lexicon.phonetic.endswith(suffix))
        .where(Lexicon.word != target_word_clean)
        .order_by(Lexicon.frequency.desc())
        .limit(20)
    )
    
    result_rhymes = await session.execute(query_rhymes)
    return result_rhymes.scalars().all()