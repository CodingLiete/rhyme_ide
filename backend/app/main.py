import os

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import rhymes

from arcjet import Mode, arcjet, detect_bot, sliding_window


# 1. Chargement des variables d'environnement
load_dotenv(find_dotenv())


app = FastAPI(
    title="Rhyme Engine API",
    description="IDE backend pour l'ingénierie textuelle et phonétique.",
    version="1.0.0"
)


# 2. Récupération de la clé Arcjet
ARCJET_KEY = os.environ.get("ARCJET_KEY")


# 3. Configuration d'Arcjet
aj = None

if not ARCJET_KEY:
    print("ATTENTION : ARCJET_KEY introuvable. Le pare-feu est désactivé.")

else:
    aj = arcjet(
        key=ARCJET_KEY,
        rules=[
            # Détection des bots
            detect_bot(
                mode=Mode.LIVE,
                allow=[]
            ),

            # Maximum de 100 requêtes par minute
            sliding_window(
                mode=Mode.LIVE,
                interval=60,
                max=100
            ),
        ],
    )


# 4. Middleware de protection global
@app.middleware("http")
async def arcjet_protection(request: Request, call_next):

    # Si Arcjet n'est pas configuré, continuer normalement
    if aj is None:
        return await call_next(request)

    try:
        # Demande à Arcjet d'analyser la requête
        decision = await aj.protect(request)

        # Si Arcjet bloque la requête
        if decision.is_denied():

            # Rate limit
            if decision.reason_v2.type == "RATE_LIMIT":
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests"
                    },
                )

            # Bot ou autre activité bloquée
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden"
                },
            )

    except Exception as error:
        # En développement, on évite de rendre toute l'API indisponible
        print(f"Erreur Arcjet : {error}")

    return await call_next(request)


# 5. Inclusion du routeur
app.include_router(rhymes.router)


@app.get("/")
async def root():
    return {
        "message": "Le moteur de rimes est opérationnel."
    }