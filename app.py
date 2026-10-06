import streamlit as st
import pandas as pd

st.title("Oil & Gas Production Analytics")

st.write(
    "A production analytics dashboard for monitoring oil, gas, water, "
    "water cut, GOR, and well performance."
)


st.sidebar.title("Dashboard")

st.sidebar.write("Oil & Gas Production Monitoring")

st.sidebar.write(
    "Use the dashboard to analyze well production performance."
)


uploaded_file = st.sidebar.file_uploader(
    "Upload Production CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("production_data.csv")

required_columns = ["Well", "Oil", "Gas", "Water"]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required columns: {', '.join(missing_columns)}"
    )
    st.stop()


numeric_columns = ["Oil", "Gas", "Water"]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

if df[numeric_columns].isnull().any().any():
    st.error(
        "Oil, Gas, and Water columns must contain only numeric values."
    )
    st.stop()


df["Total_Liquid"] = df["Oil"] + df["Water"]

df["Water_Cut_%"] = (
    df["Water"] /
    df["Total_Liquid"].replace(0, pd.NA)
) * 100

df["GOR"] = df["Gas"] / df["Oil"].replace(0, pd.NA)

def performance_status(row):

    if pd.isna(row["Water_Cut_%"]):
        return "No Production"

    if row["Oil"] >= 1200 and row["Water_Cut_%"] < 22:
        return "Good"

    elif row["Water_Cut_%"] > 23:
        return "Needs Attention"

    else:
        return "Moderate"


df["Performance_Status"] = df.apply(
    performance_status,
    axis=1
)

# Sidebar metrics
st.sidebar.write("Key metrics:")
st.sidebar.write("• Oil Production")
st.sidebar.write("• Water Cut")
st.sidebar.write("• GOR")
st.sidebar.write("• Well Performance")

# Well Filter
st.sidebar.header("Well Filter")

well_options = ["All Wells"] + list(df["Well"])

selected_well = st.sidebar.selectbox(
    "Select a Well",
    well_options
)


if selected_well == "All Wells":
    display_data = df
else:
    display_data = df[
        df["Well"] == selected_well
    ]


total_oil = display_data["Oil"].sum()

total_water = display_data["Water"].sum()

total_liquid = display_data["Total_Liquid"].sum()

field_water_cut = (
    total_water / total_liquid
) * 100

# Divider
st.divider()

# Production Overview
st.header(f"Production Overview - {selected_well}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Oil", f"{total_oil:,.0f} bbl")
col2.metric("Total Water", f"{total_water:,.0f} bbl")
col3.metric("Total Liquid", f"{total_liquid:,.0f} bbl")
col4.metric("Field Water Cut", f"{field_water_cut:.2f}%")

# Well Production Data
st.header("Well Production Data")
st.write(
    "Production data and calculated performance parameters for all wells."
)
st.dataframe(df)

st.header("Production Analysis")
st.header(f"Oil Production - {selected_well}")

st.bar_chart(
    display_data.set_index("Well")["Oil"]
)

# Water Cut
st.header(f"Water Cut - {selected_well}")

st.bar_chart(
    display_data.set_index("Well")["Water_Cut_%"]
)

# GOR
st.header(f"Gas-Oil Ratio (GOR) - {selected_well}")

st.bar_chart(
    display_data.set_index("Well")["GOR"]
)



st.header("Key Production Insights")

if selected_well == "All Wells":

    highest_oil_well = display_data.loc[
        display_data["Oil"].idxmax(),
        "Well"
    ]

    if display_data["Water_Cut_%"].notna().any():
        highest_water_cut_well = display_data.loc[
            display_data["Water_Cut_%"].idxmax(),
            "Well"
        ]
    else:
        highest_water_cut_well = "No production data"

    if display_data["GOR"].notna().any():
        highest_gor_well = display_data.loc[
        display_data["GOR"].idxmax(),
        "Well"
        ]
    else:
        highest_gor_well = "No production data"

    st.write(
        f"• {highest_oil_well} has the highest oil production."
    )

    st.write(
        f"• {highest_water_cut_well} has the highest water cut."
    )

    st.write(
        f"• {highest_gor_well} has the highest GOR."
    )

else:

    selected_row = display_data.iloc[0]

    st.write(
        f"• {selected_well} oil production: "
        f"{selected_row['Oil']:,.0f} bbl."
    )

    if pd.isna(selected_row["Water_Cut_%"]):
        st.write(
            "• Water cut: No production data."
        )
    else:
        st.write(
            f"• Water cut: "
            f"{selected_row['Water_Cut_%']:.2f}%."
        )

    st.write(
        f"• GOR: {selected_row['GOR']:.2f}."
    )

    st.write(
        f"• Performance: "
        f"{selected_row['Performance_Status']}."
    )

