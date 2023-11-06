import tensorflow as tf
import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl


def build_model(
    input_shape,
    output_shape,
    task,
    seed=42,
    **kwargs
):
    if len(input_shape) == 3: # Image
        if task == 'classification':
            return build_image_classifier(input_shape, output_shape, seed)            
        else:
            return build_image_regressor(input_shape, output_shape, seed) 
    elif len(input_shape) == 1: # Tabular
        if task == 'classification':
            return build_tabular_classifier(input_shape, output_shape, seed)            
        else:
            return build_tabular_regressor(input_shape, output_shape, seed) 
    return None

def build_image_regressor(
    input_shape,
    output_shape,
    seed,
    **kwargs
):
    input_layer = tfkl.Input(input_shape, name='input_layer')
    
    x = tf.keras.layers.RandomFlip(mode='horizontal', name='random_flip')(input_layer)
    x = tfkl.ZeroPadding2D(2, name='padding')(x)
    x = tfkl.RandomCrop(input_shape[0], input_shape[1], name='random_crop')(x)
    
    x1 = tfkl.Conv2D(64, 3, padding='same', name='conv11')(x)
    x1 = tfkl.BatchNormalization(name='bn11')(x1)
    x1 = tfkl.ReLU(name='relu11')(x1)
    x1 = tfkl.Conv2D(64, 3, padding='same', name='conv12')(x1)
    x1 = tfkl.BatchNormalization(name='bn12')(x1)
    x1 = tfkl.ReLU(name='relu12')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat1')([x,x1])
    x = tfkl.MaxPooling2D(name='mp1')(x)
    x1 = tfkl.Conv2D(128, 3, padding='same', name='conv21')(x)
    x1 = tfkl.BatchNormalization(name='bn21')(x1)
    x1 = tfkl.ReLU(name='relu21')(x1)
    x1 = tfkl.Conv2D(128, 3, padding='same', name='conv22')(x1)
    x1 = tfkl.BatchNormalization(name='bn22')(x1)
    x1 = tfkl.ReLU(name='relu22')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat2')([x,x1])
    x = tfkl.MaxPooling2D(name='mp2')(x)
    x1 = tfkl.Conv2D(256, 3, padding='same', name='conv31')(x)
    x1 = tfkl.BatchNormalization(name='bn31')(x1)
    x1 = tfkl.ReLU(name='relu31')(x1)
    x1 = tfkl.Conv2D(256, 3, padding='same', name='conv32')(x1)
    x1 = tfkl.BatchNormalization(name='bn32')(x1)
    x1 = tfkl.ReLU(name='relu32')(x1)
    x1 = tfkl.Conv2D(256, 3, padding='same', name='conv33')(x1)
    x1 = tfkl.BatchNormalization(name='bn33')(x1)
    x1 = tfkl.ReLU(name='relu33')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat3')([x,x1])
    x = tfkl.MaxPooling2D(name='mp3')(x)
    x1 = tfkl.Conv2D(512, 3, padding='same', name='conv41')(x)
    x1 = tfkl.BatchNormalization(name='bn41')(x1)
    x1 = tfkl.ReLU(name='relu41')(x1)
    x1 = tfkl.Conv2D(512, 3, padding='same', name='conv42')(x1)
    x1 = tfkl.BatchNormalization(name='bn42')(x1)
    x1 = tfkl.ReLU(name='relu42')(x1)
    x1 = tfkl.Conv2D(512, 3, padding='same', name='conv43')(x1)
    x1 = tfkl.BatchNormalization(name='bn43')(x1)
    x1 = tfkl.ReLU(name='relu43')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat4')([x,x1])
    
    x = tfkl.GlobalAveragePooling2D(name='gap')(x)
    x = tfkl.Dropout(0.5, seed=seed, name='dropout')(x)
    output_layer = tfkl.Dense(output_shape[-1], activation='tanh', name='output_layer')(x)
    
    model = tfk.Model(inputs=input_layer, outputs=output_layer, name='CNN')
    
    loss = tfk.losses.MeanSquaredError()
    optimizer = tfk.optimizers.Adam()
    
    model.compile(loss=loss, optimizer=optimizer, metrics=['mae'])
    
    return model
    
def build_tabular_regressor(
    input_shape,
    output_shape,
    seed,
    **kwargs
):
    input_layer = tfkl.Input(input_shape, name='input_layer')
    
    x = tfkl.Dense(64, activation='relu', name='fc1')(input_layer)
    x = tfkl.Dense(128, activation='relu', name='fc2')(x)
    x = tfkl.Dense(256, activation='relu', name='fc3')(x)
    
    x = tfkl.Dropout(0.5, seed=seed, name='dropout')(x)
    output_layer = tfkl.Dense(output_shape[-1], activation='tanh', name='output_layer')(x)
    
    model = tfk.Model(inputs=input_layer, outputs=output_layer, name='FFNN')
    
    loss = tfk.losses.MeanSquaredError()
    optimizer = tfk.optimizers.Adam()
    
    model.compile(loss=loss, optimizer=optimizer, metrics=['mae'])
    
    return model
    
