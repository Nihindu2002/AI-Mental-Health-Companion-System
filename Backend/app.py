from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
import joblib
import numpy as np
import os
import warnings
import logging
import io

# Reduce TensorFlow and absl logging before TF is imported
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

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

TEXT_MODEL_PATH = BASE_DIR / "text-emotion-detection" / "models" / "emotion_model.pkl"
FACE_MODEL_PATH = BASE_DIR / "models" / "face_emotion_model.keras"

# Suppress sklearn InconsistentVersionWarning when unpickling older models
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass

text_model = joblib.load(TEXT_MODEL_PATH)

# Prepare for lazy TensorFlow import and reduce runtime logging
face_model = None

def get_face_model():
  
    global face_model

    if face_model is not None:
        return face_model

    # also reduce C++ level logs
    os.environ.setdefault("GLOG_minloglevel", "3")

    try:
        import tensorflow as tf
        try:
            tf.get_logger().setLevel('ERROR')
        except Exception:
            logging.getLogger('tensorflow').setLevel(logging.ERROR)
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Face emotion prediction requires TensorFlow. "
                "Install it in the running environment and restart the server."
            ),
        ) from exc

    face_model = tf.keras.models.load_model(FACE_MODEL_PATH)
    return face_model

face_class_names = [
    "angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"
]


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
    return {"message": "AI Mental Health Companion API is running"}


@app.post("/predict-emotion")
def predict_emotion(request: EmotionRequest, db: Session = Depends(get_db)):
    prediction = text_model.predict([request.text])[0]

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


@app.post("/predict-face-emotion")
async def predict_face_emotion(file: UploadFile = File(...)):
    image_bytes = await file.read()

    try:
        model = get_face_model()
    except HTTPException:
        # propagate 503 if TF is missing
        raise

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to process uploaded image: {exc}")

    img = img.resize((48, 48))

    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=-1)
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)

    predicted_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))

    return {
        "predicted_emotion": face_class_names[predicted_index],
        "confidence": confidence
    }