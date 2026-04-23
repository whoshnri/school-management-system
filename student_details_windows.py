"""
Enhanced Student Details Windows
Separate windows for viewing bio data, attendance, and results with export functionality
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from models import Session, Student, Attendance, Mark, Subject
from datetime import datetime
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Modern color palette
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
    "border": "#dadce0"
}


class StudentBioDataWindow(ctk.CTkToplevel):
    """Window for viewing and exporting student bio data."""
    
    def __init__(self, parent, student_id, session):
        super().__init__(parent)
        self.student_id = student_id
        self.session = session
        self.student = None
        
        self.title("Student Bio Data")
        
        # Reduce window height to fit screen better
        screen_height = self.winfo_screenheight()
        window_height = min(650, int(screen_height * 0.8))  # 80% of screen or 650px max
        self.geometry(f"700x{window_height}")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 350
        y = (self.winfo_screenheight() // 2) - (window_height // 2)
        self.geometry(f"700x{window_height}+{x}+{y}")
        
        self.configure(fg_color=COLORS["bg_dark"])
        
        self.setup_ui()
        self.load_student_data()
    
    def setup_ui(self):
        """Set up the bio data UI."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0)
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="Student Bio Data",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)
        
        # Export button
        ctk.CTkButton(
            header_frame,
            text="Export to PDF",
            command=self.export_bio_data,
            width=140,
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="right", padx=20, pady=15)
        
        # Scrollable content
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    
    def load_student_data(self):
        """Load and display student bio data."""
        self.student = self.session.query(Student).filter_by(id=self.student_id).first()
        
        if not self.student:
            messagebox.showerror("Error", "Student not found")
            self.destroy()
            return
        
        # Display all student information
        self.create_info_section("Personal Information", [
            ("Student ID", self.student.student_id),
            ("Full Name", self.student.full_name),
            ("Date of Birth", self.student.date_of_birth.strftime("%Y-%m-%d")),
            ("Age", f"{self.student.age} years"),
            ("Sex", self.student.sex),
            ("Class", self.student.class_name),
            ("Admission Year", str(self.student.admission_year)),
            ("State of Origin", self.student.state_of_origin)
        ])
        
        self.create_info_section("Contact Information", [
            ("Home Address", self.student.home_address),
            ("Phone Number", self.student.phone_number or "Not provided")
        ])
        
        self.create_info_section("Guardian/Parent Information", [
            ("Guardian Name", self.student.guardian_name),
            ("Guardian Phone", self.student.guardian_phone),
            ("Guardian Address", self.student.guardian_address)
        ])
    
    def create_info_section(self, title, fields):
        """Create a section with labeled fields."""
        # Section header - left aligned, no dashes
        ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["primary"],
            anchor="w"
        ).pack(fill="x", pady=(20, 10), padx=5)
        
        # Fields
        for label, value in fields:
            field_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=8)
            field_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                field_frame,
                text=label + ":",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=180,
                anchor="w"
            ).pack(side="left", padx=15, pady=12)
            
            ctk.CTkLabel(
                field_frame,
                text=str(value),
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"],
                anchor="w",
                wraplength=400
            ).pack(side="left", padx=10, pady=12, fill="x", expand=True)
    
    def export_bio_data(self):
        """Export student bio data to PDF."""
        if not self.student:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"student_biodata_{self.student.student_id}.pdf",
            title="Export Student Bio Data"
        )
        
        if filename:
            try:
                # Create PDF
                doc = SimpleDocTemplate(filename, pagesize=A4,
                                       topMargin=0.75*inch, bottomMargin=0.75*inch,
                                       leftMargin=0.75*inch, rightMargin=0.75*inch)
                story = []
                styles = getSampleStyleSheet()
                
                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#1a73e8'),
                    spaceAfter=30,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )
                
                section_style = ParagraphStyle(
                    'SectionHeading',
                    parent=styles['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#2a2a3e'),
                    spaceAfter=12,
                    spaceBefore=20,
                    alignment=TA_LEFT,
                    fontName='Helvetica-Bold'
                )
                
                # Header
                story.append(Paragraph("STUDENT BIO DATA", title_style))
                story.append(Spacer(1, 0.3*inch))
                
                # Personal Information Section
                story.append(Paragraph("Personal Information", section_style))
                
                personal_data = [
                    ["Student ID:", self.student.student_id],
                    ["Full Name:", self.student.full_name],
                    ["Date of Birth:", self.student.date_of_birth.strftime("%Y-%m-%d")],
                    ["Age:", f"{self.student.age} years"],
                    ["Sex:", self.student.sex],
                    ["Class:", self.student.class_name],
                    ["Admission Year:", str(self.student.admission_year)],
                    ["State of Origin:", self.student.state_of_origin]
                ]
                
                personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
                personal_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ]))
                story.append(personal_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Contact Information Section
                story.append(Paragraph("Contact Information", section_style))
                
                contact_data = [
                    ["Home Address:", self.student.home_address],
                    ["Phone Number:", self.student.phone_number or "Not provided"]
                ]
                
                contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
                contact_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ]))
                story.append(contact_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Guardian Information Section
                story.append(Paragraph("Guardian/Parent Information", section_style))
                
                guardian_data = [
                    ["Guardian Name:", self.student.guardian_name],
                    ["Guardian Phone:", self.student.guardian_phone],
                    ["Guardian Address:", self.student.guardian_address]
                ]
                
                guardian_table = Table(guardian_data, colWidths=[2*inch, 4*inch])
                guardian_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ]))
                story.append(guardian_table)
                
                # Footer
                story.append(Spacer(1, 0.5*inch))
                footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
                footer_style = ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#6c757d'),
                    alignment=TA_CENTER
                )
                story.append(Paragraph(footer_text, footer_style))
                
                # Build PDF
                doc.build(story)
                
                messagebox.showinfo("Success", f"Bio data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")


