import pandas as pd
import streamlit as st
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="Sales Dashboard")

# Custom CSS for Shadcn-inspired UI
st.markdown(
    """
<style>
    /* Add your CSS styles here to match Shadcn's design */
    .shadcn-card {
        border-radius: 0.5rem;
        box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f5f5f5;
        border: 1px solid #d4d4d4;
        
    }
     .shadcn-card:hover {
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
        duration: 0.3s;
    }

    .shadcn-card-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .shadcn-card-content {
        font-wight: bold;
        font-size: 2.2rem;
        margin-top: 0.2rem;
    }
    
    .line-v{
        height: 2px;
        background-color: #d4d4d4;
        border-radius: 0.5rem;
    }
    
    .line-h{
        height: full;
        width: 10px;
        background-color: #000;
        border-radius: 0.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Color palette
colors = {
    "primary": "#3498db",  # Blue
    "secondary": "#2ecc71",  # Green
    "tertiary": "#e74c3c",  # Red
    "quaternary": "#f39c12",  # Orange
    "background": "#ffffff",
    "text": "#000000",
}


# Function to fetch data from nested folders with error handling
def fetch_data_from_nested_folders(main_folder_path):
    all_data = []
    try:
        for folder_name in os.listdir(main_folder_path):
            folder_path = os.path.join(main_folder_path, folder_name)
            if os.path.isdir(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            with open(file_path, "r") as file:
                                data = json.load(file)
                                data["Folder"] = folder_name
                                data["Filename"] = filename
                                all_data.append(data)
                        except json.JSONDecodeError:
                            st.warning(f"Could not decode JSON from {file_path}.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    return pd.DataFrame(all_data)


# Specify the main folder path where person folders are stored
main_folder_path = "data"

# Fetch the data with a loading spinner
with st.spinner("Loading data..."):
    df = fetch_data_from_nested_folders(main_folder_path)

# Convert Date to datetime
if not df.empty and "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")

# Create numeric versions of score columns for calculations and charts
score_columns = [
    "BANT Score",
    "Call Intent Score",
    "SPIN Score",
    "Sentiment Analysis Score",
    "Detailed Call Score",
]
for col in score_columns:
    df[f"{col}_numeric"] = pd.to_numeric(df[col], errors="coerce")

# Sidebar
st.sidebar.title("Dashboard Navigation")
section = st.sidebar.radio("Go to:", ["Overview", "People"])


# Helper function to safely calculate mean
def safe_mean(series):
    return series.mean() if not series.empty else "N/A"


# Overview section
if section == "Overview":
    st.title("Sales Dashboard Overview")
    # Total files
    num_files = df["Filename"].nunique()
    st.markdown(f"Data of **{num_files*3}**.")

    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        bant_mean = safe_mean(df["BANT Score_numeric"])
        bant_mean_display = (
            f"{bant_mean:.2f}" if isinstance(bant_mean, float) else bant_mean
        )
        st.markdown(
            f'<div class="shadcn-card"><p class="shadcn-card-title">Avg BANT Score</p><p class="shadcn-card-content">{bant_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    with col2:
        call_intent_mean = safe_mean(df["Call Intent Score_numeric"])
        call_intent_mean_display = (
            f"{call_intent_mean:.2f}"
            if isinstance(call_intent_mean, float)
            else call_intent_mean
        )
        st.markdown(
            f'<div class="shadcn-card"><p class="shadcn-card-title">Avg Call Intent Score</p><p class="shadcn-card-content">{call_intent_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    with col3:
        spin_mean = safe_mean(df["SPIN Score_numeric"])
        spin_mean_display = (
            f"{spin_mean:.2f}" if isinstance(spin_mean, float) else spin_mean
        )
        st.markdown(
            f'<div class="shadcn-card"><p class="shadcn-card-title">Avg SPIN Score</p><p class="shadcn-card-content">{spin_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    with col4:
        sentiment_mean = safe_mean(df["Sentiment Analysis Score_numeric"])
        sentiment_mean_display = (
            f"{sentiment_mean:.2f}"
            if isinstance(sentiment_mean, float)
            else sentiment_mean
        )
        st.markdown(
            f'<div class="shadcn-card"><p class="shadcn-card-title">Avg Sentiment Score</p><p class="shadcn-card-content">{sentiment_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    with col5:
        detailed_call_mean = safe_mean(df["Detailed Call Score_numeric"])
        detailed_call_mean_display = (
            f"{detailed_call_mean:.2f}"
            if isinstance(detailed_call_mean, float)
            else detailed_call_mean
        )
        st.markdown(
            f'<div class="shadcn-card"><p class="shadcn-card-title">Avg Detailed Call Score</p><p class="shadcn-card-content">{detailed_call_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    # Radar Chart for Course Interested and various scores

    # Define categories for the radar chart
    categories = [
        "BANT Score",
        "Call Intent Score",
        "SPIN Score",
        "Sentiment Analysis Score",
        "Detailed Call Score",
    ]

    # Filter the rows where "Course Interested" is not "N/A"
    df_radar = df[df["Course Interested"] != "N/A"]

    if not df_radar.empty:
        radar_fig = go.Figure()

        # Iterate through the filtered DataFrame and add radar chart traces
        for idx, row in df_radar.iterrows():
            radar_fig.add_trace(
                go.Scatterpolar(
                    r=[
                        row["BANT Score_numeric"],
                        row["Call Intent Score_numeric"],
                        row["SPIN Score_numeric"],
                        row["Sentiment Analysis Score_numeric"],
                        row["Detailed Call Score_numeric"],
                    ],
                    theta=categories,
                    fill="toself",
                    name=row["Course Interested"],
                )
            )

        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 10]
                )  # Adjust the range according to your score scale
            ),
            showlegend=True,
            title="Radar Chart: Course Interested vs Scores",
        )

        st.plotly_chart(radar_fig, use_container_width=True)
    else:
        st.info("No data available for 'Course Interested' field.")

    st.markdown('<div class="line-v"> </div>', unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)  # Use 4 columns for more charts

    with col1:
        fig_bant = px.histogram(
            df,
            x="BANT Score",
            title="BANT Score Distribution",
            color_discrete_sequence=[colors["primary"]],
        )
        fig_bant.update_layout(bargap=0.2, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_bant, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        fig_intent = px.histogram(
            df,
            x="Call Intent Score",
            title="Call Intent Score Distribution",
            color_discrete_sequence=[colors["secondary"]],
        )
        fig_intent.update_layout(
            bargap=0.2, plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig_intent, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="line-v">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)  # Use 4 columns for more charts

    with col1:
        fig_spin = px.histogram(
            df,
            x="SPIN Score",
            title="SPIN Score Distribution",
            color_discrete_sequence=[colors["tertiary"]],
        )
        fig_spin.update_layout(bargap=0.2, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_spin, use_container_width=True)

    with col2:
        fig_sentiment = px.histogram(
            df,
            x="Sentiment Analysis Score",
            title="Sentiment Analysis Score Distribution",
            color_discrete_sequence=[colors["quaternary"]],
        )
        fig_sentiment.update_layout(
            bargap=0.2, plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)

    col1, col2 = st.columns(2)  # Use 4 columns for more charts
    with col1:
        # Pie Chart for score proportions
        st.markdown('<div class="line-v"> </div>', unsafe_allow_html=True)
        pie_data = df[
            [
                "BANT Score_numeric",
                "Call Intent Score_numeric",
                "SPIN Score_numeric",
                "Sentiment Analysis Score_numeric",
            ]
        ].mean()
        fig_pie = px.pie(
            pie_data,
            values=pie_data.values,
            names=pie_data.index,
            title="Average Score Distribution",
            color_discrete_sequence=[
                colors["secondary"],
                colors["tertiary"],
                colors["primary"],
                colors["quaternary"],
            ],
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Bar Graph for Lead City (including "N/A")
        st.markdown('<div class="line-v"> </div>', unsafe_allow_html=True)
        st.subheader("Lead City Distribution")

        # Group by Lead City, including "N/A"
        city_counts = df["Lead City"].value_counts(dropna=False).reset_index()
        city_counts.columns = ["Lead City", "Count"]

        # Create bar chart for Lead City
        fig_lead_city = px.bar(
            city_counts,
            x="Lead City",
            y="Count",
            title="Lead City Distribution",
            text="Count",
            color_discrete_sequence=[colors["primary"]],
        )

        fig_lead_city.update_layout(
            xaxis_title="Lead City",
            yaxis_title="Count",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        st.plotly_chart(fig_lead_city, use_container_width=True)


# People section
elif section == "People":
    st.title("Person-Specific Data")

    # Dropdown to select a specific folder
    folder_options = df["Folder"].unique()
    selected_folder = st.selectbox("Select a folder:", folder_options)

    # Filter the data for the selected folder
    folder_data = df[df["Folder"] == selected_folder]

    st.subheader(f"Data for {selected_folder}")

    # Display folder-specific data in a table format
    st.dataframe(folder_data)

    # Person-specific charts (you can customize these based on your needs)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="line-v">', unsafe_allow_html=True)
        # Example: Average scores for the selected folder
        # Convert non-numeric values to NaN and calculate the mean
        numeric_scores = folder_data[score_columns].apply(
            pd.to_numeric, errors="coerce"
        )
        average_scores = numeric_scores.mean()
        fig_scores = go.Figure(
            data=[go.Bar(x=average_scores.index, y=average_scores.values)]
        )
        fig_scores.update_layout(title="Average Scores")
        st.plotly_chart(fig_scores, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="line-v">', unsafe_allow_html=True)
        # Example: Sentiment Analysis over time for the folder
        fig_sentiment = px.line(
            folder_data,
            x="Date",
            y="Sentiment Analysis Score",
            title="Sentiment Analysis Over Time",
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
