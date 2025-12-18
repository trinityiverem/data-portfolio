import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path


# ---------- COLOUR PALETTE ----------
LIGHT_BLUE = "#8fd7d7"
MED_BLUE = "#00b0be"
LIGHT_PINK = "#ff8ca1"   # adjusted to valid hex
MED_PINK = "#f45f74"
LIGHT_GREEN = "#bdd373"
MED_GREEN = "#98c127"
LIGHT_ORANGE = "#ffcd8e"
MED_ORANGE = "#ffb255"



# ---------- DATA LOADING ----------
@st.cache_data
def load_data():
    # Work out where this file lives
    current_dir = Path(__file__).resolve().parent

    # First, assume the CSV is in the same folder as this page file
    csv_path = current_dir / "world_happiness_report.csv"

    # If not there, fall back to the repo root (one level up)
    if not csv_path.exists():
        csv_path = current_dir.parent / "world_happiness_report.csv"

    # Now read from the resolved path
    df = pd.read_csv(csv_path)

    # Drop index column if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Standardise column names
    df = df.rename(
        columns={
            "Happiness Score": "HappinessScore",
            "Happiness Rank": "HappinessRank",
            "Economy (GDP per Capita)": "Economy",
            "Health (Life Expectancy)": "Health",
            "Trust (Government Corruption)": "Trust",
            "year": "Year",  # handles either 'year' or 'Year'
        }
    )

    numeric_cols = [
        "HappinessScore",
        "HappinessRank",
        "Standard Error",
        "Economy",
        "Family",
        "Health",
        "Freedom",
        "Trust",
        "Generosity",
        "Dystopia Residual",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Only keep rows with actual happiness scores and country names
    df = df[df["HappinessScore"].notna()]
    df = df[df["Country"].notna()]

    return df

df = load_data()

# Years that actually have data
valid_years = sorted(df["Year"].dropna().unique().tolist())

# ---------- SIDEBAR FILTERS ----------
st.sidebar.title("Filters")

selected_year = st.sidebar.selectbox("Year", valid_years)

regions = ["All regions"] + sorted(df["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

# Filter data by year and region
filtered = df[df["Year"] == selected_year].copy()
if selected_region != "All regions":
    filtered = filtered[filtered["Region"] == selected_region]

if filtered.empty:
    st.warning("No data for this selection. Try another year or region.")
    st.stop()

# ---------- PAGE TITLE & INTRO ----------
st.title("What makes countries happy? 🌍")

st.write(
    """
Join me to explore the World Happiness data, which scores countries based on factors such as 
income, social support, health, freedom and trust in government.

Use the filters on the left to choose a year and region, and explore:

- How happiness scores vary across countries and regions  
- How factors such as economy, health and freedom relate to happiness  
- How happiness changes over time for individual countries
"""
)

st.divider()

st.subheader("About the data")
st.write(
    """
This app uses World Happiness data for the years where complete country-level scores
and key factors are available. The goal is not to provide a live ranking, but to 
demonstrate how to clean, explore and visualise real-world data and investigate 
relationships between variables such as income, social support, health and freedom.
"""
)

st.divider()

st.write(
    """
**How to read the happiness scores (0–10)**  
- Around **0–3**: very low – people report being far from the “best possible life”.  
- Around **4–5**: mixed / below average – some positives, but significant challenges.  
- Around **6–7**: good – people generally feel satisfied with their lives.  
- **8 and above**: very high – among the happiest countries in the world for that year.

Most countries sit somewhere in the middle, so even a change of 0.3–0.5 points can be quite meaningful.
"""
)

st.divider()

# ---------- SUMMARY METRICS ----------
col1, col2, col3 = st.columns(3)

num_countries = len(filtered)
avg_score = filtered["HappinessScore"].mean()

top_row = filtered.sort_values("HappinessScore", ascending=False).iloc[0]
top_country = top_row["Country"]
top_score = top_row["HappinessScore"]

col1.metric("Countries in selection", num_countries)
col2.metric("Average happiness score (0–10)", f"{avg_score:.2f}")
col3.metric(f"Happiest country in {selected_year}", f"{top_country} ({top_score:.2f})")

st.markdown("---")

# ---------- HELPER: STYLE DATAFRAME HEADERS ----------
HEADER_STYLE = [
    {
        "selector": "th",
        "props": [("background-color", "#e0e0e0"), ("color", "black")],
    }
]

# ---------- TABS ----------
tab_overview, tab_drivers, tab_country = st.tabs(
    ["Overview", "Drivers of happiness", "Country focus"]
)

# ---------- TAB 1: OVERVIEW ----------
with tab_overview:
    st.subheader(f"Top 10 happiest countries in {selected_year}")

    top10 = (
        filtered.sort_values("HappinessScore", ascending=False)
        .head(10)
    )

    fig1, ax1 = plt.subplots(figsize=(7, 4))
    ax1.bar(top10["Country"], top10["HappinessScore"], color=MED_BLUE)
    ax1.set_ylabel("Happiness score (0–10)")
    ax1.set_xticklabels(top10["Country"], rotation=45, ha="right")
    st.pyplot(fig1)

    st.subheader(f"Average happiness score by region in {selected_year}")
    region_means = (
        df[df["Year"] == selected_year]
        .groupby("Region")["HappinessScore"]
        .mean()
        .sort_values(ascending=False)
    )

    

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.bar(region_means.index, region_means.values, color=MED_GREEN)
    ax2.set_ylabel("Average happiness score (0–10)")
    ax2.set_xticklabels(region_means.index, rotation=45, ha="right")
    st.pyplot(fig2)

    st.subheader("Distribution of happiness scores")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.hist(filtered["HappinessScore"], bins=15, color=MED_PINK, edgecolor="white")
    ax3.set_xlabel("Happiness score (0–10)")
    ax3.set_ylabel("Number of countries")
    st.pyplot(fig3)

    st.subheader("World map of happiness")
    st.write(
        "Colour intensity shows happiness scores (0–10) for each country in the selected year."
    )

    # Plotly choropleth map using your palette
    map_fig = px.choropleth(
        filtered,
        locations="Country",
        locationmode="country names",
        color="HappinessScore",
        hover_name="Country",
        color_continuous_scale=[
            LIGHT_PINK,
            MED_PINK,
            LIGHT_ORANGE,
            MED_ORANGE,
            LIGHT_GREEN,
            MED_GREEN,
            LIGHT_BLUE,
            MED_BLUE,
        ],
        range_color=(filtered["HappinessScore"].min(), filtered["HappinessScore"].max()),
        labels={"HappinessScore": "Happiness score (0–10)"},
        title=f"Happiness scores around the world ({selected_year})",
    )
    map_fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=450,
        coloraxis_colorbar=dict(title="Happiness"),
    )
    st.plotly_chart(map_fig, use_container_width=True)

    st.subheader("Overview insights")
    st.write(
        f"""
- In {selected_year}, the average happiness score in this selection is **{avg_score:.2f}**, 
  with **{top_country}** the happiest country (score **{top_score:.2f}**).
- The highest-scoring regions tend to combine stronger economies, better health outcomes 
  and higher levels of social support.
- The distribution chart shows how most countries cluster around the middle, with a smaller number 
  at the very high and very low ends of the happiness scale.
- The world map highlights clear clusters of higher happiness in some regions, and lower scores in others,
  making geographic patterns easy to see at a glance.
"""
    )
    st.divider()

    st.subheader("About the creator")
    st.write(
        """
I'm Trinity, a Computer Science graduate with a growing focus on data analysis and
data-driven problem solving. I built this app to practice working with real-world data,
explore how different factors relate to well-being, and showcase my skills in Python,
pandas, matplotlib, Plotly and Streamlit.
"""
    )

# ---------- TAB 2: DRIVERS OF HAPPINESS ----------
with tab_drivers:
    st.subheader("How do different factors relate to happiness?")

    factor_options = {
        "Economy (GDP per capita)": "Economy",
        "Family (social support)": "Family",
        "Health (life expectancy)": "Health",
        "Freedom": "Freedom",
        "Trust (government corruption)": "Trust",
        "Generosity": "Generosity",
    }

    selected_factor_label = st.selectbox(
        "Choose a factor to compare with happiness score",
        list(factor_options.keys()),
    )
    factor_col = factor_options[selected_factor_label]

    factor_df = filtered.dropna(subset=["HappinessScore", factor_col])

    if factor_df.empty:
        st.info("No data available for this factor in the current selection.")
    else:
        # Scatter plot
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        ax4.scatter(
            factor_df[factor_col],
            factor_df["HappinessScore"],
            color=MED_BLUE,
            alpha=0.8,
        )
        ax4.set_xlabel(selected_factor_label)
        ax4.set_ylabel("Happiness score (0–10)")
        st.pyplot(fig4)

        # Correlation
        if len(factor_df) > 2:
            corr = factor_df["HappinessScore"].corr(factor_df[factor_col])
            st.write(
                f"The correlation between happiness and {selected_factor_label.lower()} "
                f"in this selection is approximately **{corr:.2f}**."
            )

    st.subheader("Which factors correlate most with happiness?")

    corr_cols = ["HappinessScore", "Economy", "Family", "Health", "Freedom", "Trust", "Generosity"]
    corr_df = filtered[corr_cols].dropna()
    corr_series = corr_df.corr()["HappinessScore"].drop("HappinessScore").sort_values(ascending=False)

    styled_corr = (
        corr_series.to_frame("Correlation")
        .style
        .format({"Correlation": "{:.2f}"})
        .set_table_styles(HEADER_STYLE)
    )

    st.write("Correlation with happiness score (higher = stronger positive relationship):")
    st.dataframe(styled_corr)

    st.write(
        """
These correlations are not causal proof, but they give a useful indication of which factors 
tend to move with happiness. For example, economy and health usually show strong positive 
relationships with happiness, while trust and freedom can vary more by region.
"""
    )

# ---------- TAB 3: COUNTRY FOCUS ----------
with tab_country:
    st.subheader("Country trends over time")

    all_countries = sorted(df["Country"].dropna().unique().tolist())
    selected_country = st.selectbox("Country", all_countries)

    country_df = df[df["Country"] == selected_country].sort_values("Year")

    if country_df.empty:
        st.info("No data available for this country.")
    else:
        fig5, ax5 = plt.subplots(figsize=(7, 4))
        ax5.plot(
            country_df["Year"],
            country_df["HappinessScore"],
            marker="o",
            color=MED_BLUE,
        )
        ax5.set_xlabel("Year")
        ax5.set_ylabel("Happiness score (0–10)")
        ax5.set_title(f"Happiness score over time: {selected_country}")
        st.pyplot(fig5)

        st.write("Key factors over time:")
        country_table = country_df[
            [
                "Year",
                "HappinessRank",
                "HappinessScore",
                "Economy",
                "Family",
                "Health",
                "Freedom",
                "Trust",
                "Generosity",
            ]
        ].reset_index(drop=True)

        styled_country = country_table.style.set_table_styles(HEADER_STYLE)
        st.dataframe(styled_country)

        start_year = int(country_df["Year"].min())
        end_year = int(country_df["Year"].max())
        first_score = country_df.loc[country_df["Year"] == start_year, "HappinessScore"].iloc[0]
        last_score = country_df.loc[country_df["Year"] == end_year, "HappinessScore"].iloc[0]

        if last_score > first_score:
            trend = "increased"
        elif last_score < first_score:
            trend = "decreased"
        else:
            trend = "stayed fairly stable"

        score_change = last_score - first_score
        score_change_abs = abs(score_change)

        # Find which factor changed most for this country
        factor_cols = ["Economy", "Family", "Health", "Freedom", "Trust", "Generosity"]
        factor_changes = {}
        for fc in factor_cols:
            if fc in country_df.columns:
                first_val = country_df.loc[country_df["Year"] == start_year, fc].iloc[0]
                last_val = country_df.loc[country_df["Year"] == end_year, fc].iloc[0]
                if pd.notna(first_val) and pd.notna(last_val):
                    factor_changes[fc] = last_val - first_val

        if factor_changes:
            # Factor with largest absolute change
            top_factor = max(factor_changes, key=lambda k: abs(factor_changes[k]))
            top_change = factor_changes[top_factor]
            top_change_abs = abs(top_change)
            if top_change > 0:
                factor_direction = "increased"
            elif top_change < 0:
                factor_direction = "decreased"
            else:
                factor_direction = "stayed roughly the same"
            factor_phrase = (
                f"The biggest change over this period is in **{top_factor}**, which has "
                f"{factor_direction} by about **{top_change_abs:.2f}** points."
            )
        else:
            top_factor = None
            factor_phrase = (
                "The main happiness factors for this country appear relatively stable "
                "over the available years."
            )

        # Compare country to its region in the final year
        region = country_df["Region"].mode().iloc[0] if "Region" in country_df.columns else None
        if region is not None:
            region_df_final = df[(df["Year"] == end_year) & (df["Region"] == region)]
            region_mean_final = region_df_final["HappinessScore"].mean() if not region_df_final.empty else None
        else:
            region_mean_final = None

        if region_mean_final and pd.notna(region_mean_final):
            if last_score > region_mean_final:
                comp_phrase = (
                    f"In **{end_year}**, {selected_country}'s happiness score "
                    f"(**{last_score:.2f}**) is **above** the {region} average of "
                    f"**{region_mean_final:.2f}**."
                )
            elif last_score < region_mean_final:
                comp_phrase = (
                    f"In **{end_year}**, {selected_country}'s happiness score "
                    f"(**{last_score:.2f}**) is **below** the {region} average of "
                    f"**{region_mean_final:.2f}**."
                )
            else:
                comp_phrase = (
                    f"In **{end_year}**, {selected_country}'s happiness score "
                    f"(**{last_score:.2f}**) is very close to the {region} average "
                    f"of **{region_mean_final:.2f}**."
                )
        else:
            comp_phrase = (
                f"Regional comparison for {selected_country} in {end_year} is not available "
                "in this dataset."
            )

        if score_change > 0:
            feeling_phrase = "people now report being happier than before"
        elif score_change < 0:
            feeling_phrase = "people now report being less happy than before"
        else:
            feeling_phrase = "overall reported happiness has been very stable"

        st.subheader("Country insights")
        st.write(
            f"""
- Between **{start_year}** and **{end_year}**, {selected_country}'s happiness score has **{trend}**, 
  changing by about **{score_change_abs:.2f}** points (from **{first_score:.2f}** to **{last_score:.2f}**).
- This suggests that in {selected_country}, {feeling_phrase} over this period.
- {factor_phrase}
- {comp_phrase}
"""
        )
