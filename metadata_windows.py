import customtkinter as ctk
from tkinter import messagebox
from ui_components import center_toplevel, setup_modal_window, close_modal_window, create_modal_header, MODAL_STYLE, input_style
from models import Religion

class ManageReligionsModal(ctk.CTkToplevel):
    def __init__(self, parent, session, on_updated_callback=None):
        super().__init__(parent)
        self.session = session
        self.on_updated_callback = on_updated_callback

        self.title("Manage Religions")
        self.transient(parent)
        self.configure(fg_color=MODAL_STYLE["bg_main"])
        
        center_toplevel(self, parent, 500, 600)
        self.update_idletasks()
        setup_modal_window(self, on_close=lambda: close_modal_window(self))

        create_modal_header(self, "Manage Religions", "Add or remove religions for student registration")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=MODAL_STYLE["padding"], pady=MODAL_STYLE["padding"])

        # Add new religion form
        add_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        add_frame.pack(fill="x", pady=(0, 20))

        self.new_religion_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            add_frame,
            textvariable=self.new_religion_var,
            placeholder_text="e.g. Christianity",
            width=280,
            height=MODAL_STYLE["input_height"],
            **input_style()
        )
        entry.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            add_frame,
            text="Add",
            command=self.add_religion,
            width=80,
            height=MODAL_STYLE["input_height"],
            fg_color="#1a73e8",
            hover_color="#1557b0",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        add_btn.pack(side="left")

        # List frame
        ctk.CTkLabel(
            self.body,
            text="Existing Religions",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=MODAL_STYLE["text_primary"]
        ).pack(anchor="w", pady=(0, 10))

        self.list_frame = ctk.CTkScrollableFrame(
            self.body,
            fg_color=MODAL_STYLE["bg_card"],
            corner_radius=8,
            scrollbar_button_color="#1a73e8",
            scrollbar_button_hover_color="#1557b0"
        )
        self.list_frame.pack(fill="both", expand=True)

        self.load_religions()

    def load_religions(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        religions = self.session.query(Religion).order_by(Religion.name).all()
        
        if not religions:
            ctk.CTkLabel(
                self.list_frame,
                text="No religions added yet.",
                text_color=MODAL_STYLE["text_secondary"]
            ).pack(pady=20)
            return

        for r in religions:
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=8)

            ctk.CTkLabel(
                row,
                text=r.name,
                font=ctk.CTkFont(size=13),
                text_color=MODAL_STYLE["text_primary"]
            ).pack(side="left")

            ctk.CTkButton(
                row,
                text="Delete",
                command=lambda rid=r.id, name=r.name: self.delete_religion(rid, name),
                width=60,
                height=24,
                fg_color="#ea4335",
                hover_color="#c9302c",
                font=ctk.CTkFont(size=11)
            ).pack(side="right")

    def add_religion(self):
        name = self.new_religion_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Religion name cannot be empty", parent=self)
            return

        existing = self.session.query(Religion).filter(Religion.name.ilike(name)).first()
        if existing:
            messagebox.showwarning("Warning", "This religion already exists", parent=self)
            return

        try:
            r = Religion(name=name)
            self.session.add(r)
            self.session.commit()
            self.new_religion_var.set("")
            self.load_religions()
            if self.on_updated_callback:
                self.on_updated_callback()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", str(e), parent=self)

    def delete_religion(self, rid, name):
        if messagebox.askyesno("Confirm", f"Delete '{name}'?", parent=self):
            try:
                r = self.session.query(Religion).get(rid)
                if r:
                    self.session.delete(r)
                    self.session.commit()
                    self.load_religions()
                    if self.on_updated_callback:
                        self.on_updated_callback()
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("Error", str(e), parent=self)
