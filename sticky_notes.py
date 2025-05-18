import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel, QSystemTrayIcon, QMenu, QAction,
    QPushButton, QHBoxLayout, QInputDialog, QSpinBox, QScrollArea, QFrame, QGridLayout, QMessageBox, QDialog, QCheckBox, QDialogButtonBox, QColorDialog, QToolButton, QSlider, QSizeGrip, QLayout, QLineEdit, QShortcut, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QPainter, QIntValidator, QLinearGradient, QKeySequence
import re
import weakref
import math

SAVE_INTERVAL = 1000  # 1 second, in milliseconds
# SAVE_FILE = os.path.expanduser("~/.sticky_notes_data.json")
SAVE_FILE = os.path.join(os.getenv("SNAP_USER_COMMON", os.path.expanduser("~")), "sticky_notes_data.json")

DEFAULT_FONT_SIZE = 15
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 24
MAX_NOTES = 100
NOTES_PER_COLUMN = 3

# Pastel color palettes
LIGHT_PASTELS = [
    (255, 255, 204),  # pastel yellow
    (204, 229, 255),  # pastel blue
    (204, 255, 229),  # pastel mint
    (255, 204, 229),  # pastel pink
    (229, 204, 255),  # pastel lavender
    (255, 229, 204),  # pastel peach
]
DARK_PASTELS = [
    (44, 62, 80),     # muted navy
    (64, 61, 86),     # muted purple
    (60, 76, 74),     # muted teal
    (80, 61, 61),     # muted maroon
    (70, 70, 60),     # muted olive
    (60, 70, 80),     # muted slate
]

# Helper for icon pixmaps
ICON_SIZE = 20

def get_icon_pixmap(icon_name, theme='light'):
    # Use built-in Qt icons or draw simple SVGs for palette/color
    if icon_name == 'add':
        return QApplication.style().standardIcon(QApplication.style().SP_FileDialogNewFolder).pixmap(ICON_SIZE, ICON_SIZE)
    elif icon_name == 'showhide':
        return QApplication.style().standardIcon(QApplication.style().SP_DialogYesButton).pixmap(ICON_SIZE, ICON_SIZE)
    elif icon_name == 'trash':
        return QApplication.style().standardIcon(QApplication.style().SP_TrashIcon).pixmap(ICON_SIZE, ICON_SIZE)
    elif icon_name == 'eye':
        # Draw a simple eye icon
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(Qt.black if theme == 'light' else Qt.white)
        p.drawEllipse(3, 7, 14, 6)
        p.drawEllipse(8, 9, 4, 4)
        p.end()
        return pix
    elif icon_name == 'eye-off':
        # Draw a simple eye-off icon
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(Qt.black if theme == 'light' else Qt.white)
        p.drawEllipse(3, 7, 14, 6)
        p.drawEllipse(8, 9, 4, 4)
        p.drawLine(4, 16, 16, 4)
        p.end()
        return pix
    elif icon_name == 'minimize':
        # Draw a simple minimize icon (horizontal line)
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(Qt.black if theme == 'light' else Qt.white)
        p.setBrush(Qt.black if theme == 'light' else Qt.white)
        p.drawRect(4, ICON_SIZE - 7, ICON_SIZE - 8, 3)
        p.end()
        return pix
    elif icon_name == 'palette':
        # Draw a color gradient square
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        if theme == 'light':
            grad = QLinearGradient(0, 0, ICON_SIZE, ICON_SIZE)
            grad.setColorAt(0, QColor(255, 255, 204))
            grad.setColorAt(1, QColor(204, 229, 255))
        else:
            grad = QLinearGradient(0, 0, ICON_SIZE, ICON_SIZE)
            grad.setColorAt(0, QColor(44, 62, 80))
            grad.setColorAt(1, QColor(64, 61, 86))
        p.setBrush(grad)
        p.setPen(Qt.gray)
        p.drawRect(2, 2, ICON_SIZE-4, ICON_SIZE-4)
        p.end()
        return pix
    elif icon_name == 'settings':
        # Draw a simple macOS-style gear
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        color = Qt.black if theme == 'light' else Qt.white
        p.setPen(color)
        p.setBrush(Qt.NoBrush)
        center = ICON_SIZE // 2
        radius = 7
        for i in range(8):
            angle = i * (360 / 8)
            x1 = center + int(radius * 0.9 * math.cos(math.radians(angle)))
            y1 = center + int(radius * 0.9 * math.sin(math.radians(angle)))
            x2 = center + int((radius+3) * math.cos(math.radians(angle)))
            y2 = center + int((radius+3) * math.sin(math.radians(angle)))
            p.drawLine(x1, y1, x2, y2)
        p.drawEllipse(center-6, center-6, 12, 12)
        p.drawEllipse(center-2, center-2, 4, 4)
        p.end()
        return pix
    elif icon_name == 'delete':
        # Draw an X in a circle
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        color = Qt.black if theme == 'light' else Qt.white
        p.setPen(color)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(2, 2, ICON_SIZE-4, ICON_SIZE-4)
        p.drawLine(5, 5, ICON_SIZE-5, ICON_SIZE-5)
        p.drawLine(ICON_SIZE-5, 5, 5, ICON_SIZE-5)
        p.end()
        return pix
    return QPixmap(ICON_SIZE, ICON_SIZE)