def build_image_classifier(
    input_shape,
    output_shape,
    seed,
    **kwargs
):
    input_layer = tfkl.Input(input_shape, name='input_layer')
    
    x = tf.keras.layers.RandomFlip(mode='horizontal', name='random_flip')(input_layer)
    
    x1 = tfkl.Conv2D(64, 3, padding='same', name='conv11', kernel_initializer=tfk.initializers.HeNormal())(x)
    x1 = tfkl.BatchNormalization(name='bn11')(x1)
    x1 = tfkl.ReLU(name='relu11')(x1)
    x1 = tfkl.Conv2D(64, 3, padding='same', name='conv12', kernel_initializer=tfk.initializers.HeNormal())(x1)
    x1 = tfkl.BatchNormalization(name='bn12')(x1)
    x1 = tfkl.ReLU(name='relu12')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat1')([x,x1])
    x = tfkl.MaxPooling2D(name='mp1')(x)
    x1 = tfkl.Conv2D(128, 3, padding='same', name='conv21', kernel_initializer=tfk.initializers.HeNormal())(x)
    x1 = tfkl.BatchNormalization(name='bn21')(x1)
    x1 = tfkl.ReLU(name='relu21')(x1)
    x1 = tfkl.Conv2D(128, 3, padding='same', name='conv22', kernel_initializer=tfk.initializers.HeNormal())(x1)
    x1 = tfkl.BatchNormalization(name='bn22')(x1)
    x1 = tfkl.ReLU(name='relu22')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat2')([x,x1])
    x = tfkl.MaxPooling2D(name='mp2')(x)
    x1 = tfkl.Conv2D(256, 3, padding='same', name='conv31', kernel_initializer=tfk.initializers.HeNormal())(x)
    x1 = tfkl.BatchNormalization(name='bn31')(x1)
    x1 = tfkl.ReLU(name='relu31')(x1)
    x1 = tfkl.Conv2D(256, 3, padding='same', name='conv32', kernel_initializer=tfk.initializers.HeNormal())(x1)
    x1 = tfkl.BatchNormalization(name='bn32')(x1)
    x1 = tfkl.ReLU(name='relu32')(x1)
    x1 = tfkl.Conv2D(256, 3, padding='same', name='conv33', kernel_initializer=tfk.initializers.HeNormal())(x1)
    x1 = tfkl.BatchNormalization(name='bn33')(x1)
    x1 = tfkl.ReLU(name='relu33')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat3')([x,x1])
    x = tfkl.MaxPooling2D(name='mp3')(x)
    x1 = tfkl.Conv2D(512, 3, padding='same', name='conv41', kernel_initializer=tfk.initializers.HeNormal())(x)
    x1 = tfkl.BatchNormalization(name='bn41')(x1)
    x1 = tfkl.ReLU(name='relu41')(x1)
    x1 = tfkl.Conv2D(512, 3, padding='same', name='conv42', kernel_initializer=tfk.initializers.HeNormal())(x1)
    x1 = tfkl.BatchNormalization(name='bn42')(x1)
    x1 = tfkl.ReLU(name='relu42')(x1)
    x1 = tfkl.Conv2D(512, 3, padding='same', name='conv43', kernel_initializer=tfk.initializers.HeNormal())(x1)
    x1 = tfkl.BatchNormalization(name='bn43')(x1)
    x1 = tfkl.ReLU(name='relu43')(x1)
    x = tfkl.Concatenate(axis=-1, name='concat4')([x,x1])
    
    x = tfkl.GlobalAveragePooling2D(name='gap')(x)
    x = tfkl.Dropout(0.5, seed=seed, name='dropout')(x)
    output_layer = tfkl.Dense(output_shape[-1], activation='softmax', name='output_layer', kernel_initializer=tfk.initializers.GlorotNormal())(x)
    
    model = tfk.Model(inputs=input_layer, outputs=output_layer, name='CNN')
    
    loss = tfk.losses.CategoricalCrossentropy()
    optimizer = tfk.optimizers.Adam()
    
    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
    
    return model
    
def build_tabular_classifier(
    input_shape,
    output_shape,
    seed,
    **kwargs
):
    input_layer = tfkl.Input(input_shape, name='input_layer')
    
    x = tfkl.Dense(64, activation='relu', name='fc1')(input_layer)
    x = tfkl.Dense(128, activation='relu', name='fc2')(x)
    x = tfkl.Dense(256, activation='relu', name='fc3')(x)
    
    x = tfkl.Dropout(0.5, seed=seed, name='dropout')(x)
    output_layer = tfkl.Dense(output_shape[-1], activation='softmax', name='output_layer')(x)
    
    model = tfk.Model(inputs=input_layer, outputs=output_layer, name='FFNN')
    
    loss = tfk.losses.CategoricalCrossentropy()
    optimizer = tfk.optimizers.Adam()
    
    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
    
    return model