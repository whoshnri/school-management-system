import os
import random
from datetime import date
from models import (
    Session, Student, Department, AcademicSession, FeeStructure, Fee,
    Mark, Attendance, Admin, Subject
)

def create_seed_data():
    session = Session()
    try:
        # Create Departments
        depts = {}
        for d in ["Science", "Art", "Commercial"]:
            dept = session.query(Department).filter_by(name=d).first()
            if not dept:
                dept = Department(name=d)
                session.add(dept)
            depts[d] = dept
        
        # Create Academic Session
        acad_session = session.query(AcademicSession).filter_by(name="2024/2025").first()
        if not acad_session:
            acad_session = AcademicSession(name="2024/2025", is_active=True)
            session.add(acad_session)
            
        # Define Subjects per Department
        dept_subjects_map = {
            "Science": ["Mathematics", "English Language", "Civic Education", "Economics", "Physics", "Chemistry", "Biology", "Further Mathematics", "Technical Drawing"],
            "Art": ["Mathematics", "English Language", "Civic Education", "Economics", "Literature", "Government", "CRK/IRK", "History", "Fine Art"],
            "Commercial": ["Mathematics", "English Language", "Civic Education", "Economics", "Accounting", "Commerce", "Business Studies", "Office Practice", "Insurance"]
        }
        
        all_subjects = set(sum(dept_subjects_map.values(), []))
        subjects_map = {}
        for sname in all_subjects:
            subj = session.query(Subject).filter_by(subject_name=sname).first()
            if not subj:
                code = sname[:3].upper()
                subj = Subject(subject_name=sname, subject_code=code)
                session.add(subj)
            subjects_map[sname] = subj
            
        session.commit()
        
        from models import DepartmentSubject
        for d_name, snames in dept_subjects_map.items():
            dept = depts[d_name]
            for sname in snames:
                ds = session.query(DepartmentSubject).filter_by(dept_id=dept.id, subject_name=sname).first()
                if not ds:
                    ds = DepartmentSubject(dept_id=dept.id, subject_name=sname)
                    session.add(ds)
        session.commit()

        classes = ["SSS1", "SSS2", "SSS3"]
        terms = [1, 2, 3]

        # Seed Fee Structures
        print("Seeding fee structures...")
        fee_items_pool = [
            {"description": "Tuition", "amount": 20000},
            {"description": "Development Levy", "amount": 5000},
            {"description": "PTA", "amount": 2000},
            {"description": "Medical", "amount": 1500},
            {"description": "Sports", "amount": 1000},
            {"description": "Library", "amount": 1500}
        ]
        
        for c in classes:
            for t in terms:
                for d_name in depts.keys():
                    existing_fs = session.query(FeeStructure).filter_by(
                        class_name=c, term=t, dept_name=d_name
                    ).first()
                    
                    if not existing_fs:
                        import json
                        from datetime import datetime
                        selected = random.sample(fee_items_pool, k=random.randint(3, 6))
                        if c == "SSS3":
                            selected[0]["amount"] = 30000
                            
                        total_amt = sum(item["amount"] for item in selected)
                            
                        fs = FeeStructure(
                            class_name=c,
                            term=t,
                            dept_name=d_name,
                            amount_due=total_amt,
                            fee_items=json.dumps(selected),
                            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        session.add(fs)
        
        session.commit()

        print("Seeding students...")
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank"]
        surnames = ["Smith", "Doe", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Rodriguez"]
        religions = ["Christianity", "Islam", "Other"]
        states = ["Lagos", "Ogun", "Oyo", "Osun", "Kano", "Kaduna"]

        student_counter = 1

        for c in classes:
            for d_name, dept in depts.items():
                for i in range(3):
                    dept_code = d_name[:2].upper()
                    student_id = f"GFA/2024/S/{dept_code}/{student_counter:04d}"
                    
                    student = session.query(Student).filter_by(student_id=student_id).first()
                    if not student:
                        fname = random.choice(first_names)
                        sname = random.choice(surnames)
                        student = Student(
                            student_id=student_id,
                            surname=sname,
                            other_names=fname,
                            firstname=fname,
                            full_name=f"{sname} {fname}",
                            date_of_birth=date(2008 - classes.index(c), random.randint(1, 12), random.randint(1, 28)),
                            age=2024 - (2008 - classes.index(c)),
                            sex=random.choice(["Male", "Female"]),
                            home_address=f"{random.randint(1, 99)} Seed Street, Seed City",
                            guardian_name=f"Mr/Mrs {sname}",
                            guardian_phone=f"080{random.randint(10000000, 99999999)}",
                            guardian_address=f"{random.randint(1, 99)} Seed Street, Seed City",
                            guardian_occupation="Engineer" if random.random() > 0.5 else "Teacher",
                            class_name=c,
                            admission_year=2024,
                            state_of_origin=random.choice(states),
                            religion=random.choice(religions),
                            dept_id=dept.id,
                            session_id=acad_session.id
                        )
                        session.add(student)
                        session.commit() 

                    # Seed Fees
                    for t in terms:
                        fs = session.query(FeeStructure).filter_by(class_name=c, term=t, dept_name=d_name).first()
                        if fs:
                            fee = session.query(Fee).filter_by(student_id=student.id, term=t).first()
                            if not fee:
                                total_amt = fs.amount_due
                                paid = total_amt if random.random() > 0.3 else total_amt * 0.5
                                fee = Fee(
                                    student_id=student.id,
                                    term=t,
                                    amount_due=total_amt,
                                    amount_paid=paid
                                )
                                session.add(fee)
                    
                    # Seed Marks
                    subjs = dept_subjects_map[d_name]
                    
                    for t in terms:
                        for sname in subjs:
                            subj_id = subjects_map[sname].id
                            mark = session.query(Mark).filter_by(student_id=student.id, term=t, subject_id=subj_id).first()
                            if not mark:
                                mark = Mark(
                                    student_id=student.id,
                                    term=t,
                                    subject_id=subj_id,
                                    continuous_assessment=random.randint(10, 40),
                                    exams=random.randint(20, 60),
                                )
                                session.add(mark)
                    
                    # Seed Attendance
                    for t in terms:
                        start_month = (t - 1) * 3 + 1
                        for day in range(1, 10):
                            att_date_str = date(2024, start_month, day).isoformat()
                            att = session.query(Attendance).filter_by(student_id=student.id, date=att_date_str).first()
                            if not att:
                                att = Attendance(
                                    student_id=student.id,
                                    date=att_date_str,
                                    is_present=random.random() > 0.2
                                )
                                session.add(att)

                    student_counter += 1

        session.commit()
        print(f"Successfully seeded database with {student_counter - 1} students, fee structures, marks, and attendance!")

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_seed_data()
