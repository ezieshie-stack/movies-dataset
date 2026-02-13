# 🎬 Movies EDA - Tableau Visualization Guide

This guide walks you through building each EDA chart in Tableau using the prepared datasets.

---

## 📁 Data Files Location

All files are in: `/outputs/tableau/`

| File | Records | Use For |
|------|---------|---------|
| `movies_main.csv` | 5,009 | Main analysis - all charts |
| `movies_by_genre.csv` | 14,884 | Genre-specific analysis |
| `director_performance.csv` | 2,092 | Director metrics |
| `actor_performance.csv` | 1,767 | Actor star power |
| `yearly_trends.csv` | 90 | Time series trends |

---

## 🔌 Step 1: Connect to Data

1. Open **Tableau Desktop** or **Tableau Public**
2. Click **Text File** under Connect
3. Navigate to `Movies Dataset/outputs/tableau/`
4. Select **movies_main.csv**
5. Drag to canvas → Tableau auto-detects columns

### Data Type Adjustments
In the Data Source tab, verify these types:
- `Year` → **Date** (or keep as Number)
- `Budget`, `Revenue`, `Profit` → **Number (whole)**
- `ROI`, `Profit Margin` → **Number (decimal)**
- `Is Profitable` → **Boolean**
- `Primary Genre`, `Director`, `Lead Actor` → **String**

---

## 📊 Chart 1: Budget Distribution (Histogram)

**Goal:** Show distribution of movie budgets

### Steps:
1. Drag **Budget** to Columns
2. Right-click Budget → **Create Bins...**
   - Bin Size: `10000000` (10 million)
3. Drag **Budget (bin)** to Columns (replace original)
4. Drag **Number of Records** to Rows
5. Format:
   - Right-click X-axis → Format → Numbers → Currency (Custom) → `$0M`
   - Title: "Budget Distribution"
   - Color: Blue gradient

### Enhancement:
- Add a reference line at $50M (median) by:
  - Analytics → Drag **Reference Line** → cell → Median

---

## 📊 Chart 2: Revenue Distribution (Histogram)

**Same process as Budget:**
1. Create bin for Revenue (bin size: `50000000`)
2. Revenue (bin) → Columns
3. Number of Records → Rows
4. Format axis as currency

---

## 📊 Chart 3: Budget vs Revenue Scatter Plot ⭐

**Goal:** Visualize investment landscape with break-even line

### Steps:
1. Drag **Budget** to Columns
2. Drag **Revenue** to Rows
3. Drag **Primary Genre** to Color
4. Drag **Combined Rating** to Color (or keep Genre)
5. Drag **Popularity** to Size
6. Change Mark type to **Circle**

### Add Break-Even Reference Line:
1. Analytics → Drag **Reference Line** → entire table
2. Line: **Custom** → Formula: `[Budget]`
3. Label: "Break-Even Line"
4. Format: Red, dashed

### Add 2x ROI Line:
1. Create calculated field: `[Budget] * 2`
2. Add as another reference line (green, dashed)

### Format:
- Title: "Budget vs Revenue: The Movie Investment Landscape"
- Axis format: Currency `$0.0M` or `$0.0B`

---

## 📊 Chart 4: Genre Performance - Revenue Bar Chart

**Goal:** Compare average revenue by genre

### Steps:
1. Drag **Primary Genre** to Rows
2. Drag **Revenue** to Columns
3. Right-click Revenue (green pill) → **Measure** → **Average**
4. Sort descending (toolbar or right-click axis)
5. Color: Drag **Revenue** to Color for gradient

### Format:
- Title: ""
- Labels: Show value labels (Label shelf → check box)

---

## 📊 Chart 5: Genre Performance - ROI Bar Chart

### Steps:
1. Duplicate the Revenue chart (right-click sheet tab → Duplicate)
2. Replace Revenue with **ROI** on Columns
3. Set to **Average**
4. Add reference line at 0% (break-even)

### Format:
- Title: "Average ROI by Genre"
- Color: Red for negative, Green for positive
  - Use a diverging color palette centered at 0

---

## 📊 Chart 6: Genre Count - Treemap

**Goal:** Visualize genre distribution by volume

### Steps:
1. Change Mark type to **Treemap** (or Square)
2. Drag **Primary Genre** to Color
3. Drag **Number of Records** to Size
4. Drag **Primary Genre** to Label
5. Drag **Number of Records** to Label

### Format:
- Title: "Movie Count by Genre"

---

## 📊 Chart 7: Time Trend - Movies Per Year

**Goal:** Show movie release volume over time

### Steps:
1. Drag **Year** to Columns
2. Right-click → change to **Continuous** (not discrete)
3. Drag **Number of Records** to Rows
4. Change Mark type to **Bar** (or Area)

### Filter:
- Drag Year to Filters → Range: 1990-2017
- Show filter if desired

### Format:
- Title: "Movies Released Per Year"

---

## 📊 Chart 8: Time Trend - Average Budget Over Time

### Steps:
1. **Year** (continuous) to Columns
2. **Budget** to Rows → set to **Average**
3. Mark type: **Line** with **Area** underneath
4. Add trend line: Analytics → Trend Line → Linear

### Format:
- Title: "Average Budget Over Time"
- Format Y-axis: Currency

---

## 📊 Chart 9: Time Trend - Average Revenue Over Time

**Same as Budget, but with Revenue measure**

---

## 📊 Chart 10: Rating Distribution - Histogram

### Steps:
1. Create bins for **Combined Rating** (bin size: 0.5)
2. Combined Rating (bin) → Columns
3. Number of Records → Rows

