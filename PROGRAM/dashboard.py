import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(
    page_title="Aadhaar Service Monitoring & Planning Platform",
    layout="wide"
)

st.title("Aadhaar Service Monitoring & Planning Platform")
st.caption("Service Stress • Bottlenecks • Decision Support")

# --------------------------------
# LOAD READY DATA
# --------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("aadhaar_bottleneck_prediction.csv")

df = load_data()






st.subheader("📊 Aadhaar Service Stress Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Average ASSI", round(df["assi"].mean(), 1))
c2.metric("Maximum ASSI", round(df["assi"].max(), 1))
c3.metric("High-Stress Regions", df[df["assi"] >= 60].shape[0])
c4.metric("Low-Stress Regions", df[df["assi"] < 30].shape[0])



st.subheader("🚨 Top States by Aadhaar Service Stress Index (ASSI)")

top_assi = df.sort_values("assi", ascending=False).head(10)

st.dataframe(
    top_assi[
        ["state", "assi", "bottleneck_risk", "recommended_action"]
    ]
)



st.subheader("📊 ASSI Distribution (Top 10 States)")

fig, ax = plt.subplots(figsize=(8,4))
top_assi.set_index("state")["assi"].plot(kind="bar", ax=ax)
ax.set_ylabel("ASSI (0–100)")
ax.set_title("Highest Aadhaar Service Stress Levels")
st.pyplot(fig)



# -------------------------------
# ASSI WHAT-IF POLICY SIMULATOR
# -------------------------------

st.subheader("🎛 ASSI What-If Policy Simulator")

# State selection (unique key to avoid Streamlit errors)
state = st.selectbox(
    "Select State",
    df["state"].unique(),
    key="assi_policy_state"
)

# Slider for intervention simulation
centers = st.slider(
    "Add Temporary Enrollment Centers",
    min_value=0,
    max_value=10,
    value=5,
    step=1
)

# Fetch current ASSI
current_assi = df.loc[df["state"] == state, "assi"].values[0]

# Policy assumption: each center reduces ASSI by 2%
new_assi = current_assi * (1 - centers * 0.02)

# Display metrics
c1, c2 = st.columns(2)

c1.metric(
    "Current ASSI",
    round(current_assi, 1)
)

c2.metric(
    "Post-Intervention ASSI",
    round(new_assi, 1),
    delta=round(new_assi - current_assi, 1)
)

st.caption(
    "Assumption: Each temporary enrollment center reduces ASSI by ~2% (illustrative policy simulation)."
)







if "ies_score" not in df.columns:
    st.error("Intervention Efficiency data missing. Please re-run adhar.py.")
    st.stop()





st.subheader("🎯 Intervention Efficiency Analysis (High-ROI Zones)")

top_ies = df.sort_values("ies_score", ascending=False).head(10)

st.dataframe(
    top_ies[
        [
            "state",
            "assi",
            "ies_score",
            "intervention_priority",
            "recommended_action"
        ]
    ],
    use_container_width=True
)




fig, ax = plt.subplots(figsize=(8,4))

top_ies.set_index("state")["ies_score"].plot(
    kind="bar",
    ax=ax,
    color="green"
)

ax.set_ylabel("Intervention Efficiency Score (0–100)")
ax.set_title("Top High-ROI Aadhaar Intervention Regions")

st.pyplot(fig)




# --------------------------------
# KPI METRICS
# --------------------------------
st.subheader("📊 National Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "High Bottleneck Regions",
    df[df["bottleneck_risk"] == "High Bottleneck Risk"].shape[0]
)

c2.metric(
    "Average Update Pressure",
    round(df["update_pressure"].mean(), 2)
)

c3.metric(
    "Maximum Update Pressure",
    round(df["update_pressure"].max(), 2)
)

c4.metric(
    "Low Risk Regions",
    df[df["bottleneck_risk"] == "Low Risk"].shape[0]
)




st.subheader("🔍 State-wise Drill Down")

# State selector (UNIQUE KEY is IMPORTANT)
selected_state = st.selectbox(
    "Select a State to View Details",
    sorted(df["state"].unique()),
    key="state_drilldown_selector"
)

# Filter data
state_data = df[df["state"] == selected_state]

# ----------------------------
# KPI CARDS FOR SELECTED STATE
# ----------------------------
st.markdown(f"### 📍 {selected_state.title()} – Service Stress Snapshot")

c1, c2, c3 = st.columns(3)

