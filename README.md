# 🎬 Movies Dataset — End-to-End Data Analysis & Visualization

## 📌 Problem Statement

The movie industry generates billions of dollars annually, yet **nearly half of all films fail to recoup their investment**. Studios, investors, and analysts face a critical question:

> **What separates a profitable movie from a financial failure?**

This project set out to answer that question by analyzing **5,009 movies** from The Movie Database (TMDB), spanning nearly five decades (1970–2017). The goal was to uncover the financial, creative, and market factors that drive movie profitability — and to present those insights through interactive dashboards that a studio executive or analyst could actually use.

---

## 🎯 Objectives

1. **Explore** the raw data to understand distributions, patterns, and anomalies in movie financials
2. **Transform** messy, multi-source data into clean, analysis-ready datasets
3. **Analyze** profitability through a structured Investment-to-Profitability funnel
4. **Visualize** findings in interactive Tableau dashboards for stakeholder consumption

---

## 📊 What Was Done

This project followed a structured **3-phase data analysis pipeline**, taking raw CSV files and turning them into actionable business intelligence.

### Phase 1: Exploratory Data Analysis (EDA)

**Script:** [`01_exploratory_data_analysis.py`](notebooks/01_exploratory_data_analysis.py) (998 lines)

The first step was understanding the data. The EDA phase examined the merged dataset across multiple dimensions:

| Analysis Area | What Was Examined |
|---------------|-------------------|
| **Data Quality** | Missing data patterns across 42 columns; identified that `gross`, `budget`, and several metadata fields had significant gaps |
| **Financial Distributions** | Budget, Revenue, and Profit distributions — revealed extreme right-skew (a few blockbusters dominate, most films earn modestly) |
| **Budget vs Revenue** | Scatter analysis with break-even line — found that **54.5%** of movies fall above break-even |
| **Genre Performance** | Revenue, ROI, and success rates across all major genres — Drama has the most films, but Mystery and Horror deliver the highest ROI |
| **Director & Actor Rankings** | Top 15 directors and actors by total revenue, average ROI, and consistency |
| **Content Ratings** | How PG-13, R, PG, and G-rated films compare on financial metrics |
| **Social Media & Popularity** | Facebook likes (movie, cast, director) correlated with box office performance |
| **Time Trends** | Revenue and budget growth from 1970 to 2017, showing industry inflation and peak years |
| **Correlation Analysis** | Heatmap of all numerical variables — strongest correlations: Budget↔Revenue (0.73), Vote Count↔Revenue (0.78) |

**Output:** 16 PNG visualizations saved to `outputs/`

---

### Phase 2: ETL Pipeline (Extract, Transform, Load)

**Script:** [`02_etl_tableau_prep.py`](notebooks/02_etl_tableau_prep.py) (658 lines)

Raw data is messy. This phase cleaned and transformed it into **6 structured, Tableau-ready CSV files** with engineered features.

#### How the Data Was Transformed:

**1. Financial Cleaning**
- Combined `revenue` and `gross` columns (using revenue first, gross as fallback)
- Calculated derived metrics: `Profit = Revenue - Budget`, `ROI = (Profit / Budget) × 100`
- Flagged `Is Profitable` (binary: 1 if Revenue > Budget)

**2. Categorical Feature Engineering**
- **Budget Category:** Low Budget (<$15M) → Mid Budget ($15M–$40M) → High Budget ($40M–$100M) → Blockbuster ($100M+)
- **ROI Category:** Flop (ROI < 0%) → Low (0–100%) → Medium (100–300%) → High (300–1000%) → Mega-Hit (1000%+)
- **Rating Category:** Poor (<4) → Below Average (4–5.5) → Average (5.5–7) → Good (7–8) → Excellent (8+)
- **Era:** Classic (pre-1980) → 1980s → 1990s → 2000s → 2010s
- **Runtime Category:** Short (<90min) → Standard (90–120min) → Long (120–150min) → Epic (150min+)

