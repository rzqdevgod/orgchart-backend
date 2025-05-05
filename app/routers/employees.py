from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.auth import get_optional_current_user, has_permission

router = APIRouter()

def get_employee(db: Session, employee_id: int):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

def is_ceo(db: Session, employee_id: int) -> bool:
    employee = get_employee(db, employee_id)
    return employee.manager_id is None

def check_org_exists(db: Session, org_id: int):
    """Verify organization exists"""
    org = db.query(models.OrgChart).filter(models.OrgChart.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

def would_create_cycle(db: Session, manager_id: int, subordinate_id: int, visited=None):
    """Check if assigning manager_id as manager of subordinate_id would create a cycle"""
    if visited is None:
        visited = set()
    
    if manager_id == subordinate_id:
        return True
    
    if manager_id in visited:
        return True
    
    visited.add(manager_id)
    
    # Get the manager's manager
    manager = db.query(models.Employee).filter(models.Employee.id == manager_id).first()
    if not manager or manager.manager_id is None:
        return False  # Reached CEO, no loop
    
    # Check if this creates a loop
    if manager.manager_id == subordinate_id:
        return True
        
    # Continue checking up the chain
    return would_create_cycle(db, manager.manager_id, subordinate_id, visited)

@router.post("/", response_model=schemas.Employee, dependencies=[Depends(has_permission(["create_employee"]))])
def create_employee(
    org_id: int, 
    employee: schemas.EmployeeCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Create a new employee"""
    # Verify the organization exists
    check_org_exists(db, org_id)
    
    # If manager_id is provided, verify it exists and belongs to the same org
    if employee.manager_id:
        manager = get_employee(db, employee.manager_id)
        if manager.org_id != org_id:
            raise HTTPException(status_code=400, detail="Manager must belong to the same organization")
        
        # Check if the employee will be their own manager (direct cycle)
        if 'id' in dir(employee) and employee.id == employee.manager_id:
            raise HTTPException(status_code=400, detail="Employee cannot be their own manager")
    
    db_employee = models.Employee(**employee.model_dump(), org_id=org_id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/", response_model=List[schemas.Employee])
def list_employees(
    org_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """List all employees in an organization"""
    employees = db.query(models.Employee).filter(models.Employee.org_id == org_id).all()
    return employees

@router.get("/{employee_id}", response_model=schemas.Employee)
def get_employee_by_id(
    org_id: int, 
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Get an employee by ID"""
    employee = get_employee(db, employee_id)
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    return employee

@router.delete("/{employee_id}", dependencies=[Depends(has_permission(["delete_employee"]))])
def delete_employee(
    org_id: int, 
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Delete an employee"""
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
    
    # Get CEO of the organization (for cases where we need to reassign to CEO)
    ceo = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id.is_(None)
    ).first()
    
    # Employee's manager ID (could be null if they report directly to CEO)
    employee_manager_id = employee.manager_id
    
    if reports:
        for report in reports:
            # If the employee being deleted reports to the CEO (null manager_id),
            # reassign their direct reports to the CEO
            if employee_manager_id is None and ceo:
                report.manager_id = ceo.id
            else:
                report.manager_id = employee_manager_id
        
        # Apply changes to ensure all reports are updated before deleting the employee
        db.flush()
    
    # Delete the employee
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}

@router.put("/{employee_id}/promote", response_model=schemas.Employee, dependencies=[Depends(has_permission(["promote_employee"]))])
def promote_to_ceo(
    org_id: int, 
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Promote an employee to CEO"""
    # Verify the organization exists
    check_org_exists(db, org_id)
    
    # Verify the employee exists
    employee = get_employee(db, employee_id)
    
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    # If already CEO, nothing to do
    if employee.manager_id is None:
        return employee
    
    # Get current CEO
    current_ceo = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id.is_(None)
    ).first()
    
    if current_ceo:
        # Ensure we're not creating a cycle (current CEO shouldn't report to someone who reports to them)
        if would_create_cycle(db, employee_id, current_ceo.id):
            # Find the CEO's direct reports that aren't the new CEO
            ceo_reports = db.query(models.Employee).filter(
                models.Employee.org_id == org_id,
                models.Employee.manager_id == current_ceo.id,
                models.Employee.id != employee_id
            ).all()
            
            # Move CEO's direct reports to the new CEO to prevent cycles
            for report in ceo_reports:
                report.manager_id = employee_id
            
            # Apply these changes first
            db.flush()
        
        # Demote current CEO to report to new CEO
        current_ceo.manager_id = employee_id
    
    # Promote new CEO
    employee.manager_id = None
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/{employee_id}/direct_reports", response_model=List[schemas.Employee])
def get_direct_reports(
    org_id: int, 
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Get all direct reports for an employee"""
    employee = get_employee(db, employee_id)
    
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    # Get all direct reports
    direct_reports = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id == employee_id
    ).all()
    
    return direct_reports

@router.put("/{employee_id}", response_model=schemas.Employee, dependencies=[Depends(has_permission(["update_employee"]))])
def update_employee(
    org_id: int, 
    employee_id: int, 
    employee_update: schemas.EmployeeCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Update an employee's information"""
    # Verify the organization exists
    check_org_exists(db, org_id)
    
    # Get the employee to update
    db_employee = get_employee(db, employee_id)
    
    # Verify employee belongs to the organization
    if db_employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    # If updating manager_id, validate it doesn't create cycles
    if employee_update.manager_id:
        # Cannot assign self as manager
        if employee_id == employee_update.manager_id:
            raise HTTPException(status_code=400, detail="Employee cannot be their own manager")
        
        # Verify manager exists and belongs to same org
        manager = get_employee(db, employee_update.manager_id)
        if manager.org_id != org_id:
            raise HTTPException(status_code=400, detail="Manager must belong to the same organization")
        
        # Check if this would create a cycle in the reporting hierarchy
        if would_create_cycle(db, employee_update.manager_id, employee_id):
            raise HTTPException(status_code=400, detail="This assignment would create a cycle in the reporting hierarchy")
        
        # Cannot set CEO to report to someone else through this endpoint
        if is_ceo(db, employee_id):
            raise HTTPException(status_code=400, detail="Cannot change CEO's manager through this endpoint. Use promote_to_ceo instead.")
    
    # Update employee fields
    db_employee.name = employee_update.name
    db_employee.title = employee_update.title
    db_employee.manager_id = employee_update.manager_id
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.put("/{employee_id}/assign_as_manager", response_model=schemas.Employee, dependencies=[Depends(has_permission(["assign_manager"]))])
def assign_as_manager(
    org_id: int, 
    employee_id: int, 
    request: schemas.AssignManagerRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    """Assign an employee as manager for a list of employees"""
    # Verify organization exists
    check_org_exists(db, org_id)
    
    # Verify employee exists and belongs to the organization
    employee = get_employee(db, employee_id)
    
    if employee.org_id != org_id:
        raise HTTPException(status_code=400, detail="Employee does not belong to this organization")
    
    # Can't assign a CEO as manager via this endpoint
    if is_ceo(db, employee_id):
        raise HTTPException(status_code=400, detail="Cannot assign CEO as manager through this endpoint. Use promote_to_ceo instead.")
    
    # Get the CEO for handling hierarchical loops
    ceo = db.query(models.Employee).filter(
        models.Employee.org_id == org_id,
        models.Employee.manager_id.is_(None)
    ).first()
    
    if not ceo:
        raise HTTPException(status_code=500, detail="Organization has no CEO")
    
    # Get employee's current manager
    current_manager_id = employee.manager_id
    
    # Verify each employee in the request and check for potential cycles
    for subordinate_id in request.employee_ids:
        if subordinate_id == employee_id:
            raise HTTPException(status_code=400, detail="Employee cannot be their own manager")
            
        subordinate = get_employee(db, subordinate_id)
        
        # Verify subordinate belongs to the same org
        if subordinate.org_id != org_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Employee {subordinate_id} does not belong to this organization"
            )
            
        # Don't allow assigning CEO as subordinate
        if is_ceo(db, subordinate_id):
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot assign CEO (employee {subordinate_id}) as a subordinate"
            )
        
        # Check if this assignment would create a cycle
        if would_create_cycle(db, employee_id, subordinate_id):
            raise HTTPException(
                status_code=400,
                detail=f"Assigning employee {employee_id} as manager of {subordinate_id} would create a cycle"
            )
            
    # Process the assignments after validation
    for subordinate_id in request.employee_ids:
        subordinate = db.query(models.Employee).filter(models.Employee.id == subordinate_id).first()
        
        # Handle special case: if employee is being assigned as manager of their current manager,
        # reassign their current manager to report to the CEO
        if subordinate_id == current_manager_id:
            employee.manager_id = ceo.id
            
        # Set the new manager
        subordinate.manager_id = employee_id
    
    db.commit()
    db.refresh(employee)
    return employee