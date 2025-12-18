from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Attendance(Base):
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    date = Column(String(50), nullable=False)
    is_present = Column(Boolean, nullable=False, default=True)

    student = relationship("Student", back_populates="attendance_records")
    
    # Ensures a student has only one record per date
    __table_args__ = (UniqueConstraint('student_id', 'date', name='_student_date_uc'),)

class Fee(Base):
    __tablename__ = 'fees'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    term = Column(Integer, nullable=False)
    amount_due = Column(Float, default=0)
    amount_paid = Column(Float, default=0)

    student = relationship("Student", back_populates="fees")

    __table_args__ = (UniqueConstraint('student_id', 'term', name='_student_term_uc'),)


class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    class_name = Column(String(10), nullable=False)
    marks = relationship("Mark", back_populates="student")
    attendance_records = relationship("Attendance", order_by=Attendance.date, back_populates="student")
    fees = relationship("Fee", back_populates="student")

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    subject_code = Column(String(10), unique=True, nullable=False)
    subject_name = Column(String(50), nullable=False)

class Mark(Base):
    __tablename__ = 'marks'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    term = Column(Integer, nullable=False)
    continuous_assessment = Column(Float, default=0)
    exams = Column(Float, default=0)
    total = Column(Float, default=0)
    grade = Column(String(2))
    
    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject")

# Use SQLite for now (easier setup) - change to PostgreSQL later
engine = create_engine('sqlite:///school_management.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)