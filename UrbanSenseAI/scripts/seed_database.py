"""
UrbanSenseAI - Database Seed Script
Executes database/seed.sql to populate initial fleet nodes and sample data.
"""

import os
import sys
import argparse
from pathlib import Path
import psycopg2

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def load_env():
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
    parser = argparse.ArgumentParser(description="Seed UrbanSenseAI Database")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--dbname", default=None)
    args = parser.parse_args()

    env = load_env()

    host = args.host or env.get("POSTGRES_HOST", "localhost")
    port = args.port or env.get("POSTGRES_PORT", "5432")
    user = args.user or env.get("POSTGRES_USER", "postgres")
    password = args.password or env.get("POSTGRES_PASSWORD", "postgres")
    dbname = args.dbname or env.get("POSTGRES_DB", "urbansense")

    print(f"Connecting to '{dbname}' at {host}:{port} as '{user}'...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        cursor = conn.cursor()

        seed_file = ROOT_DIR / "database" / "seed.sql"
        with open(seed_file, "r", encoding="utf-8") as f:
            seed_sql = f.read()

        cursor.execute(seed_sql)
        conn.commit()

        cursor.execute("SELECT bus_id, registration_number, route_name, status FROM buses;")
        buses = cursor.fetchall()
        print("\n✅ Seed data populated successfully!")
        print("Fleet buses in database:")
        for b in buses:
            badge = "LIVE PROTOTYPE" if b[0] == "BUS-001" else "SIMULATED"
            print(f"  - [{badge}] {b[0]} ({b[1]}): {b[2]} - Status: {b[3]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Failed to seed database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
