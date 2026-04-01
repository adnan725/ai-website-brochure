import { useState } from "react";

export default function AskTab() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question) return;

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://127.0.0.1:5000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question })
      });

      const data = await res.json();
      setResponse(data.answer);
    } catch (err) {
      console.error(err);
      setResponse("Something went wrong");
    }

    setLoading(false);
  };

  return (
    <>
      <textarea
        placeholder="Ask anything..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={4}
        style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
      />

      <button onClick={handleAsk}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {response && (
        <div style={{ marginTop: "20px" }}>
          <h3>Answer:</h3>
          <p>{response}</p>
        </div>
      )}
    </>
  );
}