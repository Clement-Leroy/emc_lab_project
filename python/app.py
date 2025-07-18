import base64
import io
import dash
from dash import dcc, ctx, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import dash_auth
import plotly.graph_objects as go
import pandas as pd
import datetime
from datetime import datetime
import pymysql
import json
import cryptography

connection = pymysql.connect(
       host='database',
       port=3306,
       user='user',
       password="password",
       db='emc_lab_energy',
       cursorclass=pymysql.cursors.DictCursor
   )

cursor = connection.cursor()

def read_database():
    connection.ping(reconnect=True)
    cursor.execute("SELECT * FROM consumption_price ORDER BY Date ASC")
    database = cursor.fetchall()

    return pd.DataFrame.from_records(database)

database = read_database()

USERNAME_PASSWORD_PAIRS = [['username','password']]

external_scripts = ["https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.1/jquery.min.js",
                    "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js",
                    'https://trentrichardson.com/examples/timepicker/jquery-ui-timepicker-addon.js']

external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://code.jquery.com/ui/1.13.3/themes/base/jquery-ui.css']

app = dash.Dash(__name__, include_assets_files=True, external_scripts=external_scripts, external_stylesheets=external_stylesheets)
app.secret_key = 'super secret key'
app.title = "MPS | EMC Lab Energy"
app._favicon = ("icon_MPS.ico")
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

server=app.server
server.config.update(SECRET_KEY="SECRET_KEY")

# Header
logo=html.Img(src="https://community.element14.com/e14/assets/main/mfg-group-assets/monolithicpowersystemsLogo.png",style={'height': '50px','margin-right':'10px'})
title=html.H1("EMC Lab Energy",style={'font-size':50,'font-weight':'bold'})
location=html.H1("EMC Lab Ettenheim",style={'font-size':50,'font-weight':'bold'})
header = html.Div([
            html.Div([
                logo
            ], style={'display': 'flex', 'align-items': 'center'}),
            title
        ], style={'display': 'flex', 'justify-content': 'space-between', 'padding': '10px 20px', 'background-color': '#1E2A38', 'color': 'white', 'margin-bottom': '20px', "z-index": "1001"})

# Footer
footer=html.Footer([html.P('Copyright © 2025 Monolithic Power Systems, Inc. All rights reserved.',style={'text-align':'center','color':'#666'})],style={'position':'relative','bottom':'0','width':'100%','padding':'20px 0px','background-color':'#e0e0e0','text-align':'center','margin-top':'20px',"z-index": "1000",})

