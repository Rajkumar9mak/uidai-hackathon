import pandas as pd
import glob
import os


def load_csvs_from_folder(folder_path):
    csv_files = glob.glob(
        os.path.join(folder_path, "**", "*.csv"),
        recursive=True
    )

    print(f"\nSearching in folder: {folder_path}")
    print("CSV files found:", csv_files)

    df_list = []
    for file in csv_files:
        print("Reading:", file)
        df = pd.read_csv(file, encoding="latin1")
        df_list.append(df)

    if not df_list:
        raise ValueError(f"No CSV files found in {folder_path}")

    return pd.concat(df_list, ignore_index=True)


print("program started...")

# 2️⃣ Folder-based loading (THIS IS STEP 2)
enrol = load_csvs_from_folder("api_data_aadhar_enrolment")
demo  = load_csvs_from_folder("api_data_aadhar_demographic")
bio   = load_csvs_from_folder("api_data_aadhar_biometric")




print("Enrolment loaded:", enrol.shape)
print("Demographic loaded:", demo.shape)
print("Biometric loaded:", bio.shape)

print("\nENROLMENT COLUMNS:")
print(enrol.columns)

print("\nDEMOGRAPHIC UPDATE COLUMNS:")
print(demo.columns)

print("\nBIOMETRIC UPDATE COLUMNS:")
print(bio.columns)


# -------------------------------
# STEP 2: DATA CLEANING
# -------------------------------

# Make column names lowercase & clean
enrol.columns = enrol.columns.str.strip().str.lower()
demo.columns  = demo.columns.str.strip().str.lower()
bio.columns   = bio.columns.str.strip().str.lower()

print("\nCleaned Enrolment Columns:", enrol.columns)
print("Cleaned Demographic Columns:", demo.columns)
print("Cleaned Biometric Columns:", bio.columns)




# -------------------------------
# STEP 3: LIFECYCLE METRICS
# -------------------------------

# Rename common columns (adjust if names differ)
enrol = enrol.rename(columns={
    enrol.columns[-1]: "enrolment_count"
})

demo = demo.rename(columns={
    demo.columns[-1]: "demographic_updates"
})

bio = bio.rename(columns={
    bio.columns[-1]: "biometric_updates"
})

# Aggregate state-wise
enrol_state = enrol.groupby("state")["enrolment_count"].sum()
demo_state  = demo.groupby("state")["demographic_updates"].sum()
bio_state   = bio.groupby("state")["biometric_updates"].sum()

# Combine lifecycle data
lifecycle = pd.concat([enrol_state, demo_state, bio_state], axis=1).fillna(0)

# Total updates & ratio
lifecycle["total_updates"] = (
    lifecycle["demographic_updates"] + lifecycle["biometric_updates"]
)

lifecycle["update_ratio"] = (
    lifecycle["total_updates"] / lifecycle["enrolment_count"]
)

print("\nAadhaar Lifecycle Table:")
print(lifecycle.head())




# -------------------------------
# STEP 4: DATA CLEANING
# -------------------------------

# Standardize state names
lifecycle.index = lifecycle.index.str.strip().str.lower()

# Merge duplicate Andaman names
lifecycle = lifecycle.rename(index={
    "andaman & nicobar islands": "andaman and nicobar islands"
})

# Remove invalid state codes (numeric-only)
lifecycle = lifecycle[~lifecycle.index.str.isnumeric()]

# Remove zero enrolment rows (cannot compute lifecycle)
lifecycle = lifecycle[lifecycle["enrolment_count"] > 0]

print("\nCleaned Lifecycle Table:")
print(lifecycle.head())




# -------------------------------
# STEP 5: REGION CLASSIFICATION
# -------------------------------

def classify_region(ratio):
    if ratio < 1:
        return "Stable Identity Region"
    elif ratio < 5:
        return "Moderate Update Region"
    else:
        return "High Mobility / High Correction Region"

