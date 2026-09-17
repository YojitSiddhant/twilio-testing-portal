# Twilio Testing Portal

A learning/testing project for understanding how Twilio works. This is **Phase 0**:
project setup only. No Twilio features are implemented yet.

Planned features for later phases (not yet implemented):

- OTP / Twilio Verify
- SMS
- WhatsApp
- Email
- Webhooks / delivery status
- Communication logs
- Voice calling (last)

## Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python, FastAPI
- **Database:** MySQL
- **Future external service:** Twilio

## Project Structure

```
twilio-testing-portal/
├── frontend/       # Static HTML/CSS/JS frontend
├── backend/        # FastAPI backend
├── .env.example    # Environment variable template
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Create and activate a Python virtual environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r ../requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your local MySQL values:

```bash
cp ../.env.example ../.env
```

Edit `.env` with your MySQL credentials. Leave the Twilio fields blank for now —
they are placeholders for a later phase.

### 4. Start the FastAPI backend

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 5. Open the frontend

Open `frontend/index.html` directly in your browser, or serve it with a simple
static server, e.g.:

```bash
cd frontend
python3 -m http.server 5500
```

Then visit `http://127.0.0.1:5500`.

### 6. Test the health endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "ok"}
```

## Notes

- Twilio functionality (OTP, SMS, WhatsApp, Email, Voice, webhooks) will be
  implemented incrementally in later phases.
- Twilio credentials must never be committed or placed in frontend code — they
  will only ever live in backend environment variables.
