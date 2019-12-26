from threading import Thread
import websocket
from NeuroSphero import *
from NeuroLogin import *
from NeuroLogout import disconnect as disconnect_neuro
from keras.models import load_model
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

EMAIL = 'matanron3@gmail.com'
PASSWORD = 'Matan1234'
SENSOR = '00a3b4810811'
SPHERO_ID = '68:86:e7:01:fb:b2'


class NeuroSpheroManager(object):
    """Neuro sphero manager in charge of managing the connections of neuro sensor and sphero ball.
       It is also in charge of loading the classifier and predicting the state of the patient."""
    def __init__(self, email=EMAIL, password=PASSWORD, sensor=SENSOR, sphero_id=SPHERO_ID):
        self.email = email
        self.password = password
        self.sensor = sensor
        self.sphero_id = sphero_id
        self.buffer = np.zeros((20, 121))  # save samples in buffer and predict once every len(buffer) samples

        self.running = False  # indication whether we want to read data from the sensor or not
        self.ws = self.connect()

        self.is_training = False

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.neurosphero.y_prediction = -1
        self.neurolearn = load_model(dir_path + r'/NeuroClassifier.h5')
        self.neurolearn._make_predict_function()
        print('created neuro sphero manager')

    def run(self):
        """Start to run the websocket server in thread and get messages from the sensor.
           Start to run Sphero ball thread."""

        self.running = True
        self.ws_thread = Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

        self.sphero_thread = Thread(target=self.neurosphero.control_sphero)
        self.sphero_thread.daemon = True
        self.sphero_thread.start()
        print('running neuro sphero')

    # if running on python 3 erase ws argument from on_error, on_close and on_message
    def on_error(self, ws, error):
        print("ERROR: {0}".format(error))

    def on_close(self, ws):
        """Checks whether closed happened on purpose or not and handle it."""
        self.neurosphero.y_prediction = -2  # red color to signal websocket error
        print("### websocket closed ###")
        if self.running is False:  # wanted disconnection
            print('Wanted disconnection')
            disconnect_neuro(sensor=self.sensor)  # close the connection to the neuro sensor and stop the recording.
            print('sent disconnect neuro')
        else:  # not wanted disconnection
            print('Unwanted disconnection')
            try:
                self.ws_thread.join()   # Make sure websocket is really closed
            except Exception as e:
                print(e)

            self.ws = self.create_websocket_connection()
            self.ws_thread = Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            print('running neuro sphero')

    def on_message(self, ws, message):
        self.data = json.loads(message)
        self.buffer[self.neurosphero.sample_number % len(self.buffer)] = self.data[u'all'][0:121]
        self.neurosphero.sample_number += 1

        # training mode
        if self.is_training:
            self.neurosphero.y_prediction = -3

        # predict mode
        if (not self.is_training) and (self.neurosphero.sample_number % len(self.buffer)) == 0:  # checks prediction every 30 samples
            self.buf_prediction = self.neurolearn.model.predict(self.buffer)
            pred_sum = sum(self.buf_prediction) / len(self.buffer)
            pred_sum = ['%.3f' % elem for elem in pred_sum]
            pred_sum = [float(elem) for elem in pred_sum]

            print('*********Memory Meditate Weakhand Happy*********')
            print('          {}\n'.format(pred_sum))

            if self.neurosphero.y_prediction == np.argmax(pred_sum):
                pass

            if max(pred_sum) >= 0.6:  # more than 50% certainty of a prediction
                if np.argmax(pred_sum) == 3:  # higher threshold for happy music and dancing (movment can impact prediction)
                    if max(pred_sum) > 0.65:
                        self.neurosphero.y_prediction = np.argmax(pred_sum)
                    else:
                        self.neurosphero.y_prediction = -1
                else:
                    self.neurosphero.y_prediction = np.argmax(pred_sum)
            else:
                self.neurosphero.y_prediction = -1

    def login_neuro(self):
        """Login to neurosteer API"""
        login = NeuroLogin(email=self.email, password=self.password, sensor=self.sensor)
        login.get_token()
        return login

    def connect_sphero(self):
        """Connect to the sphero ball."""
        neurosphero = NeuroSphero(self.sphero_id)
        is_connected = neurosphero.connect()
        return neurosphero, is_connected

    def create_websocket_connection(self):
        """Create websocket connection to neurosteer API based on the token from login_neuro."""
        # C:\Users\owner\Anaconda2\Lib\site-packages\websocket\_logging.py
        # added null handler to avoid no handler error
        websocket.enableTrace(False)
        print("connecting to cloud...")

        ws = websocket.WebSocketApp(
            "wss://api.neurosteer.com/api/v1/features/" + self.sensor
            + "/real-time/?all=true&access_token=" + self.neurologin.token,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        return ws

    def connect(self):
        """Loging to Neuro API using credentials and Sphero ball using the sphero id"""
        self.neurologin = self.login_neuro()
        self.neurosphero, is_connected = self.connect_sphero()

        return self.create_websocket_connection()

    def disconnect(self):
        """Close the connection to neuro API and stop the recording."""
        self.running = False
        self.ws.close()


