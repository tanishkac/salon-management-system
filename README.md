# salon-management-system
python mpr

# 1. Prerequisites
- Python 3.8+
- MySQL Server
- Git (for collaboration)

# 2. Database Setup
### 1. Create database (one-time)
mysql -u root -p -e "CREATE DATABASE salon_management;"

### 2. Import schema
mysql -u root -p salon_management < schema.sql

# 3. Configure Environment
### 1. Copy the example env file
cp .env.example .env

### 2. Edit with your credentials
nano .env  # or use any text editor

# 4. Install Dependencies
pip install -r requirements.txt

# 5. Run the Application
python salon_app.py