def get_pastel_palette(theme):
    return LIGHT_PASTELS if theme == 'light' else DARK_PASTELS

def get_contrast_font_color(bg_rgb):
    # Use black for light backgrounds, white for dark
    r, g, b = bg_rgb
    luminance = (0.299*r + 0.587*g + 0.114*b)
    return '#000' if luminance > 150 else '#fff'

def create_sticky_note_icon(theme='light'):
    # Create a sticky note icon
    pix = QPixmap(ICON_SIZE, ICON_SIZE)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    
    # Set up colors based on theme
    if theme == 'light':
        note_color = QColor(255, 255, 150)  # Light yellow
        border_color = QColor(200, 200, 100)
        line_color = QColor(180, 180, 80)
    else:
        note_color = QColor(80, 80, 40)  # Dark yellow
        border_color = QColor(100, 100, 50)
        line_color = QColor(120, 120, 60)
    
    # Draw the main note shape
    p.setPen(border_color)
    p.setBrush(note_color)
    p.drawRect(2, 2, 16, 16)
    
    # Draw lines to make it look like paper
    p.setPen(line_color)
    p.drawLine(4, 8, 16, 8)
    p.drawLine(4, 12, 16, 12)
    p.drawLine(4, 16, 16, 16)
    
    p.end()
    return pix

