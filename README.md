# LibraryPro — Django Library Management System

A responsive library management web application built with Django and SQLite, with optional MySQL configuration.

## Features
- Secure Django session login and logout
- Dashboard with collection, member, active-loan and overdue statistics
- Book catalog: create, read, update, delete, search
- Category management
- Member registration and management
- Issue books and record returns
- Automatic available-copy updates when a book is issued or returned
- Overdue loan indicators
- Reports page with print support
- Django admin for trusted administrators
- Responsive premium interface for desktop, tablet and mobile

## Requirements
- Python 3.10 or newer (Python 3.12/3.13 recommended)
- Visual Studio Code
- Internet connection for first-time dependency installation and Google Fonts

## Setup on Windows / VS Code (SQLite — easiest)

1. Extract `LibraryPro_Django.zip`.
2. Open VS Code → **File → Open Folder** → select `LibraryPro_Django`.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv venv
   ```

5. Activate it in PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use this command for the current terminal only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

   Or use Command Prompt terminal:

   ```cmd
   venv\Scripts\activate.bat
   ```

6. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Create database tables:

   ```powershell
   python manage.py migrate
   ```

8. Create your administrator account:

   ```powershell
   python manage.py createsuperuser
   ```

   Enter a username, email (optional), and password. Password characters may not appear while typing; that is normal.

9. Start the development server:

   ```powershell
   python manage.py runserver
   ```

10. Open `http://127.0.0.1:8000/` in your browser and sign in using the superuser credentials.

Admin tools: `http://127.0.0.1:8000/admin/`

## Deploy to Render

1. Push the **contents** of this `LibraryPro_Django` folder to a GitHub repository. Do not upload the outer `venv` or the local `db.sqlite3` file.
2. In Render, choose **New → Blueprint**, connect that repository, and apply the `render.yaml` blueprint. It creates the web service and PostgreSQL database; the first build runs migrations and collects static files.
3. When the service is live, open its `onrender.com` URL and create a staff account from the Render service's **Shell** using `python manage.py createsuperuser`.

The free Render PostgreSQL database is temporary and may expire; use a paid database for persistent production data. Keep the generated `DJANGO_SECRET_KEY` private.

## MySQL configuration (optional)

1. Install and start MySQL using XAMPP or MySQL Server.
2. Create a database named `librarypro` using phpMyAdmin or MySQL:

   ```sql
   CREATE DATABASE librarypro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. Install the project requirements:

   ```powershell
   pip install -r requirements.txt
   ```

4. Set these environment variables in the same terminal before running Django:

   ```powershell
   $env:DB_ENGINE="mysql"
   $env:DB_NAME="librarypro"
   $env:DB_USER="root"
   $env:DB_PASSWORD=""
   $env:DB_HOST="127.0.0.1"
   $env:DB_PORT="3306"
   ```

   Replace the username/password with your actual MySQL credentials.

5. Run:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

To return to SQLite, close the terminal and open a new one (or remove `DB_ENGINE` from the current environment).

## Suggested first-time data setup

1. Sign in.
2. Open **Categories** and create categories such as Fiction, Science, Technology, History and Reference.
3. Open **Books** and add book records. ISBN must be unique.
4. Open **Members** and register members. Member code and email must be unique.
5. Open **Circulation → Issue a book** to record a loan. Only active members and books with available copies can be selected.
6. Use **Mark returned** in Circulation when a book is returned.
7. Open **Reports** to review the collection and print the summary.

## Important notes
- This is a local development/learning project. Before public deployment, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=False`, configure `ALLOWED_HOSTS`, use HTTPS, configure static files, backups and database credentials securely.
- Do not use the development server for production hosting.
- Django authentication is used; create staff/superuser accounts only for trusted library staff.
- Deleting a book/member with an active loan is blocked. Deleting a category with books is blocked.
- The initial admin dashboard is empty until you add your own library data.
