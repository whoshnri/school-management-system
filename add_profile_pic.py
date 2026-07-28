import re
import os

with open('/home/rhedawn/Desktop/sms/enhanced_registration.py', 'r') as f:
    content = f.read()

# Add import
if 'from tkinter import filedialog' not in content:
    content = content.replace('import customtkinter as ctk', 'import customtkinter as ctk\nfrom tkinter import filedialog\nfrom PIL import Image')

# Add UI
ui_code = """
        # Profile Picture
        self._label(form_scroll, "Profile Picture", row)
        pic_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        pic_frame.grid(row=row, column=1, padx=25, pady=(10, 5), sticky="w")
        
        self.pic_preview = ctk.CTkLabel(pic_frame, text="No Image", width=80, height=80, fg_color=COLORS["border"], corner_radius=10)
        self.pic_preview.pack(side="left", padx=(0, 15))
        
        self.upload_btn = ctk.CTkButton(
            pic_frame, text="Upload Picture", command=self._upload_picture,
            width=140, height=45, corner_radius=10,
            fg_color=COLORS["secondary"], hover_color=COLORS["primary"],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.upload_btn.pack(side="left")
        self.profile_picture_source = None
        row += 1
"""

content = content.replace('        # Religion', ui_code + '\n        # Religion')

# Add _upload_picture method
upload_method = """
    def _upload_picture(self):
        filepath = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filepath:
            self.profile_picture_source = filepath
            try:
                img = Image.open(filepath)
                img = img.resize((80, 80))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                self.pic_preview.configure(image=photo, text="")
            except Exception as e:
                self.pic_preview.configure(image="", text="Error")
                self.profile_picture_source = None
"""

content = content.replace('    def _load_states_data(self):', upload_method + '\n    def _load_states_data(self):')

with open('/home/rhedawn/Desktop/sms/enhanced_registration.py', 'w') as f:
    f.write(content)
