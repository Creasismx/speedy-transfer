# Speedy Transfers
# Speedy Transfer

A simple web application for fast and secure file transfers.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000`

## Features

- Simple file upload interface
- Fast transfer capabilities
- Secure handling of files

## Project Structure
## Environment

To start the application it is necessary to include the .env file

DB_NAME=
DB_USER=root
DB_PASSWORD=""
DB_HOST="localhost"
DB_PORT=3306


## Build

```shell
cd templates/assets
npm install
npm run watch
```


# Setting Up a Virtual Environment in Linux and Windows

A virtual environment helps keep dependencies isolated for different projects. Below are the steps to create and use a virtual environment named `venv` on Linux and Windows.

---

## Linux (Ubuntu, Fedora, etc.)

### **1. Install Python and Virtual Environment Module**
Ensure Python is installed:
```bash
python3 --version
```
If not installed, use:
```bash
sudo apt install python3 python3-venv  # Ubuntu/Debian
sudo dnf install python3 python3-venv  # Fedora
```

### **2. Create a Virtual Environment**
Navigate to your project directory and run:
```bash
python3 -m venv venv
```

### **3. Activate the Virtual Environment**
```bash
source venv/bin/activate
```
After activation, you should see `(venv)` in your terminal prompt.

### **4. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **5. Deactivate the Virtual Environment**
To exit, run:
```bash
deactivate
```

---

## Windows

### **1. Install Python and Virtual Environment Module**
Ensure Python is installed:
```powershell
python --version
```
If not installed, download it from [Python.org](https://www.python.org/downloads/) and install it, making sure to check "Add Python to PATH" during installation.

### **2. Create a Virtual Environment**
Navigate to your project directory and run:
```powershell
python -m venv venv
```

### **3. Activate the Virtual Environment**
Run the following in PowerShell:
```powershell
venv\Scripts\Activate
```
For **Command Prompt (cmd.exe)**:
```cmd
venv\Scripts\activate.bat
```
After activation, `(venv)` should appear in the terminal prompt.

### **4. Install Dependencies**
```powershell
pip install -r requirements.txt
```
# Speedy Transfer - Puerto Vallarta Transportation Service

A Django-based web application for booking transportation services in Puerto Vallarta, Mexico.

## Project Overview

Speedy Transfer is a transportation booking platform that allows users to:
- Book one-way or round-trip transfers between Puerto Vallarta Airport and various destinations
- Compare different vehicle options and prices
- Make reservations and payments

## Technology Stack

- **Framework**: Django 3.2
- **Database**: PostgreSQL
- **Frontend**: 
  - HTML/CSS/JavaScript
  - Tailwind CSS for styling
  - DaisyUI components
  - Swiper for sliders/carousels

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/speedy-transfer.git
   cd speedy-transfer
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your database credentials based on the `.env.example` file

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Visit http://127.0.0.1:8000 in your web browser

### Using Docker

Alternatively, you can use Docker Compose:
### **5. Deactivate the Virtual Environment**
To exit, run:
```powershell
deactivate
```

---

## Ignoring `venv` in Git
To avoid committing the virtual environment, add this to `.gitignore`:
```
venv/
```

---

Now your virtual environment is set up and ready to use! 🚀





## Running makemigrations

```shell
python manage.py makemigrations
```

## Running the migrations

```shell
python manage.py migrate
```

## Use django shell

```shell
python manage.py shell
```

## Create super user

```shell
python manage.py createsuperuser
```

## Create translations

```shell
django-admin makemessages -l en

```

## Create compile messages

```shell
django-admin compilemessages --ignore apps

```

## Start the livereload serve
```shell
python manage.py livereload
```

## Run de app locally
```shell
python manage.py runserver 0.0.0.0:8000
```