lifecycle["region_type"] = lifecycle["update_ratio"].apply(classify_region)

print("\nRegion Classification:")
print(lifecycle[["update_ratio", "region_type"]].head())




import matplotlib.pyplot as plt

lifecycle["update_ratio"].sort_values(ascending=False).head(10).plot(
    kind="bar",
    figsize=(10,5),
    title="Top States by Aadhaar Update Ratio"
)

plt.ylabel("Update Ratio")
plt.show()




# -------------------------------
# STEP 6: BOTTLENECK SIGNAL
# -------------------------------

lifecycle["update_pressure"] = lifecycle["update_ratio"]

print("\nUpdate Pressure (Bottleneck Signal):")
print(lifecycle["update_pressure"].describe())





# -------------------------------
# STEP 7: BOTTLENECK RISK PREDICTION
# -------------------------------

def bottleneck_risk(pressure):
    if pressure < 1:
        return "Low Risk"
    elif pressure < 5:
        return "Medium Risk"
    else:
        return "High Bottleneck Risk"

lifecycle["bottleneck_risk"] = lifecycle["update_pressure"].apply(bottleneck_risk)

print("\nBottleneck Risk Prediction:")
print(
    lifecycle[["update_pressure", "bottleneck_risk"]]
    .sort_values("update_pressure", ascending=False)
    .head(10)
)




# -------------------------------
# STEP 8: ENROLMENT DROPOUT RISK (PROXY)
# -------------------------------

median_enrolment = lifecycle["enrolment_count"].median()

lifecycle["dropout_risk"] = lifecycle.apply(
    lambda row: "High Dropout Risk"
    if row["bottleneck_risk"] == "High Bottleneck Risk"
    and row["enrolment_count"] < median_enrolment
    else "Low Dropout Risk",
    axis=1
)

print("\nDropout Risk Prediction:")
print(
    lifecycle[["enrolment_count", "bottleneck_risk", "dropout_risk"]]
    .head(10)
)





# -------------------------------
# STEP 9: ACTION RECOMMENDATIONS
# -------------------------------

def recommend_action(risk):
    if risk == "High Bottleneck Risk":
        return "Deploy temporary enrolment centres / vans"
    elif risk == "Medium Risk":
        return "Increase staffing during peak hours"
    else:
        return "No immediate intervention required"

lifecycle["recommended_action"] = lifecycle["bottleneck_risk"].apply(recommend_action)

print("\nActionable Recommendations:")
print(
    lifecycle[[
        "update_pressure",
        "bottleneck_risk",
        "dropout_risk",
        "recommended_action"
    ]]
    .head(10)
)





# -------------------------------
# STEP 10: ASSI V2 (SERVICE STRESS INDEX)
# -------------------------------

# Base components
lifecycle["friction_pressure"] = (
    lifecycle["total_updates"] / lifecycle["enrolment_count"]
)

lifecycle["update_load"] = lifecycle["total_updates"]

lifecycle["biometric_pressure"] = (
    lifecycle["biometric_updates"] / lifecycle["total_updates"]
)

lifecycle["enrolment_weakness"] = 1 / lifecycle["enrolment_count"]

# Normalization
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

lifecycle["fp_norm"] = normalize(lifecycle["friction_pressure"])
lifecycle["ul_norm"] = normalize(lifecycle["update_load"])
lifecycle["bp_norm"] = normalize(lifecycle["biometric_pressure"])
lifecycle["ew_norm"] = normalize(lifecycle["enrolment_weakness"])

# ASSI score (0–100)
lifecycle["assi"] = (
    0.35 * lifecycle["fp_norm"] +
    0.25 * lifecycle["ul_norm"] +
    0.20 * lifecycle["bp_norm"] +
    0.20 * lifecycle["ew_norm"]
) * 100

lifecycle["assi"] = lifecycle["assi"].round(1)

print("\nASSI (Aadhaar Service Stress Index) added:")
print(lifecycle[["assi"]].head())

