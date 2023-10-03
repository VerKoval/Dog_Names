from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

df = pd.read_csv('NYC_Dog_Licensing_Dataset.csv', dtype={'ZipCode': str})
df = df[~df['AnimalName'].isin(['UNKNOWN', 'NAME NOT PROVIDED', 'NAME']) & ~df['BreedName'].isin(['Unknown'])]

external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    dbc.Row([
        html.Div('Dog Names', className="text-primary text-center fs-3")
    ]),
    
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'})
        ], width=12),
        
        dbc.Col([
            dcc.Graph(figure={}, id='controls-and-graph', config={'staticPlot': False, 'scrollZoom': True})
        ], width=12),
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

# Pre-calculate the aggregated counts for each option
agg_animal_name = df['AnimalName'].value_counts().reset_index()
agg_animal_name.columns = ['AnimalName', 'count']
agg_animal_name = agg_animal_name[agg_animal_name['count'] > 1]

agg_breed_name = df['BreedName'].value_counts().reset_index()
agg_breed_name.columns = ['BreedName', 'count']
agg_breed_name = agg_breed_name[agg_breed_name['count'] > 1]

agg_zip_code = df['ZipCode'].value_counts().reset_index()
agg_zip_code.columns = ['ZipCode', 'count']
agg_zip_code = agg_zip_code[agg_zip_code['count'] > 1]

@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    if col_chosen == 'AnimalName':
        data_to_plot = agg_animal_name
    elif col_chosen == 'BreedName':
        data_to_plot = agg_breed_name
    else:
        data_to_plot = agg_zip_code

    fig = px.bar(data_to_plot, y=col_chosen, x='count', orientation='h').update_yaxes(categoryorder='total descending')
    
    # Set initial range for y-axis to display only the first 12 entries
    fig.update_layout(yaxis=dict(range=[0, 12]))
    
    return fig


if __name__ == '__main__':
    app.run(debug=True)