import numpy as np
from keras import Sequential
from keras.layers import Dropout, Dense
from keras import optimizers
from keras.callbacks import TensorBoard
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import itertools
import warnings
warnings.filterwarnings("ignore")



"""THIS MODULE RUNS ON PYTHON 3.6"""


class NeuroLearnANN(object):

    # Initialising the ANN
    def __init__(self):
        self.classifier = Sequential()

        # Adding the input layer and the first hidden layer
        self.classifier.add(Dropout(0.05))
        self.classifier.add(Dense(activation='relu', input_dim=121, units=600, kernel_initializer='glorot_uniform'))

        # Adding the second hidden layer
        self.classifier.add(Dropout(0.25))
        self.classifier.add(Dense(units=600, kernel_initializer="glorot_uniform", activation='relu'))

        # Adding the third hidden layer
        self.classifier.add(Dropout(0.25))
        self.classifier.add(Dense(units=600, kernel_initializer="glorot_uniform", activation='relu'))

        # Adding the output layer
        self.classifier.add(Dense(units=4, kernel_initializer='glorot_uniform', activation='softmax'))

        # Compiling the ANN
        sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)  # slower but generalizes better
        adam = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999)  # faster
        self.classifier.compile(optimizer=sgd, loss='categorical_crossentropy', metrics=['categorical_accuracy'])

    def load_data(self):
        # Loading the dataset and spliting  into train and validation
        dataset = pd.read_csv(r'train_set.csv')
        X = dataset.iloc[:, 2:123].values
        y = dataset.iloc[:, 123:].values
        #
        # Splitting the dataset into the Training set and Test set
        self.X_train, self.X_validation, self.y_train, self.y_validation = train_test_split(X, y, test_size=0.2, random_state=0)

    def train(self):

        # to view tensorboard after training open anaconda prompt in project's folder and run:
        # tensorboard --logdir ./ --host localhost --port 8088
        # now open in your browser: http://localhost:8088
        tbCallBack = TensorBoard(log_dir='./Graph', histogram_freq=0,
                                    write_graph=True, write_images=True)


        # Fitting the ANN to the Training set
        # you may use history to view accuracy
        self.history = self.classifier.fit(self.X_train, self.y_train, validation_data=(self.X_validation, self.y_validation),
                                           batch_size=10, nb_epoch=1000, shuffle=True, callbacks=[tbCallBack])
        self.save_graphs()

    def predict(self):
        # Predicting the Test set results
        dataset = pd.read_csv(r'test_set.csv')
        X = dataset.iloc[:, 2:123].values
        y = dataset.iloc[:, 123:].values

        self.y_pred = self.classifier.predict(X)

        # Making the Confusion Matrix
        y_test_non_category = [np.argmax(t) for t in y]
        y_predict_non_category = [np.argmax(t) for t in self.y_pred]
        self.cm = confusion_matrix(y_test_non_category, y_predict_non_category)


    def plot_confusion_matrix(self, cm, target_names, title='Confusion matrix', cmap=None, normalize=True):

        accuracy = np.trace(cm) / float(np.sum(cm))
        misclass = 1 - accuracy

        if cmap is None:
            cmap = plt.get_cmap('Blues')

        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()

        if target_names is not None:
            tick_marks = np.arange(len(target_names))
            plt.xticks(tick_marks, target_names, rotation=45)
            plt.yticks(tick_marks, target_names)

        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        thresh = cm.max() / 1.5 if normalize else cm.max() / 2
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            if normalize:
                plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                         horizontalalignment="center",
                         color="white" if cm[i, j] > thresh else "black")
            else:
                plt.text(j, i, "{:,}".format(cm[i, j]),
                         horizontalalignment="center",
                         color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.gcf().subplots_adjust(bottom=0.3)
        plt.ylabel('True label')
        plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
        plt.savefig(r'plots\Confusion Matrix.jpg')


    def save_graphs(self):
        epochs = self.history.epoch
        plt.plot(epochs, self.history.history['val_categorical_accuracy'], label='val_acc')
        plt.plot(epochs, self.history.history['categorical_accuracy'], label='train_acc')
        plt.legend()
        plt.xlabel('epochs')
        plt.ylabel('Accuracy')
        plt.title('Validation Accuracy={0:.4f}\nTraining Accuracy={1:.4f}'.format(self.history.history['val_categorical_accuracy'][-1],
                                                                                  self.history.history['categorical_accuracy'][-1]))
        plt.savefig(r'plots\Accuracy.jpg')
        plt.close()

        plt.plot(epochs, self.history.history['val_loss'], label='val_loss')
        plt.plot(epochs, self.history.history['loss'], label='train_loss')
        plt.legend()
        plt.xlabel('epochs')
        plt.ylabel('Loss')
        plt.title('Validation Loss={0:.4f}\nTraining Loss={1:.4f}'.format(self.history.history['val_loss'][-1],
                                                                          self.history.history['loss'][-1]))
        plt.savefig(r'plots\Loss.jpg')
        plt.close()


if __name__ == "__main__":
    model = NeuroLearnANN()
    model.load_data()
    model.train()
    model.predict()
    model.plot_confusion_matrix(model.cm, ['Memory game', 'Meditate', 'Write with weak hand', 'Happy music (dancing)'])
    model.classifier.save('NeuroClassifier.h5')

    print('Done!')

