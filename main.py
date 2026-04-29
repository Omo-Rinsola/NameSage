from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.profiles import router as profiles_router
from core.database import Base, engine

app = FastAPI()

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

# CORS — required by grading script
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles_router)
app.include_router()


@app.get("/")
def home():
    return {"status": "API running"}