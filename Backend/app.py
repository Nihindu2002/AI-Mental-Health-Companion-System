from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import joblib

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


@app.get("/")
def home():
    return {"message": "AI Mental Health Companion API is running"}


@app.post("/predict-emotion")
def predict_emotion(request: EmotionRequest):
    prediction = model.predict([request.text])[0]

    return {
        "input_text": request.text,
        "predicted_emotion": prediction
    }
