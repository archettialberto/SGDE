import json
import os
import os.path
from datetime import datetime

import numpy as np

import tensorflow as tf
import tensorflow.keras as tfk
import tf2onnx
from sklearn.model_selection import train_test_split

from sgde_client.models.classifiers import build_model
from sgde_client.models.generators import (
    ConditionalHingeGAN,
    build_generator,
    build_discriminator,
    ConditionalGANMonitor,
)
from sgde_client.models.utils import metadata_extraction, data_processing



def gafi_fit(
    X_train,
    y_train,
    X_test,
    y_test,
    gan,
    model_real,
    gan_callbacks,
    callbacks,
    metadata,
    task="classification"
):
    if metadata['task'] == 'classification':
        metadata['best_score'] = 0
    else:
        metadata['best_score'] = 1e10
        metric = tfk.losses.MeanAbsoluteError(reduction=tf.keras.losses.Reduction.NONE)
        metadata['tolerance'] = 5

    metadata['best_epoch'] = 0
    
    for e in range(metadata['gan_epochs']):
        print(f"EPOCH {e+1}/{metadata['gan_epochs']}")

        gan.fit(
        X_train,
        y_train, 
        batch_size=metadata['batch_size'], 
        epochs=1, 
        verbose=2,
        callbacks=gan_callbacks
        )
        if e+1 >= metadata['sleep_epochs']:
            if task == 'classification':
                good_samples = np.array([])
                good_labels = np.array([])
                bad_labels = np.array([])
                while(len(good_samples)<len(X_train)*0.1):

                    noise = tf.random.normal(shape=(len(X_train)-len(good_samples), metadata['latent_dim']))
                    if len(good_samples) == 0:
                        labels = tfk.utils.to_categorical(tf.math.floormod(tf.range(0,len(X_train)), metadata['labels_shape'][0]), num_classes=metadata['labels_shape'][0])
                    else:
                        labels = bad_labels

                    generator_input = tf.concat([noise,labels],axis=-1)
                    generated_data = gan.generator.predict(generator_input,batch_size=metadata['batch_size'],verbose=0)

                    predictions = model_real.predict(generated_data,batch_size=metadata['batch_size'],verbose=0)

                    index = np.argmax(predictions,axis=1) == np.argmax(labels,axis=1)
                    if len(good_samples) == 0:
                        good_samples = generated_data[index]
                        good_labels = labels[index]
                    else:
                        good_samples = np.concatenate((good_samples,generated_data[index]),axis=0)
                        good_labels = np.concatenate((good_labels,labels[index]),axis=0)

                    index = np.argmax(predictions,axis=1) != np.argmax(labels,axis=1)
                    bad_labels = labels[index]
                    
                    if metadata['verbose'] > 1:
                        print(f"Synthetic dataset completeness: {round(len(good_samples)/len(X_train)*100,4)}%")
                        
                model = build_model(metadata['dataset_shape'],metadata['labels_shape'],metadata['task'],metadata['seed'])

                model.fit(
                    good_samples,
                    good_labels,
                    validation_data=[X_test,y_test],
                    batch_size=metadata['batch_size'],
                    epochs=metadata['model_epochs'],
                    verbose=0,
                    callbacks=callbacks
                ).history

                score = model.evaluate(X_test,y_test,verbose=0)
                print(f"CAS: {round(score[1],4)} (Real Accuracy: {round(metadata['best_score_real'],4)})\n")
                if(metadata['best_score'] < score[1]):
                    
                    metadata['best_score'] = score[1]
                    metadata['best_epoch'] = e+1
                    
                    gan.generator.save(metadata['generator_path'])
                    spec = (tf.TensorSpec((None, metadata['latent_dim']+metadata['labels_shape'][0]), tf.float32, name="z"),)
                    output_path = metadata['generator_path']+'/model.onnx'
                    _, __ = tf2onnx.convert.from_keras(gan, input_signature=spec, opset=13, output_path=output_path) 
                    
                    model.save(metadata['synt_predictor_path'])
                    spec = (tf.TensorSpec(((None,) + metadata['dataset_shape']), tf.float32, name="input_layer"),)
                    output_path = metadata['synt_predictor_path']+'/model.onnx'
                    _, __ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13, output_path=output_path) 
                    
                del model

            else:
                good_samples = np.array([])
                good_labels = np.array([])
                bad_labels = np.array([])
                while(len(good_samples)<len(X_train)):

                    noise = tf.random.normal(shape=(len(X_train)-len(good_samples), metadata['latent_dim']))
                    if len(good_samples) == 0:
                        labels = tf.random.uniform(shape=(len(X_train), 1), minval=-1, maxval=1, dtype=tf.dtypes.float32)
                    else:
                        labels = bad_labels

                    generator_input = tf.concat([noise,labels],axis=-1)
                    generated_data = gan.generator.predict(generator_input,batch_size=metadata['batch_size'],verbose=0)

                    predictions = model_real.predict(generated_data,batch_size=metadata['batch_size'],verbose=0)
                    predictions_scores = metric(labels,predictions)

                    index = (predictions_scores <= metadata['best_score_real'] * metadata['tolerance']).numpy()
                    if len(good_samples) == 0:
                        good_samples = generated_data[index]
                        good_labels = labels[index]
                    else:
                        good_samples = np.concatenate((good_samples,generated_data[index]),axis=0)
                        good_labels = np.concatenate((good_labels,labels[index]),axis=0)

                    index = (predictions_scores > metadata['best_score_real'] * metadata['tolerance']).numpy()
                    bad_labels = labels[index]

                    if metadata['verbose'] > 1:
                        print(f"Synthetic dataset completeness: {round(len(good_samples)/len(X_train)*100,4)}%")


                model = build_model(metadata['dataset_shape'],metadata['labels_shape'],metadata['task'],metadata['seed'])

                model.fit(
                    good_samples,
                    good_labels,
                    validation_data=[X_test,y_test],
                    batch_size=metadata['batch_size'],
                    epochs=metadata['model_epochs'],
                    verbose=0,
                    callbacks=callbacks
                ).history

                score = model.evaluate(X_test,y_test,verbose=0)
                print(f"Generative MAE: {round(score[1], 4)} (Real MAE: {round(metadata['best_score_real'], 4)})\n")
                if(metadata['best_score'] > score[1]):

                    metadata['best_score'] = score[1]
                    metadata['best_epoch'] = e+1

                    gan.generator.save(metadata['generator_path'])
                    spec = (tf.TensorSpec((None, metadata['latent_dim']+metadata['labels_shape'][0]), tf.float32, name="z"),)
                    output_path = metadata['generator_path']+'/model.onnx'
                    _, __ = tf2onnx.convert.from_keras(gan, input_signature=spec, opset=13, output_path=output_path)

                    model.save(metadata['synt_predictor_path'])
                    spec = (tf.TensorSpec(((None,) + metadata['dataset_shape']), tf.float32, name="input_layer"),)
                    output_path = metadata['synt_predictor_path']+'/model.onnx'
                    _, __ = tf2onnx.convert.from_keras(gan, input_signature=spec, opset=13, output_path=output_path)

                del model


