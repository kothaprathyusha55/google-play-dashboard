import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Google Play Store Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("googleplaystore.csv")
    return df

df = load_data()

st.sidebar.header("🔍 Filter Options")

content_ratings = df["Content Rating"].dropna().unique().tolist()
selected_rating = st.sidebar.selectbox("Select Content Rating", sorted(content_ratings), index=content_ratings.index("Teen") if "Teen" in content_ratings else 0)

metric = st.sidebar.radio("Metric to Display", ["Reviews", "Installs"])

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📊 Google Play Store App Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>Analysis for <span style='color:#F63366'>{selected_rating}</span> Rated Apps - Sorted by <span style='color:#1f77b4'>{metric}</span></h4><hr>", unsafe_allow_html=True)

df_cleaned = df[df["Content Rating"] == selected_rating].copy()
df_cleaned["Reviews"] = pd.to_numeric(df_cleaned["Reviews"], errors='coerce')
df_cleaned["Installs"] = df_cleaned["Installs"].str.replace("[+,]", "", regex=True)
df_cleaned["Installs"] = pd.to_numeric(df_cleaned["Installs"], errors='coerce')
df_cleaned.dropna(subset=["Category", "Reviews", "Installs"], inplace=True)

top_data = df_cleaned.groupby("Category")[metric].sum().sort_values(ascending=False).head(10)

st.success(f"✅ Category with highest {metric.lower()}: **{top_data.idxmax()}** ({int(top_data.max()):,})")

fig, ax = plt.subplots(figsize=(10, 6))
colors = "magma" if metric == "Installs" else "viridis"
sns.barplot(x=top_data.values, y=top_data.index, palette=colors, ax=ax)
ax.set_title(f"Top 10 Categories by {metric}", fontsize=16)
ax.set_xlabel(f"Total {metric}", fontsize=12)
ax.set_ylabel("Category", fontsize=12)
st.pyplot(fig)


# ---- Existing bar plot above here ----

st.markdown("## 🎻 Violin Plot: Ratings per Category")
st.info("Showing distribution of app Ratings across most frequent categories.")

# Prepare data for violin plot
df_cleaned["Rating"] = pd.to_numeric(df_cleaned["Rating"], errors="coerce")
df_cleaned.dropna(subset=["Rating", "Category"], inplace=True)

# Get top 10 categories by number of apps
top_categories = df_cleaned["Category"].value_counts().head(10).index.tolist()
df_violin = df_cleaned[df_cleaned["Category"].isin(top_categories)]

# Plot violin
fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.violinplot(data=df_violin, x="Rating", y="Category", palette="coolwarm", ax=ax2)
ax2.set_title("Violin Plot of App Ratings per Category", fontsize=16)
ax2.set_xlabel("Rating")
ax2.set_ylabel("Category")
st.pyplot(fig2)


# Heatmap: Average Installs by Content Rating (SOCIAL vs EDUCATION)
st.header("🔥 Heatmap: SOCIAL vs EDUCATION Category Installs by Content Rating")

# Clean 'Installs'
df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Filter for SOCIAL and EDUCATION only
df_filtered = df[df['Category'].isin(['SOCIAL', 'EDUCATION'])]

# Pivot table: average installs by Content Rating
pivot = df_filtered.pivot_table(
    index='Category',
    columns='Content Rating',
    values='Installs',
    aggfunc='mean',
    fill_value=0
)

# Plot heatmap
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Blues', ax=ax)
ax.set_title("Average Installs by Content Rating (SOCIAL vs EDUCATION)", fontsize=14)
ax.set_xlabel("Content Rating")
ax.set_ylabel("Category")

st.pyplot(fig)

st.markdown("<hr><center>Made with ❤️ using Streamlit | Dataset: Google Play Store</center>", unsafe_allow_html=True)
