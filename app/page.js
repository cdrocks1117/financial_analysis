"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    setLoading(true);
    setMessage("Processing PDF...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Server error while processing PDF");
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Financial_Output.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();

      setMessage("Excel downloaded successfully!");
    } catch (error) {
      console.error(error);
      setMessage("Error processing PDF.");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>Financial Statement Research</h1>

      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Process Financial Statement"}
      </button>

      <p>{message}</p>
    </div>
  );
}