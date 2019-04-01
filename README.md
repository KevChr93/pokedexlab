# Pokedex
A simple tutorial demonstrating the utilisation of Flask for building REST-based APIs


## Installation
1. Use virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install packages
```python
pip install -r requirements.txt
```

3. Run using Gunicorn
```python
gunicorn wsgi:app --reload
```
