import tensorflow as tf
tfk = tensorflow.keras
tfkl = tensorflow.keras.layers
from blocks import *

class ConditionalHingeGAN(tfk.Model):
    def __init__(self, discriminator, generator, latent_dim, discriminator_rounds=1):
        super(ConditionalHingeGAN, self).__init__()
        self.discriminator = discriminator
        self.generator = generator
        self.latent_dim = latent_dim
        self.discriminator_rounds = 1

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
        return [
            self.loss_tracker,
            self.d_loss_tracker,
            self.g_loss_tracker
        ]

    @tf.function
    def train_step(self, data):
        real_samples, labels = data
        batch_size = tf.shape(real_samples)[0]
        
        z = tf.random.normal(shape=(batch_size, self.latent_dim))
        generated_samples = self.generator([z,labels], training=True)
        double_labels = tf.concat([labels,labels],axis=0)
        combined_samples = tf.concat([generated_samples, real_samples],axis=0)
        
        for i in range(self.discriminator_rounds):
            # Train the discriminator
            with tf.GradientTape() as tape:
                predictions = self.discriminator([combined_samples,double_labels], training=True)
                D_fake, D_real = tf.split(predictions, [batch_size, batch_size], axis=0)
                d_loss = self.loss_hinge_dis(D_fake,D_real)
            grads = tape.gradient(d_loss, self.discriminator.trainable_weights)
            self.d_optimizer.apply_gradients(zip(grads, self.discriminator.trainable_weights))

        loss = d_loss

        # Sample random points in the latent space
        z = tf.random.normal(shape=(batch_size, self.latent_dim))

        # Train the generator 
        with tf.GradientTape() as tape:
            fake_samples = self.generator([z,labels], training=True)
            misleading_predictions = self.discriminator([fake_samples,labels], training=True)
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