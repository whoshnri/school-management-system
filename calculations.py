# calculations.py
from sqlalchemy import func
from models import Session, Mark, Student, Subject

class GradeCalculator:
    GRADING_SCALE = {
        'A': (80, 100),
        'B': (70, 79),
        'C': (60, 69),
        'D': (50, 59),
        'F': (0, 49)
    }
    
    @staticmethod
    def calculate_grade(score):
        for grade, (min_score, max_score) in GradeCalculator.GRADING_SCALE.items():
            if min_score <= score <= max_score:
                return grade
        return 'F'
    
    @staticmethod
    def calculate_cumulative_average(student_id, current_term):
        session = Session()
        try:
            if current_term == 1:
                # Term 1: Just return term 1 average
                return GradeCalculator._get_term_average(session, student_id, 1)
            elif current_term == 2:
                # Term 2: Average of term1 and term2
                term1_avg = GradeCalculator._get_term_average(session, student_id, 1)
                term2_avg = GradeCalculator._get_term_average(session, student_id, 2)
                return (term1_avg + term2_avg) / 2
            else:  # term 3
                # Term 3: Average of previous cumulative and term3
                prev_cumulative = GradeCalculator.calculate_cumulative_average(student_id, 2)
                term3_avg = GradeCalculator._get_term_average(session, student_id, 3)
                return (prev_cumulative + term3_avg) / 2
        finally:
            session.close()
    
    @staticmethod
    def _get_term_average(session, student_id, term):
        result = session.query(func.avg(Mark.total)).filter(
            Mark.student_id == student_id,
            Mark.term == term
        ).scalar()
        return result or 0

class PositionCalculator:
    @staticmethod
    def calculate_class_positions(term, class_name):
        session = Session()
        try:
            # Get all students in the class with their averages
            students_data = []
            for student in session.query(Student).filter(Student.class_name == class_name):
                if term == 1:
                    avg = GradeCalculator._get_term_average(session, student.id, 1)
                elif term == 2:
                    avg = GradeCalculator.calculate_cumulative_average(student.id, 2)
                else:  # term 3
                    avg = GradeCalculator.calculate_cumulative_average(student.id, 3)
                
                students_data.append({
                    'student_id': student.id,
                    'name': student.name,
                    'average': avg
                })
            
            # Sort by average (descending) and assign positions
            students_data.sort(key=lambda x: x['average'], reverse=True)
            
            # Handle ties
            positions = {}
            current_position = 1
            for i, student in enumerate(students_data):
                if i > 0 and student['average'] == students_data[i-1]['average']:
                    # Same position as previous student
                    positions[student['student_id']] = current_position
                else:
                    current_position = i + 1
                    positions[student['student_id']] = current_position
            
            return positions
        finally:
            session.close()