from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
import joblib

from database import SessionLocal, engine
from models import Base, MoodHistory

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Mental Health Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "text-emotion-detection" / "models" / "emotion_model.pkl"
model = joblib.load(MODEL_PATH)


class EmotionRequest(BaseModel):
    text: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "API is running"}


@app.post("/predict-emotion")
def predict_emotion(request: EmotionRequest, db: Session = Depends(get_db)):
    prediction = model.predict([request.text])[0]

    record = MoodHistory(
        text=request.text,
        emotion=prediction
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "input_text": record.text,
        "predicted_emotion": record.emotion,
        "created_at": record.created_at
    }


@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    records = db.query(MoodHistory).order_by(MoodHistory.id.desc()).all()
    return records
