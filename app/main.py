from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import org_charts, employees, auth
from app.database import engine, Base
from app.auth import get_optional_current_user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Org Chart Service",
    description="A service for managing organization charts with hierarchical operations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production to restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional global dependency for authentication
# This is currently a no-op but enables easy addition of authentication later
# app.dependency_overrides[get_optional_current_user] = lambda: None

# Include routers
app.include_router(org_charts.router, prefix="/orgcharts", tags=["org_charts"])
app.include_router(employees.router, prefix="/orgcharts/{org_id}/employees", tags=["employees"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Create an endpoint for auth status checks (disabled for now)
@app.get("/auth/status", tags=["auth"])
async def auth_status(user=Depends(get_optional_current_user)):
    """
    Check authentication status.
    Currently always returns unauthenticated, but is prepared for future implementation.
    """
    return {
        "authenticated": False,
        "message": "Authentication not implemented for testing"
    } 