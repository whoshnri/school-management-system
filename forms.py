import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from sqlalchemy.exc import IntegrityError
from models import Session, Student, Subject, Mark, Attendance
from calculations import GradeCalculator
from datetime import date as dt_date
import csv
from ui_components import TextLabelManager, DatePickerField, MODAL_STYLE, input_style, safe_export_filename

# Modern color palette (matching enterprise_forms.py)
COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "secondary": "#5f6368",
    "secondary_hover": "#4a4f54",
    "success": "#34a853",
    "warning": "#fbbc04",
    "danger": "#ea4335",
    "bg_dark": "#ffffff",
    "bg_card": "#f8f9fa",
    "text_primary": "#202124",
    "text_secondary": "#5f6368",
    "border": "#dadce0",
    "sheet_header": "#eef2f7",
    "sheet_row": "#ffffff",
    "sheet_row_alt": "#f8f9fa",
    "text_on_primary": "#ffffff",
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
            fg_color=COLORS["sheet_row"],
            text_color=COLORS["text_primary"],
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
            fg_color=COLORS["sheet_row"],
            text_color=COLORS["text_primary"],
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
        """Increment mark value without exceeding the maximum."""
        try:
            current = int(float(var.get() or 0))
            if current < max_value:
                var.set(str(current + 1))
        except ValueError:
            var.set("0")
    
    def decrement_mark(self, var, min_value):
        """Decrement mark value without going below the minimum."""
        try:
            current = int(float(var.get() or 0))
            if current > min_value:
                var.set(str(current - 1))
        except ValueError:
            var.set(str(min_value))

    def _is_mark_value_valid(self, value_str, max_value):
        value = value_str.strip()
        if value == "":
            return True
        try:
            mark = float(value)
        except ValueError:
            return False
        return 0 <= mark <= max_value

    def validate_mark_input(self, var, entry, error_label, max_value):
        """Validate mark input and show inline errors instead of clamping values."""
        value = var.get().strip()
        normal_border = COLORS["border"]
        error_border = COLORS["danger"]

        if value == "":
            entry.configure(border_color=normal_border)
            error_label.configure(text="")
            return True

        try:
            mark = float(value)
        except ValueError:
            entry.configure(border_color=error_border)
            error_label.configure(text="Enter a valid number")
            return False

        if mark < 0:
            entry.configure(border_color=error_border)
            error_label.configure(text="Minimum is 0")
            return False

        if mark > max_value:
            entry.configure(border_color=error_border)
            error_label.configure(text=f"Maximum is {max_value}")
            return False

        entry.configure(border_color=normal_border)
        error_label.configure(text="")
        return True

    def _on_mark_change(self, var, entry, error_label, max_value, subject_id):
        self.validate_mark_input(var, entry, error_label, max_value)
        self.recalc(subject_id)

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

            ca_var = tk.StringVar(value="")
            ca_cell = ctk.CTkFrame(self.marks_frame, fg_color="transparent")
            ca_cell.grid(row=i, column=1, padx=10, pady=5, sticky="w")

            ca_frame = ctk.CTkFrame(ca_cell, fg_color="transparent")
            ca_frame.pack(anchor="w")
            
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

            ca_error_label = ctk.CTkLabel(
                ca_cell,
                text="",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["danger"],
                anchor="w",
            )
            ca_error_label.pack(anchor="w", pady=(2, 0))

            exam_var = tk.StringVar(value="")
            exam_cell = ctk.CTkFrame(self.marks_frame, fg_color="transparent")
            exam_cell.grid(row=i, column=2, padx=10, pady=5, sticky="w")

            exam_frame = ctk.CTkFrame(exam_cell, fg_color="transparent")
            exam_frame.pack(anchor="w")
            
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

            exam_error_label = ctk.CTkLabel(
                exam_cell,
                text="",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["danger"],
                anchor="w",
            )
            exam_error_label.pack(anchor="w", pady=(2, 0))

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
                'ca': ca_var,
                'exam': exam_var,
                'ca_entry': ca_entry,
                'exam_entry': exam_entry,
                'ca_error': ca_error_label,
                'exam_error': exam_error_label,
                'total': total_lbl,
                'grade': grade_lbl,
            }

            ca_var.trace_add(
                'write',
                lambda *args, v=ca_var, e=ca_entry, el=ca_error_label, s=sub: self._on_mark_change(
                    v, e, el, 30, s.id
                ),
            )
            exam_var.trace_add(
                'write',
                lambda *args, v=exam_var, e=exam_entry, el=exam_error_label, s=sub: self._on_mark_change(
                    v, e, el, 70, s.id
                ),
            )
            self.recalc(sub.id)

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
        ca_str = widgets['ca'].get().strip()
        exam_str = widgets['exam'].get().strip()

        if not self._is_mark_value_valid(ca_str, 30) or not self._is_mark_value_valid(exam_str, 70):
            widgets['total'].configure(text="-")
            widgets['grade'].configure(text="-", text_color=COLORS["text_secondary"])
            return

        try:
            ca = float(ca_str) if ca_str else 0
            exam = float(exam_str) if exam_str else 0
            total = ca + exam

            widgets['total'].configure(text=f"{total:.0f}")
            grade = GradeCalculator.calculate_grade(total)

            grade_color = COLORS["success"] if grade in ['A', 'B'] else (
                COLORS["warning"] if grade in ['C', 'D'] else COLORS["danger"]
            )
            widgets['grade'].configure(text=grade, text_color=grade_color)
        except ValueError:
            widgets['total'].configure(text="-")
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
            has_errors = False

            for sub in self.subjects:
                widgets = self.entries[sub.id]
                if not self.validate_mark_input(widgets['ca'], widgets['ca_entry'], widgets['ca_error'], 30):
                    has_errors = True
                if not self.validate_mark_input(widgets['exam'], widgets['exam_entry'], widgets['exam_error'], 70):
                    has_errors = True

            if has_errors:
                messagebox.showwarning(
                    "Invalid Marks",
                    "Please fix the highlighted errors before saving.",
                )
                return

            for sub in self.subjects:
                widgets = self.entries[sub.id]
                try:
                    ca = float(widgets['ca'].get() or 0)
                except ValueError:
                    ca = 0.0

                try:
                    exam = float(widgets['exam'].get() or 0)
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
            **input_style(),
        )
        self.class_filter_raw.pack(side="left", padx=5)

        ctk.CTkLabel(
            controls_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(20, 8))

        self.term_filter = ctk.CTkComboBox(
            controls_frame,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=150,
            height=40,
            **input_style(),
        )
        self.term_filter.pack(side="left", padx=5)

        ctk.CTkButton(
            controls_frame,
            text=TextLabelManager.get_button_text('load'),
            command=self.load_sheet,
            width=90,
            height=40,
            corner_radius=MODAL_STYLE["radius"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(20, 8))

        self.export_btn = ctk.CTkButton(
            controls_frame,
            text=TextLabelManager.get_button_text('export') + " CSV",
            command=self.export_to_csv,
            state="disabled",
            width=120,
            height=40,
            corner_radius=MODAL_STYLE["radius"],
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_hover"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.export_btn.pack(side="left", padx=5)

        self.import_btn = ctk.CTkButton(
            controls_frame,
            text="Import CSV",
            command=self.import_from_csv,
            width=100,
            height=40,
            corner_radius=MODAL_STYLE["radius"],
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.import_btn.pack(side="left", padx=5)

        # Broadsheet Grid
        self.sheet_frame = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            fg_color=COLORS["sheet_row"],
            corner_radius=MODAL_STYLE["radius"],
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        self.sheet_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    def _sheet_cell(self, parent, text, row, column, width=70, anchor="w", bold=False, bg=None):
        if bg is None:
            bg = COLORS["sheet_header"] if row == 0 else (
                COLORS["sheet_row_alt"] if row % 2 == 0 else COLORS["sheet_row"]
            )
        label = ctk.CTkLabel(
            parent,
            text=text,
            width=width,
            anchor=anchor,
            fg_color=bg,
            corner_radius=0,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold" if bold or row == 0 else "normal",
            ),
            text_color=COLORS["text_secondary"] if row == 0 else COLORS["text_primary"],
        )
        label.grid(row=row, column=column, padx=0, pady=0, sticky="nsew")
        return label

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
                text=f"No students in {class_name}",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=COLORS["text_primary"]
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
        col_widths = [40, 110, 180] + [64] * len(self.subjects) + [70, 70, 50]
        for c, h in enumerate(headers):
            self._sheet_cell(
                self.sheet_frame, h, 0, c,
                width=col_widths[c] if c < len(col_widths) else 64,
                anchor="center" if c > 2 else ("center" if c == 0 else "w"),
                bold=True,
                bg=COLORS["sheet_header"],
            )

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
            row_bg = COLORS["sheet_row"] if r % 2 == 1 else COLORS["sheet_row_alt"]

            self._sheet_cell(self.sheet_frame, str(r), r, 0, width=40, bg=row_bg, anchor="center")
            self._sheet_cell(self.sheet_frame, student.student_id, r, 1, width=110, bg=row_bg)
            self._sheet_cell(self.sheet_frame, student.name, r, 2, width=180, bg=row_bg)

            scores = []
            for c, sub in enumerate(self.subjects, 3):
                score = data_map[student.id].get(sub.id, "-")
                if isinstance(score, (int, float)):
                    scores.append(score)
                    score_text = f"{score:.0f}"
                else:
                    score_text = "-"

                self._sheet_cell(
                    self.sheet_frame,
                    score_text,
                    r,
                    c,
                    width=70,
                    bg=row_bg,
                    anchor="center",
                )

            total = sum(scores)
            avg = total / len(self.subjects) if self.subjects else 0
            pos = positions[student.id]
            summary_start = len(self.subjects) + 3

            self._sheet_cell(
                self.sheet_frame,
                f"{total:.0f}",
                r,
                summary_start,
                width=70,
                bold=True,
                bg=row_bg,
                anchor="center",
            )
            self._sheet_cell(
                self.sheet_frame,
                f"{avg:.1f}",
                r,
                summary_start + 1,
                width=70,
                bg=row_bg,
                anchor="center",
            )
            self._sheet_cell(
                self.sheet_frame,
                f"{pos}",
                r,
                summary_start + 2,
                width=50,
                bold=True,
                bg=row_bg,
                anchor="center",
            )

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
    """Excel-style attendance sheet: students as rows, dates as columns."""

    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.current_class = None
        self.students = []
        self.attendance_dates = []
        self.attendance_vars = {}
        self.record_map = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()

    def _date_key(self, value):
        if isinstance(value, dt_date):
            return value.isoformat()
        if value is None:
            return ""
        text = str(value).strip()
        return text[:10] if len(text) >= 10 else text

    def _format_date_header(self, date_key):
        try:
            parsed = dt_date.fromisoformat(date_key)
            return parsed.strftime("%a, %b %d")
        except ValueError:
            return date_key

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))

        ctk.CTkLabel(
            header_frame,
            text=TextLabelManager.get_header_text('attendance'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=20, pady=15)

        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)

        ctk.CTkLabel(
            controls_frame,
            text="Class",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 8))

        self.class_var = ctk.StringVar()
        self.class_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.class_var,
            values=["SSS1", "SSS2", "SSS3"],
            width=100,
            height=40,
            command=self.on_class_selected,
            **input_style(),
        )
        self.class_combo.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            controls_frame,
            text="New Date",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 8))

        self.date_picker = DatePickerField(
            controls_frame,
            width=120,
            height=40,
            font_size=13,
        )
        self.date_picker.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            controls_frame,
            text="Add Date Column",
            command=self.add_date_column,
            width=130,
            height=40,
            corner_radius=MODAL_STYLE["radius"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).pack(side="left", padx=(0, 12))

        self.save_btn = ctk.CTkButton(
            controls_frame,
            text=TextLabelManager.get_button_text('save') + " All",
            command=self.save_attendance,
            width=110,
            height=40,
            corner_radius=MODAL_STYLE["radius"],
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            state="disabled",
        )
        self.save_btn.pack(side="left")

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=MODAL_STYLE["radius"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.show_placeholder()

    def show_placeholder(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        placeholder = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        placeholder.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(
            placeholder,
            text="Attendance Sheet",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            placeholder,
            text="Select a class to load the sheet. Use Add Date Column to add a new date column with checkboxes for each student.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            wraplength=520,
        ).pack()

    def on_class_selected(self, value):
        self.current_class = value
        self.load_sheet()

    def load_sheet(self):
        if not self.current_class:
            return

        self.students = self.session.query(Student).filter_by(
            class_name=self.current_class
        ).order_by(Student.full_name).all()

        if not self.students:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            empty = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            empty.pack(expand=True, fill="both", padx=40, pady=40)
            ctk.CTkLabel(
                empty,
                text=f"No students registered in {self.current_class}",
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack()
            self.attendance_dates = []
            self.attendance_vars = {}
            self.save_btn.configure(state="disabled")
            return

        student_ids = [student.id for student in self.students]
        records = self.session.query(Attendance).filter(
            Attendance.student_id.in_(student_ids)
        ).all()

        self.record_map = {
            (record.student_id, self._date_key(record.date)): record.is_present
            for record in records
        }
        self.attendance_dates = sorted(
            {self._date_key(record.date) for record in records},
            key=lambda value: value,
        )

        self.attendance_vars = {}
        for date_key in self.attendance_dates:
            for student in self.students:
                key = (student.id, date_key)
                default_present = self.record_map.get(key, True)
                self.attendance_vars[key] = tk.BooleanVar(value=default_present)

        self.build_grid()
        self.save_btn.configure(state="normal")

    def add_date_column(self):
        if not self.current_class:
            messagebox.showwarning("Select Class", "Please select a class first.")
            return

        if not self.students:
            self.load_sheet()
            if not self.students:
                return

        new_date = self.date_picker.get_date()
        date_key = self._date_key(new_date)

        if date_key in self.attendance_dates:
            messagebox.showinfo("Date Exists", f"The column for {date_key} is already on the sheet.")
            return

        self.attendance_dates.append(date_key)
        self.attendance_dates.sort()

        for student in self.students:
            key = (student.id, date_key)
            existing = self.record_map.get(key, True)
            self.attendance_vars[key] = tk.BooleanVar(value=existing)

        self.build_grid()
        self.save_btn.configure(state="normal")

    def build_grid(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            toolbar,
            text=f"{self.current_class}  |  {len(self.students)} students  |  {len(self.attendance_dates)} dates",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        actions = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions.pack(side="right")

        ctk.CTkButton(
            actions,
            text="Mark Column Present",
            command=lambda: self.set_active_column(True),
            width=140,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions,
            text="Mark Column Absent",
            command=lambda: self.set_active_column(False),
            width=140,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(side="left", padx=4)

        scroll_host = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["sheet_row"],
            corner_radius=MODAL_STYLE["radius"],
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        scroll_host.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        h_scroll = ctk.CTkScrollableFrame(
            scroll_host,
            orientation="horizontal",
            fg_color="transparent",
            height=min(560, 80 + len(self.students) * 42),
        )
        h_scroll.pack(fill="both", expand=True)

        if not self.attendance_dates:
            ctk.CTkLabel(
                h_scroll,
                text="No date columns yet. Pick a date and click Add Date Column.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_secondary"],
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        fixed_headers = ["#", "Student ID", "Name"]
        fixed_widths = [40, 120, 200]

        for col, header in enumerate(fixed_headers):
            self._grid_header(h_scroll, header, 0, col, fixed_widths[col])

        date_col_padx = (12, 10)

        for offset, date_key in enumerate(self.attendance_dates):
            col = len(fixed_headers) + offset
            self._grid_header(
                h_scroll,
                self._format_date_header(date_key),
                0,
                col,
                80,
                padx=date_col_padx if offset == 0 else (0, 10),
            )

        for row_index, student in enumerate(self.students, start=1):
            row_bg = COLORS["sheet_row"] if row_index % 2 == 1 else COLORS["sheet_row_alt"]
            self._grid_cell(h_scroll, str(row_index), row_index, 0, 40, row_bg, anchor="center")
            self._grid_cell(h_scroll, student.student_id, row_index, 1, 120, row_bg)
            self._grid_cell(h_scroll, student.full_name, row_index, 2, 200, row_bg)

            for offset, date_key in enumerate(self.attendance_dates):
                col = len(fixed_headers) + offset
                cell = ctk.CTkFrame(
                    h_scroll,
                    fg_color=row_bg,
                    width=80,
                    height=36,
                    corner_radius=0,
                )
                cell.grid(
                    row=row_index,
                    column=col,
                    padx=date_col_padx if offset == 0 else (0, 10),
                    pady=0,
                    sticky="nsew",
                )

                var = self.attendance_vars[(student.id, date_key)]
                ctk.CTkCheckBox(
                    cell,
                    text="",
                    variable=var,
                    width=24,
                    height=24,
                    checkbox_width=22,
                    checkbox_height=22,
                    corner_radius=6,
                    border_width=1,
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"],
                ).pack(expand=True)

        self.active_date_key = self.attendance_dates[-1]

    def _grid_header(self, parent, text, row, column, width, padx=(0, 0)):
        frame = ctk.CTkFrame(parent, fg_color=COLORS["sheet_header"], width=width, height=36, corner_radius=0)
        frame.grid(row=row, column=column, padx=padx, pady=0, sticky="nsew")
        ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
        ).pack(expand=True)

    def _grid_cell(self, parent, text, row, column, width, bg, anchor="w"):
        ctk.CTkLabel(
            parent,
            text=text,
            width=width,
            height=36,
            anchor=anchor,
            fg_color=bg,
            corner_radius=0,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_primary"],
        ).grid(row=row, column=column, padx=0, pady=0, sticky="nsew")

    def set_active_column(self, is_present):
        date_key = getattr(self, "active_date_key", None)
        if not date_key or not self.students:
            return
        for student in self.students:
            key = (student.id, date_key)
            if key in self.attendance_vars:
                self.attendance_vars[key].set(is_present)

    def _find_record(self, student_id, date_key):
        records = self.session.query(Attendance).filter_by(student_id=student_id).all()
        for record in records:
            if self._date_key(record.date) == date_key:
                return record
        return None

    def save_attendance(self):
        if not self.students or not self.attendance_dates:
            messagebox.showwarning("No Data", "Add at least one date column before saving.")
            return

        try:
            saved_count = 0
            for date_key in self.attendance_dates:
                for student in self.students:
                    key = (student.id, date_key)
                    is_present = self.attendance_vars[key].get()

                    existing = self._find_record(student.id, date_key)

                    if existing:
                        existing.is_present = is_present
                    else:
                        self.session.add(
                            Attendance(
                                student_id=student.id,
                                date=date_key,
                                is_present=is_present,
                            )
                        )
                    saved_count += 1

            self.session.commit()
            messagebox.showinfo(
                "Attendance Saved",
                f"Saved {saved_count} attendance records for {self.current_class}.",
            )
            self.load_sheet()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to save attendance: {str(e)}")

    def add_today(self):
        self.date_picker.set_date(dt_date.today())

    def add_new_attendance_column(self):
        self.add_date_column()

    def load_class(self):
        if self.current_class:
            self.load_sheet()

    def calculate_percentage(self, student_id):
        pass

    def add_attendance_checkbox(self, student, att_date, row, col):
        pass

    def export_to_csv(self):
        if not self.students or not self.attendance_dates:
            messagebox.showwarning("No Data", "Load a class and add date columns before exporting.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=safe_export_filename(
                "attendance",
                self.current_class,
                dt_date.today().isoformat(),
                extension="csv",
            ),
            title="Export Attendance",
        )
        if not filename:
            return

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Student ID", "Name"] + self.attendance_dates)
                for student in self.students:
                    row = [student.student_id, student.full_name]
                    for date_key in self.attendance_dates:
                        present = self.attendance_vars[(student.id, date_key)].get()
                        row.append("Present" if present else "Absent")
                    writer.writerow(row)
            messagebox.showinfo("Export Success", f"Attendance exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export attendance: {str(e)}")


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