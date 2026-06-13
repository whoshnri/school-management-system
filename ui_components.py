"""
UI Components for School Management System
Provides professional text-based interface components and modal management.
"""

import re
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Optional, Callable, Dict, Any
from datetime import datetime, date as dt_date
from tkcalendar import Calendar


DATE_PICKER_COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "border": "#dadce0",
    "text_primary": "#202124",
    "text_secondary": "#5f6368",
    "bg_card": "#f8f9fa",
    "active_text": "#ffffff",
}


class DatePickerField(ctk.CTkFrame):
    """Date picker that opens a modal calendar so scrolling does not break selection."""

    def __init__(
        self,
        parent,
        initial_date=None,
        maxdate=None,
        mindate=None,
        width=160,
        height=45,
        font_size=14,
        on_change=None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._maxdate = maxdate
        self._mindate = mindate
        self._on_change = on_change
        self._popup = None
        self._date = initial_date or dt_date.today()

        self._date_var = ctk.StringVar(value=self._format_date(self._date))

        self._entry = ctk.CTkEntry(
            self,
            textvariable=self._date_var,
            width=width,
            height=height,
            corner_radius=10,
            border_width=1,
            border_color=DATE_PICKER_COLORS["border"],
            font=ctk.CTkFont(size=font_size),
        )
        self._entry.pack(side="left", fill="x", expand=True)
        self._entry.bind("<Key>", lambda _e: "break")
        self._entry.bind("<Button-1>", lambda _e: self._open_picker())

        self._button = ctk.CTkButton(
            self,
            text="Pick",
            width=56,
            height=height,
            corner_radius=10,
            fg_color=DATE_PICKER_COLORS["primary"],
            hover_color=DATE_PICKER_COLORS["primary_hover"],
            font=ctk.CTkFont(size=font_size - 1),
            command=self._open_picker,
        )
        self._button.pack(side="left", padx=(8, 0))

    def _format_date(self, value):
        return value.strftime("%Y-%m-%d")

    def get_date(self):
        return self._date

    def set_date(self, value):
        if isinstance(value, str):
            value = dt_date.fromisoformat(value)
        if self._maxdate and value > self._maxdate:
            value = self._maxdate
        if self._mindate and value < self._mindate:
            value = self._mindate
        self._date = value
        self._date_var.set(self._format_date(self._date))

    def _close_popup(self):
        popup = self._popup
        self._popup = None
        if popup is not None and popup.winfo_exists():
            try:
                popup.grab_release()
            except Exception:
                pass
            popup.destroy()

    def _open_picker(self):
        if self._popup is not None and self._popup.winfo_exists():
            return

        root = self.winfo_toplevel()
        popup = ctk.CTkToplevel(root)
        popup.title("Select Date")
        popup.resizable(False, False)
        popup.transient(root)
        self._popup = popup

        body = ctk.CTkFrame(popup, fg_color=DATE_PICKER_COLORS["bg_card"], corner_radius=12)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            body,
            text="Select Date",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=DATE_PICKER_COLORS["text_primary"],
        ).pack(anchor="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            body,
            text="Choose a day, then click Done.",
            font=ctk.CTkFont(size=12),
            text_color=DATE_PICKER_COLORS["text_secondary"],
        ).pack(anchor="w", padx=8, pady=(0, 8))

        cal_host = tk.Frame(body, bg=DATE_PICKER_COLORS["bg_card"])
        cal_host.pack(padx=8, pady=4)

        cal_kwargs = {
            "selectmode": "day",
            "date_pattern": "yyyy-mm-dd",
            "background": DATE_PICKER_COLORS["primary"],
            "foreground": "white",
            "headersbackground": DATE_PICKER_COLORS["primary"],
            "headersforeground": "white",
            "selectbackground": DATE_PICKER_COLORS["primary_hover"],
            "normalbackground": "white",
            "normalforeground": DATE_PICKER_COLORS["text_primary"],
            "weekendbackground": "#eef4fd",
            "borderwidth": 0,
            "year": self._date.year,
            "month": self._date.month,
            "day": self._date.day,
        }
        if self._maxdate:
            cal_kwargs["maxdate"] = self._maxdate
        if self._mindate:
            cal_kwargs["mindate"] = self._mindate

        calendar = Calendar(cal_host, **cal_kwargs)
        calendar.pack()

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(12, 8))

        def confirm():
            selected = calendar.selection_get()
            if selected is None:
                messagebox.showwarning(
                    "Select Date",
                    "Please choose a day from the calendar.",
                    parent=popup,
                )
                return
            self._date = selected
            self._date_var.set(self._format_date(self._date))
            self._close_popup()
            if self._on_change:
                self._on_change()

        ctk.CTkButton(
            btn_row,
            text="Done",
            width=90,
            height=36,
            fg_color=DATE_PICKER_COLORS["primary"],
            hover_color=DATE_PICKER_COLORS["primary_hover"],
            command=confirm,
        ).pack(side="right")

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=90,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=DATE_PICKER_COLORS["border"],
            text_color=DATE_PICKER_COLORS["text_secondary"],
            hover_color=DATE_PICKER_COLORS["bg_card"],
            command=self._close_popup,
        ).pack(side="right", padx=(0, 8))

        popup.protocol("WM_DELETE_WINDOW", self._close_popup)
        popup.bind("<Escape>", lambda _e: self._close_popup())

        popup.update_idletasks()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = root.winfo_rootx() + max((root.winfo_width() - popup_width) // 2, 0)
        y = root.winfo_rooty() + max((root.winfo_height() - popup_height) // 2, 0)
        popup.geometry(f"+{x}+{y}")

        popup.wait_visibility()
        popup.grab_set()
        popup.focus_force()


NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
    "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe",
    "Zamfara", "FCT",
]


class ModalOptionPicker(ctk.CTkFrame):
    """Opens a scrollable modal to choose from a list of options."""

    def __init__(
        self,
        parent,
        options,
        title="Select",
        placeholder="Select an option",
        width=380,
        height=45,
        font_size=14,
        initial_value="",
        on_change=None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._choice_options = list(options)
        self._title = title
        self._on_change = on_change
        self._popup = None
        self._value_var = ctk.StringVar(value=initial_value or "")

        self._entry = ctk.CTkEntry(
            self,
            textvariable=self._value_var,
            placeholder_text=placeholder,
            width=width,
            height=height,
            corner_radius=10,
            border_width=1,
            border_color=DATE_PICKER_COLORS["border"],
            font=ctk.CTkFont(size=font_size),
        )
        self._entry.pack(side="left", fill="x", expand=True)
        self._entry.bind("<Key>", lambda _e: "break")
        self._entry.bind("<Button-1>", lambda _e: self._open_picker())

        self._button = ctk.CTkButton(
            self,
            text="Select",
            width=72,
            height=height,
            corner_radius=10,
            fg_color=DATE_PICKER_COLORS["primary"],
            hover_color=DATE_PICKER_COLORS["primary_hover"],
            font=ctk.CTkFont(size=font_size - 1),
            command=self._open_picker,
        )
        self._button.pack(side="left", padx=(8, 0))

    def get(self):
        return self._value_var.get().strip()

    def set(self, value):
        self._value_var.set(value or "")

    def _close_popup(self):
        popup = self._popup
        self._popup = None
        if popup is not None and popup.winfo_exists():
            try:
                popup.grab_release()
            except Exception:
                pass
            popup.destroy()

    def _select_option(self, option):
        self._value_var.set(option)
        self._close_popup()
        if self._on_change:
            self._on_change()

    def _open_picker(self):
        if self._popup is not None and self._popup.winfo_exists():
            return

        root = self.winfo_toplevel()
        popup = ctk.CTkToplevel(root)
        popup.title(self._title)
        popup.resizable(False, False)
        popup.transient(root)
        self._popup = popup

        body = ctk.CTkFrame(popup, fg_color=DATE_PICKER_COLORS["bg_card"], corner_radius=12)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            body,
            text=self._title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=DATE_PICKER_COLORS["text_primary"],
        ).pack(anchor="w", padx=8, pady=(8, 4))

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            body,
            textvariable=search_var,
            placeholder_text="Search...",
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=DATE_PICKER_COLORS["border"],
            font=ctk.CTkFont(size=13),
        )
        search_entry.pack(fill="x", padx=8, pady=(4, 10))

        list_frame = ctk.CTkScrollableFrame(
            body,
            width=320,
            height=320,
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color=DATE_PICKER_COLORS["border"],
            scrollbar_button_color=DATE_PICKER_COLORS["primary"],
            scrollbar_button_hover_color=DATE_PICKER_COLORS["primary_hover"],
        )
        list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        current_value = self.get()

        def render_options(filter_text=""):
            for widget in list_frame.winfo_children():
                widget.destroy()

            query = filter_text.strip().lower()
            matches = [
                option for option in self._choice_options
                if not query or query in option.lower()
            ]

            if not matches:
                ctk.CTkLabel(
                    list_frame,
                    text="No matches found",
                    font=ctk.CTkFont(size=13),
                    text_color=DATE_PICKER_COLORS["text_secondary"],
                ).pack(pady=20)
                return

            for option in matches:
                is_selected = option == current_value
                ctk.CTkButton(
                    list_frame,
                    text=option,
                    anchor="w",
                    height=38,
                    corner_radius=8,
                    fg_color=DATE_PICKER_COLORS["primary"] if is_selected else "transparent",
                    text_color=DATE_PICKER_COLORS["active_text"] if is_selected else DATE_PICKER_COLORS["text_primary"],
                    hover_color=DATE_PICKER_COLORS["primary_hover"],
                    font=ctk.CTkFont(size=13),
                    command=lambda value=option: self._select_option(value),
                ).pack(fill="x", pady=2)

        search_var.trace_add("write", lambda *_args: render_options(search_var.get()))
        render_options()

        ctk.CTkButton(
            body,
            text="Cancel",
            width=90,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=DATE_PICKER_COLORS["border"],
            text_color=DATE_PICKER_COLORS["text_secondary"],
            hover_color=DATE_PICKER_COLORS["bg_card"],
            command=self._close_popup,
        ).pack(anchor="e", padx=8, pady=(0, 8))

        popup.protocol("WM_DELETE_WINDOW", self._close_popup)
        popup.bind("<Escape>", lambda _e: self._close_popup())

        popup.update_idletasks()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = root.winfo_rootx() + max((root.winfo_width() - popup_width) // 2, 0)
        y = root.winfo_rooty() + max((root.winfo_height() - popup_height) // 2, 0)
        popup.geometry(f"+{x}+{y}")

        popup.wait_visibility()
        popup.grab_set()
        popup.focus_force()
        search_entry.focus_set()


MODAL_STYLE = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "success": "#34a853",
    "success_hover": "#2d8f47",
    "secondary": "#5f6368",
    "secondary_hover": "#4a4f54",
    "danger": "#ea4335",
    "bg_main": "#ffffff",
    "bg_card": "#f8f9fa",
    "text_primary": "#202124",
    "text_secondary": "#5f6368",
    "text_on_primary": "#ffffff",
    "text_on_primary_muted": "#dbeafe",
    "border": "#dadce0",
    "padding": 24,
    "label_width": 160,
    "input_width": 420,
    "input_height": 42,
    "radius": 10,
}

CLASS_FILTER_OPTIONS = ["All Classes", "SSS1", "SSS2", "SSS3"]


def safe_export_filename(*parts, extension=""):
    """Build a filesystem-safe default export name from one or more parts."""
    def clean(part):
        text = str(part).strip()
        text = re.sub(r'[/\\:*?"<>|]', "-", text)
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[-_]+", "_", text)
        return text.strip("._-")

    segments = [clean(part) for part in parts if part is not None and str(part).strip()]
    base = "_".join(segments) if segments else "export"
    if extension:
        ext = extension if extension.startswith(".") else f".{extension}"
        return f"{base}{ext}"
    return base


def input_style(**kwargs):
    """Shared styling for modal text inputs."""
    options = {
        "corner_radius": MODAL_STYLE["radius"],
        "border_width": 1,
        "border_color": MODAL_STYLE["border"],
        "font": ctk.CTkFont(family="Segoe UI", size=13),
    }
    options.update(kwargs)
    return options


def center_toplevel(window, parent, width, height):
    window.update_idletasks()
    x = parent.winfo_rootx() + max((parent.winfo_width() - width) // 2, 0)
    y = parent.winfo_rooty() + max((parent.winfo_height() - height) // 2, 0)
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_modal_header(parent, title, subtitle=None):
    """Create a consistent modal header with readable contrast."""
    header = ctk.CTkFrame(parent, fg_color=MODAL_STYLE["primary"], corner_radius=0)
    header.pack(fill="x")

    inner = ctk.CTkFrame(header, fg_color="transparent")
    inner.pack(fill="x", padx=MODAL_STYLE["padding"], pady=18)

    ctk.CTkLabel(
        inner,
        text=title,
        font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        text_color=MODAL_STYLE["text_on_primary"],
        anchor="w",
    ).pack(fill="x")

    subtitle_label = None
    if subtitle:
        subtitle_label = ctk.CTkLabel(
            inner,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MODAL_STYLE["text_on_primary_muted"],
            anchor="w",
        )
        subtitle_label.pack(fill="x", pady=(4, 0))

    return header, subtitle_label


def create_section_header(parent, text):
    ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        text_color=MODAL_STYLE["primary"],
        anchor="w",
    ).pack(fill="x", pady=(18, 8))


def create_form_row(parent, label_text, widget=None, widget_factory=None):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=10)

    ctk.CTkLabel(
        frame,
        text=label_text,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        text_color=MODAL_STYLE["text_secondary"],
        width=MODAL_STYLE["label_width"],
        anchor="w",
    ).pack(side="left", padx=(0, 12))

    if widget_factory is not None:
        widget = widget_factory(frame)
    widget.pack(side="left")
    return widget


def create_form_entry(parent, label, value="", readonly=False):
    def build(frame):
        entry = ctk.CTkEntry(
            frame,
            width=MODAL_STYLE["input_width"],
            height=MODAL_STYLE["input_height"],
            **input_style(),
        )
        if value:
            entry.insert(0, value)
        if readonly:
            entry.configure(state="readonly", fg_color=MODAL_STYLE["bg_card"])
        return entry

    return create_form_row(parent, label, widget_factory=build)


def create_form_textbox(parent, label, value="", height=88):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=10)
    ctk.CTkLabel(
        frame,
        text=label,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        text_color=MODAL_STYLE["text_secondary"],
        width=MODAL_STYLE["label_width"],
        anchor="nw",
    ).pack(side="left", padx=(0, 12), anchor="n", pady=4)

    textbox = ctk.CTkTextbox(
        frame,
        width=MODAL_STYLE["input_width"],
        height=height,
        **input_style(),
    )
    textbox.pack(side="left")
    if value:
        textbox.insert("1.0", value)
    return textbox


