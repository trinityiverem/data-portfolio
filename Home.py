import streamlit as st

st.set_page_config(
    page_title="Trinity | Data Portfolio",
    page_icon="📊",
    layout="centered",
)

st.title("Trinity's Data Portfolio")
st.write(
    """
Welcome to my interactive data portfolio.  
Here you can explore projects I’ve built across data analysis, dashboarding, Python, and visualisation tools.  
Click a project card below to view each project.
"""
)

st.divider()

st.subheader("Projects")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌍 World Happiness Explorer")
    st.write(
        """
An interactive dashboard exploring World Happiness data, looking at how
economy, health, social support, and freedom relate to overall happiness
scores across countries and regions.
"""
    )
    st.page_link(
        "pages/1_World_Happiness_Explorer.py",
        label="Open project",
        icon="➡️",
    )

with col2:
    st.markdown("### 🪐 Solar System Learning Hub")
    st.write(
        """
An interactive learning app that combines a rule-based chatbot, a planet
explorer with animations, and a quiz to make the Solar System easier to
understand.
"""
    )
    st.page_link(
        "pages/2_Solar_System_Learning_Hub.py",
        label="Open project",
        icon="➡️",
    )

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.markdown("### 📈 Public Service Performance Dashboard")
    st.write(
        """
A Power BI dashboard built using publicly available OPG/HMCTS data to track
demand, throughput, backlog, and timeliness across service areas and regions,
with a focus on KPI reporting and stakeholder-friendly insight.
"""
    )
    st.page_link(
        "pages/3_Public_Service_Performance_Dashboard.py",
        label="Open project",
        icon="➡️",
    )

with col4:
    st.empty()

st.divider()

st.write(
    """
If you'd like to get in touch about my work, you can find me on LinkedIn
or contact me via email.
"""
)