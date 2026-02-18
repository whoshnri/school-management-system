"""
Database migration script to update Student table with new fields
"""
from sqlalchemy import create_engine, text
from datetime import date

def migrate_database():
    """Migrate existing database to new schema."""
    engine = create_engine('sqlite:///school_management.db')
    
    print("Starting database migration...")
    
    with engine.connect() as conn:
        # Check if migration is needed
        result = conn.execute(text("PRAGMA table_info(students)"))
        columns = [row[1] for row in result]
        
        if 'full_name' in columns:
            print("✓ Database already migrated!")
            return
        
        print("Migrating database schema...")
        
        # Create new table with updated schema
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS students_new (
                id INTEGER PRIMARY KEY,
                student_id VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(200) NOT NULL,
                date_of_birth DATE NOT NULL,
                age INTEGER NOT NULL,
                sex VARCHAR(10) NOT NULL,
                home_address VARCHAR(500) NOT NULL,
                phone_number VARCHAR(20),
                guardian_name VARCHAR(200) NOT NULL,
                guardian_phone VARCHAR(20) NOT NULL,
                guardian_address VARCHAR(500) NOT NULL,
                class_name VARCHAR(10) NOT NULL,
                admission_year INTEGER NOT NULL,
                state_of_origin VARCHAR(100) NOT NULL
            )
        """))
        
        # Migrate existing data with default values
        conn.execute(text("""
            INSERT INTO students_new (
                id, student_id, full_name, date_of_birth, age, sex,
                home_address, phone_number, guardian_name, guardian_phone,
                guardian_address, class_name, admission_year, state_of_origin
            )
            SELECT 
                id, 
                student_id, 
                name as full_name,
                '2010-01-01' as date_of_birth,
                14 as age,
                'Male' as sex,
                'Not provided' as home_address,
                NULL as phone_number,
                'Not provided' as guardian_name,
                '00000000000' as guardian_phone,
                'Not provided' as guardian_address,
                class_name,
                2024 as admission_year,
                'Lagos' as state_of_origin
            FROM students
        """))
        
        # Drop old table
        conn.execute(text("DROP TABLE students"))
        
        # Rename new table
        conn.execute(text("ALTER TABLE students_new RENAME TO students"))
        
        conn.commit()
        
        print("✓ Database migration completed successfully!")
        print("⚠ Note: Existing students have default values for new fields.")
        print("   Please update their records with actual information.")

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        print("Please backup your database and try again.")
