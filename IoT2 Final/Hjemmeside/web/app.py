from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def execute_sql_command(sql):
    try:
        conn = sqlite3.connect('testdb1.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            data = cursor.fetchall()
            return data
        else:
            conn.commit()
            return "Command executed successfully."
    except sqlite3.Error as e:
        return f"SQLite error: {e}"
    finally:
        conn.close()

@app.template_filter('sort_link')
def sort_link(column, current_sort_by):
    if column == current_sort_by:
        return f'<a href="?sort_by={column}&sort_order=DESC">▼ {column}</a>'
    else:
        return f'<a href="?sort_by={column}&sort_order=ASC">▲ {column}</a>'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sql_command = request.form['sql_command']
        result = execute_sql_command(sql_command)
        return render_template('index.html', result=result, sql_command=sql_command)
    elif request.method == 'GET':
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'ASC')
        
        column_mapping = {
            'ID': 'id',
            'Timestamp': 'timestamp',
            'Sensor_ID': 'sensor_id',
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'Analog_Value': 'analog_value',
            'Digital_Value': 'digital_value',
            'Latitude': 'latitude',
            'Longitude': 'longitude'
        }
        
        sort_column = column_mapping.get(sort_by, 'id')
        
        default_sql_command = f'SELECT * FROM received_data ORDER BY {sort_column} {sort_order};'
        default_result = execute_sql_command(default_sql_command)
        return render_template('index.html', result=default_result, sql_command=default_sql_command, current_sort_by=sort_by)
    return render_template('index.html', result=None, sql_command=None)


@app.route('/temperature')
def temperature():
    return render_template('temperature.html')


@app.route('/humidity')
def humidity():
    return render_template('humidity.html')


@app.route('/gps')
def gps():
    return render_template('gps.html')


@app.route('/fetch_temperature_data')
def fetch_temperature_data():
    try:
       
        conn = sqlite3.connect('testdb1.db')
        cursor = conn.cursor()
        
        
        cursor.execute('SELECT temperature FROM received_data')
        data = cursor.fetchall()
        temperatures = [entry[0] for entry in data]  
        return jsonify(temperatures)  
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()


@app.route('/fetch_humidity_data')
def fetch_humidity_data():
    try:
        
        conn = sqlite3.connect('testdb1.db')
        cursor = conn.cursor()
        
        
        cursor.execute('SELECT humidity FROM received_data')
        data = cursor.fetchall()
        humidities = [entry[0] for entry in data]  
        return jsonify(humidities)  
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()


@app.route('/fetch_gps_data')
def fetch_gps_data():
    try:
        
        conn = sqlite3.connect('testdb1.db')
        cursor = conn.cursor()
        
        
        cursor.execute('SELECT latitude, longitude FROM received_data WHERE latitude IS NOT NULL AND longitude IS NOT NULL')
        data = cursor.fetchall()
        return jsonify(data)  
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
