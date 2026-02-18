import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from sqlalchemy.exc import IntegrityError
from models import Session, Student, Subject, Mark, Attendance
from calculations import GradeCalculator
from datetime import date as dt_date
import csv
from ui_components import TextLabelManager
from tkcalendar import DateEntry

# Modern color palette (matching enterprise_forms.py)
COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "secondary": "#5f6368",
    "success": "#34a853",
    "warning": "#fbbc04",
    "danger": "#ea4335",
    "bg_dark": "#1e1e2e",
    "bg_card": "#2a2a3e",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "border": "#3a3a4e"
}


class StudentRegistrationTab(ctk.CTkFrame):
    def __init__(self, parent, session, on_student_added_callback):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.on_student_added_callback = on_student_added_callback
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text=TextLabelManager.get_header_text('student_registration'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(padx=20, pady=15, anchor="w")

        # Form Card
        form_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        form_card.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        form_card.grid_columnconfigure(0, weight=1)
        form_card.grid_columnconfigure(1, weight=2)

        # Instructions
        ctk.CTkLabel(
            form_card,
            text="Fill in the details below to register a new student",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, columnspan=2, padx=25, pady=(20, 15), sticky="w")

        # Student ID (numeric only)
        ctk.CTkLabel(
            form_card,
            text="Student ID *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=1, column=0, padx=25, pady=(15, 5), sticky="e")
        
        self.id_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="e.g. S001, STU2024001",
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.id_entry.grid(row=1, column=1, padx=25, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            form_card,
            text="Unique identifier for the student",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"]
        ).grid(row=2, column=1, padx=25, pady=(0, 10), sticky="w")

        # Full Name
        ctk.CTkLabel(
            form_card,
            text="Full Name *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=3, column=0, padx=25, pady=(15, 5), sticky="e")

        self.name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="e.g. John Doe",
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.name_entry.grid(row=3, column=1, padx=25, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            form_card,
            text="Student's full legal name",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"]
        ).grid(row=4, column=1, padx=25, pady=(0, 10), sticky="w")

        # Class
        ctk.CTkLabel(
            form_card,
            text="Class *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=5, column=0, padx=25, pady=(15, 5), sticky="e")

        self.class_entry = ctk.CTkComboBox(
            form_card,
            values=["SSS1", "SSS2", "SSS3"],
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.class_entry.grid(row=5, column=1, padx=25, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            form_card,
            text="Select the student's class level",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"]
        ).grid(row=6, column=1, padx=25, pady=(0, 10), sticky="w")

        # Submit Button
        self.add_btn = ctk.CTkButton(
            form_card,
            text=TextLabelManager.get_button_text('register'),
            command=self.add_student,
            width=220,
            height=50,
            corner_radius=10,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.add_btn.grid(row=7, column=0, columnspan=2, pady=40)

        # Status message
        self.status_label = ctk.CTkLabel(
            form_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["success"]
        )
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(0, 20))

    def add_student(self):
        s_id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()

        # Validation
        if not s_id:
            self.show_error("Student ID is required")
            self.id_entry.focus()
            return

        if not name:
            self.show_error("Full Name is required")
            self.name_entry.focus()
            return

        if len(name) < 2:
            self.show_error("Please enter a valid name")
            self.name_entry.focus()
            return

        try:
            new_student = Student(student_id=s_id, name=name, class_name=class_name)
            self.session.add(new_student)
            self.session.commit()

            self.show_success(f"Student '{name}' registered successfully!")

            # Clear fields
            self.id_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
            self.id_entry.focus()

            if self.on_student_added_callback:
                self.on_student_added_callback()

        except IntegrityError:
            self.session.rollback()
            self.show_error(f"Student ID '{s_id}' already exists")
        except Exception as e:
            self.session.rollback()
            self.show_error(f"Failed to add student: {str(e)}")

    def show_error(self, message):
        self.status_label.configure(text=f"Error: {message}", text_color=COLORS["danger"])

    def show_success(self, message):
        self.status_label.configure(text=message, text_color=COLORS["success"])


class MarksEntryTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.active_students = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_subjects()
        self.load_students()

    def setup_ui(self):
        # Header with controls
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text=TextLabelManager.get_header_text('marks_entry'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)
        
        # Subject count display
        self.subject_count_label = ctk.CTkLabel(
            header_frame,
            text="(20 subjects)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.subject_count_label.pack(side="left", padx=(0, 10), pady=15)

        # Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)

        ctk.CTkLabel(
            controls_frame,
            text="Student:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        self.student_var = ctk.StringVar(value="")
        self.student_combo = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.student_var,
            width=300,
            height=40,
            corner_radius=8,
            fg_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=self.on_student_change
        )
        self.student_combo.pack(side="left", padx=8)

        ctk.CTkLabel(
            controls_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(20, 8))

        self.term_var = ctk.StringVar(value="1")
        self.term_combo = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.term_var,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=150,
            height=40,
            corner_radius=8,
            fg_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=self.on_term_change
        )
        self.term_combo.pack(side="left", padx=8)

        ctk.CTkButton(
            controls_frame,
            text=TextLabelManager.get_button_text('load') + " Marks",
            command=self.load_existing_marks,
            width=110,
            height=40,
            corner_radius=8,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(side="left", padx=(20, 0))

        # Marks Grid
        self.marks_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        self.marks_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # Headers
        headers = ["Subject", "CA (30)", "Exam (70)", "Total", "Grade"]
        col_widths = [200, 100, 100, 80, 80]
        self.marks_frame.grid_columnconfigure(0, weight=2, minsize=200)
        for i in range(1, 5):
            self.marks_frame.grid_columnconfigure(i, weight=1, minsize=80)

        for col, h in enumerate(headers):
            ctk.CTkLabel(
                self.marks_frame,
                text=h,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=col, padx=15, pady=15, sticky="w")

        # Footer - Save Button
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, pady=15)

        self.save_btn = ctk.CTkButton(
            footer_frame,
            text=TextLabelManager.get_button_text('save') + " All Marks",
            command=self.save_marks,
            width=200,
            height=50,
            corner_radius=10,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.save_btn.pack(side="left", padx=10)

        # Clear button
        ctk.CTkButton(
            footer_frame,
            text=TextLabelManager.get_button_text('clear'),
            command=self.clear_all_marks,
            width=120,
            height=50,
            corner_radius=10,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["danger"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left", padx=10)

    def increment_mark(self, var, max_value):
        """Increment mark value with validation."""
        try:
            current = int(var.get() or 0)
            if current < max_value:
                var.set(str(current + 1))
        except ValueError:
            var.set("1")
    
    def decrement_mark(self, var, min_value):
        """Decrement mark value with validation."""
        try:
            current = int(var.get() or 0)
            if current > min_value:
                var.set(str(current - 1))
        except ValueError:
            var.set(str(min_value))

    def validate_mark_input(self, var, max_value):
        """Validate mark input to ensure it's within range."""
        try:
            value = var.get().strip()
            if value == "":
                return True  # Allow empty
            
            mark = float(value)
            if mark < 0:
                var.set("0")
            elif mark > max_value:
                var.set(str(max_value))
            return True
        except ValueError:
            # Remove invalid characters
            valid_chars = ''.join(c for c in var.get() if c.isdigit() or c == '.')
            var.set(valid_chars)
            return False

    def on_student_change(self, value):
        self.load_existing_marks()

    def on_term_change(self, value):
        self.load_existing_marks()

    def load_students(self):
        students = self.session.query(Student).order_by(Student.full_name).all()
        self.active_students = students
        if students:
            student_list = [f"{s.student_id} - {s.name}" for s in students]
            self.student_combo.configure(values=student_list)
            current = self.student_var.get()
            if current not in student_list:
                self.student_var.set(student_list[0])
        else:
            self.student_combo.configure(values=["No Students"])
            self.student_var.set("No Students")

    def load_subjects(self):
        self.subjects = self.session.query(Subject).all()
        self.entries = {}
        
        # Update subject count display
        if hasattr(self, 'subject_count_label'):
            self.subject_count_label.configure(text=f"({len(self.subjects)} subjects)")

        for i, sub in enumerate(self.subjects, 1):
            ctk.CTkLabel(
                self.marks_frame,
                text=sub.subject_name,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"]
            ).grid(row=i, column=0, sticky="ew", padx=15, pady=10)

            ca_var = tk.StringVar(value="30")  # Default to max value
            ca_frame = ctk.CTkFrame(self.marks_frame, fg_color="transparent")
            ca_frame.grid(row=i, column=1, padx=10, pady=10)
            
            ca_entry = ctk.CTkEntry(
                ca_frame,
                textvariable=ca_var,
                width=60,
                height=40,
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
                justify="center",
                validatecommand=(self.register(lambda char: char.isdigit() or char == ""), "%S")
            )
            ca_entry.pack(side="left", padx=2)
            
            # Add validation for CA (0-30)
            ca_var.trace_add('write', lambda *args, v=ca_var: self.validate_mark_input(v, 30))
            
            # CA increment/decrement buttons
            ca_btn_frame = ctk.CTkFrame(ca_frame, fg_color="transparent")
            ca_btn_frame.pack(side="left", padx=2)
            
            ctk.CTkButton(
                ca_btn_frame,
                text="▲",
                width=20,
                height=18,
                corner_radius=4,
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                font=ctk.CTkFont(size=10),
                command=lambda v=ca_var: self.increment_mark(v, 30)
            ).pack(pady=1)
            
            ctk.CTkButton(
                ca_btn_frame,
                text="▼",
                width=20,
                height=18,
                corner_radius=4,
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                font=ctk.CTkFont(size=10),
                command=lambda v=ca_var: self.decrement_mark(v, 0)
            ).pack(pady=1)

            exam_var = tk.StringVar(value="70")  # Default to max value
            exam_frame = ctk.CTkFrame(self.marks_frame, fg_color="transparent")
            exam_frame.grid(row=i, column=2, padx=10, pady=10)
            
            exam_entry = ctk.CTkEntry(
                exam_frame,
                textvariable=exam_var,
                width=60,
                height=40,
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
                justify="center"
            )
            exam_entry.pack(side="left", padx=2)
            
            # Add validation for Exam (0-70)
            exam_var.trace_add('write', lambda *args, v=exam_var: self.validate_mark_input(v, 70))
            
            # Exam increment/decrement buttons
            exam_btn_frame = ctk.CTkFrame(exam_frame, fg_color="transparent")
            exam_btn_frame.pack(side="left", padx=2)
            
            ctk.CTkButton(
                exam_btn_frame,
                text="▲",
                width=20,
                height=18,
                corner_radius=4,
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                font=ctk.CTkFont(size=10),
                command=lambda v=exam_var: self.increment_mark(v, 70)
            ).pack(pady=1)
            
            ctk.CTkButton(
                exam_btn_frame,
                text="▼",
                width=20,
                height=18,
                corner_radius=4,
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                font=ctk.CTkFont(size=10),
                command=lambda v=exam_var: self.decrement_mark(v, 0)
            ).pack(pady=1)

            total_lbl = ctk.CTkLabel(
                self.marks_frame,
                text="0",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=COLORS["text_primary"],
                width=60
            )
            total_lbl.grid(row=i, column=3, padx=10, pady=10)

            grade_lbl = ctk.CTkLabel(
                self.marks_frame,
                text="-",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=60
            )
            grade_lbl.grid(row=i, column=4, padx=10, pady=10)

            self.entries[sub.id] = {
                'ca': ca_var, 'exam': exam_var,
                'total': total_lbl, 'grade': grade_lbl
            }

            ca_var.trace_add('write', lambda *args, s=sub: self.recalc(s.id))
            exam_var.trace_add('write', lambda *args, s=sub: self.recalc(s.id))

    def load_existing_marks(self):
        """Load existing marks for the selected student and term"""
        student_str = self.student_var.get()
        if not student_str or student_str == "No Students":
            return

        try:
            student_id_str = student_str.split(' - ')[0]
            student = self.session.query(Student).filter_by(student_id=student_id_str).first()
            if not student:
                return

            term_value = self.term_var.get()
            term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)

            for sub in self.subjects:
                widgets = self.entries[sub.id]
                mark = self.session.query(Mark).filter_by(
                    student_id=student.id, subject_id=sub.id, term=term
                ).first()

                if mark:
                    widgets['ca'].set(str(int(mark.continuous_assessment)) if mark.continuous_assessment else "")
                    widgets['exam'].set(str(int(mark.exams)) if mark.exams else "")
                else:
                    widgets['ca'].set("")
                    widgets['exam'].set("")

        except Exception as e:
            print(f"Error loading marks: {e}")

    def clear_all_marks(self):
        for sub in self.subjects:
            widgets = self.entries[sub.id]
            widgets['ca'].set("")
            widgets['exam'].set("")

    def recalc(self, subject_id):
        widgets = self.entries[subject_id]
        try:
            ca_str = widgets['ca'].get().strip()
            exam_str = widgets['exam'].get().strip()

            ca = float(ca_str) if ca_str else 0
            exam = float(exam_str) if exam_str else 0

            # Validation
            if ca > 30:
                ca = 30
            if exam > 70:
                exam = 70
            if ca < 0:
                ca = 0
            if exam < 0:
                exam = 0

            total = ca + exam

            widgets['total'].configure(text=f"{total:.0f}")
            grade = GradeCalculator.calculate_grade(total)

            grade_color = COLORS["success"] if grade in ['A', 'B'] else (COLORS["warning"] if grade in ['C', 'D'] else COLORS["danger"])
            widgets['grade'].configure(text=grade, text_color=grade_color)
        except ValueError:
            widgets['total'].configure(text="0")
            widgets['grade'].configure(text="-", text_color=COLORS["text_secondary"])

    def save_marks(self):
        student_str = self.student_var.get()
        if not student_str or student_str == "No Students":
            messagebox.showwarning("No Student", "Please select a student first.")
            return

        try:
            student_id_str = student_str.split(' - ')[0]
            student = self.session.query(Student).filter_by(student_id=student_id_str).first()
            if not student:
                return

            term_value = self.term_var.get()
            term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)
            saved_count = 0

            for sub in self.subjects:
                widgets = self.entries[sub.id]
                try:
                    ca = float(widgets['ca'].get() or 0)
                    ca = min(max(ca, 0), 30)  # Clamp 0-30
                except ValueError:
                    ca = 0.0

                try:
                    exam = float(widgets['exam'].get() or 0)
                    exam = min(max(exam, 0), 70)  # Clamp 0-70
                except ValueError:
                    exam = 0.0

                total = ca + exam
                grade = GradeCalculator.calculate_grade(total)

                mark = self.session.query(Mark).filter_by(student_id=student.id, subject_id=sub.id, term=term).first()
                if mark:
                    mark.continuous_assessment = ca
                    mark.exams = exam
                    mark.total = total
                    mark.grade = grade
                else:
                    self.session.add(Mark(student_id=student.id, subject_id=sub.id, term=term,
                                          continuous_assessment=ca, exams=exam, total=total, grade=grade))
                saved_count += 1

            self.session.commit()
            messagebox.showinfo("Saved", f"Success: {saved_count} marks saved for {student.name} (Term {term})")

        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", str(e))


class BroadsheetTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.broadsheet_data = None
        self.students = []
        self.subjects = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Header with controls
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))

        ctk.CTkLabel(
            header_frame,
            text=TextLabelManager.get_header_text('broadsheet'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        # Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)

        ctk.CTkLabel(
            controls_frame,
            text="Class:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        class_values = [f"{cls} ({self.get_class_population(cls)})" for cls in ["SSS1", "SSS2", "SSS3"]]
        self.class_filter_raw = ctk.CTkComboBox(
            controls_frame,
            values=class_values,
            width=130,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.class_filter_raw.pack(side="left", padx=5)

        ctk.CTkLabel(
            controls_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(20, 8))

        self.term_filter = ctk.CTkOptionMenu(
            controls_frame,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=150,
            height=40,
            corner_radius=8,
            fg_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.term_filter.pack(side="left", padx=5)

        ctk.CTkButton(
            controls_frame,
            text=TextLabelManager.get_button_text('load'),
            command=self.load_sheet,
            width=90,
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(20, 8))

        self.export_btn = ctk.CTkButton(
            controls_frame,
            text=TextLabelManager.get_button_text('export') + " CSV",
            command=self.export_to_csv,
            state="disabled",
            width=120,
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.export_btn.pack(side="left", padx=5)
        
        # Import button
        self.import_btn = ctk.CTkButton(
            controls_frame,
            text="Import CSV",
            command=self.import_from_csv,
            width=100,
            height=40,
            corner_radius=8,
            fg_color=COLORS["warning"],
            hover_color="#e0a800",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.import_btn.pack(side="left", padx=5)

        # Broadsheet Grid
        self.sheet_frame = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        self.sheet_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    def get_class_population(self, class_name):
        return self.session.query(Student).filter_by(class_name=class_name).count()

    def load_sheet(self):
        for widget in self.sheet_frame.winfo_children():
            widget.destroy()

        class_name_full = self.class_filter_raw.get()
        class_name = class_name_full.split(' ')[0] if class_name_full else ""
        term_value = self.term_filter.get()
        term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)

        if not class_name:
            messagebox.showwarning("Selection Error", "Please select a class.")
            return

        self.students = self.session.query(Student).filter_by(class_name=class_name).order_by(Student.full_name).all()
        self.subjects = self.session.query(Subject).all()

        # Empty state
        if not self.students:
            empty_frame = ctk.CTkFrame(self.sheet_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, pady=60, padx=100)
            
            ctk.CTkLabel(
                empty_frame,
                text="No Data",
                font=ctk.CTkFont(size=48)
            ).pack(pady=(0, 10))
            
            ctk.CTkLabel(
                empty_frame,
                text=f"No students in {class_name}",
                font=ctk.CTkFont(family="Segoe UI", size=16),
                text_color=COLORS["text_secondary"]
            ).pack()
            
            self.export_btn.configure(state="disabled")
            return

        marks = self.session.query(Mark).filter(
            Mark.term == term,
            Mark.student.has(class_name=class_name)
        ).all()

        data_map = {s.id: {} for s in self.students}
        for m in marks:
            if m.student_id in data_map:
                data_map[m.student_id][m.subject_id] = m.total

        self.broadsheet_data = data_map
        self.export_btn.configure(state="normal")

        # Headers
        headers = ["#", "Student ID", "Name"] + [s.subject_code for s in self.subjects] + ["Total", "Avg", "Pos"]
        for c, h in enumerate(headers):
            ctk.CTkLabel(
                self.sheet_frame,
                text=h,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=70 if c > 2 else (40 if c == 0 else 100)
            ).grid(row=0, column=c, padx=6, pady=12, sticky="w")

        # Calculate totals and positions
        student_totals = []
        for student in self.students:
            scores = [data_map[student.id].get(sub.id, 0) or 0 for sub in self.subjects]
            total = sum(scores)
            avg = total / len(self.subjects) if self.subjects else 0
            student_totals.append((student, total, avg))

        # Sort by total for position
        student_totals.sort(key=lambda x: x[1], reverse=True)
        positions = {st[0].id: pos + 1 for pos, st in enumerate(student_totals)}

        # Student Rows (in original order)
        for r, student in enumerate(self.students, 1):
            ctk.CTkLabel(
                self.sheet_frame,
                text=str(r),
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                width=40
            ).grid(row=r, column=0, padx=6, pady=8)

            ctk.CTkLabel(
                self.sheet_frame,
                text=student.student_id,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_primary"]
            ).grid(row=r, column=1, padx=6, pady=8, sticky="w")

            ctk.CTkLabel(
                self.sheet_frame,
                text=student.name,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_primary"]
            ).grid(row=r, column=2, padx=6, pady=8, sticky="w")

            scores = []
            for c, sub in enumerate(self.subjects, 3):
                score = data_map[student.id].get(sub.id, "-")
                if isinstance(score, (int, float)):
                    scores.append(score)
                    score_text = f"{score:.0f}"
                    score_color = COLORS["success"] if score >= 50 else (COLORS["warning"] if score >= 40 else COLORS["danger"])
                else:
                    score_text = "-"
                    score_color = COLORS["text_secondary"]

                ctk.CTkLabel(
                    self.sheet_frame,
                    text=score_text,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=score_color
                ).grid(row=r, column=c, padx=6, pady=8)

            # Total, Average, Position
            total = sum(scores)
            avg = total / len(self.subjects) if self.subjects else 0
            pos = positions[student.id]

            ctk.CTkLabel(
                self.sheet_frame,
                text=f"{total:.0f}",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS["text_primary"]
            ).grid(row=r, column=len(self.subjects) + 3, padx=6, pady=8)

            ctk.CTkLabel(
                self.sheet_frame,
                text=f"{avg:.1f}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["primary"]
            ).grid(row=r, column=len(self.subjects) + 4, padx=6, pady=8)

            pos_color = COLORS["success"] if pos <= 3 else COLORS["text_primary"]
            ctk.CTkLabel(
                self.sheet_frame,
                text=f"{pos}",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=pos_color
            ).grid(row=r, column=len(self.subjects) + 5, padx=6, pady=8)

    def export_to_csv(self):
        if not self.broadsheet_data or not self.students or not self.subjects:
            messagebox.showwarning("No Data", "Load a broadsheet before exporting.")
            return

        class_name = self.class_filter_raw.get().split(' ')[0]
        term = self.term_filter.get()

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"Broadsheet_{class_name}_Term{term}_{dt_date.today()}.csv"
        )

        if not filename:
            return

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                header = ["#", "Student ID", "Name"] + [s.subject_code for s in self.subjects] + ["Total", "Average"]
                writer.writerow(header)

                for idx, student in enumerate(self.students, 1):
                    scores = []
                    row_data = [idx, student.student_id, student.name]
                    for sub in self.subjects:
                        score = self.broadsheet_data[student.id].get(sub.id, "-")
                        if isinstance(score, (int, float)):
                            scores.append(score)
                            score_text = f"{score:.0f}"
                        else:
                            score_text = "-"
                        row_data.append(score_text)

                    total = sum(scores)
                    avg = total / len(self.subjects) if self.subjects else 0
                    row_data.extend([f"{total:.0f}", f"{avg:.1f}"])
                    writer.writerow(row_data)

            messagebox.showinfo("Export Success", f"Success: Broadsheet exported to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during CSV export: {str(e)}")

    def import_from_csv(self):
        """Import grades from a CSV file."""
        filename = filedialog.askopenfilename(
            title="Select CSV file to import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # Load subjects for mapping
            subjects = self.session.query(Subject).all()
            subject_map = {s.subject_code: s for s in subjects}
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header row
                
                # Find subject columns based on header
                subject_cols = {}
                for i, col in enumerate(header):
                    if col in subject_map:
                        subject_cols[i] = subject_map[col]
                
                # Get term from filter
                term_value = self.term_filter.get()
                term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)
                
                for row in reader:
                    if len(row) < 3:
                        continue
                    
                    try:
                        student_id = row[1]  # Column 1 is Student ID
                        
                        # Find student
                        student = self.session.query(Student).filter_by(student_id=student_id).first()
                        if not student:
                            skipped_count += 1
                            continue
                        
                        # Import grades for each subject
                        for col_idx, subject in subject_cols.items():
                            if col_idx < len(row):
                                score_str = row[col_idx]
                                if score_str and score_str != "-":
                                    try:
                                        total = float(score_str)
                                        
                                        # Find or create mark record
                                        mark = self.session.query(Mark).filter_by(
                                            student_id=student.id,
                                            subject_id=subject.id,
                                            term=term
                                        ).first()
                                        
                                        if mark:
                                            mark.total = total
                                            # Calculate grade
                                            mark.grade = GradeCalculator.calculate_grade(total)
                                        else:
                                            new_mark = Mark(
                                                student_id=student.id,
                                                subject_id=subject.id,
                                                term=term,
                                                continuous_assessment=0,
                                                exams=total,
                                                total=total,
                                                grade=GradeCalculator.calculate_grade(total)
                                            )
                                            self.session.add(new_mark)
                                        
                                        imported_count += 1
                                    except ValueError:
                                        pass
                        
                    except Exception as row_error:
                        errors.append(str(row_error))
                
            self.session.commit()
            
            result_msg = f"Import Complete!\n\n"
            result_msg += f"Grades imported: {imported_count}\n"
            result_msg += f"Students skipped: {skipped_count}"
            if errors:
                result_msg += f"\nErrors: {len(errors)}"
            
            messagebox.showinfo("Import Success", result_msg)
            
            # Reload the broadsheet to show updated data
            if self.students:
                self.load_sheet()
                
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Import Error", f"Failed to import CSV: {str(e)}")


class AttendanceTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.current_class = None
        self.current_date = None
        self.students = []
        self.attendance_vars = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))

        ctk.CTkLabel(
            header_frame,
            text=TextLabelManager.get_header_text('attendance'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        # Step-by-step controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)

        # Step 1: Class Selection - Always show all 6 classes
        ctk.CTkLabel(
            controls_frame,
            text="1. Select Class:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 8))

        # Always show all classes regardless of student enrollment
        class_values = ["SSS1", "SSS2", "SSS3"]

        self.class_var = ctk.StringVar()
        self.class_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.class_var,
            values=class_values,
            width=100,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=self.on_class_selected
        )
        self.class_combo.pack(side="left", padx=5)

        # Step 2: Date Selection
        ctk.CTkLabel(
            controls_frame,
            text="2. Select Date:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(20, 8))

        self.date_picker = DateEntry(
            controls_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 10)
        )
        self.date_picker.pack(side="left", padx=5)
        self.date_picker.bind("<<DateEntrySelected>>", self.on_date_selected)

        # Step 3: Load Button
        self.load_btn = ctk.CTkButton(
            controls_frame,
            text="3. " + TextLabelManager.get_button_text('load'),
            command=self.load_attendance,
            width=100,
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            state="disabled"
        )
        self.load_btn.pack(side="left", padx=(20, 8))

        # Step 4: Save Button
        self.save_btn = ctk.CTkButton(
            controls_frame,
            text="4. " + TextLabelManager.get_button_text('save'),
            command=self.save_attendance,
            width=100,
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)

        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Instructions
        self.show_instructions()

    def show_instructions(self):
        """Show step-by-step instructions."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        instruction_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        instruction_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        ctk.CTkLabel(
            instruction_frame,
            text="📋 How to Record Attendance",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 30))
        
        instructions = [
            "1. Select a class from the dropdown menu",
            "2. Choose the date for attendance recording",
            "3. Click 'Load' to see the student list",
            "4. Check/uncheck students who are present",
            "5. Click 'Save' to record the attendance"
        ]
        
        for instruction in instructions:
            ctk.CTkLabel(
                instruction_frame,
                text=instruction,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(pady=5, fill="x")

    def on_class_selected(self, value):
        """Handle class selection."""
        self.current_class = value
        self.update_load_button_state()
        
    def on_date_selected(self, event=None):
        """Handle date selection."""
        self.current_date = self.date_picker.get_date()
        self.update_load_button_state()
        
    def update_load_button_state(self):
        """Enable load button when both class and date are selected."""
        if self.current_class and self.current_date:
            self.load_btn.configure(state="normal")
        else:
            self.load_btn.configure(state="disabled")

    def load_attendance(self):
        """Load students and existing attendance for the selected class and date."""
        if not self.current_class or not self.current_date:
            messagebox.showwarning("Selection Required", "Please select both class and date first.")
            return
            
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Load students
        self.students = self.session.query(Student).filter_by(
            class_name=self.current_class
        ).order_by(Student.full_name).all()
        
        if not self.students:
            self.show_no_students()
            return
            
        # Create attendance interface
        self.create_attendance_interface()
        
    def show_no_students(self):
        """Show message when no students found."""
        empty_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        ctk.CTkLabel(
            empty_frame,
            text="No Students Found",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(pady=20)
        
        ctk.CTkLabel(
            empty_frame,
            text=f"No students registered in {self.current_class}",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_secondary"]
        ).pack()
        
    def create_attendance_interface(self):
        """Create the attendance marking interface."""
        # Header with class and date info
        info_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Attendance for {self.current_class} - {self.current_date.strftime('%B %d, %Y')}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Quick actions
        actions_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        ctk.CTkButton(
            actions_frame,
            text="Mark All Present",
            command=self.mark_all_present,
            width=120,
            height=35,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="Mark All Absent",
            command=self.mark_all_absent,
            width=120,
            height=35,
            corner_radius=8,
            fg_color=COLORS["danger"],
            hover_color="#c9302c",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        ).pack(side="left", padx=5)
        
        # Students list
        students_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["border"],
            corner_radius=8
        )
        students_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.attendance_vars = {}
        
        # Load existing attendance
        existing_attendance = {}
        attendance_records = self.session.query(Attendance).filter_by(
            date=self.current_date
        ).all()
        
        for record in attendance_records:
            existing_attendance[record.student_id] = record.is_present
            
        # Create student checkboxes
        for i, student in enumerate(self.students):
            student_frame = ctk.CTkFrame(students_frame, fg_color=COLORS["bg_card"], corner_radius=8)
            student_frame.pack(fill="x", padx=10, pady=5)
            
            # Student info
            info_frame = ctk.CTkFrame(student_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=f"{i+1:2d}. {student.name}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                info_frame,
                text=f"({student.student_id})",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(side="left", padx=(10, 0))
            
            # Attendance checkbox
            is_present = existing_attendance.get(student.id, True)  # Default to present
            var = tk.BooleanVar(value=is_present)
            self.attendance_vars[student.id] = var
            
            checkbox = ctk.CTkCheckBox(
                student_frame,
                text="Present",
                variable=var,
                width=100,
                height=30,
                corner_radius=6,
                fg_color=COLORS["success"],
                hover_color=COLORS["primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13)
            )
            checkbox.pack(side="right", padx=15, pady=10)
            
        # Enable save button
        self.save_btn.configure(state="normal")
        
    def mark_all_present(self):
        """Mark all students as present."""
        for var in self.attendance_vars.values():
            var.set(True)
            
    def mark_all_absent(self):
        """Mark all students as absent."""
        for var in self.attendance_vars.values():
            var.set(False)
            
    def save_attendance(self):
        """Save attendance records."""
        if not self.students or not self.attendance_vars:
            messagebox.showwarning("No Data", "Please load attendance first.")
            return
            
        try:
            saved_count = 0
            
            for student in self.students:
                is_present = self.attendance_vars[student.id].get()
                
                # Check if record already exists
                existing_record = self.session.query(Attendance).filter_by(
                    student_id=student.id,
                    date=self.current_date
                ).first()
                
                if existing_record:
                    existing_record.is_present = is_present
                else:
                    new_record = Attendance(
                        student_id=student.id,
                        date=self.current_date,
                        is_present=is_present
                    )
                    self.session.add(new_record)
                    
                saved_count += 1
                
            self.session.commit()
            
            present_count = sum(1 for var in self.attendance_vars.values() if var.get())
            absent_count = len(self.students) - present_count
            
            messagebox.showinfo(
                "Attendance Saved", 
                f"✅ Attendance saved successfully!\n\n"
                f"Class: {self.current_class}\n"
                f"Date: {self.current_date.strftime('%B %d, %Y')}\n"
                f"Present: {present_count}\n"
                f"Absent: {absent_count}\n"
                f"Total: {len(self.students)}"
            )
            
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to save attendance: {str(e)}")

    def add_today(self):
        """Quick add today's date - kept for compatibility."""
        from datetime import date
        self.date_picker.set_date(date.today())
        self.current_date = date.today()
        self.update_load_button_state()

    # Remove all the old complex methods - they're no longer needed
    def add_new_attendance_column(self):
        """Legacy method - now handled by date picker."""
        pass
        
    def load_class(self):
        """Legacy method - now handled by load_attendance."""
        pass
        
    def calculate_percentage(self, student_id):
        """Legacy method - no longer needed."""
        pass
        
    def add_attendance_checkbox(self, student, att_date, row, col):
        """Legacy method - no longer needed."""
        pass
        
    def export_to_csv(self):
        """Export functionality - can be added later if needed."""
        messagebox.showinfo("Export", "Export functionality will be added in a future update.")


class SchoolManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Glorious Fountain Academy")
        self.session = Session()

        self.setup_tabs()

    def setup_tabs(self):
        self.tabview = ctk.CTkTabview(self.root, anchor='center')
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Student Registration")
        self.tabview.add("Marks Entry")
        self.tabview.add("Broadsheet")
        self.tabview.add("Attendance")

        self.marks_tab = MarksEntryTab(self.tabview.tab("Marks Entry"), self.session)
        self.student_tab = StudentRegistrationTab(self.tabview.tab("Student Registration"), self.session,
                                                  on_student_added_callback=self.refresh_marks_tab)
        self.sheet_tab = BroadsheetTab(self.tabview.tab("Broadsheet"), self.session)
        self.attendance_tab = AttendanceTab(self.tabview.tab("Attendance"), self.session)

        self.student_tab.pack(fill="both", expand=True)
        self.marks_tab.pack(fill="both", expand=True)
        self.sheet_tab.pack(fill="both", expand=True)
        self.attendance_tab.pack(fill="both", expand=True)

    def refresh_marks_tab(self):
        self.marks_tab.load_students()