import tensorflow as tf
import tensorflow.keras as tfk
import numpy as np
import onnxruntime as rt

rt.set_default_logger_severity(3)


def generate_samples_onnx(
        num_samples: int,
        metadata: dict,
        filter_model: bool = True,
        verbose=0
):
    path = metadata['generator_path']
    latent_dim = metadata['latent_dim']
    labels_shape = metadata['labels_shape']
    task = metadata['task']
    filter_path = None
    if filter_model and "real_predictor_path" in metadata:
        filter_path = metadata['real_predictor_path']
    verbose = 1

    so = rt.SessionOptions()
    so.log_severity_level = 3
    so.intra_op_num_threads = 1
    so.inter_op_num_threads = 1
    session = rt.InferenceSession(path, so, providers=['AzureExecutionProvider', 'CPUExecutionProvider'])

    if not filter_model:
        if task == 'classification':
            noise = tf.random.normal(shape=(num_samples, latent_dim))
            labels = tfk.utils.to_categorical(
                tf.cast(tf.math.floormod(tf.range(0, num_samples), labels_shape[0]), 'float32'),
                num_classes=labels_shape[0])
            generator_input = tf.concat([noise, labels], axis=-1).numpy()
            generated_data = session.run(["output_1"], {"z": generator_input})[0]
            return generated_data, labels
    else:
        if task == 'classification':
            good_samples = np.array([])
            good_labels = np.array([])
            bad_labels = np.array([])
            while (len(good_samples) < num_samples):

                noise = tf.random.normal(shape=(num_samples - len(good_samples), latent_dim))

                if len(good_samples) == 0:
                    labels = tfk.utils.to_categorical(
                        tf.cast(tf.math.floormod(tf.range(0, num_samples), labels_shape[0]), 'float32'),
                        num_classes=labels_shape[0])
                else:
                    labels = bad_labels

                generator_input = tf.concat([noise, labels], axis=-1).numpy()
                generated_data = session.run(["output_1"], {"z": generator_input})[0]

                so_classifier = rt.SessionOptions()
                so_classifier.log_severity_level = 3
                so_classifier.intra_op_num_threads = 1
                so_classifier.inter_op_num_threads = 1
                session_classifier = rt.InferenceSession(filter_path, so_classifier,
                                                         providers=['AzureExecutionProvider', 'CPUExecutionProvider'])

                predictions = session_classifier.run(["output_layer"], {"input_layer": generated_data})[0]

                index = np.argmax(predictions, axis=1) == np.argmax(labels, axis=1)

                if len(good_samples) == 0:
                    good_samples = generated_data[index]
                    good_labels = labels[index]
                else:
                    good_samples = np.concatenate((good_samples, generated_data[index]), axis=0)
                    good_labels = np.concatenate((good_labels, labels[index]), axis=0)

                index = np.argmax(predictions, axis=1) != np.argmax(labels, axis=1)
                bad_labels = labels[index]

                if verbose > 0:
                    print(f"Synthetic dataset completeness: {round(len(good_samples) / num_samples * 100, 4)}%")
            return good_samples, good_labels
