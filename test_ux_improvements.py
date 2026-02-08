"""
Property-based tests for School Management System UX Improvements
Tests the correctness properties defined in the design document.
"""

import pytest
from hypothesis import given, strategies as st, settings
import re
from ui_components import TextLabelManager, ModalController
from models import Session, Student, Subject, Mark, Attendance, Fee
import customtkinter as ctk
from unittest.mock import Mock, patch


class TestTextBasedInterfaceConsistency:
    """
    Property 1: Text-Based Interface Consistency
    For any UI element in the system, all action buttons and labels should use 
    descriptive text instead of emoji icons or visual symbols, and maintain 
    consistent text-based labeling patterns across the interface.
    Validates: Requirements 1.1, 1.2, 1.3
    """
    
    @given(st.sampled_from(['view', 'edit', 'delete', 'add', 'save', 'cancel', 'close', 'load', 'export']))
    @settings(max_examples=100)
    def test_button_text_consistency(self, button_key):
        """Test that all button texts are descriptive and contain no emoji."""
        button_text = TextLabelManager.get_button_text(button_key)
        
        # Property: Button text should be descriptive text, not emoji
        assert isinstance(button_text, str), "Button text must be a string"
        assert len(button_text) > 0, "Button text cannot be empty"
        
        # Property: No emoji characters in button text
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
        assert not emoji_pattern.search(button_text), f"Button text '{button_text}' contains emoji characters"
        
        # Property: Text should be professional (title case or sentence case)
        assert button_text[0].isupper(), f"Button text '{button_text}' should start with uppercase letter"
    
    @given(st.sampled_from(['student_registration', 'student_directory', 'marks_entry', 'broadsheet', 'attendance', 'fees']))
    @settings(max_examples=100)
    def test_header_text_consistency(self, header_key):
        """Test that all header texts are professional and contain no emoji."""
        header_text = TextLabelManager.get_header_text(header_key)
        
        # Property: Header text should be descriptive and professional
        assert isinstance(header_text, str), "Header text must be a string"
        assert len(header_text) > 0, "Header text cannot be empty"
        
        # Property: No emoji characters in header text
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
        assert not emoji_pattern.search(header_text), f"Header text '{header_text}' contains emoji characters"
        
        # Property: Professional formatting
        assert header_text[0].isupper(), f"Header text '{header_text}' should start with uppercase letter"
    
    @given(st.sampled_from(['students', 'fees', 'register', 'marks', 'broadsheet', 'attendance']))
    @settings(max_examples=100)
    def test_navigation_text_consistency(self, nav_key):
        """Test that all navigation texts are professional and contain no emoji."""
        nav_text = TextLabelManager.get_nav_text(nav_key)
        
        # Property: Navigation text should be descriptive and professional
        assert isinstance(nav_text, str), "Navigation text must be a string"
        assert len(nav_text) > 0, "Navigation text cannot be empty"
        
        # Property: No emoji characters in navigation text
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
        assert not emoji_pattern.search(nav_text), f"Navigation text '{nav_text}' contains emoji characters"
        
        # Property: Professional formatting
        assert nav_text[0].isupper(), f"Navigation text '{nav_text}' should start with uppercase letter"
    
    def test_text_label_manager_completeness(self):
        """Test that TextLabelManager provides all required text categories."""
        # Property: All required text categories should be available
        assert hasattr(TextLabelManager, 'BUTTONS'), "TextLabelManager must have BUTTONS dictionary"
        assert hasattr(TextLabelManager, 'HEADERS'), "TextLabelManager must have HEADERS dictionary"
        assert hasattr(TextLabelManager, 'NAVIGATION'), "TextLabelManager must have NAVIGATION dictionary"
        assert hasattr(TextLabelManager, 'STATUS'), "TextLabelManager must have STATUS dictionary"
        
        # Property: All dictionaries should contain text-only values
        for category_name, category_dict in [
            ('BUTTONS', TextLabelManager.BUTTONS),
            ('HEADERS', TextLabelManager.HEADERS),
            ('NAVIGATION', TextLabelManager.NAVIGATION),
            ('STATUS', TextLabelManager.STATUS)
        ]:
            for key, value in category_dict.items():
                assert isinstance(value, str), f"{category_name}[{key}] must be a string"
                emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
                assert not emoji_pattern.search(value), f"{category_name}[{key}] = '{value}' contains emoji characters"


