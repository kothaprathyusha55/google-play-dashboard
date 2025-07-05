import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit config
st.set_page_config(page_title="Google Play Store Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("googleplaystore.csv")
    return df

df = load_data()

# Sidebar
st.sidebar.header("🔍 Filter Options")

content_ratings = df["Content Rating"].dropna().unique().tolist()
selected_rating = st.sidebar.selectbox("Select Content Rating", sorted(content_ratings), index=content_ratings.index("Teen") if "Teen" in content_ratings else 0)

metric = st.sidebar.radio("Metric to Display", ["Reviews", "Installs"])
plot_type = st.sidebar.radio("Select Plot to Display", ["Bar Chart", "Violin Plot", "Heatmap"])

# Page header
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📊 Google Play Store App Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>Analysis for <span style='color:#F63366'>{selected_rating}</span> Rated Apps</h4><hr>", unsafe_allow_html=True)

# Clean and filter data
df_filtered = df[df["Content Rating"] == selected_rating].copy()
df_filtered["Reviews"] = pd.to_numeric(df_filtered["Reviews"], errors='coerce')
df_filtered["Installs"] = df_filtered["Installs"].astype(str).str.replace("[+,]", "", regex=True)
df_filtered["Installs"] = pd.to_numeric(df_filtered["Installs"], errors='coerce')
df_filtered["Rating"] = pd.to_numeric(df_filtered["Rating"], errors='coerce')
df_filtered.dropna(subset=["Category", "Reviews", "Installs", "Rating"], inplace=True)

# Plot 1: Bar Chart
if plot_type == "Bar Chart":
    top_data = df_filtered.groupby("Category")[metric].sum().sort_values(ascending=False).head(10)

    st.success(f"✅ Category with highest {metric.lower()} (for {selected_rating}): **{top_data.idxmax()}** ({int(top_data.max()):,})")

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = "magma" if metric == "Installs" else "viridis"
    sns.barplot(x=top_data.values, y=top_data.index, palette=colors, ax=ax)
    ax.set_title(f"Top 10 Categories by {metric} ({selected_rating})", fontsize=16)
    ax.set_xlabel(f"Total {metric}")
    ax.set_ylabel("Category")
    st.pyplot(fig)

# Plot 2: Violin Plot
elif plot_type == "Violin Plot":
    st.markdown("## 🎻 Violin Plot: Ratings per Category")
    st.info(f"Showing distribution of Ratings for top categories in {selected_rating} apps.")

    top_categories = df_filtered["Category"].value_counts().head(10).index.tolist()
    df_violin = df_filtered[df_filtered["Category"].isin(top_categories)]

    fig2, ax2 = plt.subplots(figsize=(14, 6))
    sns.violinplot(data=df_violin, x="Category", y="Rating", palette="Spectral", ax=ax2)
    ax2.set_title(f"Violin Plot of Ratings per Category ({selected_rating})", fontsize=16)
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Rating")
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

# Plot 3: Heatmap
elif plot_type == "Heatmap":
    st.header(f"🔥 Heatmap: SOCIAL vs EDUCATION Installs by Content Rating ({selected_rating})")

    df_social_edu = df_filtered[df_filtered['Category'].isin(['SOCIAL', 'EDUCATION'])]

    pivot = df_social_edu.pivot_table(
        index='Category',
        columns='Content Rating',
        values='Installs',
        aggfunc='mean',
        fill_value=0
    )

    # If selected rating not in columns, skip plot
    if selected_rating not in pivot.columns:
        st.warning(f"No data available for SOCIAL or EDUCATION apps with '{selected_rating}' rating.")
    else:
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot[[selected_rating]], annot=True, fmt='.0f', cmap='Blues', ax=ax3)
        ax3.set_title(f"Average Installs for SOCIAL vs EDUCATION ({selected_rating})", fontsize=14)
        ax3.set_xlabel("Content Rating")
        ax3.set_ylabel("Category")
        st.pyplot(fig3)
# Plot 4: Pie Chart - Non-null values in each column
elif plot_type == "Pie Chart":
    st.header("🥧 Pie Chart: Non-Null Values in Each Column")
    st.info("This chart shows the proportion of usable (non-empty) data for each column.")

    # Count non-null values
    column_counts = df.notnull().sum()
    column_counts = column_counts[column_counts > 0]  # Only columns with some data

    fig4, ax4 = plt.subplots(figsize=(10, 8))
    ax4.pie(column_counts, labels=column_counts.index, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
    ax4.axis('equal')  # Equal aspect ratio
    ax4.set_title("Non-Null Values in Columns", fontsize=14)
    st.pyplot(fig4)


# Footer
st.markdown("<hr><center>Made with ❤️ using Streamlit | Dataset: Google Play Store</center>", unsafe_allow_html=True)
