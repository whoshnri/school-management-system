# Requirements Document

## Introduction

This document covers a set of improvements to the GFA Admin Panel, a desktop school administration application built with Python (tkinter/customtkinter), SQLAlchemy/SQLite, and ReportLab. The improvements span UI/branding, login UX, year selection, admission number integrity, phone validation, keyboard navigation, academic session management, PDF export quality, and a new department/subject schema.

## Glossary

- **App**: The GFA Admin Panel desktop application
- **Admin**: The authenticated school administrator using the App
- **Login_Window**: The authentication screen shown at application startup
- **Registration_Form**: The student registration form in the App
- **Admission_Number**: The 4-digit zero-padded sequential numeric suffix (e.g. `0001`) appended to the student ID prefix
- **Student_ID**: The full composite identifier for a student, formatted as `GFA/{YY}/S{XXXX}` where `YY` is the 2-digit start year of the session and `XXXX` is the 4-digit zero-padded Admission_Number (e.g. `GFA/24/S0001` for session `2024/2025`)
- **Session**: An academic year period in the format `YYYY/YYYY+1` (e.g. `2024/2025`)
- **Session_Manager**: The Sessions tab/table in the App where the Admin manages academic sessions
- **Year_Selector**: The admission year input widget in the Registration_Form
- **Phone_Field**: Any phone number input field in the Registration_Form (student phone or guardian phone)
- **Department**: One of three academic groupings — Science, Art, or Commercial — each with its own subject list
- **Subject**: An academic subject associated with a Department
- **PDF_Exporter**: The component responsible for generating PDF reports (report cards, broadsheets)
- **Matric_Number**: Synonym for Student_ID used in sorting and retrieval contexts

---

## Requirements

### Requirement 1: App Branding

**User Story:** As an Admin, I want the application to consistently display the "GFA" brand name, so that the app identity is clear and professional throughout.

#### Acceptance Criteria

1. THE App SHALL display "GFA Admin Panel" as the main window title.
2. THE App SHALL display "GFA" or "GFA Admin Panel" as the header text on all primary screens, replacing any previous school name references.
3. THE Login_Window SHALL display "GFA Admin Panel" as its title text.

---

### Requirement 2: UI Restyling

**User Story:** As an Admin, I want a clean white-background UI with blue accents, so that the interface is visually consistent and easy to read.

#### Acceptance Criteria

1. THE App SHALL use a white (`#FFFFFF`) background color for all primary content areas and frames.
2. THE App SHALL use a blue accent color (e.g. `#1a73e8`) for headers, active tab indicators, primary buttons, and section labels.
3. THE App SHALL apply the light appearance mode throughout, replacing the current dark theme.

---

### Requirement 3: Login Button

**User Story:** As an Admin, I want a visible Login button on the login screen, so that I can submit my credentials without relying solely on the keyboard.

#### Acceptance Criteria

1. THE Login_Window SHALL display a clearly labeled "Login" button that triggers the authentication submit action.
2. WHEN the Admin clicks the Login button, THE Login_Window SHALL execute the same credential verification logic as pressing the Enter key.
3. WHEN the Admin presses the Enter key, THE Login_Window SHALL continue to trigger the same submit action (existing behavior preserved).

---

### Requirement 4: Infinite Year Scroll

**User Story:** As an Admin, I want the year selector to scroll without boundaries, so that I can register students for any past or future admission year.

#### Acceptance Criteria

1. THE Year_Selector SHALL allow the Admin to increment the year without an upper boundary.
2. THE Year_Selector SHALL allow the Admin to decrement the year without a lower boundary.
3. THE Year_Selector SHALL not restrict year selection to a predefined list of years.

---

### Requirement 5: Admission Number Prefix Integrity

**User Story:** As an Admin, I want the admission number prefix to always be "S" with a 4-digit sequential number, so that student IDs are consistently formatted and never corrupted.

#### Acceptance Criteria

1. THE Registration_Form SHALL always display the student ID prefix ending in "S" (e.g. `GFA/24/S`).
2. WHEN the Admin submits the Registration_Form, THE App SHALL construct the Student_ID using the format `GFA/{YY}/S{XXXX}` where `YY` is the 2-digit start year of the selected session and `XXXX` is a 4-digit zero-padded sequential number (e.g. `GFA/24/S0001` for session `2024/2025`).
3. THE App SHALL not inject the character "J" into the Admission_Number at any point during the registration flow, including during ID preview updates, form resets, and submission.
4. WHEN the admission year changes, THE Registration_Form SHALL update the ID prefix to `GFA/{YY}/S`, preserving the "S" character.
5. THE App SHALL zero-pad the sequential number to exactly 4 digits (e.g. `0001`, `0042`, `1000`).

