import os
import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
import plotly.graph_objects as go
from openai import OpenAI
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Gluco Guide - AI Diabetes Assistant",
    page_icon="🩸",
    layout="wide"
)
st.markdown("""
<style>
    /* Color Palette */
    :root {
        --primary: #4f46e5;       /* Rich indigo - main app color */
        --primary-light: #ede9fe; /* Light indigo background */
        --secondary: #10b981;     /* Emerald green for success states */
        --secondary-light: #d1fae5; /* Light green background */
        --warning: #f59e0b;       /* Amber for warnings/alerts */
        --warning-light: #fef3c7; /* Light amber background */
        --neutral-dark: #1f2937;  /* Dark gray for text */
        --neutral-medium: #6b7280; /* Medium gray for secondary text */
        --neutral-light: #f9fafb; /* Light gray for backgrounds */
        --white: #ffffff;         /* White */
        --shadow: rgba(0, 0, 0, 0.08); /* Shadow color */
    }

    /* Typography */
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--neutral-dark);
        line-height: 1.6;
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-light);
    }

    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Card Components */
    .metric-card {
        background-color: var(--white);
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px var(--shadow);
        transition: transform 0.2s ease;
        text-align: center;
        border-top: 4px solid var(--primary);
    }

    .metric-card:hover {
        transform: translateY(-2px);
    }

    .metric-card h3 {
        color: var(--neutral-medium);
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .metric-card h2 {
        color: var(--primary);
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    /* Information Boxes */
    .info-box {
        background-color: var(--primary-light);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 5px solid var(--primary);
        margin-bottom: 1.25rem;
        font-size: 0.95rem;
    }

    .disclaimer {
        background-color: var(--warning-light);
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid var(--warning);
        font-size: 0.9rem;
        margin-top: 2rem;
    }

    .recommendation-box {
        background-color: var(--secondary-light);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid var(--secondary);
        margin-top: 1.25rem;
        box-shadow: 0 2px 8px var(--shadow);
    }

    /* Sidebar Styling */
    .sidebar-content {
        padding: 1.5rem 1rem;
        background-color: var(--primary-light);
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .sidebar-content h3 {
        color: var(--primary);
        border-bottom: 1px solid var(--primary);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Button Styling */
    .stButton>button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: var(--primary);
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px var(--shadow);
    }

    /* Form Controls */
    input, select, textarea {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }

    input:focus, select:focus, textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px var(--primary-light) !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        background-color: var(--neutral-light);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary);
        color: white;
    }

    /* Table Styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }

    .stDataFrame [data-testid="stTable"] {
        border-collapse: separate;
        border-spacing: 0;
    }

    .stDataFrame th {
        background-color: var(--primary-light);
        color: var(--primary);
        padding: 12px 8px;
        font-weight: 600;
    }

    .stDataFrame td {
        padding: 8px;
        border-top: 1px solid #e2e8f0;
    }

    /* Chart Container */
    [data-testid="stPlotlyChart"] > div {
        border-radius: 12px;
        background-color: white;
        box-shadow: 0 2px 8px var(--shadow);
        padding: 1rem;
    }

    /* Reading Log Items */
    .log-item {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 4px var(--shadow);
        border-left: 4px solid var(--primary);
        transition: transform 0.2s ease;
    }

    .log-item:hover {
        transform: translateX(2px);
    }

    .log-high {
        border-left-color: #ef4444;
    }

    .log-normal {
        border-left-color: var(--secondary);
    }

    .log-low {
        border-left-color: var(--warning);
    }

    /* Glucose value styling */
    .glucose-value {
        font-size: 1.3rem;
        font-weight: 700;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
    }

    .glucose-high {
        color: #ef4444;
        background-color: #fee2e2;
    }

    .glucose-normal {
        color: var(--secondary);
        background-color: var(--secondary-light);
    }

    .glucose-low {
        color: var(--warning);
        background-color: var(--warning-light);
    }
</style>
""", unsafe_allow_html=True)
# Initialize session state for storing history
if 'glucose_history' not in st.session_state:
    st.session_state.glucose_history = pd.DataFrame(columns=['Date', 'Time', 'Reading', 'Period'])

if 'recommendations_history' not in st.session_state:
    st.session_state.recommendations_history = []

load_dotenv()
# Initialize Nebius API client
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://api.studio.nebius.com/v1/",
        api_key=os.environ.get("NEBIUS_API_KEY")
    )


client = get_client()

