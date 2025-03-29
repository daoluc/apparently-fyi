import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set page title
st.title("Sea Cable Media Narrative")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("combined_narrative_articles.csv")
    # Convert Published Date to datetime
    df['Published Date'] = pd.to_datetime(df['Published Date'])
    return df

@st.cache_data
def load_narratives():
    narratives_df = pd.read_csv("narratives.csv")
    return narratives_df

# Load the data
df = load_data()
narratives_df = load_narratives()

# Display data loading status
st.write(f"Loaded {len(df)} articles from the database")

# Get unique narrative IDs
narrative_ids = df['narrative_id'].unique()

# Create a visualization for each narrative
for narrative_id in narrative_ids:
    # Filter data for the current narrative
    narrative_data = df[df['narrative_id'] == narrative_id]
    
    # Create a subheader for the narrative
    st.subheader(f"Narrative ID: {narrative_id}")
    
    # Display narrative description if available
    narrative_description = narratives_df[narratives_df['id'] == narrative_id]['narrative'].values
    if len(narrative_description) > 0:
        # Replace pipe characters with newlines for better formatting
        formatted_description = narrative_description[0].replace("|", "\n")
        st.write(f"**Description:** {formatted_description}")
    
    # Get unique media locations for this narrative
    media_locations = narrative_data['Media Location'].unique()
    
    # Create a color map for media locations
    color_map = {}
    colors = plt.cm.tab20.colors
    for i, location in enumerate(media_locations):
        color_map[location] = colors[i % len(colors)]
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each media location with a different color
    for location in media_locations:
        location_data = narrative_data[narrative_data['Media Location'] == location]
        ax.scatter(
            location_data['Published Date'], 
            location_data['agreement_score'],
            label=location,
            alpha=0.7,
            s=100,
            color=color_map[location]
        )
    
    # Set plot labels and title
    ax.set_xlabel('Published Date')
    ax.set_ylabel('Agreement Score')
    ax.set_title(f'Agreement Score by Published Date for Narrative {narrative_id}')
    
    # Format x-axis to show dates nicely
    fig.autofmt_xdate()
    
    # Add a horizontal line at y=0 for reference
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Add legend with smaller font size to accommodate many media locations
    if len(media_locations) > 10:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    else:
        ax.legend(loc='best')
    
    # Show the plot in Streamlit
    st.pyplot(fig)
    
    # Add some statistics about the narrative
    st.write(f"Average agreement score: {narrative_data['agreement_score'].mean():.2f}")
    st.write(f"Number of unique media locations: {len(media_locations)}")
    
    # Add a divider between narratives
    st.markdown("---")

# Add a data table with filters
st.subheader("Filtered Data Table")
# Add filters
selected_narrative = st.selectbox("Select Narrative ID", options=narrative_ids)
min_date, max_date = st.slider(
    "Date Range",
    min_value=df['Published Date'].min().to_pydatetime(),
    max_value=df['Published Date'].max().to_pydatetime(),
    value=(df['Published Date'].min().to_pydatetime(), df['Published Date'].max().to_pydatetime())
)

# Filter the data based on selections
filtered_df = df[
    (df['narrative_id'] == selected_narrative) &
    (df['Published Date'] >= pd.Timestamp(min_date)) &
    (df['Published Date'] <= pd.Timestamp(max_date))
]

# Show the filtered data
st.dataframe(filtered_df)
