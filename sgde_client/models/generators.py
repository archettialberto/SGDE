import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl


def generator_block(x, filters: int, name: str = ""):
    x = tfkl.BatchNormalization(name=name + "bn")(x)
    x = tfkl.ReLU(name=name + "act")(x)
    x = tfkl.UpSampling2D(interpolation="bilinear", name=name + "up")(x)
    x = tfkl.Conv2D(filters, 3, padding="same", name=name + "conv")(x)

    return x


def build_generator(output_shape, latent_dim: int, filters: int, blocks: int):
    assert output_shape[0] % 2**blocks == 0
    assert output_shape[1] % 2**blocks == 0
    initial_h = output_shape[0] // 2**blocks
    initial_w = output_shape[1] // 2**blocks
    initial_c = filters * 2**blocks

    # Latent noise
    z = tfkl.Input(latent_dim, name="z")

    x = tfkl.Dense(initial_h * initial_w * initial_c, name="initial")(z)
    x = tfkl.Reshape((initial_h, initial_w, initial_c), name="reshape")(x)

    for b in range(blocks):
        x = generator_block(
            x, filters=filters * 2 ** (blocks - 1 - b), name="block" + str(b + 1) + "_"
        )

    x = tfkl.BatchNormalization(name="bn")(x)
    x = tfkl.ReLU(name="act")(x)
    x = tfkl.Conv2D(output_shape[-1], 3, padding="same", name="conv")(x)
    x = tfkl.Activation("tanh", name="tanh")(x)

    generator = tfk.Model(inputs=z, outputs=x, name="Generator")

    return generator


def discriminator_block(
    x,
    filters: int,
    name: str = "",
):
    x = tfkl.ReLU(name=name + "act2")(x)
    x = tfkl.AveragePooling2D(name=name + "pool")(x)
    x = tfkl.Conv2D(filters, 3, padding="same", name=name + "conv2")(x)

    return x


def build_discriminator(input_shape, filters: int, blocks: int):
    input_layer = tfkl.Input(input_shape, name="x")
    x = tf.keras.layers.RandomFlip(mode="horizontal")(input_layer)
    x = tfkl.Conv2D(filters, 3, padding="same", name="conv0")(x)

    for b in range(blocks):
        x = discriminator_block(
            x, filters * 2 ** (b + 1), name="block" + str(b + 1) + "_"
        )

    x = tfkl.ReLU(name="act")(x)
    x = tfkl.GlobalAveragePooling2D(name="gap")(x)
    x = tfkl.Dense(1, name="output")(x)

    discriminator = tfk.Model(inputs=input_layer, outputs=x, name="Discriminator")
    return discriminator


