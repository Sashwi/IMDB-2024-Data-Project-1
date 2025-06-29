import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt

# ---- DATABASE CONFIG ----
user = "3GKvmKYDkcwtLEJ.root"
password = "ZXoXz9ZyLjhQrn5O"
host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
port = 4000
database = "imdb2024"
ssl_ca_path = "ca.pem"  # Make sure it's in same folder or give full path

# Create SQLAlchemy connection
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl_ca={ssl_ca_path}"
)

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    query = "SELECT * FROM movies"
    df = pd.read_sql(query, con=engine)
    return df

df = load_data()

st.title("🎬 IMDb 2024 Movie Dashboard")

# ---- FILTERS ----
with st.sidebar:
    st.header("🔍 Filter Movies")
    genre_filter = st.multiselect("Select Genre(s)", options=df['Genre'].unique(), default=None)
    min_rating, max_rating = st.slider("Rating Range", 0.0, 10.0, (0.0, 10.0), 0.1)
    min_duration, max_duration = st.slider("Duration (min)", 30, 300, (60, 180), 10)
    min_votes = st.number_input("Minimum Votes", min_value=0, value=10000)

# Apply filters
filtered_df = df[
    (df['Rating'] >= min_rating) &
    (df['Rating'] <= max_rating) &
    (df['Duration (min)'] >= min_duration) &
    (df['Duration (min)'] <= max_duration) &
    (df['Voting'] >= min_votes)
]

if genre_filter:
    filtered_df = filtered_df[filtered_df['Genre'].isin(genre_filter)]

# ---- DISPLAY FILTERED RESULTS ----
st.subheader("🎥 Filtered Movies")
st.dataframe(filtered_df)

# ---- VISUALIZATIONS ----
st.subheader("📊 Top 10 Movies by Rating")
top10 = filtered_df.sort_values(by=['Rating', 'Voting'], ascending=False).head(10)
st.dataframe(top10[['Title', 'Genre', 'Rating', 'Voting']])

st.subheader("🎭 Genre Distribution")
genre_count = df['Genre'].value_counts()
st.bar_chart(genre_count)

st.subheader("⏱️ Average Duration by Genre")
avg_duration = df.groupby("Genre")["Duration (min)"].mean().sort_values()
st.bar_chart(avg_duration)

st.subheader("⭐ Rating Distribution")
fig, ax = plt.subplots()
sns.histplot(df["Rating"], bins=20, kde=True, ax=ax)
st.pyplot(fig)

st.subheader("🎬 Genre vs Average Rating")
avg_rating = df.groupby("Genre")["Rating"].mean().sort_values(ascending=False)
st.bar_chart(avg_rating)
