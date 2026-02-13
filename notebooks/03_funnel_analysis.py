# %% [markdown]
# # 🎬 Movies Dataset - Investment-to-Profitability Funnel Analysis
# 
# This notebook performs a comprehensive funnel analysis examining:
# 
# 1. **Funnel Definition** - Investment → Revenue → Profit → High ROI
# 2. **Conversion Rates** - Stage-by-stage drop-off analysis
# 3. **Bottleneck Identification** - Where movies fail in the funnel
# 4. **Segment Analysis** - Break down by genre, era, budget tier
# 5. **Success Factors** - What distinguishes top performers
# 6. **Business Recommendations** - Data-driven investment insights

# %% [markdown]
# ## 1. Setup & Load Data

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Setup paths
import os
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
base_dir = os.path.dirname(script_dir) if 'notebooks' in script_dir else script_dir
tableau_dir = os.path.join(base_dir, 'outputs', 'tableau')
output_dir = os.path.join(base_dir, 'outputs')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load main dataset
movies = pd.read_csv(os.path.join(tableau_dir, 'movies_main.csv'))
print(f"📊 Loaded {len(movies)} movies")

# %% [markdown]
# ## 2. Define the Investment-to-Profitability Funnel

# %%
print("=" * 70)
print("🎯 INVESTMENT-TO-PROFITABILITY FUNNEL DEFINITION")
print("=" * 70)

# Define funnel stages
funnel_stages = {
    'Stage 1: Total Movies': len(movies),
    'Stage 2: Has Budget': (movies['Budget'] > 0).sum(),
    'Stage 3: Generated Revenue': ((movies['Budget'] > 0) & (movies['Revenue'] > 0)).sum(),
    'Stage 4: Recovered Investment': ((movies['Budget'] > 0) & (movies['Revenue'] >= movies['Budget'])).sum(),
    'Stage 5: Profitable': ((movies['Budget'] > 0) & (movies['Profit'] > 0)).sum(),
    'Stage 6: Strong ROI (>100%)': ((movies['Budget'] > 0) & (movies['ROI'] > 100)).sum(),
    'Stage 7: High ROI (>300%)': ((movies['Budget'] > 0) & (movies['ROI'] > 300)).sum(),
    'Stage 8: Blockbuster (>1000%)': ((movies['Budget'] > 0) & (movies['ROI'] > 1000)).sum(),
}

print("\n📊 FUNNEL OVERVIEW:")
print("-" * 70)
prev_count = None
for stage, count in funnel_stages.items():
    pct_total = count / funnel_stages['Stage 1: Total Movies'] * 100
    if prev_count is not None:
        conversion = count / prev_count * 100
        drop_off = prev_count - count
        print(f"{stage:35} | {count:5} ({pct_total:5.1f}%) | Conv: {conversion:5.1f}% | Drop: {drop_off}")
    else:
        print(f"{stage:35} | {count:5} ({pct_total:5.1f}%)")
    prev_count = count

# %% [markdown]
# ## 3. Funnel Visualization

# %%
# Create funnel chart
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Left: Funnel Chart
ax1 = axes[0]
stages = list(funnel_stages.keys())
values = list(funnel_stages.values())
stage_labels = [s.split(': ')[1] for s in stages]

# Create funnel effect
colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(values)))
y_positions = range(len(values))

for i, (label, value, color) in enumerate(zip(stage_labels, values, colors)):
    width = value / max(values)
    ax1.barh(i, width, color=color, height=0.8, left=(1-width)/2)
    ax1.text(0.5, i, f'{label}\n{value:,} ({value/values[0]*100:.1f}%)', 
             ha='center', va='center', fontsize=10, fontweight='bold')

ax1.set_xlim(0, 1)
ax1.set_ylim(-0.5, len(values) - 0.5)
ax1.invert_yaxis()
ax1.set_title('Investment-to-Profitability Funnel', fontsize=14, fontweight='bold')
ax1.axis('off')

# Right: Stage-by-Stage Conversion
ax2 = axes[1]
conversions = []
stage_pairs = []
for i in range(1, len(values)):
    conv = values[i] / values[i-1] * 100
    conversions.append(conv)
    stage_pairs.append(f'{i} → {i+1}')

# Color based on conversion rate
colors2 = ['#e74c3c' if c < 70 else '#f39c12' if c < 85 else '#2ecc71' for c in conversions]
bars = ax2.bar(stage_pairs, conversions, color=colors2, edgecolor='black')

