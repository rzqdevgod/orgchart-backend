from fastapi import FastAPI
from app.routers import org_charts, employees
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Org Chart Service",
    description="A service for managing organization charts with hierarchical operations",
    version="1.0.0"
)

# Include routers
app.include_router(org_charts.router, prefix="/orgcharts", tags=["org_charts"])
app.include_router(employees.router, prefix="/orgcharts/{org_id}/employees", tags=["employees"]) 