# app.py

import dash
from dash import dash_table
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_table
from dash.exceptions import PreventUpdate

# Инициализация приложения Dash
app = dash.Dash(__name__)


# Загрузка CSV-файла с разделителем ";"
def load_data(contents):
    import io
    import base64

    # Декодируем содержимое CSV
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=";")

    return df


# Определяем layout приложения
app.layout = html.Div([
    html.H1("Финансовый анализатор данных"),

    # Компонент для загрузки файла
    dcc.Upload(
        id='upload-data',
        children=html.Button('Загрузить CSV'),
        multiple=False
    ),

    # График динамики доходов и расходов (временной ряд)
    dcc.Graph(id='line-chart'),

    # Круговая диаграмма для категорий расходов
    dcc.Graph(id='pie-chart'),

    # Гистограмма для анализа прибыли
    dcc.Graph(id='histogram'),

    # Таблица с ключевыми финансовыми показателями
    dash_table.DataTable(id='financial-table'),

    # График рассеяния для корреляции
    dcc.Graph(id='scatter-plot'),

    # Выпадающий список для выбора периода анализа
    dcc.Dropdown(
        id='period-dropdown',
        options=[
            {'label': 'Месяц', 'value': 'Месяц'},
            {'label': 'Квартал', 'value': 'Квартал'},
            {'label': 'Год', 'value': 'Год'}
        ],
        value='Месяц'
    ),

    # Индикаторы для отображения текущих показателей
    html.Div([
        html.Div("Прибыль: ", id='profit-indicator'),
        html.Div("Доходы: ", id='revenue-indicator'),
        html.Div("Расходы: ", id='expenses-indicator')
    ])
])


# Обработчик загрузки данных
@app.callback(
    Output('line-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Output('histogram', 'figure'),
    Output('financial-table', 'data'),
    Output('scatter-plot', 'figure'),
    Output('profit-indicator', 'children'),
    Output('revenue-indicator', 'children'),
    Output('expenses-indicator', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_dashboard(contents, filename):
    if contents is None:
        raise PreventUpdate

    # Загружаем данные
    df = load_data(contents)

    # Преобразуем столбец "Дата" в тип datetime
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')

    # Подсчитываем доходы и расходы
    df['Доходы'] = df[df['Тип'] == 'Доход']['Сумма']
    df['Расходы'] = df[df['Тип'] == 'Расход']['Сумма']
    total_revenue = df['Доходы'].sum()
    total_expenses = df['Расходы'].sum()
    profit = total_revenue - total_expenses

    # График временного ряда
    line_chart = px.line(df, x='Дата', y=['Доходы', 'Расходы'], labels={'Дата': 'Дата', 'value': 'Сумма'},
                         title="Динамика доходов и расходов")

    # Круговая диаграмма для категорий
    pie_chart = px.pie(df, names='Категория', values='Сумма', title="Структура расходов по категориям")

    # Гистограмма для анализа прибыли
    histogram = px.histogram(df, x='Сумма', color='Тип', nbins=20, title="Распределение прибыли и расходов")

    # Таблица с ключевыми показателями
    financial_data = [{
        'Период': 'Общий',
        'Доходы': total_revenue,
        'Расходы': total_expenses,
        'Прибыль': profit
    }]

    # График рассеяния для корреляции прибыли и других параметров
    scatter_plot = px.scatter(df, x='Сумма', y='Время', color='Тип', title="Корреляция между прибылью и временем")

    # Индикаторы для текущих значений
    profit_indicator = f'Прибыль: {profit:.2f} ₽'
    revenue_indicator = f'Доходы: {total_revenue:.2f} ₽'
    expenses_indicator = f'Расходы: {total_expenses:.2f} ₽'

    return line_chart, pie_chart, histogram, financial_data, scatter_plot, profit_indicator, revenue_indicator, expenses_indicator


if __name__ == '__main__':
    app.run_server(debug=True)

# http://127.0.0.1:8050/