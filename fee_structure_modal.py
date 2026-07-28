import customtkinter as ctk
import json
from ui_components import center_toplevel, MODAL_STYLE, create_modal_header, create_modal_footer, setup_modal_window, show_error, close_modal_window, input_style
from constants import COLORS, TERM_OPTIONS, CLASS_OPTIONS
from fee_helpers import get_fee_structure, apply_fee_structure

class FeeStructureModal(ctk.CTkToplevel):
    def __init__(self, parent, session, on_saved=None, focus_class="SSS1", focus_term=1):
        super().__init__(parent)
        self.session = session
        self.on_saved = on_saved
        self.focus_class = focus_class or "SSS1"
        self.focus_term = focus_term or 1
        
        self.title("Fee Structure Items")
        self.transient(parent)
        self.configure(fg_color=MODAL_STYLE["bg_main"])
        center_toplevel(self, parent, 600, 600)
        
        create_modal_header(
            self,
            f"Fee Structure: {self.focus_class} (Term {self.focus_term})",
            subtitle="Add fee items below. Amount must be a valid number.",
        )
        
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=MODAL_STYLE["padding"], pady=(0, 8))
        
        self.items_frame = ctk.CTkScrollableFrame(body, fg_color="transparent", height=300)
        self.items_frame.pack(fill="both", expand=True)
        
        # Load existing structure
        structure = get_fee_structure(session, self.focus_class, self.focus_term)
        self.item_rows = []
        
        existing_items = []
        if structure and structure.fee_items:
            try:
                existing_items = json.loads(structure.fee_items)
            except:
                pass
                
        if not existing_items:
            existing_items = [{"description": "", "amount": ""}]
            
        for item in existing_items:
            self.add_item_row(item.get("description", ""), item.get("amount", ""))
            
        ctk.CTkButton(
            body, text="+ Add Fee Item", command=lambda: self.add_item_row("", ""),
            fg_color=COLORS["secondary"], hover_color=COLORS["primary"], text_color="white",
            width=150, height=36
        ).pack(anchor="w", pady=(10, 0))
        
        self.total_label = ctk.CTkLabel(body, text="Total: ₦0.00", font=ctk.CTkFont(size=18, weight="bold"))
        self.total_label.pack(anchor="e", pady=(10, 0))
        
        create_modal_footer(self, save_text="Save Structure", save_command=self.save, cancel_command=self._close)
        setup_modal_window(self, on_close=self._close)
        self.calculate_total()
        
    def add_item_row(self, desc="", amt=""):
        row_frame = ctk.CTkFrame(self.items_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        
        desc_entry = ctk.CTkEntry(row_frame, placeholder_text="Item Description (e.g. Tuition)", width=250, **input_style())
        desc_entry.pack(side="left", padx=(0, 10))
        if desc: desc_entry.insert(0, desc)
        
        amt_entry = ctk.CTkEntry(row_frame, placeholder_text="Amount", width=150, **input_style())
        amt_entry.pack(side="left", padx=(0, 10))
        if amt: amt_entry.insert(0, str(amt))
        
        amt_entry.bind("<KeyRelease>", lambda e: self.calculate_total())
        
        del_btn = ctk.CTkButton(row_frame, text="X", width=36, fg_color=COLORS["danger"], hover_color="#c5221f", command=lambda: self.remove_item_row(row_frame))
        del_btn.pack(side="left")
        
        self.item_rows.append((row_frame, desc_entry, amt_entry))
        
    def remove_item_row(self, row_frame):
        for row in self.item_rows:
            if row[0] == row_frame:
                row_frame.destroy()
                self.item_rows.remove(row)
                break
        self.calculate_total()
        
    def calculate_total(self):
        total = 0.0
        for _, _, amt_entry in self.item_rows:
            try:
                val = amt_entry.get().strip()
                if val: total += float(val)
            except ValueError:
                pass
        self.total_label.configure(text=f"Total: ₦{total:,.2f}")
        return total

    def _close(self):
        close_modal_window(self)

    def save(self):
        items = []
        total = 0.0
        for _, desc_entry, amt_entry in self.item_rows:
            desc = desc_entry.get().strip()
            amt_str = amt_entry.get().strip()
            if not desc and not amt_str:
                continue
                
            if not desc:
                show_error(self, "Validation Error", "Description cannot be empty.")
                return
            if not amt_str:
                show_error(self, "Validation Error", f"Amount for '{desc}' cannot be empty.")
                return
                
            try:
                amt = float(amt_str)
                if amt < 0: raise ValueError
            except ValueError:
                show_error(self, "Validation Error", f"Amount for '{desc}' must be a positive number.")
                return
                
            items.append({"description": desc, "amount": amt})
            total += amt
            
        try:
            apply_fee_structure(self.session, self.focus_class, self.focus_term, total, json.dumps(items))
            close_modal_window(self, on_after=self.on_saved, success_message="Fee structure saved.")
        except Exception as exc:
            self.session.rollback()
            show_error(self, "Error", f"Failed to save: {exc}")
