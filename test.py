from flask import Flask, request, render_template_string
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CSV Viewer</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
    </style>
</head>
<body>
    <h2>Загрузите CSV файл</h2>
    <form action="/display" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv">
        <button type="submit">Загрузить</button>
    </form>
    {% if table %}
        <h2>Содержимое CSV файла</h2>
        {{ table|safe }}
        <a href="/">Загрузить другой файл</a>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET'])
def upload_file():
    return render_template_string(HTML_TEMPLATE)

@app.route('/display', methods=['POST'])
def display_file():
    if 'file' not in request.files:
        return "Файл не найден!"
    file = request.files['file']
    if file.filename == '':
        return "Файл не выбран!"
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        try:
            data = pd.read_csv(filepath)
            table_html = data.to_html(classes='data', header="true", index=False)
            return render_template_string(HTML_TEMPLATE, table=table_html)
        except Exception as e:
            return f"Ошибка обработки файла: {e}"
    return "Ошибка загрузки файла!"

if __name__ == '__main__':
    app.run(debug=True)