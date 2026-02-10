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
        """Open student detail modal with attendance and results options."""
        if self.current_modal:
            self.close_current_modal()
        
        # Create overlay
        self.overlay = ctk.CTkToplevel(self.parent_window)
        self.overlay.title("Student Details")
        self.overlay.geometry("800x600")
        self.overlay.transient(self.parent_window)
        self.overlay.grab_set()
        
        # Center the modal
        parent_x = self.parent_window.winfo_rootx()
        parent_y = self.parent_window.winfo_rooty()
        parent_width = self.parent_window.winfo_width()
        parent_height = self.parent_window.winfo_height()
        
        x = parent_x + (parent_width // 2) - 400  # 400 is half of modal width
        y = parent_y + (parent_height // 2) - 300  # 300 is half of modal height
        
        self.overlay.geometry(f"800x600+{x}+{y}")
        
        # Configure modal
        self.overlay.configure(fg_color=("#f0f0f0", "#2a2a3e"))
        
        # Create modal content
        self.current_modal = StudentDetailModal(self.overlay, student_id, session, self.close_current_modal)
        
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


class StudentDetailModal(ctk.CTkFrame):
    """Modal window for displaying student details with attendance and results options."""
    
    def __init__(self, parent, student_id: int, session, close_callback: Callable):
        super().__init__(parent, fg_color="transparent")
        self.student_id = student_id
        self.session = session
        self.close_callback = close_callback
        self.current_view = None
        
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.setup_ui()
        self.load_student_data()
    
    def setup_ui(self):
        """Set up the modal UI structure."""
        # Header with close button
        header_frame = ctk.CTkFrame(self, fg_color=("#e0e0e0", "#2a2a3e"), corner_radius=12)
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Student Details",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=("#000000", "#ffffff")
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        close_btn = ctk.CTkButton(
            header_frame,
            text=TextLabelManager.get_button_text('close'),
            command=self.close_callback,
            width=80,
            height=35,
            corner_radius=8,
            fg_color=("#dc3545", "#dc3545"),
            hover_color=("#c82333", "#c82333"),
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        close_btn.pack(side="right", padx=20, pady=15)
        
        # Options frame
        options_frame = ctk.CTkFrame(self, fg_color=("#f8f9fa", "#1e1e2e"), corner_radius=12)
        options_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame,
            text="Select an option to view student information:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#6c757d", "#a0a0a0")
        ).pack(pady=(20, 10))
        
        # Option buttons
        buttons_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 20))
        
        attendance_btn = ctk.CTkButton(
            buttons_frame,
            text="View Attendance Records",
            command=self.show_attendance_view,
            width=200,
            height=50,
            corner_radius=10,
            fg_color=("#007bff", "#1a73e8"),
            hover_color=("#0056b3", "#1557b0"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        attendance_btn.pack(side="left", padx=10)
        
        results_btn = ctk.CTkButton(
            buttons_frame,
            text="View Results",
            command=self.show_results_view,
            width=200,
            height=50,
            corner_radius=10,
            fg_color=("#28a745", "#34a853"),
            hover_color=("#1e7e34", "#2d8f47"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        results_btn.pack(side="left", padx=10)
        
        # Content frame for dynamic views
        self.content_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#2a2a3e"), corner_radius=12)
        self.content_frame.pack(fill="both", expand=True)
    
    def load_student_data(self):
        """Load student data and update title."""
        from models import Student
        student = self.session.query(Student).filter_by(id=self.student_id).first()
        if student:
            self.title_label.configure(text=f"Student Details - {student.name}")
    
    def clear_content_frame(self):
        """Clear the content frame for new view."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_attendance_view(self):
        """Show attendance records for the student."""
        self.clear_content_frame()
        self.current_view = AttendanceRecordsView(self.content_frame, self.student_id, self.session)
        self.current_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_results_view(self):
        """Show academic results for the student."""
        self.clear_content_frame()
        self.current_view = ResultsView(self.content_frame, self.student_id, self.session)
        self.current_view.pack(fill="both", expand=True, padx=20, pady=20)


class AttendanceRecordsView(ctk.CTkFrame):
    """Dedicated view for student attendance records."""
    
    def __init__(self, parent, student_id: int, session):
        super().__init__(parent, fg_color="transparent")
        self.student_id = student_id
        self.session = session
        self.setup_ui()
        self.load_attendance_data()
    
    def setup_ui(self):
        """Set up attendance records UI."""
        # Header
        ctk.CTkLabel(
            self,
            text="Attendance Records",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#000000", "#ffffff")
        ).pack(pady=(0, 20))
        
        # Scrollable frame for records
        self.records_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#f8f9fa", "#1e1e2e"),
            corner_radius=8
        )
        self.records_frame.pack(fill="both", expand=True)
    
    def load_attendance_data(self):
        """Load and display attendance records."""
        from models import Attendance, Student
        
        student = self.session.query(Student).filter_by(id=self.student_id).first()
        if not student:
            ctk.CTkLabel(
                self.records_frame,
                text="Student not found",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=("#dc3545", "#dc3545")
            ).pack(pady=20)
            return
        
        records = self.session.query(Attendance).filter_by(
            student_id=self.student_id
        ).order_by(Attendance.date.desc()).all()
        
        if not records:
            ctk.CTkLabel(
                self.records_frame,
                text=TextLabelManager.get_status_text('no_data'),
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=("#6c757d", "#a0a0a0")
            ).pack(pady=20)
            return
        
        # Summary
        present_count = sum(1 for r in records if r.is_present)
        total_count = len(records)
        percentage = (present_count / total_count * 100) if total_count > 0 else 0
        
        summary_frame = ctk.CTkFrame(self.records_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            summary_frame,
            text=f"Summary: {present_count}/{total_count} days present ({percentage:.1f}%)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#28a745" if percentage >= 75 else "#ffc107" if percentage >= 50 else "#dc3545", 
                       "#34a853" if percentage >= 75 else "#fbbc04" if percentage >= 50 else "#ea4335")
        ).pack(anchor="w")
        
        # Records list
        for record in records:
            record_frame = ctk.CTkFrame(self.records_frame, fg_color=("#ffffff", "#3a3a4e"), corner_radius=6)
            record_frame.pack(fill="x", padx=20, pady=5)
            
            date_str = record.date if isinstance(record.date, str) else record.date.strftime("%Y-%m-%d")
            status_text = TextLabelManager.get_status_text('present' if record.is_present else 'absent')
            status_color = ("#28a745", "#34a853") if record.is_present else ("#dc3545", "#ea4335")
            
            ctk.CTkLabel(
                record_frame,
                text=f"{date_str}: {status_text}",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=status_color
            ).pack(side="left", padx=15, pady=10)


class ResultsView(ctk.CTkFrame):
    """Dedicated view for student academic results."""
    
    def __init__(self, parent, student_id: int, session):
        super().__init__(parent, fg_color="transparent")
        self.student_id = student_id
        self.session = session
        self.setup_ui()
        self.load_results_data()
    
    def setup_ui(self):
        """Set up results UI."""
        # Header
        ctk.CTkLabel(
            self,
            text="Academic Results",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#000000", "#ffffff")
        ).pack(pady=(0, 20))
        
        # Scrollable frame for results
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#f8f9fa", "#1e1e2e"),
            corner_radius=8
        )
        self.results_frame.pack(fill="both", expand=True)
    
    def load_results_data(self):
        """Load and display academic results."""
        from models import Mark, Student, Subject
        
        student = self.session.query(Student).filter_by(id=self.student_id).first()
        if not student:
            ctk.CTkLabel(
                self.results_frame,
                text="Student not found",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=("#dc3545", "#dc3545")
            ).pack(pady=20)
            return
        
        marks = self.session.query(Mark).filter_by(student_id=self.student_id).all()
        
        if not marks:
            ctk.CTkLabel(
                self.results_frame,
                text=TextLabelManager.get_status_text('no_data'),
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=("#6c757d", "#a0a0a0")
            ).pack(pady=20)
            return
        
        # Group by term
        by_term = {}
        for mark in marks:
            if mark.term not in by_term:
                by_term[mark.term] = []
            by_term[mark.term].append(mark)
        
        # Display results by term
        for term in sorted(by_term.keys()):
            term_marks = by_term[term]
            avg = sum(m.total for m in term_marks) / len(term_marks) if term_marks else 0
            
            # Term header
            term_frame = ctk.CTkFrame(self.results_frame, fg_color=("#e9ecef", "#2a2a3e"), corner_radius=8)
            term_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                term_frame,
                text=f"Term {term} (Average: {avg:.1f})",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=("#000000", "#ffffff")
            ).pack(side="left", padx=15, pady=10)
            
            # Export button
            ctk.CTkButton(
                term_frame,
                text="📄 Export Report Card",
                command=lambda t=term: self.export_report_card(t),
                width=160,
                height=35,
                corner_radius=8,
                fg_color=("#6c757d", "#5f6368"),
                hover_color=("#5a6268", "#4a4f54"),
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
            ).pack(side="right", padx=15, pady=10)
            
            # Marks for this term
            for mark in term_marks:
                mark_frame = ctk.CTkFrame(self.results_frame, fg_color=("#ffffff", "#3a3a4e"), corner_radius=6)
                mark_frame.pack(fill="x", padx=20, pady=3)
                
                grade_color = ("#28a745" if mark.grade in ['A', 'B'] else 
                              "#ffc107" if mark.grade in ['C', 'D'] else "#dc3545",
                              "#34a853" if mark.grade in ['A', 'B'] else 
                              "#fbbc04" if mark.grade in ['C', 'D'] else "#ea4335")
                
                ctk.CTkLabel(
                    mark_frame,
                    text=f"{mark.subject.subject_name}: {mark.total:.0f} ({mark.grade})",
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    text_color=grade_color
                ).pack(side="left", padx=15, pady=8)
    
    def export_report_card(self, term):
        """Export report card as PDF for the selected term."""
        from tkinter import filedialog
        from report_card_pdf import generate_report_card
        from models import Student
        
        try:
            # Get student info for filename
            student = self.session.query(Student).filter_by(id=self.student_id).first()
            if not student:
                messagebox.showerror("Error", "Student not found")
                return
            
            # Generate default filename
            default_filename = f"{student.name.replace(' ', '_')}_Term{term}_ReportCard.pdf"
            
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Save Report Card As"
            )
            
            if file_path:
                # Generate PDF
                success = generate_report_card(self.student_id, term, file_path)
                
                if success:
                    messagebox.showinfo(
                        "Success", 
                        f"Report card exported successfully!\n\nSaved to:\n{file_path}"
                    )
                else:
                    messagebox.showerror(
                        "Error", 
                        "Failed to generate report card. Please ensure the student has grades for this term."
                    )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while exporting:\n{str(e)}")