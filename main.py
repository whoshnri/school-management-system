import tkinter as tk
import customtkinter as ctk
import hashlib
from enterprise_forms import EnterpriseSchoolManagementApp
from models import Session, Subject, Admin

# Modern color palette
COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "bg_dark": "#1e1e2e",
    "bg_card": "#2a2a3e",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "border": "#3a3a4e",
    "success": "#34a853",
    "danger": "#ea4335"
}


def initialize_subjects():
    """Pre-populate the 20 subjects"""
    session = Session()
    
    if session.query(Subject).count() == 0:
        subjects_data = [
            ("MATH", "Mathematics"), ("ENG", "English"), ("PHY", "Physics"),
            ("CHEM", "Chemistry"), ("BIO", "Biology"), ("HIST", "History"),
            ("GEO", "Geography"), ("COMM", "Commerce"), ("ACC", "Accounts"),
            ("AGRIC", "Agricultural Science"), ("LIT", "Literature"),
            ("FRENCH", "French"), ("ARABIC", "Arabic"), ("IRS", "Islamic Studies"),
            ("CRK", "Christian Knowledge"), ("CIVIC", "Civic Education"),
            ("COMP", "Computer Science"), ("FOOD", "Food & Nutrition"),
            ("ART", "Fine Arts"), ("MUSIC", "Music")
        ]
        
        for code, name in subjects_data:
            subject = Subject(subject_code=code, subject_name=name)
            session.add(subject)
        
        session.commit()
        print("20 subjects initialized successfully!")
    session.close()


def initialize_admin():
    """Create default admin if none exists"""
    from datetime import datetime
    session = Session()
    
    if session.query(Admin).count() == 0:
        # Create default admin
        password_hash = hashlib.sha256("as5XIUdc".encode()).hexdigest()
        admin = Admin(
            username="henrybassey2007@gmail.com",
            password_hash=password_hash,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_active=True
        )
        session.add(admin)
        session.commit()
        print("Default admin created: henrybassey2007@gmail.com")
    session.close()


class LoginWindow:
    """Login window for admin authentication."""
    
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback
        self.session = Session()
        
        self.root.title("School Management System - Login")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 225
        y = (self.root.winfo_screenheight() // 2) - 250
        self.root.geometry(f"450x500+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_dark"])
        main_frame.pack(fill="both", expand=True)
        
        # Logo section
        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        logo_frame.pack(pady=(50, 30))
        
        ctk.CTkLabel(
            logo_frame,
            text="🎓",
            font=ctk.CTkFont(size=60)
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="School Management System",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            logo_frame,
            text="Admin Login",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(5, 0))
        
        # Login form
        form_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        form_frame.pack(padx=40, pady=20, fill="x")
        
        # Email/Username
        ctk.CTkLabel(
            form_frame,
            text="Email / Username",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your email",
            width=320,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.username_entry.pack(padx=20, pady=(0, 15))
        
        # Password
        ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your password",
            show="●",
            width=320,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.password_entry.pack(padx=20, pady=(0, 10))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["danger"]
        )
        self.error_label.pack(pady=(0, 10))
        
        # Login button
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.attempt_login,
            width=320,
            height=50,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.login_btn.pack(padx=20, pady=(5, 25))
        
        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.attempt_login())
        self.username_entry.focus()
    
    def attempt_login(self):
        """Verify credentials and log in."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            self.error_label.configure(text="Please enter your email/username")
            return
        
        if not password:
            self.error_label.configure(text="Please enter your password")
            return
        
        # Check credentials
        admin = self.session.query(Admin).filter_by(username=username, is_active=True).first()
        
        if not admin:
            self.error_label.configure(text="Invalid email/username")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if admin.password_hash != password_hash:
            self.error_label.configure(text="Incorrect password")
            return
        
        # Success - close login and open main app
        self.session.close()
        self.on_success_callback(admin)


def start_main_app(root, current_admin):
    """Start the main application after successful login."""
    # Clear login window
    for widget in root.winfo_children():
        widget.destroy()
    
    # Resize for main app
    root.geometry("1100x800")
    root.title("Enterprise School Management System")
    root.resizable(True, True)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 550
    y = (root.winfo_screenheight() // 2) - 400
    root.geometry(f"1100x800+{x}+{y}")
    
    # Start main app
    app = EnterpriseSchoolManagementApp(root, current_admin)


if __name__ == "__main__":
    # Initialize database
    initialize_subjects()
    initialize_admin()
    
    # Set theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    
    # Start with login window
    login = LoginWindow(root, lambda admin: start_main_app(root, admin))
    
    root.mainloop()