class ShowHideDialog(QDialog):
    def __init__(self, notes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Show/Hide Notes")
        self.notes = notes
        self.checkboxes = {}
        layout = QVBoxLayout(self)
        
        # Set theme-based text and background color
        theme = parent.theme if parent and hasattr(parent, 'theme') else 'dark'
        font_color = '#fff' if theme == 'dark' else '#000'
        bg_color = '#222' if theme == 'dark' else '#fff'
        btn_bg = '#333' if theme == 'dark' else '#eee'
        btn_fg = '#fff' if theme == 'dark' else '#000'
        
        # Set stylesheet for dialog and children
        self.setStyleSheet(f"""
            QDialog {{ 
                background: {bg_color}; 
                color: {font_color}; 
            }}
            QCheckBox {{ 
                color: {font_color}; 
                background: transparent; 
            }}
            QDialogButtonBox QPushButton, QPushButton {{ 
                color: {btn_fg}; 
                background: {btn_bg}; 
                border-radius: 6px; 
                border: 1px solid #888; 
            }}
        """)
        
        # Add checkboxes for each note
        for note in notes:
            cb = QCheckBox(note.title)
            cb.setChecked(note.is_visible)
            cb.stateChanged.connect(self.make_toggle_cb(note))
            layout.addWidget(cb)
            self.checkboxes[note] = cb
            
        # Add Show All and Hide All buttons
        btn_layout = QHBoxLayout()
        show_all_btn = QPushButton("Show All")
        show_all_btn.clicked.connect(self.show_all_notes)
        hide_all_btn = QPushButton("Hide All")
        hide_all_btn.clicked.connect(self.hide_all_notes)
        btn_layout.addWidget(show_all_btn)
        btn_layout.addWidget(hide_all_btn)
        layout.addLayout(btn_layout)
        
        # Add OK button
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.accepted.connect(self.accept)
        layout.addWidget(btn_box)

        # Center the dialog on screen
        self.center_on_screen()

    def center_on_screen(self):
        # Get the screen geometry
        screen = QApplication.primaryScreen().geometry()
        # Get the dialog geometry
        dialog_geometry = self.geometry()
        # Calculate the center position
        x = (screen.width() - dialog_geometry.width()) // 2
        y = (screen.height() - dialog_geometry.height()) // 2
        # Move the dialog to the center
        self.move(x, y)

    def make_toggle_cb(self, note):
        def toggle(state):
            note.set_visible(bool(state))
        return toggle

    def show_all_notes(self):
        for note in self.notes:
            note.set_visible(True)
            if note in self.checkboxes:
                self.checkboxes[note].setChecked(True)

    def hide_all_notes(self):
        for note in self.notes:
            note.set_visible(False)
            if note in self.checkboxes:
                self.checkboxes[note].setChecked(False)

    def set_checkbox(self, note, checked):
        if note in self.checkboxes:
            self.checkboxes[note].setChecked(checked)

class ReadmeDialog(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Sticky Notes Simple")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Create text browser for content
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        
        # Content
        content_text = """<h1>Sticky Notes Simple</h1>

A modern, feature-rich sticky notes application built with PyQt5.

<h2>Features</h2>

<ul>
<li>Create, edit, and delete sticky notes</li>
<li>Customizable colors and themes</li>
<li>Stay on top of other windows</li>
<li>System tray integration</li>
<li>Multiple workspace support</li>
</ul>

<h2>Keyboard Shortcuts</h2>

<ul>
<li><b>Ctrl + N</b>: Create new note</li>
<li><b>Ctrl + H</b>: Hide current note</li>
<li><b>Ctrl + S</b>: Show/Hide notes dialog</li>
<li><b>Ctrl + I</b>: Show this information</li>
</ul>

<h2>Usage</h2>

<ol>
<li><b>Creating Notes</b>: Click the tray icon and select "New Note" or use Ctrl + N</li>
<li><b>Editing</b>: Click any note to edit its content</li>
<li><b>Colors</b>: Click the palette icon to change note color</li>
<li><b>Workspaces</b>: Use "Bring Notes to This Workspace" to move notes between workspaces</li>
</ol>

<h2>About the Developer</h2>

<b>Name:</b> Achyutha Krishna Koneti<br>
<b>Email:</b> <a href="mailto:achyuth6654@gmail.com">achyuth6654@gmail.com</a><br>
<b>GitHub:</b> <a href="https://github.com/noob-akk">@noob-akk</a>

<h2>License</h2>

This project is open source and available under the MIT License.
"""
        
        text_browser.setHtml(content_text)
        
        content_layout.addWidget(text_browser)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Add close button
        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        # Apply theme-based styling
        font_color = '#fff' if theme == 'dark' else '#000'
        bg_color = '#222' if theme == 'dark' else '#fff'
        btn_bg = '#333' if theme == 'dark' else '#eee'
        btn_fg = '#fff' if theme == 'dark' else '#000'
        
        self.setStyleSheet(f"""
            QDialog {{ 
                background: {bg_color}; 
                color: {font_color}; 
            }}
            QTextBrowser {{ 
                background: {bg_color}; 
                color: {font_color}; 
                border: none;
            }}
            QScrollArea {{ 
                background: {bg_color}; 
                border: none;
            }}
            QDialogButtonBox QPushButton {{ 
                color: {btn_fg}; 
                background: {btn_bg}; 
                border-radius: 6px; 
                border: 1px solid #888; 
                padding: 5px 15px;
            }}
        """)
        
        # Set dialog size and center it
        self.resize(600, 500)
        self.center_on_screen()

    def center_on_screen(self):
        # Get the screen geometry
        screen = QApplication.primaryScreen().geometry()
        # Get the dialog geometry
        dialog_geometry = self.geometry()
        # Calculate the center position
        x = (screen.width() - dialog_geometry.width()) // 2
        y = (screen.height() - dialog_geometry.height()) // 2
        # Move the dialog to the center
        self.move(x, y)

class NoteWidget(QMainWindow):
    def __init__(self, title, parent=None, on_delete=None, color_index=0, theme='light', on_color_change=None, main_window=None):
        super().__init__(parent)
        self.title = title
        self._on_delete = None
        self.is_visible = True
        self.color_index = color_index
        self.theme = theme
        self.on_color_change = on_color_change
        self.main_window = main_window
        self.original_size = None
        self.default_size = QSize(400, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()
        self.apply_color()
        self.resize(self.default_size)
        self._drag_pos = None
        self.set_on_delete(on_delete)
        
        # Add keyboard shortcuts
        self.setup_shortcuts()

    def set_on_delete(self, callback):
        self._on_delete = callback
        if hasattr(self, 'delete_button'):
            try:
                self.delete_button.clicked.disconnect()
            except Exception:
                pass
            if callback:
                self.delete_button.setEnabled(True)
                self.delete_button.clicked.connect(callback)
            else:
                self.delete_button.setEnabled(False)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header layout with two sections
        header_layout = QHBoxLayout()
        header_layout.setSpacing(4)
        
        # Left section for editable title
        self.title_edit = QLineEdit(self.title)
        self.title_edit.setStyleSheet("font-weight: bold;")
        self.title_edit.setFrame(False)
        self.title_edit.setMaximumWidth(160)
        self.title_edit.editingFinished.connect(self.handle_title_change)
        header_layout.addWidget(self.title_edit)
        
        # Center section for font size controls
        font_section = QHBoxLayout()
        font_section.setSpacing(2)
        font_section.setAlignment(Qt.AlignCenter)
        self.font_minus_btn = QToolButton()
        self.font_minus_btn.setText('-')
        self.font_minus_btn.setToolTip('Decrease font size')
        self.font_minus_btn.clicked.connect(self.decrease_font_size)
        font_section.addWidget(self.font_minus_btn)
        self.font_size_edit = QLineEdit(str(DEFAULT_FONT_SIZE))
        self.font_size_edit.setFixedWidth(32)
        self.font_size_edit.setAlignment(Qt.AlignCenter)
        self.font_size_edit.setValidator(QIntValidator(MIN_FONT_SIZE, MAX_FONT_SIZE))
        self.font_size_edit.editingFinished.connect(self.font_size_edit_changed)
        font_section.addWidget(self.font_size_edit)
        self.font_plus_btn = QToolButton()
        self.font_plus_btn.setText('+')
        self.font_plus_btn.setToolTip('Increase font size')
        self.font_plus_btn.clicked.connect(self.increase_font_size)
        font_section.addWidget(self.font_plus_btn)
        
        header_layout.addLayout(font_section)
        header_layout.addStretch()
        
        # Right section for control buttons
        right_section = QHBoxLayout()
        right_section.setSpacing(4)
        
        # Settings button
        self.settings_button = QToolButton()
        self.settings_button.setIcon(QIcon(get_icon_pixmap('settings', self.theme)))
        self.settings_button.setToolTip('Settings')
        self.settings_button.clicked.connect(self.show_settings_menu)
        right_section.addWidget(self.settings_button)
        
        # Hide button
        self.hide_button = QToolButton()
        self.hide_button.setIcon(QIcon(get_icon_pixmap('minimize', self.theme)))
        self.hide_button.setToolTip('Hide')
        self.hide_button.clicked.connect(self.hide_note)
        right_section.addWidget(self.hide_button)
        
        # Color palette button
        self.palette_button = QToolButton()
        self.palette_button.setIcon(QIcon(get_icon_pixmap('palette', self.theme)))
        self.palette_button.setToolTip('Change color')
        self.palette_button.clicked.connect(self.pick_color)
        right_section.addWidget(self.palette_button)
        
        # Delete button
        self.delete_button = QToolButton()
        self.delete_button.setIcon(QIcon(get_icon_pixmap('delete', self.theme)))
        self.delete_button.setToolTip('Delete')
        right_section.addWidget(self.delete_button)
        
        header_layout.addLayout(right_section)
        layout.addLayout(header_layout)
        
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        layout.addWidget(self.text_edit)
        
        # Create a container for the size grip
        grip_container = QWidget()
        grip_container.setFixedHeight(20)
        grip_layout = QHBoxLayout(grip_container)
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addStretch()
        
        # Add size grip
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        grip_layout.addWidget(self.size_grip)
        layout.addWidget(grip_container)

    def hide_note(self):
        self.hide()
        self.is_visible = False
        if self.main_window:
            if hasattr(self.main_window, 'note_hidden_from_button'):
                self.main_window.note_hidden_from_button(self)

    def set_visible(self, visible):
        self.is_visible = visible
        if visible:
            self.show()
        else:
            self.hide()

    def get_data(self):
        return {
            "title": self.title,
            "content": self.text_edit.toPlainText(),
            "font_size": int(self.font_size_edit.text()),
            "is_visible": self.is_visible,
            "color_index": self.color_index,
            "size": [self.width(), self.height()],
            "pos": [self.x(), self.y()]
        }

    def set_data(self, data):
        self.text_edit.setPlainText(data.get("content", ""))
        font_size = data.get("font_size", DEFAULT_FONT_SIZE)
        self.font_size_edit.setText(str(font_size))
        self.change_font_size(font_size)
        size = data.get("size")
        if size:
            self.resize(size[0], size[1])
        pos = data.get("pos")
        if pos:
            self.move(pos[0], pos[1])
        self.color_index = data.get("color_index", 0)
        self.apply_color()
        is_visible = data.get("is_visible", True)
        self.set_visible(is_visible)
        self.title = data.get("title", self.title)
        self.title_edit.setText(self.title)

    def apply_color(self):
        palette = get_pastel_palette(self.theme)
        bg_rgb = palette[self.color_index % len(palette)]
        font_color = get_contrast_font_color(bg_rgb)
        border_col = '#888' if self.theme == 'light' else '#444'
        btn_bg = '#eee' if self.theme == 'light' else '#222'
        btn_fg = '#000' if self.theme == 'light' else '#fff'
        self.centralWidget().setStyleSheet(f"""
            QWidget {{
                background-color: rgb{bg_rgb};
                border: none;
                border-radius: 14px;
            }}
            QLabel {{
                color: {font_color};
                background: transparent;
            }}
            QLineEdit {{
                color: {font_color};
                background: transparent;
                border: none;
                font-weight: bold;
            }}
            QTextEdit {{
                background-color: rgb{bg_rgb};
                color: {font_color};
                border: none;
                border-radius: 0px;
            }}
            QToolButton#font_minus_btn, QToolButton#font_plus_btn {{
                border: 1.5px solid {border_col};
                border-radius: 6px;
                background: {btn_bg};
                color: {btn_fg};
                min-width: 22px;
                min-height: 22px;
            }}
            QSpinBox {{
                border: none;
                background: transparent;
            }}
        """)
        self.font_minus_btn.setObjectName('font_minus_btn')
        self.font_plus_btn.setObjectName('font_plus_btn')

    def change_font_size(self, size):
        font = self.text_edit.font()
        font.setPointSize(size)
        self.text_edit.setFont(font)

    def pick_color(self):
        palette = get_pastel_palette(self.theme)
        # Show a simple palette dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Pick a color")
        l = QHBoxLayout(dlg)
        btns = []
        for i, rgb in enumerate(palette):
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(f"background-color: rgb{rgb}; border-radius: 16px; border: 2px solid #888;")
            btn.clicked.connect(lambda _, idx=i: dlg.done(idx+1))
            l.addWidget(btn)
            btns.append(btn)
        dlg.setLayout(l)
        res = dlg.exec_()
        if res > 0:
            self.color_index = res-1
            self.apply_color()
            if self.on_color_change:
                self.on_color_change(self.color_index)

    def handle_title_change(self):
        new_title = self.title_edit.text()
        if new_title != self.title:
            self.title = new_title
            if self.main_window:
                self.main_window.note_title_changed(self, new_title)

    def decrease_font_size(self):
        size = int(self.font_size_edit.text())
        if size > MIN_FONT_SIZE:
            size -= 1
            self.font_size_edit.setText(str(size))
            self.change_font_size(size)

    def increase_font_size(self):
        size = int(self.font_size_edit.text())
        if size < MAX_FONT_SIZE:
            size += 1
            self.font_size_edit.setText(str(size))
            self.change_font_size(size)

    def font_size_edit_changed(self):
        size = int(self.font_size_edit.text())
        self.change_font_size(size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()

    def show_settings_menu(self):
        menu = QMenu(self)
        
        # New Note action
        new_note_action = QAction("New Note", self)
        new_note_action.triggered.connect(lambda: self.main_window.prompt_new_note() if self.main_window else None)
        menu.addAction(new_note_action)
        
        # Show/Hide Notes action
        showhide_action = QAction("Show/Hide Notes", self)
        showhide_action.triggered.connect(lambda: self.main_window.open_showhide_dialog() if self.main_window else None)
        menu.addAction(showhide_action)
        
        # Show All Notes action
        show_all_action = QAction("Show All Notes", self)
        show_all_action.triggered.connect(lambda: self.main_window.show_all_notes() if self.main_window else None)
        menu.addAction(show_all_action)
        
        # Hide All Notes action
        hide_all_action = QAction("Hide All Notes", self)
        hide_all_action.triggered.connect(lambda: self.main_window.hide_all_notes() if self.main_window else None)
        menu.addAction(hide_all_action)
        
        # Theme toggle action
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(lambda: self.main_window.toggle_theme() if self.main_window else None)
        menu.addAction(theme_action)
        
        menu.addSeparator()
        
        # Add About action
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: self.main_window.show_readme() if self.main_window else None)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(lambda: self.main_window.quit_app() if self.main_window else None)
        menu.addAction(exit_action)
        
        # Apply theme-based styling
        font_color = '#fff' if self.theme == 'dark' else '#000'
        bg_color = '#222' if self.theme == 'dark' else '#fff'
        btn_bg = '#333' if self.theme == 'dark' else '#eee'
        btn_fg = '#fff' if self.theme == 'dark' else '#000'
        
        menu.setStyleSheet(f"""
            QMenu {{
                background: {bg_color};
                color: {font_color};
                border: 1px solid #888;
            }}
            QMenu::item {{
                padding: 5px 20px;
            }}
            QMenu::item:selected {{
                background: {btn_bg};
                color: {btn_fg};
            }}
        """)
        
        # Show menu at button position
        menu.exec_(self.settings_button.mapToGlobal(self.settings_button.rect().bottomLeft()))

    def setup_shortcuts(self):
        # New note shortcut
        new_note_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_note_shortcut.activated.connect(lambda: self.main_window.prompt_new_note() if self.main_window else None)
        
        # Hide note shortcut
        hide_note_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        hide_note_shortcut.activated.connect(self.hide_note)
        
        # Show/Hide dialog shortcut
        showhide_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        showhide_shortcut.activated.connect(lambda: self.main_window.open_showhide_dialog() if self.main_window else None)
        
        # Info/Readme shortcut
        info_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        info_shortcut.activated.connect(lambda: self.show_readme() if self.main_window else None)
    
    def show_readme(self):
        if self.main_window:
            self.main_window.show_readme()

class NewNoteDialog(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Note")
        self.setModal(True)
        layout = QVBoxLayout(self)
        label = QLabel("Enter note title:")
        layout.addWidget(label)
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        # Theming
        font_color = '#fff' if theme == 'dark' else '#000'
        bg_color = '#222' if theme == 'dark' else '#fff'
        btn_bg = '#333' if theme == 'dark' else '#eee'
        btn_fg = '#fff' if theme == 'dark' else '#000'
        self.setStyleSheet(f"""
            QDialog {{ background: {bg_color}; color: {font_color}; }}
            QLabel {{ color: {font_color}; }}
            QLineEdit {{ color: {font_color}; background: transparent; border: 1px solid #888; }}
            QDialogButtonBox QPushButton {{ color: {btn_fg}; background: {btn_bg}; border-radius: 6px; border: 1px solid #888; }}
        """)

    def get_title(self):
        return self.title_edit.text().strip()

class StickyNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme = 'dark'
        self.notes = []
        self.showhide_dialog = None
        self.setup_tray_icon_and_menu()
        self.tray_icon.show()
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_notes)
        self.save_timer.start(SAVE_INTERVAL)
        self.load_notes()
        self.update_tooltip_style()

    def setup_tray_icon_and_menu(self):
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon.deleteLater()
            self.tray_icon = None

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(create_sticky_note_icon(self.theme)))
        tray_menu = QMenu()
        new_note_action = QAction("New Note", self)
        new_note_action.triggered.connect(self.prompt_new_note)
        tray_menu.addAction(new_note_action)
        # Add static Show/Hide Notes action
        showhide_action = QAction("Show/Hide Notes", self)
        showhide_action.triggered.connect(self.open_showhide_dialog)
        tray_menu.addAction(showhide_action)
        show_all_action = QAction("Show All Notes", self)
        show_all_action.triggered.connect(self.show_all_notes)
        tray_menu.addAction(show_all_action)
        hide_all_action = QAction("Hide All Notes", self)
        hide_all_action.triggered.connect(self.hide_all_notes)
        tray_menu.addAction(hide_all_action)
        bring_notes_action = QAction("Bring Notes to This Workspace", self)
        bring_notes_action.triggered.connect(self.bring_notes_to_workspace)
        tray_menu.addAction(bring_notes_action)
        # Add theme and exit actions
        self.theme_action = QAction("Toggle Theme", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        tray_menu.addAction(self.theme_action)
        tray_menu.addSeparator()
        # Add About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_readme)
        tray_menu.addAction(about_action)
        tray_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def prompt_new_note(self):
        if len(self.notes) >= MAX_NOTES:
            QMessageBox.warning(self, "Maximum Notes Reached", f"You can only create up to {MAX_NOTES} notes.")
            return
        dlg = NewNoteDialog(self.theme, parent=None)
        if dlg.exec_() == QDialog.Accepted:
            title = dlg.get_title()
            if title:
                self.add_note(title)

    def add_note(self, title, pos=None, size=None):
        print(f"[LOG] Adding note: {title}")
        if len(self.notes) >= MAX_NOTES:
            QMessageBox.warning(self, "Maximum Notes Reached", f"You can only create up to {MAX_NOTES} notes.")
            return
        color_index = len(self.notes) % len(get_pastel_palette(self.theme))
        note_widget = NoteWidget(title, parent=None, color_index=color_index, theme=self.theme, main_window=self)
        note_widget.set_on_delete(lambda *args, widget=note_widget: self.delete_note(widget))
        note_widget.on_color_change = lambda idx, w=note_widget: self.update_note_color(w, idx)
        if size:
            note_widget.resize(size[0], size[1])
        if pos:
            note_widget.move(pos[0], pos[1])
        else:
            # Get screen geometry
            screen = QApplication.primaryScreen().geometry()
            margin = 20
            note_width = note_widget.width()
            note_height = note_widget.height()
            
            # Try to find a non-overlapping position
            found_position = False
            for row in range(3):  # Try 3 rows
                for col in range(3):  # Try 3 columns
                    x = margin + col * (note_width + margin)
                    y = margin + row * (note_height + margin)
                    
                    # Check if this position overlaps with any existing note
                    overlaps = False
                    for note in self.notes:
                        if (abs(note.x() - x) < note_width and 
                            abs(note.y() - y) < note_height):
                            overlaps = True
                            break
                    
                    if not overlaps:
                        note_widget.move(x, y)
                        found_position = True
                        break
                if found_position:
                    break
            
            # If no non-overlapping position found, use a random position
            if not found_position:
                x = margin + (len(self.notes) * 30) % (screen.width() - note_width - margin)
                y = margin + (len(self.notes) * 30) % (screen.height() - note_height - margin)
                note_widget.move(x, y)
        
        self.notes.append(note_widget)
        note_widget.show()
        print(f"[LOG] Notes after add: {[n.title for n in self.notes]}")
        self.save_notes()

    def update_note_color(self, note_widget, color_index):
        note_widget.color_index = color_index
        note_widget.apply_color()

    def delete_note(self, note_widget):
        print(f"[LOG] Deleting note: {note_widget.title}")
        menu = self.tray_icon.contextMenu()
        if menu and menu.isVisible():
            print("[LOG] Hiding tray menu before deletion.")
            menu.hide()
            for action in menu.actions():
                print(f"[LOG] Blocking signals for action: {action.text()}")
                action.blockSignals(True)
        
        # Create and style the message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Note")
        msg_box.setText(f"Are you sure you want to delete '{note_widget.title}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        # Apply theme-based styling
        font_color = '#fff' if self.theme == 'dark' else '#000'
        bg_color = '#222' if self.theme == 'dark' else '#fff'
        btn_bg = '#333' if self.theme == 'dark' else '#eee'
        btn_fg = '#fff' if self.theme == 'dark' else '#000'
        btn_hover = '#444' if self.theme == 'dark' else '#ddd'
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background: {bg_color};
                color: {font_color};
            }}
            QMessageBox QLabel {{
                color: {font_color};
            }}
            QPushButton {{
                color: {btn_fg};
                background: {btn_bg};
                border-radius: 6px;
                border: 1px solid #888;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background: {btn_hover};
            }}
        """)
        
        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            self.notes.remove(note_widget)
            note_widget.deleteLater()
            print(f"[LOG] Notes after delete: {[n.title for n in self.notes]}")
            if self.showhide_dialog:
                self.showhide_dialog.close()
            self.showhide_dialog = None
            self.save_notes()

    def show_all_notes(self):
        for note in self.notes:
            note.set_visible(True)

    def hide_all_notes(self):
        for note in self.notes:
            note.set_visible(False)

    def open_showhide_dialog(self):
        if self.showhide_dialog is None or not self.showhide_dialog.isVisible():
            self.showhide_dialog = ShowHideDialog(self.notes, self)
            self.showhide_dialog.finished.connect(self._on_showhide_dialog_closed)
            self.showhide_dialog.exec_()

    def _on_showhide_dialog_closed(self, result):
        print("[LOG] Show/Hide dialog closed.")
        self.showhide_dialog = None

    def note_hidden_from_button(self, note):
        if self.showhide_dialog:
            self.showhide_dialog.set_checkbox(note, False)

    def load_notes(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    # Load theme first
                    self.theme = data.get("theme", "dark")
                    # Update UI for theme
                    self.update_tooltip_style()
                    self.tray_icon.setIcon(QIcon(create_sticky_note_icon(self.theme)))
                    
                    for note in self.notes:
                        note.deleteLater()
                    self.notes.clear()
                    for note_data in data["notes"]:
                        pos = note_data.get("pos")
                        size = note_data.get("size")
                        self.add_note(note_data["title"], pos=pos, size=size)
                        self.notes[-1].set_data(note_data)
            except Exception as e:
                print(f"Error loading notes: {e}")

    def save_notes(self):
        try:
            data = {
                "theme": self.theme,
                "notes": [note.get_data() for note in self.notes]
            }
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        
        # Update all notes
        for note in self.notes:
            note.theme = self.theme
            note.apply_color()
            # Update icons
            note.hide_button.setIcon(QIcon(get_icon_pixmap('minimize', self.theme)))
            note.delete_button.setIcon(QIcon(get_icon_pixmap('delete', self.theme)))
            note.palette_button.setIcon(QIcon(get_icon_pixmap('palette', self.theme)))
            note.settings_button.setIcon(QIcon(get_icon_pixmap('settings', self.theme)))
        
        # Update tray icon
        self.tray_icon.setIcon(QIcon(create_sticky_note_icon(self.theme)))
        
        # Update tooltip style
        self.update_tooltip_style()

    def update_tooltip_style(self):
        tooltip_bg = '#222' if self.theme == 'dark' else '#fff'
        tooltip_fg = '#fff' if self.theme == 'dark' else '#000'
        QApplication.instance().setStyleSheet(
            f"QToolTip {{ color: {tooltip_fg}; background-color: {tooltip_bg}; border: 1px solid #888; }}")

    def quit_app(self):
        self.save_notes()
        QApplication.quit()

    def note_title_changed(self, note_widget, new_title):
        # Update tray checklist
        # Update Show/Hide dialog if open
        if self.showhide_dialog:
            self.showhide_dialog.set_checkbox(note_widget, note_widget.is_visible)
        # Update in-memory title (already done in note_widget)

    def bring_notes_to_workspace(self):
        # Record all open notes
        open_notes = [note for note in self.notes if note.is_visible]
        print(f"[LOG] Bringing notes to workspace: {open_notes}")
        # Hide all visible notes
        self.hide_all_notes()
        # Force a repaint and update of each note window
        
        for note in open_notes:
            # note.hide()
            # note.show()
            note.set_visible(True)
        
        # for note in self.notes:
        #     note.hide()
        #     note.show()
        # # Show only the previously open notes
        # for note in open_notes:
        #     note.set_visible(True)

    def show_readme(self):
        dialog = ReadmeDialog(self.theme, self)
        dialog.exec_()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = StickyNotesApp()
#     window.show()
#     sys.exit(app.exec_())
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StickyNotesApp()
    window.setAttribute(Qt.WA_DontShowOnScreen, True)  # Make invisible but Qt-functional
    window.setWindowFlags(Qt.Tool)                     # Optional: hide from taskbar
    window.show()
    sys.exit(app.exec_())

    
    
