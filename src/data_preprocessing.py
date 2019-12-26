import requests
import json
import pandas as pd
import numpy as np
import zipfile
import io
from NeuroLogin import *
import threading
from sklearn.model_selection import train_test_split

class NeuroProcess():

    def __init__(self):
        self.email = 'matanron3@gmail.com'
        self.password = 'Matan1234'
        self.sensor = '00a3b4810811'
        get_token = NeuroLogin(self.email, self.password, self.sensor)
        get_token.get_token()
        self.token = get_token.token
        self.dataset = pd.DataFrame()


    def query_sessions(self, ns_connection,quary_string='', page=1, perPage=1000):
        payload = dict(access_token=self.token)
        url = ns_connection + '/api/v1/sensors/00a3b4810811/sessions/?page='+str(page)+'&searchTerm='+str(quary_string)+'&perPage='+str(perPage)
        resp = requests.get(url, params=payload)
        data = json.loads(resp.text)
        sessions = pd.DataFrame(data['sessions'])

        return sessions.sort_values('startDate')

    def save_data_as_csv(self, ns_connection, sessionName, y_index, y_size):

        url = ns_connection + r'/api/v1/sensors/' + self.sensor + r'/' + sessionName + r'/all?access_token='+self.token
        r = requests.get(url)
        buffer = io.BytesIO(r.content)
        z = zipfile.ZipFile(buffer)
        file = z.open('%s-%s.features.txt' % (self.sensor, sessionName))
        X = np.genfromtxt(file, delimiter=',')
        X = X[10:-10]
        X = X[:, 1:122]
        X = np.tanh(0.8*(X + 4) - 2)  # normalize the same as online data
        y = np.zeros((X.shape[0], y_size))
        y[:, y_index] = 1.0  # one hot label for the categorical data
        temp = np.concatenate((X, y), axis=1)
        temp_pd = pd.DataFrame(temp)
        self.dataset = pd.concat((self.dataset, temp_pd), axis=0)


if __name__ == "__main__":
    query_list = ['MEMORY GAME', 'CHILL MUSIC MEDITATE', 'WRITE WITH WEAK HAND', 'HAPPY MUSIC DANCING']
    my = NeuroProcess()
    threads = []
    for q in range(len(query_list)):
        sessions = my.query_sessions('https://api.neurosteer.com', query_list[q])
        print("\nThere are {} sessions of {}".format(len(sessions), query_list[q]))

        for s in sessions.sessionName:
            t = threading.Thread(target=my.save_data_as_csv, args=('https://api.neurosteer.com', s, q, len(query_list),))
            t.start()
            print('Saved: {} {}'.format(query_list[q], s))
            threads.append(t)

        for t in threads:
            t.join()  # wait for all threads to finish


    my.dataset.to_csv(r'neuro_data.csv')
    dataset = pd.read_csv(r'neuro_data.csv')
    train, test = train_test_split(dataset, test_size=0.15, random_state=0)
    train.to_csv('train_set.csv')
    test.to_csv('test_set.csv')

