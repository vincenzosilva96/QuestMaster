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

