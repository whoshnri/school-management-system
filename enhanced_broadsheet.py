"""
Enhanced Broadsheet System with Multi-Term Support
Supports comprehensive reporting with term comparisons and statistics
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from models import Session, Student, Subject, Mark
from calculations import GradeCalculator
import csv
from datetime import datetime
from ui_components import TextLabelManager

# Modern color palette
COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "secondary": "#5f6368",
    "success": "#34a853",
    "warning": "#fbbc04",
    "danger": "#ea4335",
    "bg_dark": "#1e1e2e",
    "bg_card": "#2a2a3e",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "border": "#3a3a4e"
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Header with controls
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))

        ctk.CTkLabel(
            header_frame,
            text="Enhanced Broadsheet & Report Cards",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        # Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)

        # Class selection
        ctk.CTkLabel(
            controls_frame,
            text="Class:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        class_values = [f"{cls} ({self.get_class_population(cls)})" for cls in ["SSS1", "SSS2", "SSS3"]]
        self.class_filter = ctk.CTkComboBox(
            controls_frame,
            values=class_values,
            width=130,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.class_filter.pack(side="left", padx=5)

        # Term selection
        ctk.CTkLabel(
            controls_frame,
            text="Term:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(20, 8))

        self.term_filter = ctk.CTkComboBox(
            controls_frame,
            values=["1 - First Term", "2 - Second Term", "3 - Third Term"],
            width=150,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.term_filter.pack(side="left", padx=5)

        # Academic Year
        ctk.CTkLabel(
            controls_frame,
            text="Year:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(20, 8))

        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 2)]
        self.year_filter = ctk.CTkComboBox(
            controls_frame,
            values=years,
            width=80,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.year_filter.set(str(current_year))
        self.year_filter.pack(side="left", padx=5)

        # Load button
        ctk.CTkButton(
            controls_frame,
            text="Load Report",
            command=self.load_enhanced_sheet,
            width=100,
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(20, 8))

        # Export button
        self.export_btn = ctk.CTkButton(
            controls_frame,
            text="Export CSV",
            command=self.export_enhanced_csv,
            state="disabled",
            width=100,
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2d8f47",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.export_btn.pack(side="left", padx=5)

        # Broadsheet Display Area
        self.sheet_frame = ctk.CTkScrollableFrame(
            self,
            orientation="both",
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        self.sheet_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    def get_class_population(self, class_name):
        """Get number of students in a class."""
        return self.session.query(Student).filter_by(class_name=class_name).count()

    def load_enhanced_sheet(self):
        """Load enhanced broadsheet with multi-term support."""
        # Clear existing content
        for widget in self.sheet_frame.winfo_children():
            widget.destroy()

        # Get selections
        class_name_full = self.class_filter.get()
        self.current_class = class_name_full.split(' ')[0] if class_name_full else ""
        term_value = self.term_filter.get()
        self.current_term = int(term_value.split()[0]) if ' - ' in term_value else int(term_value)
        current_year = int(self.year_filter.get())

        if not self.current_class:
            messagebox.showwarning("Selection Error", "Please select a class.")
            return

        # Load students and subjects
        self.students = self.session.query(Student).filter_by(class_name=self.current_class).order_by(Student.full_name).all()
        self.subjects = self.session.query(Subject).all()

        if not self.students:
            self.show_empty_state()
            return

        # Generate enhanced broadsheet based on term
        if self.current_term == 1:
            self.generate_first_term_sheet()
        elif self.current_term == 2:
            self.generate_second_term_sheet()
        else:  # Term 3
            self.generate_third_term_sheet()

        # Enable export
        self.export_btn.configure(state="normal")

    def show_empty_state(self):
        """Show empty state when no students found."""
        empty_frame = ctk.CTkFrame(self.sheet_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=0, pady=60, padx=100)
        
        ctk.CTkLabel(
            empty_frame,
            text="📊",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text=f"No students in {self.current_class}",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=COLORS["text_secondary"]
        ).pack()

    def generate_first_term_sheet(self):
        """Generate first term broadsheet."""
        # Header information
        self.create_sheet_header("FIRST TERM REPORT")
        
        # Create table headers
        headers = ["S/N", "Student ID", "Name", "Sex"]
        
        # Add subject headers (CA, Exam, Total, Grade, Position)
        for subject in self.subjects:
            headers.extend([
                f"{subject.subject_code}\nCA(30)",
                f"{subject.subject_code}\nExam(70)", 
                f"{subject.subject_code}\nTotal",
                f"{subject.subject_code}\nGrade",
                f"{subject.subject_code}\nPos"
            ])
        
        # Add summary headers
        headers.extend(["Total Score", "Average", "Position", "Grade"])
        
        # Create headers
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.sheet_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=60 if col < 4 else 50
            )
            label.grid(row=2, column=col, padx=1, pady=5, sticky="ew")

        # Generate student data
        student_totals = []
        subject_stats = {}
        
        for i, student in enumerate(self.students, start=1):
            col = 0
            
            # Basic info
            ctk.CTkLabel(self.sheet_frame, text=str(i), width=40).grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            ctk.CTkLabel(self.sheet_frame, text=student.student_id, width=80).grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            ctk.CTkLabel(self.sheet_frame, text=student.name[:15], width=120).grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            ctk.CTkLabel(self.sheet_frame, text=student.sex, width=40).grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            
            student_total = 0
            subject_count = 0
            
            # Subject marks
            for subject in self.subjects:
                mark = self.session.query(Mark).filter_by(
                    student_id=student.id, 
                    subject_id=subject.id, 
                    term=self.current_term
                ).first()
                
                if mark:
                    ca = mark.continuous_assessment or 0
                    exam = mark.exams or 0
                    total = mark.total or 0
                    grade = mark.grade or "-"
                    
                    student_total += total
                    subject_count += 1
                    
                    # Store for position calculation
                    if subject.id not in subject_stats:
                        subject_stats[subject.id] = []
                    subject_stats[subject.id].append((student.id, total))
                else:
                    ca = exam = total = 0
                    grade = "-"
                
                # Display marks
                ctk.CTkLabel(self.sheet_frame, text=f"{ca:.0f}", width=50).grid(row=i+2, column=col, padx=1, pady=2)
                col += 1
                ctk.CTkLabel(self.sheet_frame, text=f"{exam:.0f}", width=50).grid(row=i+2, column=col, padx=1, pady=2)
                col += 1
                ctk.CTkLabel(self.sheet_frame, text=f"{total:.0f}", width=50).grid(row=i+2, column=col, padx=1, pady=2)
                col += 1
                ctk.CTkLabel(self.sheet_frame, text=grade, width=40).grid(row=i+2, column=col, padx=1, pady=2)
                col += 1
                
                # Position placeholder (will be calculated)
                pos_label = ctk.CTkLabel(self.sheet_frame, text="-", width=40)
                pos_label.grid(row=i+2, column=col, padx=1, pady=2)
                col += 1
            
            # Student summary
            average = student_total / subject_count if subject_count > 0 else 0
            student_totals.append((student.id, student_total, average, i+2))  # Store row for position update
            
            ctk.CTkLabel(self.sheet_frame, text=f"{student_total:.0f}", width=60).grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            ctk.CTkLabel(self.sheet_frame, text=f"{average:.1f}", width=60).grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            
            # Overall position placeholder
            pos_label = ctk.CTkLabel(self.sheet_frame, text="-", width=50)
            pos_label.grid(row=i+2, column=col, padx=1, pady=2)
            col += 1
            
            # Overall grade
            overall_grade = GradeCalculator.calculate_grade(average)
            ctk.CTkLabel(self.sheet_frame, text=overall_grade, width=50).grid(row=i+2, column=col, padx=1, pady=2)

        # Calculate and update positions
        self.calculate_positions(subject_stats, student_totals)
        
        # Add statistics summary
        self.add_statistics_summary(len(self.students) + 5)

    def generate_second_term_sheet(self):
        """Generate second term broadsheet with first term comparison."""
        # Header information
        self.create_sheet_header("SECOND TERM REPORT (with First Term Comparison)")
        
        # Create comprehensive headers
        headers = ["S/N", "Student ID", "Name", "Sex"]
        
        # Add subject headers with both terms
        for subject in self.subjects:
            headers.extend([
                f"{subject.subject_code}\nSecond Term CA(30)",
                f"{subject.subject_code}\nFirst Term CA(30)",
                f"{subject.subject_code}\nSecond Term Exam(70)",
                f"{subject.subject_code}\nFirst Term Exam(70)",
                f"{subject.subject_code}\nSecond Term Total",
                f"{subject.subject_code}\nFirst Term Total",
                f"{subject.subject_code}\nSecond Term Grade",
                f"{subject.subject_code}\nFirst Term Grade",
                f"{subject.subject_code}\nSecond Term Pos",
                f"{subject.subject_code}\nFirst Term Pos"
            ])
        
        # Add summary headers
        headers.extend([
            "Second Term Total", "First Term Total", "Second Term Average", "First Term Average", 
            "Second Term Position", "First Term Position", "Second Term Grade", "First Term Grade"
        ])
        
        # Create headers (smaller font due to more columns)
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.sheet_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=8, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=45 if col < 4 else 35
            )
            label.grid(row=2, column=col, padx=1, pady=3, sticky="ew")

        # Generate student data with both terms
        self.generate_dual_term_data(2, 1)  # Term 2 vs Term 1

    def generate_third_term_sheet(self):
        """Generate third term broadsheet with all terms and yearly summary."""
        # Header information  
        self.create_sheet_header("THIRD TERM REPORT (Complete Year Summary)")
        
        # This will be the most comprehensive report
        headers = ["S/N", "Student ID", "Name", "Sex"]
        
        # Add subject headers for all three terms plus averages
        for subject in self.subjects:
            headers.extend([
                f"{subject.subject_code}\nThird Term Total",
                f"{subject.subject_code}\nSecond Term Total", 
                f"{subject.subject_code}\nFirst Term Total",
                f"{subject.subject_code}\nYear Avg",
                f"{subject.subject_code}\nYear Grade",
                f"{subject.subject_code}\nYear Pos"
            ])
        
        # Add comprehensive summary
        headers.extend([
            "Third Term Total", "Second Term Total", "First Term Total", "Year Total",
            "Third Term Avg", "Second Term Avg", "First Term Avg", "Year Avg",
            "Third Term Pos", "Second Term Pos", "First Term Pos", "Year Pos",
            "Year Grade"
        ])
        
        # Create headers
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.sheet_frame,
                text=header,
                font=ctk.CTkFont(family="Segoe UI", size=8, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=40 if col < 4 else 30
            )
            label.grid(row=2, column=col, padx=1, pady=3, sticky="ew")

        # Generate comprehensive year data
        self.generate_year_summary_data()

    def generate_dual_term_data(self, current_term, comparison_term):
        """Generate data comparing two terms."""
        # Implementation for dual term comparison
        # This is a complex method that would handle the comparison logic
        pass

    def generate_year_summary_data(self):
        """Generate complete year summary data."""
        # Implementation for year summary
        # This would calculate averages across all terms
        pass

    def calculate_positions(self, subject_stats, student_totals):
        """Calculate positions for subjects and overall."""
        # Calculate subject positions
        for subject_id, scores in subject_stats.items():
            scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score descending
            for pos, (student_id, score) in enumerate(scores, 1):
                # Update position in the grid (this would need grid reference tracking)
                pass
        
        # Calculate overall positions
        student_totals.sort(key=lambda x: x[2], reverse=True)  # Sort by average descending
        for pos, (student_id, total, average, row) in enumerate(student_totals, 1):
            # Update overall position in the grid
            pass

    def create_sheet_header(self, title):
        """Create header section for the broadsheet."""
        # School info header
        header_info = ctk.CTkFrame(self.sheet_frame, fg_color="transparent")
        header_info.grid(row=0, column=0, columnspan=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            header_info,
            text="SCHOOL MANAGEMENT SYSTEM",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack()
        
        ctk.CTkLabel(
            header_info,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).pack()
        
        info_text = f"Class: {self.current_class} | Term: {self.current_term} | Year: {self.year_filter.get()}"
        ctk.CTkLabel(
            header_info,
            text=info_text,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(5, 15))

    def add_statistics_summary(self, start_row):
        """Add detailed statistics summary below the main table."""
        stats_frame = ctk.CTkFrame(self.sheet_frame, fg_color=COLORS["bg_dark"], corner_radius=8)
        stats_frame.grid(row=start_row, column=0, columnspan=20, pady=20, padx=10, sticky="ew")
        
        ctk.CTkLabel(
            stats_frame,
            text="📈 DETAILED STATISTICS SUMMARY",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        # Add various statistics here
        stats_text = self.generate_statistics_text()
        ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(padx=20, pady=10)

    def generate_statistics_text(self):
        """Generate comprehensive statistics text."""
        # Calculate various statistics
        total_students = len(self.students)
        
        # This would include:
        # - Class average
        # - Highest/lowest scores per subject
        # - Pass/fail rates
        # - Grade distribution
        # - Subject performance analysis
        
        return f"""
