from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.OrgChart)
def create_org_chart(org_chart: schemas.OrgChartCreate, db: Session = Depends(get_db)):
    db_org_chart = models.OrgChart(**org_chart.model_dump())
    db.add(db_org_chart)
    db.commit()
    db.refresh(db_org_chart)
    return db_org_chart

@router.get("/", response_model=List[schemas.OrgChart])
def list_org_charts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    org_charts = db.query(models.OrgChart).offset(skip).limit(limit).all()
    return org_charts 