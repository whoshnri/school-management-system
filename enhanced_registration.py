"""
Enhanced Student Registration Form with comprehensive details
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError
from models import Session, Student
from datetime import date as dt_date, datetime
from tkcalendar import DateEntry
from ui_components import TextLabelManager

# Modern color palette
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


class EnhancedStudentRegistrationTab(ctk.CTkFrame):
    def __init__(self, parent, session, on_student_added_callback):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.on_student_added_callback = on_student_added_callback
        self.setup_ui()

    def calculate_age(self, dob):
        """Calculate age from date of birth."""
        today = dt_date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age

    def update_age_display(self, event=None):
        """Update age display when DOB changes."""
        try:
            dob = self.dob_picker.get_date()
            age = self.calculate_age(dob)
            self.age_display.configure(text=f"{age} years old")
        except:
            self.age_display.configure(text="-- years old")

    def update_student_id_preview(self, event=None):
        """Update student ID preview based on admission year."""
        try:
            year = self.admission_year_var.get()
            if year:
                year_suffix = year[-2:]  # Last 2 digits
                self.id_prefix_label.configure(text=f"GFA/{year_suffix}/J")
        except:
            pass

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

        # Scrollable Form Card
        form_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12
        )
        form_scroll.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        form_scroll.grid_columnconfigure(0, weight=1)
        form_scroll.grid_columnconfigure(1, weight=2)

        # Instructions
        ctk.CTkLabel(
            form_scroll,
            text="Complete all required fields (*) to register a new student",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, columnspan=2, padx=25, pady=(20, 15), sticky="w")

        row = 1

        # === SECTION 1: STUDENT ID & ADMISSION ===
        ctk.CTkLabel(
            form_scroll,
            text=" Student Identification ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).grid(row=row, column=0, columnspan=2, padx=25, pady=(15, 10), sticky="w")
        row += 1

        # Admission Year
        ctk.CTkLabel(
            form_scroll,
            text="Admission Year *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 10, current_year + 2)]
        
        self.admission_year_var = ctk.StringVar(value=str(current_year))
        self.admission_year_combo = ctk.CTkComboBox(
            form_scroll,
            variable=self.admission_year_var,
            values=years,
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            command=self.update_student_id_preview
        )
        self.admission_year_combo.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Student ID (Split into prefix and number)
        ctk.CTkLabel(
            form_scroll,
            text="Student ID *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        id_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        id_frame.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")

        # Prefix (disabled)
        year_suffix = str(current_year)[-2:]
        self.id_prefix_label = ctk.CTkLabel(
            id_frame,
            text=f"GFA/{year_suffix}/S",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["border"],
            corner_radius=10,
            width=120,
            height=45
        )
        self.id_prefix_label.pack(side="left", padx=(0, 5))

        # Number input
        self.id_number_entry = ctk.CTkEntry(
            id_frame,
            placeholder_text="001",
            width=100,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            justify="center"
        )
        self.id_number_entry.pack(side="left")

        ctk.CTkLabel(
            id_frame,
            text="(Enter 3-digit number)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(10, 0))
        row += 1
        
        # Student ID error label
        self.id_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.id_error_label.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        row += 1

        # === SECTION 2: PERSONAL INFORMATION ===
        ctk.CTkLabel(
            form_scroll,
            text=" Personal Information ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).grid(row=row, column=0, columnspan=2, padx=25, pady=(20, 10), sticky="w")
        row += 1

        # Full Name
        ctk.CTkLabel(
            form_scroll,
            text="Full Name *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.name_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="e.g. John Doe Smith",
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.name_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Full Name error label
        self.name_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.name_error_label.grid(row=row, column=1, padx=25, pady=(0, 10), sticky="w")
        row += 1

        # Date of Birth
        ctk.CTkLabel(
            form_scroll,
            text="Date of Birth *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        dob_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        dob_frame.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")

        self.dob_picker = DateEntry(
            dob_frame,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 12),
            maxdate=dt_date.today()
        )
        self.dob_picker.pack(side="left", padx=(0, 15))
        self.dob_picker.bind("<<DateEntrySelected>>", self.update_age_display)

        ctk.CTkLabel(
            dob_frame,
            text="Age:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 5))

        self.age_display = ctk.CTkLabel(
            dob_frame,
            text="-- years old",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["primary"]
        )
        self.age_display.pack(side="left")
        row += 1

        # Sex
        ctk.CTkLabel(
            form_scroll,
            text="Sex *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.sex_var = ctk.StringVar(value="Male")
        self.sex_combo = ctk.CTkComboBox(
            form_scroll,
            variable=self.sex_var,
            values=["Male", "Female"],
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.sex_combo.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Class
        ctk.CTkLabel(
            form_scroll,
            text="Class *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.class_var = ctk.StringVar(value="SSS1")
        self.class_combo = ctk.CTkComboBox(
            form_scroll,
            variable=self.class_var,
            values=["SSS1", "SSS2", "SSS3"],
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.class_combo.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # State of Origin
        ctk.CTkLabel(
            form_scroll,
            text="State of Origin *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        nigerian_states = [
            "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
            "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
            "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
            "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara", "FCT"
        ]
        
        self.state_var = ctk.StringVar()
        self.state_combo = ctk.CTkComboBox(
            form_scroll,
            variable=self.state_var,
            values=nigerian_states,
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.state_combo.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        
        # State error label
        self.state_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.state_error_label.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        row += 1

        # === SECTION 3: CONTACT INFORMATION ===
        ctk.CTkLabel(
            form_scroll,
            text=" Contact Information ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).grid(row=row, column=0, columnspan=2, padx=25, pady=(20, 10), sticky="w")
        row += 1

        # Home Address
        ctk.CTkLabel(
            form_scroll,
            text="Home Address *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.home_address_text = ctk.CTkTextbox(
            form_scroll,
            width=380,
            height=80,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.home_address_text.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        
        # Home Address error label
        self.home_address_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.home_address_error_label.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        row += 1

        # Phone Number
        ctk.CTkLabel(
            form_scroll,
            text="Phone Number",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.phone_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="e.g. 08012345678",
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.phone_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # === SECTION 4: GUARDIAN/PARENT INFORMATION ===
        ctk.CTkLabel(
            form_scroll,
            text=" Guardian/Parent Information ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).grid(row=row, column=0, columnspan=2, padx=25, pady=(20, 10), sticky="w")
        row += 1

        # Guardian Name
        ctk.CTkLabel(
            form_scroll,
            text="Guardian Name *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.guardian_name_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="e.g. Mr. John Doe",
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.guardian_name_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        
        # Guardian Name error label
        self.guardian_name_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.guardian_name_error_label.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        row += 1

        # Guardian Phone
        ctk.CTkLabel(
            form_scroll,
            text="Guardian Phone *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.guardian_phone_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="e.g. 08012345678",
            width=380,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.guardian_phone_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        
        # Guardian Phone error label
        self.guardian_phone_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.guardian_phone_error_label.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        row += 1

        # Guardian Address
        ctk.CTkLabel(
            form_scroll,
            text="Guardian Address *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

        self.guardian_address_text = ctk.CTkTextbox(
            form_scroll,
            width=380,
            height=80,
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.guardian_address_text.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        
        # Guardian Address error label
        self.guardian_address_error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["danger"]
        )
        self.guardian_address_error_label.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        row += 1

        # Submit Button
        button_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=30)

        self.add_btn = ctk.CTkButton(
            button_frame,
            text=TextLabelManager.get_button_text('register'),
            command=self.add_student,
            width=220,
            height=50,
            corner_radius=10,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.add_btn.pack()

        # Status message
        self.status_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["success"]
        )
        self.status_label.grid(row=row+1, column=0, columnspan=2, pady=(0, 20))

    def clear_all_errors(self):
        """Clear all error messages."""
        self.id_error_label.configure(text="")
        self.name_error_label.configure(text="")
        self.state_error_label.configure(text="")
        self.home_address_error_label.configure(text="")
        self.guardian_name_error_label.configure(text="")
        self.guardian_phone_error_label.configure(text="")
        self.guardian_address_error_label.configure(text="")
        self.status_label.configure(text="")

    def show_field_error(self, field_name, message):
        """Show error message under a specific field."""
        self.clear_all_errors()
        if field_name == "id":
            self.id_error_label.configure(text=f"✗ {message}")
        elif field_name == "name":
            self.name_error_label.configure(text=f"✗ {message}")
        elif field_name == "state":
            self.state_error_label.configure(text=f"✗ {message}")
        elif field_name == "home_address":
            self.home_address_error_label.configure(text=f"✗ {message}")
        elif field_name == "guardian_name":
            self.guardian_name_error_label.configure(text=f"✗ {message}")
        elif field_name == "guardian_phone":
            self.guardian_phone_error_label.configure(text=f"✗ {message}")
        elif field_name == "guardian_address":
            self.guardian_address_error_label.configure(text=f"✗ {message}")

    def add_student(self):
        # Clear all previous errors
        self.clear_all_errors()
        
        # Get all values
        admission_year = self.admission_year_var.get().strip()
        id_number = self.id_number_entry.get().strip()
        full_name = self.name_entry.get().strip()
        dob = self.dob_picker.get_date()
        sex = self.sex_var.get()
        class_name = self.class_var.get()
        state = self.state_var.get().strip()
        home_address = self.home_address_text.get("1.0", "end-1c").strip()
        phone = self.phone_entry.get().strip()
        guardian_name = self.guardian_name_entry.get().strip()
        guardian_phone = self.guardian_phone_entry.get().strip()
        guardian_address = self.guardian_address_text.get("1.0", "end-1c").strip()

        # Validation with field-specific errors
        if not id_number or not id_number.isdigit() or len(id_number) != 3:
            self.show_field_error("id", "Student ID number must be exactly 3 digits")
            self.id_number_entry.focus()
            return

        # Generate full student ID
        year_suffix = admission_year[-2:]
        student_id = f"GFA/{year_suffix}/S{id_number}"

        if not full_name:
            self.show_field_error("name", "Full name is required")
            self.name_entry.focus()
            return

        # Check for at least 2 names
        name_parts = full_name.split()
        if len(name_parts) < 2:
            self.show_field_error("name", "Please enter at least 2 names (First and Last name)")
            self.name_entry.focus()
            return

        if not state:
            self.show_field_error("state", "State of origin is required")
            self.state_combo.focus()
            return

        if not home_address:
            self.show_field_error("home_address", "Home address is required")
            self.home_address_text.focus()
            return

        if not guardian_name:
            self.show_field_error("guardian_name", "Guardian name is required")
            self.guardian_name_entry.focus()
            return

        if not guardian_phone:
            self.show_field_error("guardian_phone", "Guardian phone number is required")
            self.guardian_phone_entry.focus()
            return

        if not guardian_address:
            self.show_field_error("guardian_address", "Guardian address is required")
            self.guardian_address_text.focus()
            return

        try:
            # Calculate age
            age = self.calculate_age(dob)

            new_student = Student(
                student_id=student_id,
                full_name=full_name,
                date_of_birth=dob,
                age=age,
                sex=sex,
                class_name=class_name,
                admission_year=int(admission_year),
                state_of_origin=state,
                home_address=home_address,
                phone_number=phone if phone else None,
                guardian_name=guardian_name,
                guardian_phone=guardian_phone,
                guardian_address=guardian_address
            )
            
            self.session.add(new_student)
            self.session.commit()

            self.show_success(f"Student '{full_name}' registered successfully with ID: {student_id}")

            # Clear fields
            self.id_number_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
            self.home_address_text.delete("1.0", "end")
            self.phone_entry.delete(0, 'end')
            self.guardian_name_entry.delete(0, 'end')
            self.guardian_phone_entry.delete(0, 'end')
            self.guardian_address_text.delete("1.0", "end")
            
            self.id_number_entry.focus()

            if self.on_student_added_callback:
                self.on_student_added_callback()

        except IntegrityError:
            self.session.rollback()
            self.show_field_error("id", f"Student ID '{student_id}' already exists")
        except Exception as e:
            self.session.rollback()
            self.status_label.configure(text=f"Error: Failed to add student: {str(e)}", text_color=COLORS["danger"])

    def show_success(self, message):
        self.clear_all_errors()
        self.status_label.configure(text=f"✓ {message}", text_color=COLORS["success"])
