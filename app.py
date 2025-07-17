import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page settings
st.set_page_config(page_title="Google Play Store Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("googleplaystore.csv")
    return df

df = load_data()

# Sidebar
st.sidebar.header("🔍 Filter Options")

# Multiselect: Content Rating
content_ratings = sorted(df["Content Rating"].dropna().unique().tolist())
selected_ratings = st.sidebar.multiselect("Select Content Rating(s)", content_ratings, default=["Teen"])

# Multiselect: Top 10 Genres only
top_genres = df["Genres"].value_counts().head(10).index.tolist()
selected_genres = st.sidebar.multiselect("Select Genre(s)", top_genres, default=[top_genres[0]])

# Plot options
plot_type = st.sidebar.radio("Select Plot to Display", [
    "Bar Chart", "Violin Plot", "Heatmap", "Pie Chart"
])

# Metric for Bar Chart
metric = st.sidebar.radio("Metric for Bar Chart", ["Reviews", "Installs"])

# Header
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📊 Google Play Store App Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>Filters: <span style='color:#F63366'>{', '.join(selected_ratings)}</span> & <span style='color:#1f77b4'>{', '.join(selected_genres)}</span></h4><hr>", unsafe_allow_html=True)

# Filter data
df_filtered = df[
    (df["Content Rating"].isin(selected_ratings)) &
    (df["Genres"].isin(selected_genres))
].copy()

# Clean data
df_filtered["Reviews"] = pd.to_numeric(df_filtered["Reviews"], errors='coerce')
df_filtered["Installs"] = df_filtered["Installs"].astype(str).str.replace("[+,]", "", regex=True)
df_filtered["Installs"] = pd.to_numeric(df_filtered["Installs"], errors='coerce')
df_filtered["Rating"] = pd.to_numeric(df_filtered["Rating"], errors='coerce')
df_filtered.dropna(subset=["Category", "Reviews", "Installs", "Rating"], inplace=True)

# 📊 Bar Chart
if plot_type == "Bar Chart":
    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        top_data = df_filtered.groupby("Category")[metric].sum().sort_values(ascending=False).head(10)
        st.success(f"✅ Category with highest {metric.lower()}: **{top_data.idxmax()}** ({int(top_data.max()):,})")

        fig, ax = plt.subplots(figsize=(8,2))
        colors = "magma" if metric == "Installs" else "viridis"
        sns.barplot(x=top_data.values, y=top_data.index, palette=colors, ax=ax)
        ax.set_title(f"Top 10 Categories by {metric}", fontsize=16)
        ax.set_xlabel(f"Total {metric}")
        ax.set_ylabel("Category")
        st.pyplot(fig)

# 🎻 Violin Plot
elif plot_type == "Violin Plot":
    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        st.markdown("## 🎻 Violin Plot: Ratings per Category")
        top_categories = df_filtered["Category"].value_counts().head(10).index.tolist()
        df_violin = df_filtered[df_filtered["Category"].isin(top_categories)]

        fig2, ax2 = plt.subplots(figsize=(10,2))
        sns.violinplot(data=df_violin, x="Category", y="Rating", palette="Spectral", ax=ax2)
        ax2.set_title("Violin Plot of Ratings per Category", fontsize=16)
        ax2.set_xlabel("Category")
        ax2.set_ylabel("Rating")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

# 🔥 Heatmap
elif plot_type == "Heatmap":
    st.header("🔥 Heatmap: Average Installs by Category and Content Rating")

    top_categories = df_filtered["Category"].value_counts().head(5).index.tolist()
    df_heat = df_filtered[df_filtered["Category"].isin(top_categories)]

    if df_heat.empty:
        st.warning("No data available for heatmap with the selected filters.")
    else:
        pivot = df_heat.pivot_table(
            index="Category",
            columns="Content Rating",
            values="Installs",
            aggfunc="mean",
            fill_value=0
        )

        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax3)
        ax3.set_title("Average Installs by Category and Content Rating", fontsize=14)
        ax3.set_xlabel("Content Rating")
        ax3.set_ylabel("Category")
        st.pyplot(fig3)

elif plot_type == "Pie Chart":
    st.header("🥧 Pie Chart: App Distribution by Category")

    if df_filtered.empty:
        st.warning("No data available for pie chart with the selected filters.")
    else:
        category_counts = df_filtered["Category"].value_counts().head(10)

        fig5, ax5 = plt.subplots(figsize=(1, 1))  # Reduced size here
        ax5.pie(
            category_counts,
            labels=category_counts.index,
            autopct='%1.1f%%',
            startangle=50,
            textprops={'fontsize': 2}
        )
        ax5.axis('equal')
        ax5.set_title("Top 10 Categories by App Count", fontsize=4)
        st.pyplot(fig5)


# Footer
st.markdown("<hr><center>Made with ❤️ using Streamlit | Dataset: Google Play Store</center>", unsafe_allow_html=True)