ax2.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.5, label='80% threshold')
ax2.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='60% threshold')

for bar, conv in zip(bars, conversions):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{conv:.1f}%', ha='center', va='bottom', fontsize=9)

ax2.set_xlabel('Stage Transition')
ax2.set_ylabel('Conversion Rate (%)')
ax2.set_title('Stage-by-Stage Conversion Rates', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 110)
ax2.tick_params(axis='x', rotation=45)
ax2.legend(loc='lower right')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'funnel_visualization.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 4. Bottleneck Analysis

# %%
print("=" * 70)
print("🔍 BOTTLENECK ANALYSIS - Where Movies Fail")
print("=" * 70)

# Calculate drop-off at each stage
drop_offs = {}
for i in range(1, len(values)):
    stage_from = stages[i-1].split(': ')[1]
    stage_to = stages[i].split(': ')[1]
    drop = values[i-1] - values[i]
    drop_pct = drop / values[i-1] * 100
    drop_offs[f'{stage_from} → {stage_to}'] = {
        'dropped': drop,
        'drop_pct': drop_pct,
        'retained': values[i],
        'retention_pct': 100 - drop_pct
    }

# Sort by biggest drop-offs (absolute)
sorted_drops = sorted(drop_offs.items(), key=lambda x: x[1]['dropped'], reverse=True)

print("\nBIGGEST FUNNEL LEAKS (by volume):")
print("-" * 70)
for transition, stats in sorted_drops[:5]:
    print(f"📉 {transition}")
    print(f"   Lost: {stats['dropped']:,} movies ({stats['drop_pct']:.1f}% drop-off)")
    print()

# %% [markdown]
# ## 5. Segment Analysis by Genre

# %%
print("=" * 70)
print("🎬 FUNNEL BY GENRE - Primary Genre Breakdown")
print("=" * 70)

# Load genre data
genre_df = pd.read_csv(os.path.join(tableau_dir, 'movies_by_genre.csv'))

# Calculate funnel metrics by genre
genre_funnel = genre_df.groupby('Genre').agg({
    'id': 'nunique',
    'Budget': lambda x: (x > 0).sum(),
    'Revenue': lambda x: (x > 0).sum(),
    'Profit': lambda x: (x > 0).sum(),
    'ROI': lambda x: (x > 300).sum()
}).reset_index()

genre_funnel.columns = ['Genre', 'Total Movies', 'Has Budget', 'Has Revenue', 'Profitable', 'High ROI']

# Calculate percentages
genre_funnel['Budget Rate'] = (genre_funnel['Has Budget'] / genre_funnel['Total Movies'] * 100).round(1)
genre_funnel['Revenue Rate'] = (genre_funnel['Has Revenue'] / genre_funnel['Has Budget'] * 100).round(1)
genre_funnel['Profit Rate'] = (genre_funnel['Profitable'] / genre_funnel['Has Revenue'] * 100).round(1)
genre_funnel['High ROI Rate'] = (genre_funnel['High ROI'] / genre_funnel['Profitable'] * 100).round(1)

genre_funnel = genre_funnel.sort_values('Total Movies', ascending=False)
print(genre_funnel.head(15).to_string(index=False))

# %%
# Visualize genre funnel performance
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

top_genres = genre_funnel.head(10)

# Profit Rate by Genre
ax1 = axes[0, 0]
colors1 = ['#2ecc71' if x >= 75 else '#f39c12' if x >= 60 else '#e74c3c' for x in top_genres['Profit Rate']]
ax1.barh(top_genres['Genre'], top_genres['Profit Rate'], color=colors1)
ax1.set_xlabel('Profitability Rate (%)')
ax1.set_title('Profitability Rate by Genre', fontsize=12, fontweight='bold')
ax1.invert_yaxis()
ax1.axvline(x=75, color='green', linestyle='--', alpha=0.5)
ax1.axvline(x=60, color='orange', linestyle='--', alpha=0.5)

# High ROI Rate by Genre
ax2 = axes[0, 1]
colors2 = ['#3498db' if x >= 50 else '#95a5a6' for x in top_genres['High ROI Rate']]
ax2.barh(top_genres['Genre'], top_genres['High ROI Rate'], color=colors2)
ax2.set_xlabel('High ROI Rate (>300%)')
ax2.set_title('High ROI Achievement Rate by Genre', fontsize=12, fontweight='bold')
ax2.invert_yaxis()