# Sidebar for navigation and user profile
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.image("Red Circle Health Logo.png", width=300)
    st.markdown("### User Profile")

    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
        st.session_state.diabetes_type = ""
        st.session_state.target_range = [80, 130]

    user_name = st.text_input("Name", value=st.session_state.user_name)
    diabetes_type = st.selectbox("Diabetes Type",
                                 ["Type 1", "Type 2", "Gestational", "Pre-diabetes"],
                                 index=1 if st.session_state.diabetes_type == "Type 2" else 0)

    st.markdown("### Target Glucose Range (mg/dL)")
    target_min, target_max = st.slider("", 70, 200, st.session_state.target_range, 5)

    if user_name:
        st.session_state.user_name = user_name
    if diabetes_type:
        st.session_state.diabetes_type = diabetes_type
    st.session_state.target_range = [target_min, target_max]

    st.markdown("### Navigation")
    app_mode = st.radio("", ["Dashboard", "Log Glucose", "Meal Planner", "History"])
    st.markdown("</div>", unsafe_allow_html=True)

# Main app
st.markdown("<h1 class='main-header'>Gluco Guide - AI-Powered Diabetes Assistant</h1>", unsafe_allow_html=True)

# Display different sections based on navigation
if app_mode == "Dashboard":
    # Dashboard layout with columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### Last Reading")
        if not st.session_state.glucose_history.empty:
            last_reading = st.session_state.glucose_history.iloc[-1]
            st.markdown(f"<h2>{last_reading['Reading']} mg/dL</h2>", unsafe_allow_html=True)
            st.markdown(f"{last_reading['Period']} - {last_reading['Time']}")
        else:
            st.markdown("<h2>--</h2>", unsafe_allow_html=True)
            st.markdown("No readings yet")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 7-Day Average")
        if not st.session_state.glucose_history.empty:
            avg = st.session_state.glucose_history['Reading'].mean()
            st.markdown(f"<h2>{avg:.1f} mg/dL</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2>--</h2>", unsafe_allow_html=True)
            st.markdown("No data available")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### Target Range")
        in_range = 0
        total = len(st.session_state.glucose_history)
        if total > 0:
            in_range = len(st.session_state.glucose_history[
                               (st.session_state.glucose_history['Reading'] >= st.session_state.target_range[0]) &
                               (st.session_state.glucose_history['Reading'] <= st.session_state.target_range[1])
                               ])
            percentage = (in_range / total) * 100
            st.markdown(f"<h2>{percentage:.1f}%</h2>", unsafe_allow_html=True)
            st.markdown(f"{in_range} of {total} readings in range")
        else:
            st.markdown("<h2>--</h2>", unsafe_allow_html=True)
            st.markdown("No data available")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h2 class='sub-header'>Glucose Trends</h2>", unsafe_allow_html=True)

    if not st.session_state.glucose_history.empty:
        # Create a Plotly figure
        fig = go.Figure()

        # Add the glucose readings
        fig.add_trace(go.Scatter(
            x=st.session_state.glucose_history['Date'] + ' ' + st.session_state.glucose_history['Time'],
            y=st.session_state.glucose_history['Reading'],
            mode='lines+markers',
            name='Glucose',
            marker=dict(size=8, color='#3366cc'),
            line=dict(width=2, color='#3366cc')
        ))

        # Add target range as a shaded area
        fig.add_trace(go.Scatter(
            x=st.session_state.glucose_history['Date'] + ' ' + st.session_state.glucose_history['Time'],
            y=[st.session_state.target_range[1]] * len(st.session_state.glucose_history),
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=st.session_state.glucose_history['Date'] + ' ' + st.session_state.glucose_history['Time'],
            y=[st.session_state.target_range[0]] * len(st.session_state.glucose_history),
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(76, 175, 80, 0.2)',
            name='Target Range'
        ))

        # Layout configuration
        fig.update_layout(
            title='Glucose Readings Over Time',
            xaxis_title='Date and Time',
            yaxis_title='Glucose Level (mg/dL)',
            height=400,
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            "<div class='info-box'>No glucose data available yet. Start logging your readings to see trends.</div>",
            unsafe_allow_html=True)

    # Recent recommendations
    st.markdown("<h2 class='sub-header'>Recent AI Recommendations</h2>", unsafe_allow_html=True)
    if st.session_state.recommendations_history:
        st.markdown("<div class='recommendation-box'>", unsafe_allow_html=True)
        st.write(st.session_state.recommendations_history[-1])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='info-box'>No recommendations yet. Use the Meal Planner to get personalized advice.</div>",
            unsafe_allow_html=True)

