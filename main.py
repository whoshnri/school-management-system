import tkinter as tk
from tkinter import messagebox
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
        self.secret_mask = "●"
        self.reset_admin = None
        self.reset_dialog = None

        self.root.title("Admin Panel")
        self.root.geometry("450x640")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 225
        y = (self.root.winfo_screenheight() // 2) - 320
        self.root.geometry(f"450x640+{x}+{y}")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_main"])
        main_frame.pack(fill="both", expand=True)

        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))

        # App icon
        try:
            from PIL import Image
            icon_path = find_asset(("assets/school-logo.jpeg", "school-logo.jpeg", "app_icon.png", "icon.jpg.jpeg", "icon.jpg"))
            if icon_path:
                img = Image.open(icon_path).resize((80, 80), Image.Resampling.LANCZOS)
                icon_photo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                ctk.CTkLabel(logo_frame, image=icon_photo, text="").pack()
        except Exception:
            pass

        ctk.CTkLabel(
            logo_frame, text="Admin Panel",
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

        self.email_entry = ctk.CTkEntry(
            form_frame, placeholder_text="name@school.com",
            width=320, height=45, corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.email_entry.pack(padx=20, pady=(0, 15))

        ctk.CTkLabel(form_frame, text="Password",
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Enter your password",
            show=self.secret_mask, width=320, height=45, corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(padx=20, pady=(0, 10))

        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(
            form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self._toggle_login_password_visibility,
            text_color=COLORS["text_secondary"],
            checkbox_width=18,
            checkbox_height=18,
        )
        self.show_password_checkbox.pack(anchor="w", padx=20, pady=(0, 12))

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

        self.forgot_password_button = ctk.CTkButton(
            self.button_frame,
            text="Forgot password?",
            command=self.open_forgot_password_dialog,
            width=320,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            text_color=COLORS["primary"],
            hover_color=COLORS["bg_card"],
            font=ctk.CTkFont(size=13, weight="bold"),
            border_width=0,
        )
        self.forgot_password_button.pack(pady=(6, 0))

        self.loader_label = ctk.CTkLabel(
            self.button_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["primary"]
        )
        self.loader_label.pack(pady=(8, 0))
        self.loader_index = 0
        self.loader_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        self.root.bind("<Return>", lambda e: self.attempt_login())
        self.email_entry.focus()

    def _update_loader(self):
        """Update loader animation"""
        if self.is_loading:
            self.loader_label.configure(text=f"{self.loader_chars[self.loader_index % len(self.loader_chars)]} Logging in...")
            self.loader_index += 1
            self.root.after(100, self._update_loader)

    def _hash_secret(self, secret_value):
        return hashlib.sha256(secret_value.encode()).hexdigest()

    def _toggle_login_password_visibility(self):
        self.password_entry.configure(show="" if self.show_password_var.get() else self.secret_mask)

    def _toggle_secret_entries(self, entries, reveal):
        show_value = "" if reveal else self.secret_mask
        for entry in entries:
            entry.configure(show=show_value)

    def _build_dialog_shell(self, title):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("420x340")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_main"])
        dialog_frame.pack(fill="both", expand=True, padx=20, pady=20)
        return dialog, dialog_frame

    def open_forgot_password_dialog(self):
        if self.is_loading:
            return

        if self.reset_dialog:
            try:
                if self.reset_dialog.winfo_exists():
                    self.reset_dialog.focus()
                    return
            except Exception:
                self.reset_dialog = None

        self.reset_admin = None
        self.reset_dialog, self.reset_dialog_frame = self._build_dialog_shell("Forgot Password")
        self.reset_dialog.protocol("WM_DELETE_WINDOW", self._close_reset_dialog)
        self._render_reset_email_step()

    def _close_reset_dialog(self):
        if self.reset_dialog:
            try:
                if self.reset_dialog.winfo_exists():
                    self.reset_dialog.destroy()
            except Exception:
                pass
        self.reset_dialog = None
        self.reset_admin = None

    def _clear_reset_dialog_content(self):
        for widget in self.reset_dialog_frame.winfo_children():
            widget.destroy()

    def _render_reset_email_step(self):
        self._clear_reset_dialog_content()
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text="Reset Password",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text="Enter your admin email to continue.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 18))

        self.reset_email_entry = ctk.CTkEntry(
            self.reset_dialog_frame,
            placeholder_text="name@school.com",
            width=360,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
        )
        self.reset_email_entry.pack(anchor="w")
        self.reset_email_entry.focus()

        self.reset_error_label = ctk.CTkLabel(
            self.reset_dialog_frame,
            text="",
            text_color=COLORS["danger"],
            font=ctk.CTkFont(size=12),
        )
        self.reset_error_label.pack(anchor="w", pady=(8, 14))

        ctk.CTkButton(
            self.reset_dialog_frame,
            text="Continue",
            command=self._submit_reset_email,
            width=360,
            height=42,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

    def _submit_reset_email(self):
        email = self.reset_email_entry.get().strip()
        if not email:
            self.reset_error_label.configure(text="Please enter your email.")
            return
        valid, email_error = validate_email(email)
        if not valid:
            self.reset_error_label.configure(text=email_error)
            return

        admin = self.session.query(Admin).filter_by(username=email, is_active=True).first()
        if not admin:
            self.reset_error_label.configure(text="No active administrator account found for this email.")
            return
        if not admin.recovery_pin_hash:
            self.reset_error_label.configure(text="Recovery PIN is not set for this admin. Contact another admin.")
            return

        self.reset_admin = admin
        self._render_reset_pin_step()

    def _render_reset_pin_step(self):
        self._clear_reset_dialog_content()
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text="Verify Recovery PIN",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text=f"Email: {self.reset_admin.username}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 6))
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text="Enter the recovery PIN for this admin account.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 14))

        self.reset_pin_entry = ctk.CTkEntry(
            self.reset_dialog_frame,
            placeholder_text="Recovery PIN",
            width=360,
            height=42,
            corner_radius=8,
            show=self.secret_mask,
            font=ctk.CTkFont(size=14),
        )
        self.reset_pin_entry.pack(anchor="w")
        self.reset_pin_entry.focus()

        self.reset_show_pin_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.reset_dialog_frame,
            text="Show PIN",
            variable=self.reset_show_pin_var,
            command=lambda: self._toggle_secret_entries([self.reset_pin_entry], self.reset_show_pin_var.get()),
            text_color=COLORS["text_secondary"],
            checkbox_width=18,
            checkbox_height=18,
        ).pack(anchor="w", pady=(8, 8))

        self.reset_error_label = ctk.CTkLabel(
            self.reset_dialog_frame,
            text="",
            text_color=COLORS["danger"],
            font=ctk.CTkFont(size=12),
        )
        self.reset_error_label.pack(anchor="w", pady=(0, 14))

        ctk.CTkButton(
            self.reset_dialog_frame,
            text="Verify PIN",
            command=self._submit_reset_pin,
            width=360,
            height=42,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

    def _submit_reset_pin(self):
        pin = self.reset_pin_entry.get().strip()
        if not pin:
            self.reset_error_label.configure(text="Please enter your recovery PIN.")
            return
        if self._hash_secret(pin) != self.reset_admin.recovery_pin_hash:
            self.reset_error_label.configure(text="Incorrect recovery PIN.")
            return

        self._render_new_password_step()

    def _render_new_password_step(self):
        self._clear_reset_dialog_content()
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text="Set New Password",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            self.reset_dialog_frame,
            text="Enter and confirm your new password.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 14))

        self.reset_new_password_entry = ctk.CTkEntry(
            self.reset_dialog_frame,
            placeholder_text="New password",
            width=360,
            height=42,
            corner_radius=8,
            show=self.secret_mask,
            font=ctk.CTkFont(size=14),
        )
        self.reset_new_password_entry.pack(anchor="w", pady=(0, 8))

        self.reset_confirm_password_entry = ctk.CTkEntry(
            self.reset_dialog_frame,
            placeholder_text="Confirm new password",
            width=360,
            height=42,
            corner_radius=8,
            show=self.secret_mask,
            font=ctk.CTkFont(size=14),
        )
        self.reset_confirm_password_entry.pack(anchor="w")
        self.reset_new_password_entry.focus()

        self.reset_show_new_pw_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.reset_dialog_frame,
            text="Show password fields",
            variable=self.reset_show_new_pw_var,
            command=lambda: self._toggle_secret_entries(
                [self.reset_new_password_entry, self.reset_confirm_password_entry],
                self.reset_show_new_pw_var.get(),
            ),
            text_color=COLORS["text_secondary"],
            checkbox_width=18,
            checkbox_height=18,
        ).pack(anchor="w", pady=(8, 8))

        self.reset_error_label = ctk.CTkLabel(
            self.reset_dialog_frame,
            text="",
            text_color=COLORS["danger"],
            font=ctk.CTkFont(size=12),
        )
        self.reset_error_label.pack(anchor="w", pady=(0, 14))

        ctk.CTkButton(
            self.reset_dialog_frame,
            text="Reset Password",
            command=self._submit_new_password,
            width=360,
            height=42,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

    def _submit_new_password(self):
        new_password = self.reset_new_password_entry.get()
        confirm_password = self.reset_confirm_password_entry.get()

        if not new_password or not confirm_password:
            self.reset_error_label.configure(text="Please fill in both password fields.")
            return
        if len(new_password) < 4:
            self.reset_error_label.configure(text="Password must be at least 4 characters.")
            return
        if new_password != confirm_password:
            self.reset_error_label.configure(text="Passwords do not match.")
            return

        try:
            admin = self.session.query(Admin).filter_by(id=self.reset_admin.id, is_active=True).first()
            if not admin:
                self.reset_error_label.configure(text="Admin account is no longer available.")
                return
            admin.password_hash = self._hash_secret(new_password)
            self.session.commit()
        except Exception as err:
            self.session.rollback()
            self.reset_error_label.configure(text=f"Could not reset password: {err}")
            return

        self._close_reset_dialog()
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
        self.email_entry.focus()
        messagebox.showinfo("Success", "Password reset complete. You can now log in with the new password.")

    def _prompt_recovery_pin_setup(self, admin):
        if admin.recovery_pin_hash:
            return True

        dialog, dialog_frame = self._build_dialog_shell("Set Recovery PIN")
        dialog.geometry("420x360")
        setup_state = {"completed": False}

        ctk.CTkLabel(
            dialog_frame,
            text="Set Recovery PIN",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            dialog_frame,
            text="A recovery PIN is required for forgot-password reset.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 18))

        pin_entry = ctk.CTkEntry(
            dialog_frame,
            placeholder_text="Recovery PIN (4+ digits)",
            width=360,
            height=42,
            corner_radius=8,
            show=self.secret_mask,
            font=ctk.CTkFont(size=14),
        )
        pin_entry.pack(anchor="w", pady=(0, 8))

        confirm_entry = ctk.CTkEntry(
            dialog_frame,
            placeholder_text="Confirm recovery PIN",
            width=360,
            height=42,
            corner_radius=8,
            show=self.secret_mask,
            font=ctk.CTkFont(size=14),
        )
        confirm_entry.pack(anchor="w")
        pin_entry.focus()

        show_pin_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            dialog_frame,
            text="Show PIN fields",
            variable=show_pin_var,
            command=lambda: self._toggle_secret_entries([pin_entry, confirm_entry], show_pin_var.get()),
            text_color=COLORS["text_secondary"],
            checkbox_width=18,
            checkbox_height=18,
        ).pack(anchor="w", pady=(8, 8))

        error_label = ctk.CTkLabel(
            dialog_frame,
            text="",
            text_color=COLORS["danger"],
            font=ctk.CTkFont(size=12),
        )
        error_label.pack(anchor="w", pady=(0, 14))

        def save_pin():
            pin_value = pin_entry.get().strip()
            confirm_value = confirm_entry.get().strip()
            if not pin_value or not confirm_value:
                error_label.configure(text="Both PIN fields are required.")
                return
            if not pin_value.isdigit() or len(pin_value) < 4:
                error_label.configure(text="Recovery PIN must be at least 4 digits.")
                return
            if pin_value != confirm_value:
                error_label.configure(text="PIN values do not match.")
                return

            try:
                admin_record = self.session.query(Admin).filter_by(id=admin.id, is_active=True).first()
                if not admin_record:
                    error_label.configure(text="Admin account is no longer available.")
                    return
                admin_record.recovery_pin_hash = self._hash_secret(pin_value)
                self.session.commit()
                admin.recovery_pin_hash = admin_record.recovery_pin_hash
            except Exception as err:
                self.session.rollback()
                error_label.configure(text=f"Could not save recovery PIN: {err}")
                return

            setup_state["completed"] = True
            dialog.destroy()

        ctk.CTkButton(
            dialog_frame,
            text="Save PIN and Continue",
            command=save_pin,
            width=360,
            height=42,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        self.root.wait_window(dialog)
        return setup_state["completed"]

    def attempt_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email:
            self.error_label.configure(text="Please enter your email")
            return
        ok, email_error = validate_email(email)
        if not ok:
            self.error_label.configure(text=email_error)
            return
        if not password:
            self.error_label.configure(text="Please enter your password")
            return

        # Show loader
        self.is_loading = True
        self.login_button.configure(state="disabled", fg_color="#cccccc")
        self.email_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.show_password_checkbox.configure(state="disabled")
        self.forgot_password_button.configure(state="disabled")
        self.error_label.configure(text="")
        self._update_loader()

        # Simulate authentication delay for smooth UX
        self.root.after(500, lambda: self._complete_login(email, password))

    def _complete_login(self, email, password):
        """Complete the login process after loader animation"""
        admin = self.session.query(Admin).filter_by(username=email, is_active=True).first()
        if not admin:
            self.error_label.configure(text="Invalid email or password")
            self._reset_login()
            return

        if admin.password_hash != self._hash_secret(password):
            self.error_label.configure(text="Incorrect password")
            self._reset_login()
            return

        if not self._prompt_recovery_pin_setup(admin):
            self.error_label.configure(text="Recovery PIN setup is required before access is granted.")
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
        self.email_entry.configure(state="normal")
        self.password_entry.configure(state="normal")
        self.show_password_checkbox.configure(state="normal")
        self.forgot_password_button.configure(state="normal")
        self.email_entry.focus()


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
    root.title("Admin Panel")
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
