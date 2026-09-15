"""
Broadsheet tab: class results grid with class / department / term / session filters.
"""
import csv
from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox, filedialog

from models import Session, Student, Subject, Mark, Department, AcademicSession, get_department_subjects_for_class
from calculations import GradeCalculator
from ui_components import TextLabelManager, safe_export_filename

COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "secondary": "#5f6368",
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
}


class EnhancedBroadsheetTab(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.broadsheet_data = None
        self.students = []
        self.subjects = []
        self.current_term = 1
        self.current_class = ""
        self._loading = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))

        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(
            top_row,
            text=TextLabelManager.get_header_text("broadsheet"),
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            top_row,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"],
        )
        self.status_label.pack(side="left", padx=12)

        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            controls_frame,
            text="Session:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(5, 5))

        self.session_filter = ctk.CTkComboBox(
            controls_frame,
            values=["All Sessions"],
            width=130,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.session_filter.set("All Sessions")
        self.session_filter.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            controls_frame,
            text="Class:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(5, 5))

        self.class_filter = ctk.CTkComboBox(
            controls_frame,
            values=["SSS1", "SSS2", "SSS3"],
            width=100,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.class_filter.set("SSS1")
        self.class_filter.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            controls_frame,
            text="Dept:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(5, 5))

        self.dept_filter = ctk.CTkComboBox(
            controls_frame,
            values=["All Departments", "Science", "Art", "Commercial"],
            width=140,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.dept_filter.set("All Departments")
        self.dept_filter.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            controls_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(5, 5))

        self.term_filter = ctk.CTkComboBox(
            controls_frame,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=145,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.term_filter.set("1 - First Term")
        self.term_filter.pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            controls_frame,
            text="Load Report",
            command=self.load_enhanced_sheet,
            width=110,
            height=38,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).pack(side="left", padx=(0, 10))

        self.export_btn = ctk.CTkButton(
            controls_frame,
            text="Export CSV",
            command=self.export_enhanced_csv,
            state="disabled",
            width=100,
            height=38,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.export_btn.pack(side="left", padx=0)

        self.sheet_frame = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        self.sheet_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.sheet_frame.grid_rowconfigure(0, weight=0)

        self._load_session_options()
        self.session_filter.configure(command=lambda _v: self.load_enhanced_sheet())
        self.class_filter.configure(command=lambda _v: self.load_enhanced_sheet())
        self.dept_filter.configure(command=lambda _v: self.load_enhanced_sheet())
        self.term_filter.configure(command=lambda _v: self.load_enhanced_sheet())
        self.after(50, self.load_enhanced_sheet)

    def _load_session_options(self):
        sessions = self.session.query(AcademicSession).order_by(AcademicSession.name.desc()).all()
        values = ["All Sessions"] + [s.name for s in sessions]
        self.session_filter.configure(values=values)
        self.session_filter.set("All Sessions")

    def get_class_population(self, class_name):
        return self.session.query(Student).filter_by(class_name=class_name).count()

    def _sheet_cell(self, text, row, column, width=70, anchor="center", bold=False, bg=None):
        if bg is None:
            bg = COLORS["sheet_header"] if row == 0 else (
                COLORS["sheet_row_alt"] if row % 2 == 0 else COLORS["sheet_row"]
            )
        label = ctk.CTkLabel(
            self.sheet_frame,
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

    def _resolve_subjects(self, dept_choice, class_name):
        if dept_choice and dept_choice != "All Departments":
            dept_obj = self.session.query(Department).filter_by(name=dept_choice).first()
            if not dept_obj:
                return self.session.query(Subject).order_by(Subject.subject_name).all()
            dept_subs = get_department_subjects_for_class(self.session, dept_obj.id, class_name)
            names = [ds.subject_name for ds in dept_subs]
            if not names:
                return []
            return (
                self.session.query(Subject)
                .filter(Subject.subject_name.in_(names))
                .order_by(Subject.subject_name)
                .all()
            )
        return self.session.query(Subject).order_by(Subject.subject_name).all()

    def load_enhanced_sheet(self):
        if not hasattr(self, "sheet_frame") or self._loading:
            return
        self._loading = True
        try:
            self._render_sheet()
        except Exception as exc:
            messagebox.showerror("Broadsheet Error", f"Failed to load broadsheet:\n{exc}")
        finally:
            self._loading = False

    def _render_sheet(self):
        for widget in self.sheet_frame.winfo_children():
            widget.destroy()

        self.current_class = self.class_filter.get() or "SSS1"
        dept_choice = self.dept_filter.get() or "All Departments"
        term_value = self.term_filter.get() or "1 - First Term"
        self.current_term = int(str(term_value).split()[0])
        sess_name = self.session_filter.get() or "All Sessions"

        query = self.session.query(Student).filter_by(class_name=self.current_class)
        if sess_name != "All Sessions":
            sess = self.session.query(AcademicSession).filter_by(name=sess_name).first()
            if sess:
                query = query.filter_by(session_id=sess.id)
        if dept_choice != "All Departments":
            dept_obj = self.session.query(Department).filter_by(name=dept_choice).first()
            if dept_obj:
                query = query.filter_by(dept_id=dept_obj.id)

        self.students = query.order_by(Student.full_name).all()
        self.subjects = self._resolve_subjects(dept_choice, self.current_class)

        if not self.students:
            self._show_empty(f"No students in {self.current_class}")
            self.export_btn.configure(state="disabled")
            self.status_label.configure(text="(0 students)")
            self.broadsheet_data = None
            return

        if not self.subjects:
            self._show_empty(f"No subjects configured for {dept_choice}")
            self.export_btn.configure(state="disabled")
            self.status_label.configure(text=f"({len(self.students)} students · 0 subjects)")
            self.broadsheet_data = None
            return

        student_ids = [s.id for s in self.students]
        marks = (
            self.session.query(Mark)
            .filter(Mark.term == self.current_term, Mark.student_id.in_(student_ids))
            .all()
        )

        data_map = {s.id: {} for s in self.students}
        for mark in marks:
            if mark.student_id not in data_map:
                continue
            ca = float(mark.continuous_assessment or 0)
            exam = float(mark.exams or 0)
            total = ca + exam
            if total <= 0 and mark.total not in (None, ""):
                try:
                    total = float(mark.total)
                except (TypeError, ValueError):
                    total = 0
            # Keep blank cells when the student has no score at all
            if total == 0 and not ca and not exam and not mark.total:
                continue
            data_map[mark.student_id][mark.subject_id] = total

        self.broadsheet_data = data_map
        self.status_label.configure(
            text=f"({len(self.students)} students · {len(self.subjects)} subjects · Term {self.current_term})"
        )
        self.export_btn.configure(state="normal")

        headers = ["#", "Student ID", "Name", "Dept"] + [s.subject_code for s in self.subjects] + [
            "Total",
            "Avg",
            "Grade",
            "Pos",
        ]
        widths = [40, 130, 180, 100] + [64] * len(self.subjects) + [70, 70, 60, 50]

        for col, header in enumerate(headers):
            self._sheet_cell(
                header,
                0,
                col,
                width=widths[col] if col < len(widths) else 64,
                anchor="center" if col != 2 else "w",
                bold=True,
                bg=COLORS["sheet_header"],
            )

        ranked = []
        for student in self.students:
            scores = []
            for subject in self.subjects:
                value = data_map[student.id].get(subject.id)
                if isinstance(value, (int, float)):
                    scores.append(float(value))
            total = sum(scores)
            avg = total / len(scores) if scores else 0.0
            ranked.append((student.id, total, avg))

        ranked.sort(key=lambda item: (item[1], item[2]), reverse=True)
        positions = {}
        for index, (student_id, _total, _avg) in enumerate(ranked):
            if index > 0 and ranked[index - 1][1] == _total and ranked[index - 1][2] == _avg:
                positions[student_id] = positions[ranked[index - 1][0]]
            else:
                positions[student_id] = index + 1

        for row, student in enumerate(self.students, start=1):
            row_bg = COLORS["sheet_row"] if row % 2 == 1 else COLORS["sheet_row_alt"]
            dept_name = student.department.name if getattr(student, "department", None) else "-"

            self._sheet_cell(str(row), row, 0, width=40, bg=row_bg, anchor="center")
            self._sheet_cell(student.student_id, row, 1, width=130, bg=row_bg, anchor="w")
            self._sheet_cell(student.full_name, row, 2, width=180, bg=row_bg, anchor="w")
            self._sheet_cell(dept_name, row, 3, width=100, bg=row_bg, anchor="center")

            scores = []
            for col, subject in enumerate(self.subjects, start=4):
                value = data_map[student.id].get(subject.id, "-")
                if isinstance(value, (int, float)):
                    scores.append(float(value))
                    text = f"{value:.0f}"
                else:
                    text = "-"
                self._sheet_cell(text, row, col, width=64, bg=row_bg, anchor="center")

            total = sum(scores)
            avg = total / len(scores) if scores else 0.0
            grade = GradeCalculator.calculate_grade(avg) if scores else "-"
            pos = positions.get(student.id, "-")
            summary_col = len(self.subjects) + 4

            self._sheet_cell(f"{total:.0f}", row, summary_col, width=70, bold=True, bg=row_bg)
            self._sheet_cell(f"{avg:.1f}", row, summary_col + 1, width=70, bg=row_bg)
            self._sheet_cell(str(grade), row, summary_col + 2, width=60, bold=True, bg=row_bg)
            self._sheet_cell(str(pos), row, summary_col + 3, width=50, bold=True, bg=row_bg)

    def _show_empty(self, message):
        empty = ctk.CTkFrame(self.sheet_frame, fg_color="transparent")
        empty.grid(row=0, column=0, pady=60, padx=40)
        ctk.CTkLabel(
            empty,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack()
        ctk.CTkLabel(
            empty,
            text="Adjust the filters above, or enter marks in Grades Entry.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(6, 0))

    def export_enhanced_csv(self):
        if not self.broadsheet_data or not self.students or not self.subjects:
            messagebox.showwarning("No Data", "Load a broadsheet before exporting.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Broadsheet",
            initialfile=safe_export_filename(
                "Broadsheet",
                self.current_class,
                f"Term{self.current_term}",
                extension="csv",
            ),
        )
        if not filename:
            return

        try:
            ranked = []
            for student in self.students:
                scores = [
                    float(self.broadsheet_data[student.id][sub.id])
                    for sub in self.subjects
                    if isinstance(self.broadsheet_data[student.id].get(sub.id), (int, float))
                ]
                total = sum(scores)
                avg = total / len(scores) if scores else 0.0
                ranked.append((student.id, total, avg))
            ranked.sort(key=lambda item: (item[1], item[2]), reverse=True)
            positions = {student_id: index + 1 for index, (student_id, _, _) in enumerate(ranked)}

            with open(filename, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(
                    [
                        f"Broadsheet - {self.current_class} - Term {self.current_term}",
                        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    ]
                )
                writer.writerow([])
                writer.writerow(
                    ["#", "Student ID", "Name", "Department"]
                    + [sub.subject_code for sub in self.subjects]
                    + ["Total", "Average", "Grade", "Position"]
                )

                for index, student in enumerate(self.students, start=1):
                    dept_name = student.department.name if getattr(student, "department", None) else "-"
                    row = [index, student.student_id, student.full_name, dept_name]
                    scores = []
                    for subject in self.subjects:
                        value = self.broadsheet_data[student.id].get(subject.id, "")
                        if isinstance(value, (int, float)):
                            scores.append(float(value))
                            row.append(f"{value:.0f}")
                        else:
                            row.append("")
                    total = sum(scores)
                    avg = total / len(scores) if scores else 0.0
                    grade = GradeCalculator.calculate_grade(avg) if scores else ""
                    row.extend([f"{total:.0f}", f"{avg:.1f}", grade, positions.get(student.id, "")])
                    writer.writerow(row)

            messagebox.showinfo("Success", f"Broadsheet exported to:\n{filename}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to export: {exc}")
