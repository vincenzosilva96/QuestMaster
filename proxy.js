import express from "express";
import cors from "cors";
import fetch from "node-fetch";
import dotenv from "dotenv";
dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const HF_API_TOKEN = process.env.HF_API_TOKEN;
const HF_MODEL_URL = process.env.HF_MODEL_URL;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
//const HF_MODEL_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3-medium-diffusers";
app.post("/api/imagen", async (req, res) => {
  try {
    const prompt = req.body?.prompt;
    console.log("Prompt ricevuto:", prompt);

    if (!prompt) {
      return res.status(400).json({ error: "Prompt mancante nel body" });
    }

    const response = await fetch(HF_MODEL_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${HF_API_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ inputs: prompt })
    });

    const contentType = response.headers.get("content-type");
    console.log("Tipo di risposta HF:", contentType);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Errore Hugging Face:", errorText);
      return res.status(500).json({ error: errorText });
    }

if (contentType && contentType.includes("application/json")) {
  const data = await response.json();
  if (data.error) {
    console.error("Errore Hugging Face:", data.error);
    return res.status(500).json({ error: data.error });
  }
  return res.json(data);
}

    const arrayBuffer = await response.arrayBuffer();
    const base64 = Buffer.from(arrayBuffer).toString("base64");
    console.log("Immagine generata, invio al frontend.");
    res.json({ imageBase64: base64 });

  } catch (err) {
    console.error("Errore nel proxy:", err);
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/gemini", async (req, res) => {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req.body),
      }
    );

    const data = await response.json();
    res.json(data);
  } catch (err) {
    console.error("Errore proxy Gemini:", err);
    res.status(500).json({ error: "Errore durante la richiesta al modello" });
  }
});

app.listen(5500, () =>
  console.log("Proxy Hugging Face attivo su http://localhost:5500")
);
