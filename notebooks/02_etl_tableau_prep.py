# %% [markdown]
# # 🎬 Movies Dataset - ETL & Tableau Data Preparation
# 
# This notebook transforms the merged movies dataset into a clean, 
# Tableau-ready format with:
# 
# 1. **Data Cleaning** - Handle missing values, standardize formats
# 2. **Feature Engineering** - Create calculated fields for analysis
# 3. **Genre Explosion** - One row per movie-genre for flexible analysis
# 4. **Categorical Encoding** - Create analysis-friendly categories
# 5. **Export** - Multiple CSV files optimized for Tableau

# %% [markdown]
# ## 1. Setup & Load Data

# %%
import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.filterwarnings('ignore')

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
base_dir = os.path.dirname(script_dir) if 'notebooks' in script_dir else script_dir
data_dir = os.path.join(base_dir, 'data')
output_dir = os.path.join(base_dir, 'outputs')
tableau_dir = os.path.join(output_dir, 'tableau')
os.makedirs(tableau_dir, exist_ok=True)

# Load merged dataset
df = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies_mergedwith_movie_metadata.csv'), encoding='latin1')
print(f"📊 Loaded {len(df)} movies with {len(df.columns)} columns")

# %% [markdown]
# ## 2. Data Cleaning

# %%
# Create a clean copy
movies = df.copy()

# -------------------- FINANCIAL CLEANING --------------------
print("=" * 60)
print("FINANCIAL DATA CLEANING")
print("=" * 60)

# Clean budget
movies['Budget'] = pd.to_numeric(movies['budget'], errors='coerce')

# Clean revenue - use revenue first, then gross as fallback
movies['Revenue'] = pd.to_numeric(movies['revenue'], errors='coerce')
gross_values = pd.to_numeric(movies['gross'], errors='coerce')

# Fill missing revenue with gross
movies['Revenue'] = movies['Revenue'].fillna(gross_values)

# For movies with 0 revenue but valid gross, use gross
movies.loc[(movies['Revenue'] == 0) & (gross_values > 0), 'Revenue'] = gross_values[(movies['Revenue'] == 0) & (gross_values > 0)]

print(f"Budget: {movies['Budget'].notna().sum()} valid values")
print(f"Revenue: {movies['Revenue'].notna().sum()} valid values")

# -------------------- CALCULATE FINANCIAL METRICS --------------------
movies['Profit'] = movies['Revenue'] - movies['Budget']
movies['ROI'] = ((movies['Revenue'] - movies['Budget']) / movies['Budget'] * 100).round(2)
movies['Profit_Margin'] = ((movies['Revenue'] - movies['Budget']) / movies['Revenue'] * 100).round(2)
movies['Is_Profitable'] = movies['Profit'] > 0

# Budget to Revenue Ratio
movies['Revenue_to_Budget_Ratio'] = (movies['Revenue'] / movies['Budget']).round(2)

print(f"\nCalculated metrics for {movies['ROI'].notna().sum()} movies")

# %%
# -------------------- DATE CLEANING --------------------
print("\n" + "=" * 60)
print("DATE CLEANING")
print("=" * 60)

# Parse release date
movies['Release_Date'] = pd.to_datetime(movies['release_date'], errors='coerce')
movies['Year'] = movies['Release_Date'].dt.year

# Fill missing years from title_year
movies['Year'] = movies['Year'].fillna(movies['title_year'])
movies['Year'] = movies['Year'].astype('Int64')  # Nullable integer

# Extract additional date components
movies['Month'] = movies['Release_Date'].dt.month
movies['Quarter'] = movies['Release_Date'].dt.quarter
movies['Day_of_Week'] = movies['Release_Date'].dt.dayofweek
movies['Month_Name'] = movies['Release_Date'].dt.month_name()

print(f"Years extracted: {movies['Year'].notna().sum()} valid values")
print(f"Year range: {movies['Year'].min()} - {movies['Year'].max()}")

# %%
# -------------------- RATING CLEANING --------------------
print("\n" + "=" * 60)
print("RATING CLEANING")
print("=" * 60)

# Clean ratings
movies['TMDB_Rating'] = pd.to_numeric(movies['vote_average'], errors='coerce')
movies['IMDB_Rating'] = pd.to_numeric(movies['imdb_score'], errors='coerce')
movies['Vote_Count'] = pd.to_numeric(movies['vote_count'], errors='coerce')
movies['Popularity'] = pd.to_numeric(movies['popularity'], errors='coerce')