class StudentAttendanceWindow(ctk.CTkToplevel):
    """Separate window for viewing student attendance records."""
    
    def __init__(self, parent, student_id, session):
        super().__init__(parent)
        self.student_id = student_id
        self.session = session
        self.student = None
        
        self.title("Student Attendance Records")
        self.geometry("900x700")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 450
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"900x700+{x}+{y}")
        
        self.configure(fg_color=COLORS["bg_dark"])
        
        self.setup_ui()
        self.load_attendance_data()
    
    def setup_ui(self):
        """Set up the attendance UI."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0)
        header_frame.pack(fill="x")
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📅 Attendance Records",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Export button
        ctk.CTkButton(
            header_frame,
            text="📥 Export to CSV",
            command=self.export_attendance,
            width=140,
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="right", padx=20, pady=15)
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        stats_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Loading statistics...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_secondary"]
        )
        self.stats_label.pack(pady=15)
        
        # Attendance records table
        self.records_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12
        )
        self.records_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    
    def load_attendance_data(self):
        """Load and display attendance records."""
        self.student = self.session.query(Student).filter_by(id=self.student_id).first()
        
        if not self.student:
            messagebox.showerror("Error", "Student not found")
            self.destroy()
            return
        
        self.title_label.configure(text=f"📅 Attendance Records - {self.student.full_name}")
        
        # Get attendance records
        records = self.session.query(Attendance).filter_by(
            student_id=self.student_id
        ).order_by(Attendance.date.desc()).all()
        
        # Calculate statistics
        total_records = len(records)
        present_count = sum(1 for r in records if r.is_present)
        absent_count = total_records - present_count
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        # Update statistics
        stats_text = f"Total Days: {total_records} | Present: {present_count} | Absent: {absent_count} | Attendance Rate: {attendance_rate:.1f}%"
        self.stats_label.configure(text=stats_text)
        
        # Display records
        if not records:
            ctk.CTkLabel(
                self.records_frame,
                text="No attendance records found",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return
        
        # Table headers
        headers_frame = ctk.CTkFrame(self.records_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(10, 5))
        
        headers = [("Date", 200), ("Status", 150), ("Remarks", 300)]
        for header, width in headers:
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=width
            ).pack(side="left", padx=10)
        
        # Records
        for record in records:
            record_frame = ctk.CTkFrame(self.records_frame, fg_color=COLORS["bg_dark"], corner_radius=6)
            record_frame.pack(fill="x", pady=2, padx=5)
            
            # Date
            ctk.CTkLabel(
                record_frame,
                text=record.date,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_primary"],
                width=200
            ).pack(side="left", padx=10, pady=8)
            
            # Status
            status_text = "✓ Present" if record.is_present else "✗ Absent"
            status_color = COLORS["success"] if record.is_present else COLORS["danger"]
            
            ctk.CTkLabel(
                record_frame,
                text=status_text,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=status_color,
                width=150
            ).pack(side="left", padx=10, pady=8)
            
            # Remarks
            remarks = "On time" if record.is_present else "Absent"
            ctk.CTkLabel(
                record_frame,
                text=remarks,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                width=300
            ).pack(side="left", padx=10, pady=8)
    
    def export_attendance(self):
        """Export attendance records to CSV."""
        if not self.student:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"attendance_{self.student.student_id}.csv",
            title="Export Attendance Records"
        )
        
        if filename:
            try:
                records = self.session.query(Attendance).filter_by(
                    student_id=self.student_id
                ).order_by(Attendance.date).all()
                
                # Get current academic year and term
                current_year = datetime.now().year
                next_year = current_year + 1
                session_year = f"{current_year}/{next_year}"
                # For simplicity, assume current term (could be made dynamic)
                current_term = 1
                
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Enhanced Header with all details
                    writer.writerow(["ATTENDANCE RECORDS"])
                    writer.writerow([f"Name: {self.student.full_name}"])
                    writer.writerow([f"Student ID: {self.student.student_id}"])
                    writer.writerow([f"Class: {self.student.class_name}"])
                    writer.writerow([f"Sex: {self.student.sex}"])
                    writer.writerow([f"Term: {current_term}"])
                    writer.writerow([f"Session: {session_year}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([])
                    
                    # Statistics
                    total = len(records)
                    present = sum(1 for r in records if r.is_present)
                    absent = total - present
                    rate = (present / total * 100) if total > 0 else 0
                    
                    writer.writerow(["STATISTICS"])
                    writer.writerow(["Total Days", total])
                    writer.writerow(["Present", present])
                    writer.writerow(["Absent", absent])
                    writer.writerow(["Attendance Rate", f"{rate:.1f}%"])
                    writer.writerow([])
                    
                    # Records
                    writer.writerow(["Date", "Status", "Remarks"])
                    for record in records:
                        status = "Present" if record.is_present else "Absent"
                        remarks = "On time" if record.is_present else "Absent"
                        writer.writerow([record.date, status, remarks])
                
                messagebox.showinfo("Success", f"Attendance records exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")


class StudentResultsWindow(ctk.CTkToplevel):
    """Separate window for viewing student academic results."""
    
    def __init__(self, parent, student_id, session):
        super().__init__(parent)
        self.student_id = student_id
        self.session = session
        self.student = None
        
        self.title("Student Academic Results")
        self.geometry("1100x700")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 550
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"1100x700+{x}+{y}")
        
        self.configure(fg_color=COLORS["bg_dark"])
        
        self.setup_ui()
        self.load_results_data()
    
    def setup_ui(self):
        """Set up the results UI."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0)
        header_frame.pack(fill="x")
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Academic Results",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)
        
        # Term selector
        ctk.CTkLabel(
            controls_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 8))
        
        self.term_var = ctk.StringVar(value="1")
        self.term_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.term_var,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=150,
            height=35,
            command=lambda x: self.load_results_data()
        )
        self.term_combo.pack(side="left", padx=5)
        
        # Export button
        ctk.CTkButton(
            controls_frame,
            text="📥 Export",
            command=self.export_results,
            width=100,
            height=35,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(20, 0))
        
        # Summary frame
        self.summary_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.summary_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Results table
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12
        )
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    
    def load_results_data(self):
        """Load and display academic results with term comparison."""
        self.student = self.session.query(Student).filter_by(id=self.student_id).first()
        
        if not self.student:
            messagebox.showerror("Error", "Student not found")
            self.destroy()
            return
        
        self.title_label.configure(text=f"Academic Results - {self.student.full_name}")
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # Get current term
        term_value = self.term_var.get()
        current_term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)
        
        # Get marks for current term
        current_marks = self.session.query(Mark).filter_by(
            student_id=self.student_id,
            term=current_term
        ).all()
        
        if not current_marks:
            term_names = {1: "First Term", 2: "Second Term", 3: "Third Term"}
            term_name = term_names.get(current_term, f"Term {current_term}")
            ctk.CTkLabel(
                self.results_frame,
                text=f"No results found for {term_name}",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return
        
        # Get previous term marks for comparison
        previous_marks = {}
        term1_marks = {}
        term2_marks = {}
        
        if current_term == 2:
            # Term 2: Compare with Term 1
            prev_marks_list = self.session.query(Mark).filter_by(
                student_id=self.student_id,
                term=1
            ).all()
            previous_marks = {m.subject_id: m for m in prev_marks_list}
        elif current_term == 3:
            # Term 3: Get both Term 1 and Term 2
            term1_list = self.session.query(Mark).filter_by(
                student_id=self.student_id,
                term=1
            ).all()
            term1_marks = {m.subject_id: m for m in term1_list}
            
            term2_list = self.session.query(Mark).filter_by(
                student_id=self.student_id,
                term=2
            ).all()
            term2_marks = {m.subject_id: m for m in term2_list}
        
        # Calculate summary statistics
        total_score = sum(mark.total for mark in current_marks)
        average = total_score / len(current_marks) if current_marks else 0
        
        # Display summary
        term_names = {1: "First Term", 2: "Second Term", 3: "Third Term"}
        term_name = term_names.get(current_term, f"Term {current_term}")
        summary_text = f"{term_name} | Subjects: {len(current_marks)} | Total: {total_score:.0f} | Average: {average:.1f}%"
        ctk.CTkLabel(
            self.summary_frame,
            text=summary_text,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=15)
        
        # Table headers - different for each term
        headers_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(10, 5))
        
        if current_term == 3 and (term1_marks or term2_marks):
            # Term 3: Show all three terms + average
            headers = [
                ("Subject", 120),
                ("1st CA", 50),
                ("2nd CA", 50),
                ("3rd CA", 50),
                ("1st Exam", 55),
                ("2nd Exam", 55),
                ("3rd Exam", 55),
                ("1st Total", 55),
                ("2nd Total", 55),
                ("3rd Total", 55),
                ("Avg", 50),
                ("Grade", 50)
            ]
        elif current_term == 2 and previous_marks:
            # Term 2: Compare with Term 1
            headers = [
                ("Subject", 150),
                ("1st Term CA", 65),
                ("2nd Term CA", 65),
                ("1st Term Exam", 70),
                ("2nd Term Exam", 70),
                ("1st Term Total", 70),
                ("2nd Term Total", 70),
                ("Grade", 60),
                ("Remarks", 120)
            ]
        else:
            # Term 1: Standard view
            headers = [
                ("Subject", 200),
                ("CA (30)", 80),
                ("Exam (70)", 80),
                ("Total", 80),
                ("Grade", 80),
                ("Remarks", 150)
            ]
        
        for header, width in headers:
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=width
            ).pack(side="left", padx=2)
        
        # Results rows
        for mark in current_marks:
            subject = self.session.query(Subject).filter_by(id=mark.subject_id).first()
            if not subject:
                continue
            
            row_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["bg_dark"], corner_radius=6)
            row_frame.pack(fill="x", pady=2, padx=5)
            
            # Subject name
            subject_width = 120 if current_term == 3 else (150 if current_term == 2 else 200)
            ctk.CTkLabel(
                row_frame,
                text=subject.subject_name[:18] if current_term == 3 else subject.subject_name[:20],
                font=ctk.CTkFont(family="Segoe UI", size=9 if current_term == 3 else 10),
                text_color=COLORS["text_primary"],
                width=subject_width,
                anchor="w"
            ).pack(side="left", padx=2, pady=6)
            
            if current_term == 3 and (term1_marks or term2_marks):
                # Term 3: Show all three terms + average
                t1_mark = term1_marks.get(mark.subject_id)
                t2_mark = term2_marks.get(mark.subject_id)
                
                # CAs
                for t_mark in [t1_mark, t2_mark, mark]:
                    ca_val = t_mark.continuous_assessment if t_mark else 0
                    ctk.CTkLabel(
                        row_frame,
                        text=f"{ca_val:.0f}" if t_mark else "-",
                        font=ctk.CTkFont(family="Segoe UI", size=9),
                        text_color=COLORS["text_primary"] if t_mark == mark else COLORS["text_secondary"],
                        width=50
                    ).pack(side="left", padx=1, pady=6)
                
                # Exams
                for t_mark in [t1_mark, t2_mark, mark]:
                    exam_val = t_mark.exams if t_mark else 0
                    ctk.CTkLabel(
                        row_frame,
                        text=f"{exam_val:.0f}" if t_mark else "-",
                        font=ctk.CTkFont(family="Segoe UI", size=9),
                        text_color=COLORS["text_primary"] if t_mark == mark else COLORS["text_secondary"],
                        width=55
                    ).pack(side="left", padx=1, pady=6)
                
                # Totals
                for t_mark in [t1_mark, t2_mark, mark]:
                    total_val = t_mark.total if t_mark else 0
                    ctk.CTkLabel(
                        row_frame,
                        text=f"{total_val:.0f}" if t_mark else "-",
                        font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold" if t_mark == mark else "normal"),
                        text_color=COLORS["text_primary"] if t_mark == mark else COLORS["text_secondary"],
                        width=55
                    ).pack(side="left", padx=1, pady=6)
                
                # Calculate average of all three terms
                totals = [t.total for t in [t1_mark, t2_mark, mark] if t]
                avg_total = sum(totals) / len(totals) if totals else 0
                
                ctk.CTkLabel(
                    row_frame,
                    text=f"{avg_total:.1f}",
                    font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                    text_color=COLORS["success"],
                    width=50
                ).pack(side="left", padx=1, pady=6)
                
                # Grade based on average
                from calculations import GradeCalculator
                avg_grade = GradeCalculator.calculate_grade(avg_total)
                grade_color = COLORS["success"] if avg_grade in ['A', 'B'] else (
                    COLORS["warning"] if avg_grade in ['C', 'D'] else COLORS["danger"]
                )
                ctk.CTkLabel(
                    row_frame,
                    text=avg_grade,
                    font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                    text_color=grade_color,
                    width=50
                ).pack(side="left", padx=1, pady=6)
                
            elif current_term == 2 and previous_marks and mark.subject_id in previous_marks:
                # Term 2: Show comparison with Term 1
                prev_mark = previous_marks[mark.subject_id]
                
                # 1st Term CA
                ctk.CTkLabel(
                    row_frame,
                    text=f"{prev_mark.continuous_assessment:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=10),
                    text_color=COLORS["text_secondary"],
                    width=65
                ).pack(side="left", padx=2, pady=6)
                
                # 2nd Term CA
                ctk.CTkLabel(
                    row_frame,
                    text=f"{mark.continuous_assessment:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color=COLORS["text_primary"],
                    width=65
                ).pack(side="left", padx=2, pady=6)
                
                # 1st Term Exam
                ctk.CTkLabel(
                    row_frame,
                    text=f"{prev_mark.exams:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=10),
                    text_color=COLORS["text_secondary"],
                    width=70
                ).pack(side="left", padx=2, pady=6)
                
                # 2nd Term Exam
                ctk.CTkLabel(
                    row_frame,
                    text=f"{mark.exams:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color=COLORS["text_primary"],
                    width=70
                ).pack(side="left", padx=2, pady=6)
                
                # 1st Term Total
                ctk.CTkLabel(
                    row_frame,
                    text=f"{prev_mark.total:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=10),
                    text_color=COLORS["text_secondary"],
                    width=70
                ).pack(side="left", padx=2, pady=6)
                
                # 2nd Term Total
                ctk.CTkLabel(
                    row_frame,
                    text=f"{mark.total:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color=COLORS["text_primary"],
                    width=70
                ).pack(side="left", padx=2, pady=6)
                
                # Grade
                grade_color = COLORS["success"] if mark.grade in ['A', 'B'] else (
                    COLORS["warning"] if mark.grade in ['C', 'D'] else COLORS["danger"]
                )
                ctk.CTkLabel(
                    row_frame,
                    text=mark.grade,
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color=grade_color,
                    width=60
                ).pack(side="left", padx=2, pady=6)
                
                # Remarks
                remarks = self.get_remarks(mark.total)
                ctk.CTkLabel(
                    row_frame,
                    text=remarks,
                    font=ctk.CTkFont(family="Segoe UI", size=10),
                    text_color=COLORS["text_secondary"],
                    width=120
                ).pack(side="left", padx=2, pady=6)
            else:
                # Term 1: Standard view - no comparison
                # CA
                ctk.CTkLabel(
                    row_frame,
                    text=f"{mark.continuous_assessment:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color=COLORS["text_primary"],
                    width=80
                ).pack(side="left", padx=5, pady=8)
                
                # Exam
                ctk.CTkLabel(
                    row_frame,
                    text=f"{mark.exams:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color=COLORS["text_primary"],
                    width=80
                ).pack(side="left", padx=5, pady=8)
                
                # Total
                ctk.CTkLabel(
                    row_frame,
                    text=f"{mark.total:.0f}",
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=COLORS["text_primary"],
                    width=80
                ).pack(side="left", padx=5, pady=8)
            
            # Grade
            grade_color = COLORS["success"] if mark.grade in ['A', 'B'] else (
                COLORS["warning"] if mark.grade in ['C', 'D'] else COLORS["danger"]
            )
            
            ctk.CTkLabel(
                row_frame,
                text=mark.grade,
                font=ctk.CTkFont(family="Segoe UI", size=11 if not previous_marks else 10, weight="bold"),
                text_color=grade_color,
                width=80 if not previous_marks else 60
            ).pack(side="left", padx=2 if previous_marks else 5, pady=6 if previous_marks else 8)
            
            # Remarks
            remarks = self.get_remarks(mark.total)
            ctk.CTkLabel(
                row_frame,
                text=remarks,
                font=ctk.CTkFont(family="Segoe UI", size=10 if previous_marks else 11),
                text_color=COLORS["text_secondary"],
                width=120 if previous_marks else 150
            ).pack(side="left", padx=2 if previous_marks else 5, pady=6 if previous_marks else 8)
    
    def get_remarks(self, score):
        """Get remarks based on score."""
        if score >= 75:
            return "Excellent"
        elif score >= 65:
            return "Very Good"
        elif score >= 50:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def export_results(self):
        """Export results to PDF using report card format."""
        if not self.student:
            return
        
        term_value = self.term_var.get()
        term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"report_card_{self.student.student_id}_term{term}.pdf",
            title="Export Report Card"
        )
        
        if filename:
            try:
                from report_card_pdf import generate_report_card
                success = generate_report_card(self.student_id, term, filename)
                
                if success:
                    messagebox.showinfo("Success", f"Report card exported to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to generate report card. Please ensure the student has grades for this term.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