def create_form_combobox(parent, label, values, variable, width=None):
    def build(frame):
        return ctk.CTkComboBox(
            frame,
            variable=variable,
            values=values,
            width=width or MODAL_STYLE["input_width"],
            height=MODAL_STYLE["input_height"],
            **input_style(),
        )

    return create_form_row(parent, label, widget_factory=build)


def _messagebox_parent(widget):
    """Use the owning window for dialogs, not a modal that may be destroyed."""
    current = widget
    if isinstance(current, (tk.Toplevel, ctk.CTkToplevel)):
        current = current.master
    while current is not None:
        try:
            if current.winfo_exists():
                return current
        except Exception:
            pass
        current = getattr(current, "master", None)
    return None


def close_modal_window(window, on_after=None, success_message=None):
    """Release modal grab, destroy the window, then run optional follow-up work."""
    message_parent = _messagebox_parent(window)
    callback = on_after
    try:
        window.grab_release()
    except Exception:
        pass
    window.destroy()
    if callback:
        callback()
    if success_message:
        if message_parent:
            messagebox.showinfo("Saved", success_message, parent=message_parent)
        else:
            messagebox.showinfo("Saved", success_message)


def _release_grab(window):
    try:
        window.grab_release()
    except Exception:
        pass


def _restore_grab(window):
    try:
        if window.winfo_exists():
            window.grab_set()
            window.focus_force()
    except Exception:
        pass


