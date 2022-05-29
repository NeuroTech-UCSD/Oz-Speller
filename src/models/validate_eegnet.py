import logging
import click
import numpy as np
import pandas as pd
import yaml
import os
import pickle
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
tf.autograph.set_verbosity(
    1, alsologtostdout=False
)
from tensorflow.keras.callbacks import TensorBoard
import keras_tuner as kt
import json



from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from src.models.models import EEGNet_SSVEP
from src.models.utils import build_hps
from src.data.make_dataset import prepare_data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


@click.command()
@click.argument('data_path')
@click.argument('optimal_hps_path')
@click.argument('output_path')
@click.option('-pca', '--use_pca', is_flag=True, default=False, show_default=True, help='Apply pca transform to reject fluff')
def main(data_path, optimal_hps_path, output_path, use_pca):
    """
    Args:
        data_path: data_path relative to the root directory
        output_path: where the history of the training will be stored
    """
    project_path = './'
    
    # Load Data
    X, y = prepare_data(data_path)
    _, num_targets, num_channels, timepoints_stimulus_duration = X.shape
    # flatten the trial and target dimensions
    X = X.reshape([-1, num_channels, timepoints_stimulus_duration])[..., np.newaxis]
    y = y.reshape([-1])
    logger.info((X.shape, y.shape))
    
    # Load hyperparameter
    with open(optimal_hps_path, 'r') as f:
        hps_dict = yaml.safe_load(f)
    HPS = build_hps(hps_dict)
 
    # Start validation
    tf.keras.backend.clear_session()
    base_model = EEGNet_SSVEP(nb_classes=num_targets, Chans=num_channels, Samples=timepoints_stimulus_duration)
    base_model.fit(HPS, object, X, y, verbose=1, cache_learning=True, use_pca=use_pca)
    
    with open(output_path, 'wb') as handle:
        pickle.dump(base_model.history, handle, protocol=pickle.HIGHEST_PROTOCOL)

    
if __name__ == '__main__':
    main()
