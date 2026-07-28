"""
Report Cards tab — manage per-student report card details and PDF export.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime

from models import Session, Student, Mark, ReportCard
from ui_components import (
    TextLabelManager,
    MODAL_STYLE,
    center_toplevel,
    create_modal_header,
    create_modal_footer,
    input_style,
    safe_export_filename,
    enable_mousewheel_scrolling,
    close_modal_window,
    setup_modal_window,
    ask_save_filename,
    show_info,
    show_error,
    show_warning,
)
from report_card_pdf import (
    generate_report_card,
    is_report_card_complete,
    BEHAVIOUR_TRAITS,
    BEHAVIOUR_SECTION_TITLE,
    TEACHER_COMMENT_LABEL,
    PRINCIPAL_COMMENT_LABEL,
    TEACHER_SIGNATURE_LABEL,
    PRINCIPAL_SIGNATURE_LABEL,
    PARENT_SIGNATURE_LABEL,
)

COLORS = {
    **MODAL_STYLE,
    "warning": "#fbbc04",
    "sheet_header": "#eef2f7",
    "sheet_row": "#ffffff",
}
TERM_OPTIONS = [
    (1, "First Term"),
    (2, "Second Term"),
    (3, "Third Term"),
]
BEHAVIOUR_FIELDS = BEHAVIOUR_TRAITS
RATING_VALUES = ["", "5", "4", "3", "2", "1"]


class ReportCardEditWindow(ctk.CTkToplevel):
    def __init__(self, parent, session, student, term, on_saved=None):
        super().__init__(parent)
        self.session = session
        self.student = student
        self.term = term
        self.on_saved = on_saved
        self.report_card = self._get_or_create_report_card()
        self.rating_vars = {}

        term_name = dict(TERM_OPTIONS)[term]
        self.title(f"Report Card — {student.full_name}")
        self.transient(parent)
        self.configure(fg_color=COLORS["bg_main"])
        center_toplevel(self, parent, 760, 760)

        create_modal_header(
            self,
            "Edit Report Card",
            subtitle=f"{student.full_name}  |  {student.class_name}  |  {term_name}",
        )

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        scroll.pack(fill="both", expand=True, padx=COLORS["padding"], pady=(0, 8))
        enable_mousewheel_scrolling(scroll)

        ctk.CTkLabel(
            scroll,
            text=BEHAVIOUR_SECTION_TITLE,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            scroll,
            text="Rate each trait from 5 (Excellent) to 1 (Poor).",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        for label, field in BEHAVIOUR_FIELDS:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=label,
                width=280,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"],
            ).pack(side="left")
            var = ctk.StringVar(
                value=str(getattr(self.report_card, field) or "")
            )
            self.rating_vars[field] = var
            ctk.CTkComboBox(
                row,
                variable=var,
                values=RATING_VALUES[1:],
                width=80,
                height=38,
                text_color=COLORS["text_primary"],
                **input_style(),
            ).pack(side="right")

        ctk.CTkLabel(
            scroll,
            text="Details",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(20, 10))

        self.teacher_comment = self._text_field(
            scroll,
            TEACHER_COMMENT_LABEL,
            self.report_card.teacher_comment or "",
        )
        self.principal_comment = self._text_field(
            scroll,
            PRINCIPAL_COMMENT_LABEL,
            self.report_card.principal_comment or "",
        )

        ctk.CTkLabel(
            scroll,
            text="Signatures",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(20, 10))

        self.teacher_signature = self._entry_field(
            scroll,
            TEACHER_SIGNATURE_LABEL,
            self.report_card.teacher_signature or "",
        )
        self.principal_signature = self._entry_field(
            scroll,
            PRINCIPAL_SIGNATURE_LABEL,
            self.report_card.principal_signature or "",
        )
        self.parent_signature = self._entry_field(
            scroll,
            PARENT_SIGNATURE_LABEL,
            self.report_card.parent_signature or "",
        )
        self.next_term_resumption_date = self._entry_field(
            scroll,
            "Next Term Resumption Date",
            self.report_card.next_term_resumption_date or "",
        )

        create_modal_footer(
            self,
            save_text=TextLabelManager.get_button_text("save"),
            save_command=self.save,
            cancel_command=self._close,
        )

        setup_modal_window(self, on_close=self._close)

    def _close(self):
        close_modal_window(self)

    def _get_or_create_report_card(self):
        record = self.session.query(ReportCard).filter_by(
            student_id=self.student.id,
            term=self.term,
        ).first()
        if record:
            return record
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = ReportCard(
            student_id=self.student.id,
            term=self.term,
            created_at=now,
            updated_at=now,
        )
        self.session.add(record)
        self.session.commit()
        return record

    def _text_field(self, parent, label, value):
        ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        box = ctk.CTkTextbox(
            parent,
            height=90,
            text_color=COLORS["text_primary"],
            **input_style(),
        )
        box.pack(fill="x", pady=(0, 12))
        if value:
            box.insert("1.0", value)
        return box

    def _entry_field(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(
            row,
            text=label,
            width=280,
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        entry = ctk.CTkEntry(
            row,
            width=360,
            height=38,
            text_color=COLORS["text_primary"],
            **input_style(),
        )
        entry.pack(side="right")
        if value:
            entry.insert(0, value)
        return entry

    def save(self):
        try:
            for field, var in self.rating_vars.items():
                value = var.get().strip()
                if not value:
                    setattr(self.report_card, field, None)
                    continue
                rating = int(value)
                if rating < 1 or rating > 5:
                    raise ValueError(f"Invalid rating for {field}")
                setattr(self.report_card, field, rating)

            self.report_card.teacher_comment = self.teacher_comment.get("1.0", "end").strip()
            self.report_card.principal_comment = self.principal_comment.get("1.0", "end").strip()
            self.report_card.teacher_signature = self.teacher_signature.get().strip()
            self.report_card.principal_signature = self.principal_signature.get().strip()
            self.report_card.parent_signature = self.parent_signature.get().strip()
            self.report_card.next_term_resumption_date = self.next_term_resumption_date.get().strip()
            self.report_card.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.session.commit()
            close_modal_window(
                self,
                on_after=self.on_saved,
                success_message="Report card details saved successfully.",
            )
        except ValueError as exc:
            show_error(self, "Validation Error", str(exc))
        except Exception as exc:
            self.session.rollback()
            show_error(self, "Error", f"Failed to save report card: {exc}")


class ReportCardsTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.students = []
        self.selected_student = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(
            top_row,
            text="Report Cards",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # Filters frame on new row inside header
        filters_frame = ctk.CTkFrame(header, fg_color="transparent")
        filters_frame.pack(fill="x", padx=20, pady=(10, 15))

        # Session
        ctk.CTkLabel(filters_frame, text="Session:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 3))
        self.session_var = ctk.StringVar()
        self.session_filter = ctk.CTkComboBox(filters_frame, variable=self.session_var, width=120, command=self._cascade_students)
        self.session_filter.pack(side="left", padx=(0, 5))
        
        # Dept
        ctk.CTkLabel(filters_frame, text="Dept:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_secondary"]).pack(side="left", padx=(5, 3))
        self.dept_var = ctk.StringVar()
        self.dept_filter = ctk.CTkComboBox(filters_frame, variable=self.dept_var, width=120, command=self._cascade_students)
        self.dept_filter.pack(side="left", padx=(0, 5))
        
        # Class
        ctk.CTkLabel(filters_frame, text="Class:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_secondary"]).pack(side="left", padx=(5, 3))
        self.class_var = ctk.StringVar(value="All Classes")
        self.class_filter = ctk.CTkComboBox(filters_frame, variable=self.class_var, values=["All Classes", "SSS1", "SSS2", "SSS3"], width=100, command=self._cascade_students)
        self.class_filter.pack(side="left", padx=(0, 5))

        # Student
        ctk.CTkLabel(filters_frame, text="Student:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_secondary"]).pack(side="left", padx=(5, 3))
        self.student_var = ctk.StringVar(value="")
        self.student_combo = ctk.CTkComboBox(
            filters_frame,
            variable=self.student_var,
            width=280,
            text_color=COLORS["text_primary"],
            command=self.on_student_selected,
            **input_style(),
        )
        self.student_combo.pack(side="left", padx=(0, 5))

        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        self.content.grid(row=1, column=0, sticky="nsew")
        enable_mousewheel_scrolling(self.content)

    def load_students(self):
        from models import AcademicSession, Department
        sessions = self.session.query(AcademicSession).order_by(AcademicSession.name.desc()).all()
        session_names = ["All Sessions"] + [s.name for s in sessions]
        self.session_filter.configure(values=session_names)
        self.session_var.set("All Sessions")

        depts = self.session.query(Department).all()
        dept_names = ["All Departments"] + [d.name for d in depts]
        self.dept_filter.configure(values=dept_names)
        self.dept_var.set("All Departments")
        
        self.class_var.set("All Classes")
        self._cascade_students()

    def _cascade_students(self, *_):
        from models import AcademicSession, Department
        query = self.session.query(Student)
        sess_name = self.session_var.get()
        dept_name = self.dept_var.get()
        cls_name = self.class_var.get()
        
        if sess_name != "All Sessions":
            sess = self.session.query(AcademicSession).filter_by(name=sess_name).first()
            if sess: query = query.filter_by(session_id=sess.id)
        if dept_name != "All Departments":
            dept = self.session.query(Department).filter_by(name=dept_name).first()
            if dept: query = query.filter_by(dept_id=dept.id)
        if cls_name and cls_name != "All Classes":
            query = query.filter_by(class_name=cls_name)
            
        self.students = query.order_by(Student.full_name).all()
        labels = [f"{student.full_name} ({student.student_id})" for student in self.students]
        
        if not labels:
            self.student_combo.configure(values=["No students found"], state="disabled")
            self.student_var.set("No students found")
            self.selected_student = None
            self.render_terms()
            return

        self.student_combo.configure(values=labels, state="normal")
        if not self.student_var.get() or self.student_var.get() not in labels:
            self.student_var.set(labels[0])
        self.on_student_selected(self.student_var.get())

    def on_student_selected(self, _value=None):
        label = self.student_var.get()
        self.selected_student = None
        for student in self.students:
            expected = f"{student.full_name} ({student.student_id})"
            if expected == label:
                self.selected_student = student
                break
        self.render_terms()
    def pick_student_photo(self):
        if not self.selected_student: return
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            import shutil
            import os
            # Copy to an assets/photos folder
            photos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "photos")
            os.makedirs(photos_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            dest_path = os.path.join(photos_dir, f"student_{self.selected_student.id}{ext}")
            shutil.copy(file_path, dest_path)
            
            # Save relative path for better portability
            rel_path = os.path.join("assets", "photos", f"student_{self.selected_student.id}{ext}")
            self.selected_student.profile_picture_path = rel_path
            self.session.commit()
            
            if hasattr(self, 'pic_status_label'):
                self.pic_status_label.configure(text="✅ Photo uploaded")
            show_info(self, "Success", "Student photo updated successfully.")

    def render_terms(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        if not self.selected_student:
            ctk.CTkLabel(
                self.content,
                text="Select a student to manage report cards.",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLORS["text_secondary"],
            ).pack(pady=40, padx=20)
            return

        student = self.selected_student
        
        # Profile Picture Section
        pic_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        pic_frame.pack(fill="x", padx=12, pady=(12, 12))
        
        ctk.CTkLabel(pic_frame, text="Student Photo:", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left", padx=(8, 15))
        
        pic_label_text = "✅ Photo uploaded" if getattr(student, 'profile_picture_path', None) else "❌ No photo"
        self.pic_status_label = ctk.CTkLabel(pic_frame, text=pic_label_text, font=ctk.CTkFont(family="Segoe UI", size=13), text_color=COLORS["text_secondary"])
        self.pic_status_label.pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(
            pic_frame, text="Upload Photo", command=self.pick_student_photo,
            width=120, height=32, corner_radius=8, fg_color=COLORS["secondary"], hover_color=COLORS["primary"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(side="left")

        list_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        list_frame.pack(fill="x", padx=12, pady=(12, 8))
        for col, weight in enumerate((4, 1, 1, 2)):
            list_frame.grid_columnconfigure(col, weight=weight)

        headers = ["Term", "Grades", "Details", "Actions"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                list_frame,
                text=text,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS["text_secondary"],
            ).grid(row=0, column=col, sticky="ew", padx=(12 if col == 0 else 8, 8), pady=(0, 6))

        for row_index, (term, term_name) in enumerate(TERM_OPTIONS, start=1):
            report_card = self.session.query(ReportCard).filter_by(
                student_id=student.id,
                term=term,
            ).first()
            marks_count = self.session.query(Mark).filter_by(
                student_id=student.id,
                term=term,
            ).count()
            complete = is_report_card_complete(report_card, student.id, term, self.session)
            row_bg = COLORS["sheet_row"] if row_index % 2 == 1 else COLORS["sheet_header"]
            cols = []

            term_label = f"{student.class_name} — {term_name}"
            cols.append(ctk.CTkLabel(
                list_frame,
                text=term_label,
                anchor="w",
                fg_color=row_bg,
                corner_radius=0,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_primary"],
            ))

            grades_text = f"{marks_count} subjects" if marks_count else "No grades"
            grades_color = COLORS["text_primary"] if marks_count else COLORS["danger"]
            cols.append(ctk.CTkLabel(
                list_frame,
                text=grades_text,
                anchor="w",
                fg_color=row_bg,
                corner_radius=0,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=grades_color,
            ))

            status_text = "Ready" if complete else "Incomplete"
            status_color = COLORS["success"] if complete else COLORS["warning"]
            cols.append(ctk.CTkLabel(
                list_frame,
                text=status_text,
                anchor="w",
                fg_color=row_bg,
                corner_radius=0,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=status_color,
            ))

            actions = ctk.CTkFrame(list_frame, fg_color=row_bg, corner_radius=0)
            ctk.CTkButton(
                actions,
                text="Edit" if report_card else "Create",
                width=88,
                height=32,
                corner_radius=8,
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                text_color=COLORS["text_on_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=lambda t=term: self.open_editor(t),
            ).pack(side="left", padx=(0, 6))
            download_state = "normal" if complete else "disabled"
            ctk.CTkButton(
                actions,
                text="Download",
                width=96,
                height=32,
                corner_radius=8,
                fg_color=COLORS["success"] if complete else COLORS["border"],
                hover_color=COLORS["success_hover"] if complete else COLORS["border"],
                text_color=COLORS["text_on_primary"] if complete else COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                state=download_state,
                command=lambda t=term: self.download_report_card(t),
            ).pack(side="left")
            cols.append(actions)

            for col, widget in enumerate(cols):
                widget.grid(
                    row=row_index,
                    column=col,
                    sticky="ew",
                    padx=(12 if col == 0 else 8, 8),
                    pady=4,
                )

    def open_editor(self, term):
        if not self.selected_student:
            return
        root = self.winfo_toplevel()
        ReportCardEditWindow(
            root,
            self.session,
            self.selected_student,
            term,
            on_saved=self.render_terms,
        )

    def download_report_card(self, term):
        if not self.selected_student:
            return

        student = self.selected_student
        report_card = self.session.query(ReportCard).filter_by(
            student_id=student.id,
            term=term,
        ).first()
        if not is_report_card_complete(report_card, student.id, term, self.session):
            show_warning(
                self,
                "Incomplete",
                "Complete and save all report card details before downloading.",
            )
            return

        filename = ask_save_filename(
            self,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=safe_export_filename(
                student.full_name,
                f"term{term}",
                "report_card",
                extension="pdf",
            ),
            title="Download Report Card",
        )
        if not filename:
            return

        if generate_report_card(student.id, term, filename):
            show_info(self, "Success", f"Report card saved to:\n{filename}")
        else:
            show_error(
                self,
                "Error",
                "Failed to generate report card. Ensure grades and saved details exist.",
            )
