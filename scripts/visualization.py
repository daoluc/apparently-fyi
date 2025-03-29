import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Legend, LegendItem
from bokeh.palettes import Category20
from bokeh.transform import factor_cmap

# Set page title
st.title("Sea Cable Cutting Narratives")

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
    media_locations = narrative_data['Media Location'].unique().tolist()
    
    # Create a Bokeh figure with increased size
    p = figure(
        title=f'Agreement Score by Published Date for Narrative {narrative_id}',
        x_axis_label='Published Date',
        y_axis_label='Agreement Score',
        x_axis_type='datetime',
        width=2000,  
        height=800, 
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location="above"
    )
    
    # Add a horizontal line at y=0 for reference
    p.line(
        x=[narrative_data['Published Date'].min(), narrative_data['Published Date'].max()],
        y=[0, 0],
        line_color='gray',
        line_dash='dashed',
        line_alpha=0.5
    )
    
    # Create a color palette for the media locations
    colors = Category20[20]
    color_map = {location: colors[i % len(colors)] for i, location in enumerate(media_locations)}
    
    # Create a hover tool
    hover = HoverTool(
        tooltips=[
            ("Title", "@Title"),
            ("Media Location", "@Media_Location"),
            ("Published Date", "@Published_Date{%F}"),
            ("Agreement Score", "@agreement_score")
        ],
        formatters={"@Published_Date": "datetime"}
    )
    p.add_tools(hover)
    
    # Plot each media location with a different color
    legend_items = []
    for location in media_locations:
        location_data = narrative_data[narrative_data['Media Location'] == location]
        source = ColumnDataSource(data={
            'Published_Date': location_data['Published Date'],
            'agreement_score': location_data['agreement_score'],
            'Title': location_data['Title'],
            'Media_Location': location_data['Media Location']
        })
        
        circle = p.circle(
            x='Published_Date',
            y='agreement_score',
            source=source,
            size=12,  # Increased point size from 10 to 12
            color=color_map[location],
            alpha=0.7
        )
        
        legend_items.append((location, [circle]))
    
    # Add legend
    if len(media_locations) > 10:
        # For many locations, place legend outside the plot
        p.add_layout(Legend(items=legend_items, location="center_right"), 'right')
        p.legend.click_policy = "hide"  # Make legend interactive
    else:
        # For fewer locations, place legend inside the plot
        legend = Legend(items=legend_items)
        legend.click_policy = "hide"  # Make legend interactive
        p.add_layout(legend, 'right')
    
    # Show the plot in Streamlit
    st.bokeh_chart(p, use_container_width=True)
    
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
