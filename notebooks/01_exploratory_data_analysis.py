# %% [markdown]
# # 🎬 Movies Dataset - Comprehensive Exploratory Data Analysis
# 
# This notebook explores the **FULLY MERGED** Movies dataset (5,009 movies, 42 columns) 
# combining TMDB data with movie metadata for complete analysis:
# 
# **Financial Metrics:**
# - Budget, Revenue, Gross, ROI analysis
# 
# **Quality & Popularity:**
# - IMDB scores, Vote averages, Popularity metrics
# - Social media engagement (Facebook likes)
# 
# **People & Credits:**
# - Director analysis and success patterns
# - Actor performance and star power
# 
# **Content & Classification:**
# - Genre performance patterns
# - Content ratings analysis
# - Language and country distribution
# 
# **Time Analysis:**
# - Historical trends and patterns
# - Year-over-year performance

# %% [markdown]
# ## 1. Setup & Data Loading

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from ast import literal_eval
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 200)

# %%
# Load the FULLY MERGED dataset
import os
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
base_dir = os.path.dirname(script_dir) if 'notebooks' in script_dir else script_dir
data_dir = os.path.join(base_dir, 'data')
output_dir = os.path.join(base_dir, 'outputs')
os.makedirs(output_dir, exist_ok=True)

# Use the comprehensive merged dataset
movies = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies_mergedwith_movie_metadata.csv'), encoding='latin1')

print("=" * 70)
print("📊 FULLY MERGED DATASET LOADED")
print("=" * 70)
print(f"Total Movies: {len(movies)}")
print(f"Total Features: {len(movies.columns)}")
print(f"\nColumns Available:")
for i, col in enumerate(movies.columns, 1):
    print(f"  {i:2}. {col}")

# %% [markdown]
# ## 2. Comprehensive Data Quality Assessment

# %%
# Data types overview
print("=" * 70)
print("DATA TYPES OVERVIEW")
print("=" * 70)
print(movies.dtypes.to_string())

# %%
# Missing Values Analysis
print("\n" + "=" * 70)
print("MISSING VALUES ANALYSIS")
print("=" * 70)
missing = movies.isnull().sum()
missing_pct = (missing / len(movies) * 100).round(2)
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct
}).sort_values('Missing Count', ascending=False)
print(missing_df[missing_df['Missing Count'] > 0].to_string())

# %%
# Visualize missing data pattern
fig, ax = plt.subplots(figsize=(14, 8))
missing_cols = missing_df[missing_df['Missing Count'] > 0].head(20)
colors = ['#ff6b6b' if pct > 50 else '#feca57' if pct > 25 else '#48dbfb' for pct in missing_cols['Missing %']]
ax.barh(missing_cols.index, missing_cols['Missing %'], color=colors)
ax.set_xlabel('Missing Percentage (%)')
ax.set_title('Missing Data by Column (Top 20)', fontsize=14, fontweight='bold')
ax.axvline(x=50, color='red', linestyle='--', alpha=0.5, label='50% threshold')
ax.axvline(x=25, color='orange', linestyle='--', alpha=0.5, label='25% threshold')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'missing_data_analysis.png'), dpi=150)
plt.show()

# %%
# Sample data preview
print("\n" + "=" * 70)
print("SAMPLE DATA PREVIEW (Key Columns)")
print("=" * 70)
key_cols = ['movie_title', 'budget', 'revenue', 'gross', 'imdb_score', 'vote_average', 
            'popularity', 'director_name', 'actor_1_name', 'title_year', 'content_rating']
print(movies[key_cols].head(10).to_string())

# %% [markdown]
# ## 3. Financial Data Quality Check

# %%
# Check for zero/missing financial data
print("=" * 70)
print("FINANCIAL DATA QUALITY CHECK")
print("=" * 70)

# Budget analysis
print("\n📊 BUDGET:")
print(f"  - Total records: {len(movies)}")
print(f"  - Missing (NaN): {movies['budget'].isna().sum()}")
print(f"  - Zero values: {(movies['budget'] == 0).sum()}")
print(f"  - Valid (> 0): {(movies['budget'] > 0).sum()}")
print(f"  - Valid (> $1M): {(movies['budget'] > 1e6).sum()}")

# Revenue analysis
print("\n📊 REVENUE:")
print(f"  - Missing (NaN): {movies['revenue'].isna().sum()}")
print(f"  - Zero values: {(movies['revenue'] == 0).sum()}")
print(f"  - Valid (> 0): {(movies['revenue'] > 0).sum()}")

# Gross analysis (from metadata)
print("\n📊 GROSS:")
print(f"  - Missing (NaN): {movies['gross'].isna().sum()}")
print(f"  - Zero values: {(pd.to_numeric(movies['gross'], errors='coerce') == 0).sum()}")
print(f"  - Valid (> 0): {(pd.to_numeric(movies['gross'], errors='coerce') > 0).sum()}")

# %%
# Create unified financial columns for analysis
movies['budget_clean'] = pd.to_numeric(movies['budget'], errors='coerce')
movies['revenue_clean'] = pd.to_numeric(movies['revenue'], errors='coerce').fillna(
    pd.to_numeric(movies['gross'], errors='coerce')
)  # Use gross as fallback for revenue

# Fill remaining missing revenue with gross when available
gross_numeric = pd.to_numeric(movies['gross'], errors='coerce')
movies.loc[movies['revenue_clean'].isna(), 'revenue_clean'] = gross_numeric[movies['revenue_clean'].isna()]

print("\n✅ UNIFIED FINANCIAL COLUMNS CREATED:")
print(f"  - budget_clean: {movies['budget_clean'].notna().sum()} valid values")
print(f"  - revenue_clean: {movies['revenue_clean'].notna().sum()} valid values")

