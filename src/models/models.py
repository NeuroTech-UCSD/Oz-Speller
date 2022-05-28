import numpy as np
import os
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
tf.autograph.set_verbosity(
    1, alsologtostdout=False
)
import keras_tuner as kt
from sklearn.model_selection import StratifiedKFold
import time



project_dir = './'
num_gpus = len(tf.config.list_physical_devices('GPU'))

class EEGNet_SSVEP(kt.HyperModel):
    def __init__(self, nb_classes, Chans, Samples):
        super().__init__()
         # Cache training process in history 
        self.history = {'loss':[], 'val_loss':[], 'acc':[], 'val_acc':[]}
        self.nb_classes = nb_classes
        self.Chans = Chans
        self.Samples = Samples
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_virtual_device_configuration(gpu,[tf.config.experimental.VirtualDeviceConfiguration(memory_limit=8000)])
                
#         tf.debugging.set_log_device_placement(True)
#         gpus = tf.config.list_logical_devices('GPU')
#         self.strategy = tf.distribute.MirroredStrategy(gpus)

    def build(self, hps):
        """ SSVEP Variant of EEGNet, as used in [1]. 
        Inputs:

          nb_classes      : int, number of classes to classify
          Chans, Samples  : number of channels and time points in the EEG data
          dropoutRate     : dropout fraction
          kernLength      : length of temporal convolution in first layer
          F1, F2          : number of temporal filters (F1) and number of pointwise
                            filters (F2) to learn. 
          D               : number of spatial filters to learn within each temporal
                            convolution.
          dropoutType     : Either SpatialDropout2D or Dropout, passed as a string.


        [1]. Waytowich, N. et. al. (2018). Compact Convolutional Neural Networks
        for Classification of Asynchronous Steady-State Visual Evoked Potentials.
        Journal of Neural Engineering vol. 15(6). 
        http://iopscience.iop.org/article/10.1088/1741-2552/aae5d8
        """

        nb_classes = self.nb_classes
        Chans = self.Chans
        Samples = self.Samples
        dropoutRate = hps.get('dropoutRate')
        kernLength = hps.get('kernLength')
        F1 = hps.get('F1')
        D = hps.get('D')
        F2 = F1 * D
        dropoutType = 'Dropout'


        if dropoutType == 'SpatialDropout2D':
            dropoutType = tf.keras.layers.SpatialDropout2D
        elif dropoutType == 'Dropout':
            dropoutType = tf.keras.layers.Dropout
        else:
            raise ValueError('dropoutType must be one of SpatialDropout2D '
                             'or Dropout, passed as a string.')

        input1   = tf.keras.Input(shape = (Chans, Samples, 1))

        ##################################################################
        block1       = tf.keras.layers.Conv2D(F1, (1, kernLength), padding = 'same',
                                       input_shape = (Chans, Samples, 1),
                                       use_bias = False)(input1)
        block1       = tf.keras.layers.BatchNormalization()(block1)
        block1       = tf.keras.layers.DepthwiseConv2D((Chans, 1), use_bias = False, 
                                       depth_multiplier = D,
                                       depthwise_constraint = tf.keras.constraints.max_norm(1.))(block1)
        block1       = tf.keras.layers.BatchNormalization()(block1)
        block1       = tf.keras.layers.Activation('elu')(block1)
        block1       = tf.keras.layers.AveragePooling2D((1, 4))(block1)
        block1       = dropoutType(dropoutRate)(block1)

        block2       = tf.keras.layers.SeparableConv2D(F2, (1, 16),
                                       use_bias = False, padding = 'same')(block1)
        block2       = tf.keras.layers.BatchNormalization()(block2)
        block2       = tf.keras.layers.Activation('elu')(block2)
        block2       = tf.keras.layers.AveragePooling2D((1, 8))(block2)
        block2       = dropoutType(dropoutRate)(block2)

        flatten      = tf.keras.layers.Flatten(name = 'flatten')(block2)

        dense        = tf.keras.layers.Dense(nb_classes, name = 'dense')(flatten)
        softmax      = tf.keras.layers.Activation('softmax', name = 'softmax')(dense)

        return tf.keras.Model(inputs=input1, outputs=softmax)
            
            
    def fit(self, hps, model, X, y, callbacks=[], verbose=0, cache_learning=False, **kwargs):
        '''
        model is ignored as we have to construct new model for each fold
        Args:
          
        '''
        assert type(callbacks) == list
        
        
        patience = hps.get('patience')
        batch_size = hps.get('batchSize')
        learning_rate = hps.get('learningRate')
        epochs = hps.get('epochs')      

        num_folds = 10
        kf = StratifiedKFold(n_splits=num_folds)
        val_loss_folds = np.empty([num_folds])
        val_acc_folds = np.empty([num_folds])
        for i, (train_index, test_index) in enumerate(kf.split(X, y)):
            print(f'{i + 1} / {num_folds} fold')
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            
            # clear global states to release some GPU memory for keeping states
            tf.keras.backend.clear_session()
            
            # Add early stopping to callbacks
            earlyStopping = tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=patience,  # change to higher to get better loss
                verbose=0,
                mode="auto"
            )
            callbacks.append(earlyStopping)

#             with self.strategy.scope():
            
            model = self.build(hps)
            model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss='sparse_categorical_crossentropy', metrics=['acc'])
            
            train_ds = tf.data.Dataset.from_tensor_slices((X_train, y_train)).batch(batch_size).prefetch(1)
            val_ds = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(batch_size).prefetch(1)
            start = time.time()
            history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, verbose=verbose, callbacks=callbacks)
            print(time.time() - start)
            
            # keep track of the loweset validation loss and its corresponding acc
            min_idx = np.argmin(history.history['val_loss'])
            val_loss_folds[i] = history.history['val_loss'][min_idx]
            val_acc_folds[i] = history.history['val_acc'][min_idx]
            
            # cache learning curve
            if cache_learning:
                self.history['loss'].append(history.history['loss'])
                self.history['val_loss'].append(history.history['val_loss'])
                self.history['acc'].append(history.history['acc'])
                self.history['val_acc'].append(history.history['val_acc'])
            
        overall_val_loss = val_loss_folds.mean()
        overall_val_acc = val_acc_folds.mean()
        return {"val_loss": overall_val_loss, "val_acc": overall_val_acc}