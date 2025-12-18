import customtkinter as ctk
from tkinter import messagebox
from models import Session, Student, Attendance, Mark, Fee

class StudentsListTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        self.selected_student_id = None
        self.details_frame = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        # Top Frame for controls
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(control_frame, text="All Students", font=("Roboto", 16, "bold")).pack(side="left", padx=10)

        # Main frame for the list
        self.students_list_frame = ctk.CTkScrollableFrame(self, label_text="Students")
        self.students_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def load_students(self):
        # Clear existing student list
        for widget in self.students_list_frame.winfo_children():
            widget.destroy()

        students = self.session.query(Student).order_by(Student.name).all()

        headers = ["ID", "Name", "Class", "Actions"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.students_list_frame, text=header, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=10, pady=5)

        for i, student in enumerate(students, start=1):
            ctk.CTkLabel(self.students_list_frame, text=student.student_id).grid(row=i, column=0, padx=10, pady=5)
            ctk.CTkLabel(self.students_list_frame, text=student.name).grid(row=i, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.students_list_frame, text=student.class_name).grid(row=i, column=2, padx=10, pady=5)

            action_button = ctk.CTkButton(self.students_list_frame, text="View Details", command=lambda s=student.id: self.toggle_details(s))
            action_button.grid(row=i, column=3, padx=10, pady=5)

    def toggle_details(self, student_id):
        if self.selected_student_id == student_id:
            # Hide details
            if self.details_frame:
                self.details_frame.destroy()
            self.details_frame = None
            self.selected_student_id = None
        else:
            # Show details
            if self.details_frame:
                self.details_frame.destroy()

            self.selected_student_id = student_id
            self.details_frame = ctk.CTkFrame(self)
            self.details_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

            student = self.session.query(Student).filter_by(id=student_id).one()

            # Collapsible sections
            self.create_collapsible_section(self.details_frame, "Attendance", self.get_attendance_details(student))
            self.create_collapsible_section(self.details_frame, "Results", self.get_results_details(student))

    def create_collapsible_section(self, parent, title, details_widget):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5, padx=5, fill="x")

        button = ctk.CTkButton(frame, text=title, command=lambda: self.toggle_section(details_widget))
        button.pack(fill="x")

        details_widget.pack(fill="x", expand=True)
        details_widget.pack_forget() # Initially hidden

    def toggle_section(self, widget):
        if widget.winfo_viewable():
            widget.pack_forget()
        else:
            widget.pack()

    def get_attendance_details(self, student):
        frame = ctk.CTkFrame(self.details_frame)
        records = self.session.query(Attendance).filter_by(student_id=student.id).all()
        if not records:
            ctk.CTkLabel(frame, text="No attendance records found.").pack()
        else:
            for record in records:
                status = "Present" if record.is_present else "Absent"
                ctk.CTkLabel(frame, text=f"{record.date}: {status}").pack(anchor="w")
        return frame

    def get_results_details(self, student):
        frame = ctk.CTkFrame(self.details_frame)
        marks = self.session.query(Mark).filter_by(student_id=student.id).all()
        if not marks:
            ctk.CTkLabel(frame, text="No results found.").pack()
        else:
            for mark in marks:
                ctk.CTkLabel(frame, text=f"Term {mark.term} - {mark.subject.subject_code}: Total={mark.total}, Grade={mark.grade}").pack(anchor="w")
        return frame

class SchoolFeesTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Top control frame
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(control_frame, text="Class:").pack(side="left", padx=5)
        self.class_filter = ctk.CTkComboBox(control_frame, values=["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"])
        self.class_filter.pack(side="left", padx=5)

        ctk.CTkLabel(control_frame, text="Term:").pack(side="left", padx=5)
        self.term_filter = ctk.CTkComboBox(control_frame, values=["1", "2", "3"])
        self.term_filter.pack(side="left", padx=5)

        ctk.CTkButton(control_frame, text="Load Fees", command=self.load_fees).pack(side="left", padx=10)

        self.fees_list_frame = ctk.CTkScrollableFrame(self, label_text="Fees Status")
        self.fees_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def load_fees(self):
        for widget in self.fees_list_frame.winfo_children():
            widget.destroy()

        class_name = self.class_filter.get()
        term = int(self.term_filter.get())

        students = self.session.query(Student).filter_by(class_name=class_name).all()

        headers = ["Student Name", "Amount Due", "Amount Paid", "Status", "Update Paid Amount", "Actions"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.fees_list_frame, text=header, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=10, pady=5)

        for i, student in enumerate(students, start=1):
            fee = self.session.query(Fee).filter_by(student_id=student.id, term=term).first()
            if not fee:
                fee = Fee(student_id=student.id, term=term, amount_due=0, amount_paid=0)
                self.session.add(fee)
                self.session.commit()

            status = "Paid" if fee.amount_paid >= fee.amount_due else "Pending"

            ctk.CTkLabel(self.fees_list_frame, text=student.name).grid(row=i, column=0, padx=10, pady=5)
            ctk.CTkLabel(self.fees_list_frame, text=f"{fee.amount_due:.2f}").grid(row=i, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.fees_list_frame, text=f"{fee.amount_paid:.2f}").grid(row=i, column=2, padx=10, pady=5)
            ctk.CTkLabel(self.fees_list_frame, text=status).grid(row=i, column=3, padx=10, pady=5)

            entry = ctk.CTkEntry(self.fees_list_frame, placeholder_text="Enter amount")
            entry.grid(row=i, column=4, padx=5)

            button = ctk.CTkButton(self.fees_list_frame, text="Update", command=lambda s=student.id, t=term, e=entry: self.update_fee(s, t, e.get()))
            button.grid(row=i, column=5, padx=5)

    def update_fee(self, student_id, term, amount_str):
        try:
            amount = float(amount_str)
            fee = self.session.query(Fee).filter_by(student_id=student_id, term=term).one()
            fee.amount_paid = amount
            self.session.commit()
            messagebox.showinfo("Success", "Fee updated successfully.")
            self.load_fees()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

class EnterpriseSchoolManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise School Management System")
        self.session = Session()

        self.setup_tabs()

    def setup_tabs(self):
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Students List")
        self.tabview.add("School Fees")
        self.tabview.add("Student Registration")
        self.tabview.add("Marks Entry")
        self.tabview.add("Broadsheet")
        self.tabview.add("Attendance")

        # Initialize Enterprise Tabs
        self.students_list_tab = StudentsListTab(self.tabview.tab("Students List"), self.session)
        self.school_fees_tab = SchoolFeesTab(self.tabview.tab("School Fees"), self.session)

        # Initialize Original Tabs from forms.py
        from forms import StudentRegistrationTab, MarksEntryTab, BroadsheetTab, AttendanceTab
        self.marks_tab = MarksEntryTab(self.tabview.tab("Marks Entry"), self.session)
        self.student_tab = StudentRegistrationTab(self.tabview.tab("Student Registration"), self.session,
                                                  on_student_added_callback=self.refresh_tabs)
        self.sheet_tab = BroadsheetTab(self.tabview.tab("Broadsheet"), self.session)
        self.attendance_tab = AttendanceTab(self.tabview.tab("Attendance"), self.session)

        # Layout Tabs
        self.students_list_tab.pack(fill="both", expand=True)
        self.school_fees_tab.pack(fill="both", expand=True)
        self.student_tab.pack(fill="both", expand=True)
        self.marks_tab.pack(fill="both", expand=True)
        self.sheet_tab.pack(fill="both", expand=True)
        self.attendance_tab.pack(fill="both", expand=True)

    def refresh_tabs(self):
        self.marks_tab.load_students()
        self.students_list_tab.load_students()
