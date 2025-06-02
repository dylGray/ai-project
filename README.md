# Priority Pitch for RPG (Internal)

> **Note:** This repository is intended for internal use by Revenue Path Group (RPG) team members only.

---

## 1. Overview

**Priority Pitch for RPG** is an internal web application built to help our sales team analyze and refine elevator pitches submitted by users. Leveraging RPG’s proprietary sales methodology and the OpenAI LLM (via the OpenAI API), this tool provides data-driven feedback—highlighting strengths, identifying gaps, and suggesting improvements in real time.

Key objectives:
- Automate initial pitch reviews to save time in coaching.
- Maintain consistency with RPG’s established sales framework.
- Provide actionable, AI-powered feedback to users immediately.

---

## 2. Tech Stack

- **Frontend**  
  - HTML  
  - Tailwind CSS  
  - JavaScript

- **Backend**  
  - Flask (Python 3.x)

- **Data Storage**  
  - Firebase (Firestore) for storing user submissions, feedback history, and metadata.

- **API Integration**  
  - **OpenAI API (GPT-4 or higher)**: Main LLM for generating analysis and recommendations.  
    - Developers must provide their own OpenAI API key via environment variables (see “Environment Setup” below).  
  - **Web Speech API**: Optional browser-based speech-to-text (no server-side secret required).

- **Environment Management**  
  - `python-dotenv` to load environment variables from a `.env` file.

- **Deployment**  
  - Vercel (Front + API server) or any platform supporting Flask deployments.  
  - (We currently host this internally under the `priority-pitch-rpg.vercel.app` domain.)

---

## 3. Features

1. **User Submission Form**  
   - Simple UI where users paste or speak (via Web Speech API) their elevator pitch.  
   - Supports both text input and voice dictation (Chrome, Edge, and other Web Speech API–compatible browsers).

2. **AI-Powered Analysis**  
   - Pitch text is sent to the Flask backend, which forwards it to the OpenAI API alongside our proprietary RPG sales methodology context.  
   - Returns a structured breakdown:  
     - Alignment with RPG’s core message pillars (e.g., “Pain,” "Threat,” “Belief Statement”).  
     - Tone and clarity assessment.  
     - Custom scorecard highlighting where the pitch excels or needs work.

3. **Environment & Security**  
   - All sensitive keys (Firebase service account, OpenAI API key) are loaded via `python-dotenv`.  
   - No API keys are checked into source control.  
   - Access to this repo and any deployed dashboards is restricted to RPG’s internal network users only.