from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Boolean, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date as dt_date

from app_paths import app_dir

Base = declarative_base()


class Religion(Base):
    __tablename__ = 'religions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)


class AcademicSession(Base):
    __tablename__ = 'academic_sessions'

    id        = Column(Integer, primary_key=True)
    name      = Column(String(20), unique=True, nullable=False)  # e.g. "2024/2025"
    is_active = Column(Boolean, default=False, nullable=False)


class Department(Base):
    __tablename__ = 'departments'

    id   = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # Science | Art | Commercial
    subjects = relationship("DepartmentSubject", back_populates="department",
                            cascade="all, delete-orphan")


class DepartmentSubject(Base):
    __tablename__ = 'department_subjects'

    id           = Column(Integer, primary_key=True)
    dept_id      = Column(Integer, ForeignKey('departments.id'), nullable=False)
    subject_name = Column(String(100), nullable=False)
    department   = relationship("Department", back_populates="subjects")

    __table_args__ = (UniqueConstraint('dept_id', 'subject_name', name='_dept_subject_uc'),)


class Attendance(Base):
    __tablename__ = 'attendance'

    id         = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    date       = Column(String(50), nullable=False)
    is_present = Column(Boolean, nullable=False, default=True)

    student = relationship("Student", back_populates="attendance_records")

    __table_args__ = (UniqueConstraint('student_id', 'date', name='_student_date_uc'),)


class Fee(Base):
    __tablename__ = 'fees'

    id         = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    term       = Column(Integer, nullable=False)
    amount_due = Column(Float, default=0)
    amount_paid = Column(Float, default=0)

    student = relationship("Student", back_populates="fees")

    __table_args__ = (UniqueConstraint('student_id', 'term', name='_student_term_uc'),)


class FeeStructure(Base):
    __tablename__ = 'fee_structures'

    id          = Column(Integer, primary_key=True)
    class_name  = Column(String(10), nullable=False)
    term        = Column(Integer, nullable=False)
    dept_name   = Column(String(50), nullable=True)  # Science | Art | Commercial
    amount_due  = Column(Float, default=0, nullable=False)
    updated_at  = Column(String(50), nullable=True)
    fee_items   = Column(String, nullable=True)  # JSON string

    __table_args__ = (UniqueConstraint('class_name', 'term', 'dept_name', name='_class_term_dept_fee_uc'),)


