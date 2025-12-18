import tkinter as tk
from forms import SchoolManagementApp
from models import Session, Subject, Attendance

def initialize_subjects():
    """Pre-populate the 20 subjects"""
    session = Session()
    
    if session.query(Subject).count() == 0:
        subjects_data = [
            ("MATH", "Mathematics"), ("ENG", "English"), ("PHY", "Physics"),
            ("CHEM", "Chemistry"), ("BIO", "Biology"), ("HIST", "History"),
            ("GEO", "Geography"), ("COMM", "Commerce"), ("ACC", "Accounts"),
            ("AGRIC", "Agricultural Science"), ("LIT", "Literature"),
            ("FRENCH", "French"), ("ARABIC", "Arabic"), ("IRS", "Islamic Studies"),
            ("CRK", "Christian Knowledge"), ("CIVIC", "Civic Education"),
            ("COMP", "Computer Science"), ("FOOD", "Food & Nutrition"),
            ("ART", "Fine Arts"), ("MUSIC", "Music")
        ]
        
        for code, name in subjects_data:
            subject = Subject(subject_code=code, subject_name=name)
            session.add(subject)
        
        session.commit()
        print("20 subjects initialized successfully!")
    session.close()

if __name__ == "__main__":
    # Initialize database with subjects
    initialize_subjects()
    
    # Start the application
    import customtkinter as ctk
    
    # Set theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    root = ctk.CTk()
    # Set initial window size
    root.geometry("1100x800")
    
    app = SchoolManagementApp(root)
    root.mainloop()