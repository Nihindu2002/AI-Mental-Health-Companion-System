import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [text, setText] = useState("");
  const [emotion, setEmotion] = useState("");
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    const response = await axios.get("http://127.0.0.1:8000/history");
    setHistory(response.data);
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const analyzeEmotion = async () => {
    const response = await axios.post("http://127.0.0.1:8000/predict-emotion", {
      text,
    });

    setEmotion(response.data.predicted_emotion);
    setText("");
    fetchHistory();
  };

  return (
    <div style={{ padding: "40px", maxWidth: "700px", margin: "auto" }}>
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

      {emotion && <h2>Predicted Emotion: {emotion}</h2>}

      <h2>Mood History</h2>

      {history.map((item) => (
        <div key={item.id} style={{ border: "1px solid #ccc", padding: "10px", marginTop: "10px" }}>
          <p><b>Text:</b> {item.text}</p>
          <p><b>Emotion:</b> {item.emotion}</p>
          <p><b>Date:</b> {new Date(item.created_at).toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
}

export default App;