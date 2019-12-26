from flask import Flask
from flask import Response, request
import datetime as dt
import json
from main_sphero import NeuroSpheroManager


app = Flask(__name__, static_url_path='')


@app.route('/')
def index():
    return app.send_static_file(filename='index.html')


@app.route('/start-recording/', methods=['POST'])  # describes what will happen when someone will get to this path:
def start_recording():
    print('start recording')

    neurosphero_manager.is_training = True
    neurosphero_manager.run()

    description = json.loads(request.data)['description']
    description = '{} {:%d/%m/%y %H:%M}'.format(description,
                                                dt.datetime.today())
    neurosphero_manager.neurologin.update_description(description=description)

    return Response(status=200)


@app.route('/stop-recording/')
def stop_recording():
    print('stop recording')

    try:
        neurosphero_manager.disconnect()
    except Exception as e:
        print(e)

    return Response(status=200)


@app.route('/reconnect-sphero/')
def reconnect_sphero():
    print('re connect sphero')
    is_connected = neurosphero_manager.connect_sphero()

    if is_connected:
        return Response(status=200)
    else:
        return Response(status=400)


@app.route('/predict/')
def predict():
    try:
        neurosphero_manager.run()
    except Exception as e:
        print(e)

    return Response(status=200)

if __name__ == '__main__':
    neurosphero_manager = NeuroSpheroManager()

    app.run(host='127.0.0.1', port=8000, debug=False, threaded=True)