def setup_modal_window(window, on_close=None):
    """Configure a toplevel as a modal that survives native dialogs."""
    window.grab_set()
    window.focus_force()
    window.protocol("WM_DELETE_WINDOW", on_close or (lambda: close_modal_window(window)))


def ask_save_filename(parent, **kwargs):
    dialog_parent = _messagebox_parent(parent) or parent
    _release_grab(parent)
    filename = filedialog.asksaveasfilename(parent=dialog_parent, **kwargs)
    _restore_grab(parent)
    return filename


def show_info(parent, title, message):
    dialog_parent = _messagebox_parent(parent) or parent
    _release_grab(parent)
    messagebox.showinfo(title, message, parent=dialog_parent)
    _restore_grab(parent)


def show_error(parent, title, message):
    dialog_parent = _messagebox_parent(parent) or parent
    _release_grab(parent)
    try:
        messagebox.showerror(title, message, parent=dialog_parent)
    except Exception:
        messagebox.showerror(title, message)
    _restore_grab(parent)


def show_warning(parent, title, message):
    dialog_parent = _messagebox_parent(parent) or parent
    _release_grab(parent)
    messagebox.showwarning(title, message, parent=dialog_parent)
    _restore_grab(parent)


def create_modal_footer(parent, save_text, save_command, cancel_command):
    footer = ctk.CTkFrame(parent, fg_color="transparent")
    footer.pack(fill="x", padx=MODAL_STYLE["padding"], pady=(8, MODAL_STYLE["padding"]))

    ctk.CTkButton(
        footer,
        text=save_text,
        command=save_command,
        width=160,
        height=44,
        corner_radius=MODAL_STYLE["radius"],
        fg_color=MODAL_STYLE["success"],
        hover_color=MODAL_STYLE["success_hover"],
        text_color=MODAL_STYLE["text_on_primary"],
        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
    ).pack(side="right")

    ctk.CTkButton(
        footer,
        text="Cancel",
        command=cancel_command,
        width=120,
        height=44,
        corner_radius=MODAL_STYLE["radius"],
        fg_color="transparent",
        border_width=1,
        border_color=MODAL_STYLE["border"],
        text_color=MODAL_STYLE["text_secondary"],
        hover_color=MODAL_STYLE["bg_card"],
        font=ctk.CTkFont(family="Segoe UI", size=14),
    ).pack(side="right", padx=(0, 10))

    return footer