elif app_mode == "Log Glucose":
    st.markdown("<h2 class='sub-header'>Log Your Glucose Readings</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='info-box'>Regular logging helps identify patterns and improve management.</div>",
                    unsafe_allow_html=True)
        today = datetime.now().strftime("%Y-%m-%d")
        date = st.date_input("Date", datetime.now())
        time_period = st.selectbox("Time Period",
                                   ["Morning (Before Breakfast)",
                                    "Morning (After Breakfast)",
                                    "Afternoon (Before Lunch)",
                                    "Afternoon (After Lunch)",
                                    "Evening (Before Dinner)",
                                    "Evening (After Dinner)",
                                    "Bedtime",
                                    "Other"])

        current_time = datetime.now().strftime("%H:%M")
        time = st.time_input("Time", datetime.now())
        reading = st.number_input("Glucose Reading (mg/dL)", min_value=40, max_value=500, step=1, value=120)
        notes = st.text_area("Notes (Optional)", placeholder="Exercise, stress, illness, etc.")

        if st.button("Save Reading", type="primary"):
            new_entry = {
                'Date': date.strftime("%Y-%m-%d"),
                'Time': time.strftime("%H:%M"),
                'Reading': reading,
                'Period': time_period,
                'Notes': notes
            }

            st.session_state.glucose_history = pd.concat([
                st.session_state.glucose_history,
                pd.DataFrame([new_entry])
            ], ignore_index=True)

            st.success("Reading saved successfully!")

    with col2:
        st.markdown("<h3 class='sub-header'>Recent Readings</h3>", unsafe_allow_html=True)

        if not st.session_state.glucose_history.empty:
            recent = st.session_state.glucose_history.sort_values(by=['Date', 'Time'], ascending=False).head(5)
            for _, row in recent.iterrows():
                st.markdown(f"""
                <div style="background-color:#f5f5f5; padding:10px; border-radius:5px; margin-bottom:10px;">
                    <strong>{row['Date']} - {row['Period']}</strong><br>
                    <span style="font-size:1.2rem;">{row['Reading']} mg/dL</span> at {row['Time']}
                    {f"<br><em>Notes: {row['Notes']}</em>" if 'Notes' in row and row['Notes'] else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'>No readings logged yet.</div>", unsafe_allow_html=True)

elif app_mode == "Meal Planner":
    st.markdown("<h2 class='sub-header'>AI Meal Planner & Recommendations</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            "<div class='info-box'>Get personalized meal recommendations based on your glucose readings and food preferences.</div>",
            unsafe_allow_html=True)

        # Get most recent readings for each period
        recent_readings = {}
        if not st.session_state.glucose_history.empty:
            for period in ["Morning", "Afternoon", "Evening"]:
                period_data = st.session_state.glucose_history[
                    st.session_state.glucose_history['Period'].str.contains(period)]
                if not period_data.empty:
                    latest = period_data.sort_values(by=['Date', 'Time'], ascending=False).iloc[0]
                    recent_readings[period] = latest['Reading']

        # Display recent readings or input fields
        morning_glucose = st.number_input("Morning Glucose (mg/dL)",
                                          min_value=40, max_value=500,
                                          value=recent_readings.get("Morning", 120))

        afternoon_glucose = st.number_input("Afternoon Glucose (mg/dL)",
                                            min_value=40, max_value=500,
                                            value=recent_readings.get("Afternoon", 120))

        evening_glucose = st.number_input("Evening Glucose (mg/dL)",
                                          min_value=40, max_value=500,
                                          value=recent_readings.get("Evening", 120))

        st.markdown("### Food Preferences")
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        dietary_restrictions = st.multiselect("Dietary Restrictions",
                                              ["None", "Vegetarian", "Vegan", "Gluten-Free",
                                               "Dairy-Free", "Low-Carb", "Low-Sugar", "Low-Sodium"])

        user_food = st.text_area("Foods You'd Like to Eat (comma separated)",
                                 placeholder="E.g., chicken, rice, vegetables, pasta")

        cuisine_preference = st.selectbox("Cuisine Preference (Optional)",
                                          ["Any", "Mediterranean", "Asian", "Mexican",
                                           "Italian", "American", "Indian", "Other"])

    with col2:
        if st.button("Get AI Recommendations", type="primary"):
            with st.spinner("Generating personalized recommendations..."):
                # Prepare message for AI
                restrictions = ", ".join(dietary_restrictions) if dietary_restrictions else "None"
                cuisine = cuisine_preference if cuisine_preference != "Any" else ""

                # Include user profile information if available
                profile_info = ""
                if st.session_state.diabetes_type:
                    profile_info = f"I have {st.session_state.diabetes_type} diabetes. "
                    profile_info += f"My target glucose range is {st.session_state.target_range[0]}-{st.session_state.target_range[1]} mg/dL. "

                messages = [
                    {"role": "system", "content": """You are a knowledgeable diabetes nutritional assistant providing 
                    detailed and personalized dietary recommendations based on glucose levels. 
                    Consider the glycemic index of foods, portion sizes, and overall balanced nutrition. 
                    Provide specific meal ideas and explain why they're suitable based on the glucose readings.
                    Include both what to eat and what to avoid based on the current readings."""},

                    {"role": "user", "content": f"""
                    {profile_info}
                    My recent glucose readings are:
                    - Morning: {morning_glucose} mg/dL
                    - Afternoon: {afternoon_glucose} mg/dL 
                    - Evening: {evening_glucose} mg/dL

                    I'm planning to eat for {meal_type}.
                    I'm interested in eating: {user_food if user_food else "anything healthy"}
                    Dietary restrictions: {restrictions}
                    Cuisine preference: {cuisine}

                    Please provide:
                    1. An analysis of my glucose patterns
                    2. Specific meal recommendations with portions
                    3. Foods to avoid based on my current readings
                    4. Tips for maintaining stable glucose after this meal
                    """}
                ]

                try:
                    response = client.chat.completions.create(
                        model="microsoft/phi-4",
                        temperature=0.3,
                        messages=messages
                    )

                    ai_suggestion = response.choices[0].message.content

                    # Save to recommendations history
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    recommendation_with_time = f"**{timestamp} - {meal_type} Recommendation**\n\n{ai_suggestion}"
                    st.session_state.recommendations_history.append(recommendation_with_time)

                    st.markdown("<div class='recommendation-box'>", unsafe_allow_html=True)
                    st.markdown("### AI Dietary Recommendations")
                    st.write(ai_suggestion)
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
                    st.markdown("""
                    <div class='info-box'>
                        <strong>Troubleshooting:</strong><br>
                        - Check your API key configuration<br>
                        - Ensure you have internet connectivity<br>
                        - Try again in a few moments
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(
                "<div class='info-box'>Enter your glucose readings and food preferences, then click 'Get AI Recommendations'.</div>",
                unsafe_allow_html=True)

            if st.session_state.recommendations_history:
                st.markdown("### Previous Recommendation")
                st.markdown("<div class='recommendation-box'>", unsafe_allow_html=True)
                st.write(st.session_state.recommendations_history[-1])
                st.markdown("</div>", unsafe_allow_html=True)

elif app_mode == "History":
    st.markdown("<h2 class='sub-header'>Glucose History & Trends</h2>", unsafe_allow_html=True)

    if not st.session_state.glucose_history.empty:
        tab1, tab2, tab3 = st.tabs(["Data Table", "Charts", "Statistics"])

        with tab1:
            st.dataframe(st.session_state.glucose_history.sort_values(by=['Date', 'Time'], ascending=False),
                         use_container_width=True)

            if st.button("Export Data (CSV)"):
                csv = st.session_state.glucose_history.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="glucose_history.csv",
                    mime="text/csv"
                )

        with tab2:
            # Time period for filtering
            period_filter = st.selectbox("Time Period",
                                         ["All Time", "Last 7 Days", "Last 14 Days", "Last 30 Days"],
                                         index=1)

            # Filter data based on selection
            filtered_data = st.session_state.glucose_history.copy()
            if period_filter != "All Time":
                days = int(period_filter.split()[1])
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                filtered_data = filtered_data[filtered_data['Date'] >= cutoff_date]

            # Create a Plotly figure - Time Series
            fig1 = go.Figure()

            # Add the glucose readings
            fig1.add_trace(go.Scatter(
                x=filtered_data['Date'] + ' ' + filtered_data['Time'],
                y=filtered_data['Reading'],
                mode='lines+markers',
                name='Glucose',
                marker=dict(size=8, color='#3366cc'),
                line=dict(width=2, color='#3366cc')
            ))

            # Add target range as a shaded area
            fig1.add_trace(go.Scatter(
                x=filtered_data['Date'] + ' ' + filtered_data['Time'],
                y=[st.session_state.target_range[1]] * len(filtered_data),
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))

            fig1.add_trace(go.Scatter(
                x=filtered_data['Date'] + ' ' + filtered_data['Time'],
                y=[st.session_state.target_range[0]] * len(filtered_data),
                fill='tonexty',
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(76, 175, 80, 0.2)',
                name='Target Range'
            ))

            # Layout configuration
            fig1.update_layout(
                title='Glucose Readings Over Time',
                xaxis_title='Date and Time',
                yaxis_title='Glucose Level (mg/dL)',
                height=400,
                margin=dict(l=40, r=40, t=40, b=40),
                hovermode='closest'
            )

            st.plotly_chart(fig1, use_container_width=True)

            # Box plot by time period
            fig2 = go.Figure()

            for period in ["Morning", "Afternoon", "Evening"]:
                period_data = filtered_data[filtered_data['Period'].str.contains(period)]
                if not period_data.empty:
                    fig2.add_trace(go.Box(
                        y=period_data['Reading'],
                        name=period,
                        boxpoints='all',
                        jitter=0.3,
                        pointpos=-1.8
                    ))

            fig2.update_layout(
                title='Glucose Distribution by Time of Day',
                yaxis_title='Glucose Level (mg/dL)',
                height=400,
                margin=dict(l=40, r=40, t=40, b=40)
            )

            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            col1, col2 = st.columns(2)

            with col1:
                if not filtered_data.empty:
                    st.markdown("### Overall Statistics")
                    avg = filtered_data['Reading'].mean()
                    median = filtered_data['Reading'].median()
                    std_dev = filtered_data['Reading'].std()
                    min_val = filtered_data['Reading'].min()
                    max_val = filtered_data['Reading'].max()

                    st.markdown(f"""
                    <div class='info-box'>
                        <strong>Average:</strong> {avg:.1f} mg/dL<br>
                        <strong>Median:</strong> {median:.1f} mg/dL<br>
                        <strong>Standard Deviation:</strong> {std_dev:.1f} mg/dL<br>
                        <strong>Range:</strong> {min_val} - {max_val} mg/dL
                    </div>
                    """, unsafe_allow_html=True)

                    # Calculate time in range
                    in_range = len(filtered_data[
                                       (filtered_data['Reading'] >= st.session_state.target_range[0]) &
                                       (filtered_data['Reading'] <= st.session_state.target_range[1])
                                       ])
                    total = len(filtered_data)
                    percentage = (in_range / total) * 100 if total > 0 else 0

                    fig3 = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=percentage,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Time in Range (%)"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#3366cc"},
                            'steps': [
                                {'range': [0, 50], 'color': "#ffcccb"},
                                {'range': [50, 70], 'color': "#ffffcc"},
                                {'range': [70, 100], 'color': "#ccffcc"}
                            ],
                            'threshold': {
                                'line': {'color': "green", 'width': 2},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))

                    fig3.update_layout(height=250)
                    st.plotly_chart(fig3)

            with col2:
                st.markdown("### Time of Day Analysis")

                # Calculate averages by time of day
                time_averages = {}
                for period in ["Morning", "Afternoon", "Evening"]:
                    period_data = filtered_data[filtered_data['Period'].str.contains(period)]
                    if not period_data.empty:
                        time_averages[period] = period_data['Reading'].mean()

                if time_averages:
                    fig4 = go.Figure(go.Bar(
                        x=list(time_averages.keys()),
                        y=list(time_averages.values()),
                        marker_color='#3366cc'
                    ))

                    fig4.update_layout(
                        title='Average Glucose by Time of Day',
                        xaxis_title='Time of Day',
                        yaxis_title='Average Glucose (mg/dL)',
                        height=250
                    )

                    # Add a horizontal line for target range
                    target_mid = (st.session_state.target_range[0] + st.session_state.target_range[1]) / 2
                    fig4.add_shape(
                        type="line",
                        x0=-0.5,
                        y0=target_mid,
                        x1=2.5,
                        y1=target_mid,
                        line=dict(
                            color="green",
                            width=2,
                            dash="dash",
                        )
                    )

                    st.plotly_chart(fig4)
    else:
        st.markdown(
            "<div class='info-box'>No glucose data available yet. Start logging your readings to see history and trends.</div>",
            unsafe_allow_html=True)

# Footer with disclaimer
st.markdown(
    "<div class='disclaimer'>⚠️ <strong>Important Disclaimer:</strong> This application provides general guidance only and is not a substitute for professional medical advice. Always consult your healthcare provider before making any changes to your diabetes management plan.</div>",
    unsafe_allow_html=True)