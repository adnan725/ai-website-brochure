import { useState } from "react";

export default function SummaryTab() {
  const [url, setUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!url || !question) return;

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://127.0.0.1:5000/api/summarize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ url, question })
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
      <input
        type="text"
        placeholder="Enter website URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
      />

      <textarea
        placeholder="Ask your question about the website..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={4}
        style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
      />

      <button onClick={handleSubmit}>
        {loading ? "Loading..." : "Summarize"}
      </button>

      {response && (
        <div style={{ marginTop: "20px" }}>
          <h3>Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </>
  );
}