# Combined rating (average of TMDB and IMDB if both exist)
movies['Combined_Rating'] = movies[['TMDB_Rating', 'IMDB_Rating']].mean(axis=1).round(2)

print(f"TMDB Ratings: {movies['TMDB_Rating'].notna().sum()} valid")
print(f"IMDB Ratings: {movies['IMDB_Rating'].notna().sum()} valid")
print(f"Combined Ratings: {movies['Combined_Rating'].notna().sum()} valid")

# %%
# -------------------- DURATION CLEANING --------------------
print("\n" + "=" * 60)
print("DURATION CLEANING")
print("=" * 60)

# Use runtime first, then duration as fallback
movies['Runtime_Minutes'] = pd.to_numeric(movies['runtime'], errors='coerce')
duration_values = pd.to_numeric(movies['duration'], errors='coerce')
movies['Runtime_Minutes'] = movies['Runtime_Minutes'].fillna(duration_values)

print(f"Runtime: {movies['Runtime_Minutes'].notna().sum()} valid values")
print(f"Range: {movies['Runtime_Minutes'].min():.0f} - {movies['Runtime_Minutes'].max():.0f} minutes")

# %% [markdown]
# ## 3. Categorical Feature Engineering

# %%
# -------------------- BUDGET CATEGORIES --------------------
print("=" * 60)
print("CATEGORICAL FEATURE ENGINEERING")
print("=" * 60)

def categorize_budget(budget):
    if pd.isna(budget) or budget <= 0:
        return 'Unknown'
    elif budget < 5_000_000:
        return 'Micro (<$5M)'
    elif budget < 15_000_000:
        return 'Low ($5M-$15M)'
    elif budget < 40_000_000:
        return 'Medium ($15M-$40M)'
    elif budget < 100_000_000:
        return 'High ($40M-$100M)'
    else:
        return 'Blockbuster (>$100M)'

movies['Budget_Category'] = movies['Budget'].apply(categorize_budget)
print("Budget Categories:")
print(movies['Budget_Category'].value_counts())

# %%
# -------------------- ROI CATEGORIES --------------------
def categorize_roi(roi):
    if pd.isna(roi):
        return 'Unknown'
    elif roi < -50:
        return 'Major Flop (<-50%)'
    elif roi < 0:
        return 'Flop (-50% to 0%)'
    elif roi < 100:
        return 'Moderate (0%-100%)'
    elif roi < 300:
        return 'Successful (100%-300%)'
    elif roi < 1000:
        return 'Hit (300%-1000%)'
    else:
        return 'Blockbuster (>1000%)'

movies['ROI_Category'] = movies['ROI'].apply(categorize_roi)
print("\nROI Categories:")
print(movies['ROI_Category'].value_counts())

# %%
# -------------------- RATING CATEGORIES --------------------
def categorize_rating(rating):
    if pd.isna(rating):
        return 'Unknown'
    elif rating < 5:
        return 'Poor (<5)'
    elif rating < 6:
        return 'Below Average (5-6)'
    elif rating < 7:
        return 'Average (6-7)'
    elif rating < 8:
        return 'Good (7-8)'
    else:
        return 'Excellent (8+)'

movies['Rating_Category'] = movies['Combined_Rating'].apply(categorize_rating)
print("\nRating Categories:")
print(movies['Rating_Category'].value_counts())

# %%
# -------------------- ERA CATEGORIES --------------------
def categorize_era(year):
    if pd.isna(year):
        return 'Unknown'
    elif year < 1970:
        return 'Classic (<1970)'
    elif year < 1990:
        return 'Pre-Digital (1970-1989)'
    elif year < 2000:
        return '90s Era (1990-1999)'
    elif year < 2010:
        return '2000s (2000-2009)'
    else:
        return 'Modern (2010+)'

movies['Era'] = movies['Year'].apply(categorize_era)
print("\nEra Categories:")
print(movies['Era'].value_counts())

# %%
# -------------------- RUNTIME CATEGORIES --------------------
def categorize_runtime(runtime):
    if pd.isna(runtime):
        return 'Unknown'
    elif runtime < 90:
        return 'Short (<90 min)'
    elif runtime < 120:
        return 'Standard (90-120 min)'
    elif runtime < 150:
        return 'Long (120-150 min)'
    else:
        return 'Epic (>150 min)'

