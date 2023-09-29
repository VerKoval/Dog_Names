from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

df = pd.read_csv('NYC_Dog_Licensing_Dataset.csv', dtype={'ZipCode': str})
df = df[~df['AnimalName'].isin(['UNKNOWN', 'NAME NOT PROVIDED']) & ~df['BreedName'].isin(['Unknown'])]

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
            dcc.Graph(figure={}, id='controls-and-graph')
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

@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x=col_chosen).update_xaxes(categoryorder='total descending')  # Added descending order
    return fig

if __name__ == '__main__':
    app.run(debug=True)
