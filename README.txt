QuestMaster is an experimental AI-driven system that automatically generates interactive narrative adventures using Google Gemini, Fast Downward (PDDL planner), and Hugging Face image generation models.

The project combines natural language generation, automated planning, and procedural storytelling to create dynamic quests where each decision influences the story’s outcome.

It consists of three main components:

-Phase 1 (Python) — Uses Gemini to generate coherent PDDL domain/problem files and validate them via Fast Downward.

-Proxy Server (Node.js + Express) — Acts as a middleware to securely communicate with Gemini and Hugging Face APIs.

-Phase 2 Web Application (HTML/JS) — Displays the generated narrative, available actions, and AI-generated scene illustrations.

-The result is an interactive story engine capable of producing adaptive adventures with logical consistency between narrative events and the underlying planning structure.





How to configure

The project uses a .env file to securely store API keys and other sensitive configuration variables.
This file is ignored by GitHub for security reasons.

Create a file named .env in the root directory of the project and add the following line:

GEMINI_API_KEY="your_gemini_api_key_here"

Install package:

pip install google-generativeai python-docx

npm install express cors node-fetch dotenv

(1)Run Phase 1 (PDDL Generation with Gemini)
python run_phase1.py

(2)Start the backend proxy
node proxy.js
You should see:

Proxy Hugging Face running at http://localhost:5500

(3)Launch the Web Application