movies['Runtime_Category'] = movies['Runtime_Minutes'].apply(categorize_runtime)
print("\nRuntime Categories:")
print(movies['Runtime_Category'].value_counts())

# %% [markdown]
# ## 4. Text Field Cleaning

# %%
# Clean movie title
movies['Title'] = movies['movie_title'].str.strip()

# Clean director name
movies['Director'] = movies['director_name'].str.strip()

# Clean actor names
movies['Lead_Actor'] = movies['actor_1_name'].str.strip()
movies['Actor_2'] = movies['actor_2_name'].str.strip()
movies['Actor_3'] = movies['actor_3_name'].str.strip()

# Clean content rating
movies['Content_Rating'] = movies['content_rating'].str.strip()
movies['Content_Rating'] = movies['Content_Rating'].replace({
    'Not Rated': 'NR',
    'Unrated': 'NR',
    'TV-14': 'PG-13',
    'TV-MA': 'R',
    'TV-PG': 'PG',
    'Passed': 'G',
    'Approved': 'G',
    'GP': 'PG',
    'M': 'PG'
})

# Clean language
movies['Language'] = movies['original_language'].str.upper()

print("=" * 60)
print("TEXT FIELD CLEANING COMPLETE")
print("=" * 60)
print(f"Unique Directors: {movies['Director'].nunique()}")
print(f"Unique Lead Actors: {movies['Lead_Actor'].nunique()}")
print(f"Content Ratings: {movies['Content_Rating'].nunique()}")
print(f"Languages: {movies['Language'].nunique()}")

# %% [markdown]
# ## 5. Genre Parsing & Explosion

# %%
# Parse genres from JSON
def parse_genres(genre_str):
    try:
        if pd.isna(genre_str):
            return []
        # Handle JSON format
        if '[' in str(genre_str):
            genres = json.loads(str(genre_str).replace("'", '"'))
            if isinstance(genres, list):
                return [g.get('name', g) if isinstance(g, dict) else str(g) for g in genres]
        # Handle pipe-separated format
        return [g.strip() for g in str(genre_str).split('|') if g.strip()]
    except:
        return []

movies['Genres_List'] = movies['genres'].apply(parse_genres)
movies['Genre_Count'] = movies['Genres_List'].apply(len)
movies['Primary_Genre'] = movies['Genres_List'].apply(lambda x: x[0] if len(x) > 0 else 'Unknown')
movies['All_Genres'] = movies['Genres_List'].apply(lambda x: ', '.join(x) if len(x) > 0 else 'Unknown')

print("=" * 60)
print("GENRE PARSING COMPLETE")
print("=" * 60)
print(f"Movies with genres: {(movies['Genre_Count'] > 0).sum()}")
print(f"Average genres per movie: {movies['Genre_Count'].mean():.2f}")
print(f"\nPrimary Genre Distribution:")
print(movies['Primary_Genre'].value_counts().head(10))

# %% [markdown]
# ## 6. Social Media Metrics

# %%
# Clean social media metrics
movies['Movie_FB_Likes'] = pd.to_numeric(movies['movie_facebook_likes'], errors='coerce').fillna(0).astype(int)
movies['Director_FB_Likes'] = pd.to_numeric(movies['director_facebook_likes'], errors='coerce').fillna(0).astype(int)
movies['Cast_FB_Likes'] = pd.to_numeric(movies['cast_total_facebook_likes'], errors='coerce').fillna(0).astype(int)
movies['Lead_Actor_FB_Likes'] = pd.to_numeric(movies['actor_1_facebook_likes'], errors='coerce').fillna(0).astype(int)

# Total social engagement
movies['Total_Social_Engagement'] = movies['Movie_FB_Likes'] + movies['Cast_FB_Likes'] + movies['Director_FB_Likes']

# Social engagement category
def categorize_social(engagement):
    if engagement == 0:
        return 'None'
    elif engagement < 1000:
        return 'Low (<1K)'
    elif engagement < 10000:
        return 'Medium (1K-10K)'
    elif engagement < 50000:
        return 'High (10K-50K)'
    else:
        return 'Viral (>50K)'

movies['Social_Category'] = movies['Total_Social_Engagement'].apply(categorize_social)

print("=" * 60)
print("SOCIAL MEDIA METRICS")
print("=" * 60)
print(movies['Social_Category'].value_counts())

