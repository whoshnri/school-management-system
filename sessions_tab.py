"""
SessionsTab — manage academic sessions (e.g. 2024/2025).
"""
import re
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError
from models import Session as DBSession, AcademicSession

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

SESSION_PATTERN = re.compile(r'^(\d{4})/(\d{4})$')


def validate_session_name(name: str) -> bool:
    m = SESSION_PATTERN.match(name.strip())
    if not m:
        return False
    return int(m.group(2)) == int(m.group(1)) + 1


class SessionsTab(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_main"], **kwargs)
        self.db = DBSession()
        self._setup_ui()
        self.load_sessions()

    def _setup_ui(self):
        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header, text="Academic Sessions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ New Session",
            command=self._show_add_dialog,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            width=130, height=34
        ).pack(side="right")

        # Column headers
        col_frame = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0)
        col_frame.pack(fill="x", padx=20)
        for text, w in [("Session Name", 200), ("Status", 120), ("Actions", 200)]:
            ctk.CTkLabel(
                col_frame, text=text, width=w,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).pack(side="left", padx=10, pady=8)

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_card"], corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Inline error label
        self.error_label = ctk.CTkLabel(
            self, text="", text_color=COLORS["danger"],
            font=ctk.CTkFont(size=11)
        )
        self.error_label.pack(pady=(0, 5))

    def load_sessions(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        sessions = self.db.query(AcademicSession).order_by(AcademicSession.name.desc()).all()
        if not sessions:
            ctk.CTkLabel(
                self.list_frame, text="No sessions yet. Click '+ New Session' to add one.",
                text_color=COLORS["text_secondary"]
            ).pack(pady=20)
            return

        for i, sess in enumerate(sessions):
            bg = COLORS["bg_main"] if i % 2 == 0 else COLORS["bg_card"]
            row = ctk.CTkFrame(self.list_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x")

            status_text = "Active" if sess.is_active else "Inactive"
            status_color = COLORS["success"] if sess.is_active else COLORS["text_secondary"]

            ctk.CTkLabel(row, text=sess.name, width=200,
                         text_color=COLORS["text_primary"],
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=status_text, width=120,
                         text_color=status_color,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="left", padx=10)

            if not sess.is_active:
                ctk.CTkButton(
                    btn_frame, text="Set Active", width=90, height=28,
                    fg_color=COLORS["success"], hover_color="#2d8f47",
                    command=lambda sid=sess.id: self._set_active(sid)
                ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_frame, text="Delete", width=70, height=28,
                fg_color=COLORS["danger"], hover_color="#c62828",
                command=lambda sid=sess.id, sname=sess.name: self._delete(sid, sname)
            ).pack(side="left", padx=4)

    def _show_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("New Academic Session")
        dialog.geometry("360x200")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["bg_card"])
        dialog.update_idletasks()
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Session Name (e.g. 2024/2025)",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_primary"]).pack(pady=(20, 5))
        entry = ctk.CTkEntry(dialog, width=260, placeholder_text="YYYY/YYYY+1")
        entry.pack(pady=5)
        err = ctk.CTkLabel(dialog, text="", text_color=COLORS["danger"],
                           font=ctk.CTkFont(size=11))
        err.pack()

        def submit():
            name = entry.get().strip()
            if not validate_session_name(name):
                err.configure(text="Invalid format. Use YYYY/YYYY+1 (e.g. 2024/2025)")
                return
            self.create_session(name)
            dialog.destroy()

        ctk.CTkButton(dialog, text="Create", command=submit,
                      fg_color=COLORS["primary"],
                      hover_color=COLORS["primary_hover"]).pack(pady=10)
        entry.bind("<Return>", lambda e: submit())
        entry.focus()

    def create_session(self, name: str):
        try:
            sess = AcademicSession(name=name, is_active=False)
            self.db.add(sess)
            self.db.commit()
            self.error_label.configure(text="")
            self.load_sessions()
            self.notify_sessions_changed()
        except IntegrityError:
            self.db.rollback()
            self.error_label.configure(text=f"Session '{name}' already exists.")

    def _set_active(self, session_id: int):
        self.db.query(AcademicSession).update({"is_active": False})
        sess = self.db.query(AcademicSession).filter_by(id=session_id).first()
        if sess:
            sess.is_active = True
        self.db.commit()
        self.load_sessions()
        self.notify_sessions_changed()

    def _delete(self, session_id: int, name: str):
        if not messagebox.askyesno("Delete Session",
                                   f"Delete session '{name}'? This cannot be undone."):
            return
        sess = self.db.query(AcademicSession).filter_by(id=session_id).first()
        if sess:
            self.db.delete(sess)
            self.db.commit()
            self.notify_sessions_changed()
        self.load_sessions()

    def add_on_sessions_changed_callback(self, cb):
        if not hasattr(self, "_callbacks"):
            self._callbacks = []
        self._callbacks.append(cb)

    def notify_sessions_changed(self):
        for cb in getattr(self, "_callbacks", []):
            try:
                cb()
            except Exception:
                pass

    def get_active_session(self):
        """Return the currently active AcademicSession or None."""
        return self.db.query(AcademicSession).filter_by(is_active=True).first()

    def get_all_sessions(self):
        return self.db.query(AcademicSession).order_by(AcademicSession.name.desc()).all()

