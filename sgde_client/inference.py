import os
import shutil
from datetime import datetime

import numpy as np
import onnx
from onnx_tf.backend import prepare

import tensorflow as tf
import tensorflow.keras as tfk

from schemas import Generator


def generate_data(
    model_path: str, metadata: Generator, num_samples: int = 1
) -> np.array:
    tmp_folder = os.path.join(
        os.getcwd(), f"tmp_{datetime.utcnow().strftime('%y%m%d%H%M%S')}"
    )
    os.makedirs(tmp_folder, exist_ok=True)
    model = onnx.load(model_path)
    tf_model_path = os.path.join(tmp_folder, f"tmp_model")
    prepare(model).export_graph(tf_model_path)
    model = tf.saved_model.load(tf_model_path)
    shutil.rmtree(tmp_folder)

    # TODO update api metadata to better suit this fn
    noise = tf.random.normal(shape=(num_samples, 73))
    labels = tfk.utils.to_categorical(
        tf.cast(tf.math.floormod(tf.range(0, num_samples), 10), "float32")
    )
    generator_input = tf.concat([noise, labels], axis=-1, name="input")

    # TODO update this fn to non-image stuff
    generated_samples = ((model(generator_input) + 1) / 2 * 255).astype(np.int32)

    return generated_samples
