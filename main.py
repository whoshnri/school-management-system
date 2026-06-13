import tkinter as tk
import customtkinter as ctk
import hashlib
import os
from enterprise_forms import EnterpriseSchoolManagementApp
from models import Session, Subject, Admin, Department, DepartmentSubject, AcademicSession, run_migrations
from validators import validate_email
from app_paths import find_asset

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

DEFAULT_ADMIN_USERNAME = "henrybassey2007@gmail.com"
DEFAULT_ADMIN_PASSWORD = "as5XIUdc"
SKIP_LOGIN = False

DEPARTMENT_DEFAULTS = {
    "Science":    ["English Language", "Mathematics", "Physics", "Chemistry",
                   "Biology", "Agricultural Science", "Further Mathematics",
                   "Geography", "Data Processing"],
    "Art":        ["English Language", "Mathematics", "Civic Education",
                   "Economics", "Geography", "Food and Nutrition",
                   "Literature in English", "Government", "History"],
    "Commercial": ["English Language", "Mathematics", "Civic Education",
                   "Economics", "Commerce", "Financial Accounting",
                   "Data Processing", "Business Studies", "Office Practice"],
}


def initialize_subjects():
    """Pre-populate Nigerian secondary school subjects."""
    session = Session()
    if session.query(Subject).count() == 0:
        subjects_data = [
            ("ENG", "English Language"), ("MATH", "Mathematics"), ("CIVIC", "Civic Education"),
            ("ECON", "Economics"), ("PHY", "Physics"), ("CHEM", "Chemistry"),
            ("BIO", "Biology"), ("AGRIC", "Agricultural Science"), ("FMATH", "Further Mathematics"),
            ("GEO", "Geography"), ("FOOD", "Food and Nutrition"), ("DATA", "Data Processing")
        ]
        for code, name in subjects_data:
            session.add(Subject(subject_code=code, subject_name=name))
        session.commit()
    session.close()


def initialize_departments():
    """Pre-seed departments and their default subjects on first run."""
    session = Session()
    if session.query(Department).count() == 0:
        for dept_name, subjects in DEPARTMENT_DEFAULTS.items():
            dept = Department(name=dept_name)
            session.add(dept)
            session.flush()
            for s in subjects:
                session.add(DepartmentSubject(dept_id=dept.id, subject_name=s))
        session.commit()
    session.close()


def initialize_admin():
    """Create default admin if none exists."""
    from datetime import datetime
    session = Session()
    if session.query(Admin).count() == 0:
        password_hash = hashlib.sha256(DEFAULT_ADMIN_PASSWORD.encode()).hexdigest()
        admin = Admin(
            username=DEFAULT_ADMIN_USERNAME,
            password_hash=password_hash,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_active=True
        )
        session.add(admin)
        session.commit()
    session.close()


class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback
        self.session = Session()
        self.is_loading = False

        self.root.title("GFA Admin Panel")
        self.root.geometry("450x600")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 225
        y = (self.root.winfo_screenheight() // 2) - 300
        self.root.geometry(f"450x600+{x}+{y}")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_main"])
        main_frame.pack(fill="both", expand=True)

        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))

        # App icon
        try:
            from PIL import Image
            icon_path = find_asset(("app_icon.png", "icon.jpg.jpeg", "icon.jpg"))
            if icon_path:
                img = Image.open(icon_path).resize((80, 80), Image.Resampling.LANCZOS)
                icon_photo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                ctk.CTkLabel(logo_frame, image=icon_photo, text="").pack()
        except Exception:
            pass

        ctk.CTkLabel(
            logo_frame, text="GFA Admin Panel",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            logo_frame, text="Admin Login",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(4, 0))

        # Login form card
        form_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        form_frame.pack(padx=40, pady=20, fill="x")

        ctk.CTkLabel(form_frame, text="Email",
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(20, 5))

        self.username_entry = ctk.CTkEntry(
            form_frame, placeholder_text="name@school.com",
            width=320, height=45, corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(padx=20, pady=(0, 15))

        ctk.CTkLabel(form_frame, text="Password",
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Enter your password",
            show="*", width=320, height=45, corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(padx=20, pady=(0, 10))

        self.error_label = ctk.CTkLabel(
            form_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"]
        )
        self.error_label.pack(pady=(0, 15))

        # Button frame with loader
        self.button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=(0, 25))

        self.login_button = ctk.CTkButton(
            self.button_frame, text="Login",
            command=self.attempt_login,
            width=320, height=55, corner_radius=10,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(size=18, weight="bold"),
            border_width=2,
            border_color=COLORS["primary"]
        )
        self.login_button.pack()

        self.loader_label = ctk.CTkLabel(
            self.button_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["primary"]
        )
        self.loader_label.pack(pady=(8, 0))
        self.loader_index = 0
        self.loader_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        self.root.bind("<Return>", lambda e: self.attempt_login())
        self.username_entry.focus()

    def _update_loader(self):
        """Update loader animation"""
        if self.is_loading:
            self.loader_label.configure(text=f"{self.loader_chars[self.loader_index % len(self.loader_chars)]} Logging in...")
            self.loader_index += 1
            self.root.after(100, self._update_loader)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            self.error_label.configure(text="Please enter your email")
            return
        ok, email_error = validate_email(username)
        if not ok:
            self.error_label.configure(text=email_error)
            return
        if not password:
            self.error_label.configure(text="Please enter your password")
            return

        # Show loader
        self.is_loading = True
        self.login_button.configure(state="disabled", fg_color="#cccccc")
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.error_label.configure(text="")
        self._update_loader()

        # Simulate authentication delay for smooth UX
        self.root.after(500, lambda: self._complete_login(username, password))

    def _complete_login(self, username, password):
        """Complete the login process after loader animation"""
        admin = self.session.query(Admin).filter_by(username=username, is_active=True).first()
        if not admin:
            self.error_label.configure(text="Invalid email or password")
            self._reset_login()
            return

        if admin.password_hash != hashlib.sha256(password.encode()).hexdigest():
            self.error_label.configure(text="Incorrect password")
            self._reset_login()
            return

        self.session.close()
        self.is_loading = False
        self.loader_label.configure(text="")
        self.on_success_callback(admin)

    def _reset_login(self):
        """Reset login button and fields"""
        self.is_loading = False
        self.loader_label.configure(text="")
        self.login_button.configure(state="normal", fg_color=COLORS["primary"])
        self.username_entry.configure(state="normal")
        self.password_entry.configure(state="normal")
        self.username_entry.focus()


def authenticate_admin(username, password):
    """Return the admin record if credentials are valid."""
    session = Session()
    try:
        admin = session.query(Admin).filter_by(username=username, is_active=True).first()
        if not admin:
            return None
        if admin.password_hash != hashlib.sha256(password.encode()).hexdigest():
            return None
        return admin
    finally:
        session.close()


def start_main_app(root, current_admin):
    for widget in root.winfo_children():
        widget.destroy()

    root.geometry("1200x800")
    root.title("GFA Admin Panel")
    root.resizable(True, True)

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 550
    y = (root.winfo_screenheight() // 2) - 400
    root.geometry(f"1100x800+{x}+{y}")

    EnterpriseSchoolManagementApp(root, current_admin)


if __name__ == "__main__":
    run_migrations()
    initialize_subjects()
    initialize_departments()
    initialize_admin()

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()

    if SKIP_LOGIN:
        admin = authenticate_admin(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
        if admin:
            start_main_app(root, admin)
        else:
            LoginWindow(root, lambda admin: start_main_app(root, admin))
    else:
        LoginWindow(root, lambda admin: start_main_app(root, admin))

    root.mainloop()
