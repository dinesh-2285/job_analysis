**# 🚀 Job Analytics & AI Resume Matcher Platform**

A comprehensive, end-to-end platform built with **Python** and **Streamlit** for advanced job market analysis and intelligent resume matching. This platform helps users analyze the job market, identify career trends, and find the best-fit jobs based on resume content.

---

## ✨ Key Features

### 📊 Interactive Analytics Dashboard
- Visualize trends in job streams, locations, in-demand skills, and top hiring companies.
- Built with **Plotly** for beautiful and interactive graphs.

### 🎯 AI-Powered Resume Matcher
- Upload a resume (PDF or DOCX).
- Extracts skills, education, and experience using NLP.
- Uses **hybrid scoring**: keyword matching + semantic similarity with Sentence-Transformers.

### 💡 Resume Improvement Suggestions
- Identify missing skills by comparing resume with top job listings.
- Suggest skills and improvements for better job matching.

### 🤖 Machine Learning Model Manager
- **Stream Predictor**: Predicts which job stream a job belongs to using `RandomForestClassifier`.
- **Demand Forecaster**: Forecasts future job demand using `GradientBoostingRegressor`.

### ⚙️ Automated Data Pipeline
- Cleans and validates raw job data from CSV files.
- Logs all processing events for traceability and debugging.

---

## 🛠️ Technology Stack

| Layer | Tech |
|-------|------|
| Backend & App | Python, Streamlit |
| Data | Pandas, NumPy, SQLite |
| ML Models | Scikit-learn |
| NLP | NLTK, Sentence-Transformers |
| Resume Parsing | PyMuPDF, python-docx |
| Web Scraping | Selenium, BeautifulSoup4 |
| Visualizations | Plotly, Seaborn |

---

## 📂 Project Structure

```
job_analysis/
├── backend/                     # FastAPI backend & database logic
├── frontend/                    # Streamlit multi-page UI
├── ml/                          # ML pipelines & model artifacts
├── infra/                       # Docker and deployment configs
├── data/                        # Raw/processed data (optional)
├── tests/                       # Pytest suite
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Local orchestration
├── Makefile                     # Common commands
└── requirements.txt             # Python dependencies
```

---

## ✅ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/job_analysis.git
cd job_analysis
````

### 2. Create a virtual environment

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the App

### Backend API
```bash
uvicorn backend.app.main:app --reload
```

### Frontend
```bash
streamlit run frontend/app.py
```

### Docker Compose
```bash
docker-compose up --build
```

Open your browser at [http://localhost:8501](http://localhost:8501)

---

## 📖 How to Use

1. **Home Page** – Overview of platform features.
2. **Analytics Dashboard** – Explore job trends, skill demands, top companies.
3. **Resume Matcher** – Upload a resume and get job matches + improvement tips.
4. **ML Models** – Predict job streams or forecast job demand.
5. **Job Search** – Browse real-time job listings from the database.

### 🔐 Default Login
Use `admin / admin123` for the default demo account.

---

## 📌 TODOs / Future Work

* [ ] Add real-time job data fetching using LinkedIn/Glassdoor APIs.
* [ ] Deploy using Streamlit Community Cloud / Docker / Render.
* [ ] Add user authentication for personalized dashboards.
* [ ] Build AI-generated resumes based on selected job profiles.
* [ ] Integrate skill co-occurrence heatmaps.

---

## 🧠 Credits

Developed with ❤️ by \[Your Name]
If you like this project, ⭐ star it and share it!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```

---

Let me know if you want:
- A `LICENSE` file.
- A version with deploy instructions (e.g., Docker, Streamlit Cloud).
- Logo, banners, or badges added to the top of the README.
```



<img width="1512" height="637" alt="newplot (1)" src="https://github.com/user-attachments/assets/03e01446-fd64-4f2a-b3a8-411538add108" />
<img width="546" height="450" alt="newplot (2)" src="https://github.com/user-attachments/assets/242deaf6-2064-472f-86ad-39e306692f27" />
<img width="546" height="450" alt="newplot (3)" src="https://github.com/user-attachments/assets/e8e93cd2-ca0c-424f-bd0f-5e2bfaf57c25" />

<img width="1918" height="863" alt="Screenshot 2025-07-25 134832" src="https://github.com/user-attachments/assets/ff84b6bf-c24c-4c8c-8bb4-fe4ec04dd7d6" />
