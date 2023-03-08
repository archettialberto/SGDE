import tensorflow as tf
import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl


def residual_block_up(x: tf.Tensor, filters: int, name: str = ''):
    x1 = tfkl.UpSampling2D(interpolation='bilinear', name=name + 'up1')(x)
    x1 = tfkl.Conv2D(filters, 1, padding='same', name=name + 'conv1')(x1)

    x2 = tfkl.BatchNormalization(name=name + 'bn1')(x)
    x2 = tfkl.Activation('relu', name=name + 'act1')(x2)
    x2 = tfkl.UpSampling2D(interpolation='bilinear', name=name + 'up2')(x2)
    x2 = tfkl.Conv2D(filters, 3, padding='same', name=name + 'conv2')(x2)
    x2 = tfkl.BatchNormalization(name=name + 'bn2')(x2)
    x2 = tfkl.Activation('relu', name=name + 'act2')(x2)
    x2 = tfkl.Conv2D(filters, 3, padding='same', name=name + 'conv3')(x2)

    return tfkl.Add(name=name + 'add')([x1, x2])


def residual_block_down(x, filters, name=''):
    x1 = tfkl.AveragePooling2D(name=name + 'pool1')(x)
    x1 = tfkl.Conv2D(filters, 1, padding='same', name=name + 'conv1')(x1)

    x2 = tfkl.Activation('relu', name=name + 'act1')(x)
    x2 = tfkl.Conv2D(filters, 1, padding='same', name=name + 'conv2')(x2)
    x2 = tfkl.Activation('relu', name=name + 'act2')(x2)
    x2 = tfkl.Conv2D(filters, 3, padding='same', name=name + 'conv3')(x2)
    x2 = tfkl.Activation('relu', name=name + 'act3')(x2)
    x2 = tfkl.Conv2D(filters, 3, padding='same', name=name + 'conv4')(x2)
    x2 = tfkl.Activation('relu', name=name + 'act4')(x2)
    x2 = tfkl.AveragePooling2D(name=name + 'pool2')(x2)
    x2 = tfkl.Conv2D(filters, 1, padding='same', name=name + 'conv5')(x2)

    return tfkl.Add(name=name + 'add')([x1, x2])


def build_generator(output_shape, latent_dim, embedding_dim, num_classes, filters, blocks):
    assert output_shape[0] % 2 ** blocks == 0
    assert output_shape[1] % 2 ** blocks == 0
    initial_h = output_shape[0] // 2 ** blocks
    initial_w = output_shape[1] // 2 ** blocks
    initial_c = filters * 2 ** blocks

    input_layer1 = tfkl.Input(latent_dim)
    input_layer2 = tfkl.Input((1,), dtype=tf.int32)
    x2 = tfkl.Embedding(num_classes + 1, embedding_dim)(input_layer2)
    x2 = tfkl.Flatten()(x2)
    x = tfkl.Concatenate()([input_layer1, x2])
    x = tfkl.Dense(initial_h * initial_w * initial_c)(x)
    x = tfkl.Reshape((initial_h, initial_w, initial_c))(x)

    for b in range(blocks):
        x = residual_block_up(x, filters * 2 ** (blocks - 1 - b), name='block' + str(b + 1) + '_')

    x = tfkl.BatchNormalization(name='bn')(x)
    x = tfkl.Activation('relu', name='act')(x)
    x = tfkl.Conv2D(output_shape[-1], 3, padding='same', name='conv')(x)
    x = tfkl.Activation('sigmoid', name='act2')(x)

    generator = tfk.Model(inputs=[input_layer1, input_layer2], outputs=x)
    return generator


def build_discriminator(input_shape, latent_dim, embedding_dim, num_classes, filters, blocks):
    input_layer = tfkl.Input(input_shape)
    x = tfkl.Conv2D(filters, 3, padding='same', name='conv0')(input_layer)
    for b in range(blocks):
        x = residual_block_down(x, filters * 2 ** (b + 1), name='block' + str(b + 1) + '_')
    x = tfkl.Activation('relu', name='act')(x)
    x = tfkl.GlobalAveragePooling2D(name='gap')(x)

    embedding = tfkl.Input((1,), dtype=tf.int32)
    x2 = tfkl.Embedding(num_classes + 1, embedding_dim)(embedding)
    x2 = tfkl.Flatten()(x2)
    x = tfkl.Concatenate()([x, x2])

    output_layer = tfkl.Dense(1)(x)
    discriminator = tfk.Model(inputs=[input_layer, embedding], outputs=output_layer)
    return discriminator
