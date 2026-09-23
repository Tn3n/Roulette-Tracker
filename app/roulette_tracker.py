import sys
import os
import ctypes
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QScrollArea, QFrame, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont, QIcon, QPainter

class BackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.background_pixmap = None
        try:
            self.background_pixmap = QPixmap(image_path)
        except:
            pass
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background_pixmap and not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            painter.fillRect(self.rect(), Qt.black)

class ShotTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buckshot Roulette Tracker")
        self.resize(750, 650)
        self.setMinimumSize(750, 650)
        self.center_on_screen()
        
        try:
            self.setWindowIcon(QIcon(resource_path('Nero_29.ico')))
        except:
            pass
        
        self.enable_dark_title_bar()
        
        background = BackgroundWidget(resource_path('21.png'), self)
        self.setCentralWidget(background)
        
        self.shot_number = 1
        self.live_played = 0
        self.blanks_played = 0
        self.shot_history = []
        self.predictions = {}
        self.live_total = 3
        self.blanks_total = 4
        
        main_widget = QWidget(background)
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        main_widget.setLayout(main_layout)
        background.setLayout(QVBoxLayout())
        background.layout().addWidget(main_widget)
        
        # left side - History log
        left_frame = QFrame()
        left_frame.setFixedWidth(280)
        left_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 10, 10, 200);
                border-radius: 10px;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10, 15, 10, 15)
        left_frame.setLayout(left_layout)
        
        history_title = QLabel("Shot History Log")
        history_title.setAlignment(Qt.AlignCenter)
        history_title.setStyleSheet("color: #cccccc; font-size: 16px; font-weight: bold; background: transparent;")
        left_layout.addWidget(history_title)
        
        self.history_stats = QLabel("Live 0/3  |  Blank 0/4")
        self.history_stats.setAlignment(Qt.AlignCenter)
        self.history_stats.setStyleSheet("color: #A0A0A0; font-size: 11px; background: transparent;")
        left_layout.addWidget(self.history_stats)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(5, 5, 5, 220);
                border-radius: 5px;
                border: 1px solid rgba(10, 20, 40, 100);
            }
            QScrollBar:vertical {
                background: rgba(5, 10, 20, 200);
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #051a30, stop:1 #082540);
                border-radius: 4px;
                min-height: 20px;
                border: 1px solid rgba(20, 40, 70, 80);
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0a2550, stop:1 #0d3060);
            }
            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #031020, stop:1 #051a30);
            }
            QScrollBar::add-line:vertical {
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 0px;
                height: 0px;
            }
        """)
        
        self.history_widget = QWidget()
        self.history_widget.setStyleSheet("background: transparent;")
        self.history_widget.setMinimumHeight(2000)
        self.history_layout = QVBoxLayout()
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_layout.setSpacing(5)
        self.history_widget.setLayout(self.history_layout)
        
        self.history_layout.addStretch(100)
        
        scroll_area.setWidget(self.history_widget)
        left_layout.addWidget(scroll_area)
        
        scroll_btn_layout = QHBoxLayout()
        scroll_btn_layout.setAlignment(Qt.AlignCenter)
        
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(60, 35)
        up_btn.setStyleSheet(self.button_style("#151515", "#252525"))
        up_btn.clicked.connect(lambda: scroll_area.verticalScrollBar().setValue(
            scroll_area.verticalScrollBar().value() - 100))
        scroll_btn_layout.addWidget(up_btn)
        
        down_btn = QPushButton("▼")
        down_btn.setFixedSize(60, 35)
        down_btn.setStyleSheet(self.button_style("#151515", "#252525"))
        down_btn.clicked.connect(lambda: scroll_area.verticalScrollBar().setValue(
            scroll_area.verticalScrollBar().value() + 100))
        scroll_btn_layout.addWidget(down_btn)
        
        left_layout.addLayout(scroll_btn_layout)
        main_layout.addWidget(left_frame)
        
        # right side
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        
        # Setup Frame
        setup_frame = QFrame()
        setup_frame.setStyleSheet("background-color: rgba(10, 10, 10, 200); border-radius: 10px;")
        setup_layout = QVBoxLayout()
        setup_layout.setContentsMargins(15, 12, 15, 12)
        setup_frame.setLayout(setup_layout)
        
        setup_label = QLabel("Round Setup")
        setup_label.setAlignment(Qt.AlignCenter)
        setup_label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: bold; background: transparent;")
        setup_layout.addWidget(setup_label)
        
        inputs_layout = QHBoxLayout()
        inputs_layout.setAlignment(Qt.AlignCenter)
        inputs_layout.setSpacing(25)
        
        live_label = QLabel("Live:")
        live_label.setStyleSheet("color: #ff4444; font-size: 13px; font-weight: bold; background: transparent;")
        inputs_layout.addWidget(live_label)
        
        self.live_entry = QLineEdit("3")
        self.live_entry.setFixedSize(50, 30)
        self.live_entry.setAlignment(Qt.AlignCenter)
        self.live_entry.setStyleSheet("background-color: #151515; color: #ff4444; font-size: 13px; font-weight: bold; border: none; border-radius: 5px;")
        inputs_layout.addWidget(self.live_entry)
        
        inputs_layout.addSpacing(30)
        
        blank_label = QLabel("Blank:")
        blank_label.setStyleSheet("color: #e0e0e0; font-size: 13px; font-weight: bold; background: transparent;")
        inputs_layout.addWidget(blank_label)
        
        self.blanks_entry = QLineEdit("4")
        self.blanks_entry.setFixedSize(50, 30)
        self.blanks_entry.setAlignment(Qt.AlignCenter)
        self.blanks_entry.setStyleSheet("background-color: #151515; color: #e0e0e0; font-size: 13px; font-weight: bold; border: none; border-radius: 5px;")
        inputs_layout.addWidget(self.blanks_entry)
        
        setup_layout.addLayout(inputs_layout)
        
        start_btn = QPushButton("START ROUND")
        start_btn.setFixedHeight(38)
        start_btn.setStyleSheet(self.button_style("#151515", "#252525"))
        start_btn.setFocusPolicy(Qt.NoFocus)
        start_btn.clicked.connect(self.start_round)
        setup_layout.addWidget(start_btn)
        
        right_layout.addWidget(setup_frame)
        
        # Shells/Shot display frame
        remaining_frame = QFrame()
        remaining_frame.setStyleSheet("background-color: rgba(10, 10, 10, 200); border-radius: 10px;")
        remaining_layout = QVBoxLayout()
        remaining_layout.setContentsMargins(15, 18, 15, 18)
        remaining_frame.setLayout(remaining_layout)
        
        # left side
        top_row = QHBoxLayout()
        
        
        shot_left_layout = QHBoxLayout()
        shot_left_layout.setSpacing(8)
        
        
        self.shot_label = QLabel("1")
        self.shot_label.setAlignment(Qt.AlignCenter)
        self.shot_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.shot_label.setStyleSheet("color: #ffaa00; background: transparent;")
        shot_left_layout.addWidget(self.shot_label)
        
        
        shot_text_layout = QVBoxLayout()
        shot_text_layout.setSpacing(0)
        
        shot_label_top = QLabel("SHOT")
        shot_label_top.setAlignment(Qt.AlignLeft)
        shot_label_top.setStyleSheet("""
            color: #ffaa00; 
            font-size: 9px; 
            font-weight: bold; 
            background: transparent;
            letter-spacing: 2px;
            font-family: 'Segoe UI', 'Tahoma', sans-serif;
        """)
        shot_text_layout.addWidget(shot_label_top)
        
        shot_label_bottom = QLabel("NUM")
        shot_label_bottom.setAlignment(Qt.AlignLeft)
        shot_label_bottom.setStyleSheet("""
            color: #cc8800; 
            font-size: 8px; 
            font-weight: bold; 
            background: transparent;
            letter-spacing: 1px;
            font-family: 'Segoe UI', 'Tahoma', sans-serif;
        """)
        shot_text_layout.addWidget(shot_label_bottom)
        
        shot_left_layout.addLayout(shot_text_layout)
        
        top_row.addLayout(shot_left_layout)
        
        
        top_row.addStretch()
        
        # Right side
        shells_right_layout = QHBoxLayout()
        shells_right_layout.setSpacing(8)
        
        
        shells_text_layout = QVBoxLayout()
        shells_text_layout.setSpacing(0)
        
        shells_label = QLabel("SHELLS")
        shells_label.setAlignment(Qt.AlignRight)
        shells_label.setStyleSheet("""
            color: #4a9eff; 
            font-size: 9px; 
            font-weight: bold; 
            background: transparent;
            letter-spacing: 2px;
            font-family: 'Segoe UI', 'Tahoma', sans-serif;
        """)
        shells_text_layout.addWidget(shells_label)
        
        shells_left_label = QLabel("LEFT")
        shells_left_label.setAlignment(Qt.AlignRight)
        shells_left_label.setStyleSheet("""
            color: #2d7acc; 
            font-size: 8px; 
            font-weight: bold; 
            background: transparent;
            letter-spacing: 1px;
            font-family: 'Segoe UI', 'Tahoma', sans-serif;
        """)
        shells_text_layout.addWidget(shells_left_label)
        
        shells_right_layout.addLayout(shells_text_layout)
        
        
        self.remaining_label = QLabel("7")
        self.remaining_label.setAlignment(Qt.AlignCenter)
        self.remaining_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.remaining_label.setStyleSheet("color: #4a9eff; background: transparent;")
        shells_right_layout.addWidget(self.remaining_label)
        
        top_row.addLayout(shells_right_layout)
        
        remaining_layout.addLayout(top_row)
        
        remaining_layout.addSpacing(45)
        
        # Live/Blank counts
        counts_layout = QHBoxLayout()
        counts_layout.setAlignment(Qt.AlignCenter)
        
        self.remaining_lives_label = QLabel("Live 3/3")
        self.remaining_lives_label.setStyleSheet("color: #ff4444; font-size: 14px; font-weight: bold; background: transparent;")
        counts_layout.addWidget(self.remaining_lives_label)
        
        divider = QLabel("|")
        divider.setStyleSheet("color: #333333; font-size: 14px; background: transparent;")
        counts_layout.addWidget(divider)
        
        self.remaining_blanks_label = QLabel("Blank 4/4")
        self.remaining_blanks_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold; background: transparent;")
        counts_layout.addWidget(self.remaining_blanks_label)
        
        remaining_layout.addLayout(counts_layout)
        
        right_layout.addWidget(remaining_frame)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(15)
        
        self.live_btn = QPushButton("LIVE")
        self.live_btn.setFixedSize(80, 40)
        self.live_btn.setStyleSheet(self.button_style("#cc0000", "#ee2222"))
        self.live_btn.setFocusPolicy(Qt.NoFocus)
        self.live_btn.clicked.connect(self.live_shot)
        btn_layout.addWidget(self.live_btn)
        
        self.blank_btn = QPushButton("BLANK")
        self.blank_btn.setFixedSize(80, 40)
        self.blank_btn.setStyleSheet(self.button_style("#2a2a2a", "#3a3a3a"))
        self.blank_btn.setFocusPolicy(Qt.NoFocus)
        self.blank_btn.clicked.connect(self.blank_shot)
        btn_layout.addWidget(self.blank_btn)
        
        right_layout.addLayout(btn_layout)
        
        reset_btn = QPushButton("RESET")
        reset_btn.setFixedHeight(38)
        #reset_btn.setFixedWidth(150)
        reset_btn.setStyleSheet(self.button_style("#151515", "#252525"))
        reset_btn.setFocusPolicy(Qt.NoFocus)
        reset_btn.clicked.connect(self.reset_round)
        
        reset_undo_layout = QHBoxLayout()
        reset_undo_layout.setSpacing(10)
        reset_undo_layout.addWidget(reset_btn)
        

        self.undo_btn = QPushButton("UNDO")
        self.undo_btn.setFixedHeight(38)
        #self.undo_btn.setFixedWidth(150)
        self.undo_btn.setStyleSheet(self.button_style("#151515", "#252525", "14px"))
        self.undo_btn.setFocusPolicy(Qt.NoFocus)
        self.undo_btn.clicked.connect(self.undo_shot)
        self.undo_btn.setEnabled(False)
        reset_undo_layout.addWidget(self.undo_btn)

        right_layout.addLayout(reset_undo_layout)
        
        # Predictions
        pred_frame = QFrame()
        pred_frame.setStyleSheet("background-color: rgba(10, 10, 10, 200); border-radius: 10px;")
        pred_layout = QVBoxLayout()
        pred_layout.setContentsMargins(15, 10, 15, 12)
        pred_frame.setLayout(pred_layout)
        
        pred_title = QLabel("Predictions")
        pred_title.setAlignment(Qt.AlignCenter)
        pred_title.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: bold; background: transparent;")
        pred_layout.addWidget(pred_title)
        
        note_layout = QHBoxLayout()
        note_layout.setSpacing(4)
        note_layout.setAlignment(Qt.AlignCenter)
        note1 = QLabel("Note:")
        note1.setStyleSheet("color: #ffcc00; font-size: 9px; font-weight: bold; background: transparent;")
        note_layout.addWidget(note1)
        note2 = QLabel("Count shells from your current turn only")
        note2.setStyleSheet("color: #555555; font-size: 9px; font-weight: 600; background: transparent;")
        note_layout.addWidget(note2)
        pred_layout.addLayout(note_layout)
        
        pred_entry_layout = QHBoxLayout()
        pred_entry_layout.setAlignment(Qt.AlignCenter)
        
        shell_label = QLabel("Shell")
        shell_label.setStyleSheet("color: #666666; font-size: 10px; background: transparent;")
        pred_entry_layout.addWidget(shell_label)
        
        self.pred_shell_entry = QLineEdit()
        self.pred_shell_entry.setFixedSize(40, 25)
        self.pred_shell_entry.setAlignment(Qt.AlignCenter)
        self.pred_shell_entry.setStyleSheet("background-color: #151515; color: white; font-size: 12px; font-weight: bold; border: none;")
        pred_entry_layout.addWidget(self.pred_shell_entry)
        
        self.pred_group = QButtonGroup()
        
        self.pred_live_radio = QRadioButton("Live")
        self.pred_live_radio.setChecked(True)
        self.pred_live_radio.setFocusPolicy(Qt.NoFocus)
        self.pred_live_radio.setStyleSheet("QRadioButton { color: #ff4444; font-size: 10px; font-weight: bold; background: transparent; }")
        self.pred_group.addButton(self.pred_live_radio)
        pred_entry_layout.addWidget(self.pred_live_radio)
        
        self.pred_blank_radio = QRadioButton("Blank")
        self.pred_blank_radio.setFocusPolicy(Qt.NoFocus)
        self.pred_blank_radio.setStyleSheet("QRadioButton { color: #e0e0e0; font-size: 10px; font-weight: bold; background: transparent; }")
        self.pred_group.addButton(self.pred_blank_radio)
        pred_entry_layout.addWidget(self.pred_blank_radio)
        
        save_pred_btn = QPushButton("Save")
        save_pred_btn.setFixedSize(60, 25)
        save_pred_btn.setStyleSheet(self.button_style("#151515", "#252525", "10px"))
        save_pred_btn.clicked.connect(self.save_prediction)
        pred_entry_layout.addWidget(save_pred_btn)
        
        pred_layout.addLayout(pred_entry_layout)
        
        self.pred_display = QLabel("No predictions")
        self.pred_display.setAlignment(Qt.AlignCenter)
        self.pred_display.setStyleSheet("color: #444444; font-size: 10px; background: transparent;")
        pred_layout.addWidget(self.pred_display)
        self.pred_alert_frame = QFrame()
        self.pred_alert_frame.setStyleSheet("background-color: rgba(255, 204, 0, 30); border-radius: 6px;")
        alert_layout = QVBoxLayout()
        alert_layout.setContentsMargins(13, 3, 10, 3)
        self.pred_alert_frame.setLayout(alert_layout)

        self.pred_alert = QLabel("")
        self.pred_alert.setAlignment(Qt.AlignCenter)
        self.pred_alert.setStyleSheet("color: #ffcc00; font-size: 11px; font-weight: bold; background: transparent;")
        self.pred_alert.setWordWrap(True)
        alert_layout.addWidget(self.pred_alert)

        self.pred_alert_frame.setVisible(False)
        pred_layout.addWidget(self.pred_alert_frame)
        
        right_layout.addWidget(pred_frame)
        right_layout.addStretch()
        
        # Credits section
        credits_layout = QVBoxLayout()
        credits_layout.setSpacing(4)
        
        credits_title = QLabel("Credits")
        credits_title.setAlignment(Qt.AlignCenter)
        credits_title.setStyleSheet("color: #4DD0E1; font-size: 15px; font-weight: bold; background: transparent;")
        credits_layout.addWidget(credits_title)
        
        dev_credit = QLabel(" Developed by: r4aage")
        dev_credit.setAlignment(Qt.AlignCenter)
        dev_credit.setStyleSheet("color: #B3E5FC; font-size: 11px; background: transparent;")
        credits_layout.addWidget(dev_credit)
        
        anime_credit = QLabel("Anime: Silent Witch")
        anime_credit.setAlignment(Qt.AlignCenter)
        anime_credit.setStyleSheet("color: #B3E5FC; font-size: 11px; background: transparent;")
        credits_layout.addWidget(anime_credit)
        
        bg_source_credit = QLabel("Background source: r/TheSilentWitch (Banner)")
        bg_source_credit.setAlignment(Qt.AlignCenter)
        bg_source_credit.setStyleSheet("color: #B3E5FC; font-size: 11px; background: transparent;")
        credits_layout.addWidget(bg_source_credit)
        
        icon_credit = QLabel("Icon Source: Nero - Studio Gokumi")
        icon_credit.setAlignment(Qt.AlignCenter)
        icon_credit.setStyleSheet("color: #B3E5FC; font-size: 11px; background: transparent;")
        credits_layout.addWidget(icon_credit)
        
        copyright_credit = QLabel("©2024 Matsuri Isora, Nanna Fujimi / KADOKAWA / Serendia Academy PR")
        copyright_credit.setAlignment(Qt.AlignCenter)
        copyright_credit.setStyleSheet("color: #888888; font-size: 10px; background: transparent; font-style: italic;")
        credits_layout.addWidget(copyright_credit)
        
        app_credit = QLabel("Art by their respective creators")
        app_credit.setAlignment(Qt.AlignCenter)
        app_credit.setStyleSheet("color: #888888; font-size: 10px; background: transparent; font-style: italic;")
        credits_layout.addWidget(app_credit)
        
        right_layout.addLayout(credits_layout)
        
        main_layout.addLayout(right_layout)
        
        self.update_display()
        self.update_history()
        
    def center_on_screen(self):
        
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    def enable_dark_title_bar(self):
        
        try:
            hwnd = self.winId().__int__()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_dark = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                ctypes.byref(set_dark), ctypes.sizeof(set_dark)
            )
        except:
            pass
    
    def resizeEvent(self, event):
        """Handle window resize to update background"""
        super().resizeEvent(event)
        
    
    def button_style(self, bg, hover, font_size="14px"):
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: {font_size};
                font-weight: bold;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: #1a1a1a;
                color: #555555;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """
    
    def start_round(self):
        try:
            self.live_total = int(self.live_entry.text())
            self.blanks_total = int(self.blanks_entry.text())
            self.reset_round()
        except:
            pass
    
    def live_shot(self):
        if self.live_played < self.live_total:
            self.shot_history.append(("Live", self.shot_number))
            self.live_played += 1
            self.shot_number += 1
            self.update_display()
            self.update_history()
    
    def blank_shot(self):
        if self.blanks_played < self.blanks_total:
            self.shot_history.append(("Blank", self.shot_number))
            self.blanks_played += 1
            self.shot_number += 1
            self.update_display()
            self.update_history()
            
    def undo_shot(self):
        if self.shot_history:
            last_type, last_num = self.shot_history.pop()
            if last_type == "Live":
                self.live_played -= 1
            else:
                self.blanks_played -= 1
            self.shot_number -= 1
            self.update_display()
            self.update_history()   
            
    
    def edit_shot(self, index):
        if 0 <= index < len(self.shot_history):
            shot_type, shot_num = self.shot_history[index]
            new_type = "Blank" if shot_type == "Live" else "Live"
        
            if new_type == "Live" and self.live_played >= self.live_total:
                return
            if new_type == "Blank" and self.blanks_played >= self.blanks_total:
                return
        
            if shot_type == "Live":
                self.live_played -= 1
            else:
                self.blanks_played -= 1
        
            if new_type == "Live":
                self.live_played += 1
            else:
                self.blanks_played += 1
        
            self.shot_history[index] = (new_type, shot_num)
            self.update_display()
            self.update_history()
        
    
    def save_prediction(self):
        try:
            shell_num = int(self.pred_shell_entry.text())
            pred_type = "Live" if self.pred_live_radio.isChecked() else "Blank"
            self.predictions[shell_num] = pred_type
            self.update_prediction_display()
            self.check_prediction_alert()
            self.pred_shell_entry.clear()
        except:
            pass
    
    def update_prediction_display(self):
        if self.predictions:
            pred_parts = []
            for k, v in sorted(self.predictions.items()):
                if v == "Live":
                    pred_parts.append(f'<span style="color: #ff4444; font-weight: bold;">{k}: {v}</span>')
                else:
                    pred_parts.append(f'<span style="color: #e0e0e0; font-weight: bold;">{k}: {v}</span>')
            pred_text = '  <span style="color: #444444;">|</span>  '.join(pred_parts)
            self.pred_display.setText(pred_text)
            self.pred_display.setStyleSheet("font-size: 10px; background: transparent;")
        else:
            self.pred_display.setText("No predictions")
            self.pred_display.setStyleSheet("color: #444444; font-size: 10px; background: transparent;")
    
    def reset_round(self):
        self.shot_number = 1
        self.live_played = 0
        self.blanks_played = 0
        self.shot_history = []
        self.predictions = {}
        self.update_display()
        self.update_history()
        self.update_prediction_display()
    
    def update_history(self):
        self.history_stats.setText(f"Live {self.live_played}/{self.live_total}  |  Blank {self.blanks_played}/{self.blanks_total}")
    
        while self.history_layout.count() > 1:
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
        if not self.shot_history:
            no_shots = QLabel("No shots fired yet")
            no_shots.setAlignment(Qt.AlignCenter)
            no_shots.setStyleSheet("color: #444444; font-size: 11px; background: transparent; padding: 30px;")
            self.history_layout.insertWidget(0, no_shots)
        else:
            for idx, (shot_type, shot_num) in enumerate(self.shot_history):
                color = "#ff4444" if shot_type == "Live" else "#e0e0e0"
                bg = "rgba(26, 8, 8, 200)" if shot_type == "Live" else "rgba(15, 15, 15, 200)"
            
                item_frame = QFrame()
                item_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg};
                        border-radius: 5px;
                    }}
                    QFrame:hover {{
                        background-color: rgba(255, 60, 60, 80);
                    }}
                """)
                item_layout = QHBoxLayout()
                item_layout.setContentsMargins(10, 6, 10, 6)
                item_frame.setLayout(item_layout)
            
                label = QLabel(f"Shot {shot_num}  -  {shot_type}")
                label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; background: transparent;")
                item_layout.addWidget(label)
            
                item_layout.addStretch()
            
                edit_label = QLabel("Edit")
                edit_label.setStyleSheet("color: #ffcc00; font-size: 10px; font-weight: bold; background: transparent;")
                edit_label.setCursor(Qt.PointingHandCursor)
                edit_label.setVisible(False)
                edit_label.mousePressEvent = lambda event, i=idx: self.edit_shot(i)
                item_layout.addWidget(edit_label)
            
                item_frame.enterEvent = lambda event, lbl=edit_label: lbl.setVisible(True)
                item_frame.leaveEvent = lambda event, lbl=edit_label: lbl.setVisible(False)
            
                self.history_layout.insertWidget(idx, item_frame)
    
    def update_display(self):
        remaining = (self.live_total - self.live_played) + (self.blanks_total - self.blanks_played)
        self.remaining_label.setText(str(remaining))
        self.shot_label.setText(str(self.shot_number))
        
        self.remaining_lives_label.setText(f"Live {self.live_total - self.live_played}/{self.live_total}")
        self.remaining_blanks_label.setText(f"Blank {self.blanks_total - self.blanks_played}/{self.blanks_total}")
        
        self.live_btn.setEnabled(self.live_played < self.live_total)
        self.blank_btn.setEnabled(self.blanks_played < self.blanks_total)
        self.undo_btn.setEnabled(len(self.shot_history) > 0)
        self.check_prediction_alert()
        
    def check_prediction_alert(self):
        if self.shot_number in self.predictions:
            predicted_type = self.predictions[self.shot_number]
            color = "#ff4444" if predicted_type == "Live" else "#e0e0e0"
            self.pred_alert.setText(f"This shot ({self.shot_number}) predicted: {predicted_type}")
            self.pred_alert.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold; background: transparent;")
            self.pred_alert_frame.setVisible(True)
        else:
            self.pred_alert_frame.setVisible(False)    

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = ShotTrackerApp()
    window.show()
    sys.exit(app.exec_())