today = datetime.today()
option = []
month = 8
year = 2024
month_list = ['January', 'February', 'March', 'April', 'Mai', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

while year != today.year or month != today.month:
    option.append(f'{month_list[month]} {year}')

    if month == 11:
        month = 0
        year = year + 1
    else:
        month = month + 1

month_dropdownmenu = dcc.Dropdown(options = option, value = option[-1], id='month_dropdownmenu', style={'width': '160px'}, clearable=False)
database_info = html.Label(children='Upload new data', id='database_info', style={'font-weight':'bold', 'font-size':'18'})

upload_month = dcc.Upload(
    id='upload_data',
    children=[
        'Drag and Drop or ',
        html.A('Select a File')
    ], style={
        'width': '500px',
        'height': '100px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin-top':'10px',
        'margin-bottom':'20px'
    })

date_range = dbc.Stack([html.Label(children='Date range', style={'font-weight':'bold'}), dcc.DatePickerRange(id="date_range", start_date=datetime(today.year,1, 1), end_date=today)], style={'margin-top':10})


# def summarize_data(df):
#     """Summarizes consumption and price by month and year."""
#     df['Year'] = df['Date'].dt.year
#     df['Month'] = df['Date'].dt.month_name()  # Get month names for better display
#
#     # Group by Year and Month and sum the relevant columns
#     df_summary = df.groupby(['Year', 'Month']).agg(
#         Total_Consumption_kWh=('Consumption', 'sum'),
#         Total_Price=('Price', 'sum')
#     ).reset_index()
#
#     # Format numbers for better readability
#     df_summary['Total_Consumption_kWh'] = df_summary['Total_Consumption_kWh'].round(2)
#     df_summary['Total_Price'] = df_summary['Total_Price'].round(2)
#
#     # Optional: Order months correctly for display
#     month_order = [
#         "January", "February", "March", "April", "May", "June",
#         "July", "August", "September", "October", "November", "December"
#     ]
#     df_summary['Month'] = pd.Categorical(df_summary['Month'], categories=month_order, ordered=True)
#     df_summary = df_summary.sort_values(by=['Year', 'Month']).reset_index(drop=True)
#
#     # Combine Year and Month into a single 'Data' column for display in AgGrid
#     # FIX: Convert 'Month' to string before concatenation to avoid TypeError
#     df_summary['Data'] = df_summary['Month'].astype(str) + ' ' + df_summary['Year'].astype(str)
#
#     return df_summary

def graph_scale_fct(scale, figure, value, df):
    df.set_index('Date', inplace=True)

    if scale == 'Day':
        df_new = df.resample('D').sum()
        figure['layout']['xaxis']['tickformat'] = '%b %d, %Y'
        figure['layout']['xaxis']['dtick'] = 'D1'

    elif scale == 'Week':
        df_new = df.resample('W').sum()
        figure['layout']['xaxis']['tickformat'] = '%b %U, %Y'
        figure['layout']['xaxis']['dtick'] = 604800000

    elif scale == 'Month':
        df_new = df.resample('MS').sum()
        figure['layout']['xaxis']['tickformat']='%b, %Y'
        figure['layout']['xaxis']['dtick'] = 'M1'

    elif scale == 'Year':
        df_new = df.resample('Y').sum()
        figure['layout']['xaxis']['tickformat'] = '%Y'
        figure['layout']['xaxis']['dtick'] = 31557600000

    else:
        df_new = df
        figure['layout']['xaxis']['tickformat'] = None
        figure['layout']['xaxis']['dtick'] = None

    figure['data'][0]['x'] = df_new.index
    figure['data'][0]['y'] = df_new['Consumption'] if value == 'Consumption' else df_new['Price']

    return figure, df_new

date = dcc.DatePickerSingle(
        id='date_picker',
        min_date_allowed=datetime(2024, 9, 1),
        max_date_allowed=today,
        date=datetime.today(),
    )

filtered_data = database[((database['Date'] > datetime(today.year, today.month, today.day, 0, 0, 0)) & (database['Date'] < datetime(today.year, today.month, today.day, 9, 0, 0))) | ((database['Date'] > datetime(today.year, today.month, today.day, 18, 0, 0)) & (database['Date'] < datetime(today.year, today.month, today.day, 23, 59, 0)))]
sum = filtered_data['Consumption'].sum()

energy_consumed = dbc.Stack(
    [
        date,
        html.Div(id='energy_consumed', children = f'Energy consumed out of working time: {round(sum, 1)} KWh')
    ], direction='horizontal', gap =2, style={'margin-top':10}
)

# Main layout
def get_layout():
    df = read_database()

    graph_value = html.Div([html.Label(children='Value', style={'font-weight':'bold'}), dcc.RadioItems(id='graph_value', options=['Consumption', 'Price'], value='Consumption', inline=True, inputStyle={"margin-right": "5px"}, labelStyle={"margin-right": "5px"})], style={'margin-top':10})
    graph_scale = html.Div([html.Label(children='Scale', style={'font-weight':'bold'}), dcc.RadioItems(id='graph_scale', options=['intra-Day', 'Day', 'Week', 'Month', 'Year'], value='Month', inline=True, inputStyle={"margin-right": "5px"}, labelStyle={"margin-right": "5px"})], style={'margin-top':10})

    hovertemplate = "%{x}:<br>Consumption: %{value} KWh</br><extra></extra>"
    filtered_db = df[df['Date'] > datetime(today.year, 1, 1)]

    figure = go.Figure(
                        data=go.Bar(x=filtered_db['Date'], y=filtered_db['Consumption'], hovertemplate=hovertemplate),
                        layout=go.Layout(
                            title=dict(text="EMC lab energy consumption", font=dict(size=25, weight='bold')),
                            barcornerradius=15,
                            hovermode='closest',
                            showlegend=False,
                            plot_bgcolor='white',
                            xaxis={'title_text':'Date', 'title_font':dict(size=16, weight='bold'), 'tickfont':dict(size=16)},
                            yaxis={'title_text':'Consumption (kWh)', 'title_font':dict(size=16, weight='bold'), 'gridcolor':'lightgrey', 'tickfont':dict(size=16), 'fixedrange':True},
                            uniformtext= {
                                    "mode": "hide",
                                    "minsize": 16
                            },
                            hoverlabel= {
                                    'font': {
                                        'size': 16,
                                    }},
                            margin={"t": 50, "b": 0, 'r': 0, 'l': 0},
                        ))

    # df_monthly_summary = summarize_data(df)

    figure, _ = graph_scale_fct('Month', figure, 'Consumption', filtered_db)

    chart = dcc.Loading(dcc.Graph(id='chart', figure=figure,
                      config={'toImageButtonOptions': {'filename': 'typ_graph'}, 'responsive': True,
                              'displaylogo': False,
                              'modeBarButtonsToRemove': ['zoom', 'pan', 'zoomin', 'zoomout', 'autoscale', 'resetscale',
                                                         'lasso2d', 'select2d']},
                      style={'height': '1064px', 'width': '100%', 'fontWeight': 'bold'}
                      ),overlay_style={"visibility":"visible", "filter": "blur(2px)"},type="circle")

    # columnDefs = [
    #     {"headerName": "Data", "field": "Data", 'flex':1},
    #     {"headerName": "Consumption", "field": "Total_Consumption_kWh", "type": "numericColumn", 'flex':1},
    #     {"headerName": "Price", "field": "Total_Price", "type": "numericColumn", 'flex':1}
    # ]
    #
    # defaultColDef = {
    #     "filter": True,
    #     "sortable": True,
    #     "resizable": True,
    #     "cellStyle": {"textAlign": "center"},  # Center align cell content
    #     "headerClass": "center-header",  # Custom class for header styling
    # }
    #
    # table = html.Div(
    #     dag.AgGrid( # Using dash_ag_grid.AgGrid
    #         id='monthly-summary-grid',
    #         columnDefs=columnDefs,
    #         rowData=df_monthly_summary.to_dict('records'),
    #         defaultColDef=defaultColDef,
    #         dashGridOptions={"domLayout": "autoHeight"}, # Adjust grid height automatically
    #
    #         # AG Grid theme and custom styling
    #         className="ag-theme-alpine", # Alpine theme for a clean look
    #         style={
    #             "height": "auto", # Let AgGrid determine height based on content
    #             "width": "100%",
    #             "borderRadius": "8px",
    #             "overflow": "hidden",
    #             "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
    #         }
    #     ),
    #     style={'maxWidth': '800px', 'margin': 'auto', 'marginTop': '20px'})

    upload_data = html.Div([database_info, upload_month, energy_consumed, graph_value, graph_scale, date_range], style={'border':'5px solid #d6d6d6','border-radius':'10px','padding':'10px'})
    chart_div = html.Div([chart], style={'width':'100%'})

    layout = html.Div([

        html.Div([
            header,
            html.Div(
                dbc.Stack([
                    upload_data, chart_div
                ], gap =3, direction='horizontal'),
                style={'margin-left': 20, 'margin-right': 20, 'border':'5px solid #d6d6d6','border-radius':'10px','padding':'20px'}),
            footer,
            dcc.Store(id='data', data=database.to_json())

        ], style={'display': 'block', 'flexDirection': 'column', 'minHeight': '100vh'})
    ]
    )
    return layout

app.layout = get_layout()

@app.callback(Output('energy_consumed', 'children'),
            Input('date_picker', 'date'),
            prevent_initial_call=True
            )

def energy_consumed_fct(date):

    date = datetime.fromisoformat(date)
    data = read_database()

    filtered_data = data[((data['Date'] > datetime(date.year, date.month, date.day, 0, 0, 0)) & (data['Date'] < datetime(date.year, date.month, date.day, 9, 0, 0))) | ((data['Date'] > datetime(date.year, date.month, date.day, 18, 0, 0)) & (data['Date'] < datetime(date.year, date.month, date.day, 23, 59, 0)))]
    sum = filtered_data['Consumption'].sum()

    return f'Energy consumed out of working time: {round(sum, 1)} KWh'

@app.callback(
            Output('chart', 'figure'),
            Output('database_info', 'children', allow_duplicate=True),
            Input('upload_data', 'contents'),
            State('upload_data', 'filename'),
            State('date_range', 'start_date'),
            State('date_range', 'end_date'),
            State('graph_value', 'value'),
            State('graph_scale', 'value'),
            State('chart', 'figure'),
            prevent_initial_call=True,
            running=[(Output("database_info", "children"), 'Uploading data', 'Upload new data')]
            )

def upload_data(upload_data_contents, upload_data_filename, start_date, end_date, value, scale, figure):
    if upload_data_contents is not None:
        content_type, content_string = upload_data_contents.split(',')
        decoded = base64.b64decode(content_string)

        try:
            if 'xlsx' in upload_data_filename:
                df = pd.read_excel(io.BytesIO(decoded))
            elif 'csv' in upload_data_filename:
                df = pd.read_csv(io.BytesIO(decoded))
            else:
                return no_update, 'There is an error processing this file'

            df.drop(df.index[0:9], axis='index', inplace=True)
            df.drop(df.columns[[2,3,4,6,7,8]], axis='columns', inplace=True)
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format="%d.%m.%Y %H:%M:%S", errors='coerce')

            database = read_database()['Date']

            diff_df = df[~ df.iloc[:, 0].isin(database)].copy()
            common_df = df[df.iloc[:, 0].isin(database)].copy()

            if not common_df.empty:

                tuple = list(common_df.itertuples(index=False, name=None))
                tuple = [item_tuple + (item_dates,) for item_tuple, item_dates in zip(tuple, common_df.iloc[:, 0])]
                sql = "UPDATE consumption_price SET Date = %s, Consumption = %s, Price = %s WHERE Date = %s"
                connection.ping(reconnect=True)
                cursor.executemany(sql, tuple)

            if not diff_df.empty:

                sql = "INSERT INTO consumption_price (Date, Consumption, Price) VALUES (%s, %s, %s)"
                connection.ping(reconnect=True)
                cursor.executemany(sql, list(diff_df.itertuples(index=False, name=None)))
                connection.commit()

        except:
            return no_update, 'There is an error processing this file'

        data = read_database()
        filtered_data = data[(data['Date'] > pd.to_datetime(start_date)) & (data['Date'] < pd.to_datetime(end_date))]

        figure['data'][0]['x'] = filtered_data['Date']
        figure['data'][0]['y'] = filtered_data[value]

        graph_scale_fct(scale, figure, value, filtered_data)

        return figure, 'Data successfully loaded'

