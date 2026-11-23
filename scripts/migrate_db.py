import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import create_tables, create_tables_for_year

print("Migrando DB atual...")
create_tables()

print("Migrando DB 2025...")
create_tables_for_year(2025)

print("Migrando DB 2026...")
create_tables_for_year(2026)

print("Migracao concluida!")
