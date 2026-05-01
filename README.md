# Invest Like Netaji 🇮🇳

Invest Like Netaji is a full-stack platform designed to provide transparency into the financial portfolios of Indian politicians. By scraping official election affidavits from MyNeta, the platform visualizes asset distribution, investment categories, and liability data in an intuitive dashboard.

## 🚀 Features

- **Automated Scraper**: Robust Selenium-based scraper for MyNeta.info that extracts summary assets and detailed investment breakdowns.
- **Wealth Dashboard**: Interactive UI to search for politicians and view their financial profiles.
- **Data Visualization**: Categorized asset distribution using Pie Charts.
- **Investment Deep Dive**: Granular view of bank deposits, stocks, insurance policies, and more.
- **Authentication**: Secure Google Login via Firebase.
- **Cloud Backend**: Supabase integration for persistent storage and real-time updates.

---

## 🛠 Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons.
- **Backend**: Flask (Python), Selenium, BeautifulSoup4.
- **Database**: Supabase (PostgreSQL).
- **Auth**: Firebase Authentication.

---

## 📦 Installation & Setup

### 1. Prerequisites
- Node.js (v18+)
- Python (v3.11+)
- Firefox Browser (for Selenium WebDriver)

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Environment Variables
# Create a .env file in the backend folder:
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Setup (Supabase)
Run the SQL found in `supabase_schema.sql` in your Supabase SQL Editor to create the necessary tables (`politicians` and `investments`).

### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Setup Environment Variables
# Create a .env.local file in the frontend folder:
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

---

## 🏃‍♂️ Running the Application

### Start the Backend
```bash
cd backend
source venv/bin/activate
python3 app.py
```
The API will be available at `http://localhost:5000`.

### Start the Frontend
```bash
cd frontend
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

---

## 🕷 Scraping Data

To scrape a new candidate, update the `test_url` in `backend/scraper.py` and run:
```bash
cd backend
source venv/bin/activate
python3 scraper.py
```
The data will be automatically cleaned and upserted into your Supabase instance.

---

## 📄 License
This project is for educational purposes. Data is sourced from MyNeta.info.