@app.callback(Output('chart', 'figure', allow_duplicate=True),
            Output('data', 'data'),
            Input('graph_value', 'value'),
            Input('graph_scale', 'value'),
            Input('date_range', 'start_date'),
            Input('date_range', 'end_date'),
            State('chart', 'figure'),
            State('data', 'data'),
            prevent_initial_call=True
            )

def energy_chart(value, scale, start_date, end_date, figure, data):
    trigger = ctx.triggered_id

    if trigger == 'graph_value':
        figure = graph_consumption_price(value, figure, data)
        return figure, no_update

    elif trigger == 'graph_scale':
        data = read_database()
        df = data[(data['Date'] > pd.to_datetime(start_date)) & (data['Date'] < pd.to_datetime(end_date))]

        figure, data = graph_scale_fct(scale, figure, value, df)
        return figure, data.to_json()

    elif trigger == 'date_range':
        figure, data = date_range_chart(start_date, end_date, figure, value, scale)
        data.reset_index(drop=True, inplace=True)
        return figure, data.to_json()


def graph_consumption_price(value, figure, data):
    data = pd.DataFrame(json.loads(data))

    if value == 'Consumption':
        figure['data'][0]['y'] = data['Consumption']
        figure['data'][0]['hovertemplate'] = "%{x}:<br>Consumption: %{value} KWh</br><extra></extra>"
        figure['layout']['title']['text'] = "EMC lab energy consumption"
        figure['layout']['yaxis']['title']['text'] = "Consumption (kWh)"

    elif value == 'Price':
        figure['data'][0]['y'] = data['Price']
        figure['data'][0]['hovertemplate'] = "%{x}:<br>Price: %{value} €</br><extra></extra>"
        figure['layout']['title']['text'] = "EMC lab energy price"
        figure['layout']['yaxis']['title']['text'] = "Price (€)"

    return figure

def date_range_chart(start_date, end_date, figure, value, scale):
    data = read_database()
    filtered_data = data[(data['Date'] > pd.to_datetime(start_date)) & (data['Date'] < pd.to_datetime(end_date))]

    figure['data'][0]['x'] = filtered_data['Date']
    figure['data'][0]['y'] = filtered_data[value]

    graph_scale_fct(scale, figure, value, filtered_data)

    return figure, filtered_data

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8002)