# Genre Funnel Comparison
ax3 = axes[1, 0]
x = np.arange(len(top_genres))
width = 0.2
ax3.bar(x - 1.5*width, top_genres['Budget Rate'], width, label='Has Budget', color='#3498db')
ax3.bar(x - 0.5*width, top_genres['Revenue Rate'], width, label='Has Revenue', color='#2ecc71')
ax3.bar(x + 0.5*width, top_genres['Profit Rate'], width, label='Profitable', color='#9b59b6')
ax3.bar(x + 1.5*width, top_genres['High ROI Rate'], width, label='High ROI', color='#e74c3c')
ax3.set_xticks(x)
ax3.set_xticklabels(top_genres['Genre'], rotation=45, ha='right')
ax3.legend()
ax3.set_ylabel('Rate (%)')
ax3.set_title('Funnel Stage Rates by Genre', fontsize=12, fontweight='bold')

# Volume vs Success Rate scatter
ax4 = axes[1, 1]
scatter = ax4.scatter(top_genres['Total Movies'], 
                      top_genres['Profit Rate'],
                      s=top_genres['High ROI Rate'] * 5,
                      c=top_genres['High ROI Rate'],
                      cmap='RdYlGn', alpha=0.7, edgecolors='black')
for i, genre in enumerate(top_genres['Genre']):
    ax4.annotate(genre, (top_genres['Total Movies'].iloc[i], top_genres['Profit Rate'].iloc[i]),
                 fontsize=8, ha='center')
ax4.set_xlabel('Total Movies')
ax4.set_ylabel('Profitability Rate (%)')
ax4.set_title('Volume vs Success (Size = High ROI Rate)', fontsize=12, fontweight='bold')
plt.colorbar(scatter, ax=ax4, label='High ROI Rate')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'funnel_by_genre.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 6. Segment Analysis by Budget Tier

# %%
print("=" * 70)
print("💰 FUNNEL BY BUDGET TIER")
print("=" * 70)

# Calculate funnel by budget category
budget_funnel = movies[movies['Budget'] > 0].groupby('Budget Category').agg({
    'Title': 'count',
    'Revenue': lambda x: (x > 0).sum(),
    'Is Profitable': 'sum',
    'ROI': ['mean', lambda x: (x > 300).sum()]
}).reset_index()

budget_funnel.columns = ['Budget Tier', 'Total', 'Has Revenue', 'Profitable', 'Avg ROI', 'High ROI']
budget_funnel['Profit Rate'] = (budget_funnel['Profitable'] / budget_funnel['Total'] * 100).round(1)
budget_funnel['High ROI Rate'] = (budget_funnel['High ROI'] / budget_funnel['Total'] * 100).round(1)

# Order by budget tier
tier_order = ['Micro (<$5M)', 'Low ($5M-$15M)', 'Medium ($15M-$40M)', 
              'High ($40M-$100M)', 'Blockbuster (>$100M)']
budget_funnel['Order'] = budget_funnel['Budget Tier'].apply(lambda x: tier_order.index(x) if x in tier_order else 99)
budget_funnel = budget_funnel.sort_values('Order')

print(budget_funnel[['Budget Tier', 'Total', 'Profit Rate', 'High ROI Rate', 'Avg ROI']].to_string(index=False))

# %%
# Visualize budget tier funnel
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Profit Rate by Budget Tier
ax1 = axes[0]
valid_tiers = budget_funnel[budget_funnel['Budget Tier'].isin(tier_order)]
ax1.bar(valid_tiers['Budget Tier'], valid_tiers['Profit Rate'], color='#3498db')
ax1.set_ylabel('Profitability Rate (%)')
ax1.set_title('Profitability by Budget Tier', fontsize=12, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)
ax1.axhline(y=75, color='green', linestyle='--', alpha=0.5)

