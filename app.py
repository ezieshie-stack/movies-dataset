"""
🎬 Movies Dataset — Interactive Dashboard
A Streamlit-powered analytics dashboard for exploring 5,009 movies.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ─── Page Config ───
st.set_page_config(
    page_title="Movie Industry Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 15px !important;
        padding: 8px 0;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    }
    .kpi-card.teal {
        background: linear-gradient(135deg, #2C6E6F 0%, #1a4a4b 100%);
        box-shadow: 0 8px 32px rgba(44, 110, 111, 0.25);
    }
    .kpi-card.orange {
        background: linear-gradient(135deg, #E8723A 0%, #c25a2a 100%);
        box-shadow: 0 8px 32px rgba(232, 114, 58, 0.25);
    }
    .kpi-card.green {
        background: linear-gradient(135deg, #27AE60 0%, #1e8449 100%);
        box-shadow: 0 8px 32px rgba(39, 174, 96, 0.25);
    }
    .kpi-card.red {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 8px 32px rgba(231, 76, 60, 0.25);
    }
    .kpi-number {
        font-size: 36px;
        font-weight: 700;
        margin: 4px 0;
    }
    .kpi-label {
        font-size: 13px;
        opacity: 0.85;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-sub {
        font-size: 14px;
        opacity: 0.75;
        margin-top: 4px;
    }

    /* Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a2e;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Plotly chart containers */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    tableau_dir = os.path.join(base, "outputs", "tableau")
    data = {}
    for f in ["movies_main", "movies_by_genre", "director_performance",
              "actor_performance", "yearly_trends", "funnel_analysis"]:
        path = os.path.join(tableau_dir, f"{f}.csv")
        if os.path.exists(path):
            data[f] = pd.read_csv(path, encoding='latin1')
    return data

data = load_data()
df = data.get("movies_main", pd.DataFrame())

if df.empty:
    st.error("❌ Data not found. Please run the ETL pipeline first.")
    st.stop()

# Clean numeric columns
for col in ['Budget', 'Revenue', 'Profit', 'ROI', 'TMDB Rating', 'IMDB Rating',
            'Combined Rating', 'Vote Count', 'Popularity', 'Runtime Minutes']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ─── Sidebar ───
with st.sidebar:
    st.markdown("## 🎬 Movie Analytics")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Overview", "💰 Financial Performance", "🎭 Genre & People",
         "🔄 Funnel Analysis", "📋 Movie Details"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Global Filters
    st.markdown("### 🔍 Filters")

    # Era filter
    eras = ["All"] + sorted(df["Era"].dropna().unique().tolist())
    selected_era = st.selectbox("Era", eras)

    # Genre filter
    genres = ["All"] + sorted(df["Primary Genre"].dropna().unique().tolist())
    selected_genre = st.selectbox("Genre", genres)

    # Budget filter
    budget_cats = ["All"] + sorted(df["Budget Category"].dropna().unique().tolist())
    selected_budget = st.selectbox("Budget Category", budget_cats)

    st.markdown("---")
    st.caption("📊 Analyzing 5,009 movies (1970-2017)")
    st.caption("Built by David Ezieshi")

# Apply filters
filtered = df.copy()
if selected_era != "All":
    filtered = filtered[filtered["Era"] == selected_era]
if selected_genre != "All":
    filtered = filtered[filtered["Primary Genre"] == selected_genre]
if selected_budget != "All":
    filtered = filtered[filtered["Budget Category"] == selected_budget]

# ─── Color Palette ───
COLORS = {
    "primary": "#667eea",
    "teal": "#2C6E6F",
    "orange": "#E8723A",
    "green": "#27AE60",
    "red": "#e74c3c",
    "yellow": "#f1c40f",
    "purple": "#764ba2",
    "bg": "#F5F5F5",
    "text": "#1a1a2e"
}

GENRE_COLORS = px.colors.qualitative.Set2


# ─── Helper Functions ───
def fmt_currency(val):
    if abs(val) >= 1e9:
        return f"${val/1e9:.1f}B"
    elif abs(val) >= 1e6:
        return f"${val/1e6:.0f}M"
    elif abs(val) >= 1e3:
        return f"${val/1e3:.0f}K"
    return f"${val:.0f}"


def fmt_number(val):
    if abs(val) >= 1e6:
        return f"{val/1e6:.1f}M"
    elif abs(val) >= 1e3:
        return f"{val/1e3:.1f}K"
    return f"{val:,.0f}"


def kpi_card(label, value, sub="", color_class=""):
    return f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-number">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def chart_layout(fig, title="", height=400):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=COLORS["text"]),
                   x=0, xanchor="left"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", color="#333"),
        margin=dict(l=40, r=20, t=50, b=40),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig.update_xaxes(gridcolor="#f0f0f0", gridwidth=1)
    fig.update_yaxes(gridcolor="#f0f0f0", gridwidth=1)
    return fig


# ═══════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═══════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown("# 🎬 Movie Industry Overview")
    st.markdown(f"*Analyzing **{len(filtered):,}** movies  •  Filtered by: "
                f"{'All Eras' if selected_era == 'All' else selected_era} • "
                f"{'All Genres' if selected_genre == 'All' else selected_genre} • "
                f"{'All Budgets' if selected_budget == 'All' else selected_budget}*")
    st.markdown("")

    # ── KPI Row ──
    valid = filtered[filtered["Budget"] > 0]
    profitable = valid[valid["Is Profitable"] == True]
    total_rev = filtered["Revenue"].sum()
    total_budget = filtered["Budget"].sum()
    avg_roi = valid["ROI"].median() if len(valid) > 0 else 0
    success_rate = (len(profitable) / len(valid) * 100) if len(valid) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Revenue", fmt_currency(total_rev),
                             f"{len(filtered):,} movies", "teal"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Total Budget", fmt_currency(total_budget),
                             f"Avg: {fmt_currency(total_budget/max(len(valid),1))}",
                             "orange"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Median ROI", f"{avg_roi:.0f}%",
                             f"Profitable: {len(profitable):,}", "green"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Success Rate", f"{success_rate:.1f}%",
                             f"{len(valid)-len(profitable):,} lost money", "red"),
                    unsafe_allow_html=True)

    st.markdown("")

    # ── Charts Row 1 ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header">📈 Revenue vs Budget</div>',
                    unsafe_allow_html=True)
        scatter_data = valid.head(1000)
        fig_scatter = px.scatter(
            scatter_data, x="Budget", y="Revenue",
            color="Primary Genre", size="Popularity",
            hover_name="Title",
            hover_data={"Budget": ":$,.0f", "Revenue": ":$,.0f",
                        "ROI": ":.0f", "Year": True},
            color_discrete_sequence=GENRE_COLORS,
            opacity=0.7
        )
        max_val = max(scatter_data["Budget"].max(), scatter_data["Revenue"].max())
        fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                              line=dict(color="red", width=1.5, dash="dash"))
        fig_scatter.add_annotation(x=max_val*0.7, y=max_val*0.65,
                                   text="Break-Even Line", showarrow=False,
                                   font=dict(color="red", size=11))
        chart_layout(fig_scatter, height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">🎯 Top Genres by Revenue</div>',
                    unsafe_allow_html=True)
        genre_rev = (filtered.groupby("Primary Genre")["Revenue"]
                     .sum().sort_values(ascending=True).tail(10))
        fig_genre = px.bar(
            x=genre_rev.values, y=genre_rev.index,
            orientation="h",
            color=genre_rev.values,
            color_continuous_scale=["#e8e8e8", COLORS["teal"]],
            text=[fmt_currency(v) for v in genre_rev.values]
        )
        fig_genre.update_traces(textposition="outside", textfont_size=11)
        fig_genre.update_coloraxes(showscale=False)
        chart_layout(fig_genre, height=450)
        st.plotly_chart(fig_genre, use_container_width=True)

    # ── Charts Row 2 ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">📅 Revenue Trend Over Time</div>',
                    unsafe_allow_html=True)
        yearly = (filtered.groupby("Year").agg(
            Revenue=("Revenue", "sum"),
            Budget=("Budget", "sum"),
            Count=("Title", "count")
        ).reset_index())
        yearly = yearly[yearly["Year"] > 1970]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=yearly["Year"], y=yearly["Revenue"],
            fill="tozeroy", name="Revenue",
            fillcolor="rgba(44, 110, 111, 0.3)",
            line=dict(color=COLORS["teal"], width=2)
        ))
        fig_trend.add_trace(go.Scatter(
            x=yearly["Year"], y=yearly["Budget"],
            fill="tozeroy", name="Budget",
            fillcolor="rgba(232, 114, 58, 0.2)",
            line=dict(color=COLORS["orange"], width=2)
        ))
        chart_layout(fig_trend, height=380)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">⭐ Rating Distribution</div>',
                    unsafe_allow_html=True)
        ratings = filtered["Combined Rating"].dropna()
        fig_rating = px.histogram(
            ratings, nbins=30,
            color_discrete_sequence=[COLORS["purple"]],
            opacity=0.85
        )
        fig_rating.update_layout(
            xaxis_title="Combined Rating", yaxis_title="Number of Movies",
            showlegend=False
        )
        avg_rating = ratings.mean()
        fig_rating.add_vline(x=avg_rating, line_dash="dash", line_color=COLORS["red"],
                             annotation_text=f"Avg: {avg_rating:.1f}")
        chart_layout(fig_rating, height=380)
        st.plotly_chart(fig_rating, use_container_width=True)


# ═══════════════════════════════════════════════════
# PAGE 2: FINANCIAL PERFORMANCE
# ═══════════════════════════════════════════════════
elif page == "💰 Financial Performance":
    st.markdown("# 💰 Financial Performance Deep Dive")
    st.markdown("")

    valid = filtered[(filtered["Budget"] > 0) & (filtered["Revenue"] > 0)]

    # ── KPI Row ──
    c1, c2, c3, c4 = st.columns(4)
    avg_budget = valid["Budget"].mean()
    avg_revenue = valid["Revenue"].mean()
    avg_profit = valid["Profit"].mean()
    median_roi = valid["ROI"].median()

    with c1:
        st.markdown(kpi_card("Avg Budget", fmt_currency(avg_budget),
                             f"Median: {fmt_currency(valid['Budget'].median())}",
                             "orange"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Avg Revenue", fmt_currency(avg_revenue),
                             f"Median: {fmt_currency(valid['Revenue'].median())}",
                             "teal"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Avg Profit", fmt_currency(avg_profit),
                             f"Median: {fmt_currency(valid['Profit'].median())}",
                             "green"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Median ROI", f"{median_roi:.0f}%",
                             f"Mean: {valid['ROI'].mean():,.0f}%", "purple"),
                    unsafe_allow_html=True)

    st.markdown("")

    # ── Budget Category Analysis ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📊 Budget Category Performance</div>',
                    unsafe_allow_html=True)
        budget_perf = valid.groupby("Budget Category").agg(
            Count=("Title", "count"),
            Avg_Revenue=("Revenue", "mean"),
            Avg_ROI=("ROI", "median"),
            Success_Rate=("Is Profitable", "mean")
        ).reset_index()
        budget_order = ["Low Budget (<$15M)", "Medium ($15M-$40M)",
                        "High ($40M-$100M)", "Blockbuster (>$100M)"]
        budget_perf["Budget Category"] = pd.Categorical(
            budget_perf["Budget Category"], categories=budget_order, ordered=True)
        budget_perf = budget_perf.sort_values("Budget Category").dropna(subset=["Budget Category"])

        fig_budget = make_subplots(specs=[[{"secondary_y": True}]])
        fig_budget.add_trace(go.Bar(
            x=budget_perf["Budget Category"], y=budget_perf["Success_Rate"]*100,
            name="Success Rate %", marker_color=COLORS["green"], opacity=0.8
        ), secondary_y=False)
        fig_budget.add_trace(go.Scatter(
            x=budget_perf["Budget Category"], y=budget_perf["Avg_ROI"],
            name="Median ROI %", mode="lines+markers",
            line=dict(color=COLORS["orange"], width=3),
            marker=dict(size=10)
        ), secondary_y=True)
        fig_budget.update_layout(barmode="group")
        fig_budget.update_yaxes(title_text="Success Rate (%)", secondary_y=False)
        fig_budget.update_yaxes(title_text="Median ROI (%)", secondary_y=True)
        chart_layout(fig_budget, height=420)
        st.plotly_chart(fig_budget, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">🎯 ROI Distribution by Category</div>',
                    unsafe_allow_html=True)
        roi_data = valid[valid["ROI"].between(-100, 1000)]
        fig_roi_box = px.box(
            roi_data, x="Budget Category", y="ROI",
            color="Budget Category",
            category_orders={"Budget Category": budget_order},
            color_discrete_sequence=[COLORS["teal"], COLORS["green"],
                                     COLORS["orange"], COLORS["red"]]
        )
        fig_roi_box.add_hline(y=0, line_dash="dash", line_color="gray",
                              annotation_text="Break-Even")
        chart_layout(fig_roi_box, height=420)
        fig_roi_box.update_layout(showlegend=False)
        st.plotly_chart(fig_roi_box, use_container_width=True)

    # ── Distributions ──
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">💵 Budget Distribution</div>',
                    unsafe_allow_html=True)
        fig_budget_hist = px.histogram(
            valid, x="Budget", nbins=50,
            color_discrete_sequence=[COLORS["orange"]], opacity=0.8
        )
        fig_budget_hist.update_layout(xaxis_title="Budget ($)", yaxis_title="Count",
                                      showlegend=False)
        chart_layout(fig_budget_hist, height=350)
        st.plotly_chart(fig_budget_hist, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">🎰 Revenue Distribution</div>',
                    unsafe_allow_html=True)
        fig_rev_hist = px.histogram(
            valid, x="Revenue", nbins=50,
            color_discrete_sequence=[COLORS["teal"]], opacity=0.8
        )
        fig_rev_hist.update_layout(xaxis_title="Revenue ($)", yaxis_title="Count",
                                    showlegend=False)
        chart_layout(fig_rev_hist, height=350)
        st.plotly_chart(fig_rev_hist, use_container_width=True)


# ═══════════════════════════════════════════════════
# PAGE 3: GENRE & PEOPLE
# ═══════════════════════════════════════════════════
elif page == "🎭 Genre & People":
    st.markdown("# 🎭 Genre & People Analytics")
    st.markdown("")

    valid = filtered[(filtered["Budget"] > 0) & (filtered["Revenue"] > 0)]

    # ── Genre Analysis ──
    st.markdown('<div class="section-header">🎬 Genre Performance Matrix</div>',
                unsafe_allow_html=True)

    genre_stats = valid.groupby("Primary Genre").agg(
        Movies=("Title", "count"),
        Total_Revenue=("Revenue", "sum"),
        Avg_Revenue=("Revenue", "mean"),
        Median_ROI=("ROI", "median"),
        Success_Rate=("Is Profitable", "mean"),
        Avg_Rating=("Combined Rating", "mean")
    ).reset_index()
    genre_stats = genre_stats[genre_stats["Movies"] >= 10].sort_values("Total_Revenue", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_genre_rev = px.bar(
            genre_stats.head(12), x="Primary Genre", y="Total_Revenue",
            color="Success_Rate", color_continuous_scale=["#e74c3c", "#f1c40f", "#27AE60"],
            text=[fmt_currency(v) for v in genre_stats.head(12)["Total_Revenue"]],
            range_color=[0.3, 0.8]
        )
        fig_genre_rev.update_traces(textposition="outside", textfont_size=10)
        fig_genre_rev.update_coloraxes(colorbar_title="Success %")
        chart_layout(fig_genre_rev, "Total Revenue by Genre (colored by success rate)", 420)
        st.plotly_chart(fig_genre_rev, use_container_width=True)

    with col2:
        fig_genre_roi = px.scatter(
            genre_stats, x="Median_ROI", y="Success_Rate",
            size="Movies", color="Avg_Rating",
            text="Primary Genre",
            color_continuous_scale="RdYlGn",
            size_max=50
        )
        fig_genre_roi.update_traces(textposition="top center", textfont_size=9)
        fig_genre_roi.update_layout(
            xaxis_title="Median ROI (%)", yaxis_title="Success Rate",
        )
        fig_genre_roi.update_coloraxes(colorbar_title="Avg Rating")
        chart_layout(fig_genre_roi, "Genre Risk-Return Matrix", 420)
        st.plotly_chart(fig_genre_roi, use_container_width=True)

    # ── Director & Actor Rankings ──
    st.markdown("---")
    col_d, col_a = st.columns(2)

    with col_d:
        st.markdown('<div class="section-header">🎬 Top 15 Directors by Revenue</div>',
                    unsafe_allow_html=True)
        dir_stats = valid.groupby("Director").agg(
            Total_Revenue=("Revenue", "sum"),
            Movies=("Title", "count"),
            Avg_ROI=("ROI", "median"),
            Success_Rate=("Is Profitable", "mean")
        ).reset_index()
        dir_stats = dir_stats[dir_stats["Movies"] >= 3].sort_values(
            "Total_Revenue", ascending=True).tail(15)

        fig_dir = px.bar(
            dir_stats, x="Total_Revenue", y="Director",
            orientation="h",
            color="Success_Rate",
            color_continuous_scale=["#e74c3c", "#27AE60"],
            text=[fmt_currency(v) for v in dir_stats["Total_Revenue"]],
            range_color=[0.4, 1.0]
        )
        fig_dir.update_traces(textposition="outside", textfont_size=10)
        fig_dir.update_coloraxes(colorbar_title="Success %")
        chart_layout(fig_dir, height=500)
        st.plotly_chart(fig_dir, use_container_width=True)

    with col_a:
        st.markdown('<div class="section-header">⭐ Top 15 Actors by Revenue</div>',
                    unsafe_allow_html=True)
        actor_stats = valid.groupby("Lead Actor").agg(
            Total_Revenue=("Revenue", "sum"),
            Movies=("Title", "count"),
            Avg_ROI=("ROI", "median"),
            Success_Rate=("Is Profitable", "mean")
        ).reset_index()
        actor_stats = actor_stats[actor_stats["Movies"] >= 3].sort_values(
            "Total_Revenue", ascending=True).tail(15)

        fig_actor = px.bar(
            actor_stats, x="Total_Revenue", y="Lead Actor",
            orientation="h",
            color="Success_Rate",
            color_continuous_scale=["#e74c3c", "#27AE60"],
            text=[fmt_currency(v) for v in actor_stats["Total_Revenue"]],
            range_color=[0.4, 1.0]
        )
        fig_actor.update_traces(textposition="outside", textfont_size=10)
        fig_actor.update_coloraxes(colorbar_title="Success %")
        chart_layout(fig_actor, height=500)
        st.plotly_chart(fig_actor, use_container_width=True)

    # ── Content Rating ──
    st.markdown("---")
    st.markdown('<div class="section-header">🔞 Content Rating Performance</div>',
                unsafe_allow_html=True)

    content_stats = valid.groupby("Content Rating").agg(
        Movies=("Title", "count"),
        Avg_Revenue=("Revenue", "mean"),
        Median_ROI=("ROI", "median"),
        Success_Rate=("Is Profitable", "mean")
    ).reset_index()
    content_stats = content_stats[content_stats["Movies"] >= 20]

    c1, c2, c3 = st.columns(3)
    with c1:
        fig_cr_rev = px.bar(content_stats.sort_values("Avg_Revenue", ascending=True),
                            x="Avg_Revenue", y="Content Rating", orientation="h",
                            color_discrete_sequence=[COLORS["teal"]],
                            text=[fmt_currency(v) for v in content_stats.sort_values(
                                "Avg_Revenue", ascending=True)["Avg_Revenue"]])
        fig_cr_rev.update_traces(textposition="outside")
        chart_layout(fig_cr_rev, "Avg Revenue", 300)
        st.plotly_chart(fig_cr_rev, use_container_width=True)
    with c2:
        fig_cr_roi = px.bar(content_stats.sort_values("Median_ROI", ascending=True),
                            x="Median_ROI", y="Content Rating", orientation="h",
                            color_discrete_sequence=[COLORS["orange"]],
                            text=[f"{v:.0f}%" for v in content_stats.sort_values(
                                "Median_ROI", ascending=True)["Median_ROI"]])
        fig_cr_roi.update_traces(textposition="outside")
        chart_layout(fig_cr_roi, "Median ROI (%)", 300)
        st.plotly_chart(fig_cr_roi, use_container_width=True)
    with c3:
        fig_cr_sr = px.bar(content_stats.sort_values("Success_Rate", ascending=True),
                           x="Success_Rate", y="Content Rating", orientation="h",
                           color_discrete_sequence=[COLORS["green"]],
                           text=[f"{v*100:.0f}%" for v in content_stats.sort_values(
                               "Success_Rate", ascending=True)["Success_Rate"]])
        fig_cr_sr.update_traces(textposition="outside")
        chart_layout(fig_cr_sr, "Success Rate", 300)
        st.plotly_chart(fig_cr_sr, use_container_width=True)


# ═══════════════════════════════════════════════════
# PAGE 4: FUNNEL ANALYSIS
# ═══════════════════════════════════════════════════
elif page == "🔄 Funnel Analysis":
    st.markdown("# 🔄 Investment-to-Profitability Funnel")
    st.markdown("*Tracking how movies flow from investment to blockbuster returns*")
    st.markdown("")

    valid = filtered[filtered["Budget"] > 0]

    # ── Build Funnel Stages ──
    total = len(filtered)
    has_budget = len(valid)
    has_revenue = len(valid[valid["Revenue"] > 0])
    recovered = len(valid[(valid["Revenue"] > 0) & (valid["Revenue"] >= valid["Budget"] * 0.5)])
    profitable = len(valid[valid["Is Profitable"] == True])
    strong_roi = len(valid[valid["ROI"] > 100])
    high_roi = len(valid[valid["ROI"] > 300])
    blockbuster = len(valid[valid["ROI"] > 1000])

    stages = ["Total Movies", "Has Budget", "Generated Revenue",
              "Recovered 50%+", "Profitable", "Strong ROI (>100%)",
              "High ROI (>300%)", "Blockbuster (>1000%)"]
    values = [total, has_budget, has_revenue, recovered, profitable,
              strong_roi, high_roi, blockbuster]

    # ── Funnel Chart ──
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-header">📊 The Funnel</div>',
                    unsafe_allow_html=True)
        fig_funnel = go.Figure(go.Funnel(
            y=stages, x=values,
            textposition="inside",
            textinfo="value+percent initial",
            connector={"line": {"color": "#E8723A", "width": 1}},
            marker=dict(
                color=["#1a1a2e", "#16213e", "#0f3460", "#2C6E6F",
                       "#27AE60", "#f1c40f", "#E8723A", "#e74c3c"]
            )
        ))
        chart_layout(fig_funnel, height=500)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">📉 Stage-by-Stage Drop-off</div>',
                    unsafe_allow_html=True)

        drop_data = []
        for i in range(1, len(stages)):
            conversion = (values[i] / values[i-1] * 100) if values[i-1] > 0 else 0
            dropped = values[i-1] - values[i]
            drop_data.append({
                "Transition": f"{stages[i-1][:12]}→{stages[i][:12]}",
                "Conversion": conversion,
                "Dropped": dropped
            })

        drop_df = pd.DataFrame(drop_data)

        fig_drop = px.bar(
            drop_df, x="Transition", y="Conversion",
            color="Conversion",
            color_continuous_scale=["#e74c3c", "#f1c40f", "#27AE60"],
            text=[f"{v:.0f}%" for v in drop_df["Conversion"]],
            range_color=[30, 100]
        )
        fig_drop.update_traces(textposition="outside")
        fig_drop.update_layout(xaxis_tickangle=-45)
        fig_drop.update_coloraxes(showscale=False)
        chart_layout(fig_drop, height=500)
        st.plotly_chart(fig_drop, use_container_width=True)

    # ── Funnel by Genre ──
    st.markdown("---")
    st.markdown('<div class="section-header">🎬 Funnel Conversion by Genre</div>',
                unsafe_allow_html=True)

    genre_funnel = valid.groupby("Primary Genre").agg(
        Total=("Title", "count"),
        Has_Revenue=("Revenue", lambda x: (x > 0).sum()),
        Profitable=("Is Profitable", "sum"),
        High_ROI=("ROI", lambda x: (x > 300).sum())
    ).reset_index()
    genre_funnel = genre_funnel[genre_funnel["Total"] >= 20]
    genre_funnel["Revenue_Rate"] = genre_funnel["Has_Revenue"] / genre_funnel["Total"] * 100
    genre_funnel["Profit_Rate"] = genre_funnel["Profitable"] / genre_funnel["Total"] * 100
    genre_funnel["High_ROI_Rate"] = genre_funnel["High_ROI"] / genre_funnel["Total"] * 100
    genre_funnel = genre_funnel.sort_values("Profit_Rate", ascending=True)

    fig_genre_funnel = go.Figure()
    fig_genre_funnel.add_trace(go.Bar(
        y=genre_funnel["Primary Genre"], x=genre_funnel["Revenue_Rate"],
        name="Has Revenue", orientation="h", marker_color=COLORS["teal"]
    ))
    fig_genre_funnel.add_trace(go.Bar(
        y=genre_funnel["Primary Genre"], x=genre_funnel["Profit_Rate"],
        name="Profitable", orientation="h", marker_color=COLORS["green"]
    ))
    fig_genre_funnel.add_trace(go.Bar(
        y=genre_funnel["Primary Genre"], x=genre_funnel["High_ROI_Rate"],
        name="High ROI (>300%)", orientation="h", marker_color=COLORS["orange"]
    ))
    fig_genre_funnel.update_layout(barmode="group", xaxis_title="Rate (%)")
    chart_layout(fig_genre_funnel, height=450)
    st.plotly_chart(fig_genre_funnel, use_container_width=True)

    # ── Key Takeaway ──
    st.markdown("---")
    st.info("""
    **🔑 Key Takeaway:** The biggest money leak is between *"Generated Revenue"* and
    *"Recovered Investment"* — many movies earn something at the box office, but not
    enough to cover the production budget. Genre choice and budget discipline are the
    two biggest levers to improve this conversion.
    """)


# ═══════════════════════════════════════════════════
# PAGE 5: MOVIE DETAILS
# ═══════════════════════════════════════════════════
elif page == "📋 Movie Details":
    st.markdown("# 📋 Movie Details")
    st.markdown("")

    # ── Search ──
    search = st.text_input("🔍 Search by title", placeholder="e.g. Inception, Avatar, Titanic...")

    display_df = filtered.copy()
    if search:
        display_df = display_df[display_df["Title"].str.contains(search, case=False, na=False)]

    # ── Sort Options ──
    col_sort, col_dir, col_top = st.columns([2, 1, 1])
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Revenue", "Budget", "ROI", "Year",
                                           "Combined Rating", "Popularity"])
    with col_dir:
        sort_dir = st.selectbox("Order", ["Descending", "Ascending"])
    with col_top:
        top_n = st.selectbox("Show", [25, 50, 100, 250, "All"])

    ascending = sort_dir == "Ascending"
    display_df = display_df.sort_values(sort_by, ascending=ascending, na_position="last")

    if top_n != "All":
        display_df = display_df.head(int(top_n))

    # ── Stats Bar ──
    st.markdown(f"*Showing **{len(display_df):,}** of {len(filtered):,} movies*")

    # ── Display Columns ──
    show_cols = ["Title", "Primary Genre", "Year", "Director", "Lead Actor",
                 "Budget", "Revenue", "Profit", "ROI", "Is Profitable",
                 "Combined Rating", "Content Rating", "Budget Category"]
    show_cols = [c for c in show_cols if c in display_df.columns]

    styled = display_df[show_cols].copy()

    # Format currency columns
    for col in ["Budget", "Revenue", "Profit"]:
        if col in styled.columns:
            styled[col] = styled[col].apply(
                lambda x: fmt_currency(x) if pd.notna(x) else "—")

    # Format ROI
    if "ROI" in styled.columns:
        styled["ROI"] = styled["ROI"].apply(
            lambda x: f"{x:.0f}%" if pd.notna(x) else "—")

    # Format profitability
    if "Is Profitable" in styled.columns:
        styled["Is Profitable"] = styled["Is Profitable"].apply(
            lambda x: "✅ Profitable" if x == True else ("❌ Loss" if x == False else "—"))

    st.dataframe(styled.reset_index(drop=True), use_container_width=True, height=600)

    # ── Download ──
    csv = display_df[show_cols].to_csv(index=False)
    st.download_button("📥 Download as CSV", csv, "movies_filtered.csv", "text/csv")
