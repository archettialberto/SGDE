import numpy as np

import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl


def scheduler(epoch, lr):
    if epoch == 60:
        return lr*0.01
    if epoch == 80:
        return lr*0.01
    else:
        return lr


def metadata_extraction(
        X,
        y=np.array([]),
        epochs=500,
        batch_size=128,
        image_size=32,
        model_size='small',
        task='classification',
        sub_task='',
        data_description='',
        dataset_name='',
        data_format='image'
):
    metadata = {}

    # DATASET
    metadata['dataset_name'] = dataset_name
    metadata['data_description'] = data_description
    metadata['data_format'] = data_format
    metadata['raw_shape'] = X.shape

    if metadata['data_format'] == 'image':
        if len(X.shape) > 4 or len(X.shape) < 3:
            print(f'ABORT: {X.shape} is not a proper shape for an image dataset')
            return -1
        elif len(X.shape) == 3:
            metadata['shape'] = (X.shape[0], image_size, image_size, 1)
        else:
            metadata['shape'] = (X.shape[0], image_size, image_size, X.shape[-1])
    else:
        return -1

    # LABELS
    if y.size != 0:
        assert len(X) == len(y)
        assert len(y.shape) == 1 or (len(y.shape) == 2 and y.shape[1] == 1)
        metadata['conditioned'] = True
        metadata['labels_shape'] = y.shape
        if task == 'classification':
            metadata['task'] = task
            metadata['classes'] = np.unique(y)
            metadata['num_classes'] = len(np.unique(y))
        else:
            metadata['task'] = None

    else:
        metadata['conditioned'] = False
        metadata['task'] = None
    metadata['sub_task'] = sub_task

    # GENERATIVE MODEL
    metadata['model_size'] = model_size
    metadata['epochs'] = epochs
    metadata['batch_size'] = batch_size

    metadata['discriminator_rounds'] = 3

    if model_size == 'small':
        metadata['blocks'] = 2
        metadata['filters'] = 32
        metadata['latent_dim'] = 64
    elif model_size == 'large':
        metadata['blocks'] = 4
        metadata['filters'] = 64
        metadata['latent_dim'] = 128
    else:
        metadata['blocks'] = 3
        metadata['filters'] = 32
        metadata['latent_dim'] = 128

    # TASK
    metadata['task'] = task
    metadata['sub_task'] = sub_task

    return metadata


def data_processing(metadata, data, labels=np.array([])):
    # Make the image dataset with 4 dimensions
    if len(metadata['raw_shape']) == 3 and metadata['data_format'] == 'image':
        data = np.expand_dims(data, axis=-1)

    # Make the image dataset squared
    print('\t Dataset reshaping started...')
    dim = min(data.shape[1:-1])
    data = data[:, (data.shape[1] - dim) // 2:(data.shape[1] + dim) // 2,
           (data.shape[2] - dim) // 2:(data.shape[2] + dim) // 2, :]
    print('\t Dataset reshaping completed!')

    # Resize the image dataset
    print('\t Dataset resizing started...')
    resize = tfkl.Resizing(metadata['shape'][1], metadata['shape'][2])
    data = resize(data).numpy()
    print('\t Dataset resizing completed!')

    # Save data minimum and maximum
    metadata['data_min'] = data.min()
    metadata['data_max'] = data.max()

    # Normalize in range [-1,1]
    print('\t Dataset normalization started...')
    data = ((data - metadata['data_min']) / (metadata['data_max'] - metadata['data_min']) * 2 - 1).astype(np.float32)
    print('\t Dataset normalization completed!')

    if labels.size != 0:
        labels = tfk.utils.to_categorical(labels)
        if metadata['conditioned']:
            metadata['generator_input_shape'] = (metadata['latent_dim'] + metadata['num_classes'])
            metadata['generator_output_shape'] = metadata['shape']
            metadata['discriminator_input_shape'] = list(metadata['shape'])
            metadata['discriminator_input_shape'][-1] += metadata['num_classes']
            metadata['discriminator_input_shape'] = tuple(metadata['discriminator_input_shape'])
            metadata['discriminator_output_shape'] = (1,)
    return data, labels