# High ROI Rate by Budget Tier
ax2 = axes[1]
ax2.bar(valid_tiers['Budget Tier'], valid_tiers['High ROI Rate'], color='#e74c3c')
ax2.set_ylabel('High ROI Rate (>300%)')
ax2.set_title('High ROI Achievement by Budget Tier', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'funnel_by_budget.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 7. Segment Analysis by Era

# %%
print("=" * 70)
print("📅 FUNNEL BY ERA")
print("=" * 70)

era_funnel = movies[movies['Budget'] > 0].groupby('Era').agg({
    'Title': 'count',
    'Revenue': lambda x: (x > 0).sum(),
    'Is Profitable': 'sum',
    'ROI': ['mean', lambda x: (x > 300).sum()]
}).reset_index()

era_funnel.columns = ['Era', 'Total', 'Has Revenue', 'Profitable', 'Avg ROI', 'High ROI']
era_funnel['Profit Rate'] = (era_funnel['Profitable'] / era_funnel['Total'] * 100).round(1)
era_funnel['High ROI Rate'] = (era_funnel['High ROI'] / era_funnel['Total'] * 100).round(1)

# Order eras
era_order = ['Classic (<1970)', 'Pre-Digital (1970-1989)', '90s Era (1990-1999)', 
             '2000s (2000-2009)', 'Modern (2010+)']
era_funnel['Order'] = era_funnel['Era'].apply(lambda x: era_order.index(x) if x in era_order else 99)
era_funnel = era_funnel.sort_values('Order')

print(era_funnel[['Era', 'Total', 'Profit Rate', 'High ROI Rate', 'Avg ROI']].to_string(index=False))

# %%
# Era trend visualization
fig, ax = plt.subplots(figsize=(12, 6))

valid_eras = era_funnel[era_funnel['Era'].isin(era_order)]
x = np.arange(len(valid_eras))
width = 0.35

bars1 = ax.bar(x - width/2, valid_eras['Profit Rate'], width, label='Profitability Rate', color='#2ecc71')
bars2 = ax.bar(x + width/2, valid_eras['High ROI Rate'], width, label='High ROI Rate', color='#e74c3c')

ax.set_xticks(x)
ax.set_xticklabels(valid_eras['Era'], rotation=30, ha='right')
ax.legend()
ax.set_ylabel('Rate (%)')
ax.set_title('Funnel Performance by Era', fontsize=14, fontweight='bold')
ax.axhline(y=75, color='gray', linestyle='--', alpha=0.3)

for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'funnel_by_era.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 8. Success Factor Analysis

# %%
print("=" * 70)
print("✨ SUCCESS FACTOR ANALYSIS")
print("=" * 70)

# Compare successful vs failed movies
successful = movies[(movies['Budget'] > 0) & (movies['ROI'] > 300)]
failed = movies[(movies['Budget'] > 0) & (movies['ROI'] < 0)]

print(f"\nHigh ROI Movies (>300%): {len(successful)}")
print(f"Failed Movies (ROI < 0): {len(failed)}")

# Compare key metrics
comparison_metrics = ['Budget', 'TMDB Rating', 'IMDB Rating', 'Popularity', 
                      'Vote Count', 'Runtime Minutes', 'Total Social Engagement']

comparison = pd.DataFrame({
    'Metric': comparison_metrics,
    'High ROI (Mean)': [successful[m].mean() for m in comparison_metrics],
    'Failed (Mean)': [failed[m].mean() for m in comparison_metrics],
})
comparison['Difference'] = comparison['High ROI (Mean)'] - comparison['Failed (Mean)']
comparison['% Difference'] = ((comparison['High ROI (Mean)'] - comparison['Failed (Mean)']) / 
                               comparison['Failed (Mean)'] * 100).round(1)

print("\nKEY METRIC COMPARISON:")
print(comparison.to_string(index=False))

# %%
# Success factors by genre (which genres punch above their weight)
print("\n" + "=" * 70)
print("🎯 GENRE SUCCESS PATTERNS")
print("=" * 70)

genre_success = genre_df[genre_df['Budget'] > 0].groupby('Genre').agg({
    'id': 'count',
    'Budget': 'mean',
    'ROI': 'mean',
    'Profit': lambda x: (x > 0).mean() * 100
}).reset_index()

genre_success.columns = ['Genre', 'Movies', 'Avg Budget', 'Avg ROI', 'Success Rate']
genre_success = genre_success.sort_values('Success Rate', ascending=False)

print("\nGENRES RANKED BY SUCCESS RATE:")
print(genre_success.head(15).to_string(index=False))

# %%
# Optimal Budget Sweet Spot Analysis
print("\n" + "=" * 70)
print("💰 BUDGET SWEET SPOT ANALYSIS")
print("=" * 70)

# Create fine-grained budget buckets
valid_movies = movies[(movies['Budget'] > 0) & (movies['ROI'].notna())].copy()
valid_movies['Budget_Bucket'] = pd.cut(valid_movies['Budget'] / 1e6, 
                                        bins=[0, 5, 10, 20, 30, 50, 75, 100, 150, 200, 500],
                                        labels=['0-5M', '5-10M', '10-20M', '20-30M', '30-50M', 
                                                '50-75M', '75-100M', '100-150M', '150-200M', '200M+'])

budget_analysis = valid_movies.groupby('Budget_Bucket', observed=True).agg({
    'Title': 'count',
    'ROI': 'mean',
    'Is Profitable': 'mean',
    'Revenue': 'sum'
}).reset_index()

budget_analysis.columns = ['Budget Range', 'Movies', 'Avg ROI', 'Success Rate', 'Total Revenue']
budget_analysis['Success Rate'] = (budget_analysis['Success Rate'] * 100).round(1)

print(budget_analysis.to_string(index=False))

# Find optimal range
best_success = budget_analysis.loc[budget_analysis['Success Rate'].idxmax()]
best_roi = budget_analysis.loc[budget_analysis['Avg ROI'].idxmax()]
print(f"\n🎯 OPTIMAL BUDGET RANGE:")
print(f"   Highest Success Rate: {best_success['Budget Range']} ({best_success['Success Rate']}%)")
print(f"   Highest Average ROI: {best_roi['Budget Range']} ({best_roi['Avg ROI']:.0f}%)")

# %% [markdown]
# ## 9. Director Success in Funnel

# %%
print("=" * 70)
print("🎬 TOP DIRECTORS BY FUNNEL CONVERSION")
print("=" * 70)

# Load director data
directors = pd.read_csv(os.path.join(tableau_dir, 'director_performance.csv'))

# Calculate funnel metrics
directors_with_movies = directors[directors['Movie Count'] >= 5].copy()
directors_with_movies['Efficiency'] = directors_with_movies['Total Revenue'] / directors_with_movies['Total Budget']

print("\nTOP DIRECTORS BY SUCCESS RATE (Min 5 movies):")
top_success = directors_with_movies.nlargest(15, 'Success Rate')[
    ['Director', 'Movie Count', 'Success Rate', 'Avg ROI', 'Total Revenue']
]
top_success['Total Revenue'] = (top_success['Total Revenue'] / 1e9).round(2).astype(str) + 'B'
print(top_success.to_string(index=False))

# %%
# Director scatter: Volume vs Success
fig, ax = plt.subplots(figsize=(12, 8))

scatter = ax.scatter(
    directors_with_movies['Movie Count'],
    directors_with_movies['Success Rate'],
    c=directors_with_movies['Avg ROI'].clip(0, 500),
    s=directors_with_movies['Total Revenue'] / 1e8,
    cmap='RdYlGn',
    alpha=0.6,
    edgecolors='white'
)

# Label top directors
top10 = directors_with_movies.nlargest(10, 'Total Revenue')
for _, row in top10.iterrows():
    ax.annotate(row['Director'], (row['Movie Count'], row['Success Rate']),
                fontsize=8, ha='left')

ax.axhline(y=75, color='green', linestyle='--', alpha=0.5, label='75% Success')
ax.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='50% Success')