---

### Requirement 6: Phone Number Validation

**User Story:** As an Admin, I want phone number fields to enforce an 11-digit limit with a visible error, so that invalid phone numbers are caught before saving.

#### Acceptance Criteria

1. WHEN the Admin enters more than 11 characters in a Phone_Field, THE Registration_Form SHALL display an inline error message "Value is not allowed" adjacent to that field.
2. THE Registration_Form SHALL not silently truncate or clamp phone number input to 11 digits.
3. WHEN the phone number input is 11 digits or fewer, THE Registration_Form SHALL not display a phone validation error.
4. WHEN the Admin submits the Registration_Form with a phone number exceeding 11 digits, THE Registration_Form SHALL block submission and display the inline error.

---

### Requirement 7: Keyboard Navigation (Shift+Tab)

**User Story:** As an Admin, I want to navigate backwards through registration form fields using Shift+Tab, so that I can efficiently correct earlier inputs without using the mouse.

#### Acceptance Criteria

1. WHEN the Admin presses Shift+Tab while a text input in the Registration_Form has focus, THE Registration_Form SHALL move focus to the previous input field.
2. THE Registration_Form SHALL support Shift+Tab backwards navigation across all text entry fields in the form's tab order.
3. WHEN the Admin presses Tab while a text input has focus, THE Registration_Form SHALL continue to move focus to the next input field (existing forward navigation preserved).

---

### Requirement 8: Session Management

**User Story:** As an Admin, I want to create and manage academic sessions, so that student records are organized by academic year.

#### Acceptance Criteria

1. THE App SHALL provide a dedicated Sessions tab containing a Session_Manager table that lists all academic sessions.
2. WHEN the Admin creates a new session with a valid `YYYY/YYYY+1` format, THE Session_Manager SHALL persist the session to the database.
3. IF the Admin attempts to create a session with an invalid format, THEN THE Session_Manager SHALL display an error message and not save the record.
4. THE Session_Manager SHALL allow the Admin to designate exactly one session as the active session at any time.
5. WHEN the Admin opens the Registration_Form, THE Registration_Form SHALL display a session selector populated with all available sessions.
6. WHEN the Admin selects a session during registration, THE Registration_Form SHALL derive the 2-digit start year (`YY`) from the session's start year (e.g. session `2024/2025` → `YY = 24`) and use it to construct the Student_ID in the format `GFA/{YY}/S{XXXX}`.
7. THE App SHALL allow the Admin to retrieve and sort student records by Matric_Number.

---

### Requirement 9: PDF Export Quality

**User Story:** As an Admin, I want PDF exports to be fully styled and properly paginated, so that printed reports are professional and complete.

#### Acceptance Criteria

1. THE PDF_Exporter SHALL render all student and academic content without truncation or cut-off.
2. THE PDF_Exporter SHALL apply consistent fonts and spacing throughout the generated document.
3. WHEN the content exceeds a single page, THE PDF_Exporter SHALL paginate the content correctly across multiple pages.
4. THE PDF_Exporter SHALL apply consistent styling (headers, borders, font sizes) matching the school's report card layout.
5. WHEN a PDF is generated and then opened, all fields visible in the App SHALL be present in the PDF output.

---

### Requirement 10: Department Model

**User Story:** As an Admin, I want to manage departments and their subject lists, so that students are enrolled in the correct academic track with the right subjects.

#### Acceptance Criteria

1. THE App SHALL define exactly three departments: Science, Art, and Commercial.
2. THE App SHALL persist each Department and its associated subjects in the database.
3. THE Admin SHALL be able to add a subject to a Department through the App's department management interface.
4. THE Admin SHALL be able to edit a subject name within a Department.
5. THE Admin SHALL be able to remove a subject from a Department.
6. WHEN the Admin opens the Registration_Form, THE Registration_Form SHALL display a department selector showing all three departments.
7. WHEN the Admin selects a department during registration, THE Registration_Form SHALL associate the student record with that Department and its current subject list.
8. THE App SHALL store the department association on the student record in the database.
9. WHEN the App is run for the first time and no department subjects exist, THE App SHALL pre-seed each Department with the following default subjects:
   - Science: English Language, Mathematics, Physics, Chemistry, Biology, Agricultural Science, Further Mathematics, Geography, Data Processing
   - Art: English Language, Mathematics, Civic Education, Economics, Geography, Food and Nutrition, Literature in English, Government, History
   - Commercial: English Language, Mathematics, Civic Education, Economics, Commerce, Financial Accounting, Data Processing, Business Studies, Office Practice
