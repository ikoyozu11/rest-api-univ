import threading
import time
import json
import pytz
from datetime import datetime
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

def load_urls_from_file(file_path):
    urls = []
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for item in data['data']:
                urls.append({
                    'name': item['name'], 
                    'url': item['url'], 
                    'status': 'Unknown', 
                    'last_check_up': 'Unknown'
                })
    except Exception as e:
        print(f"Error reading file: {e}")
    return urls

urls = load_urls_from_file('./templates/urls.json')

def check_status_independently(url_obj):
    while True:
        url = url_obj['url']
        local_tz = pytz.timezone('Asia/Jakarta')
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                url_obj['status'] = 'Up'
                now_local = datetime.now(local_tz)
                url_obj['last_check_up'] = now_local.strftime('%Y-%m-%d %H:%M:%S')
            else:
                url_obj['status'] = 'Down'
        except requests.RequestException:
            url_obj['status'] = 'Down'
        
        interval = 60 if url_obj['status'] == 'Up' else 30
        time.sleep(interval)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def get_status():
    sorted_urls = sorted(urls, key=lambda x: x['status'] == 'Up')
    return jsonify({'urls': sorted_urls})

if __name__ == '__main__':
    for url_obj in urls:
        thread = threading.Thread(target=check_status_independently, args=(url_obj,))
        thread.daemon = True
        thread.start()

    app.run(debug=True, port=8080)
