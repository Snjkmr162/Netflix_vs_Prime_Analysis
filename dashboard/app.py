"""
Netflix vs Prime Video — Streamlit Dashboard
Quantitative Analysis (Part 1)
Run: streamlit run dashboard/app.py
"""

import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Netflix vs Prime Video Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NETFLIX_COLOR = "#E50914"
PRIME_COLOR   = "#00A8E1"
COLOR_MAP     = {"Netflix": NETFLIX_COLOR, "Prime Video": PRIME_COLOR}

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    path = os.path.join(
        os.path.dirname(__file__), "..", "data", "processed", "clean_titles.csv"
    )
    df = pd.read_csv(path)
    df["year"]         = pd.to_numeric(df["year"],         errors="coerce")
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["popularity"]   = pd.to_numeric(df["popularity"],   errors="coerce")
    return df


df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    width=120,
)
st.sidebar.markdown("---")
st.sidebar.title("Filters")

year_min = int(df["year"].min())
year_max = int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(2015, year_max),
)

content_type = st.sidebar.multiselect(
    "Content type",
    options=["movie", "tv_series"],
    default=["movie", "tv_series"],
    format_func=lambda x: "Movie" if x == "movie" else "TV Series",
)

platforms = st.sidebar.multiselect(
    "Platforms",
    options=["Netflix", "Prime Video"],
    default=["Netflix", "Prime Video"],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Part 1 — Quantitative Analysis**\n\n"
    "Part 2 (Sentiment Analysis) coming soon once Reddit API access is granted."
)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df[
    (df["year"]     >= year_range[0]) &
    (df["year"]     <= year_range[1]) &
    (df["type"].isin(content_type))   &
    (df["platform"].isin(platforms))
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎬 Netflix vs Prime Video — Content Strategy Analysis")
st.markdown(
    "Analyzing **500 current titles** pulled live from the "
    "**Watchmode API** and enriched with **TMDb metadata**. "
    "Use the sidebar filters to explore the data."
)
st.markdown("---")

# ── KPI row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

for col, platform, color in zip(
    [col1, col2], ["Netflix", "Prime Video"], [NETFLIX_COLOR, PRIME_COLOR]
):
    p = filtered[filtered["platform"] == platform]
    col.metric(f"**{platform}** Titles", f"{len(p):,}")

col3.metric("Netflix Avg Rating",
            f"{filtered[filtered['platform']=='Netflix']['vote_average'].mean():.2f}")
col4.metric("Prime Avg Rating",
            f"{filtered[filtered['platform']=='Prime Video']['vote_average'].mean():.2f}")
col5.metric("Netflix Intl %",
            f"{filtered[filtered['platform']=='Netflix']['is_international'].mean()*100:.1f}%",
            delta=f"vs Prime {filtered[filtered['platform']=='Prime Video']['is_international'].mean()*100:.1f}%")

st.markdown("---")

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Platform Growth",
    "🎭 Genre Strategy",
    "⭐ Ratings & Quality",
    "🌍 International",
])