def _find_scrollable_frame(widget):
    """Walk widget hierarchy to find the CTkScrollableFrame under the pointer."""
    current = widget
    while current is not None:
        if isinstance(current, ctk.CTkScrollableFrame):
            return current
        current = getattr(current, "master", None)
    return None


def _scroll_canvas(frame, direction, shift_pressed=False):
    canvas = frame._parent_canvas
    scroll_amount = direction * 3

    if shift_pressed and frame._orientation == "vertical":
        if canvas.xview() != (0.0, 1.0):
            canvas.xview("scroll", scroll_amount, "units")
    elif frame._orientation == "horizontal":
        if canvas.xview() != (0.0, 1.0):
            canvas.xview("scroll", scroll_amount, "units")
    elif canvas.yview() != (0.0, 1.0):
        canvas.yview("scroll", scroll_amount, "units")


def _on_linux_mouse_scroll(event):
    frame = _find_scrollable_frame(event.widget)
    if frame is None and event.widget is not None:
        try:
            frame = _find_scrollable_frame(
                event.widget.winfo_containing(event.x_root, event.y_root)
            )
        except Exception:
            pass
    if frame is None:
        return

    if event.num == 4:
        direction = -1
    elif event.num == 5:
        direction = 1
    else:
        return

    shift_pressed = getattr(frame, "_shift_pressed", False)
    _scroll_canvas(frame, direction, shift_pressed)


