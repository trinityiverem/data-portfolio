import streamlit as st

st.set_page_config(
    page_title="Trinity | Data Portfolio",
    page_icon="📊",
    layout="centered",
)

st.title("Trinity – Data Portfolio")
st.write(
    """
Welcome to my interactive data portfolio.  
Here you can explore projects I've built using Python, data analysis and visualisation tools.
Click a project card below to open and interact with it.
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
economy, health, social support and freedom relate to overall happiness scores
across countries and regions.
"""
    )
    st.page_link(
        "pages/1_World_Happiness_Explorer.py",
        label="Open project",
        icon="➡️",
    )

with col2:
    st.markdown("### 📈 Coming soon")
    st.write(
        """
This space is reserved for my next project, focused on real-world data
and practical decision-making.
"""
    )
    st.button("Project locked", disabled=True)

st.divider()

st.write(
    """
If you'd like to get in touch about my work, you can find me on LinkedIn
or contact me via email.
"""
)
