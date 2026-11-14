from string import Template

# ── Design tokens ────────────────────────────────────────────────────────────
DARK = dict(
    bg="#0F1115", sidebar="#13151A", surface="#1A1D24", raised="#232731",
    border="#2A2F3A", input="#12141A", text="#E8EAF0", muted="#8A91A3",
    accent="#6366F1", accent_hover="#7578F5", accent_press="#5558E3",
    accent_soft="rgba(99, 102, 241, 0.18)", accent_text="#A5A8FF",
    danger="#E5484D", danger_hover="#EE6064", scroll="#343A48",
    selection="rgba(99, 102, 241, 0.22)",
)

LIGHT = dict(
    bg="#F5F6F8", sidebar="#ECEEF3", surface="#FFFFFF", raised="#EEF0F5",
    border="#E1E4EB", input="#FFFFFF", text="#1B1E27", muted="#6B7280",
    accent="#5457E8", accent_hover="#6568EE", accent_press="#4548D0",
    accent_soft="rgba(84, 87, 232, 0.12)", accent_text="#4346D6",
    danger="#D92D3A", danger_hover="#E4474F", scroll="#C9CEDA",
    selection="rgba(84, 87, 232, 0.14)",
)

_TEMPLATE = Template("""
QWidget {
    color: $text;
    font-family: "Segoe UI Variable Text", "Segoe UI";
    font-size: 10pt;
}
QMainWindow { background: $bg; }
QMessageBox, QDialog { background: $surface; }
QToolTip { background: $raised; color: $text; border: 1px solid $border; padding: 6px; }

/* ── Sidebar ─────────────────────────────────────────────── */
QFrame#Sidebar { background: $sidebar; border: none; border-right: 1px solid $border; }
QLabel#Logo {
    background: $accent; color: white; border-radius: 10px;
    font-size: 16pt; font-weight: 700;
}
QLabel#Brand { font-size: 13pt; font-weight: 700; }
QLabel#Muted, QLabel#FieldLabel { color: $muted; }
QLabel#FieldLabel { font-size: 9pt; font-weight: 600; }
QLabel#PageTitle { font-size: 22pt; font-weight: 700; }
QLabel#PanelTitle { font-size: 11pt; font-weight: 600; }
QLabel#Percent { font-size: 18pt; font-weight: 700; }
QLabel#Chip {
    background: $accent_soft; color: $accent_text;
    border-radius: 11px; padding: 3px 12px; font-weight: 600;
}

QPushButton#Nav {
    background: transparent; border: none; border-radius: 10px;
    text-align: left; padding: 11px 14px; color: $muted; font-weight: 600;
}
QPushButton#Nav:hover { background: $raised; color: $text; }
QPushButton#Nav[active="true"] { background: $accent_soft; color: $accent_text; }

/* ── Cards ───────────────────────────────────────────────── */
QFrame#Panel { background: $surface; border: 1px solid $border; border-radius: 14px; }

/* ── Inputs ──────────────────────────────────────────────── */
QLineEdit, QComboBox, QSpinBox {
    background: $input; border: 1px solid $border; border-radius: 9px;
    padding: 10px 12px; selection-background-color: $accent;
}
QLineEdit:hover, QComboBox:hover { border-color: $muted; }
QLineEdit:focus, QComboBox:focus { border: 1px solid $accent; }
QComboBox QAbstractItemView {
    background: $surface; border: 1px solid $border; padding: 4px;
    selection-background-color: $accent; selection-color: white; outline: none;
}

/* ── Buttons ─────────────────────────────────────────────── */
QPushButton {
    background: $raised; border: 1px solid $border; border-radius: 9px;
    padding: 10px 16px; font-weight: 600;
}
QPushButton:hover { border-color: $muted; }
QPushButton:pressed { background: $border; }
QPushButton:disabled { color: $muted; background: $raised; border-color: $border; }

QPushButton#Primary {
    background: $accent; color: white; border: none;
    padding: 13px 18px; font-size: 11pt;
}
QPushButton#Primary:hover { background: $accent_hover; }
QPushButton#Primary:pressed { background: $accent_press; }
QPushButton#Primary:disabled { background: $raised; color: $muted; }

QPushButton#Danger { background: transparent; color: $danger; border: 1px solid $danger; }
QPushButton#Danger:hover { background: $danger; color: white; }
QPushButton#Danger:disabled { color: $muted; border-color: $border; background: transparent; }

QPushButton#SegLeft, QPushButton#SegRight {
    background: $input; color: $muted; border: 1px solid $border; padding: 10px 20px;
}
QPushButton#SegLeft  { border-top-right-radius: 0; border-bottom-right-radius: 0; }
QPushButton#SegRight { border-top-left-radius: 0; border-bottom-left-radius: 0; border-left: none; }
QPushButton#SegLeft:checked, QPushButton#SegRight:checked {
    background: $accent_soft; color: $accent_text; border: 1px solid $accent;
}

/* ── Data views ──────────────────────────────────────────── */
QTextEdit, QTableWidget {
    background: $input; border: 1px solid $border; border-radius: 10px;
}
QTextEdit { padding: 8px; font-family: "Cascadia Mono", "Consolas"; font-size: 9pt; }
QTableWidget { gridline-color: transparent; outline: none; }
QTableWidget::item { padding: 6px 10px; border-bottom: 1px solid $border; }
QTableWidget::item:selected { background: $selection; color: $text; }
QHeaderView { background: transparent; }
QHeaderView::section {
    background: $input; color: $muted; padding: 10px; border: none;
    border-bottom: 1px solid $border; font-weight: 600;
}
QTableCornerButton::section { background: $input; border: none; }

/* ── Progress ────────────────────────────────────────────── */
QProgressBar { background: $input; border: none; border-radius: 5px; min-height: 10px; max-height: 10px; }
QProgressBar::chunk { background: $accent; border-radius: 5px; }

/* ── Checkbox ────────────────────────────────────────────── */
QCheckBox { spacing: 10px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 5px; border: 1px solid $border; background: $input; }
QCheckBox::indicator:hover { border-color: $accent; }
QCheckBox::indicator:checked { background: $accent; border-color: $accent; }

/* ── Scrollbars ──────────────────────────────────────────── */
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $scroll; border-radius: 4px; min-height: 30px; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: $scroll; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QStatusBar { background: $sidebar; color: $muted; border-top: 1px solid $border; }
QStatusBar::item { border: none; }
""")

