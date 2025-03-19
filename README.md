# Speedy Transfers

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