# Geply — AI Interview Platform

> Built by **Prasanth Ragupathy** at GEP Worldwide

## Overview
Geply is an AI-powered interview platform that automates candidate screening using voice AI. Recruiters upload JDs and resumes, candidates receive invite links and complete voice interviews with an AI agent powered by Deepgram + Groq.

## Tech Stack
- **Backend:** FastAPI + SQLAlchemy (async) + SQLite + Groq (Llama 3.1 8B)
- **Frontend:** React 18 + Vite + TailwindCSS
- **Voice AI:** Deepgram Voice Agent (STT + LLM + TTS)
- **Auth:** JWT tokens

## Features
- Recruiter portal: job management, resume upload, invite generation
- Candidate self-scheduling
- AI voice interviews with barge-in support
- Real-time proctoring (tab switch, copy/paste detection)
- Automated report generation with scoring
- Notification system

## Quick Start
\\\ash
# Backend
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
py -3.12 -m uvicorn app.main:app --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev
\\\

## Author
**Prasanth Ragupathy**
GEP Worldwide — Talent Acquisition Innovation
