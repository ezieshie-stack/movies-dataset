# %% [markdown]
# # 🎬 Movies Dataset — Full Data Merge & Clean
# 
# Merges ALL available data sources into a single, Tableau-ready dataset:
# - tmdb_5000_movies.csv (4,803 rows)
# - movie_metadata.csv (5,043 rows)
# - tmdb_5000_movies_mergedwith_movie_metadata.csv (5,009 rows — pre-merged)
# - movies_genres_summary.csv (genre-level aggregates)

# %%
import pandas as pd
import numpy as np
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
base_dir = os.path.dirname(script_dir) if 'notebooks' in script_dir else script_dir
data_dir = os.path.join(base_dir, 'data')
output_dir = os.path.join(base_dir, 'outputs')
os.makedirs(output_dir, exist_ok=True)

# %% [markdown]
# ## 1. Load All Data Sources

# %%
# Use the pre-merged file as the base (most complete)
df = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies_mergedwith_movie_metadata.csv'), encoding='latin1')
print(f"Base merged dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Columns: {list(df.columns)}")

# Load genres summary for reference
genres_summary = pd.read_csv(os.path.join(data_dir, 'movies_genres_summary.csv'))
print(f"\nGenres summary: {genres_summary.shape[0]} rows")

# %% [markdown]
# ## 2. Clean Movie Titles

# %%
# Fix encoding issues (trailing characters like Â)
df['movie_title'] = df['movie_title'].str.strip()
df['movie_title'] = df['movie_title'].str.replace('\xa0', '', regex=False)
df['movie_title'] = df['movie_title'].str.replace('Â', '', regex=False)
print("✅ Movie titles cleaned")
print(f"Sample: {df['movie_title'].head(5).tolist()}")

# %% [markdown]
# ## 3. Parse JSON Columns

# %%
def parse_json_names(json_str, key='name'):
    """Extract names from JSON-like strings."""
    if pd.isna(json_str):
        return ''
    try:
        items = json.loads(str(json_str).replace("'", '"'))
        return '|'.join([item[key] for item in items if key in item])
    except:
        return str(json_str)

# Parse genres (already pipe-separated in merged file, but let's verify)
# The merged file has genres like "Action|Adventure|Fantasy|Sci-Fi"
print("Genre sample:", df['genres'].head(3).tolist())

# Parse production companies
df['production_companies_parsed'] = df['production_companies'].apply(parse_json_names)

# Parse keywords
df['keywords_parsed'] = df['keywords'].apply(parse_json_names)

# Parse production countries
df['production_countries_parsed'] = df['production_countries'].apply(
    lambda x: parse_json_names(x, key='name')
)

# Parse spoken languages
df['spoken_languages_parsed'] = df['spoken_languages'].apply(
    lambda x: parse_json_names(x, key='name')
)

print("✅ JSON columns parsed")

# %%
# Extract primary values for each parsed column
df['primary_genre'] = df['genres'].apply(lambda x: str(x).split('|')[0] if pd.notna(x) else 'Unknown')
df['primary_company'] = df['production_companies_parsed'].apply(lambda x: str(x).split('|')[0] if x else 'Unknown')
df['primary_country'] = df['production_countries_parsed'].apply(lambda x: str(x).split('|')[0] if x else 'Unknown')
df['genre_count'] = df['genres'].apply(lambda x: len(str(x).split('|')) if pd.notna(x) else 0)

print("✅ Primary values extracted")
print(f"Top genres: {df['primary_genre'].value_counts().head(10).to_dict()}")

# %% [markdown]
# ## 4. Handle Missing Values & Data Types

