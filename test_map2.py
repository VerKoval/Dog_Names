import json
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# GeoJSON file- Lats and longs of each zip code (polygods)
nyc_geojson_path = 'GEOJSON DATA PATH GOES HERE'  #enter path to geojson file

# load PO_NAME (neighborhood) ZipCode
with open(nyc_geojson_path, 'r') as file:
    nyc_geojson = json.load(file)
nyc_zip_codes = {feature['properties']['postalCode']: feature['properties']['PO_NAME']
                 for feature in nyc_geojson['features']}

# READ ZIPCODE AS TYPE STR
dog_data = pd.read_csv('DOG LICENSING CSV GOES HERE', dtype={'ZipCode': str}) #enter path to Dataset.csv file

# Filter out unwanted names
unwanted_names = ['UNKNOWN', 'NAME NOT PROVIDED', 'NAME', 'NOT', 'NONE', 'DOG']
dog_data = dog_data[~dog_data['AnimalName'].isin(unwanted_names)]

# NYC Zip Codes from Dog Licensing Data
dog_data = dog_data[dog_data['ZipCode'].isin(nyc_zip_codes.keys())]

# Group by ZipCode and AnimalName counts
name_zip_counts = dog_data.groupby(['ZipCode', 'AnimalName']).size().reset_index(name='Count')

# Sort, Group, Top3
name_zip_counts = name_zip_counts.sort_values(['ZipCode', 'Count'], ascending=[True, False])
top_names = name_zip_counts.groupby('ZipCode').head(3).reset_index(drop=True)
top_names['Info'] = top_names['AnimalName'] + ': ' + top_names['Count'].astype(str)
top_names_info = top_names.groupby('ZipCode')['Info'].apply(lambda x: ', '.join(x)).reset_index()

# Adding the PO_NAME information
top_names_info['PO_NAME'] = top_names_info['ZipCode'].map(nyc_zip_codes)
top_names_info['Text'] = 'Neighborhood: ' + top_names_info['PO_NAME'] + '<br>' + 'Top Dogs: ' + top_names_info['Info']

# Chloropleth
fig = px.choropleth(
    top_names_info,  # df
    geojson=nyc_geojson,  # GeoJSON
    locations='ZipCode',  # df ZipCode
    color='ZipCode',  # just used for differentiating areas
    featureidkey="properties.postalCode",  # the key used for the zip codes in  GeoJSON
    hover_name='Text'  # the info to display when hovering
)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    dcc.Graph(
        id='choropleth',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
