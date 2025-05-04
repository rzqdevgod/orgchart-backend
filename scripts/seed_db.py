import random
import string
import sys
import os
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import OrgChart, Employee
from app.database import Base
from dotenv import load_dotenv
import traceback

load_dotenv()

# Lists of realistic first and last names
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Joseph", "Charles", "Thomas", "Daniel",
    "Matthew", "Anthony", "Mark", "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin",
    "Brian", "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob", "Gary",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
    "Lisa", "Nancy", "Betty", "Sandra", "Margaret", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
    "Carol", "Amanda", "Dorothy", "Melissa", "Deborah", "Stephanie", "Rebecca", "Laura", "Sharon", "Cynthia"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
    "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins"
]

# Job titles for variety
JOB_TITLES = [
    "Software Engineer", "Product Manager", "Data Analyst", "Marketing Specialist", "Sales Representative",
    "HR Coordinator", "Financial Analyst", "Customer Support", "Operations Manager", "Research Scientist",
    "UX Designer", "Content Writer", "Systems Administrator", "Business Analyst", "Quality Assurance"
]

def random_name():
    """Generate a random realistic name"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_title(is_manager=False):
    """Generate a random job title"""
    if is_manager:
        return f"{random.choice(['Senior', 'Lead', 'Principal', 'Head of'])} {random.choice(JOB_TITLES)}"
    return random.choice(JOB_TITLES)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_org_charts_bulk(session, start_id, batch_size=100):
    try:
        # Generate company names for more variety
        company_types = ["Inc.", "LLC", "Corporation", "Group", "Technologies", "Solutions", "International", "Associates"]
        company_adjectives = ["Global", "Advanced", "Innovative", "Modern", "Strategic", "Premier", "Elite", "United"]
        company_names = []
        
        for i in range(start_id, start_id + batch_size):
            if random.random() < 0.3:  # 30% chance of adjective + type
                name = f"{random.choice(company_adjectives)} {random.choice(LAST_NAMES)} {random.choice(company_types)}"
            else:  # 70% chance of just last name + type
                name = f"{random.choice(LAST_NAMES)} {random.choice(company_types)}"
            company_names.append(name)
        
        # Bulk insert org charts
        org_charts = [
            OrgChart(name=company_names[i - start_id])
            for i in range(start_id, start_id + batch_size)
        ]
        session.bulk_save_objects(org_charts)
        session.flush()
        
        # Get the inserted org chart IDs
        org_ids = session.query(OrgChart.id).order_by(OrgChart.id.desc()).limit(batch_size).all()
        org_ids = [org_id for (org_id,) in org_ids]
        
        # Create employees for each org chart
        all_employees = []
        
        for org_id in org_ids:
            # Create CEO
            ceo = Employee(
                name=random_name(),
                title="Chief Executive Officer",
                org_id=org_id,
                manager_id=None
            )
            all_employees.append(ceo)
        
        # Bulk insert CEOs first to get their IDs
        session.bulk_save_objects(all_employees)
        session.flush()
        
        # Get the CEO IDs for each org
        ceo_ids = {}
        for org_id in org_ids:
            ceo = session.query(Employee.id).filter(
                Employee.org_id == org_id,
                Employee.title == "Chief Executive Officer"
            ).first()
            if ceo:
                ceo_ids[org_id] = ceo[0]
        
        # Create additional employees with proper manager relationships
        additional_employees = []
        
        for org_id in org_ids:
            if org_id not in ceo_ids:
                continue
                
            ceo_id = ceo_ids[org_id]
            
            # Create 4-14 additional employees per org
            num_employees = random.randint(4, 14)
            
            # First level managers (report to CEO)
            managers = []
            for i in range(min(3, num_employees)):
                manager = Employee(
                    name=random_name(),
                    title=random_title(is_manager=True),
                    org_id=org_id,
                    manager_id=ceo_id
                )
                managers.append(manager)
            
            additional_employees.extend(managers)
            
            # Add remaining employees as regular staff
            remaining = num_employees - len(managers)
            if remaining > 0:
                for i in range(remaining):
                    employee = Employee(
                        name=random_name(),
                        title=random_title(),
                        org_id=org_id,
                        manager_id=ceo_id  # All report to CEO initially - will update after insert
                    )
                    additional_employees.append(employee)
        
        # Bulk insert all additional employees
        session.bulk_save_objects(additional_employees)
        
        return len(org_ids)
    except Exception as e:
        print(f"Error creating org charts batch starting at {start_id}: {str(e)}")
        traceback.print_exc()
        return 0

def main():
    try:
        start_time = time.time()
        
        # Create database engine with optimized parameters
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orgchart")
        print(f"Connecting to database: {database_url}")
        
        engine = create_engine(database_url, pool_size=10, max_overflow=20)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create tables if they don't exist
        print("Creating tables if they don't exist...")
        Base.metadata.create_all(engine)
        
        # Get the number of org charts to create
        num_orgs = int(os.getenv("NUM_ORG_CHARTS", 10000))
        if len(sys.argv) > 1:
            try:
                num_orgs = int(sys.argv[1])
            except ValueError:
                pass
        
        print(f"Creating {num_orgs} org charts...")
        
        # Use larger batch size for better performance
        batch_size = 500
        total_created = 0
        
        for start_id in range(1, num_orgs + 1, batch_size):
            # Calculate actual batch size (might be smaller for the last batch)
            current_batch_size = min(batch_size, num_orgs - start_id + 1)
            
            # Skip if batch size is 0 or negative
            if current_batch_size <= 0:
                break
                
            batch_created = create_org_charts_bulk(session, start_id, current_batch_size)
            total_created += batch_created
            
            # Commit after each batch
            session.commit()
            
            elapsed = time.time() - start_time
            rate = total_created / elapsed if elapsed > 0 else 0
            
            print(f"Created {total_created} org charts ({rate:.1f} orgs/sec) - {(total_created/num_orgs*100):.1f}% complete")
        
        print(f"Successfully created {total_created} out of {num_orgs} org charts")
        print(f"Total time: {time.time() - start_time:.2f} seconds")
        
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