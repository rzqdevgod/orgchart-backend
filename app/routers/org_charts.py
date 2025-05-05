from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.auth import get_optional_current_user, has_permission

router = APIRouter()

def get_org_chart(db: Session, org_id: int):
    """Get org chart by ID or raise 404"""
    org_chart = db.query(models.OrgChart).filter(models.OrgChart.id == org_id).first()
    if not org_chart:
        raise HTTPException(status_code=404, detail="Organization chart not found")
    return org_chart

@router.post("/", response_model=schemas.OrgChart, dependencies=[Depends(has_permission(["create_org_chart"]))])
def create_org_chart(
    org_chart: schemas.OrgChartCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Create a new organization chart"""
    db_org_chart = models.OrgChart(**org_chart.model_dump())
    db.add(db_org_chart)
    db.commit()
    db.refresh(db_org_chart)
    return db_org_chart

@router.get("/", response_model=List[schemas.OrgChart])
def list_org_charts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """List all organization charts"""
    org_charts = db.query(models.OrgChart).offset(skip).limit(limit).all()
    return org_charts

@router.get("/{org_id}", response_model=schemas.OrgChart)
def get_org_chart_by_id(
    org_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Get an org chart by ID"""
    return get_org_chart(db, org_id)

@router.put("/{org_id}", response_model=schemas.OrgChart, dependencies=[Depends(has_permission(["update_org_chart"]))])
def update_org_chart(
    org_id: int, 
    org_chart: schemas.OrgChartCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Update an org chart's information"""
    db_org_chart = get_org_chart(db, org_id)
    
    # Update the org chart name
    db_org_chart.name = org_chart.name
    
    db.commit()
    db.refresh(db_org_chart)
    return db_org_chart

@router.delete("/{org_id}", dependencies=[Depends(has_permission(["delete_org_chart"]))])
def delete_org_chart(
    org_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Delete an org chart and all its employees"""
    db_org_chart = get_org_chart(db, org_id)
    
    # Check if the org chart has any employees
    employees = db.query(models.Employee).filter(models.Employee.org_id == org_id).all()
    
    # Delete all employees first to handle foreign key constraints properly
    for employee in employees:
        db.delete(employee)
    
    # Delete the org chart
    db.delete(db_org_chart)
    db.commit()
    
    return {"message": "Organization chart deleted successfully"} 