# %% [markdown]
# ## 7. Create Funnel Metrics (Investment-to-Profitability)

# %%
print("=" * 60)
print("INVESTMENT-TO-PROFITABILITY FUNNEL")
print("=" * 60)

# Define funnel stages based on financial performance
def assign_funnel_stage(row):
    budget = row['Budget']
    revenue = row['Revenue']
    roi = row['ROI']
    
    if pd.isna(budget) or budget <= 0:
        return '0_No_Investment_Data'
    elif pd.isna(revenue) or revenue <= 0:
        return '1_Invested_No_Revenue'
    elif revenue < budget * 0.5:
        return '2_Major_Loss'
    elif revenue < budget:
        return '3_Partial_Recovery'
    elif revenue < budget * 1.5:
        return '4_Break_Even'
    elif revenue < budget * 2:
        return '5_Moderate_Profit'
    elif revenue < budget * 3:
        return '6_Strong_Profit'
    else:
        return '7_Exceptional_ROI'

movies['Funnel_Stage'] = movies.apply(assign_funnel_stage, axis=1)

# Funnel stage order for visualization
funnel_order = [
    '0_No_Investment_Data',
    '1_Invested_No_Revenue',
    '2_Major_Loss',
    '3_Partial_Recovery',
    '4_Break_Even',
    '5_Moderate_Profit',
    '6_Strong_Profit',
    '7_Exceptional_ROI'
]

movies['Funnel_Order'] = movies['Funnel_Stage'].apply(lambda x: funnel_order.index(x))

print("\nFunnel Stage Distribution:")
funnel_counts = movies['Funnel_Stage'].value_counts().reindex(funnel_order)
for stage, count in funnel_counts.items():
    pct = count / len(movies) * 100
    print(f"  {stage}: {count} ({pct:.1f}%)")

# Calculate conversion rates
print("\nFunnel Conversion Analysis:")
total = len(movies)
invested = (movies['Budget'] > 0).sum()
has_revenue = (movies['Revenue'] > 0).sum()
profitable = (movies['Profit'] > 0).sum()
strong_roi = (movies['ROI'] > 200).sum()

print(f"  Total Movies: {total}")
print(f"  With Budget Data: {invested} ({invested/total*100:.1f}%)")
print(f"  Generated Revenue: {has_revenue} ({has_revenue/invested*100:.1f}% of invested)")
print(f"  Profitable: {profitable} ({profitable/has_revenue*100:.1f}% of revenue-generating)")
print(f"  Strong ROI (>200%): {strong_roi} ({strong_roi/profitable*100:.1f}% of profitable)")

# %% [markdown]
# ## 8. Create Clean Tableau Dataset

# %%
# Select and rename columns for Tableau
tableau_columns = [
    # Identifiers
    'id', 'Title', 'Year', 'Month', 'Quarter', 'Month_Name', 'Era',
    
    # Financial
    'Budget', 'Revenue', 'Profit', 'ROI', 'Profit_Margin', 
    'Revenue_to_Budget_Ratio', 'Is_Profitable',
    'Budget_Category', 'ROI_Category', 'Funnel_Stage', 'Funnel_Order',
    
    # Ratings
    'TMDB_Rating', 'IMDB_Rating', 'Combined_Rating', 'Rating_Category',
    'Vote_Count', 'Popularity',
    
    # Content
    'Primary_Genre', 'All_Genres', 'Genre_Count',
    'Content_Rating', 'Runtime_Minutes', 'Runtime_Category',
    'Language',
    
    # People
    'Director', 'Lead_Actor', 'Actor_2', 'Actor_3',
    
    # Social
    'Movie_FB_Likes', 'Director_FB_Likes', 'Cast_FB_Likes', 
    'Lead_Actor_FB_Likes', 'Total_Social_Engagement', 'Social_Category',
    
    # Reviews
    'num_critic_for_reviews', 'num_user_for_reviews'
]

# Create Tableau-ready dataset
tableau_df = movies[tableau_columns].copy()

# Rename columns for Tableau (remove underscores for cleaner display)
tableau_df.columns = [col.replace('_', ' ') for col in tableau_df.columns]

print("=" * 60)
print("TABLEAU DATASET CREATED")
print("=" * 60)
print(f"Records: {len(tableau_df)}")
print(f"Columns: {len(tableau_df.columns)}")

