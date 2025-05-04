from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class OrgChart(Base):
    __tablename__ = "org_charts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    employees = relationship("Employee", back_populates="org_chart", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    org_id = Column(Integer, ForeignKey("org_charts.id", ondelete="CASCADE"), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    org_chart = relationship("OrgChart", back_populates="employees")
    manager = relationship("Employee", remote_side=[id], backref="direct_reports")

    # Add indexes for performance
    __table_args__ = (
        Index('ix_employees_org_id', 'org_id'),
        Index('ix_employees_manager_id', 'manager_id'),
    )