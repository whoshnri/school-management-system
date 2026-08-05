import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from models import Session, Student, Attendance, Mark, Fee
from fee_receipt_pdf import generate_fee_receipt, is_fee_fully_paid
from fee_helpers import (
    CLASS_OPTIONS,
    TERM_OPTIONS,
    apply_fee_structure,
    get_fee_structure,
    load_fee_structure_matrix,
    sync_fees_for_scope,
)
from validators import validate_email, validate_fee_payment
from app_paths import find_asset
from ui_components import (
    TextLabelManager,
    ModalController,
    enable_mousewheel_scrolling,
    DatePickerField,
    ModalOptionPicker,
    NIGERIAN_STATES,
    MODAL_STYLE,
    CLASS_FILTER_OPTIONS,
    center_toplevel,
    create_modal_header,
    create_section_header,
    create_form_entry,
    create_form_textbox,
    create_form_combobox,
    create_form_row,
    create_modal_footer,
    input_style,
    safe_export_filename,
    close_modal_window,
    setup_modal_window,
    ask_save_filename,
    show_error,
)

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
    "nav_active_text": "#ffffff",
    "nav_inactive_text": "#5f6368",
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

        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(
            top_row,
            text=TextLabelManager.get_header_text('student_directory'),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        # Student count badge
        self.count_label = ctk.CTkLabel(
            top_row,
            text="0 students",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.count_label.pack(side="left", padx=10)

        # Filters frame on new row inside header
        filters_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filters_frame.pack(fill="x", padx=20, pady=(10, 15))

        # Session
        self.session_var = ctk.StringVar()
        self.session_filter = ctk.CTkComboBox(filters_frame, variable=self.session_var, width=120, command=lambda _: self.load_students())
        self.session_filter.pack(side="left", padx=(0, 5))
        
        # Dept
        self.dept_var = ctk.StringVar()
        self.dept_filter = ctk.CTkComboBox(filters_frame, variable=self.dept_var, width=120, command=lambda _: self.load_students())
        self.dept_filter.pack(side="left", padx=5)

        # Class
        self.class_filter_var = ctk.StringVar(value="All Classes")
        class_filter = ctk.CTkComboBox(
            filters_frame,
            variable=self.class_filter_var,
            values=CLASS_FILTER_OPTIONS,
            width=130,
            command=lambda _value: self.load_students(),
            **input_style(),
        )
        class_filter.pack(side="left", padx=5)

        # Search
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filters_frame,
            placeholder_text="Search by name or ID...",
            textvariable=self.search_var,
            width=240,
            **input_style(),
        )
        search_entry.pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *args: self.load_students())
        
        self._load_filter_options()

    def _load_filter_options(self):
        from models import AcademicSession, Department
        sessions = self.session.query(AcademicSession).order_by(AcademicSession.name.desc()).all()
        session_names = ["All Sessions"] + [s.name for s in sessions]
        self.session_filter.configure(values=session_names)
        self.session_var.set("All Sessions")

        depts = self.session.query(Department).all()
        dept_names = ["All Departments"] + [d.name for d in depts]
        self.dept_filter.configure(values=dept_names)
        self.dept_var.set("All Departments")

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
        self.students_list_frame.grid_columnconfigure(0, weight=0, minsize=40)   # Row #
        self.students_list_frame.grid_columnconfigure(1, weight=1, minsize=100)  # ID
        self.students_list_frame.grid_columnconfigure(2, weight=2, minsize=160)  # Name
        self.students_list_frame.grid_columnconfigure(3, weight=1, minsize=100)  # Dept
        self.students_list_frame.grid_columnconfigure(4, weight=0, minsize=80)   # Gender
        self.students_list_frame.grid_columnconfigure(5, weight=0, minsize=80)   # Class
        self.students_list_frame.grid_columnconfigure(6, weight=0, minsize=180)  # Actions

    def load_students(self):
        # Clear existing student list
        for widget in self.students_list_frame.winfo_children():
            widget.destroy()

        if not hasattr(self, 'session_var'):
            return

        search_term = self.search_var.get().lower().strip()
        class_filter = self.class_filter_var.get()
        sess_name = self.session_var.get()
        dept_name = self.dept_var.get()
        
        from models import AcademicSession, Department
        query = self.session.query(Student)

        if sess_name and sess_name != "All Sessions":
            sess = self.session.query(AcademicSession).filter_by(name=sess_name).first()
            if sess: query = query.filter_by(session_id=sess.id)
        if dept_name and dept_name != "All Departments":
            dept = self.session.query(Department).filter_by(name=dept_name).first()
            if dept: query = query.filter_by(dept_id=dept.id)
        if class_filter and class_filter != "All Classes":
            query = query.filter_by(class_name=class_filter)
            
        students = query.order_by(Student.full_name).all()

        if search_term:
            students = [
                s for s in students
                if search_term in s.full_name.lower() or search_term in s.student_id.lower()
            ]

        # Update count
        self.count_label.configure(text=f"{len(students)} student{'s' if len(students) != 1 else ''}")

        # Empty state
        if not students:
            empty_frame = ctk.CTkFrame(self.students_list_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, columnspan=5, pady=60)
            
            message = (
                "No students found"
                if (search_term or class_filter != "All Classes")
                else "No students registered yet"
            )
            ctk.CTkLabel(
                empty_frame,
                text=message,
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack()
            
            if not search_term and class_filter == "All Classes":
                ctk.CTkLabel(
                    empty_frame,
                    text="Go to 'Registration' to add students",
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    text_color=COLORS["text_secondary"]
                ).pack(pady=(5, 0))
            return

        # Headers with separate # column
        headers = [("#", "center"), ("Student ID", "w"), ("Full Name", "w"), ("Department", "w"), ("Gender", "center"), ("Class", "center"), ("Actions", "center")]
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

            # Department
            dept_name = student.department.name if getattr(student, "department", None) else "N/A"
            ctk.CTkLabel(
                self.students_list_frame,
                text=dept_name,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).grid(row=i, column=3, padx=15, pady=12, sticky="ew")

            # Gender
            ctk.CTkLabel(
                self.students_list_frame,
                text=student.sex,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_secondary"],
                anchor="center"
            ).grid(row=i, column=4, padx=15, pady=12, sticky="ew")

            # Class badge
            class_badge = ctk.CTkLabel(
                self.students_list_frame,
                text=student.class_name,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLORS["nav_active_text"],
                fg_color=COLORS["primary"],
                corner_radius=6,
                width=65,
                height=28
            )
            class_badge.grid(row=i, column=5, padx=15, pady=12)

            # Actions frame
            actions_frame = ctk.CTkFrame(self.students_list_frame, fg_color="transparent")
            actions_frame.grid(row=i, column=6, padx=15, pady=12)

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
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
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

        edit_modal = ctk.CTkToplevel(root_window)
        edit_modal.title(f"Edit Student - {student.student_id}")
        edit_modal.transient(root_window)
        edit_modal.configure(fg_color=MODAL_STYLE["bg_main"])

        screen_height = root_window.winfo_screenheight()
        window_height = min(720, int(screen_height * 0.85))
        center_toplevel(edit_modal, root_window, 720, window_height)
        edit_modal.update_idletasks()
        setup_modal_window(edit_modal, on_close=lambda: close_modal_window(edit_modal))

        create_modal_header(
            edit_modal,
            "Edit Student Details",
            subtitle=f"{student.student_id} | {student.full_name}",
        )

        form_scroll = ctk.CTkScrollableFrame(
            edit_modal,
            fg_color="transparent",
            scrollbar_button_color=MODAL_STYLE["primary"],
            scrollbar_button_hover_color=MODAL_STYLE["primary_hover"],
        )
        form_scroll.pack(fill="both", expand=True, padx=MODAL_STYLE["padding"], pady=MODAL_STYLE["padding"])

        current_dept = student.department.name if student.department else "Science"
        dept_var = ctk.StringVar(value=current_dept)

        id_entry = create_form_entry(form_scroll, "Student ID", student.student_id)

        def _on_edit_dept_change(choice):
            dept_code_map = {"Science": "SC", "Art": "AR", "Commercial": "CO"}
            new_code = dept_code_map.get(choice, "SC")
            curr_id = id_entry.get()
            for old_code in ["SC", "AR", "CO"]:
                if f"/{old_code}/" in curr_id:
                    new_id = curr_id.replace(f"/{old_code}/", f"/{new_code}/")
                    id_entry.delete(0, "end")
                    id_entry.insert(0, new_id)
                    break

        create_section_header(form_scroll, "Personal Information")
        full_name_entry = create_form_entry(form_scroll, "Full Name *", student.full_name)

        dob_picker = create_form_row(
            form_scroll,
            "Date of Birth *",
            widget_factory=lambda frame: DatePickerField(
                frame,
                initial_date=student.date_of_birth,
                width=308,
                height=MODAL_STYLE["input_height"],
                font_size=13,
            ),
        )

        sex_var = ctk.StringVar(value=student.sex)
        create_form_combobox(form_scroll, "Sex *", ["Male", "Female"], sex_var)

        create_form_combobox(form_scroll, "Department *", ["Science", "Art", "Commercial"], dept_var, command=_on_edit_dept_change)

        class_var = ctk.StringVar(value=student.class_name)
        create_form_combobox(form_scroll, "Class *", ["SSS1", "SSS2", "SSS3"], class_var)

        admission_year_entry = create_form_entry(
            form_scroll, "Admission Year *", str(student.admission_year)
        )

        state_picker = create_form_row(
            form_scroll,
            "State of Origin *",
            widget_factory=lambda frame: ModalOptionPicker(
                frame,
                options=NIGERIAN_STATES,
                title="State of Origin",
                placeholder="Select state...",
                width=308,
                height=MODAL_STYLE["input_height"],
                font_size=13,
                initial_value=student.state_of_origin,
            ),
        )

        create_section_header(form_scroll, "Contact Information")
        home_address_text = create_form_textbox(form_scroll, "Home Address *", student.home_address)
        phone_entry = create_form_entry(form_scroll, "Phone Number", student.phone_number or "")

        create_section_header(form_scroll, "Guardian/Parent Information")
        guardian_name_entry = create_form_entry(form_scroll, "Guardian Name *", student.guardian_name)
        guardian_phone_entry = create_form_entry(form_scroll, "Guardian Phone *", student.guardian_phone)
        guardian_address_text = create_form_textbox(
            form_scroll, "Guardian Address *", student.guardian_address
        )
        def save_all_changes():
            """Save all edited student information."""
            # Get all values
            new_id = id_entry.get().strip()
            new_name = full_name_entry.get().strip()
            new_dob = dob_picker.get_date()
            new_sex = sex_var.get()
            new_dept = dept_var.get()
            new_class = class_var.get()
            new_admission_year = admission_year_entry.get().strip()
            new_state = state_picker.get()
            new_home_address = home_address_text.get("1.0", "end-1c").strip()
            new_phone = phone_entry.get().strip()
            new_guardian_name = guardian_name_entry.get().strip()
            new_guardian_phone = guardian_phone_entry.get().strip()
            new_guardian_address = guardian_address_text.get("1.0", "end-1c").strip()
            
            # Validation
            if not new_id:
                show_error(edit_modal, "Error", "Student ID is required")
                return

            if not new_name or len(new_name.split()) < 2:
                show_error(edit_modal, "Error", "Please enter a valid full name (at least 2 names)")
                return
            
            if not new_admission_year.isdigit():
                show_error(edit_modal, "Error", "Admission year must be a valid year")
                return
            
            if not new_state:
                show_error(edit_modal, "Error", "Please select a state of origin")
                return
            
            if not new_home_address:
                show_error(edit_modal, "Error", "Home address is required")
                return
            
            if not new_guardian_name:
                show_error(edit_modal, "Error", "Guardian name is required")
                return
            
            if not new_guardian_phone:
                show_error(edit_modal, "Error", "Guardian phone is required")
                return
            
            if not new_guardian_address:
                show_error(edit_modal, "Error", "Guardian address is required")
                return
            
            try:
                # Calculate age
                from datetime import date as dt_date
                today = dt_date.today()
                age = today.year - new_dob.year - ((today.month, today.day) < (new_dob.month, new_dob.day))
                
                # Update student
                student.student_id = new_id
                student.full_name = new_name
                name_parts = new_name.split(maxsplit=1)
                student.surname = name_parts[0] if name_parts else ""
                student.other_names = name_parts[1] if len(name_parts) > 1 else ""
                student.firstname = student.other_names
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
                
                dept_obj = self.session.query(Department).filter_by(name=new_dept).first()
                if dept_obj:
                    student.dept_id = dept_obj.id

                self.session.commit()


                def after_save():
                    self.load_students()
                    if self.on_student_deleted_callback:
                        self.on_student_deleted_callback()

                close_modal_window(
                    edit_modal,
                    on_after=after_save,
                    success_message=f"Student '{new_name}' updated successfully!",
                )
            except Exception as e:
                self.session.rollback()
                show_error(edit_modal, "Error", f"Failed to update student: {str(e)}")
        
        create_modal_footer(
            edit_modal,
            "Save Changes",
            save_all_changes,
            lambda: close_modal_window(edit_modal),
        )

        edit_modal.bind("<Escape>", lambda e: close_modal_window(edit_modal))


class FeeItemEditorModal(ctk.CTkToplevel):
    """Modal for editing fee items for a specific (class, dept, term)."""

    def __init__(self, parent, session, class_name, dept_name, term, on_saved=None):
        super().__init__(parent)
        self.session = session
        self.on_saved = on_saved
        self.class_name = class_name
        self.dept_name = dept_name
        self.term = term

        term_label = {1: "First Term", 2: "Second Term", 3: "Third Term"}.get(term, f"Term {term}")
        self.title(f"Fee Items — {class_name} / {dept_name} / {term_label}")
        self.transient(parent)
        self.configure(fg_color=MODAL_STYLE["bg_main"])
        center_toplevel(self, parent, 600, 600)

        create_modal_header(
            self,
            f"Fee Structure: {class_name} · {dept_name} · {term_label}",
            subtitle="Add fee items below. Amount must be a valid number.",
        )

        import json
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=MODAL_STYLE["padding"], pady=(0, 8))

        self.items_frame = ctk.CTkScrollableFrame(body, fg_color="transparent", height=300)
        self.items_frame.pack(fill="both", expand=True)

        from fee_helpers import get_fee_structure
        structure = get_fee_structure(session, class_name, term, dept_name)
        self.item_rows = []

        existing_items = []
        if structure and structure.fee_items:
            try:
                existing_items = json.loads(structure.fee_items)
            except Exception:
                pass

        if not existing_items:
            existing_items = [{"description": "", "amount": ""}]

        for item in existing_items:
            self.add_item_row(item.get("description", ""), item.get("amount", ""))

        ctk.CTkButton(
            body, text="+ Add Fee Item", command=lambda: self.add_item_row("", ""),
            fg_color=COLORS["secondary"], hover_color=COLORS["primary"], text_color="white",
            width=150, height=36
        ).pack(anchor="w", pady=(10, 0))

        self.total_label = ctk.CTkLabel(body, text="Total: ₦0.00", font=ctk.CTkFont(size=18, weight="bold"))
        self.total_label.pack(anchor="e", pady=(10, 0))

        create_modal_footer(self, save_text="Save Structure", save_command=self.save, cancel_command=self._close)
        setup_modal_window(self, on_close=self._close)
        self.calculate_total()

    def add_item_row(self, desc="", amt=""):
        row_frame = ctk.CTkFrame(self.items_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        desc_entry = ctk.CTkEntry(row_frame, placeholder_text="Item Description (e.g. Tuition)", width=250, **input_style())
        desc_entry.pack(side="left", padx=(0, 10))
        if desc:
            desc_entry.insert(0, desc)

        amt_entry = ctk.CTkEntry(row_frame, placeholder_text="Amount", width=150, **input_style())
        amt_entry.pack(side="left", padx=(0, 10))
        if amt:
            amt_entry.insert(0, str(amt))

        def enforce_numbers(e):
            val = amt_entry.get()
            cleaned = "".join([c for c in val if c.isdigit() or c == '.'])
            parts = cleaned.split('.')
            if len(parts) > 2:
                cleaned = parts[0] + '.' + "".join(parts[1:])
            if val != cleaned:
                amt_entry.delete(0, 'end')
                amt_entry.insert(0, cleaned)
            self.calculate_total()

        amt_entry.bind("<KeyRelease>", enforce_numbers)

        del_btn = ctk.CTkButton(row_frame, text="X", width=36, fg_color=COLORS["danger"], hover_color="#c5221f",
                                command=lambda: self.remove_item_row(row_frame))
        del_btn.pack(side="left")

        self.item_rows.append((row_frame, desc_entry, amt_entry))

    def remove_item_row(self, row_frame):
        for row in self.item_rows:
            if row[0] == row_frame:
                row_frame.destroy()
                self.item_rows.remove(row)
                break
        self.calculate_total()

    def calculate_total(self):
        total = 0.0
        for _, _, amt_entry in self.item_rows:
            try:
                val = amt_entry.get().strip()
                if val:
                    total += float(val)
            except ValueError:
                pass
        self.total_label.configure(text=f"Total: ₦{total:,.2f}")
        return total

    def _close(self):
        close_modal_window(self)

    def save(self):
        import json
        from fee_helpers import apply_fee_structure
        items = []
        total = 0.0
        for _, desc_entry, amt_entry in self.item_rows:
            desc = desc_entry.get().strip()
            amt_str = amt_entry.get().strip()
            if not desc and not amt_str:
                continue
            if not desc:
                show_error(self, "Validation Error", "Description cannot be empty.")
                return
            if not amt_str:
                show_error(self, "Validation Error", f"Amount for '{desc}' cannot be empty.")
                return
            try:
                amt = float(amt_str)
                if amt < 0:
                    raise ValueError
            except ValueError:
                show_error(self, "Validation Error", f"Amount for '{desc}' must be a positive number.")
                return
            items.append({"description": desc, "amount": amt})
            total += amt

        try:
            apply_fee_structure(self.session, self.class_name, self.term, total, json.dumps(items), self.dept_name)
            close_modal_window(self, on_after=self.on_saved, success_message="Fee structure saved.")
        except Exception as exc:
            self.session.rollback()
            show_error(self, "Error", f"Failed to save: {exc}")


class FeeStructureModal(ctk.CTkToplevel):
    """Tabbed overview modal showing fee status for all class/dept/term combos."""

    def __init__(self, parent, session, on_saved=None):
        super().__init__(parent)
        self.session = session
        self.on_saved = on_saved

        self.title("Fee Structure Overview")
        self.transient(parent)
        self.configure(fg_color=MODAL_STYLE["bg_main"])
        center_toplevel(self, parent, 700, 500)

        create_modal_header(
            self,
            "Fee Structure Overview",
            subtitle="Set fees per class, department, and term. Click a cell to edit.",
        )

        # Tabs for classes
        self.tab_view = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_card"],
            segmented_button_fg_color=COLORS["border"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_color="#e0e0e0",
            segmented_button_unselected_hover_color=COLORS["primary_hover"],
            text_color="white",
            text_color_disabled=COLORS["text_secondary"],
            corner_radius=12,
        )
        self.tab_view.pack(fill="both", expand=True, padx=MODAL_STYLE["padding"], pady=(0, 8))

        from fee_helpers import CLASS_OPTIONS, DEPT_OPTIONS, TERM_OPTIONS
        self.class_options = CLASS_OPTIONS
        self.dept_options = DEPT_OPTIONS
        self.term_options = TERM_OPTIONS

        for cls in self.class_options:
            self.tab_view.add(cls)

        self._build_grids()

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=MODAL_STYLE["padding"], pady=(0, MODAL_STYLE["padding"]))
        ctk.CTkButton(
            footer, text="Close", command=self._close,
            fg_color=COLORS["border"], text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_card"], width=100, height=36, corner_radius=8
        ).pack(side="right")

        setup_modal_window(self, on_close=self._close)

    def _build_grids(self):
        from fee_helpers import load_fee_structure_matrix
        matrix = load_fee_structure_matrix(self.session)

        for cls in self.class_options:
            tab = self.tab_view.tab(cls)
            # Clear any existing widgets
            for w in tab.winfo_children():
                w.destroy()

            tab.grid_columnconfigure(0, weight=1, minsize=100)
            for j in range(len(self.term_options)):
                tab.grid_columnconfigure(j + 1, weight=1, minsize=140)

            # Column headers (Terms)
            ctk.CTkLabel(
                tab, text="Department",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=0, padx=10, pady=(15, 10), sticky="w")

            for j, (term_num, term_label) in enumerate(self.term_options):
                ctk.CTkLabel(
                    tab, text=term_label,
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                    text_color=COLORS["text_secondary"]
                ).grid(row=0, column=j + 1, padx=10, pady=(15, 10))

            # Rows (Departments)
            for i, dept in enumerate(self.dept_options):
                ctk.CTkLabel(
                    tab, text=dept,
                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).grid(row=i + 1, column=0, padx=10, pady=8, sticky="w")

                for j, (term_num, term_label) in enumerate(self.term_options):
                    key = (cls, term_num, dept)
                    structure = matrix.get(key)

                    if structure and structure.amount_due > 0:
                        btn_text = f"Edit ₦{structure.amount_due:,.0f}"
                        btn_fg = COLORS["success"]
                        btn_hover = "#2d8f47"
                        btn_text_color = "white"
                    else:
                        btn_text = "Not Set"
                        btn_fg = COLORS["danger"]
                        btn_hover = "#c5221f"
                        btn_text_color = "white"

                    ctk.CTkButton(
                        tab,
                        text=btn_text,
                        fg_color=btn_fg,
                        hover_color=btn_hover,
                        text_color=btn_text_color,
                        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                        width=130, height=36, corner_radius=8,
                        command=lambda c=cls, d=dept, t=term_num: self._open_editor(c, d, t),
                    ).grid(row=i + 1, column=j + 1, padx=8, pady=8)

    def _open_editor(self, class_name, dept_name, term):
        FeeItemEditorModal(
            self, self.session,
            class_name=class_name,
            dept_name=dept_name,
            term=term,
            on_saved=self._on_item_saved,
        )

    def _on_item_saved(self):
        self._build_grids()
        if self.on_saved:
            self.on_saved()

    def _close(self):
        close_modal_window(self)


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
            text="Edit Fee Structure",
            command=self.open_fee_structure_modal,
            width=140,
            height=36,
            corner_radius=8,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).pack(side="left", padx=(12, 0))

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
        ).pack(side="left", padx=(12, 0))

        self.structure_summary = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"],
        )
        self.structure_summary.pack(side="left", padx=(12, 0), pady=15)

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

    def _selected_scope(self):
        class_name = self.class_filter.get()
        term_value = self.term_filter.get()
        term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)
        return class_name, term

    def open_fee_structure_modal(self):
        root = self.winfo_toplevel()
        FeeStructureModal(
            root,
            self.session,
            on_saved=self.load_fees,
        )

    def load_fees(self):
        for widget in self.fees_list_frame.winfo_children():
            widget.destroy()

        class_name, term = self._selected_scope()
        sync_fees_for_scope(self.session, class_name, term)

        structure = get_fee_structure(self.session, class_name, term)
        if structure and structure.amount_due > 0:
            self.structure_summary.configure(
                text=f"Fee due for {class_name} · {TERM_OPTIONS[term - 1][1]}: ₦{structure.amount_due:,.2f}"
            )
        else:
            self.structure_summary.configure(
                text=f"No fee structure set for {class_name} · {TERM_OPTIONS[term - 1][1]}. Click Edit Fee Structure."
            )

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

        headers = ["Student", "Amount Due", "Amount Paid", "Balance", "Status", "Update Payment", "Receipt"]
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
            is_paid = is_fee_fully_paid(fee)
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

            # Amount Paid
            ctk.CTkLabel(
                self.fees_list_frame,
                text=f"₦{fee.amount_paid:,.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["success"] if fee.amount_paid > 0 else COLORS["text_secondary"]
            ).grid(row=i, column=2, padx=10, pady=12, sticky="w")

            # Balance
            ctk.CTkLabel(
                self.fees_list_frame,
                text=f"₦{balance:,.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["danger"] if balance > 0 else COLORS["success"]
            ).grid(row=i, column=3, padx=10, pady=12, sticky="w")

            # Status
            ctk.CTkLabel(
                self.fees_list_frame,
                text=status_text,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=status_color
            ).grid(row=i, column=4, padx=10, pady=12, sticky="w")

            # Update Payment Entry + Button
            payment_frame = ctk.CTkFrame(self.fees_list_frame, fg_color="transparent")
            payment_frame.grid(row=i, column=5, padx=5, pady=12, sticky="w")

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

            receipt_state = "normal" if is_paid else "disabled"
            ctk.CTkButton(
                self.fees_list_frame,
                text="Receipt",
                command=lambda s=student, t=term: self.download_receipt(s, t),
                width=88,
                height=32,
                corner_radius=6,
                fg_color=COLORS["primary"] if is_paid else COLORS["border"],
                hover_color=COLORS["primary_hover"] if is_paid else COLORS["border"],
                text_color=COLORS["nav_active_text"] if is_paid else COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                state=receipt_state,
            ).grid(row=i, column=6, padx=10, pady=12, sticky="w")

    def update_fee(self, student_id, term, amount_str):
        try:
            fee = self.session.query(Fee).filter_by(student_id=student_id, term=term).one()
            amount, error = validate_fee_payment(amount_str, fee.amount_due, fee.amount_paid)
            if error:
                messagebox.showerror("Invalid Payment", error)
                return

            fee.amount_paid += amount
            self.session.commit()
            messagebox.showinfo("Success", f"Payment of ₦{amount:,.2f} recorded successfully.")
            self.load_fees()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def download_receipt(self, student, term):
        fee = self.session.query(Fee).filter_by(student_id=student.id, term=term).first()
        if not is_fee_fully_paid(fee):
            messagebox.showwarning(
                "Not Paid",
                "Receipts are only available when the fee has been paid in full.",
            )
            return

        term_names = {1: "term1", 2: "term2", 3: "term3"}
        filename = ask_save_filename(
            self,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=safe_export_filename(
                student.full_name,
                term_names.get(term, f"term{term}"),
                "fees_receipt",
                extension="pdf",
            ),
            title="Save Payment Receipt",
        )
        if not filename:
            return

        if generate_fee_receipt(student.id, term, filename):
            messagebox.showinfo("Success", f"Payment receipt saved to:\n{filename}")
        else:
            messagebox.showerror("Error", "Failed to generate payment receipt.")


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
        
        # SECTION 3: MANAGE ADMINS
        self.setup_manage_admins_section()

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
        email = self.current_admin.username if self.current_admin else "Unknown"
        self.create_field(update_frame, "Email:", email, readonly=True)
        
        self.update_current_pw = self.create_field(update_frame, "Current Password:", placeholder="Enter current password", is_password=True)
        self.update_new_pw = self.create_field(update_frame, "New Password:", placeholder="Enter new password", is_password=True)
        self.update_confirm_pw = self.create_field(update_frame, "Confirm Password:", placeholder="Confirm new password", is_password=True)

        self.show_update_passwords = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            update_frame,
            text="Show password fields",
            variable=self.show_update_passwords,
            command=lambda: self._toggle_entry_visibility(
                [self.update_current_pw, self.update_new_pw, self.update_confirm_pw],
                self.show_update_passwords.get(),
            ),
            text_color=COLORS["text_secondary"],
            checkbox_width=18,
            checkbox_height=18,
        ).pack(anchor="w", padx=182, pady=(0, 10))
        
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
        
        self.reg_username = self.create_field(register_frame, "New Email:", placeholder="name@school.com")
        self.reg_password = self.create_field(register_frame, "Password:", placeholder="Enter password", is_password=True)
        self.reg_confirm = self.create_field(register_frame, "Confirm Password:", placeholder="Confirm password", is_password=True)
        self.reg_recovery_pin = self.create_field(register_frame, "Recovery PIN:", placeholder="Enter 4+ digit PIN", is_password=True)
        self.reg_confirm_pin = self.create_field(register_frame, "Confirm PIN:", placeholder="Re-enter recovery PIN", is_password=True)

        self.show_register_passwords = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            register_frame,
            text="Show password and PIN fields",
            variable=self.show_register_passwords,
            command=lambda: self._toggle_entry_visibility(
                [
                    self.reg_password,
                    self.reg_confirm,
                    self.reg_recovery_pin,
                    self.reg_confirm_pin,
                ],
                self.show_register_passwords.get(),
            ),
            text_color=COLORS["text_secondary"],
            checkbox_width=18,
            checkbox_height=18,
        ).pack(anchor="w", padx=182, pady=(0, 10))
        
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

    def setup_manage_admins_section(self):
        manage_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        manage_frame.grid(row=2, column=0, padx=5, pady=(20, 20), sticky="ew")
        
        ctk.CTkLabel(
            manage_frame,
            text="Manage Admins",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=30, pady=(20, 5))
        
        ctk.CTkLabel(
            manage_frame,
            text="View and remove administrators from the system.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30, pady=(0, 20))
        
        # Admin list container
        self.admins_list_frame = ctk.CTkFrame(manage_frame, fg_color="transparent")
        self.admins_list_frame.pack(fill="x", padx=30, pady=(0, 25))
        
        self.load_admins()

    def load_admins(self):
        for widget in self.admins_list_frame.winfo_children():
            widget.destroy()
            
        from models import Admin
        admins = self.session.query(Admin).order_by(Admin.username).all()
        
        # Headers
        header_row = ctk.CTkFrame(self.admins_list_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_row, text="Email", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_secondary"], width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_row, text="Created At", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_secondary"], width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_row, text="Actions", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_secondary"], width=80, anchor="center").pack(side="right", padx=5)
        
        for admin in admins:
            row = ctk.CTkFrame(self.admins_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            # Highlight current admin
            is_current = (self.current_admin and admin.id == self.current_admin.id)
            display_name = f"{admin.username} (You)" if is_current else admin.username
            
            ctk.CTkLabel(row, text=display_name, font=ctk.CTkFont(size=13), text_color=COLORS["text_primary"], width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=admin.created_at, font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"], width=150, anchor="w").pack(side="left", padx=5)
            
            if is_current or len(admins) <= 1:
                # Disabled button
                ctk.CTkButton(
                    row, text="Remove", width=70, height=28, corner_radius=6,
                    fg_color=COLORS["bg_dark"], text_color=COLORS["text_secondary"],
                    state="disabled"
                ).pack(side="right", padx=5)
            else:
                ctk.CTkButton(
                    row, text="Remove", width=70, height=28, corner_radius=6,
                    fg_color=COLORS["danger"], hover_color="#c9302c",
                    command=lambda a_id=admin.id, u=admin.username: self.handle_remove_admin(a_id, u)
                ).pack(side="right", padx=5)

    def handle_remove_admin(self, admin_id, username):
        confirm = messagebox.askyesno(
            "Remove Admin",
            f"Are you sure you want to remove administrator '{username}'?\n\nThey will no longer have access to the system.",
            icon="warning"
        )
        if not confirm:
            return
            
        from models import Admin
        admin_to_delete = self.session.query(Admin).filter_by(id=admin_id).first()
        if admin_to_delete:
            self.session.delete(admin_to_delete)
            try:
                self.session.commit()
                messagebox.showinfo("Success", f"Administrator '{username}' has been removed.")
                self.load_admins()
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("Database Error", f"Could not remove admin: {e}")

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

    def _toggle_entry_visibility(self, entries, reveal):
        """Toggle one or more secret fields between hidden and visible text."""
        secret_mask = "" if reveal else "●"
        for entry in entries:
            entry.configure(show=secret_mask)

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
        recovery_pin = self.reg_recovery_pin.get().strip()
        confirm_pin = self.reg_confirm_pin.get().strip()
        
        if not username or not password or not confirm or not recovery_pin or not confirm_pin:
            messagebox.showerror("Error", "All fields are required.")
            return

        ok, email_error = validate_email(username)
        if not ok:
            messagebox.showerror("Error", email_error)
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if recovery_pin != confirm_pin:
            messagebox.showerror("Error", "Recovery PIN values do not match.")
            return

        if not recovery_pin.isdigit() or len(recovery_pin) < 4:
            messagebox.showerror("Error", "Recovery PIN must be at least 4 digits.")
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
            recovery_pin_hash = hashlib.sha256(recovery_pin.encode()).hexdigest()
            
            # Create new admin
            new_admin = Admin(
                username=username,
                password_hash=password_hash,
                recovery_pin_hash=recovery_pin_hash,
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
            self.reg_recovery_pin.delete(0, 'end')
            self.reg_confirm_pin.delete(0, 'end')
            
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Failed to register admin: {str(e)}")


class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        import os
        from PIL import Image
        from app_paths import find_asset
        
        banner_path = find_asset(("assets/school-ad-banner.png", "school-ad-banner.png"))
        if banner_path and os.path.exists(banner_path):
            try:
                img = Image.open(banner_path)
                width, height = img.size
                aspect_ratio = width / height
                new_width = 800
                new_height = int(new_width / aspect_ratio)
                img = img.resize((new_width, new_height))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(new_width, new_height))
                
                label = ctk.CTkLabel(self, image=photo, text="")
                label.pack(expand=True, fill="both", padx=20, pady=20)
            except Exception as e:
                ctk.CTkLabel(self, text=f"Dashboard\nError loading banner: {e}").pack(expand=True)
        else:
            ctk.CTkLabel(self, text="Dashboard\n(Banner ad not found)").pack(expand=True)

class EnterpriseSchoolManagementApp:
    def __init__(self, root, current_admin=None):
        self.root = root
        self.current_admin = current_admin
        self.root.title("Admin Panel")
        self.session = Session()

        # Configure grid layout (1x2)
        self.root.grid_columnconfigure(0, minsize=180)  # Sidebar fixed width
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_frames()
        enable_mousewheel_scrolling(self.root)

        # Select default frame
        self.select_frame_by_name("Dashboard")

    def setup_sidebar(self):
        self.navigation_frame = ctk.CTkFrame(
            self.root, corner_radius=0, fg_color=COLORS["bg_dark"], width=180
        )
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_propagate(False)
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        self.navigation_frame.grid_rowconfigure(1, weight=1)

        # Logo / title — centered
        logo_frame = ctk.CTkFrame(self.navigation_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(28, 24))

        logo_inner = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_inner.pack(anchor="center")

        try:
            import os
            from PIL import Image
            icon_path = find_asset(("assets/school-logo.jpeg", "school-logo.jpeg", "app_icon.png"))
            if icon_path:
                icon_image = Image.open(icon_path).resize((80, 80), Image.Resampling.LANCZOS)
                icon_photo = ctk.CTkImage(
                    light_image=icon_image, dark_image=icon_image, size=(80, 80)
                )
                ctk.CTkLabel(logo_inner, image=icon_photo, text="").pack()
            else:
                ctk.CTkLabel(
                    logo_inner, text="SMS",
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=COLORS["primary"],
                ).pack()
        except Exception:
            ctk.CTkLabel(
                logo_inner, text="SMS",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=COLORS["primary"],
            ).pack()

        ctk.CTkLabel(
            logo_inner,
            text="Admin Panel",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(10, 0))

        # Nav buttons — scroll when the window is too short for every item
        nav_scroll = ctk.CTkScrollableFrame(
            self.navigation_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        nav_scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        nav_scroll.grid_columnconfigure(0, weight=1)

        nav_items = [
            ("Dashboard", "Dashboard"),
            (TextLabelManager.get_nav_text('register'), "Student Registration"),
            (TextLabelManager.get_nav_text('students'), "Students List"),
            (TextLabelManager.get_nav_text('fees'), "School Fees"),
            (TextLabelManager.get_nav_text('marks'), "Grades Entry"),
            (TextLabelManager.get_nav_text('broadsheet'), "Broadsheet"),
            (TextLabelManager.get_nav_text('attendance'), "Attendance"),
            (TextLabelManager.get_nav_text('report_cards'), "Report Cards"),
            ("Sessions", "Sessions"),
            ("Departments", "Departments"),
        ]

        self.nav_buttons = {}
        for row, (text, name) in enumerate(nav_items):
            btn = self._create_nav_button(nav_scroll, text, name)
            btn.grid(row=row, column=0, sticky="ew", pady=3)
            self.nav_buttons[name] = btn

        # Bottom section — settings + logout
        bottom_frame = ctk.CTkFrame(self.navigation_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 20))
        bottom_frame.grid_columnconfigure(0, weight=1)

        separator = ctk.CTkFrame(bottom_frame, fg_color=COLORS["border"], height=1)
        separator.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        settings_btn = self._create_nav_button(
            bottom_frame, "Settings", "Admin Settings"
        )
        settings_btn.grid(row=1, column=0, sticky="ew", pady=3)
        self.nav_buttons["Admin Settings"] = settings_btn

        logout_btn = ctk.CTkButton(
            bottom_frame,
            corner_radius=8,
            height=36,
            text="Logout",
            fg_color=COLORS["danger"],
            text_color=COLORS["nav_active_text"],
            hover_color="#c9302c",
            anchor="center",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.logout,
        )
        logout_btn.grid(row=2, column=0, sticky="ew", pady=(12, 0))

    def logout(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from main import LoginWindow, start_main_app
        LoginWindow(self.root, lambda admin: start_main_app(self.root, admin))

    def _create_nav_button(self, parent, text, frame_name):
        btn = ctk.CTkButton(
            parent,
            corner_radius=8,
            height=36,
            text=text,
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["nav_inactive_text"],
            hover_color=COLORS["primary"],
            anchor="center",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=lambda n=frame_name: self.select_frame_by_name(n),
        )
        btn._nav_active = False

        def on_enter(_event):
            if not btn._nav_active:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color=COLORS["nav_active_text"],
                )

        def on_leave(_event):
            if btn._nav_active:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color=COLORS["nav_active_text"],
                )
            else:
                btn.configure(
                    fg_color=COLORS["bg_dark"],
                    text_color=COLORS["nav_inactive_text"],
                )

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _set_nav_button_active(self, btn, active):
        btn._nav_active = active
        if active:
            btn.configure(
                fg_color=COLORS["primary"],
                text_color=COLORS["nav_active_text"],
                hover_color=COLORS["primary_hover"],
            )
        else:
            btn.configure(
                fg_color=COLORS["bg_dark"],
                text_color=COLORS["nav_inactive_text"],
                hover_color=COLORS["primary"],
            )

    def setup_main_frames(self):
        from forms import MarksEntryTab, AttendanceTab
        from enhanced_broadsheet import EnhancedBroadsheetTab
        from enhanced_registration import EnhancedStudentRegistrationTab
        from sessions_tab import SessionsTab
        from departments_tab import DepartmentsTab
        from report_cards_tab import ReportCardsTab

        self.dashboard_frame = DashboardTab(self.root, self.session)
        self.students_list_frame = StudentsListTab(self.root, self.session, on_student_deleted_callback=self.refresh_data)
        self.school_fees_frame = SchoolFeesTab(self.root, self.session)
        self.registration_frame = EnhancedStudentRegistrationTab(self.root, self.session, on_student_added_callback=self.refresh_data)
        self.marks_frame = MarksEntryTab(self.root, self.session)
        self.broadsheet_frame = EnhancedBroadsheetTab(self.root, self.session)
        self.attendance_frame = AttendanceTab(self.root, self.session)
        self.report_cards_frame = ReportCardsTab(self.root, self.session)
        self.admin_settings_frame = AdminSettingsTab(self.root, self.session, self.current_admin)
        self.sessions_frame = SessionsTab(self.root)
        self.departments_frame = DepartmentsTab(self.root)

        # Wire dynamic session & subject update callbacks
        def _on_sessions_updated():
            if hasattr(self.registration_frame, 'refresh_sessions'):
                self.registration_frame.refresh_sessions()
            if hasattr(self.students_list_frame, 'load_students'):
                self.students_list_frame.load_students()

        self.sessions_frame.add_on_sessions_changed_callback(_on_sessions_updated)

        def _on_subjects_updated():
            if hasattr(self.marks_frame, 'load_subjects'):
                self.marks_frame.load_subjects()
            if hasattr(self.broadsheet_frame, 'load_enhanced_sheet'):
                self.broadsheet_frame.load_enhanced_sheet()

        self.departments_frame.add_on_subject_changed_callback(_on_subjects_updated)


    def select_frame_by_name(self, name):
        for btn_name, btn in self.nav_buttons.items():
            self._set_nav_button_active(btn, btn_name == name)

        # Frame mapping
        frames = {
            "Dashboard": self.dashboard_frame,
            "Students List": self.students_list_frame,
            "School Fees": self.school_fees_frame,
            "Student Registration": self.registration_frame,
            "Grades Entry": self.marks_frame,
            "Broadsheet": self.broadsheet_frame,
            "Attendance": self.attendance_frame,
            "Report Cards": self.report_cards_frame,
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
        if hasattr(self, "report_cards_frame"):
            self.report_cards_frame.load_students()

