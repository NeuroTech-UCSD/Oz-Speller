import logging
import click
import numpy as np
import pandas as pd
import yaml
import os
import pickle
import logging

import tensorflow as tf
import keras_tuner as kt
import json





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


    

    
