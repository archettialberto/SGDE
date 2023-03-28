import numpy as np
import onnxruntime as rt
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.keras as tfk


def generate_samples_onnx(num_samples, path, input_shape, num_classes=None, verbose=0):
    if num_classes is None:
        gen_input = tf.random.normal(shape=(num_samples, input_shape))
    else:
        noise = tf.random.normal(shape=(num_samples, input_shape - num_classes))
        labels = tfk.utils.to_categorical(
            tf.cast(tf.math.floormod(tf.range(0, num_samples), num_classes), "float32")
        )
        gen_input = np.array(tf.concat([noise, labels], axis=-1))

    so = rt.SessionOptions()
    so.log_severity_level = 3
    so.intra_op_num_threads = 1
    so.inter_op_num_threads = 1
    session = rt.InferenceSession(path, so)
    generated_images = session.run(None, {"z": gen_input})[0]
    if verbose > 0:
        fig, axes = plt.subplots(1, 10, figsize=(20, 2 * 10))
        for i in range(10):
            img = tfk.preprocessing.image.array_to_img(generated_images[i])
            ax = axes[i % 10]
            ax.imshow(np.squeeze(img), cmap="gray")
        plt.tight_layout()
        plt.show()

    return generated_images
