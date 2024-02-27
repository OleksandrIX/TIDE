from tensorflow.keras.models import model_from_json
import tensorflow as tf


def load_model(model_architecture_path, model_weights_path):
    json_file = open(model_architecture_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()

    loaded_model = tf.keras.models.model_from_json(loaded_model_json)
    loaded_model.load_weights(model_weights_path)
    return loaded_model
