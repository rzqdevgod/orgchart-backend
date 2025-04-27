import os
import sys
import subprocess

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    result = subprocess.run([sys.executable, script_path], check=True)
    return result.returncode == 0

def main():
    print("===== Setting up and seeding the database =====")
    
    # Step 1: Setup the database
    print("\n=> Setting up database...")
    if run_script("db_setup.py"):
        print("Database setup completed successfully")
    else:
        print("Database setup failed")
        return
    
    # Step 2: Seed the database
    print("\n=> Seeding database with sample data...")
    if run_script("seed_db.py"):
        print("Database seeding completed successfully")
    else:
        print("Database seeding failed")
        return
    
    print("\n===== Setup and seeding completed successfully =====")

if __name__ == "__main__":
    main() 