### Compare TMDB vs IMDB:
1. Create a dual-axis chart:
   - TMDB Rating (bin) → Columns
   - IMDB Rating (bin) → Columns (Ctrl+drag to duplicate)
2. Right-click second axis → Dual Axis
3. Synchronize axes
4. Differentiate colors

---

## 📊 Chart 11: Correlation - Scatter Matrix

**Goal:** Show relationships between key metrics

### Option A: Single Scatter
1. Budget → Columns
2. Revenue → Rows
3. Add trend line: Analytics → Trend Line
4. Right-click trend line → "Describe Trend Model" to see R² and p-value

### Option B: Multiple Pairs (Small Multiples)
Create separate scatter plots for:
- Budget vs Revenue
- Budget vs ROI
- Popularity vs Revenue
- Rating vs Revenue

Then combine in a dashboard.

---

## 📊 Chart 12: Director Analysis - Bar Chart

**Data:** Use `director_performance.csv`

### Steps:
1. Connect to `director_performance.csv`
2. Drag **Director** to Rows
3. Drag **Total Revenue** to Columns
4. Filter: **Movie Count** >= 5
5. Sort descending
6. Limit to Top 15: Right-click Director → Filter → Top → By Field → Top 15 by Total Revenue

### Format:
- Title: "Top 15 Directors by Total Revenue"
- Add Success Rate as a second measure (dual axis or separate)

---

## 📊 Chart 13: Director Success Rate

### Steps:
1. Director → Rows
2. Success Rate → Columns
3. Add reference lines at 50% and 70%
4. Color by Success Rate (green gradient)

---

## 📊 Chart 14: Lead Actor Analysis

**Data:** Use `actor_performance.csv`

### Steps:
Same as Director charts, using Lead Actor field

---

## 📊 Chart 15: Content Rating Analysis

### Steps:
1. **Content Rating** → Columns
2. **Revenue** (Average) → Rows as bar
3. Add **ROI** (Average) on secondary axis
4. Dual axis chart with bars and line

### Filter:
- Exclude null/unknown ratings

---

## 📊 Chart 16: Profitability Funnel

**For the Investment-to-Profitability Funnel:**

### Create Calculated Fields:
```
// 1. Has Budget
IF [Budget] > 0 THEN 1 ELSE 0 END

// 2. Has Revenue  
IF [Budget] > 0 AND [Revenue] > 0 THEN 1 ELSE 0 END

// ç

// 4. High ROI (>300%)
IF [Budget] > 0 AND [ROI] > 300 THEN 1 ELSE 0 END
```

### Build Funnel Chart:
1. Create a bar chart with these 4 measures stacked
2. Sort in funnel order
3. Use the built-in Funnel viz type (if available) or create manually

---

## 🎨 Dashboard Assembly

### Recommended Layout:

**Dashboard 1: Overview**
```
┌─────────────────────────────────────────────────┐
│  KPI Cards: Total Movies | Avg ROI | Success % │
├─────────────────────┬───────────────────────────┤
│  Genre Treemap      │  Budget vs Revenue Scatter│
├─────────────────────┴───────────────────────────┤
│  Movies Released Per Year (Timeline)             │
└─────────────────────────────────────────────────┘
```

**Dashboard 2: Financial Deep Dive**
```
┌─────────────────────┬───────────────────────────┐
│  Budget Distribution│  Revenue Distribution     │
├─────────────────────┼───────────────────────────┤
│  ROI by Genre       │  Revenue by Genre         │
├─────────────────────┴───────────────────────────┤
│  Budget Category Performance (Bar Chart)         │
└─────────────────────────────────────────────────┘
```

**Dashboard 3: People Analytics**
```
┌─────────────────────┬───────────────────────────┐
│  Top Directors      │  Director Success Rate    │
├─────────────────────┼───────────────────────────┤
│  Top Actors         │  Actor Success Rate       │
└─────────────────────┴───────────────────────────┘
```

---

## 💡 Pro Tips

### Formatting
- Use consistent color palette across all charts
- Format numbers: Budget/Revenue as `$0.0M` or `$0.0B`
- Format ROI as percentage with 1 decimal

### Interactivity
- Add **Filters** as dropdowns (Year, Genre, Director)
- Enable **Highlight Actions** between charts
- Add **Tooltips** with rich information

### Calculated Fields to Add:
```
// Budget Tier (for grouping)
IF [Budget] < 5000000 THEN 'Micro (<$5M)'
ELSEIF [Budget] < 15000000 THEN 'Low ($5-15M)'
ELSEIF [Budget] < 40000000 THEN 'Medium ($15-40M)'
ELSEIF [Budget] < 100000000 THEN 'High ($40-100M)'
ELSE 'Blockbuster (>$100M)'
END

// Profit Status
IF [Profit] > 0 THEN 'Profitable' ELSE 'Loss' END

// ROI Tier
IF [ROI] < 0 THEN 'Loss'
ELSEIF [ROI] < 100 THEN 'Low ROI'
ELSEIF [ROI] < 300 THEN 'Good ROI'
ELSE 'Exceptional ROI'
END
```

---

## 📍 Quick Start Checklist

- [ ] Connect to `movies_main.csv`
- [ ] Verify data types
- [ ] Build Budget Distribution histogram
- [ ] Build Budget vs Revenue scatter with break-even line
- [ ] Build Genre performance bars (Revenue + ROI)
- [ ] Build Time trends (line charts)
- [ ] Build Director/Actor bar charts
- [ ] Create calculated fields for tiers
- [ ] Assemble into dashboards
- [ ] Add filters and interactivity
- [ ] Apply consistent formatting

---

Good luck building your Tableau dashboards! 🎬📊