# Optional: plot top ASSI states
lifecycle.sort_values("assi", ascending=False).head(10)[
    "assi"
].plot(
    kind="bar",
    figsize=(10,5),
    title="Top States by Aadhaar Service Stress Index (ASSI)"
)

plt.ylabel("ASSI (0–100)")
plt.show()


# -------------------------------
# STEP 10.5: UPDATE QUALITY & SYSTEM FRICTION ANALYSIS
# -------------------------------

# Friction ratio: updates per enrolment
lifecycle["friction_ratio"] = (
    lifecycle["total_updates"] / lifecycle["enrolment_count"]
)

# Normalize friction score (0–100)
lifecycle["friction_score"] = (
    (lifecycle["friction_ratio"] - lifecycle["friction_ratio"].min()) /
    (lifecycle["friction_ratio"].max() - lifecycle["friction_ratio"].min())
) * 100

lifecycle["friction_score"] = lifecycle["friction_score"].round(1)

# Classify friction level
def friction_level(x):
    if x < 30:
        return "Low Friction"
    elif x < 60:
        return "Moderate Friction"
    else:
        return "High Friction"

lifecycle["friction_level"] = lifecycle["friction_score"].apply(friction_level)

print("\nUpdate Quality & System Friction Analysis:")
print(
    lifecycle[[
        "friction_ratio",
        "friction_score",
        "friction_level"
    ]]
    .sort_values("friction_score", ascending=False)
    .head(10)
)

# Optional visualization
lifecycle.sort_values("friction_score", ascending=False).head(10)[
    "friction_score"
].plot(
    kind="bar",
    figsize=(10,5),
    title="Top States by Aadhaar Update Friction Score"
)

plt.ylabel("Friction Score (0–100)")
plt.show()




# -------------------------------
# STEP 10.6: INTERVENTION EFFICIENCY SCORE (IES)
# -------------------------------

# Avoid division by zero
lifecycle["enrolment_capacity_proxy"] = lifecycle["enrolment_count"].replace(0, 1)

# Compute raw IES
lifecycle["ies_raw"] = (
    lifecycle["assi"] / lifecycle["enrolment_capacity_proxy"]
)


# Normalize IES to 0–100 scale
lifecycle["ies_score"] = (
    (lifecycle["ies_raw"] - lifecycle["ies_raw"].min()) /
    (lifecycle["ies_raw"].max() - lifecycle["ies_raw"].min())
) * 100

lifecycle["ies_score"] = lifecycle["ies_score"].round(1)


def intervention_priority(x):
    if x >= 70:
        return "🔥 High ROI Intervention Zone"
    elif x >= 40:
        return "⚠️ Medium ROI Zone"
    else:
        return "Low ROI Zone"

lifecycle["intervention_priority"] = lifecycle["ies_score"].apply(intervention_priority)


print("\nTop Intervention Efficiency Regions:")
print(
    lifecycle[
        ["assi", "enrolment_count", "ies_score", "intervention_priority"]
    ]
    .sort_values("ies_score", ascending=False)
    .head(10)
)
print("DEBUG — Columns before export:")
print(lifecycle.columns.tolist())

lifecycle.to_csv("aadhaar_bottleneck_prediction.csv")

# -------------------------------
# STEP 11
# -------------------------------




# lifecycle.to_csv("aadhaar_bottleneck_prediction.csv")
print("\nFinal bottleneck prediction data exported.")





# -------------------------------
# STEP 12: QUERY A PARTICULAR STATE
# -------------------------------

state_name = "andhra pradesh"   # change this state name

if state_name in lifecycle.index:
    print(f"\nDetails for {state_name.title()}:")
    print(lifecycle.loc[state_name])
else:
    print(f"\nState '{state_name}' not found")





def load_csvs_from_folder(folder_path):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    df_list = []
    for file in csv_files:
        print("Reading:", file)   # optional but useful
        df = pd.read_csv(file, encoding="latin1")
        df_list.append(df)
    
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df