def train_generator(
    X,
    y,
    gan_epochs=500,
    model_epochs=200,
    sleep_epochs=100,
    batch_size=256,
    data_structure='image',
    task='classification',
    sub_task='',
    dataset_name='',
    data_description='',
    name="",
    verbose=1,
    find_best_threshold=False,
    find_best_std=False,
    **kwargs
):
    ####################
    # Extract metadata #
    ####################
    if verbose > 0: print("Metadata extraction started...")
        
    metadata = metadata_extraction(
        X=X, 
        y=y, 
        gan_epochs=gan_epochs,
        model_epochs=model_epochs,
        sleep_epochs=sleep_epochs,
        batch_size=batch_size,
        data_structure=data_structure,
        task=task,
        sub_task=sub_task,
        dataset_name=dataset_name,
        data_description=data_description,
        verbose=verbose
    )

    metadata["name"] = name
    
    if metadata['verbose'] > 0: print("Metadata extraction completed!")
    
    ##################
    # Pre-processing #
    ##################
    if metadata['verbose'] > 0: print("Data pre-processing started...")
        
    X, y = data_processing(X, y, metadata)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=metadata['seed'], test_size=.1, stratify=np.argmax(y,axis=1))
    
    if metadata['verbose'] > 0: print("Data pre-processing completed!")
    
    ###################################
    # Train a classifier on real data #
    ###################################
    if metadata['verbose'] > 0: print("Classifier training on real data started...")  
        
    model_real = build_model(metadata['dataset_shape'],metadata['labels_shape'],metadata['task'],metadata['seed'])
    
    if metadata['task'] == 'classification':
        callbacks = [
            tfk.callbacks.EarlyStopping(monitor='val_accuracy', patience=15, restore_best_weights=True, mode='auto'),
            tfk.callbacks.ReduceLROnPlateau(monitor="val_accuracy", factor=0.1, patience=10, min_lr=1e-5, mode='auto')
        ]
        metadata['metric'] = 'accuracy'
    elif metadata['task'] == 'regression':
        callbacks = [
            tfk.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, mode='auto'),
            tfk.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=10, min_lr=1e-5, mode='auto')
        ]
        metadata['metric'] = 'mean absolute error'
    
    classifier_real_history = model_real.fit(
        X_train,
        y_train,
        validation_data=[X_test,y_test],
        batch_size=metadata['batch_size'],
        epochs=metadata['model_epochs'],
        verbose=2,
        callbacks=callbacks
    ).history
    
    model_real.save(metadata['real_predictor_path'])
    spec = (tf.TensorSpec(((None,) + metadata['dataset_shape']), tf.float32, name="input_layer"),)
    output_path = metadata['real_predictor_path']+'/model.onnx'
    _, __ = tf2onnx.convert.from_keras(model_real, input_signature=spec, opset=13, output_path=output_path) 
    
    if metadata['task'] == 'classification':
        metadata['best_score_real'] = max(classifier_real_history['val_accuracy'])
    elif metadata['task'] == 'regression':
        metadata['best_score_real'] = min(classifier_real_history['val_loss']) 
        
    if metadata['verbose'] > 0: print("Classifier training on real data completed!") 
        
    #######################    
    # Build the generator #
    #######################
    if metadata['verbose'] > 0: print("Generator building started...")  
    
    gan = ConditionalHingeGAN(
        generator = build_generator(metadata['dataset_shape'],metadata['latent_dim'],metadata['labels_shape']), 
        discriminator = build_discriminator(metadata['dataset_shape'],metadata['labels_shape']), 
        latent_dim = metadata['latent_dim'],
        condition_dim = metadata['labels_shape'][0],
        discriminator_rounds = metadata['discriminator_rounds'],
        data_structure = metadata['data_structure']
    )
    
    gan.compile(
        d_optimizer = tfk.optimizers.AdamW(learning_rate=2e-4),
        g_optimizer = tfk.optimizers.AdamW(learning_rate=1e-4, use_ema=True)
    )
    
    if metadata['data_structure'] == 'image' and metadata['verbose'] > 0:
        gan_callbacks = [ConditionalGANMonitor(10, metadata['labels_shape'][0], metadata['latent_dim'], gray=(metadata['dataset_shape'][-1] == 1), task=metadata['task'])]
    else:
        gan_callbacks = []
        
    if metadata['verbose'] > 0: print("Generator building completed!") 
        
    ##############################################    
    # Train the generator with the GaFi pipeline #
    ##############################################    
    if metadata['verbose'] > 0: print("Generator training started...")      
        
    gafi_fit(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        gan=gan,
        model_real=model_real,
        gan_callbacks=gan_callbacks,
        callbacks=callbacks,
        metadata=metadata
    )    
    
    if metadata['verbose'] > 0: print("Generator training completed!")    
      
    
    #############################################    
    # Compute the best threshold for generation #
    #############################################   
    if metadata['verbose'] > 0: print("Best threshold computation started...")   
        
    metadata['best_threshold'] = 1. 
    # TO BE COMPLETED
    
    if metadata['verbose'] > 0: print("Best threshold computation completed!") 
    
    ######################################################    
    # Compute the best standard deviation for generation #
    ###################################################### 
    if metadata['verbose'] > 0: print("Best standard deviation computation started...")  
        
    metadata['best_std'] = 1. 
    # TO BE COMPLETED
    
    if metadata['verbose'] > 0: print("Best standard deviation computation completed!") 
    
    metadata['dataset_min'] = list(metadata['dataset_min'])
    metadata['dataset_max'] = list(metadata['dataset_max'])

    metadata["base_path"] = metadata["generator_path"]
    metadata["generator_path"] = metadata["base_path"] + "/model.onnx"
    if "real_predictor_path" in metadata:
        metadata["real_predictor_path"] = metadata["real_predictor_path"] + "/model.onnx"
    metadata["metadata_path"] = metadata["base_path"] + "/metadata.json"

    for k, v in metadata.items():
        if type(v) == tuple:
            metadata[k] = list(metadata[k])
        if type(v) == np.float32:
            metadata[k] = float(metadata[k])
        if type(v) == list:
            for i, e in enumerate(metadata[k]):
                if type(e) == np.float32:
                    metadata[k][i] = float(metadata[k][i])

    with open(metadata["metadata_path"], "w") as f:
        json.dump(metadata, f)

    return metadata
