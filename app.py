# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Configure the page
st.set_page_config(
    page_title="Gender Gap at the Political Party Leadership Level",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded")



# Load and process data
data_cleaned = pd.read_csv('https://raw.githubusercontent.com/selinekarabulut/gendergap_dashboard/main/Data/data_cleaned.csv')
country_lat_lon = pd.read_csv('https://raw.githubusercontent.com/selinekarabulut/gendergap_dashboard/main/Data/countries.csv')
merged_data = pd.merge(data_cleaned, country_lat_lon, on='country', how='left')

# Calculate the percentage of female leaders by system of government and by country
def calculate_gender_percentage(data, group_by):
    gender_percentage = data.groupby(group_by + ['sex']).size().unstack(fill_value=0)
    total = gender_percentage.sum(axis=1)
    gender_percentage = (gender_percentage.div(total, axis=0) * 100).reset_index()
    female_percentage = gender_percentage[[*group_by, 'F']].rename(columns={'F': 'percentage'})
    return female_percentage.groupby(group_by).mean().reset_index()

female_percentage = calculate_gender_percentage(merged_data, ['country', 'in_year'])
female_percentage_by_sysofgov = calculate_gender_percentage(merged_data, ['sysofgov', 'in_year'])

# Sidebar for user input
with st.sidebar:
    st.title('⚖️  Gender Disparity in Political Party Leadership')
    year_list = sorted(set(female_percentage['in_year']).union(female_percentage_by_sysofgov['in_year']), reverse=True)
    selected_year = st.selectbox('Select a year', [int(year) for year in year_list])

df_selected_year = female_percentage[female_percentage['in_year'] == selected_year]
selected_data_sysofgov = female_percentage_by_sysofgov[female_percentage_by_sysofgov['in_year'] == selected_year]

# Function to create choropleth map

def make_choropleth(data):
    choropleth = px.choropleth(data, locations="country", locationmode='country names', color="percentage",
                               hover_name="country", hover_data={"percentage": True},
                               color_continuous_scale=px.colors.sequential.Plasma,
                               labels={'percentage': 'Percentage of Females'},
                               title=" 🌍 Percentage of Females by Country in Selected Year")
    # Update layout to set the plot background to light gray and adjust border properties
    choropleth.update_layout(
        margin={"r":0, "t":0, "l":0, "b":0},
        coloraxis_colorbar=dict(title="Percentage"),
        geo=dict(
            bgcolor='white',    # Sets the background of the geographical map area
            showframe=True,
            showcoastlines=True,
            projection_type='equirectangular',
            countrycolor='black',  # Set the color of the country borders
            countrywidth=100       # Set the width of the country borders to make them visible and distinct
        )
    )
    return choropleth

 


# Function to create pie chart
def make_pie_chart(year):
    data = female_percentage[female_percentage['in_year'] == year]
    total_percentage = data['percentage'].mean()
    fig = px.pie(names=["Female", "Male"], values=[total_percentage, 100-total_percentage])
    return fig

# Create a bar chart for sysofgov data
def create_sysofgov_bar_chart(data):
    bar_chart = px.bar(data, x='sysofgov', y='percentage', color='sysofgov',
                       title=f"Percentage of Women Leaders by System of Government in {selected_year}",
                       labels={'(%)': '(%) of Women', 'sysofgov': 'System of Government'})
    bar_chart.update_layout(xaxis_title="System of Government", yaxis_title="(%) of Women Political Party Leaders")
    return bar_chart


with st.expander(':red[**About**]', expanded=True):
        st.write('''
            - Data:
                -  The data on political party leadership was collected as part of my doctoral dissertation research.
                -  GPS coordinates for every world country (https://developers.google.com/public-data/docs/canonical/countries_csv).
            - Github repo: (https://github.com/selinekarabulut/gendergap_dashboard/)
            ''')
        
# Display the choropleth map and pie chart
col1, col2 = st.columns([3, 1])  # Allocates space to choropleth map and pie chart


        
with col1:
    st.subheader(f" 🌍 Comparative Analysis of Women Political Party Leaders in {selected_year}")
    choropleth = make_choropleth(df_selected_year)
    st.plotly_chart(choropleth, use_container_width=True)

   

with col2:
    st.subheader(f"Percentage of Women Political Party Leaders in {selected_year}")
    pie_chart = make_pie_chart(selected_year)
    st.plotly_chart(pie_chart, use_container_width=True)

    

# Display the bar chart below the maps
st.subheader(f"Women Political Party Leaders by System of Government in {selected_year}")
sysofgov_chart = create_sysofgov_bar_chart(selected_data_sysofgov)
st.plotly_chart(sysofgov_chart, use_container_width=True)
