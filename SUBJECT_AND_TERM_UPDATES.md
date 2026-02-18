# Subject List and Term Naming Updates

## Date: February 18, 2026

## Updates Completed

### 1. Subject List Updated
**File:** `main.py`

**New Subject List (12 subjects):**
1. English Language
2. Mathematics
3. Civic Education
4. Economics
5. Physics
6. Chemistry
7. Biology
8. Agricultural Science
9. Further Mathematics
10. Geography
11. Food and Nutrition
12. Data Processing

**Previous:** 28 subjects including History, Government, Commerce, Literature, Languages (Hausa, Igbo, Yoruba, French), Religious Studies, etc.

### 2. Term Naming Convention Updated

**Changed From:** T1, T2, T3
**Changed To:** First Term, Second Term, Third Term

**Files Updated:**
- ✅ `student_details_windows.py` - Results view headers
- ✅ `enhanced_broadsheet.py` - Broadsheet headers for all term views

**Examples:**
- "T2 CA" → "Second Term CA"
- "T1 Exam" → "First Term Exam"  
- "T3 Total" → "Third Term Total"

### 3. Display Changes

**Student Results Window:**
- Term comparison headers now show full term names
- Example: "Second Term CA | First Term CA | Second Term Exam | First Term Exam"

**Enhanced Broadsheet:**
- Second Term Report: Shows "Second Term" and "First Term" columns
- Third Term Report: Shows "Third Term", "Second Term", and "First Term" columns

## Implementation Notes

- Subject codes remain short for database efficiency (ENG, MATH, CIVIC, etc.)
- Full subject names are displayed in all user-facing interfaces
- Term naming is more professional and easier to understand
- All existing data remains compatible - only display labels changed

## Testing Recommendations

1. Verify all 12 subjects appear in marks entry
2. Check term comparison views show correct term names
3. Test broadsheet generation for all three terms
4. Confirm PDF report cards use updated terminology
