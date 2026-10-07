# 🌱 TouchGrass-AI

TouchGrass-AI is a local-first AI outdoor activity guide.

It uses an open-weight AI model running locally through Ollama
to generate personalized outdoor activity plans.

The goal is simple:

> Spend less time looking at a screen and more time outside.

---

## ✨ Features

- Local AI inference
- Ollama integration
- Gemma model
- FastAPI backend
- HTML/CSS/JavaScript frontend
- No React
- No cloud LLM API
- No API key required
- Personalized outdoor plans
- Activity recommendations
- Safety suggestions
- What-to-bring checklist
- Offline-friendly guidance

---

## 🧠 Architecture

```text
Browser
   |
   | HTTP
   v
FastAPI
   |
   | localhost
   v
Ollama
   |
   v
gemma4:e2b
   |
   v
Outdoor Activity Guide