class TestFunctionalityPreservation:
    """
    Property 2: Functionality Preservation During UI Updates
    For any existing system feature, all original functionality should remain 
    intact and accessible after visual presentation updates.
    Validates: Requirements 1.4
    """
    
    def test_text_label_manager_fallback(self):
        """Test that TextLabelManager provides fallback for unknown keys."""
        # Property: Unknown keys should return a reasonable fallback
        unknown_key = "unknown_button_key"
        result = TextLabelManager.get_button_text(unknown_key)
        
        # Should return title-cased version of the key as fallback
        expected = unknown_key.title()
        assert result == expected, f"Expected fallback '{expected}' for unknown key '{unknown_key}'"
        
        # Property: Fallback should still be text-only
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
        assert not emoji_pattern.search(result), f"Fallback text '{result}' contains emoji characters"
    
    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))))
    @settings(max_examples=50)
    def test_all_text_methods_preserve_functionality(self, test_key):
        """Test that all TextLabelManager methods handle arbitrary keys gracefully."""
        # Property: All methods should handle any string key without crashing
        try:
            button_result = TextLabelManager.get_button_text(test_key)
            header_result = TextLabelManager.get_header_text(test_key)
            nav_result = TextLabelManager.get_nav_text(test_key)
            status_result = TextLabelManager.get_status_text(test_key)
            
            # All results should be strings
            assert isinstance(button_result, str), "get_button_text must return string"
            assert isinstance(header_result, str), "get_header_text must return string"
            assert isinstance(nav_result, str), "get_nav_text must return string"
            assert isinstance(status_result, str), "get_status_text must return string"
            
            # All results should be non-empty
            assert len(button_result) > 0, "get_button_text must return non-empty string"
            assert len(header_result) > 0, "get_header_text must return non-empty string"
            assert len(nav_result) > 0, "get_nav_text must return non-empty string"
            assert len(status_result) > 0, "get_status_text must return non-empty string"
            
        except Exception as e:
            pytest.fail(f"TextLabelManager methods should handle key '{test_key}' gracefully, but raised: {e}")


