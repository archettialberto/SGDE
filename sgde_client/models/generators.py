import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl


class ZeroOneClipping(tfkl.Layer):
    def __init__(self, **kwargs):
        super(ZeroOneClipping, self).__init__(**kwargs)

    def call(self, inputs):
        # Clips the output between 0 and 1
        cropped_output = tf.clip_by_value(inputs, 0, 1)
        return cropped_output


def build_generator(
    output_shape, 
    latent_dim, 
    condition_dim,
    blocks=3,
    seed=42,
    **kwargs
):
    if len(output_shape) == 3: # Image
        return build_image_generator(output_shape,latent_dim,condition_dim[0],blocks,seed)                        
    elif len(output_shape) == 2: # Time Series
        return None  
    elif len(output_shape) == 1: # Tabular
        return build_tabular_generator(output_shape,latent_dim,condition_dim[0],blocks,seed)
    return None

def build_image_generator(
    output_shape, 
    latent_dim, 
    condition_dim,
    blocks,
    seed,
    **kwargs
):
    filters = 96
    assert output_shape[0] % 2**blocks == 0
    assert output_shape[1] % 2**blocks == 0
    initial_h = output_shape[0] // 2**blocks
    initial_w = output_shape[1] // 2**blocks
    initial_c = filters * 2**(blocks-1)

    z = tfkl.Input((latent_dim+condition_dim), name='z')

    x = tfkl.Dense(initial_h*initial_w*initial_c, name='dense0', use_bias=False, kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(z)
    x = tfkl.BatchNormalization(momentum=0.9, epsilon=1e-5, name='bn0')(x)
    x = tfkl.ReLU(name='relu0')(x)
    x = tfkl.Reshape((initial_h,initial_w,initial_c))(x)

    for b in range(blocks):
        if b > 0:
            dim = initial_h*initial_w*2**((b+1)*2)
            x_ = tfkl.Dense(dim, kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(z)
            x_ = tfkl.Reshape((int(np.sqrt(dim)),int(np.sqrt(dim)),1))(x_)
            x = tfkl.Conv2DTranspose(filters*2**(blocks-b-1), 3, 2, use_bias=False, padding='same', name='conv'+str(b+1)+'0', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
            x = tfkl.Concatenate(axis=-1)([x_,x])
        else:
            x = tfkl.Conv2DTranspose(filters*2**(blocks-b-1), 3, 2, use_bias=False, padding='same', name='conv'+str(b+1)+'0', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
        x = tfkl.BatchNormalization(momentum=0.9, epsilon=1e-5, name='bn'+str(b+1)+'0')(x)
        x = tfkl.ReLU(name='relu'+str(b+1)+'0')(x)
        x = tfkl.Conv2D(filters*2**(blocks-b-1), 3, padding='same', use_bias=False, name='conv'+str(b+1)+'1', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
        x = tfkl.BatchNormalization(momentum=0.9, epsilon=1e-5, name='bn'+str(b+1)+'1')(x)
        x = tfkl.ReLU(name='relu'+str(b+1)+'1')(x)

    output_layer = tfkl.Conv2D(output_shape[-1], 3, padding='same', use_bias=False, name='conv_out', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
    if output_shape[-1] == 3:
        output_layer = tfkl.Activation('sigmoid', name='sigmoid')(output_layer)
    else:
        output_layer = ZeroOneClipping(name='clipping')(output_layer)

    generator = tfk.Model(inputs=z, outputs=output_layer, name="Generator")
    return generator

def build_tabular_generator(
    output_shape, 
    latent_dim, 
    condition_dim,
    blocks,
    seed,
    **kwargs
):
    units = 32
    
    z = tfkl.Input((latent_dim+condition_dim), name='z')
    
    x = tfkl.Dense(units*2**blocks, name='dense0', use_bias=False, kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(z)
    x = tfkl.BatchNormalization(momentum=0.9, epsilon=1e-5, name='bn0')(x)
    x = tfkl.ReLU(name='relu0')(x)
    
    for b in range(blocks):
        x = tfkl.Dense(units*2**(blocks-b-1), name='dense'+str(b+1), use_bias=False, kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
        x = tfkl.BatchNormalization(momentum=0.9, epsilon=1e-5, name='bn'+str(b+1))(x)
        x = tfkl.ReLU(name='relu'+str(b+1))(x)
    
    x = tfkl.Dense(output_shape[-1], name='dense_out', use_bias=False, kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
    output_layer = tfkl.Activation('sigmoid', name='sigmoid')(x)
    generator = tfk.Model(inputs=z, outputs=output_layer, name="Generator")
    return generator


def build_discriminator(
    input_shape, 
    condition_dim,
    blocks=3,
    seed=42,
    **kwargs
):
    if len(input_shape) == 3: # Image
        return build_image_discriminator(input_shape,condition_dim[0],blocks,seed)                        
    elif len(input_shape) == 2: # Time Series
        return None  
    elif len(input_shape) == 1: # Tabular
        return build_tabular_discriminator(input_shape,condition_dim[0],blocks,seed) 
    return None

def build_image_discriminator(
    input_shape, 
    condition_dim,
    blocks,
    seed,
    **kwargs
):
    filters = 96
    
    input_layer = tfkl.Input((input_shape[0],input_shape[1],input_shape[2]+condition_dim), name='input_layer')
    
    x = tfkl.RandomFlip(mode='horizontal')(input_layer)
    x = tfkl.ZeroPadding2D(2, name='padding')(x)
    x = tfkl.RandomCrop(input_shape[0], input_shape[1], name='random_crop')(x)
    
    x1 = tfkl.Conv2D(filters, 3, padding='same', activation='relu', name='conv00', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
    x1 = tfkl.Conv2D(filters, 3, padding='same', activation='relu', name='conv01', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x1)
    x = tfkl.Concatenate(name='concat0')([x,x1])
    x = tfkl.MaxPooling2D(name='mp0')(x)
    
    for b in range(blocks-1):
        x1 = tfkl.Conv2D(filters*2**(b+1), 3, padding='same', activation='relu', name='conv'+str(b+1)+'0', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
        x1 = tfkl.Conv2D(filters*2**(b+1), 3, padding='same', activation='relu', name='conv'+str(b+1)+'1', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x1)
        x = tfkl.Concatenate(name='concat'+str(b+1))([x,x1])
        x = tfkl.MaxPooling2D(name='mp'+str(b+1))(x)
        
    x1 = tfkl.Conv2D(filters*2**(b+2), 3, padding='same', activation='relu', name='conv'+str(b+2)+'0', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
    x1 = tfkl.Conv2D(filters*2**(b+2), 3, padding='same', activation='relu', name='conv'+str(b+2)+'1', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x1)
    x1 = tfkl.Conv2D(filters*2**(b+2), 3, padding='same', activation='relu', name='conv'+str(b+2)+'2', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x1)
    x = tfkl.Concatenate(name='concat'+str(b+2))([x,x1])
    
    x = tfkl.GlobalAveragePooling2D(name='gap')(x)
    output_layer = tfkl.Dense(1, name='dense_out', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
    
    discriminator = tfk.Model(inputs=input_layer, outputs=output_layer, name='Discriminator')
    return discriminator

def build_tabular_discriminator(
    input_shape, 
    condition_dim,
    blocks,
    seed,
    **kwargs
):
    
    input_layer = tfkl.Input(input_shape[-1]+condition_dim, name='input_layer')
    
    x = tfkl.Dense(64, activation='relu', name='fc0', kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(input_layer)
    
    for b in range(blocks-1):
        x = tfkl.Dense(128, activation='relu', name='fc'+str(b+1), kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
        
    x = tfkl.Dense(256, activation='relu', name='fc'+str(b+2), kernel_initializer=tfk.initializers.TruncatedNormal(stddev=0.02, seed=seed))(x)
    
    output_layer = tfkl.Dense(1, name='output_layer')(x)
    discriminator = tfk.Model(inputs=input_layer, outputs=output_layer, name='Discriminator')
    return discriminator


class ConditionalHingeGAN(tfk.Model):
    def __init__(self, discriminator, generator, latent_dim, condition_dim, discriminator_rounds=1, data_structure='image', task="classification"):
        super(ConditionalHingeGAN, self).__init__()
        self.discriminator = discriminator
        self.generator = generator
        self.latent_dim = latent_dim
        self.discriminator_rounds = discriminator_rounds
        self.condition_dim = condition_dim
        self.tast = task

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
            self.d_loss_tracker,
            self.g_loss_tracker
        ]
    
    def call(self, inputs, training=False):
        return self.generator(inputs)

    @tf.function
    def train_step(self, data):
        real_samples, one_hot_labels = data
        batch_size = tf.shape(real_samples)[0]
        image_size = tf.shape(real_samples)[1]
        
        image_one_hot_labels = one_hot_labels[:, :, None, None]
        image_one_hot_labels = tf.repeat(image_one_hot_labels, repeats=[image_size * image_size])
        image_one_hot_labels = tf.reshape(image_one_hot_labels, (-1, image_size, image_size, self.condition_dim))
        
        for i in range(self.discriminator_rounds):
            
            z = tf.random.normal(shape=(batch_size, self.latent_dim))            
            generator_input = tf.concat([z,one_hot_labels],axis=-1)
            generated_samples = self.generator(generator_input, training=True)
            
            double_labels = tf.concat([image_one_hot_labels,image_one_hot_labels],axis=0)
            combined_samples = tf.concat([generated_samples, real_samples],axis=0)
            discriminator_input = tf.concat([combined_samples,double_labels],axis=-1)
            
            # Train the discriminator
            with tf.GradientTape() as tape:
                predictions = self.discriminator(discriminator_input, training=True)
                D_fake, D_real = tf.split(predictions, [batch_size, batch_size], axis=0)
                d_loss = self.loss_hinge_dis(D_fake,D_real)
            grads = tape.gradient(d_loss, self.discriminator.trainable_weights)
            self.d_optimizer.apply_gradients(zip(grads, self.discriminator.trainable_weights))

        loss = d_loss

        # Sample random points in the latent space
        z = tf.random.normal(shape=(batch_size, self.latent_dim))
        generator_input = tf.concat([z,one_hot_labels],axis=-1)

        # Train the generator 
        with tf.GradientTape() as tape:
            generated_samples = self.generator(generator_input, training=True)
            discriminator_input = tf.concat([generated_samples,image_one_hot_labels],axis=-1)
            misleading_predictions = self.discriminator(discriminator_input, training=True)
            g_loss = self.loss_hinge_gen(misleading_predictions)
        grads = tape.gradient(g_loss, self.generator.trainable_weights)
        self.g_optimizer.apply_gradients(zip(grads, self.generator.trainable_weights))

        # Update metrics
        self.d_loss_tracker.update_state(d_loss)
        self.g_loss_tracker.update_state(g_loss)
        return {
            "d_loss": self.d_loss_tracker.result(),
            "g_loss": self.g_loss_tracker.result(),
        }


class ConditionalGANMonitor(tfk.callbacks.Callback):
    def __init__(self, num_img, condition_dim, latent_dim, gray=False, task='classification'):
        self.num_img = num_img
        self.latent_dim = latent_dim
        self.gray = gray
        self.noise = tf.random.normal(shape=(self.num_img, self.latent_dim))
        if task == 'classification':
            self.labels = tfk.utils.to_categorical(tf.math.floormod(tf.range(0,self.num_img), condition_dim), num_classes=condition_dim)
        else:
            self.labels = tf.cast(tf.expand_dims(tf.linspace(0, 1, num_img),axis=-1), dtype='float32')
        
    def on_epoch_end(self, epoch, logs=None):
        generator_input = tf.concat([self.noise,self.labels],axis=-1)
        generated_images = self.model.generator.predict(generator_input,verbose=0)

        fig, axes = plt.subplots(1, self.num_img, figsize=(20,2*self.num_img))
        for i in range(self.num_img):
            img = tfk.preprocessing.image.array_to_img((generated_images[i]))
            ax = axes[i%self.num_img]
            if self.gray:
                ax.imshow(np.squeeze(img), cmap='gray')
            else:
                ax.imshow(np.squeeze(img))
        plt.tight_layout()
        plt.show()
