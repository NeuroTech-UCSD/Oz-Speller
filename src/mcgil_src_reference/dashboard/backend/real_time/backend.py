#!/usr/bin/env python

from multiprocessing import Process, Queue, Lock
from data import *
import numpy as np
import sys
sys.path.append('NeuroTech-ML/')
from pylsl import StreamInlet, resolve_stream
import time

from real_time_class import Prediction
from prediction_server import PredictionServer

def keyboard_producer(queue):
    while True:
        # key = repr(readchar.readkey())[1:-1]
        key = repr(input())[1:-1]
        queue.put(key)
        if key == "\\x03":
            exit()

def ml_producer(queue):

    BUFFER_SIZE_SECONDS = 0.5
    BUFFER_DIST_SECONDS = 0.5
    OPENBCI_HERTZ = 250
    BUFFER_SIZE = round(OPENBCI_HERTZ * BUFFER_SIZE_SECONDS)
    BUFFER_DIST = round(OPENBCI_HERTZ * BUFFER_DIST_SECONDS)
    FEATURES = ['var']
    DEBUG = True

    # model_file = 'NeuroTech-ML/models/model_windows_date_all_subject_all_mode_1_2_4_groups_ok_good.pkl'
    model_file = 'NeuroTech-ML/models/knn_final_500ms.pkl'
    bci_buffer = np.zeros([8, 1])
    # predictor = Prediction(model_filename=model_file, shift=BUFFER_DIST/BUFFER_SIZE)
    predictor = Prediction(model_filename=model_file, shift=BUFFER_DIST_SECONDS)

    print("Attempting to connect to OpenBCI. Please make sure OpenBCI is open with LSL enabled.")

    # Set up streaming over lsl from OpenBCI. 0 picks up the first of three
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    while True:
        # Pull and append sample from OpenBCI to buffer
        sample, timestamp = inlet.pull_sample()
        sample_np = np.array([sample]).transpose()
        bci_buffer = np.append(bci_buffer, sample_np, axis=1)

        # Check if buffer is large enough to make a prediction
        if (bci_buffer.shape[1] == BUFFER_SIZE):
            # Build filter buffer
            timestamp = round(time.time() * 1000)

            filter_buffer, feature_dict, finger_probs = predictor.get_filtered_features_prediction(
                np.array(bci_buffer))

            # Predict finger pressed
            finger_index = np.argmax(finger_probs)
            formatted_feature_dict = {}
            formatted_feature_dict["timestamp"] = timestamp

            # construct feature dictionary for frontend
            for feature in FEATURES:
                feature_array = []
                for i in range(1, 9):
                    # [0] because elements of feature_dict array of length 1
                    feature_array.append(
                        feature_dict["channel " + str(i) + "_" + feature][0])

                formatted_feature_dict[feature] = feature_array

            # Push predictions to queue
            queue.put(
                {
                    'Finger': int(finger_index),
                    'FingerProbs': str(finger_probs[0].tolist()),
                    'Feature_Data': formatted_feature_dict,
                    'Filtered_Signal_Data': {
                "data": str(filter_buffer[:, (BUFFER_SIZE - 1)].tolist()),
                "timestamp": timestamp
                        }
                })

            if (DEBUG):
                print(finger_probs[0])

            # Remove BUFFER_DIST from beginning of buffer
            bci_buffer = np.delete(bci_buffer, np.arange(0, BUFFER_DIST, 1), 1)


def consumer(queue, server_mode, finger_mode):

    word_groupings = PredictionServer.get_finger_number_to_word_map(top_10000_words)
    prediction_server = PredictionServer(queue, word_groupings, server_mode=server_mode, finger_mode=finger_mode)
    prediction_server.startServer()


if __name__ == "__main__":
    # server mode means emit instruction over socketIO
    server_mode = True

    # finger mode is the opposite of keyboard mode
    # finger mode means prediction mode
    finger_mode = True

    queue = Queue()

    consumer = Process(target=consumer, args=(queue, server_mode, finger_mode))
    consumer.daemon = True
    consumer.start()

    if finger_mode:
        ml_producer(queue)
    else:
        keyboard_producer(queue)

    consumer.join()
