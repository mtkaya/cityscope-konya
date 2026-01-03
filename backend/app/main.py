from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import vehicles, work_orders, inventory, digital_twin

# Try to import traffic analysis (requires ML dependencies)
traffic_analysis_available = False
try:
    from .routers import traffic_analysis
    from .services.scheduler import start_scheduler, stop_scheduler
    traffic_analysis_available = True
except ImportError as e:
    print(f"⚠️ Traffic analysis not available: {e}")
    print("   Install ML dependencies: pip install ultralytics sentinelhub torch opencv-python")


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Konya CityScope API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start traffic analysis scheduler if available
    if traffic_analysis_available:
        print("⏰ Starting traffic analysis scheduler...")
        try:
            start_scheduler()
            print("✅ Scheduler started successfully - running every hour")
        except Exception as e:
            print(f"⚠️ Warning: Could not start scheduler: {e}")
            print("   Traffic analysis can still be triggered manually via API")

    yield

    # Shutdown
    print("🛑 Shutting down...")
    if traffic_analysis_available:
        stop_scheduler()
    print("👋 Goodbye!")


app = FastAPI(
    title="Konya CityScope API",
    version="2.0.0",
    description="Urban analytics platform with satellite-based traffic analysis",
    lifespan=lifespan
)

# CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
    "http://localhost:5000",
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

# Include traffic analysis router if available
if traffic_analysis_available:
    app.include_router(traffic_analysis.router)

@app.get("/")
def read_root():
    features = [
        "Vehicle Management",
        "Work Orders",
        "Inventory Tracking",
        "Digital Twin",
    ]

    if traffic_analysis_available:
        features.append("Satellite Traffic Analysis (YOLO + Sentinel Hub)")

    return {
        "message": "Welcome to Konya CityScope API",
        "version": "2.0.0",
        "features": features,
        "traffic_analysis_enabled": traffic_analysis_available
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-01-03T00:00:00Z"
    }
