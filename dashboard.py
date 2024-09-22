import pandas as pd
import streamlit as st
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(layout="wide", page_title="Sales Dashboard")


# Function to fetch data from nested folders with error handling
def fetch_data_from_nested_folders(main_folder_path):
    all_data = []
    try:
        for person_folder in os.listdir(main_folder_path):
            person_folder_path = os.path.join(main_folder_path, person_folder)
            if os.path.isdir(person_folder_path):
                for filename in os.listdir(person_folder_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(person_folder_path, filename)
                        try:
                            with open(file_path, "r") as file:
                                data = json.load(file)
                                data["Person"] = person_folder
                                data["Filename"] = (
                                    filename  # Add filename for reference
                                )
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

# Custom CSS for black and white shadcn-inspired UI
st.markdown(
    """
<style>
    /* Add your CSS styles here */
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

# Sidebar
st.sidebar.title("Dashboard Navigation")
section = st.sidebar.radio("Go to:", ["Overview", "People"])


# Helper function to safely calculate mean
def safe_mean(series):
    return series.mean() if not series.empty else "N/A"


# Overview section
if section == "Overview":
    st.title("Sales Dashboard Overview")

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        bant_mean = safe_mean(df["BANT Score_numeric"])
        bant_mean_display = (
            f"{bant_mean:.2f}" if isinstance(bant_mean, float) else bant_mean
        )
        st.markdown(
            f'<div class="card"><p class="card-title">Avg BANT Score</p><p class="metric">{bant_mean_display}</p></div>',
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
            f'<div class="card"><p class="card-title">Avg Call Intent Score</p><p class="metric">{call_intent_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    with col3:
        spin_mean = safe_mean(df["SPIN Score_numeric"])
        spin_mean_display = (
            f"{spin_mean:.2f}" if isinstance(spin_mean, float) else spin_mean
        )
        st.markdown(
            f'<div class="card"><p class="card-title">Avg SPIN Score</p><p class="metric">{spin_mean_display}</p></div>',
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
            f'<div class="card"><p class="card-title">Avg Sentiment Score</p><p class="metric">{sentiment_mean_display}</p></div>',
            unsafe_allow_html=True,
        )

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
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

    # Pie Chart for score proportions
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
            colors["primary"],
            colors["secondary"],
            colors["tertiary"],
            colors["quaternary"],
        ],
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# People section
elif section == "People":
    st.title("Person-Specific Data")

    # Dropdown to select a specific person
    people_options = df["Person"].unique()
    selected_person = st.selectbox("Select a person:", people_options)

    # Filter the data for the selected person
    person_data = df[df["Person"] == selected_person]

    st.subheader(f"Data for {selected_person}")

    # Display the selected person's data in a card format
    for _, row in person_data.iterrows():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            f"""
        <p><strong>Filename:</strong> {row['Filename']}</p>
        <p><strong>BANT Score:</strong> {row['BANT Score']}</p>
        <p><strong>Call Intent Score:</strong> {row['Call Intent Score']}</p>
        <p><strong>Course Interested:</strong> {row['Course Interested']}</p>
        <p><strong>Detailed Call Score:</strong> {row['Detailed Call Score']}</p>
        <p><strong>Feedback for improvement:</strong> {row['Feedback for improvement']}</p>
        <p><strong>Follow Up:</strong> {row['Follow Up']}</p>
        <p><strong>Lead City:</strong> {row['Lead City']}</p>
        <p><strong>Sentiment Analysis Score:</strong> {row['Sentiment Analysis Score']}</p>
        <p><strong>Date:</strong> {row['Date'].strftime('%d-%m-%Y')}</p>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Person-specific charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig_scores = go.Figure()
        fig_scores.add_trace(
            go.Bar(
                x=["BANT", "Call Intent", "SPIN", "Sentiment"],
                y=[
                    row["BANT Score"],
                    row["Call Intent Score"],
                    row["SPIN Score"],
                    row["Sentiment Analysis Score"],
                ],
                marker_color=[
                    colors["primary"],
                    colors["secondary"],
                    colors["tertiary"],
                    colors["quaternary"],
                ],
            )
        )
        fig_scores.update_layout(
            title="Score Comparison",
            yaxis_title="Score",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig_timeline = px.scatter(
            person_data,
            x="Date",
            y="Sentiment Analysis Score",
            title="Sentiment Analysis Over Time",
            color_discrete_sequence=[colors["primary"]],
        )
        fig_timeline.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.sidebar.markdown(
    '<div class="card"><strong>Designed with a black and white shadcn-inspired UI elements</strong></div>',
    unsafe_allow_html=True,
)
