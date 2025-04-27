#!/usr/bin/env python
"""
Database setup script for OrgChat application.
This script provides an easy way to set up and seed the database.
"""

import os
import sys
import argparse
import subprocess

def run_script(script_path):
    """Run a Python script and return True if successful."""
    result = subprocess.run([sys.executable, script_path], check=False)
    return result.returncode == 0

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Set up and seed the OrgChat database.')
    parser.add_argument('--setup-only', action='store_true', help='Only set up the database, don\'t seed it')
    parser.add_argument('--seed-only', action='store_true', help='Only seed the database, don\'t create it')
    parser.add_argument('--sql-init', action='store_true', help='Use SQL script to initialize the database')
    parser.add_argument('--num-orgs', type=int, default=None, help='Number of organizations to create (default: 10000)')
    args = parser.parse_args()
    
    # Set environment variables
    if args.num_orgs is not None:
        os.environ['NUM_ORG_CHARTS'] = str(args.num_orgs)
    
    # Determine which scripts to run
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
    
    if args.sql_init:
        # Run SQL initialization script
        sql_runner_script = os.path.join(scripts_dir, 'run_sql_init.py')
        print("Initializing database with SQL script...")
        success = run_script(sql_runner_script)
        if not success:
            print("SQL database initialization failed")
            return 1
        
        if args.seed_only or not args.setup_only:
            # Seed the database after SQL init
            print("\nSeeding database...")
            seed_script = os.path.join(scripts_dir, 'seed_db.py')
            seed_success = run_script(seed_script)
            print("Database seeding " + ("successful" if seed_success else "failed"))
            return 0 if seed_success else 1
        return 0
            
    elif args.setup_only:
        # Only run database setup
        setup_script = os.path.join(scripts_dir, 'db_setup.py')
        print("Setting up database...")
        success = run_script(setup_script)
        print("Database setup " + ("successful" if success else "failed"))
        return 0 if success else 1
    elif args.seed_only:
        # Only run database seeding
        seed_script = os.path.join(scripts_dir, 'seed_db.py')
        print("Seeding database...")
        success = run_script(seed_script)
        print("Database seeding " + ("successful" if success else "failed"))
        return 0 if success else 1
    else:
        # Run the full setup_and_seed script
        setup_and_seed_script = os.path.join(scripts_dir, 'setup_and_seed.py')
        print("Setting up and seeding database...")
        success = run_script(setup_and_seed_script)
        print("Database setup and seeding " + ("successful" if success else "failed"))
        return 0 if success else 1
    
if __name__ == "__main__":
    sys.exit(main()) 