# %% [markdown]
# ## 4. Create Analysis-Ready Dataset

# %%
# Filter for movies with valid financial data
valid_movies = movies[
    (movies['budget_clean'] > 1e6) &  # Budget > $1M to filter out low-quality data
    (movies['revenue_clean'] > 0)      # Must have some revenue data
].copy()

print("=" * 70)
print("ANALYSIS-READY DATASET CREATED")
print("=" * 70)
print(f"Original dataset: {len(movies)} movies")
print(f"Valid movies (budget > $1M, revenue > 0): {len(valid_movies)} movies")
print(f"Dropped: {len(movies) - len(valid_movies)} movies ({(len(movies) - len(valid_movies))/len(movies)*100:.1f}%)")

# Calculate derived financial metrics
valid_movies['profit'] = valid_movies['revenue_clean'] - valid_movies['budget_clean']
valid_movies['roi'] = (valid_movies['profit'] / valid_movies['budget_clean'] * 100).round(2)
valid_movies['profitable'] = valid_movies['profit'] > 0

print(f"\nProfitable Movies: {valid_movies['profitable'].sum()} ({valid_movies['profitable'].mean()*100:.1f}%)")
print(f"Average ROI: {valid_movies['roi'].mean():.1f}%")
print(f"Median ROI: {valid_movies['roi'].median():.1f}%")

# %% [markdown]
# ## 5. Basic Statistics - All Key Metrics

# %%
# Comprehensive statistics for all numerical columns
print("=" * 70)
print("COMPREHENSIVE NUMERICAL STATISTICS")
print("=" * 70)

numerical_cols = ['budget_clean', 'revenue_clean', 'profit', 'roi', 'popularity', 
                  'vote_average', 'vote_count', 'imdb_score', 'duration', 'runtime',
                  'num_critic_for_reviews', 'num_user_for_reviews', 'num_voted_users',
                  'movie_facebook_likes', 'director_facebook_likes', 'cast_total_facebook_likes',
                  'actor_1_facebook_likes', 'actor_2_facebook_likes', 'actor_3_facebook_likes']

available_cols = [col for col in numerical_cols if col in valid_movies.columns]
print(valid_movies[available_cols].describe().round(2).to_string())

# %% [markdown]
# ## 6. Distribution Analysis

# %%
# Financial Distributions
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Budget (log scale)
axes[0, 0].hist(valid_movies['budget_clean'] / 1e6, bins=50, edgecolor='black', alpha=0.7, color='#3498db')
axes[0, 0].set_xlabel('Budget (Millions $)')
axes[0, 0].set_ylabel('Count')
axes[0, 0].set_title('Budget Distribution', fontsize=12, fontweight='bold')

# Revenue
axes[0, 1].hist(valid_movies['revenue_clean'] / 1e6, bins=50, edgecolor='black', alpha=0.7, color='#2ecc71')
axes[0, 1].set_xlabel('Revenue (Millions $)')
axes[0, 1].set_ylabel('Count')
axes[0, 1].set_title('Revenue Distribution', fontsize=12, fontweight='bold')

# Profit
axes[0, 2].hist(valid_movies['profit'] / 1e6, bins=50, edgecolor='black', alpha=0.7, color='#9b59b6')
axes[0, 2].set_xlabel('Profit (Millions $)')
axes[0, 2].set_ylabel('Count')
axes[0, 2].set_title('Profit Distribution', fontsize=12, fontweight='bold')
axes[0, 2].axvline(x=0, color='red', linestyle='--', linewidth=2)

# ROI Distribution (capped for visibility)
roi_capped = valid_movies['roi'].clip(-200, 1000)
axes[1, 0].hist(roi_capped, bins=50, edgecolor='black', alpha=0.7, color='#e74c3c')
axes[1, 0].set_xlabel('ROI % (capped at -200% to 1000%)')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_title('ROI Distribution', fontsize=12, fontweight='bold')
axes[1, 0].axvline(x=0, color='black', linestyle='--', linewidth=2)

# IMDB Score vs Vote Average comparison
if 'imdb_score' in valid_movies.columns:
    axes[1, 1].hist(valid_movies['imdb_score'].dropna(), bins=30, alpha=0.6, label='IMDB Score', color='#f39c12')
axes[1, 1].hist(valid_movies['vote_average'].dropna(), bins=30, alpha=0.6, label='TMDB Vote Avg', color='#1abc9c')
axes[1, 1].set_xlabel('Rating')
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_title('Rating Distribution Comparison', fontsize=12, fontweight='bold')
axes[1, 1].legend()