class Student(Base):
    __tablename__ = 'students'

    id         = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False)

    # Personal Information
    full_name     = Column(String(200), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age           = Column(Integer, nullable=False)
    sex           = Column(String(10), nullable=False)

    # Contact Information
    home_address = Column(String(500), nullable=False)
    phone_number = Column(String(20), nullable=True)

    # Guardian/Parent Information
    guardian_name    = Column(String(200), nullable=False)
    guardian_phone   = Column(String(20), nullable=False)
    guardian_address = Column(String(500), nullable=False)
    guardian_occupation = Column(String(100), nullable=True)

    # Academic Information
    class_name     = Column(String(10), nullable=False)
    admission_year = Column(Integer, nullable=False)
    state_of_origin = Column(String(100), nullable=False)

    # New FK columns (nullable for backward compat)
    dept_id    = Column(Integer, ForeignKey('departments.id'), nullable=True)
    session_id = Column(Integer, ForeignKey('academic_sessions.id'), nullable=True)

    # V2 Enhancements
    surname = Column(String(100), nullable=True)
    firstname = Column(String(100), nullable=True)
    religion = Column(String(100), nullable=True)
    lga_of_origin = Column(String(100), nullable=True)
    profile_picture_path = Column(String(500), nullable=True)

    # Relationships
    marks             = relationship("Mark", back_populates="student")
    report_cards      = relationship("ReportCard", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", order_by=Attendance.date, back_populates="student")
    fees              = relationship("Fee", back_populates="student")
    department        = relationship("Department")
    academic_session  = relationship("AcademicSession")

    @property
    def name(self):
        """Backward compatibility property."""
        return self.full_name


class Subject(Base):
    __tablename__ = 'subjects'

    id           = Column(Integer, primary_key=True)
    subject_code = Column(String(10), unique=True, nullable=False)
    subject_name = Column(String(50), nullable=False)


class Mark(Base):
    __tablename__ = 'marks'

    id                    = Column(Integer, primary_key=True)
    student_id            = Column(Integer, ForeignKey('students.id'), nullable=False)
    subject_id            = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    term                  = Column(Integer, nullable=False)
    continuous_assessment = Column(Float, default=0)
    exams                 = Column(Float, default=0)
    total                 = Column(Float, default=0)
    grade                 = Column(String(2))

    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject")


class ReportCard(Base):
    __tablename__ = 'report_cards'

    id                  = Column(Integer, primary_key=True)
    student_id          = Column(Integer, ForeignKey('students.id'), nullable=False)
    term                = Column(Integer, nullable=False)
    punctuality         = Column(Integer, nullable=True)
    neatness            = Column(Integer, nullable=True)
    discipline          = Column(Integer, nullable=True)
    teamwork            = Column(Integer, nullable=True)
    teacher_comment     = Column(String(1000), nullable=True)
    principal_comment   = Column(String(1000), nullable=True)
    teacher_signature   = Column(String(200), nullable=True)
    principal_signature = Column(String(200), nullable=True)
    parent_signature    = Column(String(200), nullable=True)
    next_term_resumption_date = Column(String(50), nullable=True)
    created_at          = Column(String(50), nullable=True)
    updated_at          = Column(String(50), nullable=True)

    student = relationship("Student", back_populates="report_cards")

    __table_args__ = (UniqueConstraint('student_id', 'term', name='_student_term_report_uc'),)


class Admin(Base):
    __tablename__ = 'admins'

    id            = Column(Integer, primary_key=True)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at    = Column(String(50), nullable=False)
    is_active     = Column(Boolean, default=True)


# Use SQLite beside the app/exe so data persists across runs.
DB_FILE = app_dir() / "school_management.db"
engine = create_engine(f"sqlite:///{DB_FILE.as_posix()}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def run_migrations():
    """Safely add new columns to existing tables using PRAGMA table_info."""
    with engine.connect() as conn:
        # Check and add dept_id to students
        result = conn.execute(text("PRAGMA table_info(students)"))
        existing_cols = {row[1] for row in result}

        if 'dept_id' not in existing_cols:
            try:
                conn.execute(text("ALTER TABLE students ADD COLUMN dept_id INTEGER REFERENCES departments(id)"))
                conn.commit()
            except Exception:
                pass

        if 'session_id' not in existing_cols:
            try:
                conn.execute(text("ALTER TABLE students ADD COLUMN session_id INTEGER REFERENCES academic_sessions(id)"))
                conn.commit()
            except Exception:
                pass

        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS fee_structures ("
            "id INTEGER PRIMARY KEY, "
            "class_name VARCHAR(10) NOT NULL, "
            "term INTEGER NOT NULL, "
            "amount_due FLOAT NOT NULL DEFAULT 0, "
            "updated_at VARCHAR(50), "
            "fee_items VARCHAR, "
            "UNIQUE(class_name, term))"
        ))
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS report_cards ("
            "id INTEGER PRIMARY KEY, "
            "student_id INTEGER NOT NULL REFERENCES students(id), "
            "term INTEGER NOT NULL, "
            "punctuality INTEGER, "
            "neatness INTEGER, "
            "discipline INTEGER, "
            "teamwork INTEGER, "
            "teacher_comment VARCHAR(1000), "
            "principal_comment VARCHAR(1000), "
            "teacher_signature VARCHAR(200), "
            "principal_signature VARCHAR(200), "
            "parent_signature VARCHAR(200), "
            "created_at VARCHAR(50), "
            "updated_at VARCHAR(50), "
            "UNIQUE(student_id, term))"
        ))

        # Add new columns to students
        if 'guardian_occupation' not in existing_cols:
            try: conn.execute(text("ALTER TABLE students ADD COLUMN guardian_occupation VARCHAR(100)")); conn.commit()
            except Exception: pass
        if 'surname' not in existing_cols:
            try: conn.execute(text("ALTER TABLE students ADD COLUMN surname VARCHAR(100)")); conn.commit()
            except Exception: pass
        if 'firstname' not in existing_cols:
            try: conn.execute(text("ALTER TABLE students ADD COLUMN firstname VARCHAR(100)")); conn.commit()
            except Exception: pass
        if 'religion' not in existing_cols:
            try: conn.execute(text("ALTER TABLE students ADD COLUMN religion VARCHAR(100)")); conn.commit()
            except Exception: pass
        if 'lga_of_origin' not in existing_cols:
            try: conn.execute(text("ALTER TABLE students ADD COLUMN lga_of_origin VARCHAR(100)")); conn.commit()
            except Exception: pass
        if 'profile_picture_path' not in existing_cols:
            try: conn.execute(text("ALTER TABLE students ADD COLUMN profile_picture_path VARCHAR(500)")); conn.commit()
            except Exception: pass

        # Add new columns to fee_structures if table existed before
        result_fees = conn.execute(text("PRAGMA table_info(fee_structures)"))
        fee_cols = {row[1] for row in result_fees}
        if 'fee_items' not in fee_cols:
            try: conn.execute(text("ALTER TABLE fee_structures ADD COLUMN fee_items VARCHAR")); conn.commit()
            except Exception: pass
        if 'dept_name' not in fee_cols:
            try: conn.execute(text("ALTER TABLE fee_structures ADD COLUMN dept_name VARCHAR(50)")); conn.commit()
            except Exception: pass

        # Create religions table
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS religions ("
            "id INTEGER PRIMARY KEY, "
            "name VARCHAR(100) NOT NULL UNIQUE)"
        ))
        
        conn.commit()
