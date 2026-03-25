# DOCTOR-DEV – Hospital Management System

A full‑featured Clinic Management System built with **Python CGI** and **SQL**. This system allows patients to book appointments, doctors to manage their schedules, and administrators to oversee all operations. It was developed as part of the **SSE 2304 Server‑Side Programming** coursework at Kirinyaga University.

---

## 🚀 Features

### 👤 Patient Module
- Register & login securely
- Book, reschedule, and cancel appointments
- View appointment history
- Update personal profile and change password
- View doctor profiles and specialties

### 👨‍⚕️ Doctor Module
- Login with assigned credentials
- View own appointment schedule
- Update availability slots
- Manage patient appointments (complete, reschedule, cancel)
- Edit profile and change password

### 🛡️ Admin Module
- Manage doctors (add, edit, view, delete)
- Manage patients (add, edit, view)
- Oversee all appointments
- Generate reports (exportable)
- Configure clinic settings and specialties

### ✨ Additional Features
- Responsive, modern UI (Bootstrap 5 + Font Awesome)
- Animated scrolling (AOS library)
- Secure password hashing (bcrypt)
- Session management for role‑based access
- Email‑style alerts and toast notifications

---

## 📁 Project Structure

The repository contains all Python CGI scripts, and a SQL schema file for setup. Key files:
DOCTOR-DEV/
├── index.py # Landing page
├── patient_.py # Patient‑side scripts
├── doctor_.py # Doctor‑side scripts
├── admin_*.py # Admin‑side scripts
├── database.py # Database operations
├── session.py # Session handling
├── validation.py # Input validation
├── clinic_system.sql # Full database schema
├── config.py # Configuration settings
└── README.md # This file


---

## 🛠️ Technologies Used

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Backend      | Python 3.13, CGI, SQL           |
| Frontend     | HTML5, CSS3, JavaScript              |
| Frameworks   | Bootstrap 5, Font Awesome 6, AOS.js |
| Security     | bcrypt password hashing, sessions   |
| Web Server   | Apache with CGI support (or any CGI‑capable server) |

---

## 📦 Installation & Setup

### Prerequisites
- **Python 3.13** or higher installed (with `sqlite3` and `bcrypt` modules)
- A web server with CGI support (e.g., Apache, XAMPP, or Python's built‑in `http.server` with CGI)

### Step 1: Clone the Repository
```bash
git clone https://github.com/brandoenkimu/DOCTOR-DEV.git
cd DOCTOR-DEV
Step 2: Set Up the Database
bash
sqlite3 clinic.db < clinic_system.sql
This creates all tables and inserts sample data (including default admin credentials).

Step 3: Configure Python Path (if needed)
Edit the shebang line (#!C:\Program Files\Python313\python.exe) in each .py file to point to your Python interpreter.
Alternatively, on Linux/macOS, use #!/usr/bin/env python3.

Step 4: Deploy to Your Web Server
Apache: Place the project folder in cgi-bin/ and ensure CGI execution is enabled.

XAMPP: Copy to C:\xampp\cgi-bin\ and start Apache.

Python built‑in server:

bash
python -m http.server --cgi 8000
Then access http://localhost:8000/index.py.

Step 5: Login Credentials
Role	Username / Email	Password
Patient	john.mwangi@email.com	patient123
Doctor	sarah.johnson@clinic.com	doctor123
Admin	admin	Admin@123
🧪 Usage
Visit index.py – the home page.

Login using the credentials above (or register as a new patient).

Book an appointment – choose a doctor, date, and time.

View appointments – see upcoming/past visits.

Manage profile – update personal details or change password.

Admin area – add/remove doctors, view all appointments, etc.

📚 Database Schema
The system uses the following main tables:

patients – stores patient details and registration numbers.

doctors – doctor profiles, specialties, availability.

appointments – booking records with statuses.

admins – system administrators.

specialties – medical specialties.

schedules – weekly working hours for doctors.

See clinic_system.sql for the complete schema and sample data.

🤝 Contributing
Contributions are welcome! To contribute:

Fork the repository.

Create a new branch (git checkout -b feature/amazing-feature).

Commit your changes (git commit -m 'Add some amazing feature').

Push to the branch (git push origin feature/amazing-feature).

Open a Pull Request.

📄 License
This project is for educational purposes. No specific license is applied – feel free to use and modify for your own learning.

📧 Contact
Author: Brandon Kimutai (brandoenkimu)

University: Kirinyaga University

Email: bentelybrandoen@gmail.com

GitHub: brandoenkimu/DOCTOR-DEV

Thank you for using DOCTOR-DEV!
If you encounter any issues, please open an issue on GitHub.