# -------------------------------
# STEP 13: SCATTER PLOT ANALYSIS
# -------------------------------

import matplotlib.pyplot as plt

# Color mapping for risk levels
color_map = {
    "Low Risk": "green",
    "Medium Risk": "orange",
    "High Bottleneck Risk": "red"
}

colors = lifecycle["bottleneck_risk"].map(color_map)

plt.figure(figsize=(10,6))
plt.scatter(
    lifecycle["enrolment_count"],
    lifecycle["update_pressure"],
    c=colors,
    alpha=0.7
)

plt.xlabel("Enrolment Count")
plt.ylabel("Update Pressure Index")
plt.title("Enrolment vs Update Pressure (Bottleneck Detection)")

# Add legend manually
for label, color in color_map.items():
    plt.scatter([], [], c=color, label=label)

plt.legend(title="Bottleneck Risk")
plt.grid(True)


top_states = lifecycle.sort_values("update_pressure", ascending=False).head(5)

for state in top_states.index:
    plt.annotate(
        state.title(),
        (lifecycle.loc[state, "enrolment_count"],
         lifecycle.loc[state, "update_pressure"]),
        textcoords="offset points",
        xytext=(5,5),
        fontsize=9
    )

plt.show()







# -------------------------------
# STEP 13: UPDATE COMPOSITION ANALYSIS
# -------------------------------

# Share of update types
lifecycle["biometric_share"] = (
    lifecycle["biometric_updates"] / lifecycle["total_updates"]
)

lifecycle["demographic_share"] = (
    lifecycle["demographic_updates"] / lifecycle["total_updates"]
)

print("\nUpdate Composition (Shares):")
print(
    lifecycle[[
        "biometric_share",
        "demographic_share"
    ]].head()
)








# -------------------------------
# STEP 14: PIE CHART – UPDATE COMPOSITION
# -------------------------------

total_biometric = lifecycle["biometric_updates"].sum()
total_demographic = lifecycle["demographic_updates"].sum()

plt.figure(figsize=(6,6))
plt.pie(
    [total_biometric, total_demographic],
    labels=["Biometric Updates", "Demographic Updates"],
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Overall Aadhaar Update Composition")
plt.show()






# -------------------------------
# STEP 15: INDIA MAP VISUALIZATION
# -------------------------------

import geopandas as gpd
import matplotlib.pyplot as plt

print("Loading India map...")

# Load GeoJSON
india_map = gpd.read_file("INDIA_STATES.geojson")

print("India map loaded")
print("Columns in GeoJSON:")
print(india_map.columns)

# 🔑 Automatically detect state-name column
state_col = [c for c in india_map.columns if c.lower() != "geometry"][0]
print("Using state column:", state_col)

# Standardize state names
india_map["state"] = india_map[state_col].str.strip().str.lower()

# Prepare lifecycle data
lifecycle_map = lifecycle.reset_index()
lifecycle_map["state"] = lifecycle_map["state"].str.lower()

# Fix common name mismatches
state_fix = {
    "nct of delhi": "delhi",
    "andaman & nicobar islands": "andaman and nicobar islands",
    "dadra and nagar haveli and daman and diu": "dadra and nagar haveli and daman and diu"
}
india_map["state"] = india_map["state"].replace(state_fix)

# Merge map with Aadhaar data
merged_map = india_map.merge(
    lifecycle_map,
    on="state",
    how="left"
)

print("Merge completed")

# Plot map
fig, ax = plt.subplots(1, 1, figsize=(10,12))
merged_map.plot(
    column="update_pressure",
    cmap="Reds",
    linewidth=0.8,
    ax=ax,
    edgecolor="black",
    legend=True
)

ax.set_title(
    "India Map: Aadhaar Enrollment Bottleneck Risk",
    fontsize=14
)
ax.axis("off")
plt.show()







