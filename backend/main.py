from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load backend/.env so TWILIO_* / DB_* variables are available via os.getenv().
load_dotenv()

from routes.email import router as email_router  # noqa: E402
from routes.otp import router as otp_router  # noqa: E402

app = FastAPI(title="Twilio Testing Portal")

# Part 8: dev-only CORS for the static frontend origins we actually use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(otp_router)
app.include_router(email_router)


@app.get("/")
def read_root():
    return {"message": "Twilio Testing Portal backend is running."}


@app.get("/health")
def health_check():
    return {"status": "ok"}