# Well Production Ranking
# ==============================

st.header("Well Production Ranking")

ranking_data = display_data[
    ["Well", "Oil", "Water_Cut_%", "GOR", "Performance_Status"]
].sort_values(
    by="Oil",
    ascending=False
)

ranking_data = ranking_data.reset_index(drop=True)

ranking_data.index = ranking_data.index + 1

st.dataframe(ranking_data)

# Well Screening
# ==============================

st.header("Well Screening")

screening_data = display_data[
    [
        "Well",
        "Oil",
        "Water_Cut_%",
        "GOR",
        "Performance_Status"
    ]
].copy()

screening_data["Screening_Status"] = screening_data[
    "Performance_Status"
].replace(
    {
        "Good": "Normal",
        "Moderate": "Monitor",
        "Needs Attention": "Investigate"
    }
)

st.dataframe(screening_data)

# Overall Field Status
# ==============================

if selected_well == "All Wells":

    st.header("Overall Field Status")

    attention_count = len(
        display_data[
            display_data["Performance_Status"] == "Needs Attention"
        ]
    )

    total_wells = len(display_data)

    if attention_count == 0:
        field_status = "Good"
    elif attention_count <= total_wells * 0.2:
        field_status = "Attention Required"
    else:
        field_status = "Needs Review"

    st.metric(
        "Field Status",
        field_status
    )

    st.write(
        f"{attention_count} out of {total_wells} wells "
        "require further investigation."
    )
    
if selected_well == "All Wells":

    st.header("Field-Level Summary")

    average_oil = display_data["Oil"].mean()

    number_of_attention_wells = len(
        display_data[
            display_data["Performance_Status"] == "Needs Attention"
        ]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Oil / Well",
        f"{average_oil:,.0f} bbl"
    )

    col2.metric(
        "Wells Needing Attention",
        number_of_attention_wells
    )

    col3.metric(
        "Overall Water Cut",
        f"{field_water_cut:.2f}%"
    )

st.header("Executive Summary")

if selected_well == "All Wells":

    highest_oil_well = display_data.loc[
        display_data["Oil"].idxmax(),
        "Well"
    ]

    if display_data["Water_Cut_%"].notna().any():
        highest_water_cut_well = display_data.loc[
            display_data["Water_Cut_%"].idxmax(),
            "Well"
        ]
        water_cut_summary = (
            f"{highest_water_cut_well} has the highest water cut."
        )
    else:
        water_cut_summary = (
            "Water cut: No production data available."
        )

    attention_count = len(
        display_data[
            display_data["Performance_Status"] == "Needs Attention"
        ]
    )

    if field_water_cut > 0:
        field_water_cut_summary = (
            f"Overall field water cut is {field_water_cut:.2f}%."
        )
    else:
        field_water_cut_summary = (
            "Overall field water cut: No production data available."
        )

    st.write(
        f"• {highest_oil_well} has the highest oil production."
    )

    st.write(
        f"• {water_cut_summary}"
    )

    st.write(
        f"• {attention_count} well(s) require further investigation."
    )

    st.write(
        f"• {field_water_cut_summary}"
    )
# ==============================
# Download Analyzed Data
# ==============================

st.header("Download Analyzed Data")

csv_data = display_data.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="analyzed_production_data.csv",
    mime="text/csv"
)
# Production Trend Analysis

st.header("Production Trend Analysis")

history_data = pd.read_csv("production_history.csv")

if selected_well == "All Wells":
    trend_data = history_data
else:
    trend_data = history_data[
        history_data["Well"] == selected_well
    ]
if len(trend_data) == 0:
    st.warning(
        f"No historical production data is available for {selected_well}."
    )
    st.stop()

st.write(
    "Monthly oil production trend for monitoring changes in well performance."
)

st.line_chart(
    trend_data,
    x="Month",
    y="Oil",
    color="Well"
)
st.write("Monthly water production trend.")

st.line_chart(
    trend_data,
    x="Month",
    y="Water",
    color="Well"
)
trend_data = trend_data.copy()

trend_data["Total_Liquid"] = (
    trend_data["Oil"] + trend_data["Water"]
)

trend_data["Water_Cut_%"] = (
    trend_data["Water"] /
    trend_data["Total_Liquid"]
) * 100

st.write("Monthly water cut trend.")

st.line_chart(
    trend_data,
    x="Month",
    y="Water_Cut_%",
    color="Well"
)

trend_data["GOR"] = (
    trend_data["Gas"] /
    trend_data["Oil"].replace(0, pd.NA)
)

