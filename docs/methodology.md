# Methodology — Detailed Analysis Documentation

This document contains the full technical detail behind each analysis phase. For a summary, see [README.md](../README.md).

---

## Phase 1: Exploratory Data Analysis (EDA)

**Script:** [`01_exploratory_data_analysis.py`](../notebooks/01_exploratory_data_analysis.py) (998 lines)

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

## Phase 2: ETL Pipeline (Extract, Transform, Load)

**Script:** [`02_etl_tableau_prep.py`](../notebooks/02_etl_tableau_prep.py) (658 lines)

Raw data is messy. This phase cleaned and transformed it into **6 structured, Tableau-ready CSV files** with engineered features.

### How the Data Was Transformed:

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

### Output Tables:

| Table | Rows | Purpose |
|-------|------|---------|
| `movies_main.csv` | 5,009 | Core dataset with all engineered features |
| `movies_by_genre.csv` | 14,884 | One row per movie-genre combination |
| `director_performance.csv` | 2,300+ | Aggregated director stats |
| `actor_performance.csv` | 4,500+ | Aggregated actor stats |
| `yearly_trends.csv` | 47 | Year-over-year industry trends |
| `funnel_analysis.csv` | 5,009 | Each movie tagged with its funnel stage |

---

## Phase 3: Investment-to-Profitability Funnel Analysis

**Script:** [`03_funnel_analysis.py`](../notebooks/03_funnel_analysis.py) (614 lines)

This phase introduced a **creative, business-style funnel** — treating movie investment like a sales pipeline to identify where money gets lost.

### The 8-Stage Funnel:

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

### Segment Breakdowns:
The funnel was broken down by **Genre**, **Budget Tier**, **Era**, and **Director** to identify which segments convert investment to profit most efficiently.

### Key Bottleneck:
The biggest drop-off occurs between **"Generated Revenue"** and **"Recovered Investment"** — meaning many movies earn *something*, but not enough to break even. This is where studios lose the most money.

---

## Detailed Findings

### Financial Reality
- **54.5% of movies are profitable** — meaning 45.5% represent a total loss for investors
- The break-even point is the biggest hurdle: many movies earn *some* box office revenue but not enough to cover the production budget

### Genre Insights
- **Mystery and Horror** deliver the highest ROI despite lower budgets — they're the most capital-efficient genres
- **Drama** is the most produced genre but has middling financial performance — the genre is oversaturated
- **Action and Adventure** generate the highest *total* revenue, but require massive budgets ($80M+)
- **Comedy** sits in a sweet spot: moderate budgets with consistent returns

### Budget Strategy
- **Mid-budget films ($15M–$40M)** offer the best risk-adjusted returns
- **Blockbuster budgets ($100M+)** have higher success rates overall, but when they fail, the losses are catastrophic
- **Low-budget films (<$15M)** are high-variance: most fail quietly, but the rare hit delivers extraordinary ROI

### People & Timing
- **Christopher Nolan, Steven Spielberg, and James Cameron** consistently outperform industry averages
- **Industry revenue peaked around 2015**, with average budgets growing faster than average returns
- **PG-13 films** are the financial sweet spot for audience reach