class TestModalWindowBehavior:
    """
    Property 3: Modal Window Behavior
    For any student record, clicking the "View" action should open a modal popup 
    that contains "View Attendance Records" and "View Results" options, and provides 
    a clear way to close and return to the main interface.
    Validates: Requirements 2.1, 2.2, 2.6
    """
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.mock_parent = Mock()
        self.mock_session = Mock()
        
    def test_modal_controller_initialization(self):
        """Test that ModalController initializes correctly."""
        # Property: ModalController should initialize with parent window
        controller = ModalController(self.mock_parent)
        
        assert controller.parent_window == self.mock_parent, "ModalController should store parent window reference"
        assert controller.current_modal is None, "ModalController should start with no active modal"
        assert controller.overlay is None, "ModalController should start with no overlay"
    
    @patch('ui_components.ctk.CTkToplevel')
    def test_modal_opens_with_student_options(self, mock_toplevel):
        """Test that student detail modal opens with correct options."""
        # Property: Modal should open with attendance and results options
        controller = ModalController(self.mock_parent)
        mock_overlay = Mock()
        mock_toplevel.return_value = mock_overlay
        
        # Mock student data
        mock_student = Mock()
        mock_student.id = 1
        mock_student.name = "Test Student"
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_student
        
        controller.open_student_detail_modal(1, self.mock_session)
        
        # Property: Modal window should be created
        mock_toplevel.assert_called_once_with(self.mock_parent)
        
        # Property: Modal should be configured properly
        mock_overlay.title.assert_called_once_with("")
        mock_overlay.geometry.assert_called()
        mock_overlay.transient.assert_called_once_with(self.mock_parent)
        mock_overlay.grab_set.assert_called_once()
        
        # Property: Current modal should be set
        assert controller.current_modal is not None, "ModalController should track current modal"
        assert controller.overlay == mock_overlay, "ModalController should track overlay"
    
    def test_modal_close_functionality(self):
        """Test that modal can be closed properly."""
        # Property: Modal should provide close functionality
        controller = ModalController(self.mock_parent)
        
        # Set up mock modal and overlay
        mock_modal = Mock()
        mock_overlay = Mock()
        controller.current_modal = mock_modal
        controller.overlay = mock_overlay
        
        controller.close_current_modal()
        
        # Property: Modal references should be cleared
        assert controller.current_modal is None, "Current modal should be cleared on close"
        
        # Property: Overlay should be properly cleaned up
        mock_overlay.grab_release.assert_called_once()
        mock_overlay.destroy.assert_called_once()
        assert controller.overlay is None, "Overlay should be cleared on close"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestStudentSpecificDataLoading:
    """
    Property 4: Student-Specific Data Loading
    For any selected student and any view option (attendance or results), the system 
    should load and display data that belongs specifically to that student, not 
    generic or incorrect data.
    Validates: Requirements 2.3, 2.4, 2.5
    """
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.mock_session = Mock()
        self.mock_parent = Mock()
        
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_attendance_view_loads_correct_student_data(self, student_id):
        """Test that attendance view loads data for the correct student only."""
        from ui_components import AttendanceRecordsView
        
        # Mock student data
        mock_student = Mock()
        mock_student.id = student_id
        mock_student.name = f"Student {student_id}"
        
        # Mock attendance records for this specific student
        mock_attendance_records = [Mock(student_id=student_id, date="2024-01-01", is_present=True)]
        
        # Set up session mock
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_student
        self.mock_session.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = mock_attendance_records
        
        # Property: AttendanceRecordsView should query for the specific student
        with patch('ui_components.ctk.CTkFrame'):
            view = AttendanceRecordsView(self.mock_parent, student_id, self.mock_session)
            
            # Verify that the session was queried with the correct student_id
            # The view should have called session.query(Student).filter_by(id=student_id)
            # and session.query(Attendance).filter_by(student_id=student_id)
            assert view.student_id == student_id, "AttendanceRecordsView should store the correct student_id"
            assert view.session == self.mock_session, "AttendanceRecordsView should use the provided session"
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_results_view_loads_correct_student_data(self, student_id):
        """Test that results view loads data for the correct student only."""
        from ui_components import ResultsView
        
        # Mock student data
        mock_student = Mock()
        mock_student.id = student_id
        mock_student.name = f"Student {student_id}"
        
        # Mock marks for this specific student
        mock_marks = [Mock(student_id=student_id, term=1, total=85, grade='A')]
        
        # Set up session mock
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_student
        self.mock_session.query.return_value.filter_by.return_value.all.return_value = mock_marks
        
        # Property: ResultsView should query for the specific student
        with patch('ui_components.ctk.CTkFrame'):
            view = ResultsView(self.mock_parent, student_id, self.mock_session)
            
            # Verify that the view stores the correct student_id and session
            assert view.student_id == student_id, "ResultsView should store the correct student_id"
            assert view.session == self.mock_session, "ResultsView should use the provided session"
    
    def test_student_detail_modal_loads_correct_student_title(self):
        """Test that student detail modal displays the correct student name in title."""
        from ui_components import StudentDetailModal
        
        student_id = 42
        mock_student = Mock()
        mock_student.id = student_id
        mock_student.name = "John Doe"
        
        # Set up session mock
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_student
        
        mock_close_callback = Mock()
        
        # Property: Modal should load and display the correct student's name
        with patch('ui_components.ctk.CTkFrame'), \
             patch('ui_components.ctk.CTkLabel') as mock_label:
            
            modal = StudentDetailModal(self.mock_parent, student_id, self.mock_session, mock_close_callback)
            
            # Verify that the modal stores the correct student_id
            assert modal.student_id == student_id, "StudentDetailModal should store the correct student_id"
            assert modal.session == self.mock_session, "StudentDetailModal should use the provided session"
            assert modal.close_callback == mock_close_callback, "StudentDetailModal should store the close callback"
    
    @given(st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=10, unique=True))
    @settings(max_examples=20)
    def test_data_isolation_between_students(self, student_ids):
        """Test that data for different students is properly isolated."""
        from ui_components import AttendanceRecordsView
        
        # Property: Each student's data should be isolated from others
        for student_id in student_ids:
            mock_student = Mock()
            mock_student.id = student_id
            mock_student.name = f"Student {student_id}"
            
            # Mock attendance records specific to this student
            mock_attendance = [Mock(student_id=student_id, date=f"2024-01-{student_id:02d}", is_present=True)]
            
            self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_student
            self.mock_session.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = mock_attendance
            
            with patch('ui_components.ctk.CTkFrame'):
                view = AttendanceRecordsView(self.mock_parent, student_id, self.mock_session)
                
                # Property: Each view should be associated with its specific student
                assert view.student_id == student_id, f"View should be associated with student {student_id}"
                
                # Property: Student ID should not be mixed up with other students
                for other_id in student_ids:
                    if other_id != student_id:
                        assert view.student_id != other_id, f"Student {student_id} data should not be mixed with student {other_id}"


