from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import vehicles, work_orders, inventory, digital_twin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Konya Workshop System API", version="1.0.0")

# CORS
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(vehicles.router)
app.include_router(work_orders.router)
app.include_router(inventory.router)
app.include_router(digital_twin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Konya Workshop Manager API"}