st.write("Monthly gas-oil ratio (GOR) trend.")

st.line_chart(
    trend_data,
    x="Month",
    y="GOR",
    color="Well"
)

first_oil = trend_data["Oil"].iloc[0]
last_oil = trend_data["Oil"].iloc[-1]

if first_oil != 0:
    oil_change_percent = (
        (last_oil - first_oil) / first_oil
    ) * 100
else:
    oil_change_percent = 0

st.write("Oil Production Change")

st.metric(
    "Production Change",
    f"{abs(oil_change_percent):.2f}%",
    delta=f"{oil_change_percent:+.2f}%"
)
if oil_change_percent > 5:
    trend_status = "Increasing"
elif oil_change_percent < -5:
    trend_status = "Declining"
else:
    trend_status = "Stable"

st.metric(
    "Trend Status",
    trend_status
)
if trend_status == "Increasing":
    st.success(
        "Oil production is showing an increasing trend."
    )
elif trend_status == "Declining":
    st.warning(
        "Oil production is showing a declining trend and requires monitoring."
    )
else:
    st.info(
        "Oil production is relatively stable."
    )

st.write("### Well Trend Summary")

trend_summary = []

for well in history_data["Well"].unique():

    well_data = history_data[
        history_data["Well"] == well
    ]

    first_oil = well_data["Oil"].iloc[0]
    last_oil = well_data["Oil"].iloc[-1]

    if first_oil != 0:
        change_percent = (
            (last_oil - first_oil) / first_oil
        ) * 100
    else:
        change_percent = 0

    if change_percent > 5:
        status = "Increasing"
    elif change_percent < -5:
        status = "Declining"
    else:
        status = "Stable"

    trend_summary.append(
        {
            "Well": well,
            "Oil Change %": round(change_percent, 2),
            "Trend Status": status
        }
    )

trend_summary_df = pd.DataFrame(trend_summary)

st.dataframe(trend_summary_df)

st.write("### Trend-Based Screening")

screening_results = []

for _, row in trend_summary_df.iterrows():

    well = row["Well"]
    trend = row["Trend Status"]

    current_data = df[
        df["Well"] == well
    ]

    if len(current_data) > 0:
        performance = current_data[
            "Performance_Status"
        ].iloc[0]

        if performance == "Needs Attention" and trend == "Declining":
            screening_status = "Priority Investigation"

        elif performance == "Good" and trend == "Increasing":
            screening_status = "Strong"

        elif performance == "Moderate" or trend == "Stable":
            screening_status = "Monitor"

        else:
            screening_status = "Review"

        screening_results.append(
            {
                "Well": well,
                "Current Performance": performance,
                "Oil Trend": trend,
                "Screening Status": screening_status
            }
        )

trend_screening_df = pd.DataFrame(screening_results)

st.dataframe(trend_screening_df)

st.write("### Analyst Recommendation")

for _, row in trend_screening_df.iterrows():

    if row["Screening Status"] == "Priority Investigation":
        st.warning(
            f"{row['Well']}: Production is declining and current performance "
            "requires attention. Further investigation is recommended."
        )

    elif row["Screening Status"] == "Strong":
        st.success(
            f"{row['Well']}: Production trend and current performance "
            "are positive."
        )

    elif row["Screening Status"] == "Monitor":
        st.info(
            f"{row['Well']}: Performance is acceptable but should "
            "continue to be monitored."
        )

    else:
        st.warning(
            f"{row['Well']}: Further review of production performance "
            "is recommended."
        )
# Well Performance Status
st.header("Well Performance Status")
st.write(
    "Well performance is classified using oil production and water cut "
    "to identify wells performing well, moderately, or requiring attention."
)

st.dataframe(
    display_data[
        [
            "Well",
            "Oil",
            "Water_Cut_%",
            "GOR",
            "Performance_Status"
        ]
    ]
)

# Selected Well Details
st.write("### Selected Well Details")

st.dataframe(
    display_data[
        [
            "Well",
            "Oil",
            "Gas",
            "Water",
            "Total_Liquid",
            "Water_Cut_%",
            "GOR",
            "Performance_Status"
        ]
    ]
)

# Wells Needing Attention
st.header("Wells Needing Attention")
st.write(
    "Wells with high water cut or lower production performance "
    "are flagged for further monitoring and investigation."
)
attention_wells = display_data[
    display_data["Performance_Status"] == "Needs Attention"
]

if len(attention_wells) > 0:
    for _, row in attention_wells.iterrows():
        st.warning(
            f"{row['Well']} — Water Cut: {row['Water_Cut_%']:.2f}%"
        )
else:
    st.success("No wells currently need attention.")