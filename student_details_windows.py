"""
Enhanced Student Details Windows
Separate windows for viewing bio data, attendance, and results with export functionality
"""
import customtkinter as ctk
from models import Session, Student, Attendance, Mark, Subject
from datetime import datetime
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from ui_components import (
    MODAL_STYLE,
    center_toplevel,
    create_modal_header,
    input_style,
    safe_export_filename,
    setup_modal_window,
    ask_save_filename,
    show_info,
    show_error,
    show_warning,
    close_modal_window,
)

COLORS = MODAL_STYLE


class StudentBioDataWindow(ctk.CTkToplevel):
    """Window for viewing and exporting student bio data."""
    
    def __init__(self, parent, student_id, session):
        super().__init__(parent)
        self.student_id = student_id
        self.session = session
        self.student = None
        
        self.title("Student Bio Data")

        screen_height = self.winfo_screenheight()
        window_height = min(650, int(screen_height * 0.8))
        self.transient(parent)
        self.configure(fg_color=COLORS["bg_main"])
        center_toplevel(self, parent, 720, window_height)

        self.setup_ui()
        self.load_student_data()
        setup_modal_window(self)

    def setup_ui(self):
        """Set up the bio data UI."""
        _, self.header_subtitle = create_modal_header(self, "Student Bio Data")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=COLORS["padding"], pady=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="Export to PDF",
            command=self.export_bio_data,
            width=140,
            height=40,
            corner_radius=COLORS["radius"],
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).pack(side="right")

        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=COLORS["padding"],
            pady=(0, COLORS["padding"]),
        )

    
    def load_student_data(self):
        """Load and display student bio data."""
        self.student = self.session.query(Student).filter_by(id=self.student_id).first()
        
        if not self.student:
            show_error(self, "Error", "Student not found")
            close_modal_window(self)
            return

        if self.header_subtitle is not None:
            self.header_subtitle.configure(
                text=f"{self.student.full_name}  |  {self.student.student_id}  |  {self.student.class_name}"
            )

        # Profile Picture Section
        import os
        from PIL import Image
        from app_paths import find_asset
        
        # Banner Section
        banner_path = find_asset(("assets/report-banner.png", "report-banner.png", "school_header.png"))
        if banner_path and os.path.exists(banner_path):
            try:
                img = Image.open(banner_path)
                w, h = img.size
                new_w = 600
                new_h = int(h * (new_w / w))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
                banner_label = ctk.CTkLabel(self.content_frame, image=photo, text="")
                banner_label.pack(anchor="w", pady=(0, 20))
            except Exception:
                pass

        
        pic_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        pic_frame.pack(fill="x", pady=(10, 20))
        
        pic_path = self.student.profile_picture_path
        if pic_path and os.path.exists(pic_path):
            try:
                from PIL import ImageOps
                img = Image.open(pic_path)
                img = ImageOps.fit(img, (160, 160), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 160))
                pic_label = ctk.CTkLabel(pic_frame, image=photo, text="", width=160, height=160, corner_radius=10)
                pic_label.pack(side="top", anchor="w")
                
                ctk.CTkButton(
                    pic_frame,
                    text="Replace Picture",
                    command=self.replace_picture,
                    width=120, height=28, corner_radius=6,
                    fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
                ).pack(side="top", anchor="w", pady=(10, 0))
            except Exception:
                pass

        # Display all student information
        dept_name = self.student.department.name if self.student.department else "Not specified"
        session_name = self.student.academic_session.name if self.student.academic_session else "Not specified"
        
        self.create_info_section("Personal Information", [
            ("Student ID", self.student.student_id),
            ("Surname", self.student.surname or ""),
            ("First Name", self.student.firstname or ""),
            ("Full Name", self.student.full_name),
            ("Date of Birth", self.student.date_of_birth.strftime("%Y-%m-%d")),
            ("Age", f"{self.student.age} years"),
            ("Sex", self.student.sex),
            ("Religion", self.student.religion or "Not specified"),
            ("Class", self.student.class_name),
            ("Department", dept_name),
            ("Session", session_name),
            ("Admission Year", str(self.student.admission_year)),
            ("State of Origin", self.student.state_of_origin),
            ("LGA of Origin", self.student.lga_of_origin or "")
        ])
        
        self.create_info_section("Contact Information", [
            ("Home Address", self.student.home_address),
            ("Phone Number", self.student.phone_number or "Not provided")
        ])
        
        self.create_info_section("Guardian/Parent Information", [
            ("Guardian Name", self.student.guardian_name),
            ("Guardian Occupation", getattr(self.student, "guardian_occupation", "Not provided")),
            ("Guardian Phone", self.student.guardian_phone),
            ("Guardian Address", self.student.guardian_address)
        ])
        
    def replace_picture(self):
        from tkinter import filedialog
        import os
        import shutil
        file_path = filedialog.askopenfilename(
            title="Select New Profile Picture",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not file_path:
            return
            
        try:
            profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "profile_pictures")
            os.makedirs(profile_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            new_filename = f"{self.student.student_id.replace('/', '_')}{ext}"
            new_path = os.path.join(profile_dir, new_filename)
            
            shutil.copy2(file_path, new_path)
            
            self.student.profile_picture_path = f"assets/profile_pictures/{new_filename}"
            self.session.commit()
            
            from ui_components import show_info
            show_info(self, "Success", "Profile picture updated successfully!")
            
            self.destroy()
        except Exception as e:
            from ui_components import show_error
            show_error(self, "Error", f"Failed to update picture: {e}")
    
    def create_info_section(self, title, fields):
        """Create a section with labeled fields."""
        ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(fill="x", pady=(18, 10))

        for label, value in fields:
            field_frame = ctk.CTkFrame(
                self.content_frame,
                fg_color=COLORS["bg_card"],
                corner_radius=COLORS["radius"],
                border_width=1,
                border_color=COLORS["border"],
            )
            field_frame.pack(fill="x", pady=4)

            ctk.CTkLabel(
                field_frame,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=COLORS["label_width"],
                anchor="w",
            ).pack(side="left", padx=16, pady=14)

            ctk.CTkLabel(
                field_frame,
                text=str(value),
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_primary"],
                anchor="w",
                wraplength=420,
            ).pack(side="left", padx=(0, 16), pady=14, fill="x", expand=True)
    
    def export_bio_data(self):
        """Export student bio data to PDF."""
        if not self.student:
            return
        
        filename = ask_save_filename(
            self,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=safe_export_filename(self.student.full_name, "biodata", extension="pdf"),
            title="Export Student Bio Data",
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
                    alignment=TA_LEFT,
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
                from report_card_pdf import _header_block
                story.extend(_header_block())
                import os
                from reportlab.platypus import Image as RLImage
                pic_path = self.student.profile_picture_path
                
                story.append(Paragraph("STUDENT BIO DATA", title_style))
                
                if pic_path and os.path.exists(pic_path):
                    try:
                        img = RLImage(pic_path, width=1.5*inch, height=1.5*inch)
                        img.hAlign = 'LEFT'
                        story.append(Spacer(1, 0.1*inch))
                        story.append(img)
                    except Exception:
                        pass
                
                story.append(Spacer(1, 0.3*inch))
                
                # Personal Information Section
                story.append(Paragraph("Personal Information", section_style))
                
                dept_name = self.student.department.name if self.student.department else "Not specified"
                session_name = self.student.academic_session.name if self.student.academic_session else "Not specified"
                
                personal_data = [
                    ["Student ID:", self.student.student_id],
                    ["Surname:", self.student.surname or ""],
                    ["First Name:", self.student.firstname or ""],
                    ["Full Name:", self.student.full_name],
                    ["Date of Birth:", self.student.date_of_birth.strftime("%Y-%m-%d")],
                    ["Age:", f"{self.student.age} years"],
                    ["Sex:", self.student.sex],
                    ["Religion:", self.student.religion or "Not specified"],
                    ["Class:", self.student.class_name],
                    ["Department:", dept_name],
                    ["Session:", session_name],
                    ["Admission Year:", str(self.student.admission_year)],
                    ["State of Origin:", self.student.state_of_origin],
                    ["LGA of Origin:", self.student.lga_of_origin or ""]
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
                    ["Guardian Occupation:", getattr(self.student, "guardian_occupation", "Not provided") or "Not provided"],
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
                
                show_info(self, "Success", f"Bio data exported to {filename}")
            except Exception as e:
                show_error(self, "Error", f"Failed to export: {str(e)}")


class StudentAttendanceWindow(ctk.CTkToplevel):
    """Separate window for viewing student attendance records."""
    
    def __init__(self, parent, student_id, session):
        super().__init__(parent)
        self.student_id = student_id
        self.session = session
        self.student = None
        
        self.title("Student Attendance Records")
        self.transient(parent)
        self.configure(fg_color=COLORS["bg_main"])
        center_toplevel(self, parent, 900, 700)

        self.setup_ui()
        self.load_attendance_data()
        setup_modal_window(self)

    def setup_ui(self):
        """Set up the attendance UI."""
        _, self.header_subtitle = create_modal_header(self, "Attendance Records")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=COLORS["padding"], pady=(0, 8))

        ctk.CTkLabel(
            toolbar,
            text="Term",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        self.term_var = ctk.StringVar(value="1 - First Term")
        ctk.CTkComboBox(
            toolbar,
            variable=self.term_var,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=170,
            height=40,
            **input_style(),
        ).pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            toolbar,
            text="Export to CSV",
            command=self.export_attendance,
            width=140,
            height=40,
            corner_radius=COLORS["radius"],
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).pack(side="right")

        self.stats_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=COLORS["radius"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.stats_frame.pack(fill="x", padx=COLORS["padding"], pady=(0, 12))

        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="Loading statistics...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_primary"],
        )
        self.stats_label.pack(pady=16, padx=16)

        self.records_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=COLORS["radius"],
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        self.records_frame.pack(
            fill="both",
            expand=True,
            padx=COLORS["padding"],
            pady=(0, COLORS["padding"]),
        )

    
    def load_attendance_data(self):
        """Load and display attendance records."""
        self.student = self.session.query(Student).filter_by(id=self.student_id).first()
        
        if not self.student:
            show_error(self, "Error", "Student not found")
            close_modal_window(self)
            return
        
        if self.header_subtitle is not None:
            self.header_subtitle.configure(
                text=f"{self.student.full_name}  |  {self.student.student_id}  |  {self.student.class_name}"
            )

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
            record_frame = ctk.CTkFrame(
                self.records_frame,
                fg_color=COLORS["bg_main"],
                corner_radius=COLORS["radius"],
                border_width=1,
                border_color=COLORS["border"],
            )
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
            status_text = "Present" if record.is_present else "Absent"
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
    
    def _selected_term(self):
        term_value = self.term_var.get()
        return int(term_value.split()[0]) if " - " in term_value else int(term_value)

    def export_attendance(self):
        """Export attendance records to CSV."""
        if not self.student:
            return

        current_term = self._selected_term()
        filename = ask_save_filename(
            self,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=safe_export_filename(
                self.student.full_name,
                f"term{current_term}",
                "attendance",
                extension="csv",
            ),
            title="Export Attendance Records",
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
                
                show_info(self, "Success", f"Attendance records exported to {filename}")
            except Exception as e:
                show_error(self, "Error", f"Failed to export: {str(e)}")


class StudentResultsWindow(ctk.CTkToplevel):
    """Separate window for viewing student academic results."""
    
    def __init__(self, parent, student_id, session):
        super().__init__(parent)
        self.student_id = student_id
        self.session = session
        self.student = None
        
        self.title("Student Academic Results")
        self.transient(parent)
        self.configure(fg_color=COLORS["bg_main"])
        center_toplevel(self, parent, 1100, 700)

        self.setup_ui()
        self.load_results_data()
        setup_modal_window(self)

    def setup_ui(self):
        """Set up the results UI."""
        _, self.header_subtitle = create_modal_header(self, "Academic Results")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=COLORS["padding"], pady=(0, 8))

        ctk.CTkLabel(
            toolbar,
            text="Term",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        self.term_var = ctk.StringVar(value="1")
        self.term_combo = ctk.CTkComboBox(
            toolbar,
            variable=self.term_var,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=170,
            height=40,
            command=lambda _value: self.load_results_data(),
            **input_style(),
        )
        self.term_combo.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            toolbar,
            text="Export",
            command=self.export_results,
            width=100,
            height=40,
            corner_radius=COLORS["radius"],
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color=COLORS["text_on_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).pack(side="right")

        self.summary_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=COLORS["radius"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.summary_frame.pack(fill="x", padx=COLORS["padding"], pady=(0, 12))

        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=COLORS["radius"],
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"],
        )
        self.results_frame.pack(
            fill="both",
            expand=True,
            padx=COLORS["padding"],
            pady=(0, COLORS["padding"]),
        )

    
    def load_results_data(self):
        """Load and display academic results with term comparison."""
        self.student = self.session.query(Student).filter_by(id=self.student_id).first()
        
        if not self.student:
            show_error(self, "Error", "Student not found")
            close_modal_window(self)
            return
        
        if self.header_subtitle is not None:
            self.header_subtitle.configure(
                text=f"{self.student.full_name}  |  {self.student.student_id}  |  {self.student.class_name}"
            )

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
            
            row_frame = ctk.CTkFrame(
                self.results_frame,
                fg_color=COLORS["bg_main"],
                corner_radius=COLORS["radius"],
                border_width=1,
                border_color=COLORS["border"],
            )
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

        from models import ReportCard
        from report_card_pdf import is_report_card_complete

        report_card = self.session.query(ReportCard).filter_by(
            student_id=self.student_id,
            term=term,
        ).first()
        if not is_report_card_complete(report_card, self.student_id, term, self.session):
            show_warning(
                self,
                "Incomplete Report Card",
                "Complete the report card details in the Report Cards section before downloading.",
            )
            return
        
        filename = ask_save_filename(
            self,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=safe_export_filename(
                self.student.full_name,
                f"term{term}",
                "report_card",
                extension="pdf",
            ),
            title="Export Report Card",
        )
        
        if filename:
            try:
                from report_card_pdf import generate_report_card
                success = generate_report_card(self.student_id, term, filename)
                
                if success:
                    show_info(self, "Success", f"Report card exported to {filename}")
                else:
                    show_error(
                        self,
                        "Error",
                        "Failed to generate report card. Please ensure the student has grades for this term.",
                    )
            except Exception as e:
                show_error(self, "Error", f"Failed to export: {str(e)}")
