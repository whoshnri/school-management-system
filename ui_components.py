"""
UI Components for School Management System
Provides professional text-based interface components and modal management.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Any
from datetime import datetime, date
from tkcalendar import DateEntry


class TextLabelManager:
    """Centralizes all text labels and button descriptions for consistent professional appearance."""
    
    # Button labels
    BUTTONS = {
        'view': 'View Details',
        'edit': 'Edit',
        'delete': 'Delete',
        'add': 'Add New',
        'save': 'Save',
        'cancel': 'Cancel',
        'close': 'Close',
        'load': 'Load',
        'export': 'Export',
        'register': 'Register Student',
        'clear': 'Clear All',
        'pay': 'Record Payment',
        'set': 'Set Amount',
        'today': 'Add Today',
        'add_date': 'Add Date'
    }
    
    # Section headers
    HEADERS = {
        'student_registration': 'New Student Registration',
        'student_directory': 'Student Directory',
        'marks_entry': 'Grades Entry',
        'broadsheet': 'Class Broadsheet',
        'attendance': 'Attendance Tracker',
        'fees': 'School Fees Management'
    }
    
    # Navigation items
    NAVIGATION = {
        'students': 'Students',
        'fees': 'Fees',
        'register': 'Register',
        'marks': 'Grades',
        'broadsheet': 'Broadsheet',
        'attendance': 'Attendance'
    }
    
    # Status messages
    STATUS = {
        'paid': 'Paid',
        'unpaid': 'Unpaid',
        'partial': 'Partial Payment',
        'present': 'Present',
        'absent': 'Absent',
        'no_data': 'No data available',
        'loading': 'Loading...'
    }
    
    @classmethod
    def get_button_text(cls, key: str) -> str:
        """Get professional button text by key."""
        return cls.BUTTONS.get(key, key.title())
    
    @classmethod
    def get_header_text(cls, key: str) -> str:
        """Get professional header text by key."""
        return cls.HEADERS.get(key, key.title())
    
    @classmethod
    def get_nav_text(cls, key: str) -> str:
        """Get professional navigation text by key."""
        return cls.NAVIGATION.get(key, key.title())
    
    @classmethod
    def get_status_text(cls, key: str) -> str:
        """Get professional status text by key."""
        return cls.STATUS.get(key, key.title())


class ModalController:
    """Manages modal windows for student details and other popup interfaces."""
    
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.current_modal = None
        self.overlay = None
    
    def open_student_detail_modal(self, student_id: int, session, on_close: Optional[Callable] = None):
        """Open student detail modal with options to view bio data, attendance, and results."""
        from student_details_windows import StudentBioDataWindow, StudentAttendanceWindow, StudentResultsWindow
        from models import Student
        
        if self.current_modal:
            self.close_current_modal()
        
        # Create menu overlay
        self.overlay = ctk.CTkToplevel(self.parent_window)
        self.overlay.title("Student Details")
        self.overlay.geometry("500x400")
        self.overlay.transient(self.parent_window)
        
        # Center the modal
        parent_x = self.parent_window.winfo_rootx()
        parent_y = self.parent_window.winfo_rooty()
        parent_width = self.parent_window.winfo_width()
        parent_height = self.parent_window.winfo_height()
        
        x = parent_x + (parent_width // 2) - 250
        y = parent_y + (parent_height // 2) - 200
        
        self.overlay.geometry(f"500x400+{x}+{y}")
        self.overlay.update_idletasks()
        self.overlay.grab_set()
        self.overlay.configure(fg_color=("#f0f0f0", "#2a2a3e"))
        
        # Get student info
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            messagebox.showerror("Error", "Student not found")
            self.close_current_modal()
            return
        
        # Create menu content
        menu_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        ctk.CTkLabel(
            menu_frame,
            text="Student Details",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=("#000000", "#ffffff")
        ).pack(pady=(0, 10))
        
        # Student info
        ctk.CTkLabel(
            menu_frame,
            text=f"{student.full_name}\n{student.student_id} | {student.class_name}",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#6c757d", "#a0a0a0")
        ).pack(pady=(0, 30))
        
        # Menu buttons
        def open_bio_data():
            self.close_current_modal()
            StudentBioDataWindow(self.parent_window, student_id, session)
        
        def open_attendance():
            self.close_current_modal()
            StudentAttendanceWindow(self.parent_window, student_id, session)
        
        def open_results():
            self.close_current_modal()
            StudentResultsWindow(self.parent_window, student_id, session)
        
        ctk.CTkButton(
            menu_frame,
            text="View & Export Bio Data",
            command=open_bio_data,
            width=300,
            height=50,
            corner_radius=10,
            fg_color=("#007bff", "#1a73e8"),
            hover_color=("#0056b3", "#1557b0"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkButton(
            menu_frame,
            text="View Attendance Records",
            command=open_attendance,
            width=300,
            height=50,
            corner_radius=10,
            fg_color=("#28a745", "#34a853"),
            hover_color=("#1e7e34", "#2d8f47"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkButton(
            menu_frame,
            text="View Academic Results",
            command=open_results,
            width=300,
            height=50,
            corner_radius=10,
            fg_color=("#6f42c1", "#8e44ad"),
            hover_color=("#5a32a3", "#7d3c98"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=10)
        
        # Close button
        ctk.CTkButton(
            menu_frame,
            text="Close",
            command=self.close_current_modal,
            width=150,
            height=40,
            corner_radius=8,
            fg_color=("#6c757d", "#5f6368"),
            hover_color=("#5a6268", "#4a4f54"),
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(pady=(20, 0))
        
        # Handle window close
        self.overlay.protocol("WM_DELETE_WINDOW", self.close_current_modal)
        
        # Bind ESC key to close
        self.overlay.bind("<Escape>", lambda e: self.close_current_modal())
        self.overlay.focus_set()
    
    def close_current_modal(self):
        """Close the current modal window."""
        if self.current_modal:
            self.current_modal = None
        if self.overlay:
            self.overlay.grab_release()
            self.overlay.destroy()
            self.overlay = None
