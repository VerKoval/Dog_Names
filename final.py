from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import json
import dash

# READ ZIPCODE AS TYPE STR
dog_data = pd.read_csv('NYC_Dog_Licensing_Dataset.csv', dtype={'ZipCode': str}) #enter path to Dataset.csv file

# Filter out unwanted names
unwanted_names = ['UNKNOWN', 'NAME NOT PROVIDED', 'NAME', 'NOT', 'NONE', 'DOG']
dog_data = dog_data[~dog_data['AnimalName'].isin(unwanted_names) & ~dog_data['BreedName'].isin(['Unknown'])]

# GeoJSON file- Lats and longs of each zip code (polygods)
nyc_geojson_path = 'nyc-zip-code-tabulation-areas-polygons.geojson'  #enter path to geojson file

# load PO_NAME (neighborhood) ZipCode
with open(nyc_geojson_path, 'r') as file:
    nyc_geojson = json.load(file)
nyc_zip_codes = {feature['properties']['postalCode']: feature['properties']['PO_NAME']
                 for feature in nyc_geojson['features']}

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

external_stylesheets = [dbc.themes.SKETCHY]
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    dbc.Row([
        html.Div('Dog Names', className="text-primary text-center fs-3")
    ]),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(data=dog_data.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'})
        ], width=12),
        dbc.Col([
            dcc.Graph(figure={}, id='controls-and-graph')
        ], width=6),
        dbc.Col([
            dcc.Graph(figure={}, id='choropleth-map')
        ], width=6),
    ]),
    
    dbc.Row([
        dcc.RadioItems(
            options=[
                    {'label': 'Animal Name', 'value': 'AnimalName'},
                    {'label': 'Breed Name', 'value': 'BreedName'},
                    {'label': 'Zip Code', 'value': 'ZipCode'}
            ],
            value='AnimalName',
            id='controls-and-radio-item',
            labelStyle={'display': 'block', 'margin-right': '10px'},
            inline=True
        )
    ])
], fluid=True)

@callback(
    [Output(component_id='controls-and-graph', component_property='figure'),
     Output(component_id='choropleth-map', component_property='figure')],
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    # Update the graph
    fig1 = px.histogram(dog_data, x=col_chosen).update_xaxes(categoryorder='total descending')
    
    # Chloropleth
    choropleth_fig = px.choropleth(
        top_names_info,  # df
        geojson=nyc_geojson,  # GeoJSON
        locations='ZipCode',  # df ZipCode
        color='ZipCode',  # just used for differentiating areas
        featureidkey="properties.postalCode",  # the key used for the zip codes in  GeoJSON
        hover_name='Text'  # the info to display when hovering

    )
    
    choropleth_fig.update_geos(fitbounds="locations")

    return fig1, choropleth_fig

if __name__ == '__main__':
    app.run(debug=True)
