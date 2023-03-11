import os.path
from datetime import datetime

import numpy as np

import tensorflow as tf
import tensorflow.keras as tfk
import tf2onnx
from sklearn.model_selection import train_test_split

from schemas import GeneratorCreate
from sgde_client.models.classifiers import build_resnet18
from sgde_client.models.generators import ConditionalHingeGAN, build_generator, build_discriminator, \
    ConditionalGANMonitor
from sgde_client.models.utils import metadata_extraction, data_processing, scheduler


def train_image_generator(
        name: str,
        description: str,
        X: np.array,
        y: np.array = None,
        epochs: int = 500,
        batch_size: int = 128,
        image_size: int = 32,
        model_size: str = '',
        task: str = '',
        sub_task: str = '',
        data_description: str = '',
        dataset_name: str = '',
        verbose: int = 1,
        classification_epochs=100,
        path: str = None
) -> tuple[str, dict, GeneratorCreate]:

    # Extract metadata
    if verbose > 0: print('Metadata extraction started...')
    metadata = metadata_extraction(
        X=X,
        y=y,
        epochs=epochs,
        batch_size=batch_size,
        image_size=image_size,
        model_size=model_size,
        task=task,
        sub_task=sub_task,
        data_description=data_description,
        dataset_name=dataset_name,
        data_format='image'
    )
    metadata['name'] = name
    metadata['description'] = description
    parsed_metadata = GeneratorCreate(**metadata)
    if verbose > 0: print('Metadata extraction completed!')

    # Process data
    if verbose > 0: print('Data processing started...')
    X, y = data_processing(metadata, X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, stratify=np.argmax(y, axis=1))

    dataset_train = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    dataset_train = dataset_train.shuffle(buffer_size=1024).batch(metadata['batch_size'])

    dataset_test = tf.data.Dataset.from_tensor_slices((X_test, y_test))
    dataset_test = dataset_test.shuffle(buffer_size=1024).batch(metadata['batch_size'])
    if verbose > 0: print('Data processing completed!')

    # Train a classifier on real data
    if verbose > 0: print('Classifier training on real data started...')
    '''
    real_classifier = build_resnet18(metadata['generator_output_shape'][1:], metadata['num_classes'])
    metadata['classifier_real_history'] = real_classifier.fit(
        dataset_train,
        validation_data=dataset_test,
        batch_size=128,
        epochs=classification_epochs,
        verbose=2,
        callbacks=[tfk.callbacks.LearningRateScheduler(scheduler)]
    ).history

    metadata['classifier_real_best_accuracy'] = max(metadata['classifier_real_history']['val_accuracy'])
    '''
    if verbose > 0: print('Classifier training on real data completed!')

    # Build the generator
    if verbose > 0: print('Generator building started...')
    gan = ConditionalHingeGAN(
        generator=build_generator(
            output_shape=metadata['generator_output_shape'][1:],
            latent_dim=metadata['generator_input_shape'],
            filters=metadata['filters'],
            blocks=metadata['blocks']
        ),
        discriminator=build_discriminator(
            input_shape=metadata['discriminator_input_shape'][1:],
            filters=metadata['filters'],
            blocks=metadata['blocks']
        ),
        latent_dim=metadata['latent_dim'],
        discriminator_rounds=metadata['discriminator_rounds'],
        num_classes=metadata['num_classes']
    )
    gan.compile(
        d_optimizer=tfk.optimizers.Adam(
            learning_rate=2e-4,
            beta_1=0.5,
            beta_2=0.999,
            epsilon=1e-6
        ),
        g_optimizer=tfk.optimizers.Adam(
            learning_rate=5e-5,
            beta_1=0.5,
            beta_2=0.999,
            epsilon=1e-6,
        )
    )
    cb = [ConditionalGANMonitor(10, metadata['num_classes'], metadata['latent_dim'], gray=True)]
    if verbose > 0: print('Generator building completed!')

    # Train the generator
    if verbose > 0: print('Generator training started...')
    '''
    metadata['history'] = gan.fit(
        dataset_train,
        batch_size=metadata['batch_size'],
        epochs=metadata['epochs'],
        verbose=2,
        callbacks=cb
    ).history
    '''
    if verbose > 0: print('Generator training completed!')

    # Save the generator
    if verbose > 0: print('Generator saving started...')
    # gan.generator.save('gan_gen_prova')
    # gan.discriminator.save('gan_disc_prova')

    if path is None:
        path = os.path.join(os.getcwd(), f"{name}_{datetime.utcnow().strftime('%y%m%d%H%M%S')}.onnx")

    # TODO fix input shape
    model_proto, _ = tf2onnx.convert.from_keras(
        gan,
        input_signature=(tf.TensorSpec((None, 74), tf.float32, name="input"),),
        opset=13,
        output_path=path
    )

    metadata['model'] = gan
    if verbose > 0: print('Generator saving completed!')
    '''

    # Generate a dataset
    if verbose > 0: print('Sampling started...')
    noise = tf.random.normal(shape=(len(X_train), metadata['latent_dim']))
    labels = tfk.utils.to_categorical(
        tf.cast(tf.math.floormod(tf.range(0, len(X_train)), metadata['num_classes']), 'float32'))
    generator_input = tf.concat([noise, labels], axis=-1)
    generated_samples = gan.generator.predict(generator_input, batch_size=metadata['batch_size'], verbose=0)
    dataset_gen = tf.data.Dataset.from_tensor_slices((generated_samples, labels))
    dataset_gen = dataset_gen.shuffle(buffer_size=1024).batch(metadata['batch_size'])
    if verbose > 0: print('Sampling completed!')

    # Compute similarity metrics
    if verbose > 0: print('Similarity metrics computation started...')
    temp_generated_samples = ((generated_samples + 1) / 2 * 255).astype(np.int32)
    generated_mean = np.expand_dims(np.mean(temp_generated_samples, axis=0), axis=0)
    temp_real_samples = ((X_train + 1) / 2 * 255).astype(np.int32)
    real_mean = np.expand_dims(np.mean(temp_real_samples, axis=0), axis=0)
    metadata['SSIM'] = tf.image.ssim(generated_mean, real_mean, max_val=255)
    if verbose > 0: print('Similarity metrics computation completed!')

    # Train a classifier on generated data
    if verbose > 0: print('Classifier training on generated data started...')
    gen_classifier = build_resnet18(metadata['generator_output_shape'][1:], metadata['num_classes'])
    metadata['classifier_gen_history'] = gen_classifier.fit(
        dataset_train,
        validation_data=dataset_test,
        batch_size=128,
        epochs=classification_epochs,
        verbose=2,
        callbacks=[tfk.callbacks.LearningRateScheduler(scheduler)]
    ).history

    metadata['classifier_gen_best_accuracy'] = max(metadata['classifier_gen_history']['val_accuracy'])
    if verbose > 0: print('Classifier training on generated data completed!')
    '''

    return path, metadata, parsed_metadata