**3. Genre Parsing**
- Parsed JSON-formatted genre strings into clean lists
- Exploded multi-genre movies into individual rows (5,009 movies → 14,884 genre-rows)
- Assigned `Primary Genre` (first listed genre)

**4. Social Media Metrics**
- Calculated `Total Social Engagement` = Movie FB Likes + Cast FB Likes + Director FB Likes
- Categorized engagement: Low → Medium → High → Viral

#### Output Tables:

| Table | Rows | Purpose |
|-------|------|---------|
| [`movies_main.csv`](outputs/tableau/movies_main.csv) | 5,009 | Core dataset with all engineered features |
| [`movies_by_genre.csv`](outputs/tableau/movies_by_genre.csv) | 14,884 | One row per movie-genre combination |
| [`director_performance.csv`](outputs/tableau/director_performance.csv) | 2,300+ | Aggregated director stats (avg ROI, success rate, total revenue) |
| [`actor_performance.csv`](outputs/tableau/actor_performance.csv) | 4,500+ | Aggregated actor stats with star power metrics |
| [`yearly_trends.csv`](outputs/tableau/yearly_trends.csv) | 47 | Year-over-year industry trends (1970–2017) |
| [`funnel_analysis.csv`](outputs/tableau/funnel_analysis.csv) | 5,009 | Each movie tagged with its funnel stage |

---

### Phase 3: Investment-to-Profitability Funnel Analysis

**Script:** [`03_funnel_analysis.py`](notebooks/03_funnel_analysis.py) (614 lines)

This phase introduced a **creative, business-style funnel** — treating movie investment like a sales pipeline to identify where money gets lost.

#### The 8-Stage Funnel:

```
Stage 1: Total Movies (5,009)
  ↓ 100%
Stage 2: Has Budget Data
  ↓
Stage 3: Generated Revenue (earned something at the box office)
  ↓
Stage 4: Recovered Investment (revenue > 50% of budget)
  ↓
Stage 5: Profitable (revenue > budget)
  ↓
Stage 6: Strong ROI (> 100% return)
  ↓
Stage 7: High ROI (> 300% return)
  ↓
Stage 8: Blockbuster ROI (> 1000% return)
```

#### Segment Breakdowns:
The funnel was then broken down by:
- **Genre** — Which genres convert investment to profit most efficiently?
- **Budget Tier** — Do bigger budgets mean safer bets or bigger risks?
- **Era** — Has the industry gotten better or worse at generating returns?
- **Director** — Which directors have the best investment-to-hit conversion?

#### Key Bottleneck Found:
The biggest drop-off occurs between **"Generated Revenue"** and **"Recovered Investment"** — meaning many movies earn *something*, but not enough to break even. This is where studios lose the most money.

---

## 📈 Interactive Dashboards

### 🖥️ Streamlit Dashboard (Run Locally)

A 5-page interactive dashboard built with Streamlit & Plotly for exploring all findings:

| Page | What You'll See |
|------|----------------|
| **🏠 Overview** | KPI cards (total revenue, success rate, median ROI), Budget vs Revenue scatter with break-even line, Revenue by genre, Yearly revenue trends, Rating distribution |
| **💰 Financial Performance** | Budget category success rates vs ROI, ROI box plots by budget tier, Budget & Revenue distributions |
| **🎭 Genre & People** | Genre risk-return matrix, Top 15 Directors & Actors by revenue, Content rating performance comparison |
| **🔄 Funnel Analysis** | 8-stage investment-to-profitability funnel, Stage-by-stage drop-off rates, Genre-level funnel conversion breakdown |
| **📋 Movie Details** | Searchable, sortable table of all 5,009 movies with profitability indicators and CSV download |

**Run it:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 📊 Tableau Dashboards (Online)

Static dashboards are also available on Tableau Public:

