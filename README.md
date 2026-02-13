# 🎬 Movies Dataset — End-to-End Data Analysis & Visualization

A comprehensive data analysis project exploring **5,009 movies** from The Movie Database (TMDB), covering financial performance, genre trends, director/actor analytics, and investment profitability. The project spans Python-based EDA, a full ETL pipeline, and interactive Tableau dashboards.

[![Tableau Public](https://img.shields.io/badge/Tableau-Public%20Dashboard-blue?logo=tableau)](https://public.tableau.com/views/MovieIndustryAnalysis_17681128080920/OverviewDashboard)

---

## 📊 Project Overview

| Metric | Value |
|--------|-------|
| **Movies Analyzed** | 5,009 |
| **Industry Success Rate** | 54.50% |
| **Average ROI** | 298,361% |
| **Dashboards Built** | 4 Interactive Tableau Dashboards |
| **Visualizations** | 20+ Charts |

---

## 🏗️ Project Structure

```
Movies Dataset/
├── data/                         # Raw datasets
│   ├── tmdb_5000_movies.csv
│   ├── movie_metadata.csv
│   └── tmdb_5000_movies_mergedwith_movie_metadata.csv
├── notebooks/                    # Analysis scripts
│   ├── 01_exploratory_data_analysis.py   # Comprehensive EDA
│   ├── 02_full_data_merge.py             # Dataset merging
│   ├── 02_etl_tableau_prep.py            # ETL pipeline → 6 Tableau-ready tables
│   └── 03_funnel_analysis.py             # Investment-to-Profitability funnel
├── outputs/                      # Generated outputs
│   ├── tableau/                  # Tableau-ready CSV datasets
│   │   ├── movies_main.csv       # 5,009 movies with engineered features
│   │   ├── movies_by_genre.csv   # 14,884 genre-exploded rows
│   │   ├── director_performance.csv
│   │   ├── actor_performance.csv
│   │   ├── yearly_trends.csv
│   │   └── funnel_analysis.csv
│   └── *.png                     # EDA visualization outputs
├── docs/
│   └── Tableau_EDA_Guide.md      # Step-by-step Tableau guide
└── README.md
```

---

## 🔬 Analysis Pipeline

### Phase 1: Exploratory Data Analysis
- Financial distributions (Budget, Revenue, Profit)
- Genre performance & ROI analysis
- Director and actor rankings
- Content rating impact
- Social media engagement analysis
- Time trends (1970–2017)
- Correlation matrix of key variables

### Phase 2: ETL Pipeline
Transforms raw data into **6 Tableau-ready datasets** with engineered features:

| Output Table | Rows | Description |
|-------------|------|-------------|
| `movies_main.csv` | 5,009 | Core movie data with Budget Category, ROI Category, Era, Runtime Category |
| `movies_by_genre.csv` | 14,884 | Genre-exploded for multi-genre analysis |
| `director_performance.csv` | — | Aggregated director stats (revenue, avg ROI, success rate) |
| `actor_performance.csv` | — | Aggregated actor stats with star power metrics |
| `yearly_trends.csv` | — | Year-over-year industry trends |
| `funnel_analysis.csv` | — | Investment-to-profitability funnel stages |

### Phase 3: Investment-to-Profitability Funnel
An 8-stage funnel analyzing the movie investment pipeline:

```
Total Movies (5,009) → Has Budget → Generated Revenue → Recovered Investment
→ Profitable → Strong ROI (>100%) → High ROI (>300%) → Blockbuster (>1000%)
```

Includes bottleneck identification, segment breakdowns by genre/budget/era, and business recommendations.

---

## 📈 Tableau Dashboards

### Dashboard 1: Movie Industry Overview
> KPI cards, Budget vs Revenue scatter, Genre revenue breakdown, Release treemap

### Dashboard 2: Financial Performance
> Budget & Revenue distributions, Budget category performance, Genre ROI analysis

### Dashboard 3: People Analytics
> Top 15 Directors & Actors by revenue, Success rate analysis, Content rating performance

### Dashboard 4: Time Trends & Ratings
> Revenue vs Budget over time (area chart), IMDB & TMDB rating distributions

🔗 [**View on Tableau Public →**](https://public.tableau.com/views/MovieIndustryAnalysis_17681128080920/OverviewDashboard)

---

## 🔑 Key Findings

1. **Success Rate**: Only **54.5%** of movies are profitable
2. **Genre ROI**: Mystery and Horror genres deliver the highest ROI despite lower budgets
3. **Budget Sweet Spot**: Mid-budget films ($15M–$40M) offer the best risk-adjusted returns
4. **Director Impact**: Top directors like Christopher Nolan consistently outperform industry averages
5. **Industry Growth**: Average revenue has grown significantly since the 1990s, peaking around 2015
6. **The Funnel Drop**: The biggest loss occurs between "Generated Revenue" and "Recovered Investment"

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** (Pandas, NumPy, Matplotlib, Seaborn) | EDA & ETL |
| **Tableau Public** | Interactive dashboards & visualization |

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run the Analysis
```bash
# Step 1: EDA
python notebooks/01_exploratory_data_analysis.py

# Step 2: ETL Pipeline (generates Tableau-ready CSVs)
python notebooks/02_etl_tableau_prep.py

# Step 3: Funnel Analysis
python notebooks/03_funnel_analysis.py
```

### View Dashboards
Open the generated CSVs in `outputs/tableau/` with Tableau Public to explore the interactive dashboards.

---

## 📄 License

This project is licensed under the Apache 2.0 License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**David Ezieshi**
- [Tableau Public Profile](https://public.tableau.com/app/profile/david.ezieshi)
- [GitHub](https://github.com/ezieshie-stack)
