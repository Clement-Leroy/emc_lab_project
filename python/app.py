import dash
from dash import dcc, ctx, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_auth
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime
from datetime import date
import math
import base64
import pymysql
import time

columnDefs_project_list=[
    {"headerName": "",
     "field": "Show",
     "cellRenderer": "Button",
     "cellRendererParams": {'className': "block text-center text-md text-white rounded no-underline cursor-pointer hover:bg-blue-600"},
     'width': 70, 'pinned': 'left',
     'cellStyle': {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 'sortable': False},
    {"headerName":"Start Date","field": "Start Date", 'flex':1, 'filter': 'agDateColumnFilter', "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals", "Before","After","Between"], "debounceMs": 500}},
    {"headerName":"End Date","field": "End Date", 'flex':1, 'filter': 'agDateColumnFilter', "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals", "Before","After","Between"], "debounceMs": 500}},
    {"headerName":"Location","field": "Location", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Number","field": "Number", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Project","field": "Project", 'width':350, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"PM","field": "PM", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Category","field": "Category", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Type","field": "Typ", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Client","field": "Client", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"PL","field": "PL", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Hours","field": "Work [hours]", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    ]

columnDefs_project = [
    {"headerName":"", "checkboxSelection": True, 'width': 45, 'pinned': 'left', 'sortable': False},
    {"headerName":"Test Service","field": "Test_Service", 'flex':1, "editable": True, "cellEditor": "agSelectCellEditor", "cellEditorParams": {"values": ["EMC-BCI", "EMC-CE", "EMC-CI", "EMC-DOC", "EMC-ESD", "EMC-IC1", "EMC-IC2", "EMC-RE1", "EMC-RE2", "EMC-RI", "EMC-SET", "EMC-SW", "EMC-PRO"]}},
    {"headerName":"Tester","field": "Tester", 'flex':1, "editable": True, "cellEditor": "agSelectCellEditor", "cellEditorParams": {"values": ["Jan", "Philipp", "Rolf", "Lukas", "Clement"]}},
    {"headerName":"Location","field": "Location", 'flex':1, "editable": True, "cellEditor": "agSelectCellEditor", "cellEditorParams": {"values": ["ALSE", "SAC 3", "SK", "Pulses", "ESD", "Office"]}},
    {"headerName":"Start Date","field": "Start_Date", 'flex':1, "editable": True, "cellEditor": "agDateStringCellEditor"},
    {"headerName":"Stop Date","field": "Stop_Date", 'flex':1, "editable": True, "cellEditor": "agDateStringCellEditor"},
    {"headerName":"Hours","field": "Hours", 'flex':1, "editable": True, "cellDataType": 'number'},
    {"headerName":"Status","field": "Status", 'flex':1, "editable": False}
]

project_table = html.Div(dag.AgGrid(
            id="project_table",
            columnDefs=columnDefs_project,
            rowData=[],
            defaultColDef={"cellDataType": False},
            dashGridOptions = {'singleClickEdit':True, 'suppressRowTransform': True, "rowSelection": "multiple"},
            style = {'margin-bottom':10}
        ))

connection = pymysql.connect(
       host='localhost',
       port=3306,
       user='root',
       password="root",
       db='emc_lab_project',
       cursorclass=pymysql.cursors.DictCursor,
        connect_timeout = 30,
        read_timeout = 60,
        write_timeout = 60
   )

def read_database(table):
    cursor = connection.cursor()

    if table == "project_tracker":
        cursor.execute("SELECT * FROM emc_lab_project.project_tracker ORDER BY Number ASC")
        project_tracker = cursor.fetchall()
        project_tracker = pd.DataFrame(project_tracker)
        project_tracker['Start Date'] = pd.to_datetime(project_tracker['Start Date'])
        project_tracker['End Date'] = pd.to_datetime(project_tracker['End Date'])
        data = project_tracker

    elif table == "project_description":
        cursor.execute("SELECT * FROM emc_lab_project.project_description ORDER BY Number ASC")
        project_description = cursor.fetchall()
        project_description = pd.DataFrame(project_description).sort_values('Number')
        data = project_description

    return data

check = html.Img(src="https://cdn-icons-png.flaticon.com/512/5610/5610944.png",style={'height': '20px','width':'20px'})
cross = html.Img(src="https://cdn-icons-png.flaticon.com/512/10100/10100000.png",style={'height': '20px','width':'20px'})

USERNAME_PASSWORD_PAIRS = [['username','password']]

external_scripts = ["https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.1/jquery.min.js",
                    "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js",
                    'https://trentrichardson.com/examples/timepicker/jquery-ui-timepicker-addon.js']

external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://code.jquery.com/ui/1.13.3/themes/base/jquery-ui.css']

app = dash.Dash(__name__, include_assets_files=True, external_scripts=external_scripts, external_stylesheets=external_stylesheets)
app.secret_key = 'super secret key'
app.title = "MPS | EMC Project Tracker"
app._favicon = ("icon_MPS.ico")
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server
server.config.update(SECRET_KEY="SECRET_KEY")

project_list_btn=dbc.Stack([
                html.Div(html.Button('Add project',id='add_project',n_clicks=0,style={'width':'150px','borderRadius':'5px'})),
                html.Div(html.Button('Save backup',id='save_backup',n_clicks=0,style={'width':'150px','borderRadius':'5px'})),
                dcc.Download(id="download_backup"),
                dcc.Upload(id='upload-backup', children=html.Div(html.Button('Load backup',id='load_backup',n_clicks=0,style={'width':'150px','borderRadius':'5px'}))),
                html.Div(dbc.Button(id='loading-screen', children=['No action selected'],disabled=True, style = {'width':'270px', 'borderRadius':'5px', 'border':'none','align-items':'center', 'font-weight':'bold', 'backgroundColor':'#119DFF'})),
            ],direction="horizontal",gap=3,style={'margin-left':'30px','margin-bottom':'20px','align-items':'center'})


start_date_input = html.Div(dbc.Stack([html.Label('Start Date', style={'fontWeight':'bold'}), dcc.DatePickerSingle(id="start_date_input",style={'width':150})]))
stop_date_input = html.Div(dbc.Stack([html.Label('Stop Date', style={'fontWeight':'bold'}), dcc.DatePickerSingle(id="stop_date_input",style={'width':150})]))
project_input = html.Div(dbc.Stack([html.Label('Project', style={'fontWeight':'bold'}), dcc.Input(id="project_input", value='', style={'width':150, "height": 35})]))
location_input = html.Div(dbc.Stack([html.Label('Location', style={'fontWeight':'bold'}), dcc.Input(id="location_input",style={'width':150, "height": 35})]))
project_manager_input = html.Div(dbc.Stack([html.Label('Project manager', style={'fontWeight':'bold'}), dcc.Dropdown(['JS','PS','RG','LK','CL'],id="project_manager_input",style={'width':150, "height": 35})]))
category_input = html.Div(dbc.Stack([html.Label('Category', style={'fontWeight':'bold'}), dcc.Dropdown(['Internal', 'External'],id="category_input",style={'width':150, "height": 35})]))
type_input = html.Div(dbc.Stack([html.Label('Type', style={'fontWeight':'bold'}), dcc.Dropdown(['Paid','Non Paid'],id="type_input",style={'width':150, "height": 35})]))
client_input = html.Div(dbc.Stack([html.Label('Client', style={'fontWeight':'bold'}), dcc.Dropdown(['EXT','FAE / Sales', 'AE / PL'],id="client_input",style={'width':150, "height": 35})]))
PL_input = html.Div(dbc.Stack([html.Label('PL', style={'fontWeight':'bold'}), dcc.Dropdown(['Automotive','AC/DC - Lighting','STD DC/DC','Telecom and Computing','Analog','Sensor','Sensor','Power Magnetics','ADC','Automotive BMS','Axign','EMC','EXT','Other'],id="PL_input",style={'width':150, "height": 35})]))
contact_input = html.Div(dbc.Stack([html.Label('Contact', style={'fontWeight':'bold'}), dcc.Input(id="contact_input",style={'width':250, "height": 35})]))
quote_input = html.Div(dbc.Stack([html.Label('Quote', style={'fontWeight':'bold'}), dcc.Input(id="quote_input", readOnly=True,style={'width':150, "height": 35})]))
quote2_input = html.Div(dbc.Stack([html.Label('Quote2', style={'fontWeight':'bold'}), dcc.Input(id="Quote2",style={'width':150, "height": 35})]))
PO_input = html.Div(dbc.Stack([html.Label('PO', style={'fontWeight':'bold'}), dcc.Input(id="PO_input",style={'width':150, "height": 35})]))
draft_input = html.Div(dbc.Stack([html.Label('Draft', style={'fontWeight':'bold'}), dcc.Input(id="draft_input",style={'width':150, "height": 35})]))
report_input = html.Div(dbc.Stack([html.Label('Report', style={'fontWeight':'bold'}), dcc.Input(id="report_input",style={'width':150, "height": 35})]))
time_input = html.Div(dbc.Stack([html.Label('Time[H]', style={'fontWeight':'bold', 'margin-right':5}), dcc.Input(id="time_input", type='number', readOnly=True, style={'width':60, "height": 35, 'text-align': 'center'})], direction= 'horizontal', style={'margin-left': 320}))
invoice_input = html.Div(dbc.Stack([html.Label('Invoice', style={'fontWeight':'bold'}), dcc.Input(id="invoice_input",style={'width':150, "height": 35})]))
notes_input = html.Div(dbc.Stack([html.Label('Notes', style={'fontWeight':'bold'}), dcc.Input(id="notes_input",style={'width':250, "height": 35})]))

