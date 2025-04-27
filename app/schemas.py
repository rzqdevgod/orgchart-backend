from pydantic import BaseModel
from typing import Optional, List

class OrgChartBase(BaseModel):
    name: str

class OrgChartCreate(OrgChartBase):
    pass

class OrgChart(OrgChartBase):
    id: int

    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    name: str
    title: str
    manager_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    org_id: int

    class Config:
        from_attributes = True

class EmployeeWithReports(Employee):
    direct_reports: List['EmployeeWithReports'] = []

    class Config:
        from_attributes = True

class EmployeePromote(BaseModel):
    new_ceo_id: int 