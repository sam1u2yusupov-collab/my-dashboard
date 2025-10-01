import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

app = dash.Dash(__name__)
server = app.server

# Данные для робота
def get_robot_data(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    data = {
        'date': dates,
        'total_emails': [156, 189, 143, 201, 178, 165, 192],
        'processed_by_robot': [132, 158, 118, 167, 152, 138, 161],
        'correctly_processed': [120, 145, 105, 150, 140, 125, 148],
        'redirected_to_staff': [12, 13, 13, 17, 12, 13, 13],
        'interdep_agreements': [45, 52, 38, 58, 49, 44, 51],
        'interdep_processed': [40, 46, 32, 50, 44, 39, 45]
    }
    df = pd.DataFrame(data)
    
    # Расчеты процентов
    df['processed_percent'] = (df['processed_by_robot'] / df['total_emails'] * 100).round(1)
    df['robot_processed_percent'] = ((df['processed_by_robot'] - df['redirected_to_staff']) / df['total_emails'] * 100).round(1)
    df['correct_percent'] = (df['correctly_processed'] / df['processed_by_robot'] * 100).round(1)
    df['interdep_percent'] = (df['interdep_processed'] / df['interdep_agreements'] * 100).round(1)
    
    return df

# Данные для НПА
def get_npa_data():
    data = {
        'document_name': ['НПА-001', 'НПА-002', 'НПА-003', 'НПА-004', 'НПА-005'],
        'changes_count': [23, 18, 35, 12, 28],
        'implemented_count': [18, 15, 28, 8, 22],
        'implementation_rate': [78.3, 83.3, 80.0, 66.7, 78.6]
    }
    return pd.DataFrame(data)

# Стили
card_style = {
    'textAlign': 'center', 'padding': '20px', 'background': 'white', 
    'borderRadius': '10px', 'border': '1px solid #dee2e6', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'minWidth': '150px', 'flex': '1'
}

graph_style = {
    'background': 'white', 'padding': '15px', 'borderRadius': '10px', 
    'border': '1px solid #dee2e6', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'marginBottom': '20px'
}

app.layout = html.Div([
    # Заголовок и управление
    html.Div([
        html.H1("🤖 Аналитика работы робота и НПА", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Мониторинг эффективности обработки документов", 
              style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'}),
        
        # Переключатель отчетов
        html.Div([
            dcc.RadioItems(
                id='report-selector',
                options=[
                    {'label': ' 📊 Отчет по роботу', 'value': 'robot'},
                    {'label': ' 📈 Отчет по НПА', 'value': 'npa'}
                ],
                value='robot',
                inline=True,
                style={'textAlign': 'center', 'marginBottom': '20px'}
            )
        ], style={'textAlign': 'center'}),
        
        # Выбор периода
        html.Div([
            dcc.DatePickerRange(
                id='date-picker',
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now(),
                display_format='YYYY-MM-DD'
            )
        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
        
        # Переключатель темы
        html.Div([
            html.Button('🌙 Темная тема', id='theme-toggle', n_clicks=0,
                       style={'padding': '10px 15px', 'border': 'none', 'borderRadius': '5px', 
                              'background': '#3498db', 'color': 'white', 'cursor': 'pointer'})
        ], style={'textAlign': 'center', 'marginBottom': '30px'})
    ]),
    
    # Контент отчетов
    html.Div(id='report-content')
], style={'padding': '20px', 'background': '#f8f9fa', 'minHeight': '100vh'}, id='main-container')

# Колбэк для переключения отчетов
@callback(
    Output('report-content', 'children'),
    Input('report-selector', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)
def update_report(report_type, start_date, end_date):
    if report_type == 'robot':
        return create_robot_report(start_date, end_date)
    else:
        return create_npa_report()

def create_robot_report(start_date, end_date):
    df = get_robot_data(start_date, end_date)
    latest = df.iloc[-1]
    
    # KPI карточки
    kpi_cards = html.Div([
        html.Div([html.Div("📨", style={'fontSize': '2rem'}), html.H3(f"{latest['total_emails']}", style={'color': '#3498db'}), html.P("Всего писем")], style=card_style),
        html.Div([html.Div("🔧", style={'fontSize': '2rem'}), html.H3(f"{latest['processed_percent']}%", style={'color': '#27ae60'}), html.P("Обработано")], style=card_style),
        html.Div([html.Div("🤖", style={'fontSize': '2rem'}), html.H3(f"{latest['robot_processed_percent']}%", style={'color': '#2980b9'}), html.P("Расписано роботом")], style=card_style),
        html.Div([html.Div("✅", style={'fontSize': '2rem'}), html.H3(f"{latest['correct_percent']}%", style={'color': '#27ae60'}), html.P("Верно расписано")], style=card_style),
        html.Div([html.Div("🔄", style={'fontSize': '2rem'}), html.H3(f"{latest['redirected_to_staff']}", style={'color': '#f39c12'}), html.P("Перенаправлено")], style=card_style),
        html.Div([html.Div("🤝", style={'fontSize': '2rem'}), html.H3(f"{latest['interdep_agreements']}", style={'color': '#9b59b6'}), html.P("Межведомственные")], style=card_style),
        html.Div([html.Div("📊", style={'fontSize': '2rem'}), html.H3(f"{latest['interdep_percent']}%", style={'color': '#2980b9'}), html.P("Эффективность межвед.")], style=card_style),
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'gap': '15px', 'marginBottom': '40px'})
    
    # Графики
    # График 1: Распределение писем
    pie_fig = px.pie(
        values=[latest['processed_by_robot'] - latest['redirected_to_staff'], 
                latest['redirected_to_staff'],
                latest['total_emails'] - latest['processed_by_robot']],
        names=['Обработано роботом', 'Перенаправлено', 'Не обработано'],
        title='📊 Распределение обработки писем',
        color_discrete_sequence=['#3498db', '#e74c3c', '#95a5a6']
    )
    
    # График 2: Динамика
    trend_fig = go.Figure()
    trend_fig.add_trace(go.Scatter(x=df['date'], y=df['total_emails'], name='Всего писем', line=dict(color='#3498db')))
    trend_fig.add_trace(go.Scatter(x=df['date'], y=df['processed_by_robot'], name='Обработано', line=dict(color='#27ae60')))
    trend_fig.add_trace(go.Scatter(x=df['date'], y=df['correctly_processed'], name='Верно расписано', line=dict(color='#e74c3c')))
    trend_fig.update_layout(title='📈 Динамика показателей')
    
    # График 3: Эффективность
    efficiency_fig = go.Figure()
    efficiency_fig.add_trace(go.Scatter(x=df['date'], y=df['processed_percent'], name='Обработано %', line=dict(color='#3498db')))
    efficiency_fig.add_trace(go.Scatter(x=df['date'], y=df['correct_percent'], name='Верно расписано %', line=dict(color='#27ae60')))
    efficiency_fig.update_layout(title='📊 Эффективность работы')
    
    graphs = html.Div([
        html.Div([
            html.Div([dcc.Graph(figure=pie_fig)], style={'flex': '1', 'minWidth': '300px'}),
            html.Div([dcc.Graph(figure=trend_fig)], style={'flex': '2', 'minWidth': '400px'}),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'marginBottom': '20px'}),
        html.Div([dcc.Graph(figure=efficiency_fig)], style=graph_style)
    ])
    
    return html.Div([kpi_cards, graphs])

def create_npa_report():
    df = get_npa_data()
    
    # KPI для НПА
    total_implemented = df['implemented_count'].sum()
    total_changes = df['changes_count'].sum()
    avg_implementation = df['implementation_rate'].mean().round(1)
    
    kpi_cards = html.Div([
        html.Div([html.Div("📄", style={'fontSize': '2rem'}), html.H3(f"{len(df)}", style={'color': '#3498db'}), html.P("Документов НПА")], style=card_style),
        html.Div([html.Div("✅", style={'fontSize': '2rem'}), html.H3(f"{total_implemented}", style={'color': '#27ae60'}), html.P("Внедрено изменений")], style=card_style),
        html.Div([html.Div("📊", style={'fontSize': '2rem'}), html.H3(f"{avg_implementation}%", style={'color': '#2980b9'}), html.P("Средняя эффективность")], style=card_style),
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'gap': '15px', 'marginBottom': '40px'})
    
    # Графики НПА
    # График 1: Статус внедрения
    npa_pie_fig = px.pie(
        values=[total_implemented, total_changes - total_implemented],
        names=['Внедрено', 'Не внедрено'],
        title='📊 Статус внедрения изменений',
        color_discrete_sequence=['#27ae60', '#e74c3c']
    )
    
    # График 2: Эффективность по документам
    npa_bar_fig = px.bar(df, x='document_name', y='implementation_rate',
                        title='📈 Эффективность внедрения по документам',
                        color_discrete_sequence=['#3498db'])
    npa_bar_fig.update_layout(yaxis_title='Процент внедрения (%)')
    
    graphs = html.Div([
        html.Div([
            html.Div([dcc.Graph(figure=npa_pie_fig)], style={'flex': '1', 'minWidth': '300px'}),
            html.Div([dcc.Graph(figure=npa_bar_fig)], style={'flex': '2', 'minWidth': '400px'}),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
    ])
    
    return html.Div([kpi_cards, graphs])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=False)