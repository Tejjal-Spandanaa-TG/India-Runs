# HireMind AI — Recruiter Intelligence & Candidate Ranking Engine

HireMind AI is an end-to-end intelligent candidate retrieval, filtering, and ranking system developed for the Redrob Intelligent Candidate Discovery & Ranking Challenge. 

The system processes a pool of **100,000 candidates** in under 6 minutes on a standard CPU, filters out data anomalies (honeypots) and consulting lifers, and outputs a highly precise, semantically matched shortlist of the top 100 candidates for a **Senior AI Engineer — Founding Team** role.

It features a premium **Recruiter Dashboard** (`dashboard.html`) to visualize the shortlist and an **Interactive Resume Uploader** (`upload.html`) to rank custom external resumes in real-time.

---

## 🚀 Key Features

* **Dual-Pass CPU-Optimized Pipeline**: Filters 100,000 candidates down to ~7,800 relevant profiles using fast word-boundary regex before running the neural network. This allows local semantic embedding computations to finish in under 6 minutes on a standard CPU.
* **0% Honeypot Trap Rate**: A strict validation layer automatically flags and removes anomalous profiles (impossible job tenures, active dates prior to signup dates, and skill duration conflicts).
* **Targeted Business Filters**: Excludes consulting lifers (candidates whose entire career histories are at service-based firms like TCS, Infosys, Wipro, Accenture, Cognizant, etc.) to target core startup-ready engineers.
* **Interactive Recruiter Dashboard (`dashboard.html`)**: A beautiful, standalone glassmorphism dark-mode UI containing the top 100 candidates, timeline components, AI reasoning statements, and live weights sliders to re-calculate rankings in the browser.
* **Client-Side Resume Uploader (`upload.html`)**: A drag-and-drop resume parser that extracts text from PDF, Word (DOCX), and text files entirely in-browser (using PDF.js and Mammoth.js). It scores custom resumes against editable job descriptions on the fly.

---

## 📂 Project Structure

* `rank.py`: The core python execution script that loads, filters, and ranks the 100K candidates offline.
* `download_model.py`: Helper script to download and cache the sentence-transformer model (`all-MiniLM-L6-v2`) locally to bypass internet access checks.
* `build_ui_data.py`: Compiles the top 100 candidate profiles from the dataset and outputs a self-contained, data-injected recruiter UI.
* `dashboard.html`: The main recruiter intelligence dashboard.
* `upload.html`: The custom resume uploader and matcher workspace.
* `submission.csv`: The validated output list containing the top 100 candidate IDs, ranks, scores, and custom fact-based AI reasonings.
* `submission_metadata.yaml`: The mandatory competition metadata details.
* `requirements.txt`: Python package dependencies.
* `.gitignore`: Excludes large datasets and binary weights files from Git tracking.

---

## 🛠️ Setup & Installation

### 1. Install Dependencies
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 2. Download the AI Model
Since the evaluator runs completely network-free, download and cache the transformer model locally by running:
```bash
python download_model.py
```

### 3. Run the Candidate Ranking Pipeline
To run the ranking engine on the `candidates.jsonl` dataset and output the final `submission.csv`:
```bash
python rank.py
```

### 4. Build/Regenerate the Dashboard
To update the Recruiter Dashboard with the newly computed scores and reasoning:
```bash
python build_ui_data.py
```

---

## 🖥️ Viewing the Interfaces

The visual dashboards are **100% self-contained and run offline** directly in the web browser. You do not need to host a local server.

1. **Recruiter Dashboard**: 
   * Open [dashboard.html](dashboard.html) in your browser.
   * Search candidates, toggle notice periods/locations, and adjust the weight sliders to see candidates re-sort in real time.
2. **Resume Matcher**:
   * Open [upload.html](upload.html) in your browser (or click the **"Upload Resumes"** link in the dashboard header).
   * Drag and drop candidate resumes to extract text, view match percentages, check strengths/gaps, and adjust job requirements.
