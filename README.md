# Document Scanner

A Django-based document scanner application.

## Setup Instructions

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Run the development server:
```bash
python manage.py runserver
```

## Features
- Document scanning and storage
- PDF and image file support
- Document metadata management
- REST API endpoints