# %% [markdown]
# ## 9. Create Genre-Exploded Table (For Many-to-Many Analysis)

# %%
# Create exploded genre table for genre-specific analysis
genre_exploded = movies[['id', 'Title', 'Year', 'Budget', 'Revenue', 'Profit', 'ROI', 
                          'Combined_Rating', 'Director', 'Lead_Actor', 'Funnel_Stage']].copy()
genre_exploded['Genre'] = movies['Genres_List']
genre_exploded = genre_exploded.explode('Genre')
genre_exploded = genre_exploded[genre_exploded['Genre'].notna() & (genre_exploded['Genre'] != '')]

print("=" * 60)
print("GENRE-EXPLODED TABLE")
print("=" * 60)
print(f"Records: {len(genre_exploded)}")
print(f"Unique Movies: {genre_exploded['id'].nunique()}")
print(f"Unique Genres: {genre_exploded['Genre'].nunique()}")

# %% [markdown]
# ## 10. Create Director Performance Table

# %%
# Aggregate director statistics
director_stats = movies[movies['Director'].notna()].groupby('Director').agg({
    'Title': 'count',
    'Budget': 'sum',
    'Revenue': 'sum',
    'Profit': 'sum',
    'ROI': 'mean',
    'Combined_Rating': 'mean',
    'Is_Profitable': 'mean',
    'Director_FB_Likes': 'first'
}).reset_index()

director_stats.columns = ['Director', 'Movie Count', 'Total Budget', 'Total Revenue', 
                          'Total Profit', 'Avg ROI', 'Avg Rating', 'Success Rate', 'FB Likes']
director_stats['Success Rate'] = (director_stats['Success Rate'] * 100).round(1)
director_stats = director_stats.sort_values('Total Revenue', ascending=False)

print("=" * 60)
print("DIRECTOR PERFORMANCE TABLE")
print("=" * 60)
print(f"Directors: {len(director_stats)}")
print(f"\nTop 10 by Revenue:")
print(director_stats.head(10)[['Director', 'Movie Count', 'Total Revenue', 'Avg ROI', 'Success Rate']].to_string(index=False))

# %% [markdown]
# ## 11. Create Actor Performance Table

# %%
# Aggregate lead actor statistics
actor_stats = movies[movies['Lead_Actor'].notna()].groupby('Lead_Actor').agg({
    'Title': 'count',
    'Budget': 'sum',
    'Revenue': 'sum',
    'Profit': 'sum',
    'ROI': 'mean',
    'Combined_Rating': 'mean',
    'Is_Profitable': 'mean',
    'Lead_Actor_FB_Likes': 'first'
}).reset_index()

actor_stats.columns = ['Lead Actor', 'Movie Count', 'Total Budget', 'Total Revenue', 
                       'Total Profit', 'Avg ROI', 'Avg Rating', 'Success Rate', 'FB Likes']
actor_stats['Success Rate'] = (actor_stats['Success Rate'] * 100).round(1)
actor_stats = actor_stats.sort_values('Total Revenue', ascending=False)

print("=" * 60)
print("ACTOR PERFORMANCE TABLE")
print("=" * 60)
print(f"Lead Actors: {len(actor_stats)}")
print(f"\nTop 10 by Revenue:")
print(actor_stats.head(10)[['Lead Actor', 'Movie Count', 'Total Revenue', 'Avg ROI', 'Success Rate']].to_string(index=False))

# %% [markdown]
# ## 12. Create Yearly Trend Table

# %%
# Aggregate yearly statistics
yearly_stats = movies[movies['Year'].notna()].groupby('Year').agg({
    'Title': 'count',
    'Budget': 'mean',
    'Revenue': 'mean',
    'Profit': 'mean',
    'ROI': 'mean',
    'Combined_Rating': 'mean',
    'Is_Profitable': 'mean',
    'Total_Social_Engagement': 'mean'
}).reset_index()

yearly_stats.columns = ['Year', 'Movie Count', 'Avg Budget', 'Avg Revenue', 
                        'Avg Profit', 'Avg ROI', 'Avg Rating', 'Success Rate', 'Avg Social']
yearly_stats['Success Rate'] = (yearly_stats['Success Rate'] * 100).round(1)
yearly_stats = yearly_stats.sort_values('Year')

print("=" * 60)
print("YEARLY TREND TABLE")
print("=" * 60)
print(f"Years covered: {len(yearly_stats)}")
print(f"Range: {yearly_stats['Year'].min()} - {yearly_stats['Year'].max()}")

