import streamlit as st

st.markdown("---")
st.header("Public Service Performance Dashboard")
st.caption("Power BI | Independent portfolio project using publicly available OPG/HMCTS data")

col1, col2 = st.columns([1.4, 1])

with col1:
    st.image("solar_system_bot/images/dashboard.png", use_container_width=True)

with col2:
    st.markdown("#### Overview")
    st.write(
        """
        Built to demonstrate KPI reporting, dashboard design, and performance analysis
        in a stakeholder-facing format.
        """
    )

    st.markdown("#### Tools")
    st.markdown("Power BI · KPI design · Data modelling · Performance analysis")

    st.markdown("#### Focus")
    st.markdown(
        """
        - Demand and throughput trends  
        - Backlog and timeliness  
        - Regional and service-area comparison  
        - Decision-useful reporting
        """
    )

st.markdown("### Project Summary")
st.write(
    """
    This dashboard was designed to show how performance metrics interact over time,
    rather than presenting isolated visuals. It tracks demand, throughput, backlog,
    and timeliness to help surface patterns, pressure points, and service variation.
    """
)

st.markdown("### What I contributed")
st.markdown(
    """
    - Defined KPIs and reporting structure  
    - Prepared data for dashboard use  
    - Built measures for comparison and trend analysis  
    - Designed visuals for clarity and usability  
    - Framed the dashboard around stakeholder decision-making
    """
)

st.success(
    "Key insight: viewing intake, output, and backlog together gives a stronger "
    "picture of whether demand is being absorbed or pressure is building."
)

st.caption(
    "Independent portfolio project created using publicly available data. "
    "Not affiliated with or endorsed by the Ministry of Justice."
)