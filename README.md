<div align="center">

# 🌿 Sustainability Scoring Dashboard

<p>A lightweight Flask application that scores consumer products for sustainability, stores results in SQLite, and visualizes insights on a modern dashboard.</p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img alt="Flask" src="https://img.shields.io/badge/Flask-black?style=for-the-badge&logo=flask&logoColor=white"/>
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img alt="Chart.js" src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white"/>
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
</p>
</div>

---

## ✨ Features

* **REST API:** Simple and powerful endpoints for `POST /score`, `GET /history`, and `GET /score-summary`.
* **Dynamic Dashboard:** Features a bar chart for recent scores, a doughnut chart for ratings, and a summary of key performance indicators.
* **AI Suggestions:** An optional panel that explains the "why" behind a score when a user clicks on a chart bar.
* **Standalone Submit Tool:** A clean, validation-rich HTML form to post new data without needing external API clients like Postman.
* **Zero Build Frontend:** Built with pure HTML, CSS, and JavaScript for maximum portability and ease of hosting.

---

## 🚀 Quick Start (Local)

### Prerequisites

* Python 3.10+
* `pip` and `venv` (or a similar virtual environment tool)

### Setup & Run

1.  **Clone the repository and create a virtual environment:**
    ```bash
    git clone [https://github.com/GulshanMS/Assignmnet-Sustainability-Score.git](https://github.com/GulshanMS/Assignmnet-Sustainability-Score.git)
    cd Assignmnet-Sustainability-Score
    python -m veny .venv
    ```

2.  **Activate the environment:**
    ```bash
    # Windows
    .venv\Scripts\activate
    
    # macOS / Linux
    source .venv/bin/activate
    ```

3.  **Install all dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python src/app.py
    ```
    > The app will be running at `http://127.0.0.1:5000/`

### First Use

To see the dashboard populate with data:
1.  Navigate to the **Submit Tool** at `/static/submit.html`.
2.  Create and submit one or two products using the form.
3.  Visit the main **Dashboard** at `/` to see the charts update in real-time.
    > If charts don't appear, do a hard refresh (`Ctrl+F5` or `Cmd+Shift+R`).

---

## 📂 Repository Structure

```plaintext
/
├── data/
│   └── app.db            # SQLite database (created on first write)
├── src/
│   └── app.py            # Flask app, API routes, and scoring logic
├── static/
│   ├── index.html        # Main dashboard page
│   ├── submit.html       # Frontend form to POST /score
│   ├── style.css         # Base application styles
│   └── ...               # Other UI styles and JS files
└── requirements.txt      # Python dependencies
