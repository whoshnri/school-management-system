import customtkinter as ctk
from tkinter import messagebox
from models import Session, Student, Attendance, Mark, Fee
from ui_components import TextLabelManager, ModalController

# Modern color palette
COLORS = {
    "primary":       "#1a73e8",
    "primary_hover": "#1557b0",
    "secondary":     "#5f6368",
    "success":       "#34a853",
    "warning":       "#fbbc04",
    "danger":        "#ea4335",
    "bg_dark":       "#ffffff",   # light mode
    "bg_card":       "#f8f9fa",
    "text_primary":  "#202124",
    "text_secondary":"#5f6368",
    "border":        "#dadce0",
}


class StudentsListTab(ctk.CTkFrame):
    def __init__(self, parent, session, on_student_deleted_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.on_student_deleted_callback = on_student_deleted_callback
        # Get the root window for modal controller
        root_window = parent
        while hasattr(root_window, 'master') and root_window.master:
            root_window = root_window.master
        self.modal_controller = ModalController(root_window)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text=TextLabelManager.get_header_text('student_directory'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        # Student count badge
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="0 students",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.count_label.pack(side="left", padx=10, pady=15)

        # Search bar
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Search by name or ID...",
            textvariable=self.search_var,
            width=280,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        search_entry.pack(side="right", padx=20, pady=15)
        self.search_var.trace_add("write", lambda *args: self.load_students())

        # Main frame for the list
        self.students_list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        self.students_list_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # Configure columns with proper weights
        self.students_list_frame.grid_columnconfigure(0, weight=0, minsize=50)   # Row #
        self.students_list_frame.grid_columnconfigure(1, weight=1, minsize=100)  # ID
        self.students_list_frame.grid_columnconfigure(2, weight=2, minsize=200)  # Name
        self.students_list_frame.grid_columnconfigure(3, weight=0, minsize=80)   # Class
        self.students_list_frame.grid_columnconfigure(4, weight=0, minsize=250)  # Actions

    def load_students(self):
        # Clear existing student list
        for widget in self.students_list_frame.winfo_children():
            widget.destroy()

        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') else ""

        students = self.session.query(Student).order_by(Student.full_name).all()
        if search_term:
            students = [s for s in students if search_term in s.name.lower() or search_term in s.student_id.lower()]

        # Update count
        self.count_label.configure(text=f"{len(students)} student{'s' if len(students) != 1 else ''}")

        # Empty state
        if not students:
            empty_frame = ctk.CTkFrame(self.students_list_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, columnspan=5, pady=60)
            
            ctk.CTkLabel(
                empty_frame,
                text="No Data",
                font=ctk.CTkFont(size=48)
            ).pack(pady=(0, 10))
            
            message = "No students found" if search_term else "No students registered yet"
            ctk.CTkLabel(
                empty_frame,
                text=message,
                font=ctk.CTkFont(family="Segoe UI", size=16),
                text_color=COLORS["text_secondary"]
            ).pack()
            
            if not search_term:
                ctk.CTkLabel(
                    empty_frame,
                    text="Go to 'Registration' to add students",
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    text_color=COLORS["text_secondary"]
                ).pack(pady=(5, 0))
            return

        # Headers with separate # column
        headers = [("#", "center"), ("Student ID", "w"), ("Full Name", "w"), ("Class", "center"), ("Actions", "center")]
        for col, (header, anchor) in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.students_list_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"],
                anchor=anchor
            )
            lbl.grid(row=0, column=col, padx=15, pady=15, sticky="ew")

        for i, student in enumerate(students, start=1):
            # Row number
            ctk.CTkLabel(
                self.students_list_frame,
                text=str(i),
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_secondary"],
                anchor="center"
            ).grid(row=i, column=0, padx=15, pady=12)
            
            # Student ID
            ctk.CTkLabel(
                self.students_list_frame,
                text=student.student_id,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).grid(row=i, column=1, padx=15, pady=12, sticky="ew")

            ctk.CTkLabel(
                self.students_list_frame,
                text=student.name,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).grid(row=i, column=2, padx=15, pady=12, sticky="ew")

            # Class badge
            class_badge = ctk.CTkLabel(
                self.students_list_frame,
                text=student.class_name,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLORS["text_primary"],
                fg_color=COLORS["primary"],
                corner_radius=6,
                width=65,
                height=28
            )
            class_badge.grid(row=i, column=3, padx=15, pady=12)

            # Actions frame
            actions_frame = ctk.CTkFrame(self.students_list_frame, fg_color="transparent")
            actions_frame.grid(row=i, column=4, padx=15, pady=12)

            ctk.CTkButton(
                actions_frame,
                text=TextLabelManager.get_button_text('view'),
                command=lambda s=student.id: self.open_student_modal(s),
                width=80,
                height=32,
                corner_radius=8,
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                font=ctk.CTkFont(family="Segoe UI", size=12)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                actions_frame,
                text=TextLabelManager.get_button_text('edit'),
                command=lambda s=student.id: self.edit_student(s),
                width=60,
                height=32,
                corner_radius=8,
                fg_color=COLORS["warning"],
                hover_color="#e0a800",
                font=ctk.CTkFont(family="Segoe UI", size=12)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                actions_frame,
                text=TextLabelManager.get_button_text('delete'),
                command=lambda s=student.id, n=student.name: self.delete_student(s, n),
                width=60,
                height=32,
                corner_radius=8,
                fg_color=COLORS["danger"],
                hover_color="#c9302c",
                font=ctk.CTkFont(family="Segoe UI", size=12)
            ).pack(side="left", padx=4)

    def open_student_modal(self, student_id):
        """Open student detail modal instead of inline details."""
        self.modal_controller.open_student_detail_modal(student_id, self.session)

    def delete_student(self, student_id, student_name):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{student_name}'?\n\nThis will also delete all their attendance records, marks, and fee records.",
            icon="warning"
        )
        if confirm:
            try:
                student = self.session.query(Student).filter_by(id=student_id).first()
                if student:
                    # Delete related records
                    self.session.query(Attendance).filter_by(student_id=student_id).delete()
                    self.session.query(Mark).filter_by(student_id=student_id).delete()
                    self.session.query(Fee).filter_by(student_id=student_id).delete()
                    self.session.delete(student)
                    self.session.commit()
                    messagebox.showinfo("Deleted", f"Student '{student_name}' has been deleted.")
                    self.load_students()
                    if self.on_student_deleted_callback:
                        self.on_student_deleted_callback()
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("Error", f"Failed to delete student: {str(e)}")

    def edit_student(self, student_id):
        """Open comprehensive edit dialog for a student with all fields."""
        student = self.session.query(Student).filter_by(id=student_id).first()
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        # Get the root window for modal
        root_window = self
        while hasattr(root_window, 'master') and root_window.master:
            root_window = root_window.master
        
        # Reduce window height to fit screen better
        screen_height = root_window.winfo_screenheight()
        window_height = min(700, int(screen_height * 0.85))  # 85% of screen or 700px max
        
        # Create edit modal
        edit_modal = ctk.CTkToplevel(root_window)
        edit_modal.title(f"Edit Student - {student.student_id}")
        edit_modal.geometry(f"700x{window_height}")
        edit_modal.transient(root_window)
        
        # Center the modal
        x = root_window.winfo_rootx() + (root_window.winfo_width() // 2) - 350
        y = root_window.winfo_rooty() + (root_window.winfo_height() // 2) - (window_height // 2)
        edit_modal.geometry(f"700x{window_height}+{x}+{y}")
        
        edit_modal.configure(fg_color=COLORS["bg_card"])
        edit_modal.update_idletasks()
        edit_modal.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(edit_modal, fg_color=COLORS["primary"], corner_radius=0)
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="Edit Student Details",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=15)
        
        # Scrollable form
        form_scroll = ctk.CTkScrollableFrame(
            edit_modal,
            fg_color="transparent"
        )
        form_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Student ID (read-only)
        self.create_edit_field(form_scroll, "Student ID", student.student_id, readonly=True)
        
        # Personal Information Section
        self.create_section_header(form_scroll, "Personal Information")
        
        full_name_entry = self.create_edit_field(form_scroll, "Full Name *", student.full_name)
        
        # Date of Birth
        from tkcalendar import DateEntry
        from datetime import datetime
        dob_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        dob_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            dob_frame,
            text="Date of Birth *",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        dob_picker = DateEntry(
            dob_frame,
            width=20,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 11),
            year=student.date_of_birth.year,
            month=student.date_of_birth.month,
            day=student.date_of_birth.day
        )
        dob_picker.pack(side="left")
        
        # Sex
        sex_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        sex_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            sex_frame,
            text="Sex *",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        sex_var = ctk.StringVar(value=student.sex)
        sex_combo = ctk.CTkComboBox(
            sex_frame,
            variable=sex_var,
            values=["Male", "Female"],
            width=300,
            height=35
        )
        sex_combo.pack(side="left")
        
        # Class
        class_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        class_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            class_frame,
            text="Class *",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        class_var = ctk.StringVar(value=student.class_name)
        class_combo = ctk.CTkComboBox(
            class_frame,
            variable=class_var,
            values=["SSS1", "SSS2", "SSS3"],
            width=300,
            height=35
        )
        class_combo.pack(side="left")
        
        # Admission Year
        admission_year_entry = self.create_edit_field(form_scroll, "Admission Year *", str(student.admission_year))
        
        # State of Origin
        state_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        state_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            state_frame,
            text="State of Origin *",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        nigerian_states = [
            "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
            "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
            "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
            "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara", "FCT"
        ]
        
        state_var = ctk.StringVar(value=student.state_of_origin)
        state_combo = ctk.CTkComboBox(
            state_frame,
            variable=state_var,
            values=nigerian_states,
            width=300,
            height=35
        )
        state_combo.pack(side="left")
        
        # Contact Information Section
        self.create_section_header(form_scroll, "Contact Information")
        
        home_address_text = self.create_edit_textbox(form_scroll, "Home Address *", student.home_address)
        phone_entry = self.create_edit_field(form_scroll, "Phone Number", student.phone_number or "")
        
        # Guardian Information Section
        self.create_section_header(form_scroll, "Guardian/Parent Information")
        
        guardian_name_entry = self.create_edit_field(form_scroll, "Guardian Name *", student.guardian_name)
        guardian_phone_entry = self.create_edit_field(form_scroll, "Guardian Phone *", student.guardian_phone)
        guardian_address_text = self.create_edit_textbox(form_scroll, "Guardian Address *", student.guardian_address)
        
        # Buttons
        btn_frame = ctk.CTkFrame(edit_modal, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def save_all_changes():
            """Save all edited student information."""
            # Get all values
            new_name = full_name_entry.get().strip()
            new_dob = dob_picker.get_date()
            new_sex = sex_var.get()
            new_class = class_var.get()
            new_admission_year = admission_year_entry.get().strip()
            new_state = state_var.get()
            new_home_address = home_address_text.get("1.0", "end-1c").strip()
            new_phone = phone_entry.get().strip()
            new_guardian_name = guardian_name_entry.get().strip()
            new_guardian_phone = guardian_phone_entry.get().strip()
            new_guardian_address = guardian_address_text.get("1.0", "end-1c").strip()
            
            # Validation
            if not new_name or len(new_name.split()) < 2:
                messagebox.showerror("Error", "Please enter a valid full name (at least 2 names)")
                return
            
            if not new_admission_year.isdigit():
                messagebox.showerror("Error", "Admission year must be a valid year")
                return
            
            if not new_state:
                messagebox.showerror("Error", "Please select a state of origin")
                return
            
            if not new_home_address:
                messagebox.showerror("Error", "Home address is required")
                return
            
            if not new_guardian_name:
                messagebox.showerror("Error", "Guardian name is required")
                return
            
            if not new_guardian_phone:
                messagebox.showerror("Error", "Guardian phone is required")
                return
            
            if not new_guardian_address:
                messagebox.showerror("Error", "Guardian address is required")
                return
            
            try:
                # Calculate age
                from datetime import date as dt_date
                today = dt_date.today()
                age = today.year - new_dob.year - ((today.month, today.day) < (new_dob.month, new_dob.day))
                
                # Update student
                student.full_name = new_name
                student.date_of_birth = new_dob
                student.age = age
                student.sex = new_sex
                student.class_name = new_class
                student.admission_year = int(new_admission_year)
                student.state_of_origin = new_state
                student.home_address = new_home_address
                student.phone_number = new_phone if new_phone else None
                student.guardian_name = new_guardian_name
                student.guardian_phone = new_guardian_phone
                student.guardian_address = new_guardian_address
                
                self.session.commit()
                messagebox.showinfo("Success", f"Student '{new_name}' updated successfully!")
                edit_modal.destroy()
                self.load_students()
                if self.on_student_deleted_callback:
                    self.on_student_deleted_callback()
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("Error", f"Failed to update student: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save All Changes",
            command=save_all_changes,
            width=180,
            height=45,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=edit_modal.destroy,
            width=120,
            height=45,
            corner_radius=8,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["danger"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left", padx=10)
        
        # Bind ESC to close
        edit_modal.bind("<Escape>", lambda e: edit_modal.destroy())
    
    def create_section_header(self, parent, text):
        """Create a section header in the edit form."""
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["primary"],
            anchor="w"
        ).pack(fill="x", pady=(15, 10), padx=5)
    
    def create_edit_field(self, parent, label, value="", readonly=False):
        """Create a labeled entry field."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        entry = ctk.CTkEntry(
            frame,
            width=400,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        entry.pack(side="left")
        
        if value:
            entry.insert(0, value)
        
        if readonly:
            entry.configure(state="readonly", fg_color=COLORS["border"])
        
        return entry
    
    def create_edit_textbox(self, parent, label, value=""):
        """Create a labeled textbox field."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="nw"
        ).pack(side="left", padx=(0, 10), anchor="n")
        
        textbox = ctk.CTkTextbox(
            frame,
            width=400,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        textbox.pack(side="left")
        
        if value:
            textbox.insert("1.0", value)
        
        return textbox


class SchoolFeesTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Header control frame
        control_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        control_frame.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(
            control_frame,
            text=TextLabelManager.get_header_text('fees'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        # Filters frame
        filters_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        filters_frame.pack(side="right", padx=20, pady=15)

        ctk.CTkLabel(
            filters_frame,
            text="Class:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        self.class_filter = ctk.CTkComboBox(
            filters_frame,
            values=["SSS1", "SSS2", "SSS3"],
            width=100,
            height=36,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.class_filter.pack(side="left", padx=5)

        ctk.CTkLabel(
            filters_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(20, 8))

        self.term_filter = ctk.CTkComboBox(
            filters_frame,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=150,
            height=36,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.term_filter.pack(side="left", padx=5)

        ctk.CTkButton(
            filters_frame,
            text=TextLabelManager.get_button_text('load') + " Fees",
            command=self.load_fees,
            width=110,
            height=36,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(20, 0))

        # Fees list
        self.fees_list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        self.fees_list_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # Configure columns
        for i in range(7):
            self.fees_list_frame.grid_columnconfigure(i, weight=1)

    def load_fees(self):
        for widget in self.fees_list_frame.winfo_children():
            widget.destroy()

        class_name = self.class_filter.get()
        term_value = self.term_filter.get()
        term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)

        students = self.session.query(Student).filter_by(class_name=class_name).order_by(Student.full_name).all()

        # Empty state
        if not students:
            empty_frame = ctk.CTkFrame(self.fees_list_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, columnspan=7, pady=60)
            
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
            return

        headers = ["Student", "Amount Due", "Set Due", "Amount Paid", "Balance", "Status", "Update Payment"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.fees_list_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=col, padx=10, pady=15, sticky="w")

        for i, student in enumerate(students, start=1):
            fee = self.session.query(Fee).filter_by(student_id=student.id, term=term).first()
            if not fee:
                fee = Fee(student_id=student.id, term=term, amount_due=0, amount_paid=0)
                self.session.add(fee)
                self.session.commit()

            balance = fee.amount_due - fee.amount_paid
            is_paid = balance <= 0
            status_text = TextLabelManager.get_status_text('paid') if is_paid else (TextLabelManager.get_status_text('partial') if fee.amount_paid > 0 else TextLabelManager.get_status_text('unpaid'))
            status_color = COLORS["success"] if is_paid else (COLORS["warning"] if fee.amount_paid > 0 else COLORS["danger"])

            # Student name
            ctk.CTkLabel(
                self.fees_list_frame,
                text=student.name,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"]
            ).grid(row=i, column=0, padx=10, pady=12, sticky="w")

            # Amount Due
            ctk.CTkLabel(
                self.fees_list_frame,
                text=f"₦{fee.amount_due:,.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"]
            ).grid(row=i, column=1, padx=10, pady=12, sticky="w")

            # Set Due Amount Entry + Button
            due_frame = ctk.CTkFrame(self.fees_list_frame, fg_color="transparent")
            due_frame.grid(row=i, column=2, padx=5, pady=12, sticky="w")

            due_entry = ctk.CTkEntry(
                due_frame,
                placeholder_text="Set due",
                width=80,
                height=32,
                corner_radius=6,
                border_width=1,
                border_color=COLORS["border"],
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            due_entry.pack(side="left", padx=2)

            ctk.CTkButton(
                due_frame,
                text=TextLabelManager.get_button_text('set'),
                command=lambda s=student.id, t=term, e=due_entry: self.set_due_amount(s, t, e.get()),
                width=40,
                height=32,
                corner_radius=6,
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                font=ctk.CTkFont(family="Segoe UI", size=11)
            ).pack(side="left", padx=2)

            # Amount Paid
            ctk.CTkLabel(
                self.fees_list_frame,
                text=f"₦{fee.amount_paid:,.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["success"] if fee.amount_paid > 0 else COLORS["text_secondary"]
            ).grid(row=i, column=3, padx=10, pady=12, sticky="w")

            # Balance
            ctk.CTkLabel(
                self.fees_list_frame,
                text=f"₦{balance:,.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["danger"] if balance > 0 else COLORS["success"]
            ).grid(row=i, column=4, padx=10, pady=12, sticky="w")

            # Status
            ctk.CTkLabel(
                self.fees_list_frame,
                text=status_text,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=status_color
            ).grid(row=i, column=5, padx=10, pady=12, sticky="w")

            # Update Payment Entry + Button
            payment_frame = ctk.CTkFrame(self.fees_list_frame, fg_color="transparent")
            payment_frame.grid(row=i, column=6, padx=5, pady=12, sticky="w")

            entry = ctk.CTkEntry(
                payment_frame,
                placeholder_text="Amount",
                width=90,
                height=32,
                corner_radius=6,
                border_width=1,
                border_color=COLORS["border"],
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            entry.pack(side="left", padx=2)

            ctk.CTkButton(
                payment_frame,
                text=TextLabelManager.get_button_text('pay'),
                command=lambda s=student.id, t=term, e=entry: self.update_fee(s, t, e.get()),
                width=60,
                height=32,
                corner_radius=6,
                fg_color=COLORS["success"],
                hover_color="#2d8f47",
                font=ctk.CTkFont(family="Segoe UI", size=12)
            ).pack(side="left", padx=2)

    def set_due_amount(self, student_id, term, amount_str):
        try:
            amount = float(amount_str)
            if amount < 0:
                messagebox.showerror("Error", "Amount cannot be negative.")
                return
            fee = self.session.query(Fee).filter_by(student_id=student_id, term=term).one()
            fee.amount_due = amount
            self.session.commit()
            messagebox.showinfo("Success", "Fee amount due updated successfully.")
            self.load_fees()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_fee(self, student_id, term, amount_str):
        try:
            amount = float(amount_str)
            if amount < 0:
                messagebox.showerror("Error", "Amount cannot be negative.")
                return
            fee = self.session.query(Fee).filter_by(student_id=student_id, term=term).one()
            fee.amount_paid += amount  # Add to existing paid amount
            self.session.commit()
            messagebox.showinfo("Success", f"Payment of ₦{amount:,.2f} recorded successfully.")
            self.load_fees()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")


class AdminSettingsTab(ctk.CTkFrame):
    """Admin settings tab for managing login credentials."""
    
    def __init__(self, parent, session, current_admin=None):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.current_admin = current_admin
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            header_frame,
            text="⚙ Admin Settings",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(padx=20, pady=15, anchor="w")
        
        # Main content with scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # SECTION 1: UPDATE PASSWORD
        self.setup_update_password_section()
        
        # SECTION 2: REGISTER NEW ADMIN
        self.setup_register_admin_section()

    def setup_update_password_section(self):
        update_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        update_frame.grid(row=0, column=0, padx=5, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            update_frame,
            text="Update My Password",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=30, pady=(20, 5))
        
        ctk.CTkLabel(
            update_frame,
            text="Change your current login password.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30, pady=(0, 20))
        
        # Current User (Read-only)
        username = self.current_admin.username if self.current_admin else "Unknown"
        self.create_field(update_frame, "Username:", username, readonly=True)
        
        self.update_current_pw = self.create_field(update_frame, "Current Password:", placeholder="Enter current password", is_password=True)
        self.update_new_pw = self.create_field(update_frame, "New Password:", placeholder="Enter new password", is_password=True)
        self.update_confirm_pw = self.create_field(update_frame, "Confirm Password:", placeholder="Confirm new password", is_password=True)
        
        btn_frame = ctk.CTkFrame(update_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(10, 25))
        
        ctk.CTkButton(
            btn_frame,
            text="Update Password",
            command=self.handle_update_password,
            width=160,
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(side="left")

    def setup_register_admin_section(self):
        register_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        register_frame.grid(row=1, column=0, padx=5, pady=0, sticky="ew")
        
        ctk.CTkLabel(
            register_frame,
            text="Register New Admin",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=30, pady=(20, 5))
        
        ctk.CTkLabel(
            register_frame,
            text="Add a new administrator to the system.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30, pady=(0, 20))
        
        self.reg_username = self.create_field(register_frame, "New Username:", placeholder="Enter email/username")
        self.reg_password = self.create_field(register_frame, "Password:", placeholder="Enter password", is_password=True)
        self.reg_confirm = self.create_field(register_frame, "Confirm Password:", placeholder="Confirm password", is_password=True)
        
        btn_frame = ctk.CTkFrame(register_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(10, 25))
        
        ctk.CTkButton(
            btn_frame,
            text="Create Admin Account",
            command=self.handle_create_admin,
            width=200,
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(side="left")

    def create_field(self, parent, label_text, value="", placeholder="", is_password=False, readonly=False):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_primary"],
            width=140,
            anchor="w"
        ).pack(side="left")
        
        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            width=350,
            height=38,
            corner_radius=8,
            show="●" if is_password else "",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        if value:
            entry.insert(0, value)
        if readonly:
            entry.configure(state="readonly", fg_color=COLORS["bg_card"], border_width=0)
        
        entry.pack(side="left", padx=10)
        return entry

    def handle_update_password(self):
        """Update current admin password."""
        import hashlib
        from models import Admin
        
        if not self.current_admin:
            messagebox.showerror("Error", "No logged-in admin found.")
            return

        current_password = self.update_current_pw.get()
        new_password = self.update_new_pw.get()
        confirm_password = self.update_confirm_pw.get()
        
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "All password fields are required.")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match.")
            return
        
        if len(new_password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters.")
            return
        
        try:
            # Refresh admin object from session
            admin = self.session.query(Admin).filter_by(id=self.current_admin.id).first()
            
            # Verify current password
            current_hash = hashlib.sha256(current_password.encode()).hexdigest()
            if admin.password_hash != current_hash:
                messagebox.showerror("Error", "Incorrect current password.")
                return
            
            # Update password
            admin.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            self.session.commit()
            
            messagebox.showinfo("Success", "Your password has been updated successfully!")
            
            # Clear fields
            self.update_current_pw.delete(0, 'end')
            self.update_new_pw.delete(0, 'end')
            self.update_confirm_pw.delete(0, 'end')
            
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to update password: {str(e)}")

    def handle_create_admin(self):
        """Register a new admin account."""
        import hashlib
        from datetime import datetime
        from models import Admin
        
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters.")
            return
        
        try:
            # Check if admin already exists
            existing = self.session.query(Admin).filter_by(username=username).first()
            if existing:
                messagebox.showerror("Error", f"Administrator '{username}' already exists.")
                return
            
            # Create password hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Create new admin
            new_admin = Admin(
                username=username,
                password_hash=password_hash,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_active=True
            )
            self.session.add(new_admin)
            self.session.commit()
            
            messagebox.showinfo("Success", f"New administrator '{username}' created successfully!")
            
            # Clear fields
            self.reg_username.delete(0, 'end')
            self.reg_password.delete(0, 'end')
            self.reg_confirm.delete(0, 'end')
            
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to register admin: {str(e)}")


class EnterpriseSchoolManagementApp:
    def __init__(self, root, current_admin=None):
        self.root = root
        self.current_admin = current_admin
        self.root.title("GFA Admin Panel")
        self.session = Session()

        # Configure grid layout (1x2)
        self.root.grid_columnconfigure(0, minsize=220)  # Sidebar fixed width
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_frames()

        # Select default frame
        self.select_frame_by_name("Student Registration")

    def setup_sidebar(self):
        self.navigation_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=COLORS["bg_dark"], width=220)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_propagate(False)  # Fix sidebar width
        self.navigation_frame.grid_rowconfigure(11, weight=1)  # Updated for Settings row

        # Logo/Title
        logo_frame = ctk.CTkFrame(self.navigation_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=15, pady=(25, 35), sticky="ew")

        # Try to load the app icon
        try:
            import os
            from PIL import Image
            # Try both possible icon files
            icon_path = None
            if os.path.exists("app_icon.png"):
                icon_path = "app_icon.png"
            elif os.path.exists("icon.jpg.jpeg"):
                icon_path = "icon.jpg.jpeg"
            elif os.path.exists("icon.jpg"):
                icon_path = "icon.jpg"
            
            if icon_path:
                # Load and resize the icon for sidebar
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((40, 40), Image.Resampling.LANCZOS)
                icon_photo = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(40, 40))
                
                ctk.CTkLabel(
                    logo_frame,
                    image=icon_photo,
                    text=""
                ).pack(side="left", padx=(0, 12))
            else:
                # Fallback to text if no icon found
                ctk.CTkLabel(
                    logo_frame,
                    text="SMS",
                    font=ctk.CTkFont(size=36, weight="bold")
                ).pack(side="left")
        except ImportError:
            # Fallback if PIL is not available
            ctk.CTkLabel(
                logo_frame,
                text="SMS",
                font=ctk.CTkFont(size=36, weight="bold")
            ).pack(side="left")
        except Exception:
            # Fallback for any other error
            ctk.CTkLabel(
                logo_frame,
                text="SMS",
                font=ctk.CTkFont(size=36, weight="bold")
            ).pack(side="left")

        ctk.CTkLabel(
            logo_frame,
            text="GFA Admin Panel",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=12)

        # Navigation buttons with consistent text labels
        nav_items = [
            (TextLabelManager.get_nav_text('register'), "Student Registration", 1),
            (TextLabelManager.get_nav_text('students'), "Students List", 2),
            (TextLabelManager.get_nav_text('fees'), "School Fees", 3),
            (TextLabelManager.get_nav_text('marks'), "Grades Entry", 4),
            (TextLabelManager.get_nav_text('broadsheet'), "Broadsheet", 5),
            (TextLabelManager.get_nav_text('attendance'), "Attendance", 6),
            ("Sessions", "Sessions", 7),
            ("Departments", "Departments", 8),
        ]

        self.nav_buttons = {}
        for text, name, row in nav_items:
            btn = ctk.CTkButton(
                self.navigation_frame,
                corner_radius=8,
                height=46,
                border_spacing=14,
                text=text,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card"],
                anchor="center",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                command=lambda n=name: self.select_frame_by_name(n)
            )
            btn.grid(row=row, column=0, sticky="ew", padx=10, pady=3)
            self.nav_buttons[name] = btn

        # Separator before settings
        separator = ctk.CTkFrame(self.navigation_frame, fg_color=COLORS["border"], height=1)
        separator.grid(row=9, column=0, sticky="ew", padx=20, pady=20)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            self.navigation_frame,
            corner_radius=8,
            height=46,
            border_spacing=14,
            text="Settings",
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card"],
            anchor="center",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            command=lambda: self.select_frame_by_name("Admin Settings")
        )
        settings_btn.grid(row=10, column=0, sticky="ew", padx=10, pady=3)
        self.nav_buttons["Admin Settings"] = settings_btn
        
        # Logout button
        logout_btn = ctk.CTkButton(
            self.navigation_frame,
            corner_radius=8,
            height=46,
            border_spacing=14,
            text="Logout",
            fg_color=COLORS["danger"],
            text_color=COLORS["text_primary"],
            hover_color="#c9302c",
            anchor="center",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self.logout
        )
        logout_btn.grid(row=11, column=0, sticky="ew", padx=10, pady=(10, 3))

    def setup_main_frames(self):
        from forms import MarksEntryTab, BroadsheetTab, AttendanceTab
        from enhanced_registration import EnhancedStudentRegistrationTab
        from sessions_tab import SessionsTab
        from departments_tab import DepartmentsTab

        self.students_list_frame = StudentsListTab(self.root, self.session, on_student_deleted_callback=self.refresh_data)
        self.school_fees_frame = SchoolFeesTab(self.root, self.session)
        self.registration_frame = EnhancedStudentRegistrationTab(self.root, self.session, on_student_added_callback=self.refresh_data)
        self.marks_frame = MarksEntryTab(self.root, self.session)
        self.broadsheet_frame = BroadsheetTab(self.root, self.session)
        self.attendance_frame = AttendanceTab(self.root, self.session)
        self.admin_settings_frame = AdminSettingsTab(self.root, self.session, self.current_admin)
        self.sessions_frame = SessionsTab(self.root)
        self.departments_frame = DepartmentsTab(self.root)

    def select_frame_by_name(self, name):
        # Update button styles
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=COLORS["primary"], text_color=COLORS["text_primary"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])

        # Frame mapping
        frames = {
            "Students List": self.students_list_frame,
            "School Fees": self.school_fees_frame,
            "Student Registration": self.registration_frame,
            "Grades Entry": self.marks_frame,
            "Broadsheet": self.broadsheet_frame,
            "Attendance": self.attendance_frame,
            "Admin Settings": self.admin_settings_frame,
            "Sessions": self.sessions_frame,
            "Departments": self.departments_frame,
        }

        # Show/hide frames
        for frame_name, frame in frames.items():
            if frame_name == name:
                frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            else:
                frame.grid_forget()

    def refresh_data(self):
        self.marks_frame.load_students()
        self.students_list_frame.load_students()
    
    def logout(self):
        """Logout and return to login screen."""
        confirm = messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to logout?",
            icon="question"
        )
        if confirm:
            # Close current window
            self.root.destroy()
            
            # Create new root window for login
            import tkinter as tk
            new_root = tk.Tk()
            
            # Import and show login window
            from main import LoginWindow
            def on_login_success(admin):
                new_root.destroy()
                root = tk.Tk()
                EnterpriseSchoolManagementApp(root, admin)
                root.mainloop()
            
            LoginWindow(new_root, on_login_success)
            new_root.mainloop()