DARK_STYLESHEET = _TEMPLATE.substitute(DARK)
LIGHT_STYLESHEET = _TEMPLATE.substitute(LIGHT)
# DARK_STYLESHEET = """
# QWidget { background: #111827; color: #e5e7eb; font-family: "Segoe UI"; font-size: 10pt; }
# QMainWindow { background: #0b1120; }
# QFrame#Sidebar { background: #0f172a; border-right: 1px solid #253047; }
# QLabel#Brand { font-size: 18pt; font-weight: 700; color: #f8fafc; }
# QLabel#PageTitle { font-size: 22pt; font-weight: 700; color: #f8fafc; }
# QLabel#Muted { color: #94a3b8; }
# QFrame#Panel { background: #172033; border: 1px solid #29364d; border-radius: 14px; }
# QLineEdit, QComboBox { background: #0f172a; border: 1px solid #34445f; border-radius: 8px; padding: 11px; color: #f8fafc; }
# QPushButton { background: #25334b; border: 1px solid #3a4b68; border-radius: 8px; padding: 10px 14px; color: #f8fafc; }
# QPushButton:hover { background: #31435f; }
# QPushButton#Primary { background: #2563eb; border: none; font-weight: 700; }
# QPushButton#Primary:hover { background: #1d4ed8; }
# QPushButton#Danger { background: #7f1d1d; border: none; }
# QListWidget, QTableWidget, QTextEdit { background: #0f172a; border: 1px solid #29364d; border-radius: 8px; }
# QHeaderView::section { background: #1e293b; color: #cbd5e1; padding: 8px; border: none; }
# QProgressBar { background: #0f172a; border: none; border-radius: 6px; height: 12px; text-align: center; }
# QProgressBar::chunk { background: #3b82f6; border-radius: 6px; }
# QCheckBox { spacing: 8px; }
# QComboBox QAbstractItemView { background: #172033; selection-background-color: #2563eb; }
# """
# LIGHT_STYLESHEET = """
# QWidget { background: #f3f6fb; color: #172033; font-family: "Segoe UI"; font-size: 10pt; }
# QMainWindow { background: #f3f6fb; }
# QFrame#Sidebar { background: #e7edf6; border-right: 1px solid #d3dce9; }
# QLabel#Brand, QLabel#PageTitle { color: #14213a; font-weight: 700; }
# QLabel#Brand { font-size: 18pt; } QLabel#PageTitle { font-size: 22pt; }
# QLabel#Muted { color: #64748b; }
# QFrame#Panel { background: white; border: 1px solid #dce4ef; border-radius: 14px; }
# QLineEdit, QComboBox { background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 11px; }
# QPushButton { background: #e5ebf4; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px 14px; }
# QPushButton#Primary { background: #2563eb; color: white; border: none; font-weight: 700; }
# QPushButton#Danger { background: #b91c1c; color: white; border: none; }
# QListWidget, QTableWidget, QTextEdit { background: white; border: 1px solid #dce4ef; border-radius: 8px; }
# QHeaderView::section { background: #e7edf6; padding: 8px; border: none; }
# QProgressBar { background: #e5eaf2; border: none; border-radius: 6px; height: 12px; }
# QProgressBar::chunk { background: #2563eb; border-radius: 6px; }
# """
