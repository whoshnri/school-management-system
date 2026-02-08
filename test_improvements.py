#!/usr/bin/env python3
"""
Test script to verify UX improvements are working correctly.
"""

import sys
import traceback

def test_imports():
    """Test that all imports work correctly."""
    try:
        print("Testing imports...")
        
        # Test UI components import
        from ui_components import TextLabelManager, ModalController
        print("✓ UI components imported successfully")
        
        # Test text label manager
        button_text = TextLabelManager.get_button_text('view')
        assert button_text == 'View Details', f"Expected 'View Details', got '{button_text}'"
        print("✓ TextLabelManager working correctly")
        
        # Test forms import
        from forms import MarksEntryTab, AttendanceTab
        print("✓ Forms imported successfully")
        
        # Test enterprise forms import
        from enterprise_forms import StudentsListTab, SchoolFeesTab
        print("✓ Enterprise forms imported successfully")
        
        # Test date picker import
        from tkcalendar import DateEntry
        print("✓ Date picker imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_text_labels():
    """Test that text labels are working correctly."""
    try:
        print("\nTesting text labels...")
        from ui_components import TextLabelManager
        
        # Test button labels
        test_cases = [
            ('view', 'View Details'),
            ('edit', 'Edit'),
            ('delete', 'Delete'),
            ('save', 'Save'),
            ('load', 'Load')
        ]
        
        for key, expected in test_cases:
            result = TextLabelManager.get_button_text(key)
            assert result == expected, f"Button '{key}': expected '{expected}', got '{result}'"
        
        print("✓ All button text labels working correctly")
        
        # Test header labels
        header_cases = [
            ('student_registration', 'New Student Registration'),
            ('marks_entry', 'Marks Entry'),
            ('attendance', 'Attendance Tracker')
        ]
        
        for key, expected in header_cases:
            result = TextLabelManager.get_header_text(key)
            assert result == expected, f"Header '{key}': expected '{expected}', got '{result}'"
        
        print("✓ All header text labels working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Text labels test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=== School Management System UX Improvements Test ===\n")
    
    tests = [
        test_imports,
        test_text_labels
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! UX improvements are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())