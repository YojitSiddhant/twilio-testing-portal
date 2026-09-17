from fastapi import FastAPI

app = FastAPI(title="Twilio Testing Portal")


@app.get("/")
def read_root():
    return {"message": "Twilio Testing Portal backend is running."}


@app.get("/health")
def health_check():
    return {"status": "ok"}
