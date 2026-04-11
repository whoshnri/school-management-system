# Implementation Tasks

## Tasks

- [-] 1. Update models.py with new tables and migration
  - [ ] 1.1 Add AcademicSession model
  - [ ] 1.2 Add Department and DepartmentSubject models
  - [ ] 1.3 Add dept_id and session_id columns to Student
  - [ ] 1.4 Add run_migrations() function using PRAGMA table_info

- [-] 2. Update main.py — branding, theme, seeding
  - [ ] 2.1 Switch appearance mode to light
  - [ ] 2.2 Update window titles and header labels to "GFA Admin Panel"
  - [ ] 2.3 Update COLORS dict to white/blue light theme
  - [ ] 2.4 Add initialize_departments() and call it on startup
  - [ ] 2.5 Call run_migrations() on startup

- [-] 3. Rewrite report_card_pdf.py
  - [ ] 3.1 Remove attendance section
  - [ ] 3.2 Add school header image placeholder (full width, 2/5 height ratio)
  - [ ] 3.3 Student info as 4-column table
  - [ ] 3.4 Fix column widths to fit A4 (6.27in usable)
  - [ ] 3.5 Add KeepTogether for all sections
  - [ ] 3.6 Update CA(30)/Exam(70) header labels
  - [ ] 3.7 Term comparison logic (T1 standard, T2 side-by-side, T3 all+avg)

- [-] 4. Create sessions_tab.py
  - [ ] 4.1 SessionsTab widget with list, add, set-active, delete
  - [ ] 4.2 Session name validation (YYYY/YYYY+1 format)
  - [ ] 4.3 At-most-one-active invariant

- [-] 5. Create departments_tab.py
  - [ ] 5.1 DepartmentsTab widget with Science/Art/Commercial selector
  - [ ] 5.2 Subject list with add, edit, remove per department

- [-] 6. Update enhanced_registration.py
  - [ ] 6.1 Replace year ComboBox with YearSpinner widget
  - [ ] 6.2 Add session selector ComboBox from AcademicSession records
  - [ ] 6.3 Fix admission number to always use S prefix, 4-digit zero-padded
  - [ ] 6.4 Add phone validation (11-digit limit, inline error)
  - [ ] 6.5 Add Shift+Tab keyboard navigation
  - [ ] 6.6 Add department selector ComboBox

- [-] 7. Update enterprise_forms.py
  - [ ] 7.1 Update COLORS to light theme
  - [ ] 7.2 Update all titles/headers to GFA branding
  - [ ] 7.3 Add SessionsTab to main tab view
  - [ ] 7.4 Add DepartmentsTab to main tab view

- [-] 8. Delete temp files
  - [x] 8.1 Delete report_card_pdf_new.py
  - [x] 8.2 Delete _create_report_card.py