# ── Tab 1: Platform Growth ────────────────────────────────────────────────────
with tab1:
    st.subheader("Content Added Per Year")

    yearly = (
        filtered.groupby(["year", "platform"])
        .size()
        .reset_index(name="count")
    )

    fig = px.line(
        yearly, x="year", y="count", color="platform",
        color_discrete_map=COLOR_MAP,
        markers=True,
        labels={"count": "Number of Titles", "year": "Year"},
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig.update_layout(
        template="plotly_dark",
        height=420,
        legend=dict(title=""),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Movies vs TV Series")
        type_counts = (
            filtered.groupby(["platform", "type"])
            .size()
            .reset_index(name="count")
        )
        type_counts["type"] = type_counts["type"].map(
            {"movie": "Movie", "tv_series": "TV Series"}
        )
        fig2 = px.bar(
            type_counts, x="platform", y="count", color="type",
            barmode="group",
            color_discrete_sequence=["#f5c518", "#888888"],
            labels={"count": "Titles", "platform": ""},
        )
        fig2.update_layout(template="plotly_dark", height=350, legend=dict(title=""))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Content by Decade")
        decade_counts = (
            filtered.groupby(["decade", "platform"])
            .size()
            .reset_index(name="count")
        )
        decade_counts["decade"] = decade_counts["decade"].astype(str) + "s"
        fig3 = px.bar(
            decade_counts, x="decade", y="count", color="platform",
            barmode="group", color_discrete_map=COLOR_MAP,
            labels={"count": "Titles", "decade": "Decade"},
        )
        fig3.update_layout(template="plotly_dark", height=350, legend=dict(title=""))
        st.plotly_chart(fig3, use_container_width=True)


# ── Tab 2: Genre Strategy ─────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Genres")
        platform_sel = st.selectbox(
            "Select platform", ["Netflix", "Prime Video"], key="genre_platform"
        )
        genre_data = (
            filtered[filtered["platform"] == platform_sel]["primary_genre"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        genre_data.columns = ["genre", "count"]
        fig4 = px.bar(
            genre_data, x="count", y="genre",
            orientation="h",
            color="count",
            color_continuous_scale=["#333", NETFLIX_COLOR if platform_sel == "Netflix" else PRIME_COLOR],
            labels={"count": "Titles", "genre": ""},
        )
        fig4.update_layout(template="plotly_dark", height=400,
                           coloraxis_showscale=False)
        fig4.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        st.subheader("Genre Heatmap")
        top_genres = (
            filtered["primary_genre"]
            .value_counts()
            .head(10)
            .index.tolist()
        )
        pivot = (
            filtered[filtered["primary_genre"].isin(top_genres)]
            .groupby(["primary_genre", "platform"])
            .size()
            .unstack(fill_value=0)
        )
        fig5 = px.imshow(
            pivot,
            color_continuous_scale="RdBu",
            aspect="auto",
            labels=dict(color="Titles"),
        )
        fig5.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig5, use_container_width=True)


# ── Tab 3: Ratings ────────────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rating Distribution")
        fig6 = px.box(
            filtered[filtered["vote_average"] > 0],
            x="platform", y="vote_average",
            color="platform", color_discrete_map=COLOR_MAP,
            points="outliers",
            labels={"vote_average": "TMDb Rating", "platform": ""},
        )
        fig6.update_layout(template="plotly_dark", height=380,
                           showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        st.subheader("Avg Rating Over Time")
        yearly_r = (
            filtered[filtered["vote_average"] > 0]
            .groupby(["year", "platform"])["vote_average"]
            .mean()
            .reset_index()
        )
        fig7 = px.line(
            yearly_r, x="year", y="vote_average",
            color="platform", color_discrete_map=COLOR_MAP,
            markers=True,
            labels={"vote_average": "Avg Rating", "year": "Year"},
        )
        fig7.update_layout(template="plotly_dark", height=380,
                           legend=dict(title=""), hovermode="x unified")
        st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Rating Category Breakdown")
    cat_counts = (
        filtered.groupby(["platform", "rating_category"])
        .size()
        .reset_index(name="count")
    )
    totals = cat_counts.groupby("platform")["count"].transform("sum")
    cat_counts["pct"] = (cat_counts["count"] / totals * 100).round(1)

    fig8 = px.bar(
        cat_counts, x="rating_category", y="pct",
        color="platform", barmode="group",
        color_discrete_map=COLOR_MAP,
        category_orders={"rating_category": ["Poor", "Average", "Good", "Great"]},
        labels={"pct": "% of Titles", "rating_category": "Category"},
        text="pct",
    )
    fig8.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig8.update_layout(template="plotly_dark", height=380, legend=dict(title=""))
    st.plotly_chart(fig8, use_container_width=True)


# ── Tab 4: International ──────────────────────────────────────────────────────
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("International Content Share")
        intl = (
            filtered.groupby(["platform", "is_international"])
            .size()
            .reset_index(name="count")
        )
        intl["label"] = intl["is_international"].map(
            {True: "International", False: "English"}
        )
        fig9 = px.pie(
            intl, values="count", names="label",
            facet_col="platform",
            color="label",
            color_discrete_map={
                "International": "#f5c518",
                "English": "#444444",
            },
            hole=0.4,
        )
        fig9.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        st.subheader("International % Over Time")
        intl_yr = (
            filtered.groupby(["year", "platform", "is_international"])
            .size()
            .reset_index(name="count")
        )
        totals = intl_yr.groupby(["year", "platform"])["count"].transform("sum")
        intl_yr["pct"] = intl_yr["count"] / totals * 100
        intl_only = intl_yr[intl_yr["is_international"] == True]

        fig10 = px.line(
            intl_only, x="year", y="pct",
            color="platform", color_discrete_map=COLOR_MAP,
            markers=True,
            labels={"pct": "% International", "year": "Year"},
        )
        fig10.update_layout(template="plotly_dark", height=380,
                            legend=dict(title=""), hovermode="x unified")
        st.plotly_chart(fig10, use_container_width=True)

    st.subheader("Top Producing Countries")
    platform_intl = st.selectbox(
        "Select platform", ["Netflix", "Prime Video"], key="intl_platform"
    )
    countries = (
        filtered[filtered["platform"] == platform_intl]["production_countries"]
        .dropna()
        .str.split("|")
        .explode()
        .str.strip()
        .value_counts()
        .head(15)
        .reset_index()
    )
    countries.columns = ["country", "count"]
    fig11 = px.bar(
        countries, x="count", y="country",
        orientation="h",
        color="count",
        color_continuous_scale=["#333",
            NETFLIX_COLOR if platform_intl == "Netflix" else PRIME_COLOR],
        labels={"count": "Titles", "country": ""},
    )
    fig11.update_layout(template="plotly_dark", height=450,
                        coloraxis_showscale=False)
    fig11.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig11, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "**Part 1 — Quantitative Analysis** | "
    "Data: Watchmode API + TMDb API | 500 titles | 2026  \n"
    "⏳ **Part 2 — Sentiment Analysis** (Reddit) coming soon."
)