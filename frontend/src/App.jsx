import { useState } from "react";
import axios from "axios";

function App() {
  const [text, setText] = useState("");
  const [emotion, setEmotion] = useState("");

  const analyzeEmotion = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/predict-emotion", {
        text: text,
      });

      setEmotion(response.data.predicted_emotion);
    } catch (error) {
      console.error(error);
      setEmotion("Error connecting to backend");
    }
  };

  return (
    <div style={{ padding: "40px", maxWidth: "600px", margin: "auto" }}>
      <h1>AI Mental Health Companion</h1>

      <textarea
        rows="6"
        style={{ width: "100%", padding: "10px" }}
        placeholder="Write how you feel today..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button onClick={analyzeEmotion} style={{ marginTop: "15px" }}>
        Analyze Mood
      </button>

      {emotion && (
        <h2>
          Predicted Emotion: {emotion}
        </h2>
      )}
    </div>
  );
}

export default App;