# Popularity
axes[1, 2].hist(valid_movies['popularity'].dropna(), bins=50, edgecolor='black', alpha=0.7, color='#e91e63')
axes[1, 2].set_xlabel('Popularity Score')
axes[1, 2].set_ylabel('Count')
axes[1, 2].set_title('Popularity Distribution', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'distributions_comprehensive.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 7. Budget vs Revenue Deep Analysis

# %%
# Scatter plot: Budget vs Revenue with multiple dimensions
fig, ax = plt.subplots(figsize=(14, 10))

scatter = ax.scatter(
    valid_movies['budget_clean'] / 1e6, 
    valid_movies['revenue_clean'] / 1e6,
    c=valid_movies['vote_average'],
    cmap='RdYlGn',
    alpha=0.6,
    s=valid_movies['popularity'].clip(0, 100) * 3,  # Size by popularity
    edgecolors='white',
    linewidth=0.5
)

# Add break-even line
max_val = max(valid_movies['budget_clean'].max(), valid_movies['revenue_clean'].max()) / 1e6
ax.plot([0, max_val], [0, max_val], 'r--', label='Break-even line', linewidth=2)
ax.plot([0, max_val], [0, max_val * 2], 'g--', label='2x ROI line', linewidth=1.5, alpha=0.7)
ax.plot([0, max_val], [0, max_val * 3], 'b--', label='3x ROI line', linewidth=1, alpha=0.5)

ax.set_xlabel('Budget (Millions $)', fontsize=12)
ax.set_ylabel('Revenue (Millions $)', fontsize=12)
ax.set_title('Budget vs Revenue: The Movie Investment Landscape\n(Size = Popularity, Color = Rating)', 
             fontsize=14, fontweight='bold')
ax.legend(loc='upper left')

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Vote Average', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'budget_vs_revenue_comprehensive.png'), dpi=150)
plt.show()

# Key insight
above_line = (valid_movies['revenue_clean'] > valid_movies['budget_clean']).sum()
below_line = (valid_movies['revenue_clean'] <= valid_movies['budget_clean']).sum()
print(f"\n📊 INVESTMENT INSIGHT:")
print(f"  - {above_line} movies ({above_line/(above_line+below_line)*100:.1f}%) are above break-even")
print(f"  - {below_line} movies ({below_line/(above_line+below_line)*100:.1f}%) lost money or broke even")

# %% [markdown]
# ## 8. Genre Analysis (Comprehensive)

# %%
# Parse genres from JSON format
def parse_genres(genre_str):
    try:
        if pd.isna(genre_str):
            return []
        # Handle JSON format
        if '[' in str(genre_str):
            genres = json.loads(str(genre_str).replace("'", '"'))
            if isinstance(genres, list):
                return [g.get('name', g) if isinstance(g, dict) else g for g in genres]
        # Handle pipe-separated format
        return str(genre_str).split('|')
    except:
        return []

valid_movies['genres_list'] = valid_movies['genres'].apply(parse_genres)

# Explode to one row per genre
genre_df = valid_movies.explode('genres_list')
genre_df = genre_df[genre_df['genres_list'].notna() & (genre_df['genres_list'] != '')]

print(f"Total genre-movie combinations: {len(genre_df)}")
print(f"Unique genres: {genre_df['genres_list'].nunique()}")

# %%
# Comprehensive genre performance
genre_stats = genre_df.groupby('genres_list').agg({
    'movie_title': 'count',
    'budget_clean': 'mean',
    'revenue_clean': 'mean',
    'profit': 'mean',
    'roi': 'mean',
    'vote_average': 'mean',
    'imdb_score': 'mean',
    'popularity': 'mean',
    'profitable': 'mean'
}).round(2)

genre_stats.columns = ['Movie Count', 'Avg Budget', 'Avg Revenue', 'Avg Profit', 
                       'Avg ROI', 'Avg TMDB Rating', 'Avg IMDB Score', 'Avg Popularity', 'Success Rate']
genre_stats['Success Rate'] = (genre_stats['Success Rate'] * 100).round(1)
genre_stats = genre_stats.sort_values('Movie Count', ascending=False)
print(genre_stats.to_string())

# %%
# Genre Visualization - 4 panel view
fig, axes = plt.subplots(2, 2, figsize=(18, 14))

top_genres = genre_stats.head(12)

# Movie Count by Genre
ax1 = axes[0, 0]
bars1 = ax1.barh(top_genres.index, top_genres['Movie Count'], color='#3498db')
ax1.set_xlabel('Number of Movies')
ax1.set_title('Movie Count by Genre', fontsize=12, fontweight='bold')
ax1.invert_yaxis()
for bar, val in zip(bars1, top_genres['Movie Count']):
    ax1.text(val + 5, bar.get_y() + bar.get_height()/2, f'{int(val)}', va='center', fontsize=9)

# Average Revenue by Genre
ax2 = axes[0, 1]
bars2 = ax2.barh(top_genres.index, top_genres['Avg Revenue'] / 1e6, color='#2ecc71')
ax2.set_xlabel('Average Revenue (Millions $)')
ax2.set_title('Average Revenue by Genre', fontsize=12, fontweight='bold')
ax2.invert_yaxis()

# ROI by Genre
ax3 = axes[1, 0]
colors3 = ['#2ecc71' if x > 0 else '#e74c3c' for x in top_genres['Avg ROI']]
bars3 = ax3.barh(top_genres.index, top_genres['Avg ROI'], color=colors3)
ax3.set_xlabel('Average ROI %')
ax3.set_title('Average ROI by Genre', fontsize=12, fontweight='bold')
ax3.invert_yaxis()
ax3.axvline(x=0, color='black', linestyle='--', linewidth=1)

# Success Rate by Genre
ax4 = axes[1, 1]
bars4 = ax4.barh(top_genres.index, top_genres['Success Rate'], color='#9b59b6')
ax4.set_xlabel('Success Rate (%)')
ax4.set_title('Profitability Rate by Genre', fontsize=12, fontweight='bold')
ax4.invert_yaxis()
ax4.axvline(x=50, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'genre_analysis_comprehensive.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 9. Director Analysis

# %%
# Director performance analysis
director_stats = valid_movies.groupby('director_name').agg({
    'movie_title': 'count',
    'budget_clean': 'sum',
    'revenue_clean': 'sum',
    'profit': 'sum',
    'roi': 'mean',
    'vote_average': 'mean',
    'imdb_score': 'mean',
    'profitable': 'mean'
}).reset_index()

director_stats.columns = ['Director', 'Movies', 'Total Budget', 'Total Revenue', 
                          'Total Profit', 'Avg ROI', 'Avg TMDB Rating', 'Avg IMDB Score', 'Success Rate']
director_stats['Success Rate'] = (director_stats['Success Rate'] * 100).round(1)

# Filter for directors with at least 3 movies
prolific_directors = director_stats[director_stats['Movies'] >= 3].sort_values('Total Revenue', ascending=False)

print("=" * 70)
print("TOP 15 DIRECTORS BY TOTAL REVENUE (Min 3 movies)")
print("=" * 70)
display_df = prolific_directors.head(15).copy()
display_df['Total Budget'] = (display_df['Total Budget'] / 1e6).round(1).astype(str) + 'M'
display_df['Total Revenue'] = (display_df['Total Revenue'] / 1e6).round(1).astype(str) + 'M'
display_df['Total Profit'] = (display_df['Total Profit'] / 1e6).round(1).astype(str) + 'M'
display_df['Avg ROI'] = display_df['Avg ROI'].round(1).astype(str) + '%'
print(display_df.to_string(index=False))

# %%
# Director visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

top_15 = prolific_directors.head(15)

# Revenue by Director
ax1 = axes[0]
ax1.barh(top_15['Director'], top_15['Total Revenue'] / 1e6, color='#3498db')
ax1.set_xlabel('Total Revenue (Millions $)')
ax1.set_title('Top 15 Directors by Total Revenue', fontsize=12, fontweight='bold')
ax1.invert_yaxis()

# Success Rate by Director
ax2 = axes[1]
colors = ['#2ecc71' if x >= 70 else '#f39c12' if x >= 50 else '#e74c3c' for x in top_15['Success Rate']]
ax2.barh(top_15['Director'], top_15['Success Rate'], color=colors)
ax2.set_xlabel('Success Rate (%)')
ax2.set_title('Success Rate of Top 15 Directors', fontsize=12, fontweight='bold')
ax2.invert_yaxis()
ax2.axvline(x=50, color='red', linestyle='--', alpha=0.5)
ax2.axvline(x=70, color='green', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'director_analysis.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 10. Actor Analysis (Star Power)

# %%
# Actor 1 (Lead Actor) Performance Analysis
actor1_stats = valid_movies.groupby('actor_1_name').agg({
    'movie_title': 'count',
    'budget_clean': 'sum',
    'revenue_clean': 'sum',
    'profit': 'sum',
    'roi': 'mean',
    'vote_average': 'mean',
    'actor_1_facebook_likes': 'mean',
    'profitable': 'mean'
}).reset_index()

actor1_stats.columns = ['Lead Actor', 'Movies', 'Total Budget', 'Total Revenue', 
                        'Total Profit', 'Avg ROI', 'Avg Rating', 'Avg FB Likes', 'Success Rate']
actor1_stats['Success Rate'] = (actor1_stats['Success Rate'] * 100).round(1)

# Filter for actors with at least 5 movies
prolific_actors = actor1_stats[actor1_stats['Movies'] >= 5].sort_values('Total Revenue', ascending=False)

print("=" * 70)
print("TOP 20 LEAD ACTORS BY TOTAL REVENUE (Min 5 movies)")
print("=" * 70)
display_df = prolific_actors.head(20).copy()
display_df['Total Revenue'] = (display_df['Total Revenue'] / 1e6).round(1).astype(str) + 'M'
display_df['Total Profit'] = (display_df['Total Profit'] / 1e6).round(1).astype(str) + 'M'
display_df['Avg ROI'] = display_df['Avg ROI'].round(1).astype(str) + '%'
display_df['Avg FB Likes'] = display_df['Avg FB Likes'].round(0).astype(int)
print(display_df[['Lead Actor', 'Movies', 'Total Revenue', 'Avg ROI', 'Avg Rating', 'Success Rate']].to_string(index=False))

# %%
# Star Power Visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 10))

top_20 = prolific_actors.head(20)

# Revenue by Actor
ax1 = axes[0]
ax1.barh(top_20['Lead Actor'], top_20['Total Revenue'] / 1e6, color='#e74c3c')
ax1.set_xlabel('Total Revenue (Millions $)')
ax1.set_title('Top 20 Lead Actors by Total Revenue', fontsize=12, fontweight='bold')
ax1.invert_yaxis()

# ROI by Actor
ax2 = axes[1]
colors = ['#2ecc71' if x > 100 else '#f39c12' if x > 0 else '#e74c3c' for x in top_20['Avg ROI']]
ax2.barh(top_20['Lead Actor'], top_20['Avg ROI'], color=colors)
ax2.set_xlabel('Average ROI %')
ax2.set_title('Average ROI by Lead Actor', fontsize=12, fontweight='bold')
ax2.invert_yaxis()
ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax2.axvline(x=100, color='green', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'actor_analysis.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 11. Content Rating Analysis

# %%
# Content Rating Performance
rating_stats = valid_movies.groupby('content_rating').agg({
    'movie_title': 'count',
    'budget_clean': 'mean',
    'revenue_clean': 'mean',
    'profit': 'mean',
    'roi': 'mean',
    'vote_average': 'mean',
    'profitable': 'mean'
}).reset_index()

rating_stats.columns = ['Content Rating', 'Movies', 'Avg Budget', 'Avg Revenue', 
                        'Avg Profit', 'Avg ROI', 'Avg Rating', 'Success Rate']
rating_stats['Success Rate'] = (rating_stats['Success Rate'] * 100).round(1)
rating_stats = rating_stats.sort_values('Movies', ascending=False)

print("=" * 70)
print("CONTENT RATING PERFORMANCE")
print("=" * 70)
print(rating_stats.to_string(index=False))

# %%
# Content Rating Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Filter for major ratings only
major_ratings = rating_stats[rating_stats['Movies'] >= 20].copy()

# Movie Count
ax1 = axes[0, 0]
ax1.bar(major_ratings['Content Rating'], major_ratings['Movies'], color='#3498db')
ax1.set_xlabel('Content Rating')
ax1.set_ylabel('Number of Movies')
ax1.set_title('Movie Count by Content Rating', fontsize=12, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)

# Average Revenue
ax2 = axes[0, 1]
ax2.bar(major_ratings['Content Rating'], major_ratings['Avg Revenue'] / 1e6, color='#2ecc71')
ax2.set_xlabel('Content Rating')
ax2.set_ylabel('Average Revenue (Millions $)')
ax2.set_title('Average Revenue by Content Rating', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

# ROI
ax3 = axes[1, 0]
colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in major_ratings['Avg ROI']]
ax3.bar(major_ratings['Content Rating'], major_ratings['Avg ROI'], color=colors)
ax3.set_xlabel('Content Rating')
ax3.set_ylabel('Average ROI %')
ax3.set_title('Average ROI by Content Rating', fontsize=12, fontweight='bold')
ax3.tick_params(axis='x', rotation=45)
ax3.axhline(y=0, color='black', linestyle='--')

# Success Rate
ax4 = axes[1, 1]
ax4.bar(major_ratings['Content Rating'], major_ratings['Success Rate'], color='#9b59b6')
ax4.set_xlabel('Content Rating')
ax4.set_ylabel('Success Rate %')
ax4.set_title('Profitability Rate by Content Rating', fontsize=12, fontweight='bold')
ax4.tick_params(axis='x', rotation=45)
ax4.axhline(y=50, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'content_rating_analysis.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 12. Time Trend Analysis

# %%
# Parse and clean year data
valid_movies['year'] = pd.to_numeric(valid_movies['title_year'], errors='coerce')
# Fallback to release_date if title_year is missing
valid_movies.loc[valid_movies['year'].isna(), 'year'] = pd.to_datetime(
    valid_movies.loc[valid_movies['year'].isna(), 'release_date'], errors='coerce'
).dt.year

# Filter for valid years
valid_years = valid_movies[(valid_movies['year'] >= 1970) & (valid_movies['year'] <= 2017)]

# Yearly trends
yearly = valid_years.groupby('year').agg({
    'movie_title': 'count',
    'budget_clean': 'mean',
    'revenue_clean': 'mean',
    'profit': 'mean',
    'roi': 'mean',
    'vote_average': 'mean',
    'imdb_score': 'mean',
    'profitable': 'mean'
}).reset_index()

yearly.columns = ['Year', 'Movies', 'Avg Budget', 'Avg Revenue', 'Avg Profit', 
                  'Avg ROI', 'Avg TMDB Rating', 'Avg IMDB Score', 'Success Rate']
yearly['Success Rate'] = (yearly['Success Rate'] * 100).round(1)

print("=" * 70)
print("YEARLY TRENDS (1990-2017)")
print("=" * 70)
print(yearly[yearly['Year'] >= 1990].to_string(index=False))

# %%
# Time series plots - 6 panel view
fig, axes = plt.subplots(3, 2, figsize=(16, 14))

plot_yearly = yearly[yearly['Year'] >= 1990]

# Movie count by year
ax1 = axes[0, 0]
ax1.bar(plot_yearly['Year'], plot_yearly['Movies'], color='#3498db', alpha=0.8)
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Movies')
ax1.set_title('Movies Released Per Year', fontsize=12, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)

# Budget trend
ax2 = axes[0, 1]
ax2.plot(plot_yearly['Year'], plot_yearly['Avg Budget'] / 1e6, marker='o', linewidth=2, color='#e74c3c')
ax2.fill_between(plot_yearly['Year'], plot_yearly['Avg Budget'] / 1e6, alpha=0.3, color='#e74c3c')
ax2.set_xlabel('Year')
ax2.set_ylabel('Average Budget (Millions $)')
ax2.set_title('Average Budget Over Time', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

# Revenue trend
ax3 = axes[1, 0]
ax3.plot(plot_yearly['Year'], plot_yearly['Avg Revenue'] / 1e6, marker='o', linewidth=2, color='#2ecc71')
ax3.fill_between(plot_yearly['Year'], plot_yearly['Avg Revenue'] / 1e6, alpha=0.3, color='#2ecc71')
ax3.set_xlabel('Year')
ax3.set_ylabel('Average Revenue (Millions $)')
ax3.set_title('Average Revenue Over Time', fontsize=12, fontweight='bold')
ax3.tick_params(axis='x', rotation=45)

# ROI trend
ax4 = axes[1, 1]
ax4.plot(plot_yearly['Year'], plot_yearly['Avg ROI'], marker='o', linewidth=2, color='#9b59b6')
ax4.set_xlabel('Year')
ax4.set_ylabel('Average ROI %')
ax4.set_title('Average ROI Over Time', fontsize=12, fontweight='bold')
ax4.axhline(y=0, color='red', linestyle='--')
ax4.tick_params(axis='x', rotation=45)

# Rating trends (both TMDB and IMDB)
ax5 = axes[2, 0]
ax5.plot(plot_yearly['Year'], plot_yearly['Avg TMDB Rating'], marker='o', linewidth=2, 
         color='#1abc9c', label='TMDB Rating')
ax5.plot(plot_yearly['Year'], plot_yearly['Avg IMDB Score'], marker='s', linewidth=2, 
         color='#f39c12', label='IMDB Score')
ax5.set_xlabel('Year')
ax5.set_ylabel('Average Rating')
ax5.set_title('Rating Trends Over Time', fontsize=12, fontweight='bold')
ax5.legend()
ax5.set_ylim(5, 8)
ax5.tick_params(axis='x', rotation=45)

# Success Rate trend
ax6 = axes[2, 1]
ax6.plot(plot_yearly['Year'], plot_yearly['Success Rate'], marker='o', linewidth=2, color='#e91e63')
ax6.fill_between(plot_yearly['Year'], plot_yearly['Success Rate'], alpha=0.3, color='#e91e63')
ax6.set_xlabel('Year')
ax6.set_ylabel('Success Rate %')
ax6.set_title('Profitability Rate Over Time', fontsize=12, fontweight='bold')
ax6.axhline(y=50, color='red', linestyle='--', alpha=0.5)
ax6.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'time_trends_comprehensive.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 13. Comprehensive Correlation Analysis

# %%
# Extended Correlation matrix including all relevant metrics
corr_cols = ['budget_clean', 'revenue_clean', 'profit', 'roi', 'popularity', 
             'vote_average', 'vote_count', 'imdb_score', 'duration',
             'num_critic_for_reviews', 'num_user_for_reviews', 
             'movie_facebook_likes', 'director_facebook_likes', 
             'actor_1_facebook_likes', 'cast_total_facebook_likes']

available_corr_cols = [col for col in corr_cols if col in valid_movies.columns]
corr_matrix = valid_movies[available_corr_cols].corr()

fig, ax = plt.subplots(figsize=(14, 12))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0, fmt='.2f', ax=ax,
            mask=mask, square=True, linewidths=0.5)
ax.set_title('Comprehensive Correlation Matrix: All Key Metrics', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'correlation_matrix_comprehensive.png'), dpi=150)
plt.show()

# Key insights
print("\n📊 KEY CORRELATIONS:")
print(f"Budget ↔ Revenue: {corr_matrix.loc['budget_clean', 'revenue_clean']:.2f}")
print(f"Budget ↔ ROI: {corr_matrix.loc['budget_clean', 'roi']:.2f}")
print(f"Vote Average ↔ Revenue: {corr_matrix.loc['vote_average', 'revenue_clean']:.2f}")
print(f"Popularity ↔ Revenue: {corr_matrix.loc['popularity', 'revenue_clean']:.2f}")
if 'movie_facebook_likes' in corr_matrix.columns:
    print(f"Movie FB Likes ↔ Revenue: {corr_matrix.loc['movie_facebook_likes', 'revenue_clean']:.2f}")
if 'cast_total_facebook_likes' in corr_matrix.columns:
    print(f"Cast FB Likes ↔ Revenue: {corr_matrix.loc['cast_total_facebook_likes', 'revenue_clean']:.2f}")

# %% [markdown]
# ## 14. Social Media Engagement Analysis

# %%
# Facebook Likes Analysis
fb_cols = ['movie_facebook_likes', 'director_facebook_likes', 'cast_total_facebook_likes',
           'actor_1_facebook_likes', 'actor_2_facebook_likes', 'actor_3_facebook_likes']

available_fb = [col for col in fb_cols if col in valid_movies.columns]

print("=" * 70)
print("SOCIAL MEDIA ENGAGEMENT STATISTICS")
print("=" * 70)
print(valid_movies[available_fb].describe().round(0).to_string())

# %%
# Facebook likes vs Success
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# Movie FB Likes vs Revenue
ax1 = axes[0, 0]
ax1.scatter(valid_movies['movie_facebook_likes'] / 1000, 
            valid_movies['revenue_clean'] / 1e6, 
            alpha=0.3, color='#3498db')
ax1.set_xlabel('Movie Facebook Likes (K)')
ax1.set_ylabel('Revenue (Millions $)')
ax1.set_title('Movie Facebook Likes vs Revenue', fontsize=12, fontweight='bold')
ax1.set_xlim(0, valid_movies['movie_facebook_likes'].quantile(0.99) / 1000)

# Cast FB Likes vs Revenue
ax2 = axes[0, 1]
ax2.scatter(valid_movies['cast_total_facebook_likes'] / 1000, 
            valid_movies['revenue_clean'] / 1e6, 
            alpha=0.3, color='#e74c3c')
ax2.set_xlabel('Cast Total Facebook Likes (K)')
ax2.set_ylabel('Revenue (Millions $)')
ax2.set_title('Cast Facebook Likes vs Revenue', fontsize=12, fontweight='bold')
ax2.set_xlim(0, valid_movies['cast_total_facebook_likes'].quantile(0.99) / 1000)

# Director FB Likes vs ROI
ax3 = axes[1, 0]
ax3.scatter(valid_movies['director_facebook_likes'] / 1000, 
            valid_movies['roi'].clip(-100, 500), 
            alpha=0.3, color='#2ecc71')
ax3.set_xlabel('Director Facebook Likes (K)')
ax3.set_ylabel('ROI % (capped)')
ax3.set_title('Director Facebook Likes vs ROI', fontsize=12, fontweight='bold')
ax3.set_xlim(0, valid_movies['director_facebook_likes'].quantile(0.99) / 1000)
ax3.axhline(y=0, color='red', linestyle='--')

# Lead Actor FB Likes vs Profitability (Box plot)
ax4 = axes[1, 1]
valid_movies['actor_fb_tier'] = pd.qcut(valid_movies['actor_1_facebook_likes'].fillna(0), 
                                         q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                                         duplicates='drop')
valid_movies.boxplot(column='roi', by='actor_fb_tier', ax=ax4)
ax4.set_xlabel('Lead Actor Facebook Likes Tier')
ax4.set_ylabel('ROI %')
ax4.set_title('ROI Distribution by Lead Actor Social Influence', fontsize=12, fontweight='bold')
ax4.set_ylim(-200, 500)
plt.suptitle('')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'social_media_analysis.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 15. Top Performers Analysis

# %%
# Top 15 by Revenue
print("🏆 TOP 15 MOVIES BY REVENUE:")
top_revenue = valid_movies.nlargest(15, 'revenue_clean')[
    ['movie_title', 'budget_clean', 'revenue_clean', 'profit', 'roi', 'vote_average', 'imdb_score', 'director_name', 'year']
].copy()
top_revenue['budget_clean'] = (top_revenue['budget_clean'] / 1e6).round(1).astype(str) + 'M'
top_revenue['revenue_clean'] = (top_revenue['revenue_clean'] / 1e6).round(1).astype(str) + 'M'
top_revenue['profit'] = (top_revenue['profit'] / 1e6).round(1).astype(str) + 'M'
top_revenue['roi'] = top_revenue['roi'].round(1).astype(str) + '%'
print(top_revenue.to_string(index=False))

# %%
# Top 15 by ROI (minimum budget $10M to filter outliers)
print("\n🚀 TOP 15 MOVIES BY ROI (Budget > $10M):")
top_roi = valid_movies[valid_movies['budget_clean'] > 10e6].nlargest(15, 'roi')[
    ['movie_title', 'budget_clean', 'revenue_clean', 'profit', 'roi', 'vote_average', 'director_name', 'year']
].copy()
top_roi['budget_clean'] = (top_roi['budget_clean'] / 1e6).round(1).astype(str) + 'M'
top_roi['revenue_clean'] = (top_roi['revenue_clean'] / 1e6).round(1).astype(str) + 'M'
top_roi['profit'] = (top_roi['profit'] / 1e6).round(1).astype(str) + 'M'
top_roi['roi'] = top_roi['roi'].round(1).astype(str) + '%'
print(top_roi.to_string(index=False))

# %%
# Biggest Flops
print("\n💔 BIGGEST FLOPS (Revenue < Budget, sorted by loss):")
flops = valid_movies[valid_movies['profit'] < 0].nsmallest(15, 'profit')[
    ['movie_title', 'budget_clean', 'revenue_clean', 'profit', 'roi', 'director_name', 'year']
].copy()
flops['budget_clean'] = (flops['budget_clean'] / 1e6).round(1).astype(str) + 'M'
flops['revenue_clean'] = (flops['revenue_clean'] / 1e6).round(1).astype(str) + 'M'
flops['profit'] = (flops['profit'] / 1e6).round(1).astype(str) + 'M'
flops['roi'] = flops['roi'].round(1).astype(str) + '%'
print(flops.to_string(index=False))

# %%
# Hidden Gems - High rating, low budget, profitable
print("\n💎 HIDDEN GEMS (Budget < $20M, ROI > 200%, Rating > 7.0):")
hidden_gems = valid_movies[
    (valid_movies['budget_clean'] < 20e6) & 
    (valid_movies['roi'] > 200) & 
    (valid_movies['vote_average'] > 7.0)
].nlargest(15, 'roi')[
    ['movie_title', 'budget_clean', 'revenue_clean', 'profit', 'roi', 'vote_average', 'director_name', 'year']
].copy()
hidden_gems['budget_clean'] = (hidden_gems['budget_clean'] / 1e6).round(1).astype(str) + 'M'
hidden_gems['revenue_clean'] = (hidden_gems['revenue_clean'] / 1e6).round(1).astype(str) + 'M'
hidden_gems['profit'] = (hidden_gems['profit'] / 1e6).round(1).astype(str) + 'M'
hidden_gems['roi'] = hidden_gems['roi'].round(1).astype(str) + '%'
print(hidden_gems.to_string(index=False))

# %% [markdown]
# ## 16. Language & Country Analysis

# %%
# Language Distribution
lang_stats = valid_movies.groupby('original_language').agg({
    'movie_title': 'count',
    'budget_clean': 'mean',
    'revenue_clean': 'mean',
    'roi': 'mean',
    'vote_average': 'mean',
    'profitable': 'mean'
}).reset_index()

lang_stats.columns = ['Language', 'Movies', 'Avg Budget', 'Avg Revenue', 'Avg ROI', 'Avg Rating', 'Success Rate']
lang_stats['Success Rate'] = (lang_stats['Success Rate'] * 100).round(1)
lang_stats = lang_stats.sort_values('Movies', ascending=False)

print("=" * 70)
print("TOP 10 LANGUAGES BY MOVIE COUNT")
print("=" * 70)
print(lang_stats.head(10).to_string(index=False))

# %%
# Language Visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

top_langs = lang_stats.head(10)

ax1 = axes[0]
ax1.bar(top_langs['Language'], top_langs['Movies'], color='#3498db')
ax1.set_xlabel('Original Language')
ax1.set_ylabel('Number of Movies')
ax1.set_title('Movie Count by Language', fontsize=12, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)

ax2 = axes[1]
ax2.bar(top_langs['Language'], top_langs['Avg Revenue'] / 1e6, color='#2ecc71')
ax2.set_xlabel('Original Language')
ax2.set_ylabel('Average Revenue (Millions $)')
ax2.set_title('Average Revenue by Language', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'language_analysis.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 17. Summary Dashboard

# %%
print("=" * 80)
print("📊 COMPREHENSIVE EXPLORATORY DATA ANALYSIS SUMMARY")
print("=" * 80)

print(f"""
================================================================================
                          DATASET OVERVIEW
================================================================================
- Original merged dataset: {len(movies)} movies, {len(movies.columns)} features
- Analysis-ready dataset: {len(valid_movies)} movies (budget > $1M, revenue > 0)
- Date range: {valid_movies['year'].min():.0f} - {valid_movies['year'].max():.0f}
- Unique Directors: {valid_movies['director_name'].nunique()}
- Unique Lead Actors: {valid_movies['actor_1_name'].nunique()}
- Unique Genres: {genre_df['genres_list'].nunique()}
- Content Ratings: {valid_movies['content_rating'].nunique()}

================================================================================
                          FINANCIAL INSIGHTS
================================================================================
- Total Budget (all movies): ${valid_movies['budget_clean'].sum()/1e9:.2f}B
- Total Revenue (all movies): ${valid_movies['revenue_clean'].sum()/1e9:.2f}B
- Total Profit (all movies): ${valid_movies['profit'].sum()/1e9:.2f}B
- Average Budget: ${valid_movies['budget_clean'].mean()/1e6:.1f}M
- Average Revenue: ${valid_movies['revenue_clean'].mean()/1e6:.1f}M
- Average Profit: ${valid_movies['profit'].mean()/1e6:.1f}M
- Average ROI: {valid_movies['roi'].mean():.1f}%
- Median ROI: {valid_movies['roi'].median():.1f}%
- Profitable Movies: {valid_movies['profitable'].sum()} ({valid_movies['profitable'].mean()*100:.1f}%)

================================================================================
                          GENRE INSIGHTS
================================================================================
- Most common genre: {genre_stats.index[0]} ({genre_stats.iloc[0]['Movie Count']:.0f} movies)
- Highest ROI genre: {genre_stats.sort_values('Avg ROI', ascending=False).index[0]} ({genre_stats.sort_values('Avg ROI', ascending=False).iloc[0]['Avg ROI']:.1f}%)
- Highest revenue genre: {genre_stats.sort_values('Avg Revenue', ascending=False).index[0]} (${genre_stats.sort_values('Avg Revenue', ascending=False).iloc[0]['Avg Revenue']/1e6:.1f}M avg)
- Highest success rate: {genre_stats.sort_values('Success Rate', ascending=False).index[0]} ({genre_stats.sort_values('Success Rate', ascending=False).iloc[0]['Success Rate']:.1f}%)

================================================================================
                          KEY CORRELATIONS
================================================================================
- Budget strongly correlates with Revenue (r={corr_matrix.loc['budget_clean', 'revenue_clean']:.2f})
- Budget has weak negative correlation with ROI (r={corr_matrix.loc['budget_clean', 'roi']:.2f})
- Popularity is a moderate predictor of revenue (r={corr_matrix.loc['popularity', 'revenue_clean']:.2f})
- Vote Average weakly correlates with revenue (r={corr_matrix.loc['vote_average', 'revenue_clean']:.2f})

================================================================================
                          TOP PERFORMERS
================================================================================
- Highest Grossing: {valid_movies.nlargest(1, 'revenue_clean')['movie_title'].values[0]} (${valid_movies.nlargest(1, 'revenue_clean')['revenue_clean'].values[0]/1e9:.2f}B)
- Highest ROI (>$10M budget): {valid_movies[valid_movies['budget_clean']>10e6].nlargest(1, 'roi')['movie_title'].values[0]} ({valid_movies[valid_movies['budget_clean']>10e6].nlargest(1, 'roi')['roi'].values[0]:.0f}%)
- Top Director by Revenue: {prolific_directors.iloc[0]['Director']} ({prolific_directors.iloc[0]['Movies']} movies)
- Top Lead Actor by Revenue: {prolific_actors.iloc[0]['Lead Actor']} ({prolific_actors.iloc[0]['Movies']} movies)

================================================================================
                          RECOMMENDATIONS FOR NEXT STEPS
================================================================================
1. Clean and transform data for Tableau dashboard
2. Investigate low-budget high-ROI success factors
3. Analyze genre trends over time
4. Build investment-to-profitability funnel analysis
5. Deep dive into director and actor success patterns
6. Social media engagement impact study
7. Content rating strategy optimization
""")

# %%
# Save processed dataframe for future use
output_file = os.path.join(output_dir, 'movies_eda_comprehensive.csv')
valid_movies.to_csv(output_file, index=False)
print(f"\n✅ Comprehensive cleaned data saved to: {output_file}")
print(f"   Records: {len(valid_movies)}")
print(f"   Columns: {len(valid_movies.columns)}")

# Also save the full movies dataset with calculated fields for Tableau
full_output = os.path.join(output_dir, 'movies_full_analysis.csv')
movies['budget_clean'] = pd.to_numeric(movies['budget'], errors='coerce')
movies['revenue_clean'] = pd.to_numeric(movies['revenue'], errors='coerce').fillna(
    pd.to_numeric(movies['gross'], errors='coerce')
)
movies['profit'] = movies['revenue_clean'] - movies['budget_clean']
movies['roi'] = (movies['profit'] / movies['budget_clean'] * 100).round(2)
movies['profitable'] = movies['profit'] > 0
movies.to_csv(full_output, index=False)
print(f"\n✅ Full dataset with calculated fields saved to: {full_output}")
print(f"   Records: {len(movies)}")
print(f"   Columns: {len(movies.columns)}")

# %% [markdown]
# ## Generated Outputs
# 
# This analysis generated the following files in the `outputs/` directory:
# 
# **Visualizations:**
# 1. `missing_data_analysis.png` - Missing data patterns
# 2. `distributions_comprehensive.png` - Financial and rating distributions
# 3. `budget_vs_revenue_comprehensive.png` - Investment landscape scatter plot
# 4. `genre_analysis_comprehensive.png` - Genre performance analysis
# 5. `director_analysis.png` - Director performance metrics
# 6. `actor_analysis.png` - Lead actor analysis
# 7. `content_rating_analysis.png` - Content rating performance
# 8. `time_trends_comprehensive.png` - Historical trends
# 9. `correlation_matrix_comprehensive.png` - All variable correlations
# 10. `social_media_analysis.png` - Social media engagement impact
# 11. `language_analysis.png` - Language distribution
# 
# **Data Files:**
# 1. `movies_eda_comprehensive.csv` - Cleaned analysis-ready dataset
# 2. `movies_full_analysis.csv` - Full dataset with calculated fields for Tableau
