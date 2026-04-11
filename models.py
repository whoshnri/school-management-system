from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Boolean, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date as dt_date

Base = declarative_base()


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

    # Academic Information
    class_name     = Column(String(10), nullable=False)
    admission_year = Column(Integer, nullable=False)
    state_of_origin = Column(String(100), nullable=False)

    # New FK columns (nullable for backward compat)
    dept_id    = Column(Integer, ForeignKey('departments.id'), nullable=True)
    session_id = Column(Integer, ForeignKey('academic_sessions.id'), nullable=True)

    # Relationships
    marks             = relationship("Mark", back_populates="student")
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


class Admin(Base):
    __tablename__ = 'admins'

    id            = Column(Integer, primary_key=True)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at    = Column(String(50), nullable=False)
    is_active     = Column(Boolean, default=True)


# Use SQLite
engine = create_engine('sqlite:///school_management.db')
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