# %% [markdown]
# ## 13. Export All Tables

# %%
print("=" * 60)
print("EXPORTING TABLEAU DATASETS")
print("=" * 60)

# 1. Main Movie Table
main_file = os.path.join(tableau_dir, 'movies_main.csv')
tableau_df.to_csv(main_file, index=False)
print(f"✅ Main Movies Table: {main_file}")
print(f"   Records: {len(tableau_df)}, Columns: {len(tableau_df.columns)}")

# 2. Genre-Exploded Table
genre_file = os.path.join(tableau_dir, 'movies_by_genre.csv')
genre_exploded.to_csv(genre_file, index=False)
print(f"✅ Genre Analysis Table: {genre_file}")
print(f"   Records: {len(genre_exploded)}")

# 3. Director Performance Table
director_file = os.path.join(tableau_dir, 'director_performance.csv')
director_stats.to_csv(director_file, index=False)
print(f"✅ Director Performance: {director_file}")
print(f"   Records: {len(director_stats)}")

# 4. Actor Performance Table
actor_file = os.path.join(tableau_dir, 'actor_performance.csv')
actor_stats.to_csv(actor_file, index=False)
print(f"✅ Actor Performance: {actor_file}")
print(f"   Records: {len(actor_stats)}")

# 5. Yearly Trends Table
yearly_file = os.path.join(tableau_dir, 'yearly_trends.csv')
yearly_stats.to_csv(yearly_file, index=False)
print(f"✅ Yearly Trends: {yearly_file}")
print(f"   Records: {len(yearly_stats)}")

# 6. Funnel Analysis Table (Aggregated)
funnel_agg = movies.groupby('Funnel_Stage').agg({
    'Title': 'count',
    'Budget': 'sum',
    'Revenue': 'sum',
    'Profit': 'sum',
    'ROI': 'mean',
    'Combined_Rating': 'mean'
}).reset_index()
funnel_agg.columns = ['Funnel Stage', 'Movie Count', 'Total Budget', 'Total Revenue', 
                      'Total Profit', 'Avg ROI', 'Avg Rating']
funnel_agg['Stage Order'] = funnel_agg['Funnel Stage'].apply(lambda x: funnel_order.index(x))
funnel_agg = funnel_agg.sort_values('Stage Order')

funnel_file = os.path.join(tableau_dir, 'funnel_analysis.csv')
funnel_agg.to_csv(funnel_file, index=False)
print(f"✅ Funnel Analysis: {funnel_file}")
print(f"   Records: {len(funnel_agg)}")

# %% [markdown]
# ## 14. Summary

# %%
print("\n" + "=" * 60)
print("📊 ETL & TABLEAU PREP COMPLETE")
print("=" * 60)

print(f"""
DATASETS CREATED:
─────────────────────────────────────────────────────────────
1. movies_main.csv          - Primary analysis table ({len(tableau_df)} movies)
2. movies_by_genre.csv      - Genre-exploded table ({len(genre_exploded)} rows)
3. director_performance.csv - Director aggregates ({len(director_stats)} directors)
4. actor_performance.csv    - Actor aggregates ({len(actor_stats)} actors)
5. yearly_trends.csv        - Yearly statistics ({len(yearly_stats)} years)
6. funnel_analysis.csv      - Investment funnel ({len(funnel_agg)} stages)

TABLEAU DASHBOARD RECOMMENDATIONS:
─────────────────────────────────────────────────────────────
1. OVERVIEW DASHBOARD
   - KPI cards: Total Revenue, Avg ROI, Success Rate
   - Treemap: Revenue by Genre
   - Line chart: Yearly trends
   
2. FINANCIAL DEEP DIVE
   - Scatter: Budget vs Revenue (colored by genre)
   - Bar chart: ROI by Budget Category
   - Highlight table: Funnel stage breakdown
   
3. PEOPLE ANALYTICS
   - Bar chart: Top Directors by Revenue
   - Scatter: Director Success Rate vs Avg ROI
   - Top Actors leaderboard
   
4. FUNNEL ANALYSIS
   - Funnel chart: Investment to Profitability conversion
   - Stacked bar: Funnel stages by Genre
   - Cohort analysis by Era

All files saved to: {tableau_dir}
""")

print("🎬 Ready for Tableau visualization!")