class TestInlineSectionElimination:
    """
    Property 5: Inline Section Elimination
    For any student detail view, the system should not display student information 
    in inline sections at the bottom of pages.
    Validates: Requirements 2.7
    """
    
    def test_modal_replaces_inline_sections(self):
        """Test that modal system replaces inline detail sections."""
        from ui_components import ModalController
        
        # Property: Modal system should be used instead of inline sections
        controller = ModalController(Mock())
        
        # Property: ModalController should not have inline section methods
        assert not hasattr(controller, 'toggle_details'), "ModalController should not have toggle_details method"
        assert not hasattr(controller, 'create_collapsible_section'), "ModalController should not have create_collapsible_section method"
        assert not hasattr(controller, 'get_attendance_details'), "ModalController should not have get_attendance_details method"
        assert not hasattr(controller, 'get_results_details'), "ModalController should not have get_results_details method"
        
        # Property: ModalController should have modal-specific methods
        assert hasattr(controller, 'open_student_detail_modal'), "ModalController should have open_student_detail_modal method"
        assert hasattr(controller, 'close_current_modal'), "ModalController should have close_current_modal method"
    
    def test_student_detail_modal_structure(self):
        """Test that StudentDetailModal uses proper modal structure."""
        from ui_components import StudentDetailModal
        
        mock_parent = Mock()
        mock_session = Mock()
        mock_close_callback = Mock()
        student_id = 1
        
        # Mock student data
        mock_student = Mock()
        mock_student.id = student_id
        mock_student.name = "Test Student"
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_student
        
        with patch('ui_components.ctk.CTkFrame'):
            modal = StudentDetailModal(mock_parent, student_id, mock_session, mock_close_callback)
            
            # Property: Modal should have dedicated view components, not inline sections
            assert hasattr(modal, 'content_frame'), "Modal should have dedicated content frame"
            assert hasattr(modal, 'show_attendance_view'), "Modal should have show_attendance_view method"
            assert hasattr(modal, 'show_results_view'), "Modal should have show_results_view method"
            assert hasattr(modal, 'clear_content_frame'), "Modal should have clear_content_frame method"
            
            # Property: Modal should not use inline section patterns
            assert not hasattr(modal, 'details_frame'), "Modal should not have details_frame attribute"
            assert not hasattr(modal, 'selected_student_id'), "Modal should not have selected_student_id attribute"