🔗 [**View on Tableau Public →**](https://public.tableau.com/views/MovieIndustryAnalysis_17681128080920/OverviewDashboard)

> The Tableau dashboards are being rebuilt with an advanced, app-style design. See [`docs/Advanced_Dashboard_Guide.md`](docs/Advanced_Dashboard_Guide.md) for the rebuild plan.

---

## 🔑 Key Findings & Results

### Results at a Glance

| Metric | Result | Insight |
|--------|--------|---------|
| **Total Movies Analyzed** | 5,009 | Spanning 1970–2017, covering nearly 50 years of cinema |
| **Industry Success Rate** | 54.5% | Nearly half of all movies **lose money** — the industry is a coin flip |
| **Average Budget** | ~$35M | But ranges from under $1M to $300M+ — extreme variance |
| **Average Revenue** | ~$82M | Top earners distort this; median revenue is much lower |
| **Highest ROI Genre** | Mystery / Horror | Low budgets + strong audience = most capital-efficient |
| **Best Budget Range** | $15M–$40M | Mid-budget films offer the best risk-adjusted returns |
| **Budget↔Revenue Correlation** | 0.73 | Spending more *helps*, but it doesn't guarantee profit |
| **Vote Count↔Revenue Correlation** | 0.78 | Audience engagement is the strongest predictor of revenue |
| **Biggest Funnel Leak** | Revenue → Break-Even | Many films earn *something* but fail to recover the full budget |
| **Blockbuster ROI Hit Rate** | ~3-5% | Only a tiny fraction of all films achieve 1000%+ ROI |

---

### Financial Reality
- **54.5% of movies are profitable** — meaning 45.5% represent a total loss for investors
- **Average ROI (298,361%)** is misleading — it's driven by a handful of massive outliers like Paranormal Activity (~$194M revenue on a $15K budget). The **median ROI** tells the real story: most profitable films earn moderate returns
- The break-even point is the biggest hurdle: many movies earn *some* box office revenue but not enough to cover the production budget. This is the #1 place studios lose money

### Genre Insights
- **Mystery and Horror** deliver the highest ROI despite lower budgets — they're the most capital-efficient genres because audiences show up even without $100M in visual effects
- **Drama** is the most produced genre but has middling financial performance — the genre is oversaturated, making it harder to stand out
- **Action and Adventure** generate the highest *total* revenue, but they require massive budgets ($80M+), meaning the downside risk is equally massive when they flop
- **Comedy** sits in a sweet spot: moderate budgets with consistent (if unglamorous) returns

### Budget Strategy
- **Mid-budget films ($15M–$40M)** offer the best risk-adjusted returns — large enough for quality production, small enough to limit catastrophic losses
- **Blockbuster budgets ($100M+)** have higher success rates overall, but when they fail, the losses are catastrophic (often $50M-$200M lost per film)
- **Low-budget films (<$15M)** are high-variance: most fail quietly, but the rare hit (e.g., horror) delivers extraordinary ROI

### People & Timing
- **Christopher Nolan, Steven Spielberg, and James Cameron** consistently outperform industry averages on both revenue and ROI — their name alone acts as a risk-reduction factor
- **Industry revenue peaked around 2015**, with average budgets growing faster than average returns in recent years — a warning sign of cost inflation
- **PG-13 films** are the financial sweet spot — they draw the broadest audience demographics with strong box office potential

### The Funnel Truth
- The funnel narrows most sharply between **"Generated Revenue"** and **"Recovered Investment"** — this is the #1 bottleneck
- Only **~15%** of all movies achieve Strong ROI (>100% return on investment)
- Genre choice and budget discipline are the two biggest levers at the profitability gate
- **Horror and Mystery** have the tightest funnels (highest conversion from "invested" to "profitable"), while **Drama** and **Sci-Fi** have the leakiest

### 💡 Business Recommendations (from the Data)

1. **Prioritize mid-budget productions** ($15M–$40M) over blockbuster bets to maximize portfolio ROI
2. **Invest in Horror/Mystery** as a capital-efficient genre — high conversion, low downside
3. **Pair high-budget films with proven directors** (Nolan, Spielberg-tier talent) to reduce risk
4. **Target PG-13 ratings** for maximum audience reach and box office potential
5. **Watch the break-even gap** — the largest value destruction happens when films earn revenue but can't cover costs. Tighter budget control at the production stage is the highest-leverage intervention

---

## 🏗️ Project Structure

```
Movies Dataset/
├── data/                                    # Raw datasets
│   ├── tmdb_5000_movies.csv                 # TMDB movie data (5,000 movies)
│   ├── movie_metadata.csv                   # Extended metadata from IMDB
│   └── tmdb_5000_movies_mergedwith_movie_metadata.csv  # Merged master file
│
├── notebooks/                               # Analysis scripts (Python)
│   ├── 01_exploratory_data_analysis.py      # EDA with 16 visualizations
│   ├── 02_full_data_merge.py                # Dataset merging logic
│   ├── 02_etl_tableau_prep.py               # ETL → 6 Tableau-ready tables
│   └── 03_funnel_analysis.py                # 8-stage funnel analysis
│
├── outputs/                                 # Generated outputs
│   ├── tableau/                             # Tableau-ready CSV datasets
│   │   ├── movies_main.csv                  # 5,009 movies, all features
│   │   ├── movies_by_genre.csv              # 14,884 genre-exploded rows
│   │   ├── director_performance.csv         # Aggregated director stats
│   │   ├── actor_performance.csv            # Aggregated actor stats
│   │   ├── yearly_trends.csv                # Year-over-year trends
│   │   └── funnel_analysis.csv              # Funnel stage assignments
│   └── *.png                                # 16 EDA visualization charts
│
├── docs/
│   ├── Tableau_EDA_Guide.md                 # Step-by-step Tableau guide
│   └── Advanced_Dashboard_Guide.md          # Advanced dashboard rebuild plan
│
├── app.py                                   # Streamlit interactive dashboard
├── requirements.txt                         # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| **Python 3.x** | 3.9+ | Data analysis scripting |
| **Pandas** | 1.5+ | Data manipulation and cleaning |
| **NumPy** | 1.24+ | Numerical computations |
| **Matplotlib** | 3.7+ | Static visualizations |
| **Seaborn** | 0.12+ | Statistical visualization |
| **Streamlit** | 1.30+ | Interactive web dashboard |
| **Plotly** | 5.18+ | Dynamic charts & visualizations |
| **Tableau Public** | 2024.x | Online dashboard publishing |

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install pandas numpy matplotlib seaborn
```

### Run the Analysis

```bash
# Step 1: Exploratory Data Analysis (generates 16 charts in outputs/)
python notebooks/01_exploratory_data_analysis.py

# Step 2: ETL Pipeline (generates 6 Tableau CSVs in outputs/tableau/)
python notebooks/02_etl_tableau_prep.py

# Step 3: Funnel Analysis (generates funnel charts + analysis)
python notebooks/03_funnel_analysis.py
```

### View Dashboards

Open the CSV files in `outputs/tableau/` with [Tableau Public](https://public.tableau.com/en-us/s/download) to explore the interactive dashboards.

---

## 📂 Data Source

- **The Movie Database (TMDB)** — 5,000 movies dataset via [Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
- **IMDB Movie Metadata** — Extended metadata including director, actor, and social media metrics
- Combined and merged into a single 5,009-row, 42-column master dataset

---

## 👤 Author

**David Ezieshi**
- 🔗 [Tableau Public](https://public.tableau.com/app/profile/david.ezieshi)
- 🔗 [GitHub](https://github.com/ezieshie-stack)
- 🔗 [LinkedIn](https://www.linkedin.com/in/davidezieshi)
