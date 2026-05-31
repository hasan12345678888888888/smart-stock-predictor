# 📦 Smart Stock-Out Predictor

> **Hamdard University — Artificial Intelligence Lab**  
> Faculty of Engineering Sciences and Technology, Karachi, Pakistan

**Team:**
- Inayatullah (3076-2023)
- Muhammad Hassan Raza (2903-2023)
- Ahsan Ali (3112-2023)

---

## 🧠 Project Overview

The **Smart Stock-Out Predictor** is a Streamlit-based AI decision-support tool for small retail shops in Pakistan. It uses a **Model-Based Goal-Driven AI Agent** to:

- Monitor current inventory levels
- Analyze 10-day historical sales patterns
- Predict when each product will run out
- Issue automated alerts with reorder recommendations

---

## 📁 Project Structure

```
smart_stock_predictor/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── agent/
│   ├── __init__.py
│   └── stock_agent.py        # AI Agent (Model-Based Goal-Driven)
│
├── utils/
│   ├── __init__.py
│   ├── data_processor.py     # Data loading, cleaning, mean imputation
│   └── visualizer.py         # Plotly charts & dashboards
│
└── data/
    └── sample_inventory.csv  # Sample data for testing
```

---

## 🚀 Running Locally

### Step 1: Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-stock-predictor.git
cd smart-stock-predictor
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (Free Hosting)

1. Push this project to a **public GitHub repository**
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **"New app"** → Select your repo
5. Set **Main file path** to `app.py`
6. Click **Deploy** → Your app goes live in ~2 minutes!

Your app URL will be: `https://YOUR_USERNAME-smart-stock-predictor.streamlit.app`

---

## 📊 Features

| Feature | Description |
|---|---|
| 🤖 AI Agent | Model-Based Goal-Driven agent evaluates stock vs thresholds |
| 📈 Sales Trends | 10-day daily consumption line charts |
| 📊 Stock Duration | Horizontal bar chart with critical/warning zones |
| 🔮 Depletion Forecast | Projected stock levels for next 20 days |
| 🚨 Smart Alerts | Auto-generated alerts with reorder quantities |
| 📤 CSV Upload | Upload your own shop inventory data |
| ⚙️ Configurable | Adjustable critical/warning day thresholds |

---

## 📋 CSV Upload Format

To use your own data, upload a CSV with this format:

```csv
product,day_1,day_2,...,day_10,current_stock
Tapal Tea,5,4,6,5,7,4,6,5,7,6,12
Pepsi 1.5L,10,8,12,9,11,10,13,8,10,12,24
```

- `product`: Product name
- `day_1` to `day_10`: Units sold each day (missing values are auto-filled)
- `current_stock`: Current units in stock

---

## 🔧 Technical Concepts Implemented

- **Data Wrangling**: Pandas DataFrames, missing value detection, mean imputation
- **AI Agent**: Model-Based Goal-Driven agent with perception, internal model, goal evaluation
- **Visualization**: Plotly interactive charts (line, bar, area)
- **Prediction**: Weighted consumption velocity → days-until-depletion formula
- **Alerts**: Rule-based alert generation with reorder quantity recommendations
