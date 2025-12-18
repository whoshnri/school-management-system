import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from sqlalchemy.exc import IntegrityError
from models import Session, Student, Subject, Mark, Attendance
from calculations import GradeCalculator

class StudentRegistrationTab(ctk.CTkFrame):
    def __init__(self, parent, session, on_student_added_callback):
        super().__init__(parent)
        self.session = session
        self.on_student_added_callback = on_student_added_callback
        self.setup_ui()

    def setup_ui(self):
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        # Title
        ctk.CTkLabel(self, text="Register New Student", font=("Roboto", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        # ID
        ctk.CTkLabel(self, text="Student ID (e.g. S001):").grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.id_entry = ctk.CTkEntry(self, placeholder_text="Enter ID")
        self.id_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        # Name
        ctk.CTkLabel(self, text="Full Name:").grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter Name", width=300)
        self.name_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Class
        ctk.CTkLabel(self, text="Class:").grid(row=3, column=0, padx=20, pady=10, sticky="e")
        self.class_entry = ctk.CTkComboBox(self, values=["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"])
        self.class_entry.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        
        # Button
        self.add_btn = ctk.CTkButton(self, text="Add Student", command=self.add_student, font=("Roboto", 14, "bold"))
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=30)

    def add_student(self):

        # Get data from entries
        s_id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        
        # Validate data
        if not s_id or not name:
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return

        try:
            # Create new student
            new_student = Student(student_id=s_id, name=name, class_name=class_name)
            self.session.add(new_student)
            self.session.commit()
            
            messagebox.showinfo("Success", f"Student {name} added successfully!")
            
            # Clear fields
            self.id_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
            
            # Notify parent to refresh other tabs
            if self.on_student_added_callback:
                self.on_student_added_callback()
                
        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("Error", f"Student ID '{s_id}' already exists.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to add student: {str(e)}")


class MarksEntryTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        self.active_students = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Scrollable part expands
        
        self.setup_ui()
        self.load_subjects()
        self.load_students() # Initial load

    def setup_ui(self):
        # Top Bar
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(top_frame, text="Student:").pack(side="left", padx=10)
        self.student_var = ctk.StringVar(value="")
        self.student_combo = ctk.CTkOptionMenu(top_frame, variable=self.student_var, width=250)
        self.student_combo.pack(side="left", padx=10)
        
        ctk.CTkLabel(top_frame, text="Term:").pack(side="left", padx=10)
        self.term_var = ctk.StringVar(value="1")
        self.term_combo = ctk.CTkOptionMenu(top_frame, variable=self.term_var, values=["1", "2", "3"], width=80)
        self.term_combo.pack(side="left", padx=10)

        # Marks Grid (Scrollable)
        self.marks_frame = ctk.CTkScrollableFrame(self, label_text="Results Entry")
        self.marks_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Headers
        headers = ["Subject", "CA (40)", "Exam (60)", "Total", "Grade"]
        self.marks_frame.grid_columnconfigure(0, weight=2)
        for i in range(1, 5): self.marks_frame.grid_columnconfigure(i, weight=1)
            
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.marks_frame, text=h, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=5, pady=5)
            
        # Footer
        self.save_btn = ctk.CTkButton(self, text="Save Marks", command=self.save_marks, height=40, width=200, font=("Roboto", 14, "bold"))
        self.save_btn.grid(row=2, column=0, pady=15)

    def load_students(self):
        # Refresh student list
        students = self.session.query(Student).all()
        self.active_students = students
        if students:
            student_list = [f"{s.student_id} - {s.name}" for s in students]
            self.student_combo.configure(values=student_list)
            # Preserve selection if possible, else select first
            current = self.student_var.get()
            if current not in student_list:
                self.student_var.set(student_list[0])
        else:
            self.student_combo.configure(values=["No Students"])
            self.student_var.set("No Students")

    def load_subjects(self):
        self.subjects = self.session.query(Subject).all()
        self.entries = {} # {subject_id: {'ca': var, 'exam': var, 'total': label, 'grade': label}}
        
        for i, sub in enumerate(self.subjects, 1):
            # Name
            ctk.CTkLabel(self.marks_frame, text=sub.subject_name, anchor="w").grid(row=i, column=0, sticky="ew", padx=5)
            
            # CA
            ca_var = tk.StringVar()
            ca_entry = ctk.CTkEntry(self.marks_frame, textvariable=ca_var, width=70)
            ca_entry.grid(row=i, column=1, padx=2)
            
            # Exam
            exam_var = tk.StringVar()
            exam_entry = ctk.CTkEntry(self.marks_frame, textvariable=exam_var, width=70)
            exam_entry.grid(row=i, column=2, padx=2)
            
            # Total & Grade
            total_lbl = ctk.CTkLabel(self.marks_frame, text="0.0")
            total_lbl.grid(row=i, column=3)
            
            grade_lbl = ctk.CTkLabel(self.marks_frame, text="-")
            grade_lbl.grid(row=i, column=4)
            
            # Store refs
            self.entries[sub.id] = {
                'ca': ca_var, 'exam': exam_var, 
                'total': total_lbl, 'grade': grade_lbl
            }
            
            # Tracing
            ca_var.trace_add('write', lambda *args, s=sub: self.recalc(s.id))
            exam_var.trace_add('write', lambda *args, s=sub: self.recalc(s.id))

    def recalc(self, subject_id):
        widgets = self.entries[subject_id]
        try:
            ca = float(widgets['ca'].get() or 0)
            exam = float(widgets['exam'].get() or 0)
            total = ca + exam
            
            widgets['total'].configure(text=f"{total:.1f}")
            grade = GradeCalculator.calculate_grade(total)
            widgets['grade'].configure(text=grade, text_color="red" if grade=='F' else ("#00C853" if grade=='A' else ["black", "white"]))
        except ValueError:
            pass # Ignore active typing errors

    def save_marks(self):
        student_str = self.student_var.get()
        if not student_str or student_str == "No Students":
            return
            
        try:
            student_id_str = student_str.split(' - ')[0]
            student = self.session.query(Student).filter_by(student_id=student_id_str).first()
            if not student: return
            
            term = int(self.term_var.get())
            
            for sub in self.subjects:
                widgets = self.entries[sub.id]
                # Guardrails: Default to 0 if empty/invalid
                try:
                    ca = float(widgets['ca'].get() or 0)
                except ValueError: ca = 0.0
                
                try:
                    exam = float(widgets['exam'].get() or 0)
                except ValueError: exam = 0.0
                
                total = ca + exam
                grade = GradeCalculator.calculate_grade(total)
                
                # DB Update/Insert
                mark = self.session.query(Mark).filter_by(student_id=student.id, subject_id=sub.id, term=term).first()
                if mark:
                    mark.continuous_assessment = ca
                    mark.exams = exam
                    mark.total = total
                    mark.grade = grade
                else:
                    self.session.add(Mark(student_id=student.id, subject_id=sub.id, term=term, 
                                          continuous_assessment=ca, exams=exam, total=total, grade=grade))
            
            self.session.commit()
            messagebox.showinfo("Saved", f"Marks updated for {student.name}")
            
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", str(e))


class BroadsheetTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        self.broadsheet_data = None # Stores pivoted data for export
        self.students = []
        self.subjects = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()

    def setup_ui(self):
        # --- Controls Frame ---
        ctrl = ctk.CTkFrame(self)
        ctrl.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Class Filter
        ctk.CTkLabel(ctrl, text="Class:").pack(side="left", padx=5)
        
        # Determine class options dynamically (assuming Student model is available)
        class_values = [f"{cls} ({self.get_class_population(cls)})" for cls in ["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"]]
        if not self.session.query(Student).first():
            class_values = ["JSS1 (0)"] # Default if DB is empty
            
        self.class_filter_raw = ctk.CTkComboBox(ctrl, values=class_values, width=150)
        self.class_filter_raw.pack(side="left", padx=5)
        
        # Term Filter
        ctk.CTkLabel(ctrl, text="Term:").pack(side="left", padx=5)
        self.term_filter = ctk.CTkOptionMenu(ctrl, values=["1", "2", "3"], width=70)
        self.term_filter.pack(side="left", padx=5)
        
        # Load Button
        ctk.CTkButton(ctrl, text="Load Broadsheet", command=self.load_sheet).pack(side="left", padx=20)
        
        # Export Button
        self.export_btn = ctk.CTkButton(ctrl, text="Export to CSV", command=self.export_to_csv, state="disabled")
        self.export_btn.pack(side="right", padx=10)
        
        # --- Broadsheet Grid (Scrollable) ---
        self.sheet_frame = ctk.CTkScrollableFrame(self, orientation="horizontal") 
        self.sheet_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    
    def get_class_population(self, class_name):
        # Counts how many students are in a given class
        entries = self.session.query(Student).filter_by(class_name=class_name).count()
        return entries

    def load_sheet(self):
        """Fetches and displays the broadsheet data for the selected class and term."""
        # Clear previous data
        for widget in self.sheet_frame.winfo_children():
            widget.destroy()
            
        # Get filters
        class_name_full = self.class_filter_raw.get()
        class_name = class_name_full.split(' ')[0] if class_name_full else ""
        term = int(self.term_filter.get())
        
        if not class_name:
            messagebox.showwarning("Selection Error", "Please select a class.")
            return

        # Data Fetch
        self.students = self.session.query(Student).filter_by(class_name=class_name).order_by(Student.name).all()
        self.subjects = self.session.query(Subject).all()
        
        if not self.students or not self.subjects:
            messagebox.showinfo("No Data", f"No students or subjects found for {class_name}.")
            self.export_btn.configure(state="disabled")
            return

        # Fetch marks efficiently by joining Student (to filter by class)
        # Assuming Mark has a relationship 'student'
        marks = self.session.query(Mark).filter(
            Mark.term == term, 
            Mark.student.has(class_name=class_name)
        ).all()
        
        # Pivot Data (Map: student_id -> {subject_id -> total_score})
        data_map = {s.id: {} for s in self.students}
        for m in marks:
            if m.student_id in data_map:
                data_map[m.student_id][m.subject_id] = m.total

        self.broadsheet_data = data_map # Store for export
        self.export_btn.configure(state="normal")
        
        # --- Render Grid ---
        
        # 0. Set up column configuration for better alignment
        self.sheet_frame.grid_columnconfigure(0, weight=0) # ID
        self.sheet_frame.grid_columnconfigure(1, weight=1) # Name
        for i in range(2, len(self.subjects) + 2):
             self.sheet_frame.grid_columnconfigure(i, weight=0) # Marks
        
        # Header Row
        headers = ["Student ID", "Name"] + [s.subject_code for s in self.subjects]
        for c, h in enumerate(headers):
            ctk.CTkLabel(self.sheet_frame, text=h, font=("Roboto", 12, "bold"), width=80).grid(row=0, column=c, padx=5, pady=5)
            
        # Student Rows
        for r, student in enumerate(self.students, 1):
            # ID
            ctk.CTkLabel(self.sheet_frame, text=student.student_id).grid(row=r, column=0, padx=5)
            # Name
            ctk.CTkLabel(self.sheet_frame, text=student.name, anchor="w").grid(row=r, column=1, padx=5, sticky="w")
            
            # Marks
            for c, sub in enumerate(self.subjects, 2):
                score = data_map[student.id].get(sub.id, "-")
                score_text = f"{score:.0f}" if isinstance(score, float) else score
                ctk.CTkLabel(self.sheet_frame, text=score_text).grid(row=r, column=c, padx=5)

    def export_to_csv(self):
        """Exports the currently loaded broadsheet data to a CSV file."""
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
        
        if not filename: return

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Header Row
                header = ["Student ID", "Name"] + [s.subject_code for s in self.subjects]
                writer.writerow(header)

                # Data Rows
                for student in self.students:
                    row_data = [student.student_id, student.name]
                    
                    # Marks
                    for sub in self.subjects:
                        score = self.broadsheet_data[student.id].get(sub.id, "-")
                        score_text = f"{score:.0f}" if isinstance(score, float) else score
                        row_data.append(score_text)
                        
                    writer.writerow(row_data)

            messagebox.showinfo("Export Success", f"Broadsheet data saved to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during CSV export: {str(e)}")


class AttendanceTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        self.current_class = None
        self.setup_ui()
        self.attendance_widgets = {} # {student_id: {date_str: CheckboxVar, 'percentage': label}}
        self.loaded_dates = []

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Controls ---
        ctrl_frame = ctk.CTkFrame(self)
        ctrl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(ctrl_frame, text="Class:").pack(side="left", padx=5)
        
        # Get class values dynamically
        unique_classes = [result[0] for result in self.session.query(Student.class_name).distinct().all()]
        class_values = unique_classes if unique_classes else ["JSS1"]
        
        self.class_filter = ctk.CTkComboBox(ctrl_frame, values=class_values, width=150)
        self.class_filter.pack(side="left", padx=5)

        load_btn = ctk.CTkButton(ctrl_frame, text="Load Class", command=self.load_class)
        load_btn.pack(side="left", padx=10)
        
        self.add_date_btn = ctk.CTkButton(ctrl_frame, text="Add New Date", command=self.add_new_attendance_column, state="disabled")
        self.add_date_btn.pack(side="left", padx=10)
        
        self.save_btn = ctk.CTkButton(ctrl_frame, text="Save Attendance", command=self.save_attendance, state="disabled")
        self.save_btn.pack(side="left", padx=10)

        self.export_btn = ctk.CTkButton(ctrl_frame, text="Export to CSV", command=self.export_to_csv, state="disabled")
        self.export_btn.pack(side="right", padx=10)

        # --- Scrollable Attendance Grid ---
        self.attendance_grid = ctk.CTkScrollableFrame(self, orientation="horizontal") 
        self.attendance_grid.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
    def load_class(self):
        class_name = self.class_filter.get().split(' ')[0]
        if not class_name: return

        # Clear existing
        for widget in self.attendance_grid.winfo_children():
            widget.destroy()
        self.attendance_widgets = {}
        self.loaded_dates = []
        self.current_class = class_name
        
        self.students = self.session.query(Student).filter_by(class_name=class_name).order_by(Student.name).all()
        if not self.students:
            messagebox.showinfo("Empty Class", f"No students found in {class_name}.")
            self.add_date_btn.configure(state="disabled")
            self.save_btn.configure(state="disabled")
            self.export_btn.configure(state="disabled")
            return

        self.add_date_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.export_btn.configure(state="normal")

        # Initial Headers: Name, (Dates...), Percentage
        headers = ["Student Name"]
        col = 0
        ctk.CTkLabel(self.attendance_grid, text=headers[0], font=("Roboto", 12, "bold"), width=150).grid(row=0, column=col, padx=5, pady=5)
        col += 1

        # Fetch all unique attendance dates for this class
        date_records = self.session.query(Attendance.date).filter(
            Attendance.student.has(class_name=class_name)
        ).distinct().order_by(Attendance.date).all()
        
        self.loaded_dates = [r[0] for r in date_records]
        
        # Load date headers
        for att_date in self.loaded_dates:
            ctk.CTkLabel(self.attendance_grid, text=att_date.strftime("%Y-%m-%d"), font=("Roboto", 12, "bold"), width=80).grid(row=0, column=col, padx=2, pady=5)
            col += 1
            
        # Percentage Header
        ctk.CTkLabel(self.attendance_grid, text="Attendance %", font=("Roboto", 12, "bold"), width=100).grid(row=0, column=col, padx=5, pady=5)
        
        # Load student rows and existing data
        row = 1
        for student in self.students:
            self.attendance_widgets[student.id] = {'percentage': None, 'attendance': {}}
            
            # Name
            ctk.CTkLabel(self.attendance_grid, text=student.name, anchor="w", width=150).grid(row=row, column=0, sticky="w", padx=5)
            
            # Attendance data for each loaded date
            col = 1
            for att_date in self.loaded_dates:
                self.add_attendance_checkbox(student, att_date, row, col)
                col += 1
            
            # Percentage Label
            percent_lbl = ctk.CTkLabel(self.attendance_grid, text="0.0%", width=100)
            percent_lbl.grid(row=row, column=col, padx=5)
            self.attendance_widgets[student.id]['percentage'] = percent_lbl
            
            self.calculate_percentage(student.id)
            row += 1

    def add_attendance_checkbox(self, student, att_date, row, col):
        date_str = att_date.strftime("%Y-%m-%d")
        
        # Check if record exists for this student/date
        record = self.session.query(Attendance).filter_by(student_id=student.id, date=att_date).first()
        initial_value = 1 if (record and record.is_present) else 0

        # Boolean Var for Checkbox
        var = tk.IntVar(value=initial_value)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(self.attendance_grid, text="", variable=var, 
                                   command=lambda s_id=student.id: self.calculate_percentage(s_id))
        checkbox.grid(row=row, column=col, padx=2, pady=2)
        
        # Store widget reference
        self.attendance_widgets[student.id]['attendance'][date_str] = var

    def add_new_attendance_column(self):
        if not self.current_class: return
        
        # Simple date prompt (for real app, use a date picker)
        new_date_str = ctk.CTkInputDialog(text="Enter Attendance Date (YYYY-MM-DD):", title="New Attendance Date").get_input()
        if not new_date_str: return
        
        # try:
        #     new_date = dt_date.fromisoformat(new_date_str)
        # except ValueError:
        #     messagebox.showerror("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
        #     # return

        if new_date in self.loaded_dates:
            messagebox.showwarning("Duplicate Date", "Attendance for this date is already loaded.")
            return
            
        # 1. Update list of loaded dates
        self.loaded_dates.append(new_date)
        self.loaded_dates.sort()
        
        # 2. Re-render the grid to place the new column correctly
        self.load_class() # Easiest way to re-render: clear and reload.

    def calculate_percentage(self, student_id):
        widget_data = self.attendance_widgets.get(student_id)
        if not widget_data: return
        
        total_days = len(self.loaded_dates)
        if total_days == 0:
            percentage = 0.0
        else:
            present_days = sum(var.get() for var in widget_data['attendance'].values())
            percentage = (present_days / total_days) * 100
        
        widget_data['percentage'].configure(text=f"{percentage:.1f}%")

    def save_attendance(self):
        if not self.students or not self.loaded_dates: return
        
        try:
            for student in self.students:
                student_id = student.id
                widget_data = self.attendance_widgets[student_id]['attendance']
                
                for date_str, var in widget_data.items():
                    att_date = dt_date.fromisoformat(date_str)
                    is_present = bool(var.get())
                    
                    # Check if record exists
                    att_record = self.session.query(Attendance).filter_by(student_id=student_id, date=att_date).first()
                    
                    if att_record:
                        # Update
                        att_record.is_present = is_present
                    else:
                        # Insert
                        new_record = Attendance(student_id=student_id, date=att_date, is_present=is_present)
                        self.session.add(new_record)
                        
            self.session.commit()
            messagebox.showinfo("Saved", f"Attendance for {len(self.loaded_dates)} days updated successfully.")
            
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to save attendance: {str(e)}")
            
    def export_to_csv(self):
        if not self.students or not self.loaded_dates:
            messagebox.showwarning("No Data", "Load a class before exporting.")
            return
            
        filename = tk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"Attendance_{self.current_class}_{dt_date.today()}.csv"
        )
        
        if not filename: return

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Header Row
                header = ["Student ID", "Name"] + [d.strftime("%Y-%m-%d") for d in self.loaded_dates] + ["Attendance %"]
                writer.writerow(header)

                # Data Rows
                for student in self.students:
                    widget_data = self.attendance_widgets[student.id]
                    row_data = [student.student_id, student.name]
                    
                    # Attendance status
                    for att_date in self.loaded_dates:
                        date_str = att_date.strftime("%Y-%m-%d")
                        # Use the checkmark var value (1 for present, 0 for absent) or fetch from DB if not loaded
                        present = widget_data['attendance'].get(date_str, tk.IntVar(value=0)).get()
                        row_data.append("P" if present == 1 else "A")
                        
                    # Percentage
                    percent_text = widget_data['percentage'].cget("text")
                    row_data.append(percent_text)
                    
                    writer.writerow(row_data)

            messagebox.showinfo("Export Success", f"Attendance data saved to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during CSV export: {str(e)}")

class SchoolManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.session = Session()
        
        self.setup_tabs()
        
    def setup_tabs(self):
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("Student Registration")
        self.tabview.add("Marks Entry")
        self.tabview.add("Broadsheet")
        self.tabview.add("Attendance")
        
        # Initialize Tabs
        self.marks_tab = MarksEntryTab(self.tabview.tab("Marks Entry"), self.session)
        self.student_tab = StudentRegistrationTab(self.tabview.tab("Student Registration"), self.session, 
                                                  on_student_added_callback=self.refresh_marks_tab)
        self.sheet_tab = BroadsheetTab(self.tabview.tab("Broadsheet"), self.session)
        self.attendance_tab = AttendanceTab(self.tabview.tab("Attendance"), self.session)

        # Layout Tabs
        self.student_tab.pack(fill="both", expand=True)
        self.marks_tab.pack(fill="both", expand=True)
        self.sheet_tab.pack(fill="both", expand=True)
        self.attendance_tab.pack(fill="both", expand=True)
        
    def refresh_marks_tab(self):
        self.marks_tab.load_students()