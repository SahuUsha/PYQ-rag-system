import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit(1)

engine = create_engine(DATABASE_URL)

migration_sql = "ALTER TABLE questions ALTER COLUMN marks TYPE VARCHAR(255) USING marks::varchar;"

try:
    with engine.connect() as conn:
        conn.execute(text(migration_sql))
        conn.commit()
    print("Migration successful: marks column type changed to VARCHAR")
except Exception as e:
    print(f"Migration failed: {e}")