ax.set_xlabel('Number of Movies', fontsize=11)
ax.set_ylabel('Success Rate (%)', fontsize=11)
ax.set_title('Director Performance: Volume vs Success Rate\n(Size = Total Revenue, Color = Avg ROI)', 
             fontsize=14, fontweight='bold')
ax.legend(loc='lower right')

plt.colorbar(scatter, ax=ax, label='Avg ROI %')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'director_funnel_analysis.png'), dpi=150)
plt.show()

# %% [markdown]
# ## 10. Business Recommendations

# %%
print("=" * 80)
print("📊 FUNNEL ANALYSIS - KEY FINDINGS & RECOMMENDATIONS")
print("=" * 80)

print(f"""
================================================================================
                         FUNNEL CONVERSION SUMMARY
================================================================================
Total Movies Analyzed: {len(movies)}
Movies with Budget Data: {funnel_stages['Stage 2: Has Budget']} ({funnel_stages['Stage 2: Has Budget']/len(movies)*100:.1f}%)
Generated Revenue: {funnel_stages['Stage 3: Generated Revenue']}
Profitable Movies: {funnel_stages['Stage 5: Profitable']} ({funnel_stages['Stage 5: Profitable']/funnel_stages['Stage 2: Has Budget']*100:.1f}% of invested)
High ROI (>300%): {funnel_stages['Stage 7: High ROI (>300%)']} ({funnel_stages['Stage 7: High ROI (>300%)']/funnel_stages['Stage 5: Profitable']*100:.1f}% of profitable)

================================================================================
                         KEY BOTTLENECKS IDENTIFIED
================================================================================
1. INVESTMENT → REVENUE GAP
   - {(funnel_stages['Stage 2: Has Budget'] - funnel_stages['Stage 3: Generated Revenue'])} movies with budget but no revenue data
   - These represent unreleased, shelved, or data-incomplete projects
   
2. PROFITABILITY THRESHOLD
   - Only {funnel_stages['Stage 5: Profitable']/funnel_stages['Stage 3: Generated Revenue']*100:.1f}% of revenue-generating movies are profitable
   - {funnel_stages['Stage 3: Generated Revenue'] - funnel_stages['Stage 5: Profitable']} movies fail to recover their investment

3. STRONG ROI ACHIEVEMENT
   - Only {funnel_stages['Stage 7: High ROI (>300%)']/funnel_stages['Stage 5: Profitable']*100:.1f}% of profitable movies achieve >300% ROI
   - The jump from "profitable" to "hit" is the hardest conversion

================================================================================
                       DATA-DRIVEN RECOMMENDATIONS
================================================================================

📌 RECOMMENDATION 1: BUDGET OPTIMIZATION
   - Optimal budget range for highest success: {best_success['Budget Range']}
   - Best ROI potential: {best_roi['Budget Range']} range
   - Avoid extreme budgets unless backed by proven IP/talent

📌 RECOMMENDATION 2: GENRE SELECTION
   - Highest success rate genres: {genre_success.head(3)['Genre'].tolist()}
   - Consider genre diversification within portfolio
   - Documentary and Horror show high ROI potential with lower budgets

📌 RECOMMENDATION 3: TALENT SELECTION
   - Directors with high success rates should command premium
   - Consider track record (min 5 films) over single hits
   - Social media presence correlates moderately with success

📌 RECOMMENDATION 4: MODERN ERA CONSIDERATIONS
   - Modern era (2010+) movies show different patterns than historical
   - Adjust expectations for inflation and market changes
   - Social media engagement increasingly important

📌 RECOMMENDATION 5: RISK MITIGATION
   - Blockbuster budgets have lower success rates
   - Consider portfolio approach: mix of budget tiers
   - Factor in marketing spend (not in this data)

================================================================================
                         NEXT STEPS FOR ANALYSIS
================================================================================
1. Build interactive Tableau dashboard with these segments
2. Create predictive model for success probability
3. Analyze marketing spend impact (if data available)
4. Time-series forecasting for future trends
5. A/B testing simulation for portfolio optimization
""")

