"""
UrbanSenseAI - Database Initialization Script
Follows Requirement 3:
1. Connects first to the existing 'postgres' maintenance database.
2. Checks if the 'urbansense' database exists; creates it if missing.
3. Connects to 'urbansense' database.
4. Creates all tables, foreign keys, and indexes from database/schema.sql.
"""

import os
import sys
import argparse
from pathlib import Path
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def load_env():
    """Simple .env parser to avoid extra dependency issues."""
    env_file = ROOT_DIR / ".env"
    env_vars = {}
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def main():
    parser = argparse.ArgumentParser(description="Initialize UrbanSenseAI PostgreSQL Database")
    parser.add_argument("--host", default=None, help="PostgreSQL host")
    parser.add_argument("--port", default=None, help="PostgreSQL port")
    parser.add_argument("--user", default=None, help="PostgreSQL username")
    parser.add_argument("--password", default=None, help="PostgreSQL password")
    parser.add_argument("--dbname", default="urbansense", help="Target database name")
    args = parser.parse_args()

    env = load_env()

    # Determine connection parameters
    host = args.host or env.get("POSTGRES_HOST", "localhost")
    port = args.port or env.get("POSTGRES_PORT", "5432")
    user = args.user or env.get("POSTGRES_USER", "postgres")
    password = args.password or env.get("POSTGRES_PASSWORD", "postgres")
    target_db = args.dbname or env.get("POSTGRES_DB", "urbansense")

    print("=" * 60)
    print("UrbanSenseAI - PostgreSQL Database Setup")
    print("=" * 60)
    print(f"Host: {host}:{port}")
    print(f"User: {user}")
    print(f"Target Database: {target_db}")

    # Step 1: Connect to default maintenance database 'postgres'
    print("\n[Step 1/3] Connecting to default 'postgres' database...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print(" Connected to 'postgres' maintenance database.")
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure PostgreSQL 18 service is running.")
        print(f"2. Check if the password is correct. You can update it in .env or pass --password <YOUR_PASSWORD>")
        sys.exit(1)

    # Step 2: Check and create target database
    print(f"\n[Step 2/3] Checking if database '{target_db}' exists...")
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
    exists = cursor.fetchone()

    if not exists:
        print(f"Database '{target_db}' does not exist. Creating it now...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
        print(f"✅ Database '{target_db}' created successfully.")
    else:
        print(f" Database '{target_db}' already exists.")

    cursor.close()
    conn.close()

    # Step 3: Connect to target database and apply schema
    print(f"\n[Step 3/3] Connecting to '{target_db}' and applying schema...")
    try:
        target_conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=target_db
        )
        target_cursor = target_conn.cursor()

        schema_file = ROOT_DIR / "database" / "schema.sql"
        if not schema_file.exists():
            print(f"❌ Schema file not found at {schema_file}")
            sys.exit(1)

        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        target_cursor.execute(schema_sql)
        target_conn.commit()

        # Verify created tables
        target_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = [row[0] for row in target_cursor.fetchall()]

        print("✅ Schema applied successfully!")
        print(f"Tables in '{target_db}':")
        for table in tables:
            print(f"  - {table}")

        target_cursor.close()
        target_conn.close()
        print("\n🎉 Database initialization complete!")

    except Exception as e:
        print(f"\n❌ Failed to apply schema to '{target_db}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