# %%
print("Missing values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])
print()

# Fill numerical nulls
df['gross'] = df['gross'].fillna(0)
df['duration'] = df['duration'].fillna(df['duration'].median())
df['runtime'] = df['runtime'].fillna(df['runtime'].median())
df['title_year'] = df['title_year'].fillna(0).astype(int)
df['aspect_ratio'] = df['aspect_ratio'].fillna(df['aspect_ratio'].median())
df['num_critic_for_reviews'] = df['num_critic_for_reviews'].fillna(0)
df['num_user_for_reviews'] = df['num_user_for_reviews'].fillna(0)
df['facenumber_in_poster'] = df['facenumber_in_poster'].fillna(0)

# Fill facebook likes nulls
for col in ['director_facebook_likes', 'actor_1_facebook_likes', 'actor_2_facebook_likes', 'actor_3_facebook_likes']:
    df[col] = df[col].fillna(0)

# Fill categorical nulls
df['director_name'] = df['director_name'].fillna('Unknown')
df['actor_1_name'] = df['actor_1_name'].fillna('Unknown')
df['actor_2_name'] = df['actor_2_name'].fillna('Unknown')
df['actor_3_name'] = df['actor_3_name'].fillna('Unknown')
df['content_rating'] = df['content_rating'].fillna('Not Rated')
df['overview'] = df['overview'].fillna('')
df['tagline'] = df['tagline'].fillna('')

print("Missing values after cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# %% [markdown]
# ## 5. Create Calculated Fields

# %%
# Use best revenue figure (revenue from TMDB, gross from IMDB)
df['best_revenue'] = df.apply(
    lambda row: row['revenue'] if row['revenue'] > 0 else row['gross'], axis=1
)

# Profit and ROI
df['profit'] = df['best_revenue'] - df['budget']
df['roi'] = np.where(
    df['budget'] > 0,
    (df['best_revenue'] - df['budget']) / df['budget'] * 100,
    0
)

# Profitability flags
df['is_profitable'] = (df['profit'] > 0) & (df['budget'] > 0) & (df['best_revenue'] > 0)
df['profit_category'] = pd.cut(
    df['roi'],
    bins=[-np.inf, -50, 0, 100, 300, np.inf],
    labels=['Major Loss', 'Loss', 'Moderate Return', 'Strong Return', 'Blockbuster Return']
)

# Release decade
df['decade'] = (df['title_year'] // 10 * 10).astype(int)
df['decade_label'] = df['decade'].apply(lambda x: f"{x}s" if x > 0 else 'Unknown')

# Budget tier
df['budget_tier'] = pd.cut(
    df['budget'],
    bins=[0, 1e6, 10e6, 50e6, 100e6, np.inf],
    labels=['Micro (<$1M)', 'Low ($1-10M)', 'Mid ($10-50M)', 'High ($50-100M)', 'Mega ($100M+)']
)

# Rating category
df['rating_category'] = pd.cut(
    df['vote_average'],
    bins=[0, 4, 5.5, 7, 8, 10],
    labels=['Poor', 'Below Average', 'Average', 'Good', 'Excellent']
)

# Total social media buzz
df['total_facebook_likes'] = (
    df['movie_facebook_likes'] + df['director_facebook_likes'] +
    df['cast_total_facebook_likes']
)

# Parse release date for more granularity
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_month'] = df['release_date'].dt.month
df['release_quarter'] = df['release_date'].dt.quarter
df['release_day_of_week'] = df['release_date'].dt.day_name()

# Season
def get_season(month):
    if pd.isna(month):
        return 'Unknown'
    month = int(month)
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

df['release_season'] = df['release_month'].apply(get_season)

print("✅ Calculated fields created")
print(f"New columns added: profit, roi, is_profitable, profit_category, decade, budget_tier, rating_category, total_facebook_likes, release_month/quarter/season")

# %% [markdown]
# ## 6. Final Quality Check

# %%
print("=" * 60)
print("FINAL DATASET SUMMARY")
print("=" * 60)
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nAll columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2}. {col} ({df[col].dtype})")

# %%
# Key stats
valid = df[(df['budget'] > 1e6) & (df['best_revenue'] > 0)]
print(f"\n📊 KEY STATISTICS (movies with budget > $1M):")
print(f"  Movies: {len(valid)}")
print(f"  Profitable: {valid['is_profitable'].sum()} ({valid['is_profitable'].mean()*100:.1f}%)")
print(f"  Avg Budget: ${valid['budget'].mean()/1e6:.1f}M")
print(f"  Avg Revenue: ${valid['best_revenue'].mean()/1e6:.1f}M")
print(f"  Avg ROI: {valid['roi'].mean():.1f}%")
print(f"  Top Director: {valid.groupby('director_name')['best_revenue'].sum().idxmax()}")
print(f"  Top Actor: {valid.groupby('actor_1_name')['best_revenue'].sum().idxmax()}")
print(f"  Top Genre: {valid.groupby('primary_genre')['best_revenue'].sum().idxmax()}")

# %% [markdown]
# ## 7. Export for Tableau

# %%
# Select and order columns for Tableau
tableau_columns = [
    # Identifiers
    'id', 'movie_title', 'original_title',
    
    # Core metrics
    'budget', 'gross', 'revenue', 'best_revenue', 'profit', 'roi',
    
    # Ratings
    'vote_average', 'vote_count', 'imdb_score', 'popularity',
    'num_critic_for_reviews', 'num_user_for_reviews', 'num_voted_users',
    
    # Categories
    'genres', 'primary_genre', 'genre_count', 'content_rating',
    'is_profitable', 'profit_category', 'budget_tier', 'rating_category',
    
    # Time
    'release_date', 'title_year', 'decade', 'decade_label',
    'release_month', 'release_quarter', 'release_day_of_week', 'release_season',
    
    # People
    'director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name',
    
    # Production
    'production_companies_parsed', 'primary_company',
    'production_countries_parsed', 'primary_country',
    'original_language',
    
    # Social Media
    'movie_facebook_likes', 'director_facebook_likes',
    'cast_total_facebook_likes', 'actor_1_facebook_likes',
    'actor_2_facebook_likes', 'actor_3_facebook_likes',
    'total_facebook_likes',
    
    # Movie Details
    'duration', 'runtime', 'overview', 'tagline',
    'keywords_parsed', 'status',
]

df_tableau = df[tableau_columns].copy()

# Export
output_path = os.path.join(output_dir, 'movies_full_eda.csv')
df_tableau.to_csv(output_path, index=False)
print(f"\n✅ Full EDA dataset exported: {output_path}")
print(f"   Rows: {len(df_tableau)}, Columns: {len(df_tableau.columns)}")

# Also save a quick summary
print(f"\n📋 COLUMN SUMMARY FOR TABLEAU:")
for col in tableau_columns:
    dtype = df_tableau[col].dtype
    nulls = df_tableau[col].isnull().sum()
    print(f"   {col:40s} | {str(dtype):10s} | nulls: {nulls}")
