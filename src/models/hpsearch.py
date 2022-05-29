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


def build_hps(hps_dict):
    """
    Create HyperParameters instance from hp dictionary
    """
    hps = kt.engine.hyperparameters.HyperParameters()
    for key in hps_dict:
        hp_type = hps_dict[key]['type'].lower()
        if hp_type == 'int':
            hps.Int(
            name = key,
            min_value = hps_dict[key]['min_value'],
            max_value = hps_dict[key]['max_value'],
            step= hps_dict[key].get('step', 1),
            sampling=hps_dict[key].get('sampling', None),
            default=hps_dict[key].get('default', None),
            parent_name=hps_dict[key].get('parent_name', None),
            parent_values=hps_dict[key].get('parent_values', None))
        elif hp_type == 'float':
            hps.Float(
            name = key,
            min_value = hps_dict[key]['min_value'],
            max_value = hps_dict[key]['max_value'],
            step= hps_dict[key].get('step', None),
            sampling=hps_dict[key].get('sampling', None),
            default=hps_dict[key].get('default', None),
            parent_name=hps_dict[key].get('parent_name', None),
            parent_values=hps_dict[key].get('parent_values', None))
        elif hp_type == 'fixed':
            hps.Fixed(name = key, 
                    value = hps_dict[key]['value'],
                    parent_name=hps_dict[key].get('parent_name', None),
                      parent_values=hps_dict[key].get('parent_values', None))
        else:
            raise Exception(f'Hyperparameter type {hp_type} not yet supported')
    return hps


@click.command()
@click.argument('data_path')
@click.argument('hps_space_dir')
@click.option('-pca', '--use_pca', is_flag=True, default=False, show_default=True, help='Apply pca transform to reject fluff')
def main(data_path, hps_space_dir, use_pca):
    """
    Args:
        data_path: data_path relative to the root directory
    """
    project_path = './'
    
    # Load Data
    X, y = prepare_data(data_path)
    _, num_targets, num_channels, timepoints_stimulus_duration = X.shape
    # flatten the trial and target dimensions
    X = X.reshape([-1, num_channels, timepoints_stimulus_duration])[..., np.newaxis]
    y = y.reshape([-1])
    logger.info((X.shape, y.shape))

    # Load hyperparameter search space
    optimal_hps_path = os.path.join(hps_space_dir, 'hps.yaml')
    hps_space_path = os.path.join(hps_space_dir, 'hpspace.json')
    with open(hps_space_path, 'r') as f:
        hps_dict = json.load(f)
    HPS = build_hps(hps_dict)
    
    # HPS Tuning
    tuner = kt.BayesianOptimization(
        objective=kt.Objective("val_loss", "min"),
        max_trials=10,
        hypermodel=EEGNet_SSVEP(nb_classes=num_targets, Chans=num_channels, Samples=timepoints_stimulus_duration),
        hyperparameters=HPS,
        overwrite=True,
        directory=os.path.join(project_path, 'logs', 'hps', os.path.basename(hps_space_dir))
    )
    
    tuner.search(X=X, y=y, use_pca=use_pca, verbose=1)
    best_hps = tuner.get_best_hyperparameters()[0]
    logger.info(best_hps.values)

    # Write optimal HPS to YAML file
    with open(optimal_hps_path, 'w', encoding='utf8') as outfile:
        hps_dict_out = {}
        for key, value in best_hps.values.items():
            hps_dict_out[key] = {'type':'fixed', 'value':value}
        yaml.dump(hps_dict_out, outfile, default_flow_style=False, allow_unicode=True)

    
if __name__ == '__main__':
    main()
