from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.profiles import router as profiles_router
from core.database import Base, engine

app = FastAPI()

# create tables
Base.metadata.create_all(bind=engine)

# CORS (REQUIRED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routes
app.include_router(profiles_router)


@app.get("/")
def home():
    return {"status": "API running"}