import sys
import os
import platform

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,QLineEdit, QPushButton, QCheckBox, QTextEdit, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import qdarktheme
#from qdarktheme import setup_theme
#from PyQtDarkTheme import setup_theme
from converter import convert_heic_to_jpeg, convert_heic_file

# Handle DPI awareness for Windows
if platform.system() == "Windows":
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Enable HiDPI scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1.25"

class HEICConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HEIC to JPEG Converter")
        self.resize(600, 500)
        
        icon_path = os.path.join(
            getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))),
            "ht.png"  # 打包时的图标路径
        )
        self.setWindowIcon(QIcon(icon_path)) 
        # Main layout
        main_layout = QVBoxLayout()

        # Path input section
        path_layout = QHBoxLayout()
        self.path_label = QLabel("File or Directory Path:")
        self.path_entry = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_entry)
        path_layout.addWidget(self.browse_button)
        main_layout.addLayout(path_layout)

        # Options section
        self.remove_check = QCheckBox("Remove converted HEIC Files")
        self.overwrite_check = QCheckBox("Overwrite existing JPEG files")
        self.recursive_check = QCheckBox("Search subdirectories")
        self.recursive_check.setChecked(True)

        main_layout.addWidget(self.remove_check)
        main_layout.addWidget(self.overwrite_check)
        main_layout.addWidget(self.recursive_check)

        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert)
        main_layout.addWidget(self.convert_button)

        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        main_layout.addWidget(self.console_output)

        # Add theme switch button and auto-switch option
        theme_layout = QHBoxLayout()

        self.theme_switch_button = QPushButton("Switch Theme")
        self.theme_switch_button.clicked.connect(self.switch_theme)
        theme_layout.addWidget(self.theme_switch_button)

        self.auto_theme_check = QCheckBox("Follow System Theme")
        self.auto_theme_check.stateChanged.connect(self.toggle_auto_theme)
        theme_layout.addWidget(self.auto_theme_check, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(theme_layout)

        # Footer with author information
        footer_layout = QVBoxLayout()

        # Adding the first author information
        first_row_layout = QHBoxLayout()
        self.author_label = QLabel("Authorship : Sascha Schiwy | GitHub: ")
        self.github_link = QLabel("<a href='https://github.com/saschiwy/HeicConverter'>https://github.com/saschiwy/HeicConverter</a>")
        self.github_link.setOpenExternalLinks(True)
        first_row_layout.addWidget(self.author_label)
        first_row_layout.addWidget(self.github_link, alignment=Qt.AlignmentFlag.AlignRight)

        # Adding the second author information
        second_row_layout = QHBoxLayout()
        self.author_label2 = QLabel("Fix and beautify : PupilDamon | GitHub: ")
        self.github_link2 = QLabel("<a href='https://github.com/PupilDamon/HeicToJpg'>https://github.com/PupilDamon/HeicToJpg</a>")
        self.github_link2.setOpenExternalLinks(True)
        second_row_layout.addWidget(self.author_label2)
        second_row_layout.addWidget(self.github_link2, alignment=Qt.AlignmentFlag.AlignRight)


        footer_layout.addLayout(first_row_layout)
        footer_layout.addLayout(second_row_layout)

        main_layout.addLayout(footer_layout)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Track current theme
        self.current_theme = "dark"
        self.auto_theme_enabled = False

    def browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_entry.setText(path)

    def convert(self):
        path = self.path_entry.text()
        remove = self.remove_check.isChecked()
        overwrite = self.overwrite_check.isChecked()
        recursive = self.recursive_check.isChecked()

        output_text = ""

        if os.path.isdir(path):
            output_text += f'Converting HEIC files in directory {path}\n'
            converted = convert_heic_to_jpeg(path, recursive, overwrite, remove)
            output_text += f'Successfully converted {len(converted)} files\n'

        elif os.path.isfile(path):
            output_text += f'Converting HEIC file {path}\n'
            convert_heic_file(path, os.path.splitext(path)[0] + ".jpg", overwrite, remove)
            output_text += 'Successfully converted file\n'

        else:
            output_text += f'Don\'t know what to do with {path}\n'

        self.console_output.append(output_text)

    def switch_theme(self):
        if not self.auto_theme_enabled:
            if self.current_theme == "dark":
                qdarktheme.setup_theme("light")
                self.current_theme = "light"
            else:
                qdarktheme.setup_theme("dark")
                self.current_theme = "dark"

    def toggle_auto_theme(self):
        self.auto_theme_enabled = self.auto_theme_check.isChecked()
        if self.auto_theme_enabled:
            self.apply_system_theme()

    def apply_system_theme(self):
        import platform
        if platform.system() == "Windows":
            import ctypes
            dark_mode = ctypes.windll.dwmapi.DwmGetWindowAttribute(
                ctypes.windll.kernel32.GetConsoleWindow(), 20
            )
            qdarktheme.setup_theme("dark" if dark_mode else "light")
            self.current_theme = "dark" if dark_mode else "light"
        elif platform.system() == "Darwin":
            from subprocess import check_output
            output = check_output(
                "defaults read -g AppleInterfaceStyle", shell=True, stderr=open(os.devnull, 'w')
            ).decode()
            qdarktheme.setup_theme("dark" if "Dark" in output else "light")
            self.current_theme = "dark" if "Dark" in output else "light"
        else:
            # Assume light theme for other systems
            qdarktheme.setup_theme("light")
            self.current_theme = "light"

# Main function
def main():
    app = QApplication([])
    qdarktheme.setup_theme("dark")
    window = HEICConverterGUI()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