# %% [markdown]
# ## 11. Save Funnel Metrics

# %%
# Save detailed funnel data for Tableau
funnel_detailed = movies[['Title', 'Year', 'Budget', 'Revenue', 'Profit', 'ROI',
                           'Primary Genre', 'Budget Category', 'Era', 'Funnel Stage',
                           'Director', 'Combined Rating', 'Is Profitable']].copy()
funnel_detailed.columns = ['Title', 'Year', 'Budget', 'Revenue', 'Profit', 'ROI',
                           'Genre', 'Budget_Tier', 'Era', 'Funnel_Stage',
                           'Director', 'Rating', 'Is_Profitable']

funnel_file = os.path.join(tableau_dir, 'funnel_detailed.csv')
funnel_detailed.to_csv(funnel_file, index=False)
print(f"\n✅ Detailed funnel data saved: {funnel_file}")
print(f"   Records: {len(funnel_detailed)}")

# Save conversion metrics
conversion_data = []
for i, (stage, count) in enumerate(funnel_stages.items()):
    pct_total = count / funnel_stages['Stage 1: Total Movies'] * 100
    if i > 0:
        prev_stage = list(funnel_stages.keys())[i-1]
        prev_count = funnel_stages[prev_stage]
        conversion = count / prev_count * 100
    else:
        conversion = 100
    conversion_data.append({
        'Stage': stage,
        'Stage_Number': i + 1,
        'Count': count,
        'Pct_of_Total': round(pct_total, 1),
        'Conversion_from_Previous': round(conversion, 1)
    })

conversion_df = pd.DataFrame(conversion_data)
conversion_file = os.path.join(tableau_dir, 'funnel_conversion_rates.csv')
conversion_df.to_csv(conversion_file, index=False)
print(f"✅ Conversion rates saved: {conversion_file}")

print("\n🎬 Funnel Analysis Complete!")
