from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

def get_employee(db: Session, employee_id: int):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

def is_ceo(db: Session, employee_id: int) -> bool:
    employee = get_employee(db, employee_id)
    return employee.manager_id is None

@router.post("/", response_model=schemas.Employee)
def create_employee(org_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # If manager_id is provided, verify it exists and belongs to the same org
    if employee.manager_id:
        manager = get_employee(db, employee.manager_id)
        if manager.org_id != org_id:
            raise HTTPException(status_code=400, detail="Manager must belong to the same organization")
    
    db_employee = models.Employee(**employee.model_dump(), org_id=org_id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/", response_model=List[schemas.Employee])
def list_employees(org_id: int, db: Session = Depends(get_db)):
    employees = db.query(models.Employee).filter(models.Employee.org_id == org_id).all()
    return employees

@router.get("/{employee_id}", response_model=schemas.Employee)
def get_employee_by_id(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee(db, employee_id)
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    return employee

@router.delete("/{employee_id}")
def delete_employee(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee(db, employee_id)
    
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    if is_ceo(db, employee_id):
        raise HTTPException(status_code=403, detail="Cannot delete CEO")
    
    # Get all direct reports
    reports = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id == employee_id
    ).all()
    
    # Re-parent all reports to the employee's manager
    for report in reports:
        report.manager_id = employee.manager_id
    
    # Delete the employee
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}

@router.put("/{employee_id}/promote", response_model=schemas.Employee)
def promote_to_ceo(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee(db, employee_id)
    
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    # Get current CEO
    current_ceo = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id.is_(None)
    ).first()
    
    if current_ceo:
        # Demote current CEO
        current_ceo.manager_id = employee_id
    
    # Promote new CEO
    employee.manager_id = None
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/{employee_id}/direct_reports", response_model=List[schemas.Employee])
def get_direct_reports(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee(db, employee_id)
    
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    # Get all direct reports
    direct_reports = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id == employee_id
    ).all()
    
    return direct_reports