ok_project_btn = html.Div(html.Button('OK', id='ok_project_btn', n_clicks=0, style={'width':100}))
cancel_btn = html.Div(html.Button('Cancel', id='cancel_btn', n_clicks=0, style={'width':100}))

project_window = html.Div([
                                html.Div(html.Label('Add new project', style={'fontWeight':'bold', 'fontSize':20, 'margin-left':10})),
                                dbc.Stack([project_input, location_input, project_manager_input, start_date_input, stop_date_input], direction='horizontal',gap=3, style={'margin-bottom':10}),
                                dbc.Stack([category_input, type_input, client_input, PL_input], direction='horizontal',gap=3, style={'margin-bottom':10}),
                                dbc.Stack([ok_project_btn, cancel_btn], direction='horizontal',gap=1)],
                                id='project_window',style={'width':850,'display':'none','position':'fixed','top':'40%','left':'35%','backgroundColor':"#e0e0e0",'padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'2002','borderRadius':'8px','overflow':'auto'})

yes_remove_btn = html.Div(html.Button('Confirm', id='yes_remove_btn', n_clicks=0, style={'width':90}))
no_remove_btn =  html.Div(html.Button('Cancel', id='no_remove_btn', n_clicks=0, style={'width':90}))

encoded_image = base64.b64encode(open("assets/warning.png", 'rb').read())

remove_window = html.Div([
    dbc.Row([
    dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'width':100})), width='auto'),
    dbc.Col([
            html.Label('Are you sure to remove definitively this project ?', style={'fontWeight':'bold', 'margin-bottom':5}),
            dbc.Stack([yes_remove_btn, no_remove_btn], direction='horizontal',gap=2)], align='center', width='auto'),
    ])
    ], id='remove_window',style={'display':'none','position':'fixed','top':'60%','left':'40%','backgroundColor':"#e0e0e0",'padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'2003','borderRadius':'8px'})


project_description_label = html.Label(id='project_description_label', style={'fontWeight':'bold', 'fontSize':20})
add_test_service_btn = html.Button('+ Add Test Service', id='add_test_service_btn', n_clicks=0,style={'width':170, 'margin-right': 10})
remove_test_service_btn = html.Button('- Remove Test Service', id='remove_test_service_btn', n_clicks=0,style={'width':170})

project_input = html.Div(dbc.Stack([html.Label('Project', style={'fontWeight':'bold'}), dcc.Input(id="project_description_input",style={'width':150, "height": 35})]))
location_input = html.Div(dbc.Stack([html.Label('Location', style={'fontWeight':'bold'}), dcc.Input(id="location_description_input",style={'width':150, "height": 35})]))
project_manager_input = html.Div(dbc.Stack([html.Label('Project manager', style={'fontWeight':'bold'}), dcc.Dropdown(['JS','PS','RG','LK','CL'],id="project_manager_description_input",style={'width':150})]))
category_input = html.Div(dbc.Stack([html.Label('Category', style={'fontWeight':'bold'}), dcc.Dropdown(['Internal', 'External'],id="category_description_input",style={'width':150})]))
type_input = html.Div(dbc.Stack([html.Label('Type', style={'fontWeight':'bold'}), dcc.Dropdown(['Paid','Non Paid'],id="type_description_input",style={'width':150})]))
client_input = html.Div(dbc.Stack([html.Label('Client', style={'fontWeight':'bold'}), dcc.Dropdown(['EXT','FAE / Sales', 'AE / PL'],id="client_description_input",style={'width':150})]))
PL_input = html.Div(dbc.Stack([html.Label('PL', style={'fontWeight':'bold'}), dcc.Dropdown(['Automotive','AC/DC - Lighting','STD DC/DC','Telecom and Computing','Analog','Sensor','Sensor','Power Magnetics','ADC','Automotive BMS','Axign','EMC','EXT','Other'],id="PL_description_input",style={'width':150})]))

start_date_input = html.Div(dbc.Stack([html.Label('Start Date', style={'fontWeight':'bold'}), dcc.DatePickerSingle(id="start_date_description_input",style={'width':150})]))
stop_date_input = html.Div(dbc.Stack([html.Label('Stop Date', style={'fontWeight':'bold'}), dcc.DatePickerSingle(id="stop_date_description_input",style={'width':150})]))

ok_project_description_btn = html.Button('Update', id='close_project_description_btn', n_clicks=0,style={'width':150,'borderRadius':'5px', 'margin-right': 10})
cancel_project_description_btn = html.Div(html.Button('Cancel',id='cancel_project_description_btn',n_clicks=0,style={'width':'150px','borderRadius':'5px', 'margin-right': 10}))
remove_project_btn = html.Div(html.Button('Remove project',id='remove_project',n_clicks=0,style={'width':'150px','borderRadius':'5px'}))

project_description = html.Div([
                    dbc.Stack([project_description_label], direction='horizontal', style={'margin-bottom':10, 'margin-left':10}),
                    dbc.Stack([project_input, location_input, project_manager_input, start_date_input, stop_date_input], direction='horizontal',gap=3, style={'margin-bottom':10}),
                    dbc.Stack([category_input, type_input, client_input, PL_input, PO_input], direction='horizontal',gap=3, style={'margin-bottom':10}),
                    dbc.Stack([quote_input, quote2_input, draft_input,report_input, invoice_input, contact_input], direction='horizontal',gap=3, style={'margin-bottom':10}),
                    dbc.Stack([add_test_service_btn, remove_test_service_btn], direction='horizontal'),
                    project_table,
                    dbc.Stack([ok_project_description_btn, cancel_project_description_btn, remove_project_btn, time_input], direction='horizontal',gap=1),
                                ],
                              id='project_description', style={'width':1100,'display':'none','position':'fixed','top':'25%','left':'30%','backgroundColor':"#e0e0e0",'padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'2002','borderRadius':'8px','overflow':'auto'}
)

def lab_member_list_fct(project_data):
    project_data = project_data.to_dict('records')
    lab_member_list = {}
    for project in project_data:
        PM = project['PM']
        if PM not in list(lab_member_list.keys()):
            lab_member_list[PM] = [project]
        else:
            lab_member_list[PM].append(project)
    return lab_member_list

def create_project_timeline(lab_member_list):
    project_timeline_data_list = []
    row = 0
    ticktext = []
    tickvals = []
    for member, projects in lab_member_list.items():
        ticktext.append(member)
        val = ((len(projects)*0.1 + row) - row)/2 + row
        tickvals.append(val)

        for project in projects:
            if project['PM'] is not None:
                current_date = datetime.date.today()
                start = pd.to_datetime(project['Start Date'], format='%Y-%m-%d').date()
                end = pd.to_datetime(project['End Date'], format='%Y-%m-%d').date()
                if start == end:
                    end = end + datetime.timedelta(days=1)

                if start <= current_date <= end:
                    status = 'in progress'
                elif start < current_date:
                    status = 'completed'
                else:
                    status = 'upcoming'

                project_timeline_data = {
                    "Task": member,
                    "Start": start,
                    "Finish": end,
                    "Project": project["Project"],
                    "Status": status,
                    "Row": row
                }
                project_timeline_data_list.append(project_timeline_data)

                row = row + 0.1

        row = row + 0.1

    project_timeline_data_list = pd.DataFrame(project_timeline_data_list)
    project_timeline_figure = px.timeline(project_timeline_data_list, x_start='Start', x_end="Finish", y='Row',
                                          text='Project', color="Status", color_discrete_map=color_map, custom_data=[project_timeline_data_list['Start'].apply(lambda x: x.strftime("%B %d, %Y")), project_timeline_data_list['Finish'].apply(lambda x: x.strftime("%B %d, %Y")), project_timeline_data_list['Task'], project_timeline_data_list['Status']])

    project_timeline_figure.update_traces(width=0.09, marker=dict(cornerradius=30), insidetextanchor="middle", insidetextfont=dict(weight="bold"),
        hovertemplate="<b>Project: %{text}<br>PM: %{customdata[2]}<br>Status: %{customdata[3]}<br>Start Date: %{customdata[0]}<br>Stop Date: %{customdata[1]}<extra></extra>"
    )
    project_timeline_figure.update_yaxes(tickvals=tickvals, ticktext=ticktext)
    project_timeline_figure.update_layout(plot_bgcolor='white', title=dict(text="Personnel Timeline", font=dict(size=25, weight='bold'), xanchor="left", x=0.44), margin={'t':50,'b':0,'r':0,'l':0}, xaxis_title='', yaxis_title='', showlegend=False, xaxis={'tickfont': dict(size=16), 'range': [date(date.today().year,1,1), date(date.today().year+1, 1, 1),]}, yaxis={'fixedrange': True, 'tickfont':dict(size=16), 'range': [-0.1, project_timeline_data_list.iloc[-1]['Row'] + 0.1]})

    project_timeline_figure.add_trace(go.Scatter(
        x=[datetime.date.today(), datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1),
           datetime.date.today() + datetime.timedelta(days=1)],
        y=[-0.1, project_timeline_data_list.iloc[-1]['Row'] + 0.1, project_timeline_data_list.iloc[-1]['Row'] + 0.1, -0.1],
        name='<b>Current Date</b>', showlegend=False,
        visible=True, fill="toself",
        mode='text', fillcolor='blue', opacity=0.3, hoverinfo='text'))

    return project_timeline_figure

color_map = {
    "completed": "green",
    "in progress": "yellow",
    "upcoming": "blue"
}

start_stop_date_timeline_input = html.Div([html.Label('Start → End Dates', style={'fontWeight':'bold'}),
                                    dcc.DatePickerRange(
                                    id='start_stop_date_timeline_input',
                                    start_date=date(date.today().year,1,1),
                                    end_date=date(date.today().year+1, 1, 1),
                                    style={'width':287}
                                    )])

timeline_checklist = html.Div([
    html.Label('Personnel List', style={'fontWeight':'bold', 'margin-left':'15px'}),
    dcc.Checklist(
        ['Philipp Schroer', 'Rolf Giessler', 'Jan Spindler', 'Clement Leroy', 'Lukas Kurz'],
        ['Philipp Schroer', 'Rolf Giessler', 'Jan Spindler', 'Clement Leroy', 'Lukas Kurz'],
        id='timeline_checklist',
        inputStyle={"margin-right": "10px", "margin-bottom": "10px"}
    )])

timeline_parameters = html.Div([
    html.Label('Timeline Parameters', style={'margin-bottom':'10px','fontWeight':'bold', 'fontSize':20}),
    dbc.Stack([start_stop_date_timeline_input, timeline_checklist], gap=2
    )], style={'border':'5px solid #d6d6d6','border-radius':'10px','padding':'10px', 'width':317})

project_timeline = dcc.Loading(dcc.Graph(id='project_timeline',
                            figure= create_project_timeline(lab_member_list_fct(read_database("project_tracker"))),
                            config={'toImageButtonOptions': {'filename':'Lab_member_timeline'}, 'responsive':True, 'displaylogo':False, 'modeBarButtonsToRemove': ['zoom', 'pan','zoomin','zoomout','autoscale','resetscale','lasso2d', 'select2d']},
                            style={'margin-left':'10px','width':'2130px','height': '1060px','fontWeight':'bold'}),
                            overlay_style={"visibility":"unvisible", "filter": "blur(2px)"},type="circle")

timeline_graph = html.Div([
                    dbc.Stack([timeline_parameters, project_timeline], direction='horizontal')],
                    style={'border':'5px solid #d6d6d6','border-radius':'10px','padding':'20px'})

def create_chart_figure(type, label_1, label_2, value, start_date, end_date):
    value = 'Work [hours]' if value == 'Working time' else value
    project_data = read_database("project_tracker")
    project_data = project_data[((start_date <= project_data['Start Date']) & (project_data['Start Date'] <= end_date)) | ((start_date <= project_data['End Date']) & (project_data['End Date'] <= end_date)) | ((project_data['Start Date'] <= start_date) & (project_data['End Date'] <= end_date)) | ((project_data['Start Date'] >= start_date) & (project_data['End Date'] >= end_date))]
    project_data = project_data.to_dict('records')

    label_value = {}
    for project in project_data:
        label_value_label_1 = project[label_1]
        label_value_label_2 = project[label_2] if label_2 is not None else None
        if value == 'Project' and label_value_label_1 is not None and project[label_1] is not None or value == 'Work [hours]' and not math.isnan(project[value]) and label_value_label_1 is not None and project[value] != 0:
            if project[label_1] not in list(label_value.keys()) or label_2 is not None and project[label_2] not in list(label_value[label_value_label_1].keys()):
                if label_2 is not None :
                    if project[label_1] not in list(label_value.keys()):
                        label_value[label_value_label_1] = {}
                    if label_value_label_2 not in list(label_value[label_value_label_1].keys()):
                        label_value[label_value_label_1].update({label_value_label_2:[project[value]]})
                    else:
                        label_value[label_value_label_1][label_value_label_2] = label_value[label_value_label_1][label_value_label_2] + [project[value]]
                else:
                    label_value[label_value_label_1] = [project[value]]
            else:
                if label_value_label_2 is not None:
                    label_value[label_value_label_1][label_value_label_2] = label_value[label_value_label_1][label_value_label_2] + [project[value]]
                else:
                    label_value[label_value_label_1] = label_value[label_value_label_1] + [project[value]]


    if type == 'Pie chart':
        if label_2 is None:

            labels = list(label_value.keys())

            values = []
            if value == 'Project':
                for label_value_value in label_value.values():
                    values.append(len(label_value_value))
            else:
                for label_value_value in label_value.values():
                    values.append(sum(label_value_value))

            hovertemplate = "%{label}: <br>%{value} Hours</br>%{percent}<extra></extra>" if value == 'Work [hours]' else "%{label}: <br>%{value} Projects</br>%{percent}<extra></extra>"
            figure = go.Figure(data=[go.Pie(labels=labels, values=values, hovertemplate = hovertemplate, marker=dict(line=dict(width=2)))],
                               layout=go.Layout(
                                   title=dict(text=f"{'Work time' if value == 'Work [hours]' else value} per {label_1}{'-' + label_2 if label_2 is not None else ''}", font=dict(size=25, weight='bold'), xanchor="left", x=0.6),
                                   hovermode='closest',
                                   showlegend=True,
                                   margin={"t": 50, "b": 0, 'r': 0, 'l': 0},
                                   uniformtext={
                                       "mode": "hide",
                                       "minsize": 16
                                   },
                                   hoverlabel={
                                       'font': {
                                           'size': 16,
                                       }},
                                   legend=dict(
                                       font=dict(size=16),
                                       yanchor="top",
                                       y=0.99,
                                       xanchor="left",
                                       x=0.8,
                                       bgcolor=None),

                               ))
        else:
            ids = []
            labels = []
            parents = []
            values = []
            for key_parent, value_parent in label_value.items():
                ids.append(key_parent)
                labels.append(key_parent)
                parents.append("")
                values.append(0)
                value_nb = 0
                for key_2, value_2 in label_value[key_parent].items():
                    ids.append(f"{key_parent} - {key_2}")
                    labels.append(key_2)
                    parents.append(key_parent)
                    values.append(len(value_2) if value == 'Project' else sum(value_2))
                    value_nb = value_nb + len(value_2) if value == 'Project' else value_nb + sum(value_2)
                for i, n in enumerate(values):
                    if n == 0:
                        values[i] = value_nb

            hovertemplate = "%{label}: <br>%{value} Hours</br><extra></extra>" if value == 'Work [hours]' else "%{label}: <br>%{value} Projects</br><extra></extra>"
            figure = go.Figure(go.Sunburst(
                        ids=ids,
                        labels=labels,
                        parents=parents,
                        values=values,
                        branchvalues="total", hovertemplate = hovertemplate, marker=dict(line=dict(width=2, color='black'))),
                        layout=go.Layout(
                       title=dict(text=f"{'Work time' if value == 'Work [hours]' else value} per {label_1}{'-' + label_2 if label_2 is not None else ''}", font=dict(size=25, weight='bold'), xanchor="left", x=0.6),
                       hovermode='closest',
                       showlegend=True,
                       margin={"t": 50, "b": 0, 'r': 0, 'l': 0},
                        uniformtext={
                            "mode": "hide",
                            "minsize": 16
                        },
                        hoverlabel={
                            'font': {
                                'size': 16,
                            }},
                       legend=dict(
                           font=dict(size=16),
                           yanchor="top",
                           y=0.99,
                           xanchor="left",
                           x=0.8,
                           bgcolor=None,
                       ))
                   )

    else:

        if label_2 is None:
            labels = list(label_value.keys())

            values = []
            if value == 'Project':
                for label_value_value in label_value.values():
                    values.append(len(label_value_value))
            else:
                for label_value_value in label_value.values():
                    values.append(sum(label_value_value))


            sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
            sorted_labels, sorted_values = zip(*sorted_data)

            hovertemplate = "%{label}: <br>%{value} Hours</br><extra></extra>" if value == 'Work [hours]' else "%{label}: <br>%{value} Projects</br><extra></extra>"
            traces = []
            for label_value, value_value in zip(sorted_labels, sorted_values):
                traces.append(go.Bar(name=label_value, x=[label_value], y=[value_value], text=value_value, hovertemplate=hovertemplate, texttemplate='%{text:.2s}', textposition='outside'))

        else:
            traces = []
            labels = []
            values = {}
            for key_parent, value_parent in label_value.items():
                labels.append(key_parent)
                for key_2, value_2 in label_value[key_parent].items():
                    if key_2 not in list(values.keys()):
                        values[key_2] = []
                    values[key_2].append((key_parent, len(value_2) if value == 'Project' else sum(value_2)))

            df = pd.DataFrame({
            'label': list(label_value.keys())
            })

            for key, val in values.items():
                y = []
                i=0
                for index, label in enumerate(labels):
                    try:
                        if val[index - i][0] == label:
                            y.append(val[index - i][1])
                        else:
                            y.append(0)
                            i=i+1
                    except:
                        y.append(0)

                df[key] = y

            df['sum'] = df.iloc[:, 1:].sum(axis=1)
            df = df.sort_values(by='sum', ascending=False)

            for column_name, column_series in df.iloc[:, 1:-1].items():
                hovertemplate = column_name + ": <br>%{value} Hours</br><extra></extra>" if value == 'Work [hours]' else column_name + ": <br>%{value} Projects</br><extra></extra>"
                traces.append(go.Bar(name=column_name, x=df['label'], y=column_series, text=column_series,
                                     hovertemplate=hovertemplate, texttemplate='%{text:.2s}', textposition='inside',
                ))

        figure = go.Figure(
                            data=traces,
                            layout=go.Layout(
                                title=dict(text=f"{'Work time' if value == 'Work [hours]' else value} per {label_1}{'-' + label_2 if label_2 is not None else ''}",
                                           font=dict(size=25, weight='bold'), xanchor="center"),
                                barcornerradius=15,
                                hovermode='closest',
                                barmode='stack',
                                showlegend=True,
                                plot_bgcolor='white',
                                xaxis={'tickfont':dict(size=16)},
                                yaxis={'gridcolor':'lightgrey', 'tickfont':dict(size=16)},
                                uniformtext= {
                                        "mode": "hide",
                                        "minsize": 16
                                },
                                hoverlabel= {
                                        'font': {
                                            'size': 16,
                                        }},
                                margin={"t": 50, "b": 0, 'r': 0, 'l': 0},
                                legend=dict(
                                    font=dict(size=16),
                                    yanchor="top",
                                    y=0.99,
                                    xanchor="left",
                                    x=1,
                                    bgcolor=None,
                                )
                            ))

    return figure

chart = dcc.Graph(
                id='chart',
                figure= create_chart_figure('Pie chart', 'PM', None, 'Project', datetime.datetime(date.today().year,1,1), datetime.datetime(date.today().year+1,1,1)),
                config={'toImageButtonOptions': {'filename':'typ_graph'}, 'responsive':True, 'displaylogo':False, 'modeBarButtonsToRemove': ['zoom', 'pan','zoomin','zoomout','autoscale','resetscale','lasso2d', 'select2d']},
                style={'height': '1062px','width':'2200px','fontWeight':'bold'})



type_chart = html.Div([html.Label('Pie or bar chart', style={'fontWeight':'bold', 'margin-left':'15px'}),
                    dcc.Dropdown(['Pie chart', 'Bar chart'],id="type_chart_input", value='Pie chart', clearable=False, style={'width':287})],)

chart_label_1 = html.Div([html.Label('Label 1', style={'fontWeight':'bold', 'margin-left':'15px'}),
                    dcc.Dropdown(['Project', 'PM', 'Category', 'Typ', 'Client', 'PL'],id="label_chart_input_1", value='PM', clearable=False, style={'width':287})],)

chart_label_2 = html.Div([html.Label('Label 2', style={'fontWeight':'bold', 'margin-left':'15px'}),
                    dcc.Dropdown(['Project', 'PM', 'Category', 'Typ', 'Client', 'PL'],id="label_chart_input_2", value=None, clearable=True, style={'width':287})],)

chart_value = html.Div([html.Label('Value', style={'fontWeight':'bold', 'margin-left':'15px'}),
                    dcc.Dropdown(['Project', 'Working time'],id="value_chart_input", value='Project', clearable=False, style={'width':287})])


chart_date = html.Div([
    html.Label('Start → End Dates', style={'fontWeight':'bold', 'margin-left':'15px'}),
    dcc.DatePickerRange(
        id='chart_date',
        start_date=date(date.today().year,1,1),
        end_date=date(date.today().year+1, 1, 1),
        style={'width':287}
    )])

chart_parameters = html.Div([html.Label('Chart parameters', style={'margin-bottom':'10px','fontWeight':'bold','fontSize':'20px'}),
                    dbc.Stack([type_chart, chart_label_1, chart_label_2, chart_value, chart_date],gap=2)],
                    style={'border':'5px solid #d6d6d6','border-radius':'10px','padding':'10px', 'width':317, 'margin-right':'10px'})

chart_graph = html.Div([
                    dbc.Stack([chart_parameters, chart], direction='horizontal')],
                    style={'border':'5px solid #d6d6d6','border-radius':'10px','padding':'20px'})

menu_btn = html.Div([
                html.Button("Project List", id="btn-project-list", style = {'width': 150, 'height':45,'fontWeight':'bold', "color":"white", "background-color": "#1c4efe"}, className='active_menu_btn'),
                html.Button("Timeline", id="btn-staff-timeline", style = {'width': 150, 'height':45,'fontWeight':'bold', "color":"white", "background-color": "#1c4efe"}, className='menu_btn'),
                html.Button("Graphs", id="btn_graph_report", style = {'width': 150, 'height':45,'fontWeight':'bold', "color":"white", "background-color": "#1c4efe"}, className='menu_btn'),
    ], style={'display': 'flex', 'margin-bottom':-10, 'align-items': 'end', 'margin-left':-800} )

# Header
logo=html.Img(src="https://community.element14.com/e14/assets/main/mfg-group-assets/monolithicpowersystemsLogo.png",style={'height': '50px','margin-right':'10px'})
title=html.H1("EMC Lab Project Management",style={'font-size':50,'font-weight':'bold'})
location=html.H1("EMC Lab Ettenheim",style={'font-size':50,'font-weight':'bold'})
header = html.Div([
            html.Div([
                logo
            ], style={'display': 'flex', 'align-items': 'center'}),
            menu_btn,
            title
        ], style={'display': 'flex', 'justify-content': 'space-between', 'padding': '10px 20px', 'background-color': '#1E2A38', 'color': 'white', 'margin-bottom': '20px', "z-index": "1001"})

# Footer
footer=html.Footer([html.P('Copyright © 2025 Monolithic Power Systems, Inc. All rights reserved.',style={'text-align':'center','color':'#666'})],style={'position':'relative','bottom':'0','width':'100%','padding':'20px 0px','background-color':'#e0e0e0','text-align':'center','margin-top':'20px',"z-index": "1000",})
# Main layout
def get_layout():
    rowData = read_database("project_tracker")
    project_list = ['>>' for i in rowData.values]
    project_list = pd.Series(project_list)
    rowData['Show'] = project_list.values
    rowData['Start Date'] = pd.to_datetime(rowData['Start Date']).dt.strftime("%d/%m/%Y")
    rowData['End Date'] = pd.to_datetime(rowData['End Date']).dt.strftime("%d/%m/%Y")
    project_list = dag.AgGrid(
        id="project_list_table",
        rowData=rowData.to_dict('records'),
        columnDefs=columnDefs_project_list,
        defaultColDef={'resizable': True},
        style={'width': '100%', 'center': True},
        dashGridOptions={"domLayout": "autoHeight"},
        dangerously_allow_code=True,)

    layout = html.Div([

        html.Div([
            dcc.Store(id='project_number', data=None),
            header,
            html.Div(
                [project_list_btn, project_list, project_description, project_window, remove_window], id='project_list_tab',
                style={'display': 'block', 'margin-left': 20, 'margin-right': 20}),
            html.Div(
                [timeline_graph], id='project_timeline_tab',
                style={'display': 'none', 'margin-left': 20, 'margin-right': 20}),
            html.Div(
                [chart_graph], id='graph_tab',
                style={'display': 'none', 'margin-left': 20, 'margin-right': 20}),
            footer,

        ], style={'display': 'block', 'flexDirection': 'column', 'minHeight': '100vh'})
    ]
    )
    return layout

app.layout = get_layout

@app.callback(Output('project_description', 'style'),
    Output('project_description_label', 'children'),
    Output("project_list_table", 'rowData'),
    Output("project_table", 'rowData', allow_duplicate=True),

    Output("start_date_description_input", 'date'),
    Output("stop_date_description_input", 'date'),
    Output("project_description_input", 'value'),
    Output("location_description_input", 'value'),
    Output("project_manager_description_input", 'value'),
    Output("category_description_input", 'value'),
    Output("type_description_input", 'value'),
    Output("client_description_input", 'value'),
    Output("PL_description_input", 'value'),
    Output("contact_input", 'value'),
    Output("quote_input", 'value'),
    Output("Quote2", 'value'),
    Output("PO_input", 'value'),
    Output("draft_input", 'value'),
    Output("report_input", 'value'),
    Output("time_input", 'value'),
    Output("invoice_input", 'value'),
    Output("project_number", 'data'),

    Output("loading-screen", 'children'),
    Output("loading-screen", 'style'),

    Input("project_list_table", "cellRendererData"),
    Input("close_project_description_btn", "n_clicks"),
    Input("add_test_service_btn", "n_clicks"),
    Input("remove_test_service_btn", "n_clicks"),
    Input('cancel_project_description_btn', "n_clicks"),

    Input("project_table", 'cellValueChanged'),

    Input("type_description_input", 'value'),
    Input("client_description_input", 'value'),

    State('project_description', 'style'),
    State("project_list_table", 'rowData'),
    State("project_table", 'rowData'),

    State("start_date_description_input", 'date'),
    State("stop_date_description_input", 'date'),
    State("project_description_input", 'value'),
    State("location_description_input", 'value'),
    State("project_manager_description_input", 'value'),
    State("category_description_input", 'value'),
    State("PL_description_input", 'value'),
    State("contact_input", 'value'),
    State("quote_input", 'value'),
    State("Quote2", 'value'),
    State("PO_input", 'value'),
    State("draft_input", 'value'),
    State("report_input", 'value'),
    State("time_input", 'value'),
    State("invoice_input", 'value'),

    State("loading-screen", 'children'),
    State("loading-screen", 'style'),
    State("project_number", 'data'),

    prevent_initial_call=True
              )

def show_project(project_btn, ok_project_description_btn, add_test_service_btn, remove_test_service_btn, cancel_project_description_btn, project_table_cellValueChanged, type_input, client_input, project_description_style, project_list_table_rowData, project_table_rowData, start_date_input, stop_date_input,  project_input, location_input, project_manager_input, category_input, PL_input, contact_input, quote_input, quote2_input, PO_input, draft_input, report_input, time_input, invoice_input, loading_screen_children, loading_screen_style, project_number):
    project_description_label_children = no_update
    triggered_id = ctx.triggered_id

    if triggered_id == 'project_list_table' and project_description_style['display'] == 'none':
        data_project_tracker = read_database("project_tracker")
        data_project_description = read_database("project_description")

        selectedRow = data_project_tracker.iloc[int(project_btn['rowId'])]
        start_date_input, stop_date_input = selectedRow["Start Date"], selectedRow["End Date"]
        project_number = project_list_table_rowData[int(project_btn['rowId'])]['Number']
        project_input = selectedRow["Project"]
        location_input = selectedRow["Location"]
        project_manager_input = selectedRow["PM"]
        category_input = selectedRow["Category"]
        type_input = selectedRow["Typ"]
        client_input = selectedRow["Client"]
        PL_input = selectedRow["PL"]
        contact_input = selectedRow["Contact"]
        quote_input = selectedRow["Quote"]
        quote2_input = selectedRow["Quote2"]
        PO_input = selectedRow["Quote2"]
        draft_input = selectedRow["DRAFT"]
        report_input = selectedRow["Report"]
        invoice_input = selectedRow["Invoice"]

        project_description_label_children = "Project: " + project_list_table_rowData[int(project_btn['rowId'])]['Project'] if project_list_table_rowData[int(project_btn['rowId'])]['Project'] is not None else ''
        data_project_description = data_project_description[data_project_description['Number'] == project_number]
        data_project_description['Start Date'] = pd.to_datetime(data_project_description['Start Date']).dt.strftime("%Y/%m/%d")
        data_project_description['End Date'] = pd.to_datetime(data_project_description['End Date']).dt.strftime("%Y/%m/%d")
        data_project_description = data_project_description.to_dict('records')
        time = 0
        project_table_rowData = []

        for project_description in data_project_description:
            project_table_rowData.append(
            {'Test_Service': project_description['Test Service'],
             'Tester': project_description['Tester'],
             'Location': project_description['Location2'],
             'Start_Date': datetime.datetime.strptime(project_description['Start Date'], '%Y/%m/%d').date() if type(project_description['Start Date']) is str or math.isnan(project_description['Start Date']) is not True else None,
             'Stop_Date': datetime.datetime.strptime(project_description['End Date'], '%Y/%m/%d').date() if type(project_description['End Date']) is str or math.isnan(project_description['End Date']) is not True else None,
             'Hours': project_description['Hours'],
             'Status': project_description['Notes']}
            )
            time = time + project_description['Hours']

        time_input = time

        project_description_style['display'] = 'block'

    elif triggered_id == 'close_project_description_btn':

        try:
            cursor = connection.cursor()

            project_description_style['display'] = 'none'

            project_list_table_rowData[project_number - 1] = {
                        'Show': '>>',
                        'Start Date': datetime.datetime.fromisoformat(start_date_input).date(),
                        'End Date': datetime.datetime.fromisoformat(stop_date_input).date(),
                        'Location': location_input,
                        'Number': project_number,
                        'Project': project_input,
                        'PM': project_manager_input,
                        'Category': category_input,
                        'Typ': type_input,
                        'Client': client_input,
                        'PL': PL_input,
                        'Work [hours]': time_input
                    }

            sql = "UPDATE project_tracker SET `Start Date` = %s, `End Date` = %s, Location = %s, Project = %s, PM = %s, Category = %s, Typ = %s, Client = %s, PL = %s, Contact = %s, Quote = %s, Quote2 = %s, PO = %s, DRAFT = %s, Report = %s, `Work [hours]` = %s, Invoice = %s WHERE Number = %s"
            cursor.execute(sql, (start_date_input, stop_date_input, location_input, project_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, quote2_input, PO_input, draft_input, report_input, time_input, invoice_input, project_number))
            connection.commit()

            data_project_description = read_database("project_description")
            data_project_description = data_project_description.to_dict('list')

            if project_number in data_project_description['Number']:
                sql = "DELETE FROM project_description WHERE NUMBER = %s"
                cursor.execute(sql, (project_number))
                connection.commit()

            for test in project_table_rowData:
                sql = "INSERT INTO `project_description` (Number, Project, `Test Service`, Tester, Location2, `Start Date`, `End Date`, Hours, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

                cursor.execute(sql, (project_number, project_input, test['Test_Service'], test['Tester'], test['Location'], test['Start_Date'], test['Stop_Date'], test['Hours'], test['Status']))

            # sql = "INSERT INTO `project_description` (Number, Project, `Test Service`, Tester, Location2, `Start Date`, `End Date`, Hours, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # print(project_list_table_rowData[project_number - 1])
            # print(list(pd.DataFrame.from_records(project_list_table_rowData[project_number - 1]).itertuples(index=False, name=None)))
            # cursor.executemany(sql, list(pd.DataFrame.from_records(data_project_description).itertuples(index=False, name=None)))
            connection.commit()

        except:
            loading_screen_children, loading_screen_style['backgroundColor'] = [cross, " Project failed to update"], 'red'

            raise PreventUpdate

        project_input = None
        location_input = None
        project_manager_input = None
        category_input = None
        type_input = None
        client_input = None
        PL_input = None
        contact_input = ''
        quote_input = ''
        quote2_input = ''
        PO_input = None
        draft_input = None
        report_input = None
        time_input = 0
        invoice_input = None
        start_date_input, stop_date_input = None, None

        loading_screen_children, loading_screen_style['backgroundColor'] = [check, " Project successfully updated"], 'green'

    elif triggered_id == 'cancel_project_description_btn':

        project_input = None
        location_input = None
        project_manager_input = None
        category_input = None
        type_input = None
        client_input = None
        PL_input = None
        contact_input = ''
        quote_input = ''
        quote2_input = ''
        PO_input = None
        draft_input = None
        report_input = None
        time_input = 0
        invoice_input = None
        start_date_input, stop_date_input = None, None

        project_description_style['display'] = 'none'

        project_list_table_rowData = no_update

    elif triggered_id == 'type_description_input' or triggered_id == 'client_description_input':
        quote_input = add_quote(type_input, client_input)

    else:
        raise PreventUpdate
    return project_description_style, project_description_label_children, project_list_table_rowData, project_table_rowData, start_date_input, stop_date_input, project_input, location_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, quote2_input, PO_input, draft_input, report_input, time_input, invoice_input, project_number, loading_screen_children, loading_screen_style

def add_quote(type_input, client_input):
    if type_input == 'Paid' and client_input == 'EXT':
        data_project_tracker = read_database("project_tracker")
        data_project_tracker = data_project_tracker[
            (data_project_tracker['Quote'].notnull()) & (data_project_tracker['Typ'] == 'Paid') & (
                        data_project_tracker['Client'] == 'EXT')]
        quote_number = data_project_tracker['Quote'].str[-3:].astype(int).max() + 1
        quote_input = "GER25EMC00" + str(quote_number) if quote_number < 10 else "GER25EMC0" + str(
            quote_number) if quote_number < 100 else "GER25EMC" + str(quote_number)
    else:
        quote_input = ''

    return quote_input

@app.callback(
    Output('download_backup', 'data'),
    Output("loading-screen", 'children', allow_duplicate=True),
    Output("loading-screen", 'style', allow_duplicate=True),
    Input("save_backup", "n_clicks"),
    State("loading-screen", 'style'),
    prevent_initial_call=True)

def save_backup(n_clicks, loading_screen_style):
    trigger_id = ctx.triggered_id
    if trigger_id == "save_backup":
        try:

            data_project_tracker = read_database("project_tracker")
            data_project_description = read_database("project_description")

            data_project_tracker['Start Date'] = data_project_tracker['Start Date'].astype(str)
            data_project_tracker['End Date'] = data_project_tracker['End Date'].astype(str)
            data_project_description['Start Date'] = data_project_description['Start Date'].astype(str)
            data_project_description['End Date'] = data_project_description['End Date'].astype(str)

            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                data_project_tracker.to_excel(writer, sheet_name="Project Tracker", index=False, startrow=1, header=False)
                data_project_description.to_excel(writer, sheet_name="Project Description", index=False, startrow=1, header=False)

                wb = writer.book
                ws1 = writer.sheets["Project Tracker"]
                ws2 = writer.sheets["Project Description"]
                header_format = wb.add_format({'bold':True})

                def write_headers_autowidth(ws, df):
                    for i, col in enumerate(df.columns):
                        ws.write(0, i, col, header_format)
                        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                        ws.set_column(i, i, max_len)

                write_headers_autowidth(ws1, data_project_tracker)
                write_headers_autowidth(ws2, data_project_description)

                for col_num, value in enumerate(data_project_description.columns.values):
                    ws2.write(0, col_num, value, header_format)

                ws1.add_table(0,0,len(data_project_tracker), len(data_project_tracker.columns)-1, {
                    'name': "project_tracker",
                    'columns': [{'header': col} for col in data_project_tracker.columns],
                    'style': 'Table Style Medium 9'
                })

                ws2.add_table(0, 0, len(data_project_description), len(data_project_description.columns) - 1, {
                    'name': "project_description",
                    'columns': [{'header': col} for col in data_project_description.columns],
                    'style': 'Table Style Medium 9'
                })

            output.seek(0)

            loading_screen_children, loading_screen_style['backgroundColor'] = [check, " Backup successfully created"], 'green'

            return dcc.send_bytes(output.read(), 'EMC_projects_backup.xlsx'), loading_screen_children, loading_screen_style

        except:
            loading_screen_children, loading_screen_style['backgroundColor'] = [cross, " Backup failed to create"], 'red'
            return None, loading_screen_children, loading_screen_style
    else:
        raise PreventUpdate

import io
@app.callback(
    Output("loading-screen", 'children', allow_duplicate=True),
    Output("loading-screen", 'style', allow_duplicate=True),
    Input('upload-backup', "contents"),
    State("loading-screen", 'style'),
    prevent_initial_call=True)

def load_backup(contents, loading_screen_style):
    trigger_id = ctx.triggered_id
    if trigger_id == 'upload-backup':
        try:

            cursor = connection.cursor()

            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            excel_file = io.BytesIO(decoded)

            df_dict = pd.read_excel(excel_file, sheet_name=None)
            sheet_names = list(df_dict.keys())
            data_project_tracker = df_dict[sheet_names[0]]
            data_project_description = df_dict[sheet_names[1]]

            data_project_tracker['Start Date'] = data_project_tracker['Start Date'].astype(str)
            data_project_tracker['End Date'] = data_project_tracker['End Date'].astype(str)
            data_project_description['Start Date'] = data_project_description['Start Date'].astype(str)
            data_project_description['End Date'] = data_project_description['End Date'].astype(str)
            data_project_tracker = data_project_tracker.map(lambda x: None if pd.isnull(x) else x)
            data_project_description = data_project_description.map(lambda x: None if pd.isnull(x) else x)

            supabase.table("project_tracker").delete().not_.is_('Number',None).execute()
            supabase.table("project_description").delete().not_.is_('Number', None).execute()

            supabase.table("project_tracker").insert(data_project_tracker.to_dict('records')).execute()
            supabase.table("project_description").insert(data_project_description.to_dict('records')).execute()

            loading_screen_children, loading_screen_style['backgroundColor'] = [check, " Backup successfully loaded"], 'green'

            return loading_screen_children, loading_screen_style

        except:
            loading_screen_children, loading_screen_style['backgroundColor'] = [cross, " Backup failed to load"], 'red'
            return loading_screen_children, loading_screen_style
    else:
        raise PreventUpdate

@app.callback(
    Output("project_table", 'rowData', allow_duplicate=True),
    Output("time_input", 'value', allow_duplicate=True),
    Input("add_test_service_btn", "n_clicks"),
    Input("remove_test_service_btn", "n_clicks"),
    Input("project_table", 'cellValueChanged'),
    State("project_table", 'rowData'),
    State("project_table", 'selectedRows'),
    prevent_initial_call=True)

def update_project_description_table(add_test_service_btn, remove_test_service_btn, project_table_cellValueChanged, project_table_rowData, project_table_selectedRows):
    triggered_id = ctx.triggered_id
    time_input = no_update
    if triggered_id == 'add_test_service_btn':
        project_table_rowData.append(
            {'Test_Service': None,
             'Tester': None,
             'Location': None,
             'Start_Date': date.today(),
             'Stop_Date': date.today(),
             'Hours': 0,
             'Status': 'ONGOING'}
        )
    elif triggered_id == 'remove_test_service_btn' and project_table_selectedRows is not None and project_table_selectedRows != []:
        for test_service in project_table_selectedRows:
            project_table_rowData.remove(test_service)
        time_input = 0
        for project_description in project_table_rowData:
            time_input = time_input + project_description['Hours']

    elif triggered_id == 'project_table' and project_table_cellValueChanged is not None and (project_table_cellValueChanged[0]['colId'] == 'Start_Date' or project_table_cellValueChanged[0]['colId'] == 'Stop_Date'):
        start_date = datetime.datetime.strptime(project_table_cellValueChanged[0]['data']['Start_Date'], '%Y-%m-%d').date() if project_table_cellValueChanged[0]['data']['Start_Date'] is not None else None
        stop_date = datetime.datetime.strptime(project_table_cellValueChanged[0]['data']['Stop_Date'], '%Y-%m-%d').date() if project_table_cellValueChanged[0]['data']['Stop_Date'] is not None else None
        if start_date is not None and stop_date is not None:
            if start_date > date.today():
                project_table_rowData[project_table_cellValueChanged[0]['rowIndex']]['Status'] = 'UPCOMING'
            elif stop_date < date.today():
                project_table_rowData[project_table_cellValueChanged[0]['rowIndex']]['Status'] = 'COMPLETED'
            else:
                project_table_rowData[project_table_cellValueChanged[0]['rowIndex']]['Status'] = 'ONGOING'
        else:
            project_table_rowData[project_table_cellValueChanged[0]['rowIndex']]['Status'] = ''

    elif triggered_id == 'project_table' and project_table_cellValueChanged[0]['colId'] == 'Hours':
        time_input = 0
        for project_description in project_table_rowData:
            time_input = time_input + project_description['Hours']

    else:
        raise PreventUpdate
    return project_table_rowData, time_input

@app.callback(Output('project_list_tab', 'style', allow_duplicate=True),
    Output('project_timeline_tab', 'style', allow_duplicate=True),
    Output('graph_tab', 'style', allow_duplicate=True),
    Output("btn-project-list", 'className'),
    Output("btn-staff-timeline", 'className'),
    Output("btn_graph_report", 'className'),
    Input("btn-project-list", 'n_clicks'),
    Input("btn-staff-timeline", 'n_clicks'),
    Input("btn_graph_report", 'n_clicks'),
    State('project_list_tab', 'style'),
    State('project_timeline_tab', 'style'),
    State('graph_tab', 'style'),
    prevent_initial_call=True)

def show_table(btn_project_list, btn_staff_timeline, btn_graph_tab, project_list_tab_style, project_timeline_tab_style, graph_tab_style):
    project_list_tab_className, project_timeline_tab_className, graph_tab_className = "menu_btn", "menu_btn", "menu_btn"
    triggered_id = ctx.triggered_id
    if triggered_id == 'btn-project-list':
        project_list_tab_style['display'] = 'block'
        project_timeline_tab_style['display'] = 'none'
        graph_tab_style['display'] = 'none'
        project_list_tab_className = "active_menu_btn"
    elif triggered_id == 'btn-staff-timeline':
        project_list_tab_style['display'] = 'none'
        project_timeline_tab_style['display'] = 'block'
        graph_tab_style['display'] = 'none'
        project_timeline_tab_className = "active_menu_btn"
    elif triggered_id == 'btn_graph_report':
        project_list_tab_style['display'] = 'none'
        project_timeline_tab_style['display'] = 'none'
        graph_tab_style['display'] = 'block'
        graph_tab_className = "active_menu_btn"
    else:
        raise PreventUpdate
    return project_list_tab_style, project_timeline_tab_style, graph_tab_style, project_list_tab_className, project_timeline_tab_className, graph_tab_className

@app.callback(Output('project_window', 'style', allow_duplicate=True),
    Output("loading-screen", 'children', allow_duplicate=True),
    Output("loading-screen", 'style', allow_duplicate=True),
    Output("project_input", 'value', allow_duplicate=True),
    Output("location_input", 'value', allow_duplicate=True),
    Output("project_manager_input", 'value', allow_duplicate=True),
    Output("category_input", 'value', allow_duplicate=True),
    Output("type_input", 'value', allow_duplicate=True),
    Output("client_input", 'value', allow_duplicate=True),
    Output("PL_input", 'value', allow_duplicate=True),
    Output("contact_input", 'value', allow_duplicate=True),
    Output("quote_input", 'value', allow_duplicate=True),
    Output("Quote2", 'value', allow_duplicate=True),
    Output("PO_input", 'value', allow_duplicate=True),
    Output("draft_input", 'value', allow_duplicate=True),
    Output("report_input", 'value', allow_duplicate=True),
    Output("time_input", 'value', allow_duplicate=True),
    Output("invoice_input", 'value', allow_duplicate=True),
    # Output("notes_input", 'value', allow_duplicate=True),
    Output("start_date_input", 'date', allow_duplicate=True),
    Output("stop_date_input", 'date', allow_duplicate=True),
    Input('add_project', 'n_clicks'),
    Input('ok_project_btn', 'n_clicks'),
    Input('cancel_btn', 'n_clicks'),
    State("loading-screen", 'style'),
    State('project_window', 'style'),
    State("project_list_table", 'selectedRows'),
    prevent_initial_call=True)

def display_project_window(add_project_btn, ok_btn, cancel_btn, loading_screen_style, project_window_style, project_list_table_selectedRows):
    triggered_id = ctx.triggered_id

    if triggered_id == 'add_project':
        project_window_style['display'] = 'block'
        project_input, location_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, Quote2, PO_input, draft_input, report_input, time_input, invoice_input, start_date_input, stop_date_input = '', '', None, None, None, None, None, '', '', '', '', '', '', None, '', None, None
        loading_screen_children, loading_screen_style['backgroundColor'] = ["No action selected"], '#119DFF'

    # elif triggered_id == 'modify_project':
    #     if project_list_table_selectedRows!=None and project_list_table_selectedRows!=[]:
    #         project_window_style['display'] = 'block'
    #         selectedRow = project_list_table_selectedRows[0]
    #         project_input=selectedRow["Project"]
    #         location_input=selectedRow["Location"]
    #         project_manager_input=selectedRow["PM"]
    #         category_input=selectedRow["Category"]
    #         type_input=selectedRow["Typ"]
    #         client_input=selectedRow["Client"]
    #         PL_input=selectedRow["PL"]
    #         start_date_input=selectedRow["Start Date"]
    #         stop_date_input =selectedRow["End Date"]
    #         loading_screen_children, loading_screen_style['backgroundColor'] = ["No action selected"], '#119DFF'
    #     else:
    #         project_input, location_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, Quote2, PO_input, draft_input, report_input, time_input, invoice_input, start_date_input, stop_date_input = '', '', None, None, None, None, None, '', '', '', '', '', '', None, '', '', None, None
    #         loading_screen_children, loading_screen_style['backgroundColor'] = ["No project selected"], '#119DFF'

    elif triggered_id == 'ok_project_btn' or triggered_id == 'cancel_btn':
        project_window_style['display'] = 'none'
        project_input, location_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, Quote2, PO_input, draft_input, report_input, time_input, invoice_input, start_date_input, stop_date_input = '', '', None, None, None, None, None, '', '', '', '', '', '', None, '', None, None
        loading_screen_children, loading_screen_style['backgroundColor'] = no_update, no_update

    else:
        raise PreventUpdate
    return project_window_style, loading_screen_children, loading_screen_style, project_input, location_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, Quote2, PO_input, draft_input, report_input, time_input, invoice_input, start_date_input, stop_date_input

@app.callback(Output("project_list_table", 'rowData', allow_duplicate=True),
    Output('add_project', 'n_clicks'),
    Output("loading-screen", 'children', allow_duplicate=True),
    Output("loading-screen", 'style', allow_duplicate=True),
    Input('ok_project_btn', 'n_clicks'),
    State('add_project', 'n_clicks'),
    State("project_list_table", 'rowData'),
    State("project_list_table", 'selectedRows'),
    State("loading-screen", 'style'),
    State("project_input", 'value'),
    State("location_input", 'value'),
    State("project_manager_input", 'value'),
    State("category_input", 'value'),
    State("type_input", 'value'),
    State("client_input", 'value'),
    State("PL_input", 'value'),
    State("contact_input", 'value'),
    State("quote_input", 'value'),
    State("Quote2", 'value'),
    State("PO_input", 'value'),
    State("draft_input", 'value'),
    State("report_input", 'value'),
    State("time_input", 'value'),
    State("invoice_input", 'value'),
    State("start_date_input", 'date'),
    State("stop_date_input", 'date'),
    prevent_initial_call=True)

def add_project(ok_btn, add_project, project_list_table_rowData, project_list_table_selectedRows, loading_screen_style, project_input, location_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, quote_input, Quote2, PO_input, draft_input, report_input, time_input, invoice_input, start_date_input, stop_date_input):
    if ok_btn!= 0:
        try:
            cursor = connection.cursor()

            if start_date_input is None:
                start_date_input = date(date.today().year, 1, 1)
            if stop_date_input is None:
                stop_date_input = date(date.today().year + 1, 1, 1)

            if add_project == 1:

                number = len(project_list_table_rowData) + 1
                new_project = {
                    'Show': '>>',
                    'Start Date': start_date_input,
                    'End Date': stop_date_input,
                    'Location': location_input,
                    'Number': number,
                    'Project': project_input,
                    'PM': project_manager_input,
                    'Category': category_input,
                    'Typ': type_input,
                    'Client': client_input,
                    'PL': PL_input,
                    "Work [hours]": 0
                }
                project_list_table_rowData.append(new_project)

                add_quote(type_input, client_input)

                # start_date_input = start_date_input.isoformat() if type(start_date_input) is not str else start_date_input
                # stop_date_input = stop_date_input.isoformat() if type(stop_date_input) is not str else stop_date_input

                sql = ("INSERT INTO project_tracker (`Start Date`, `End Date`, Location, Number, Project, PM, Category, Typ, Client, PL, Contact, Quote, Quote2, PO, DRAFT, Report, `Work [hours]`, Invoice, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(sql, (str(start_date_input), str(stop_date_input), location_input, number, project_input, project_manager_input, category_input, type_input, client_input, PL_input, contact_input, None, None, None, None, None, 0, None, None))
                connection.commit()

            if add_project == 1:
                loading_screen_children, loading_screen_style['backgroundColor'] = [check, " Project successfully added"], 'green'
            else:
                loading_screen_children, loading_screen_style['backgroundColor'] = [check, " Project successfully modified"], 'green'

        except:
            if add_project == 1:
                loading_screen_children, loading_screen_style['backgroundColor'] = [cross, " Project failed to add"], 'red'
            else:
                loading_screen_children, loading_screen_style['backgroundColor'] = [cross, " Project failed to modify"], 'red'

        return project_list_table_rowData, 0, loading_screen_children, loading_screen_style
    raise PreventUpdate

@app.callback(Output('remove_window', 'style', allow_duplicate=True),
    Output("loading-screen", 'children', allow_duplicate=True),
    Input('remove_project', 'n_clicks'),
    Input('yes_remove_btn', 'n_clicks'),
    Input('no_remove_btn', 'n_clicks'),
    State('remove_window', 'style'),
    prevent_initial_call=True)

def confirm_remove_window(remove_project, yes_remove_btn, no_remove_btn,  remove_window_style):
    triggered_id = ctx.triggered_id
    if triggered_id == 'remove_project':
        remove_window_style['display'] = 'block'
        loading_screen_children = no_update
    elif triggered_id == 'yes_remove_btn' or triggered_id == 'no_remove_btn':
        remove_window_style['display'] = 'none'
        loading_screen_children = no_update
    else:
        raise PreventUpdate
    return remove_window_style, loading_screen_children

@app.callback(Output("project_list_table", 'rowData', allow_duplicate=True),
    Output("loading-screen", 'children', allow_duplicate=True),
    Output("loading-screen", 'style', allow_duplicate=True),
    Output('project_description', 'style', allow_duplicate=True),
    Input('yes_remove_btn', 'n_clicks'),
    State("project_list_table", 'rowData'),
    State("loading-screen", 'style'),
    State("project_number", 'data'),
    State('project_description', 'style'),
    prevent_initial_call=True)

def remove_project(remove_project, project_list_table_rowData, loading_screen_style, project_number, project_description_style):
    if remove_project!=0:
        try:
            cursor = connection.cursor()

            index = project_number - 1
            project_list_table_rowData.pop(index)

            sql = "DELETE FROM project_tracker WHERE Number = %s"
            cursor.execute(sql, (project_number))
            sql = "DELETE FROM project_description WHERE Number = %s"
            cursor.execute(sql, (project_number))
            connection.commit()

            for row_index in range(index, len(project_list_table_rowData)):
                project_list_table_rowData[row_index]['Number'] = row_index + 1

                sql = "UPDATE project_tracker SET Number = %s WHERE Number = %s"
                cursor.execute(sql, (row_index + 1, row_index + 2))
                sql = "UPDATE project_description SET Number = %s WHERE Number = %s"
                cursor.execute(sql, (row_index + 1, row_index + 2))
                connection.commit()

            project_description_style['display'] = 'none'

            loading_screen_children, loading_screen_style['backgroundColor'] = [check, " Project successfully removed"], 'green'

        except:
            loading_screen_children, loading_screen_style['backgroundColor'] = [cross, " Project remove failed"], 'red'

    else:
        raise PreventUpdate
    return project_list_table_rowData, loading_screen_children, loading_screen_style, project_description_style

@app.callback(Output("project_timeline", 'figure', allow_duplicate=True),
    Output('start_stop_date_timeline_input', 'start_date'),
    Output('start_stop_date_timeline_input', 'end_date'),
    Input('start_stop_date_timeline_input', 'start_date'),
    Input('start_stop_date_timeline_input', 'end_date'),
    Input("project_timeline", 'relayoutData'),
    Input('timeline_checklist', 'value'),
    Input("project_list_table", 'rowData'),
    State("project_timeline", 'figure'),
    prevent_initial_call=True)

def update_timeline(start_date_timeline_input, stop_date_timeline_input, project_timeline_relayoutData, timeline_checklist_value, project_list_rowData, project_timeline_figure):
    triggered_id = ctx.triggered_id

    if triggered_id == 'start_stop_date_timeline_input':
        start_date_timeline_input, stop_date_timeline_input = start_date_timeline_input.split('T')[0], stop_date_timeline_input.split('T')[0]
        if len(start_date_timeline_input.split('-')[0]) != 4:
            start_date_timeline_input = f"{start_date_timeline_input.split('-')[2]}-{start_date_timeline_input.split('-')[1]}-{start_date_timeline_input.split('-')[0]}"
        if len(stop_date_timeline_input.split('-')[0]) != 4:
            stop_date_timeline_input = f"{stop_date_timeline_input.split('-')[2]}-{stop_date_timeline_input.split('-')[1]}-{stop_date_timeline_input.split('-')[0]}"
        start_date_timeline_input, stop_date_timeline_input = datetime.datetime.strptime(start_date_timeline_input , '%Y-%m-%d'), datetime.datetime.strptime(stop_date_timeline_input , '%Y-%m-%d')
        project_timeline_figure['layout']['xaxis']['range'] = [start_date_timeline_input, stop_date_timeline_input]

    elif triggered_id == 'project_timeline':
        start_date_timeline_input, stop_date_timeline_input = project_timeline_figure['layout']['xaxis']['range']
        start_date_timeline_input, stop_date_timeline_input = start_date_timeline_input.split(' ')[0], stop_date_timeline_input.split(' ')[0]

    elif triggered_id == 'timeline_checklist' or triggered_id == 'project_list_table' :
        for index, value in enumerate(timeline_checklist_value):
            timeline_checklist_value[index] = value.split(' ')[0][0] + value.split(' ')[1][0]

        lab_member_list = lab_member_list_fct(read_database("project_tracker"))
        for lab_member in list(lab_member_list.keys()):
            if lab_member not in timeline_checklist_value:
                del lab_member_list[lab_member]
        project_timeline_figure = create_project_timeline(lab_member_list)
    else:
        raise PreventUpdate
    return project_timeline_figure, start_date_timeline_input, stop_date_timeline_input
import numpy as np

@app.callback(Output('chart', 'figure'),
    Input("type_chart_input", 'value'),
    Input("label_chart_input_1", 'value'),
    Input("label_chart_input_2", 'value'),
    Input("value_chart_input", 'value'),
    Input("chart_date", 'start_date'),
    Input("chart_date", 'end_date'),
    Input("close_project_description_btn", 'n_clicks'),
    Input("remove_project", 'n_clicks'),
    prevent_initial_call=True)

def update_chart(type_chart_input_value, label_pie_chart_input_value_1, label_pie_chart_input_value_2, value_pie_chart_input_value, chart_start_date, chart_end_date, close_project_description_btn, remove_project):
    time.sleep(0.5)
    chart_start_date, chart_end_date = np.datetime64(chart_start_date), np.datetime64(chart_end_date)
    chart_figure = create_chart_figure(type_chart_input_value, label_pie_chart_input_value_1, label_pie_chart_input_value_2, value_pie_chart_input_value, chart_start_date, chart_end_date)

    if type_chart_input_value == 'Pie chart':
        chart_figure['layout']['legend']['x'] = 0.9
        chart_figure['layout']['title']['x'] = 0.6
    else:
        chart_figure['layout']['legend']['x'] = 1
        chart_figure['layout']['title']['x'] = 0.5
    return chart_figure

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port= 8001)