class ConditionalHingeGAN(tfk.Model):
    def __init__(
        self, discriminator, generator, latent_dim, num_classes, discriminator_rounds=1
    ):
        super(ConditionalHingeGAN, self).__init__()
        self.discriminator = discriminator
        self.generator = generator
        self.latent_dim = latent_dim
        self.discriminator_rounds = discriminator_rounds
        self.num_classes = num_classes

        self.loss_tracker = tfk.metrics.Mean(name="loss")
        self.d_loss_tracker = tfk.metrics.Mean(name="d_loss")
        self.g_loss_tracker = tfk.metrics.Mean(name="g_loss")

    def compile(self, d_optimizer, g_optimizer):
        super(ConditionalHingeGAN, self).compile()
        self.d_optimizer = d_optimizer
        self.g_optimizer = g_optimizer

    def loss_hinge_dis(self, dis_fake, dis_real):
        loss_real = tf.reduce_mean(tf.nn.relu(1.0 - dis_real))
        loss_fake = tf.reduce_mean(tf.nn.relu(1.0 + dis_fake))
        loss = loss_real + loss_fake
        return loss

    def loss_hinge_gen(self, dis_fake):
        loss = -tf.reduce_mean(dis_fake)
        return loss

    @property
    def metrics(self):
        return [self.loss_tracker, self.d_loss_tracker, self.g_loss_tracker]

    def call(self, inputs, training=False):
        return self.generator(inputs)

    @tf.function
    def train_step(self, data):
        real_samples, one_hot_labels = data
        batch_size = tf.shape(real_samples)[0]
        image_size = tf.shape(real_samples)[1]

        image_one_hot_labels = one_hot_labels[:, :, None, None]
        image_one_hot_labels = tf.repeat(
            image_one_hot_labels, repeats=[image_size * image_size]
        )
        image_one_hot_labels = tf.reshape(
            image_one_hot_labels, (-1, image_size, image_size, self.num_classes)
        )

        for i in range(self.discriminator_rounds):
            z = tf.random.normal(shape=(batch_size, self.latent_dim))
            generator_input = tf.concat([z, one_hot_labels], axis=-1)
            generated_samples = self.generator(generator_input, training=True)

            double_labels = tf.concat(
                [image_one_hot_labels, image_one_hot_labels], axis=0
            )
            combined_samples = tf.concat([generated_samples, real_samples], axis=0)
            discriminator_input = tf.concat([combined_samples, double_labels], axis=-1)

            # Train the discriminator
            with tf.GradientTape() as tape:
                predictions = self.discriminator(discriminator_input, training=True)
                D_fake, D_real = tf.split(predictions, [batch_size, batch_size], axis=0)
                d_loss = self.loss_hinge_dis(D_fake, D_real)
            grads = tape.gradient(d_loss, self.discriminator.trainable_weights)
            self.d_optimizer.apply_gradients(
                zip(grads, self.discriminator.trainable_weights)
            )

        loss = d_loss

        # Sample random points in the latent space
        z = tf.random.normal(shape=(batch_size, self.latent_dim))
        generator_input = tf.concat([z, one_hot_labels], axis=-1)

        # Train the generator
        with tf.GradientTape() as tape:
            generated_samples = self.generator(generator_input, training=True)
            discriminator_input = tf.concat(
                [generated_samples, image_one_hot_labels], axis=-1
            )
            misleading_predictions = self.discriminator(
                discriminator_input, training=True
            )
            g_loss = self.loss_hinge_gen(misleading_predictions)
        grads = tape.gradient(g_loss, self.generator.trainable_weights)
        self.g_optimizer.apply_gradients(zip(grads, self.generator.trainable_weights))

        loss += g_loss

        # Update metrics
        self.loss_tracker.update_state(loss)
        self.d_loss_tracker.update_state(d_loss)
        self.g_loss_tracker.update_state(g_loss)
        return {
            "loss": self.loss_tracker.result(),
            "d_loss": self.d_loss_tracker.result(),
            "g_loss": self.g_loss_tracker.result(),
        }


class ConditionalGANMonitor(tfk.callbacks.Callback):
    def __init__(self, num_img, num_classes, latent_dim, name="", gray=False):
        self.num_img = num_img
        self.latent_dim = latent_dim
        self.name = name
        self.gray = gray
        self.noise = tf.random.normal(shape=(self.num_img, self.latent_dim))
        self.labels = tfk.utils.to_categorical(
            tf.math.floormod(tf.range(0, self.num_img), num_classes)
        )

    def on_epoch_end(self, epoch, logs=None):
        generator_input = tf.concat([self.noise, self.labels], axis=-1)
        generated_images = self.model.generator.predict(generator_input, verbose=0)

        fig, axes = plt.subplots(1, self.num_img, figsize=(20, 2 * self.num_img))
        for i in range(self.num_img):
            img = tfk.preprocessing.image.array_to_img((generated_images[i] + 1) / 2)
            ax = axes[i % self.num_img]
            if self.gray:
                ax.imshow(np.squeeze(img), cmap="gray")
            else:
                ax.imshow(np.squeeze(img))
        plt.tight_layout()
        plt.show()
