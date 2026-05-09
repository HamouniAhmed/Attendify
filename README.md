<p align="center">
  <img src="app/static/images/logo_page.png" alt="Attendify Logo" width="120"/>
</p>

<h1 align="center">🏢 Attendify</h1>

<p align="center">
  <strong>A modern web-based Attendance Management System for tracking suppliers, interns, and visitors across multiple facility locations.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white" alt="Bootstrap"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Usage](#-usage)
- [Testing](#-testing)
- [Build Portable Version](#-build-portable-version)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📋 About the Project

**Attendify** is a full-featured attendance tracking system built for organizations that need to manage the flow of **suppliers**, **interns**, and **visitors** across one or more physical sites. It provides:

- Real-time check-in / check-out via **manual ID**, **CIN**, or **RFID** badge
- Role-based dashboards for **Administrators** and **Secretaries**
- Rich analytics with interactive charts
- One-click data export to **CSV** and **Excel**
- A portable standalone `.exe` build option (via PyInstaller)

---

## ✨ Features

### 🔐 Authentication & Authorization
- Secure login with password hashing (Werkzeug)
- **Two roles**: Admin (full access) and Secretary (attendance only)
- CSRF protection on all forms (Flask-WTF)

### 👥 People Management
- **Suppliers**: Register with company, CIN, CNSS, chef info, and profile photo
- **Interns**: Register with department, supervisor, internship type, and photo
- **Visitors**: Quick walk-in registration at the attendance desk
- Full CRUD operations (Create, Read, Update, Delete)
- Pagination and search across all entity lists

### 📋 Attendance Tracking
- Check-in / check-out by **manual ID**, **RFID UID**, or **CIN**
- Automatic detection: already checked in → check-out; not checked in → check-in
- Supplier check-ins require extra details (visit type, department, person visited)
- Real-time "currently on-site" counters
- Hours-spent calculation on checkout

### 📊 Admin Dashboard
- Summary cards: active suppliers/interns, today's attendance
- **30-day attendance trend** (line chart)
- **Top 10 supplier companies** by hours spent
- **Attendance by location** (bar chart)
- **Interns by department** and **by type** (pie charts)
- **Suppliers by visit type** and **by company** (donut charts)
- All charts powered by [Plotly.js](https://plotly.com/javascript/)

### 📤 Data Export
- Export supplier, intern, or attendance records to **CSV** or **Excel (.xlsx)**
- Filtered exports (by date range, name, department, company, location)
- Formatted Excel output with styled headers and auto-sized columns

### 🔁 Multi-Site Support
- Each user is assigned to a facility location
- Data is scoped per-site for secretaries
- Admins have cross-site visibility

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 3.x |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Auth** | Flask-Login, Werkzeug |
| **Forms** | Flask-WTF / WTForms |
| **Frontend** | Bootstrap 5, Font Awesome 6 |
| **Charts** | Plotly.js |
| **Export** | Pandas, OpenPyXL, XlsxWriter |
| **Production Server** | Waitress |
| **Packaging** | PyInstaller |
| **Testing** | Pytest |

---

## 📁 Project Structure

```
Attendify/
│
├── app/                          # Main application package
│   ├── __init__.py               # App factory (create_app)
│   ├── config.py                 # Configuration classes
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py               # User model (admin/secretary)
│   │   ├── supplier.py           # Supplier model
│   │   ├── intern.py             # Intern model
│   │   └── attendance.py         # Attendance models (supplier, intern, visitor)
│   │
│   ├── controllers/              # Business logic
│   │   ├── auth.py               # Authentication helpers & decorators
│   │   └── attendance_controller.py  # Attendance processing logic
│   │
│   ├── routes/                   # Flask blueprints (views)
│   │   ├── auth_routes.py        # Login, logout, user management
│   │   ├── attendance_routes.py  # Check-in/out, details, export
│   │   ├── dashboard.py          # Admin dashboard & API endpoints
│   │   ├── intern_routes.py      # Intern CRUD
│   │   ├── supplier_routes.py    # Supplier CRUD
│   │   └── records.py            # Historical attendance records
│   │
│   ├── forms/                    # WTForms form classes
│   │   ├── auth_forms.py
│   │   ├── attendance_forms.py
│   │   ├── intern_forms.py
│   │   └── supplier_forms.py
│   │
│   ├── utils/                    # Utility modules
│   │   ├── export_utils.py       # CSV & Excel export helpers
│   │   └── upload_pics.py        # Profile picture upload handler
│   │
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base layout
│   │   ├── _form_macros.html     # Reusable form macros
│   │   ├── admin/                # Dashboard template
│   │   ├── auth/                 # Login, users templates
│   │   ├── attendance/           # Attendance pages
│   │   ├── interns/              # Intern CRUD pages
│   │   └── suppliers/            # Supplier CRUD pages
│   │
│   └── static/                   # Static assets
│       ├── css/                  # Stylesheets
│       ├── js/                   # JavaScript (Bootstrap, jQuery, Plotly, custom)
│       ├── images/               # App logos
│       ├── uploads/              # User-uploaded photos (gitignored)
│       └── webfonts/             # Font Awesome fonts
│
├── tests/                        # Test suite
│   ├── conftest.py               # Pytest fixtures
│   ├── models/
│   │   └── test_user.py          # User model tests
│   └── routes/
│       └── test_auth_routes.py   # Auth route tests
│
├── run.py                        # Development entry point
├── serve.py                      # Production server (Waitress)
├── launcher.py                   # Desktop launcher (server + browser)
├── build_standalone.py           # PyInstaller packaging script
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git exclusions
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10** or higher
- **pip** (Python package manager)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Attendify.git
   cd Attendify
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the project root (optional but recommended):

```env
SECRET_KEY=your-super-secret-random-key-here
FLASK_CONFIG=development
```

> ⚠️ **Important:** If you don't set `SECRET_KEY`, the app will use a default fallback which is **not secure for production**.

### Running the App

**Development mode:**
```bash
python run.py
```
The app will start at `http://127.0.0.1:5000` with debug mode enabled.

**Production mode (Waitress):**
```bash
python serve.py
```

**Desktop launcher (opens browser automatically):**
```bash
python launcher.py
```

### Default Admin Account

On first launch, a default admin account is created automatically:

| Field | Value |
|---|---|
| Email | `admin@attendify.com` |
| Password | `admin123` |

> ⚠️ **Change the default password immediately after first login!**

---

## 📖 Usage

### Secretary Workflow
1. Log in with your secretary account
2. On the **Attendance** page, enter a supplier/intern ID, RFID, or CIN
3. The system auto-detects whether to **check in** or **check out**
4. For suppliers: fill in visit type, department, and person visited
5. For walk-in visitors: use the **Register Visitor** form

### Admin Workflow
1. Log in with admin credentials
2. Access the **Dashboard** for real-time analytics and charts
3. Manage **Suppliers** and **Interns** (add, edit, delete, view history)
4. View **Attendance Records** with date/type/location filters
5. **Export** filtered data to CSV or Excel
6. Manage **Users** (create secretary accounts)

---

## 🧪 Testing

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/models/test_user.py -v
```

The test suite uses an **in-memory SQLite database** with automatic transaction rollback for full test isolation.

---

## 📦 Build Portable Version

To create a standalone `.exe` (no Python installation required):

1. Ensure PyInstaller is installed:
   ```bash
   pip install pyinstaller
   ```

2. Create an `attendify.spec` file (or use the build script):
   ```bash
   python build_standalone.py
   ```

3. The portable package will be created in the `Attendify_Portable/` directory.

---

## 🖼 Screenshots

> _Add screenshots of the login page, dashboard, attendance page, and supplier management here._

<!-- Example:
![Login Page](docs/screenshots/login.png)
![Dashboard](docs/screenshots/dashboard.png)
![Attendance](docs/screenshots/attendance.png)
-->

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code style
- Add tests for new features
- Update this README if adding new functionality
- Use WTForms for all user input (CSRF protection)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using Flask
</p>
