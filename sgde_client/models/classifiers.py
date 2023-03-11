import tensorflow as tf
import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl


def build_resnet18(
        input_shape: tuple[int, int, int],
        num_classes: int,
        filters: int = 64,
        weight_decay: float = 2e-4
):
    input_layer = tfkl.Input(input_shape, name='input_layer')

    pad = input_shape[0] // 8
    padding = tfkl.ZeroPadding2D(padding=(pad, pad))(input_layer)
    crop = tfkl.RandomCrop(input_shape[0], input_shape[0])(padding)
    flip = tf.keras.layers.RandomFlip(mode='horizontal')(crop)

    x = tfkl.Conv2D(filters, 3, 2, padding='same', name='conv0')(flip)
    x = tfkl.BatchNormalization(name='bn0')(x)
    x = tfkl.ReLU(name='act0')(x)
    x = tfkl.Conv2D(filters * 2, 3, 2, padding='same', name='conv1')(x)
    x = tfkl.BatchNormalization(name='bn1')(x)
    x = tfkl.ReLU(name='act1')(x)
    x = tfkl.Conv2D(filters * 4, 3, 2, padding='same', name='conv2')(x)
    x = tfkl.BatchNormalization(name='bn2')(x)
    x = tfkl.ReLU(name='act2')(x)

    x = tfkl.GlobalAveragePooling2D()(x)
    x = tfkl.Dropout(0.5)(x)
    x = tfkl.Dense(num_classes, activation='softmax')(x)

    model = tfk.Model(inputs=input_layer, outputs=x, name='CNN')

    loss = tfk.losses.CategoricalCrossentropy()
    optimizer = tfk.optimizers.experimental.SGD(learning_rate=0.1, momentum=0.9, nesterov=True,
                                                weight_decay=weight_decay)

    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])

    return model
