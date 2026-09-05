from fastapi import FastAPI
from app.api import rhymes

app = FastAPI(
    title="Rhyme Engine API",
    description="IDE backend pour l'ingénierie textuelle et phonétique.",
    version="1.0.0"
)

# Inclusion du routeur
app.include_router(rhymes.router)

@app.get("/")
async def root():
    return {"message": "Le moteur de rimes est opérationnel."}