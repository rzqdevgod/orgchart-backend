import random
import string
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import OrgChart, Employee
from app.database import Base
from dotenv import load_dotenv
import traceback

load_dotenv()

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_org_chart_with_employees(session, org_id):
    try:
        # Create org chart
        org = OrgChart(name=f"Organization {org_id}")
        session.add(org)
        session.flush()  # Get the org.id
        
        # Create CEO
        ceo = Employee(
            name=f"CEO {org_id}",
            title="Chief Executive Officer",
            org_id=org.id,
            manager_id=None
        )
        session.add(ceo)
        session.flush()
        
        # Create 4-14 additional employees
        num_employees = random.randint(4, 14)
        for i in range(num_employees):
            # Randomly assign to CEO or another employee
            manager_id = ceo.id if random.random() < 0.5 else None
            if manager_id is None and i > 0:
                manager_id = random.choice(session.query(Employee.id).filter(
                    Employee.org_id == org.id,
                    Employee.id != ceo.id
                ).all())[0]
            
            employee = Employee(
                name=f"Employee {i+1} of Org {org_id}",
                title=f"Title {random.randint(1, 5)}",
                org_id=org.id,
                manager_id=manager_id
            )
            session.add(employee)
        
        return True
    except Exception as e:
        print(f"Error creating org chart {org_id}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    try:
        # Create database engine
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orgchart")
        print(f"Connecting to database: {database_url}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create tables if they don't exist
        print("Creating tables if they don't exist...")
        Base.metadata.create_all(engine)
        
        # Get the number of org charts to create from environment variable, 
        # or command line argument, or default to 100 for testing
        num_orgs = int(os.getenv("NUM_ORG_CHARTS", 10000))
        if len(sys.argv) > 1:
            try:
                num_orgs = int(sys.argv[1])
            except ValueError:
                pass
        
        print(f"Creating {num_orgs} org charts...")
        success_count = 0
        
        for i in range(1, num_orgs + 1):
            if create_org_chart_with_employees(session, i):
                success_count += 1
                
            if i % 10 == 0:
                # Commit every 10 organizations to avoid large transactions
                session.commit()
                print(f"Created {i} org charts")
        
        # Final commit for any remaining records
        session.commit()
        print(f"Successfully created {success_count} out of {num_orgs} org charts")
        
    except Exception as e:
        print(f"Error in main seeding function: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 