c1.metric("ASSI Score", round(state_data["assi"].values[0], 1))
c2.metric("Bottleneck Risk", state_data["bottleneck_risk"].values[0])
c3.metric("Update Pressure", round(state_data["update_pressure"].values[0], 2))

# ----------------------------
# DETAILED TABLE
# ----------------------------
st.markdown("### 📊 Detailed Metrics")

st.dataframe(
    state_data[[
        "enrolment_count",
        "demographic_updates",
        "biometric_updates",
        "update_pressure",
        "assi",
        "bottleneck_risk",
        "recommended_action"
    ]]
)
st.markdown("### 🧠 Stress Contributors")

contributors = state_data[[
    "enrolment_count",
    "demographic_updates",
    "biometric_updates"
]].T

contributors.columns = ["Value"]
st.bar_chart(contributors)












# --------------------------------
# VISUALS
# --------------------------------
left, right = st.columns(2)

with left:
    st.subheader("📈 Enrolment vs Update Pressure")
    fig, ax = plt.subplots()
    ax.scatter(
        df["enrolment_count"],
        df["update_pressure"],
        alpha=0.6
    )
    ax.set_xlabel("Enrolment Count")
    ax.set_ylabel("Update Pressure")
    st.pyplot(fig)

with right:
    st.subheader("🧩 Update Composition")
    fig2, ax2 = plt.subplots()
    ax2.pie(
        [
            df["biometric_updates"].sum(),
            df["demographic_updates"].sum()
        ],
        labels=["Biometric Updates", "Demographic Updates"],
        autopct="%1.1f%%",
        startangle=90
    )
    st.pyplot(fig2)
    
    
    
    
    st.subheader("🗺️ India Map – Aadhaar Service Stress Index (ASSI)")

@st.cache_data
def load_india_map():
    india = gpd.read_file("INDIA_STATES.geojson")

    # Automatically detect state-name column
    state_col = [c for c in india.columns if c.lower() != "geometry"][0]

    india["state"] = india[state_col].str.strip().str.lower()
    return india

india_map = load_india_map()

# Prepare ASSI data
map_df = df.copy()
map_df["state"] = map_df["state"].str.lower()

# Fix common name mismatches
state_fix = {
    "nct of delhi": "delhi",
    "andaman & nicobar islands": "andaman and nicobar islands",
    "dadra and nagar haveli and daman and diu":
        "dadra and nagar haveli and daman and diu"
}

india_map["state"] = india_map["state"].replace(state_fix)
map_df["state"] = map_df["state"].replace(state_fix)

# Merge map with ASSI data
merged = india_map.merge(
    map_df,
    on="state",
    how="left"
)

# Plot map
fig, ax = plt.subplots(figsize=(8, 10))

merged.plot(
    column="assi",
    cmap="Reds",
    linewidth=0.6,
    ax=ax,
    edgecolor="black",
    legend=True,
    legend_kwds={"label": "ASSI (0–100)"}
)

ax.set_title(
    "India: Aadhaar Service Stress Index (ASSI)",
    fontsize=14
)
ax.axis("off")

st.pyplot(fig)

    
    
    
    
    
    
    
    
    
    
    

# --------------------------------
# INTERVENTION PLANNER
# --------------------------------
st.subheader("🚨 Intervention Planner (Top 10 Regions)")

top10 = df.sort_values(
    "update_pressure",
    ascending=False
).head(10)

st.dataframe(
    top10[
        [
            "state",
            "update_pressure",
            "bottleneck_risk",
            "recommended_action"
        ]
    ]
)




# WHAT-IF POLICY SIMULATOR
# --------------------------------
st.subheader("🎛 What-If Policy Simulator")

state = st.selectbox(
    "Select State",
    df["state"].unique(),
    key="policy_state_select"
)

centers = st.slider(
    "Add Temporary Centers",
    0, 10, 5,
    key="policy_centers_slider"
)

current_pressure = df.loc[
    df["state"] == state, "update_pressure"
].values[0]

# Conservative assumption
new_pressure = current_pressure * (1 - centers * 0.02)

c1, c2 = st.columns(2)
c1.metric("Current Pressure", round(current_pressure, 2))
c2.metric("Post-Intervention Pressure", round(new_pressure, 2))
# --------------------------------






# --------------------------------
# DATA VIEW (OPTIONAL)
# --------------------------------
with st.expander("📄 View Full Data"):
    st.dataframe(df)
