import tensorflow as tf
import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl

from metadata import *
from blocks import *
from gan import *


def train_generator(
        X,
        y=None,
        epochs=100,
        batch_size=128,
        conditioned=True,
        data_format='image',
        model_size='medium',
        task='classification',
        padding=False,
        verbose=1
):
    # TODO: Implementare controlli sulle epoche e sul batch size

    # Extract metadata
    metadata = metadata_extraction(
        data=X,
        labels=y,
        epochs=epochs,
        batch_size=batch_size,
        conditioned=conditioned,
        data_format=data_format,
        model_size=model_size,
        task=task
    )

    # Process data
    X, y = data_processing(metadata, X, y)

    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    dataset = dataset.shuffle(buffer_size=1024).batch(metadata['batch_size'])

    gan = ConditionalHingeGAN(
        generator=build_generator(
            output_shape=metadata['shape'][1:],
            latent_dim=metadata['latent_dim'],
            embedding_dim=metadata['embedding_dim'],
            num_classes=metadata['num_classes'],
            filters=metadata['filters'],
            blocks=metadata['blocks']
        ),
        discriminator=build_discriminator(
            input_shape=metadata['shape'][1:],
            latent_dim=metadata['latent_dim'],
            embedding_dim=metadata['embedding_dim'],
            num_classes=metadata['num_classes'],
            filters=metadata['filters'],
            blocks=metadata['blocks']
        ),
        latent_dim=metadata['latent_dim'],
        discriminator_rounds=metadata['discriminator_rounds']
    )
    gan.compile(
        d_optimizer=tfk.optimizers.Adam(learning_rate=metadata['leraning_rate'], beta_1=0, epsilon=1e-8),
        g_optimizer=tfk.optimizers.experimental.Adam(learning_rate=metadata['leraning_rate'], beta_1=0, epsilon=1e-8,
                                                     use_ema=True)
    )

    if verbose > 1:
        gan.generator.summary()
        gan.discriminator.summary()

    metadata['history'] = gan.fit(
        dataset,
        batch_size=metadata['batch_size'],
        epochs=metadata['epochs'],
        verbose=2
    ).history

    gan.generator.save('gan_gen_prova')
    gan.discriminator.save('gan_disc_prova')

    return metadata
