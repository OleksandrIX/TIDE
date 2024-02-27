import os
import tensorflow
from yaml import load, FullLoader
from loguru import logger


def compile_model(model):
    path = os.path.abspath("config.yml")
    config = load(open(path, "rb"), Loader=FullLoader)

    optimizer = tensorflow.keras.optimizers.Adam(learning_rate=config["learning_rate"])
    model.compile(optimizer=optimizer,
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    logger.info("Model compiled.")
    return model
