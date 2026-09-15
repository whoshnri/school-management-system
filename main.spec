# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_dir = Path(SPECPATH)

datas = []
datas += collect_data_files("customtkinter")
datas += collect_data_files("tkcalendar")

# Add assets folder
assets_dir = project_dir / "assets"
if assets_dir.exists():
    datas.append((str(assets_dir), "assets"))

for asset in (
    "app_icon.png",
    "icon.jpg.jpeg",
    "myIcon.ico",
    "school_header.png",
):
    asset_path = project_dir / asset
    if asset_path.exists():
        datas.append((str(asset_path), "."))

hiddenimports = [
    "PIL._tkinter_finder",
    "tkcalendar",
    "babel.numbers",
    "sqlalchemy.sql.default_comparator",
    "reportlab.graphics.barcode.common",
    "reportlab.graphics.barcode.code128",
    "reportlab.graphics.barcode.code93",
    "reportlab.graphics.barcode.code39",
    "reportlab.graphics.barcode.usps",
    "reportlab.graphics.barcode.usps4s",
    "reportlab.graphics.barcode.ecc200datamatrix",
    "add_profile_pic",
    "app_paths",
    "calculations",
    "departments_tab",
    "enhanced_broadsheet",
    "enhanced_registration",
    "enterprise_forms",
    "fee_helpers",
    "fee_receipt_pdf",
    "fee_structure_modal",
    "forms",
    "metadata_windows",
    "models",
    "report_card_pdf",
    "report_cards_tab",
    "sessions_tab",
    "student_details_windows",
    "ui_components",
    "validators",
]
hiddenimports += collect_submodules("customtkinter")

a = Analysis(
    ["main.py"],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pandas", "numpy", "psycopg2"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GFA-Admin-Panel",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / "assets" / "school-logo.ico") if (project_dir / "assets" / "school-logo.ico").exists() else str(project_dir / "myIcon.ico"),
)
