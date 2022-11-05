import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

data = pd.read_csv('registrations_by_county_2013-2021_v4.csv')
data['Year'] = pd.to_datetime(data['Date']).dt.year
# data['1000Count/population'] = data['Count/population']*1000

# Crerate temporary dataframe, calculate population numbers and left join values to source data
temp = data.loc[data['Fuel type'] == 'Gas'].copy()
temp['Population'] = (temp['Count']/temp['Count/population']).astype('int64')
temp = temp.set_index(['County code', 'Year'])
data = data.join(temp['Population'], on=['County code', 'Year'], how='left')




st.sidebar.header("Customize the chart")

year = st.sidebar.selectbox('Year:', list(data['Year'].sort_values(ascending=False).unique()))
fuel = st.sidebar.selectbox('Fuel type:', ['All'] + list(data['Fuel type'].unique()))

if fuel == 'All':
    sample = data[data['Year'] == year]
else:
    sample = data.loc[(data['Year'] == year) & (data['Fuel type'] == fuel) ]

sample_gpby = sample.groupby(by='County', as_index=False).agg({'Count':'sum', 'Population':'mean'})
sample_gpby['Count per 1000 people'] = 1000*sample_gpby['Count']/sample_gpby['Population']




field = st.sidebar.radio('Show absolute counts or registrations per 1000 people?',['Per 1000 people', 'Absolute'])

if field == 'Absolute':
    yval = 'Count'
else:
    yval = 'Count per 1000 people'




sorttype = st.sidebar.radio('Sort counties by:', ['Values: High->Low', 'Values: Low->High', 'Alphabetical'])
if sorttype == 'Values: High->Low':
    sample_gpby = pd.DataFrame(sample_gpby).sort_values(by=yval, ascending= False)
elif sorttype == 'Values: Low->High':
    sample_gpby = pd.DataFrame(sample_gpby).sort_values(by=yval)
else:
    sample_gpby = pd.DataFrame(sample_gpby).sort_values(by='County')

sortlist = list(sample_gpby['County'])




st.title(f'Initial car registrations in Swedish counties ({year})')
st.write(f'Fuel type: {fuel}')
barchart = alt.Chart(sample_gpby).mark_bar().encode(
    x=alt.X(yval, title=yval, axis=alt.Axis(orient='top')),
    y=alt.Y('County', sort=sortlist, title='County')
)

st.altair_chart(barchart, use_container_width=True)
