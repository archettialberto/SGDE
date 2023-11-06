import os
from datetime import datetime

import numpy as np


def metadata_extraction(
    X,
    y,
    gan_epochs,
    model_epochs,
    sleep_epochs,
    batch_size,
    data_structure,
    task,
    sub_task,
    dataset_name,
    data_description,
    verbose
):
    
    metadata = {} 
    
    metadata['dataset_length'] = len(X)  
    metadata['labels_length'] = len(y)
    assert metadata['dataset_length'] == metadata['labels_length'], 'X and y must have the same length.'

    metadata['data_structure'] = data_structure
    assert metadata['data_structure'] in ['image', 'tabular'], 'The current allowed data structures are \'image\' and \'tabular\'.'
    
    metadata['dataset_shape'] = X.shape[1:]
    if metadata['data_structure'] == 'image':
        assert len(metadata['dataset_shape']) == 3, 'Invalid data shape. Image data must have shape equal to (None, Height, Width, Channels).'
        assert metadata['dataset_shape'][0] >= 32 and metadata['dataset_shape'][1] >= 32, 'Invalid data shape. Both the height and the width must be greater than or equal to 32.'
    elif metadata['data_structure'] == 'tabular':
        assert len(metadata['dataset_shape']) == 1, 'Invalid data shape. Tabular data must have shape equal to (None, Features).'
    
    metadata['task'] = task
    assert metadata['task'] in ['classification', 'regression'], 'The current allowed tasks are \'classification\' and \'regression\'.'          
    
    metadata['gan_epochs'] = gan_epochs
    metadata['model_epochs'] = model_epochs
    metadata['batch_size'] = batch_size
    
    metadata['data_description'] = data_description
    metadata['dataset_name'] = dataset_name
    metadata['verbose'] = verbose
    
    metadata['seed'] = 42
    metadata['latent_dim'] = 128
    metadata['discriminator_rounds'] = 3
    metadata['sleep_epochs'] = min(sleep_epochs,gan_epochs)
    
    metadata['main_path'] = metadata['dataset_name']+'_'+metadata['data_structure']+'_'+metadata['task']+'_'+datetime.today().strftime('%Y%m%d_%H%M')
    os.makedirs(metadata['main_path'], exist_ok=True)
    
    metadata['generator_path'] = metadata['main_path'] + '/generator'
    os.makedirs(metadata['generator_path'], exist_ok=True)
    
    if metadata['task'] == 'classification':
        metadata['predictor_path'] = metadata['main_path'] + '/classifiers'
        os.makedirs(metadata['predictor_path'], exist_ok=True)
        metadata['real_predictor_path'] = metadata['predictor_path']+'/real_classifier'
        metadata['synt_predictor_path'] = metadata['predictor_path']+'/synt_classifier'
    else:
        metadata['predictor_path'] = metadata['main_path'] + '/regressors'
        os.makedirs(metadata['predictor_path'], exist_ok=True)
        metadata['real_predictor_path'] = metadata['predictor_path']+'/real_classifier'
        metadata['synt_predictor_path'] = metadata['predictor_path']+'/synt_classifier'
    
    return metadata


def data_processing(
    X,
    y,
    metadata
):
    
    if metadata['data_structure'] == 'image':
        metadata['dataset_min'] = X.min(axis=(0,1,2))
        metadata['dataset_max'] = X.max(axis=(0,1,2))
    elif metadata['data_structure'] == 'tabular':
        metadata['dataset_min'] = X.min(axis=0)
        metadata['dataset_max'] = X.max(axis=0)
    
    X = (X - metadata['dataset_min'])/(metadata['dataset_max']-metadata['dataset_min']).astype(np.float32)
        
    if metadata['task'] == 'regression':
        metadata['labels_min'] = y.min()
        metadata['labels_max'] = y.max()
        y = (y - metadata['labels_min'])/(metadata['labels_max']-metadata['labels_min']).astype(np.float32)
    
    metadata['labels_shape'] = y.shape[1:]
    
    return X, y