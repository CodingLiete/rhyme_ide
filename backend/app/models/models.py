from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

# --- Modèles d'Infrastructure Créative ---

class Project(SQLModel, table=True):
    """Conteneur principal d'un texte/morceau."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    bpm: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relation One-to-Many avec les versions
    versions: List["Version"] = Relationship(back_populates="project")

class Version(SQLModel, table=True):
    """Historique des brouillons (Versioning)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    content: str # Le texte complet brut
    version_number: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    project: Project = Relationship(back_populates="versions")

# --- Modèles du Moteur Linguistique ---

class Lexicon(SQLModel, table=True):
    """Dictionnaire de référence phonétique (Lecture seule en prod)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(index=True, max_length=100)
    phonetic: str = Field(index=True) # Index crucial pour la recherche de rimes
    syllables: int
    frequency: float = Field(default=0.0) # Pour suggérer les mots les plus courants d'abord

class RhymeVault(SQLModel, table=True):
    """Le coffre-fort personnel de rimes multisyllabiques de l'utilisateur."""
    id: Optional[int] = Field(default=None, primary_key=True)
    phonetic_pattern: str = Field(index=True) # Ex: "a-i-o"
    words_combo: str # Ex: "magie d'eau"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)