def enable_mousewheel_scrolling(root):
    """Enable scroll wheel and trackpad scrolling for CTkScrollableFrame on Linux."""
    if not sys.platform.startswith("linux"):
        return
    root.bind_all("<Button-4>", _on_linux_mouse_scroll, add="+")
    root.bind_all("<Button-5>", _on_linux_mouse_scroll, add="+")


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
        'report_cards': 'Report Cards',
        'fees': 'School Fees Management'
    }
    
    # Navigation items
    NAVIGATION = {
        'students': 'Students',
        'fees': 'Fees',
        'register': 'Register',
        'marks': 'Grades',
        'broadsheet': 'Broadsheet',
        'attendance': 'Attendance',
        'report_cards': 'Report Cards'
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

        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            messagebox.showerror("Error", "Student not found")
            return

        self.overlay = ctk.CTkToplevel(self.parent_window)
        self.overlay.title("Student Details")
        self.overlay.transient(self.parent_window)
        self.overlay.configure(fg_color=MODAL_STYLE["bg_main"])
        center_toplevel(self.overlay, self.parent_window, 480, 460)
        self.overlay.update_idletasks()
        self.overlay.grab_set()

        create_modal_header(
            self.overlay,
            "Student Details",
            subtitle=f"{student.full_name}  |  {student.student_id}  |  {student.class_name}",
        )

        menu_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=MODAL_STYLE["padding"], pady=MODAL_STYLE["padding"])

        def open_bio_data():
            self.close_current_modal()
            StudentBioDataWindow(self.parent_window, student_id, session)

        def open_attendance():
            self.close_current_modal()
            StudentAttendanceWindow(self.parent_window, student_id, session)

        def open_results():
            self.close_current_modal()
            StudentResultsWindow(self.parent_window, student_id, session)

        action_buttons = [
            ("View and Export Bio Data", open_bio_data, MODAL_STYLE["primary"], MODAL_STYLE["primary_hover"]),
            ("View Attendance Records", open_attendance, MODAL_STYLE["success"], MODAL_STYLE["success_hover"]),
            ("View Academic Results", open_results, MODAL_STYLE["secondary"], MODAL_STYLE["secondary_hover"]),
        ]

        for text, command, fg, hover in action_buttons:
            ctk.CTkButton(
                menu_frame,
                text=text,
                command=command,
                width=360,
                height=48,
                corner_radius=MODAL_STYLE["radius"],
                fg_color=fg,
                hover_color=hover,
                text_color=MODAL_STYLE["text_on_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            ).pack(pady=8)

        ctk.CTkButton(
            menu_frame,
            text="Close",
            command=self.close_current_modal,
            width=120,
            height=40,
            corner_radius=MODAL_STYLE["radius"],
            fg_color="transparent",
            border_width=1,
            border_color=MODAL_STYLE["border"],
            text_color=MODAL_STYLE["text_secondary"],
            hover_color=MODAL_STYLE["bg_card"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        ).pack(pady=(16, 0))

        self.overlay.protocol("WM_DELETE_WINDOW", self.close_current_modal)
        self.overlay.bind("<Escape>", lambda _e: self.close_current_modal())
        self.overlay.focus_set()
    
    def close_current_modal(self):
        """Close the current modal window."""
        if self.current_modal:
            self.current_modal = None
        if self.overlay:
            self.overlay.grab_release()
            self.overlay.destroy()
            self.overlay = None