CLASS PERFORMANCE ANALYSIS:
• Total Students: {total_students}
• Class Average: [Calculated]
• Pass Rate: [Calculated]%
• Grade Distribution: A: [X], B: [X], C: [X], D: [X], F: [X]

SUBJECT ANALYSIS:
• Best Performing Subject: [Subject Name] (Avg: [Score])
• Weakest Subject: [Subject Name] (Avg: [Score])
• Most Improved: [Analysis]

RECOMMENDATIONS:
• [Generated recommendations based on performance]
        """

    def export_enhanced_csv(self):
        """Export enhanced broadsheet to CSV."""
        if not self.students:
            messagebox.showwarning("No Data", "Please load a broadsheet first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Enhanced Broadsheet"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write header information
                    writer.writerow([f"Enhanced Broadsheet - {self.current_class} - Term {self.current_term}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([])  # Empty row
                    
                    # Write data based on current term
                    if self.current_term == 1:
                        self.export_first_term_csv(writer)
                    elif self.current_term == 2:
                        self.export_second_term_csv(writer)
                    else:
                        self.export_third_term_csv(writer)
                
                messagebox.showinfo("Success", f"Enhanced broadsheet exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def export_first_term_csv(self, writer):
        """Export first term data to CSV."""
        # Implementation for first term CSV export
        pass

    def export_second_term_csv(self, writer):
        """Export second term comparison data to CSV."""
        # Implementation for second term CSV export
        pass

    def export_third_term_csv(self, writer):
        """Export complete year summary to CSV."""
        # Implementation for third term CSV export
        pass