"""
Enhanced Student Registration Form — GFA Admin Panel
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError
from models import Session, Student, AcademicSession, Department
from datetime import date as dt_date, datetime
from tkcalendar import DateEntry
from ui_components import TextLabelManager

COLORS = {
    "primary":       "#1a73e8",
    "primary_hover": "#1557b0",
    "success":       "#34a853",
    "danger":        "#ea4335",
    "bg_main":       "#ffffff",
    "bg_card":       "#f8f9fa",
    "text_primary":  "#202124",
    "text_secondary":"#5f6368",
    "border":        "#dadce0",
}

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
    "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe",
    "Zamfara", "FCT"
]


class YearSpinner(ctk.CTkFrame):
    """Unbounded year spinner widget — no min/max limits."""

    def __init__(self, parent, initial_year: int, on_change=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._year = initial_year
        self._on_change = on_change

        ctk.CTkButton(self, text="▲", width=36, height=22,
                      fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
                      hover_color=COLORS["border"],
                      command=self._increment).pack(side="left", padx=(0, 4))

        self._label = ctk.CTkLabel(self, text=str(self._year), width=70,
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   text_color=COLORS["text_primary"])
        self._label.pack(side="left", padx=4)

        ctk.CTkButton(self, text="▼", width=36, height=22,
                      fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
                      hover_color=COLORS["border"],
                      command=self._decrement).pack(side="left", padx=(4, 0))

    def _increment(self):
        self._year += 1
        self._label.configure(text=str(self._year))
        if self._on_change:
            self._on_change(self._year)

    def _decrement(self):
        self._year -= 1
        self._label.configure(text=str(self._year))
        if self._on_change:
            self._on_change(self._year)

    def get(self) -> int:
        return self._year

    def set(self, year: int):
        self._year = year
        self._label.configure(text=str(year))


def next_admission_number(db_session, year_suffix: str) -> str:
    """Return next 4-digit zero-padded sequential number for a given YY prefix."""
    prefix = f"GFA/{year_suffix}/S"
    existing = db_session.query(Student.student_id).filter(
        Student.student_id.like(f"{prefix}%")
    ).all()
    max_num = 0
    for (sid,) in existing:
        try:
            num = int(sid[len(prefix):])
            max_num = max(max_num, num)
        except ValueError:
            pass
    return f"{max_num + 1:04d}"


class EnhancedStudentRegistrationTab(ctk.CTkFrame):
    def __init__(self, parent, session, on_student_added_callback):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.on_student_added_callback = on_student_added_callback
        self._phone_valid = {"phone": True, "guardian_phone": True}
        self.setup_ui()

    # ------------------------------------------------------------------ helpers
    def calculate_age(self, dob):
        today = dt_date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def update_age_display(self, event=None):
        try:
            age = self.calculate_age(self.dob_picker.get_date())
            self.age_display.configure(text=f"{age} years old")
        except Exception:
            self.age_display.configure(text="-- years old")

    def _on_year_change(self, year: int):
        yy = str(year)[-2:]
        self.id_prefix_label.configure(text=f"GFA/{yy}/S")
        self._refresh_id_preview()

    def _on_session_change(self, session_name: str):
        """Update ID prefix when session selection changes."""
        try:
            yy = session_name[2:4]  # e.g. "2024/2025" -> "24"
            self.id_prefix_label.configure(text=f"GFA/{yy}/S")
            self._refresh_id_preview()
        except Exception:
            pass

    def _refresh_id_preview(self):
        """Auto-fill the ID number field with next available number."""
        try:
            prefix_text = self.id_prefix_label.cget("text")  # e.g. "GFA/24/S"
            yy = prefix_text.split("/")[1]
            next_num = next_admission_number(self.session, yy)
            self.id_number_entry.configure(state="normal")
            self.id_number_entry.delete(0, "end")
            self.id_number_entry.insert(0, next_num)
        except Exception:
            pass

    def _validate_phone(self, field: str, *_):
        value = self._phone_vars[field].get()
        err_label = self.phone_error_label if field == "phone" else self.guardian_phone_error_label
        if len(value) > 11:
            err_label.configure(text="Value is not allowed")
            self._phone_valid[field] = False
        else:
            err_label.configure(text="")
            self._phone_valid[field] = True

    def _bind_tab_order(self):
        """Bind Shift+Tab for backwards navigation."""
        order = [
            self.name_entry,
            self.id_number_entry,
            self.phone_entry,
            self.guardian_name_entry,
            self.guardian_phone_entry,
        ]
        for i, widget in enumerate(order):
            prev = order[i - 1]
            widget.bind("<Shift-Tab>", lambda e, p=prev: (p.focus_set(), "break"))

    # ------------------------------------------------------------------ UI
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(
            header_frame,
            text="Student Registration",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(padx=20, pady=15, anchor="w")

        # Scrollable form
        form_scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_card"], corner_radius=12
        )
        form_scroll.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        form_scroll.grid_columnconfigure(0, weight=1)
        form_scroll.grid_columnconfigure(1, weight=2)

        ctk.CTkLabel(
            form_scroll,
            text="Complete all required fields (*) to register a new student",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, columnspan=2, padx=25, pady=(20, 15), sticky="w")

        row = 1

        # ---- Section: Student Identification ----
        self._section(form_scroll, "Student Identification", row); row += 1

        # Session selector
        self._label(form_scroll, "Academic Session *", row)
        sessions = self.session.query(AcademicSession).order_by(AcademicSession.name.desc()).all()
        session_names = [s.name for s in sessions] or ["No sessions — add one in Sessions tab"]
        active = self.session.query(AcademicSession).filter_by(is_active=True).first()
        default_session = active.name if active else (session_names[0] if sessions else "")

        self.session_var = ctk.StringVar(value=default_session)
        self.session_combo = ctk.CTkComboBox(
            form_scroll, variable=self.session_var, values=session_names,
            width=380, height=45, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=14),
            command=self._on_session_change
        )
        self.session_combo.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Year spinner (for manual override / standalone use)
        self._label(form_scroll, "Admission Year *", row)
        current_year = datetime.now().year
        self.year_spinner = YearSpinner(
            form_scroll, initial_year=current_year,
            on_change=self._on_year_change
        )
        self.year_spinner.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Student ID
        self._label(form_scroll, "Student ID *", row)
        id_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        id_frame.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")

        yy = str(current_year)[-2:]
        self.id_prefix_label = ctk.CTkLabel(
            id_frame, text=f"GFA/{yy}/S",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["border"], corner_radius=10,
            width=120, height=45
        )
        self.id_prefix_label.pack(side="left", padx=(0, 5))

        self.id_number_entry = ctk.CTkEntry(
            id_frame, placeholder_text="0001",
            width=100, height=45, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=14), justify="center"
        )
        self.id_number_entry.pack(side="left")
        ctk.CTkLabel(id_frame, text="(auto-filled)",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(8, 0))
        row += 1

        self.id_error_label = self._error_label(form_scroll, row); row += 1

        # ---- Section: Personal Information ----
        self._section(form_scroll, "Personal Information", row); row += 1

        # Full Name
        self._label(form_scroll, "Full Name *", row)
        self.name_entry = ctk.CTkEntry(
            form_scroll, placeholder_text="e.g. John Doe Smith",
            width=380, height=45, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.name_error_label = self._error_label(form_scroll, row); row += 1

        # Date of Birth
        self._label(form_scroll, "Date of Birth *", row)
        dob_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        dob_frame.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        self.dob_picker = DateEntry(
            dob_frame, width=15, background='darkblue', foreground='white',
            borderwidth=2, date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 12), maxdate=dt_date.today()
        )
        self.dob_picker.pack(side="left", padx=(0, 15))
        self.dob_picker.bind("<<DateEntrySelected>>", self.update_age_display)
        ctk.CTkLabel(dob_frame, text="Age:", font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.age_display = ctk.CTkLabel(dob_frame, text="-- years old",
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        text_color=COLORS["primary"])
        self.age_display.pack(side="left")
        row += 1

        # Sex
        self._label(form_scroll, "Sex *", row)
        self.sex_var = ctk.StringVar(value="Male")
        ctk.CTkComboBox(form_scroll, variable=self.sex_var, values=["Male", "Female"],
                        width=380, height=45, corner_radius=10,
                        border_width=1, border_color=COLORS["border"],
                        font=ctk.CTkFont(size=14)
                        ).grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Class
        self._label(form_scroll, "Class *", row)
        self.class_var = ctk.StringVar(value="SSS1")
        ctk.CTkComboBox(form_scroll, variable=self.class_var,
                        values=["SSS1", "SSS2", "SSS3"],
                        width=380, height=45, corner_radius=10,
                        border_width=1, border_color=COLORS["border"],
                        font=ctk.CTkFont(size=14)
                        ).grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # Department
        self._label(form_scroll, "Department *", row)
        self.dept_var = ctk.StringVar(value="Science")
        ctk.CTkComboBox(form_scroll, variable=self.dept_var,
                        values=["Science", "Art", "Commercial"],
                        width=380, height=45, corner_radius=10,
                        border_width=1, border_color=COLORS["border"],
                        font=ctk.CTkFont(size=14)
                        ).grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1

        # State of Origin
        self._label(form_scroll, "State of Origin *", row)
        self.state_var = ctk.StringVar()
        ctk.CTkComboBox(form_scroll, variable=self.state_var, values=NIGERIAN_STATES,
                        width=380, height=45, corner_radius=10,
                        border_width=1, border_color=COLORS["border"],
                        font=ctk.CTkFont(size=14)
                        ).grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.state_error_label = self._error_label(form_scroll, row); row += 1

        # ---- Section: Contact Information ----
        self._section(form_scroll, "Contact Information", row); row += 1

        # Home Address
        self._label(form_scroll, "Home Address *", row)
        self.home_address_text = ctk.CTkTextbox(
            form_scroll, width=380, height=80, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=13)
        )
        self.home_address_text.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.home_address_error_label = self._error_label(form_scroll, row); row += 1

        # Phone Number
        self._label(form_scroll, "Phone Number", row)
        self._phone_vars = {}
        self._phone_vars["phone"] = ctk.StringVar()
        self.phone_entry = ctk.CTkEntry(
            form_scroll, textvariable=self._phone_vars["phone"],
            placeholder_text="e.g. 08012345678",
            width=380, height=45, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=14)
        )
        self.phone_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.phone_error_label = self._error_label(form_scroll, row); row += 1
        self._phone_vars["phone"].trace_add("write",
            lambda *a: self._validate_phone("phone"))

        # ---- Section: Guardian/Parent Information ----
        self._section(form_scroll, "Guardian/Parent Information", row); row += 1

        # Guardian Name
        self._label(form_scroll, "Guardian Name *", row)
        self.guardian_name_entry = ctk.CTkEntry(
            form_scroll, placeholder_text="e.g. Mr. John Doe",
            width=380, height=45, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=14)
        )
        self.guardian_name_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.guardian_name_error_label = self._error_label(form_scroll, row); row += 1

        # Guardian Phone
        self._label(form_scroll, "Guardian Phone *", row)
        self._phone_vars["guardian_phone"] = ctk.StringVar()
        self.guardian_phone_entry = ctk.CTkEntry(
            form_scroll, textvariable=self._phone_vars["guardian_phone"],
            placeholder_text="e.g. 08012345678",
            width=380, height=45, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=14)
        )
        self.guardian_phone_entry.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.guardian_phone_error_label = self._error_label(form_scroll, row); row += 1
        self._phone_vars["guardian_phone"].trace_add("write",
            lambda *a: self._validate_phone("guardian_phone"))

        # Guardian Address
        self._label(form_scroll, "Guardian Address *", row)
        self.guardian_address_text = ctk.CTkTextbox(
            form_scroll, width=380, height=80, corner_radius=10,
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=13)
        )
        self.guardian_address_text.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        row += 1
        self.guardian_address_error_label = self._error_label(form_scroll, row); row += 1

        # Submit
        btn_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)
        self.add_btn = ctk.CTkButton(
            btn_frame, text="Register Student",
            command=self.add_student,
            width=220, height=50, corner_radius=10,
            fg_color=COLORS["success"], hover_color="#2d8f47",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.add_btn.pack()

        self.status_label = ctk.CTkLabel(
            form_scroll, text="",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["success"]
        )
        self.status_label.grid(row=row + 1, column=0, columnspan=2, pady=(0, 20))

        # Bind Shift+Tab and auto-fill ID
        self._bind_tab_order()
        self._refresh_id_preview()
        if default_session:
            self._on_session_change(default_session)

    # ------------------------------------------------------------------ widget helpers
    def _section(self, parent, text, row):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).grid(row=row, column=0, columnspan=2, padx=25, pady=(20, 10), sticky="w")

    def _label(self, parent, text, row):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=row, column=0, padx=25, pady=(10, 5), sticky="w")

    def _error_label(self, parent, row):
        lbl = ctk.CTkLabel(parent, text="",
                           font=ctk.CTkFont(size=11),
                           text_color=COLORS["danger"])
        lbl.grid(row=row, column=1, padx=25, pady=(0, 5), sticky="w")
        return lbl

    # ------------------------------------------------------------------ validation
    def clear_all_errors(self):
        for lbl in [self.id_error_label, self.name_error_label, self.state_error_label,
                    self.home_address_error_label, self.guardian_name_error_label,
                    self.guardian_phone_error_label, self.guardian_address_error_label,
                    self.phone_error_label, self.status_label]:
            lbl.configure(text="")

    def show_field_error(self, field_name, message):
        self.clear_all_errors()
        mapping = {
            "id": self.id_error_label,
            "name": self.name_error_label,
            "state": self.state_error_label,
            "home_address": self.home_address_error_label,
            "guardian_name": self.guardian_name_error_label,
            "guardian_phone": self.guardian_phone_error_label,
            "guardian_address": self.guardian_address_error_label,
        }
        lbl = mapping.get(field_name)
        if lbl:
            lbl.configure(text=f"x {message}")

    # ------------------------------------------------------------------ submit
    def add_student(self):
        self.clear_all_errors()

        # Phone validation check first
        if not all(self._phone_valid.values()):
            return

        id_number = self.id_number_entry.get().strip()
        full_name = self.name_entry.get().strip()
        dob = self.dob_picker.get_date()
        sex = self.sex_var.get()
        class_name = self.class_var.get()
        dept_name = self.dept_var.get()
        state = self.state_var.get().strip()
        home_address = self.home_address_text.get("1.0", "end-1c").strip()
        phone = self._phone_vars["phone"].get().strip()
        guardian_name = self.guardian_name_entry.get().strip()
        guardian_phone = self._phone_vars["guardian_phone"].get().strip()
        guardian_address = self.guardian_address_text.get("1.0", "end-1c").strip()

        # Derive year from prefix label
        prefix_text = self.id_prefix_label.cget("text")  # e.g. "GFA/24/S"
        parts = prefix_text.split("/")
        yy = parts[1] if len(parts) >= 2 else str(datetime.now().year)[-2:]
        admission_year = int("20" + yy) if len(yy) == 2 else datetime.now().year

        if not id_number or not id_number.isdigit() or len(id_number) != 4:
            self.show_field_error("id", "Student ID must be exactly 4 digits")
            self.id_number_entry.focus()
            return

        student_id = f"GFA/{yy}/S{id_number}"

        if not full_name:
            self.show_field_error("name", "Full name is required")
            self.name_entry.focus()
            return
        if len(full_name.split()) < 2:
            self.show_field_error("name", "Please enter at least 2 names")
            self.name_entry.focus()
            return
        if not state:
            self.show_field_error("state", "State of origin is required")
            return
        if not home_address:
            self.show_field_error("home_address", "Home address is required")
            return
        if not guardian_name:
            self.show_field_error("guardian_name", "Guardian name is required")
            self.guardian_name_entry.focus()
            return
        if not guardian_phone:
            self.show_field_error("guardian_phone", "Guardian phone is required")
            self.guardian_phone_entry.focus()
            return
        if not guardian_address:
            self.show_field_error("guardian_address", "Guardian address is required")
            return

        try:
            age = self.calculate_age(dob)

            # Resolve dept_id
            dept = self.session.query(Department).filter_by(name=dept_name).first()
            dept_id = dept.id if dept else None

            # Resolve session_id
            sess_name = self.session_var.get()
            sess_obj = self.session.query(AcademicSession).filter_by(name=sess_name).first()
            session_id = sess_obj.id if sess_obj else None

            new_student = Student(
                student_id=student_id,
                full_name=full_name,
                date_of_birth=dob,
                age=age,
                sex=sex,
                class_name=class_name,
                admission_year=admission_year,
                state_of_origin=state,
                home_address=home_address,
                phone_number=phone if phone else None,
                guardian_name=guardian_name,
                guardian_phone=guardian_phone,
                guardian_address=guardian_address,
                dept_id=dept_id,
                session_id=session_id,
            )
            self.session.add(new_student)
            self.session.commit()

            self.show_success(f"Student '{full_name}' registered with ID: {student_id}")

            # Clear fields
            self.id_number_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            self.home_address_text.delete("1.0", "end")
            self.phone_entry.delete(0, "end")
            self.guardian_name_entry.delete(0, "end")
            self.guardian_phone_entry.delete(0, "end")
            self.guardian_address_text.delete("1.0", "end")
            self._refresh_id_preview()
            self.id_number_entry.focus()

            if self.on_student_added_callback:
                self.on_student_added_callback()

        except IntegrityError:
            self.session.rollback()
            self.show_field_error("id", f"Student ID '{student_id}' already exists")
        except Exception as e:
            self.session.rollback()
            self.status_label.configure(
                text=f"Error: {str(e)}", text_color=COLORS["danger"]
            )

    def show_success(self, message):
        self.clear_all_errors()
        self.status_label.configure(text=f"✓ {message}", text_color=COLORS["success"])

    def refresh_sessions(self):
        """Reload session list (call after adding a new session)."""
        sessions = self.session.query(AcademicSession).order_by(AcademicSession.name.desc()).all()
        names = [s.name for s in sessions] or ["No sessions"]
        self.session_combo.configure(values=names)
        active = self.session.query(AcademicSession).filter_by(is_active=True).first()
        if active:
            self.session_var.set(active.name)
            self._on_session_change(active.name)
