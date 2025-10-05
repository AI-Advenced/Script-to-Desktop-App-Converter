# Script to Desktop App Converter v2.0

## 📖 Description

Automatic Python script to desktop application converter with a graphical user interface. This tool allows you to easily transform your Python scripts into fully functional GUI applications with executable building.

<img width="804" height="778" alt="image" src="https://github.com/user-attachments/assets/bbb0c0b0-c721-402f-9757-0981e8011979" />



## ✨ Features

### 🔧 Multi-Framework Support

* **Tkinter** – Native Python interface (recommended)
* **PyQt5/PyQt6** – Modern, professional interface
* **Flask** – Web applications in the browser
* **Console** – Enhanced text/terminal interface

### 🎯 Core Features

* **Automatic code analysis** – Detect frameworks and dependencies
* **Adaptive interface generation** – Custom templates based on source code
* **Executable building** – Create EXE files using PyInstaller
* **Project management** – Save and load configurations
* **Modern web interface** – Responsive and intuitive Flask UI
* **Integrated database** – SQLite storage for persistence

### 🚀 Benefits

* **Easy to use** – Intuitive web interface
* **Customizable** – Full configuration of options
* **Professional** – Production-quality generated code
* **Portable** – Standalone executables
* **Scalable** – Modular, extensible architecture

## 🛠️ Installation

### Prerequisites

* Python 3.7 or higher
* pip (Python package manager)

### Install dependencies

```bash
cd script_converter
pip install -r requirements.txt
```

### Optional dependencies

For PyQt5/PyQt6 (if desired):

```bash
pip install PyQt5==5.15.9
# or
pip install PyQt6==6.5.2
```

## 🚀 Usage

### Start the application

```bash
python app.py
```

The web interface will be available at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### User Guide

#### 1. **Upload a Script**

* Go to the “Upload” tab
* Select your Python file (.py or .pyw)
* Automatic analysis detects the framework used

#### 2. **Project Configuration**

* Fill general information (name, author, version)
* Choose the appropriate GUI framework
* Set build options
* Verify detected dependencies

#### 3. **Preview**

* Click “Preview” to view the generated code
* Export code if needed
* Check the structure before building

#### 4. **Build Executable**

* Click “Build” to create the EXE
* Monitor progress in the modal window
* Download the executable once complete

## 📂 Project Structure

```
script_converter/
├── app.py                 # Main application
├── templates/             # Flask templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── upload.html        # Upload page
│   └── project_config.html# Project configuration
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── script.js      # Custom JavaScript
├── uploads/               # Uploaded scripts
├── output/                # Generated executables
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🎨 Generated Templates

### Tkinter Template

* Native Python GUI
* Tabs for execution, source code, console
* Built-in code editor with syntax highlighting
* Redirect output to interface
* Full menus and keyboard shortcuts

### PyQt5/PyQt6 Template

* Modern, professional interface
* Advanced, responsive widgets
* Formatted code editor
* Optimized event handling
* Cross-platform support

### Flask Template

* Complete web application
* Responsive Bootstrap interface
* REST API for code execution
* Customizable Jinja2 templates
* Built-in development server

### Console Template

* Interactive text interface
* Intuitive navigation menu
* Custom code execution
* Formatted and colored output
* Advanced error handling

## ⚙️ Advanced Configuration

### Build Options

* **Single file** – Standalone EXE
* **Include console** – Show console window for debugging
* **UPX compression** – Reduce executable size
* **Debug mode** – Detailed information
* **Architecture** – x86, x64, or auto

### Dependency Management

* Automatic import detection
* Filter standard Python modules
* Manual addition of specific dependencies
* Validation before building

## 🔧 Development

### Architecture

The application follows a modular architecture:

* **DatabaseManager** – SQLite management
* **CodeAnalyzer** – Python AST code analysis
* **TemplateGenerator** – GUI code generation
* **PyInstallerBuilder** – Executable building
* **FlaskWebInterface** – Web interface

### Extensibility

Easily add new frameworks:

1. Create a `_generate_[framework]_template` method
2. Add the framework to the `templates` dictionary
3. Update detection in `CodeAnalyzer`

## 📝 Usage Examples

### Simple Script

```python
# hello.py
print("Hello, world!")
name = input("Your name: ")
print(f"Hi {name}!")
```

→ Generates a GUI application with execution interface

### Script with Interface

```python
# calculator.py
import tkinter as tk
# ... calculator code
```

→ Detects Tkinter and generates an enhanced interface

### Web Script

```python
# webapp.py
from flask import Flask
app = Flask(__name__)
# ... Flask application
```

→ Generates a complete web interface

## 🐛 Troubleshooting

### Common Errors

**"PyInstaller not found"**

```bash
pip install pyinstaller
```

**"Unable to analyze code"**

* Check Python syntax
* Ensure file is UTF-8 encoded

**"Build failed"**

* Verify listed dependencies
* Try debug mode
* Check detailed logs

**"Web interface inaccessible"**

* Ensure Flask is installed
* Port 5000 may be in use
* Check firewall/antivirus

## 📊 Limitations

* Maximum file size: 50MB
* System dependencies not automatically handled
* Some native modules require manual configuration
* PyInstaller may require exclusions for certain antiviruses

## 🤝 Contribution

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under MIT. See the `LICENSE` file for details.

## 🔗 Technologies Used

* **Backend**: Python 3.7+, Flask, SQLite
* **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
* **Build**: PyInstaller, UPX (optional)
* **GUI**: Tkinter, PyQt5/6 (optional)

## 📞 Support

For questions or issues:

* Open an issue on GitHub
* Check the documentation
* Review error logs

---

**Version**: 2.0
**Last Update**: 2025
**Author**: AI-Advenced

