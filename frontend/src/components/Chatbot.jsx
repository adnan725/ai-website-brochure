//import crypto from "crypto";
import React, { useState, useRef, useEffect, use } from "react";

const BASE_URL = import.meta.env.VITE_BASE_URL || "http://localhost:5000";

export default function ChatbotWithUpload() {

  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  function getSessionId() {
    let sessionId = localStorage.getItem("session_id");

    if (!sessionId) {
      console.log("No session ID found, generating new one.");
      sessionId = crypto.randomUUID();
      localStorage.setItem("session_id", sessionId);
    }

    setSessionId(sessionId);
  }

  useEffect(() => {
    getSessionId();
  },)

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, sessionId: sessionId }),
      });

      const data = await res.json();
      console.log("API Response:", data); // Debugging line

      const botMessage = {
        sender: "bot",
        text: data.answer || "No response",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error getting response" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSend();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length) {
      setFiles((prev) => [...prev, ...droppedFiles]);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length) {
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (!files.length) return;

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      await fetch(`${BASE_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });
      alert("Files uploaded successfully");
      setFiles([]);
    } catch (err) {
      alert("Upload failed");
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.layout}>
        {/* LEFT: CHAT */}
        <div style={styles.chatContainer}>
          <div style={styles.header}>AI Chatbot</div>

          <div style={styles.messages}>
            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  ...styles.messageRow,
                  justifyContent:
                    msg.sender === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    ...styles.bubble,
                    ...(msg.sender === "user"
                      ? styles.userBubble
                      : styles.botBubble),
                  }}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {loading && <div style={styles.loading}>Bot is typing...</div>}
            <div ref={messagesEndRef} />
          </div>

          <div style={styles.inputContainer}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              style={styles.input}
            />
            <button onClick={handleSend} style={styles.button}>
              Send
            </button>
          </div>
        </div>

        {/* RIGHT: UPLOAD */}
        <div style={styles.uploadContainer}>
          <div style={styles.header}>Upload Documents</div>

          <div
            style={styles.dropZone}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current.click()}
          >
            <div style={styles.dropText}>
              Drag & Drop or Click to Select Files
            </div>
          </div>

          <input
            type="file"
            multiple
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />

          <div style={styles.fileList}>
            {files.map((file, index) => (
              <div key={index} style={styles.fileItem}>
                <span>{file.name}</span>
                <button
                  style={styles.removeButton}
                  onClick={() => removeFile(index)}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          <button onClick={handleUpload} style={styles.button}>
            Upload
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    backgroundColor: "#0f172a",
    height: "calc(100vh - 40px)",
    padding: "20px",
  },
  layout: {
    display: "flex",
    height: "100%",
    gap: "20px",
    maxWidth: "1400px",
    margin: "0 auto",
  },
  chatContainer: {
    flex: 7,
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#111827",
    border: "1px solid #1f2937",
    borderRadius: "14px",
    overflow: "hidden",
  },
  uploadContainer: {
    flex: 3,
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#111827",
    border: "1px solid #1f2937",
    borderRadius: "14px",
    padding: "16px",
    gap: "12px",
  },
  header: {
    padding: "16px",
    fontSize: "16px",
    fontWeight: "600",
    borderBottom: "1px solid #1f2937",
    color: "#e5e7eb",
    backgroundColor: "#020617",
  },
  messages: {
    flex: 1,
    padding: "20px",
    overflowY: "auto",
    backgroundColor: "#020617",
  },
  messageRow: {
    display: "flex",
    marginBottom: "12px",
  },
  bubble: {
    padding: "12px 16px",
    borderRadius: "14px",
    maxWidth: "60%",
    fontSize: "14px",
  },
  userBubble: {
    backgroundColor: "#2563eb",
    color: "#fff",
  },
  botBubble: {
    backgroundColor: "#1f2937",
    color: "#e5e7eb",
  },
  loading: {
    fontSize: "12px",
    color: "#6b7280",
  },
  inputContainer: {
    display: "flex",
    padding: "14px",
    borderTop: "1px solid #1f2937",
    backgroundColor: "#020617",
  },
  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "10px",
    border: "1px solid #374151",
    marginRight: "10px",
    backgroundColor: "#111827",
    color: "#e5e7eb",
  },
  button: {
    padding: "12px 18px",
    borderRadius: "10px",
    border: "none",
    backgroundColor: "#2563eb",
    color: "#fff",
    cursor: "pointer",
  },
  dropZone: {
    border: "2px dashed #374151",
    borderRadius: "12px",
    padding: "30px",
    textAlign: "center",
    color: "#9ca3af",
    cursor: "pointer",
    backgroundColor: "#020617",
  },
  dropText: {
    fontSize: "14px",
  },
  fileList: {
    maxHeight: "150px",
    overflowY: "auto",
  },
  fileItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "6px 10px",
    backgroundColor: "#020617",
    border: "1px solid #1f2937",
    borderRadius: "8px",
    marginBottom: "6px",
    color: "#e5e7eb",
    fontSize: "13px",
  },
  removeButton: {
    background: "transparent",
    border: "none",
    color: "#ef4444",
    cursor: "pointer",
  },
};