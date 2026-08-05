"""
DepartmentsTab — manage departments and their subject lists.
"""
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from sqlalchemy.exc import IntegrityError
from models import Session as DBSession, Department, DepartmentSubject

COLORS = {
    "primary":       "#1a73e8",
    "primary_hover": "#1557b0",
    "bg_main":       "#ffffff",
    "bg_card":       "#f8f9fa",
    "text_primary":  "#202124",
    "text_secondary":"#5f6368",
    "border":        "#dadce0",
    "success":       "#34a853",
    "danger":        "#ea4335",
}

DEPT_NAMES = ["Science", "Art", "Commercial"]


class DepartmentsTab(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_main"], **kwargs)
        self.db = DBSession()
        self._current_dept = DEPT_NAMES[0]
        self._setup_ui()
        self.load_department(self._current_dept)

    def _setup_ui(self):
        # Title
        ctk.CTkLabel(
            self, text="Departments & Subjects",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Department selector tabs
        tab_row = ctk.CTkFrame(self, fg_color="transparent")
        tab_row.pack(fill="x", padx=20, pady=(0, 10))
        self._dept_buttons = {}
        for name in DEPT_NAMES:
            btn = ctk.CTkButton(
                tab_row, text=name, width=120, height=34,
                command=lambda n=name: self._switch_dept(n)
            )
            btn.pack(side="left", padx=4)
            self._dept_buttons[name] = btn
        self._update_tab_colors()

        # Subject list header
        subj_header = ctk.CTkFrame(self, fg_color="transparent")
        subj_header.pack(fill="x", padx=20, pady=(0, 5))
        self.dept_label = ctk.CTkLabel(
            subj_header, text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.dept_label.pack(side="left")
        ctk.CTkButton(
            subj_header, text="+ Add Subject", width=120, height=30,
            fg_color=COLORS["success"], hover_color="#2d8f47",
            command=self._add_subject
        ).pack(side="right")

        # Column headers
        col_frame = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0)
        col_frame.pack(fill="x", padx=20)
        for text, w in [("#", 40), ("Subject Name", 260), ("Classes Allowed", 200), ("Actions", 140)]:
            ctk.CTkLabel(col_frame, text=text, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").pack(side="left", padx=8, pady=8)

        # Scrollable subject list
        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_card"], corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Error label
        self.error_label = ctk.CTkLabel(
            self, text="", text_color=COLORS["danger"],
            font=ctk.CTkFont(size=11)
        )
        self.error_label.pack(pady=(0, 5))

    def _update_tab_colors(self):
        for name, btn in self._dept_buttons.items():
            if name == self._current_dept:
                btn.configure(fg_color=COLORS["primary"],
                              hover_color=COLORS["primary_hover"],
                              text_color="white")
            else:
                btn.configure(fg_color=COLORS["bg_card"],
                              hover_color=COLORS["border"],
                              text_color=COLORS["text_primary"])

    def _switch_dept(self, name: str):
        self._current_dept = name
        self._update_tab_colors()
        self.load_department(name)

    def load_department(self, dept_name: str):
        self._current_dept = dept_name
        self.dept_label.configure(text=f"Subjects in {dept_name}:")
        for w in self.list_frame.winfo_children():
            w.destroy()

        dept = self.db.query(Department).filter_by(name=dept_name).first()
        if not dept:
            ctk.CTkLabel(self.list_frame, text="Department not found.",
                         text_color=COLORS["danger"]).pack(pady=10)
            return

        subjects = self.db.query(DepartmentSubject).filter_by(dept_id=dept.id).all()
        if not subjects:
            ctk.CTkLabel(self.list_frame,
                         text="No subjects yet. Click '+ Add Subject'.",
                         text_color=COLORS["text_secondary"]).pack(pady=20)
            return

        for i, subj in enumerate(subjects):
            bg = COLORS["bg_main"] if i % 2 == 0 else COLORS["bg_card"]
            row = ctk.CTkFrame(self.list_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x")

            ctk.CTkLabel(row, text=str(i + 1), width=40,
                         text_color=COLORS["text_secondary"],
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=8, pady=7)
            ctk.CTkLabel(row, text=subj.subject_name, width=260,
                         text_color=COLORS["text_primary"],
                         font=ctk.CTkFont(size=12),
                         anchor="w").pack(side="left", padx=8)

            classes_str = subj.target_classes or "SSS1,SSS2,SSS3"
            allowed = [c.strip() for c in classes_str.split(",") if c.strip()]

            cls_frame = ctk.CTkFrame(row, fg_color="transparent", width=200)
            cls_frame.pack(side="left", padx=4)

            def make_toggle(target_subj, c_name):
                def toggle():
                    curr_classes = [c.strip() for c in (target_subj.target_classes or "SSS1,SSS2,SSS3").split(",") if c.strip()]
                    if c_name in curr_classes:
                        curr_classes.remove(c_name)
                    else:
                        curr_classes.append(c_name)
                    ordered = [c for c in ["SSS1", "SSS2", "SSS3"] if c in curr_classes]
                    target_subj.target_classes = ",".join(ordered)
                    self.db.commit()
                    self.notify_subject_changed()
                return toggle

            for c_name in ["SSS1", "SSS2", "SSS3"]:
                var = ctk.BooleanVar(value=(c_name in allowed))
                cb = ctk.CTkCheckBox(
                    cls_frame, text=c_name, variable=var,
                    command=make_toggle(subj, c_name),
                    width=55, height=20, font=ctk.CTkFont(size=11),
                    checkbox_width=16, checkbox_height=16
                )
                cb.pack(side="left", padx=2)

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="left", padx=8)
            ctk.CTkButton(
                btn_frame, text="Edit", width=60, height=26,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                command=lambda sid=subj.id, sname=subj.subject_name: self._edit_subject(sid, sname)
            ).pack(side="left", padx=3)
            ctk.CTkButton(
                btn_frame, text="Remove", width=70, height=26,
                fg_color=COLORS["danger"], hover_color="#c62828",
                command=lambda sid=subj.id, sname=subj.subject_name: self._remove_subject(sid, sname)
            ).pack(side="left", padx=3)


    def _add_subject(self):
        dept = self.db.query(Department).filter_by(name=self._current_dept).first()
        if not dept:
            return
        name = simpledialog.askstring("Add Subject",
                                      f"Subject name for {self._current_dept}:",
                                      parent=self)
        if not name or not name.strip():
            return
        self.add_subject(dept.id, name.strip())

    def add_subject(self, dept_id: int, subject_name: str):
        try:
            self.db.add(DepartmentSubject(dept_id=dept_id, subject_name=subject_name))
            self.db.commit()
            _ensure_core_subject(self.db, subject_name)
            self.error_label.configure(text="")
            self.load_department(self._current_dept)
            self.notify_subject_changed()
        except IntegrityError:
            self.db.rollback()
            self.error_label.configure(text=f"'{subject_name}' already exists in this department.")

    def _edit_subject(self, subject_id: int, current_name: str):
        new_name = simpledialog.askstring("Edit Subject",
                                          "New subject name:",
                                          initialvalue=current_name,
                                          parent=self)
        if not new_name or not new_name.strip() or new_name.strip() == current_name:
            return
        self.edit_subject(subject_id, new_name.strip())

    def edit_subject(self, subject_id: int, new_name: str):
        try:
            subj = self.db.query(DepartmentSubject).filter_by(id=subject_id).first()
            if subj:
                subj.subject_name = new_name
                self.db.commit()
                _ensure_core_subject(self.db, new_name)
                self.notify_subject_changed()
            self.error_label.configure(text="")
            self.load_department(self._current_dept)
        except IntegrityError:
            self.db.rollback()
            self.error_label.configure(text=f"'{new_name}' already exists in this department.")

    def _remove_subject(self, subject_id: int, name: str):
        if not messagebox.askyesno("Remove Subject",
                                   f"Remove '{name}' from {self._current_dept}?"):
            return
        self.remove_subject(subject_id)

    def remove_subject(self, subject_id: int):
        subj = self.db.query(DepartmentSubject).filter_by(id=subject_id).first()
        if subj:
            self.db.delete(subj)
            self.db.commit()
            self.notify_subject_changed()
        self.load_department(self._current_dept)

    def add_on_subject_changed_callback(self, cb):
        if not hasattr(self, "_callbacks"):
            self._callbacks = []
        self._callbacks.append(cb)

    def notify_subject_changed(self):
        for cb in getattr(self, "_callbacks", []):
            try:
                cb()
            except Exception:
                pass


def _ensure_core_subject(db, subject_name: str):
    """Ensure subject exists in core Subject table."""
    try:
        from models import Subject
        existing = db.query(Subject).filter_by(subject_name=subject_name).first()
        if not existing:
            base_code = "".join(e for e in subject_name if e.isalnum()).upper()[:5] or "SUBJ"
            code = base_code
            counter = 1
            while db.query(Subject).filter_by(subject_code=code).first():
                code = f"{base_code[:3]}{counter:02d}"
                counter += 1
            core_sub = Subject(subject_code=code, subject_name=subject_name)
            db.add(core_sub)
            db.commit()
    except Exception:
        db.rollback()

