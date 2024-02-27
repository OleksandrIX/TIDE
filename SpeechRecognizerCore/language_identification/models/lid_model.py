import os
import shutil
import time
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from loguru import logger

from language_identification.config.lid_config import LanguageIdentificationSettings
from language_identification.utils.spectrogram import generate_spectrogram
from language_identification.utils.data_loader import load_dataset, image_loader


class CNNModel(nn.Module):
    def __init__(self, amount_language: int):
        super(CNNModel, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()
        self.fc1 = nn.Linear(60 * 60 * 128, 1000)
        self.fc2 = nn.Linear(1000, amount_language)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.reshape(x.size(0), -1)
        x = self.fc1(x)
        x = self.fc2(x)
        return x


class LidModelTrainAndTest:
    """
    Class for training and testing language identification model
    """

    def __init__(self, device: str = torch.device("cuda" if torch.cuda.is_available() else "cpu")):
        lid_settings = LanguageIdentificationSettings()
        self.data_loader = None
        self.device = device
        self.epochs = lid_settings.lid_model["lid_model_train_settings"]["epochs"]
        self.batch_size = lid_settings.lid_model["lid_model_train_settings"]["batch_size"]
        self.train_data_dir = lid_settings.get_train_data_path_abs
        self.test_data_dir = lid_settings.get_test_data_path_abs
        self.models_dir_path = lid_settings.models_dir_path

    def train_model(self) -> None:
        """
        Trains the model on the training data and saves checkpoints and final version model in models_dir
        """
        train_loader = load_dataset(self.train_data_dir, self.batch_size)

        model = CNNModel(amount_language=len(train_loader.dataset.classes)).to(self.device)
        loss = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters())

        loss_history = []
        accuracy_history = []
        performance = [0]
        batches = len(train_loader)

        time_string = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime())
        model_dir = Path().joinpath(self.models_dir_path, time_string)
        os.mkdir(model_dir)
        shutil.copy(Path(lid_settings.lid_settings_path, "config.yml"),
                    Path.joinpath(model_dir, "config.yml"))
        logger.add(Path(model_dir, "train-lid-model.log"), level="TRACE")
        logger.info(f"Created model directory: {model_dir}")
        logger.info(f"Copied config file to {model_dir}")
        logger.info(f"Total epochs: {self.epochs}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Classes: {train_loader.dataset.classes}")
        logger.info(f"Total files for train: {len(train_loader.dataset.imgs)}")

        for epoch in range(0, self.epochs):
            correct_train, total_train, error_train = 0, 0, 0
            for step, (images, labels) in enumerate(train_loader):
                images = images.to(self.device)
                labels = labels.to(self.device)

                outputs = model(images)
                error = loss(outputs, labels)
                loss_history.append(error.item())

                optimizer.zero_grad()
                error.backward()
                optimizer.step()

                total = labels.size(0)
                _, predicted = torch.max(outputs.data, 1)
                correct = (predicted == labels).sum().item()
                accuracy_history.append(correct / total)

                correct_train += correct
                error_train += error
                total_train += total

                logger.trace(f"Epoch [{epoch + 1}/{self.epochs}], "
                             f"Step [{step + 1}/{batches}], "
                             f"Loss: {error.item():.4f}, "
                             f"Accuracy: {(correct / total) * 100:.2f}%")

            self.data_loader = load_dataset(self.test_data_dir, self.batch_size)
            correct_test, total_test, error_test = self.test_accuracy(model, loss)
            test_accuracy = (correct_test / total_test) * 100
            performance.append(test_accuracy)

            flag = True
            for i in performance:
                if test_accuracy < i:
                    flag = False

            if flag is True:
                model_filename = f"CNNModel-{epoch + 1}-{test_accuracy:.2f}.pth"
                torch.save({"epoch": epoch + 1,
                            "model_state_dict": model.state_dict(),
                            "optimizer_state_dict": optimizer.state_dict(),
                            "loss": loss},
                           Path(model_dir, model_filename))
                logger.success(f"Saved {epoch + 1} epoch model to {model_dir}")

            logger.info(f"Train Error of the model on the test images: {(error_train / total_train)} %")
            logger.info(f"Train Accuracy of the model on the test images: {(correct_train / total_train) * 100} %")
            logger.info(f"Test Error of the model on the test images: {(error_test / total_test)} %")
            logger.info(f"Test Accuracy of the model on the test images: {test_accuracy} %")

        model_filename = f"CNNModel-final-{test_accuracy:.2f}.pth"
        torch.save(model.state_dict(), Path(model_dir, model_filename))
        logger.success(f"Saved final ({self.epochs} epochs) model to {model_dir}")

    def test_accuracy_from_model(self, path_to_model: str, amount_languages: int) -> None:
        """
        Test the accuracy of the model on the test data
        :param path_to_model: path to the model
        """
        model = CNNModel(amount_languages).to(self.device)
        model.load_state_dict(torch.load(path_to_model))
        loss = nn.CrossEntropyLoss()
        logger.success(f"Model '{os.path.basename(path_to_model)}' is loaded")
        self.check_accuracy(model, loss)

    def test_accuracy_from_checkpoint(self, path_to_model: str, amount_languages: int) -> None:
        """
        Test the accuracy of the model checkpoint on the test data
        :param path_to_model: path to the model
        """
        checkpoint = torch.load(path_to_model)
        model = CNNModel(amount_languages).to(self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        loss = checkpoint['loss']
        logger.success(f"Model '{os.path.basename(path_to_model)}' is loaded")
        self.check_accuracy(model, loss)

    def check_accuracy(self, model: CNNModel, loss: nn.CrossEntropyLoss) -> None:
        """
        Function for the check and print the accuracy of the model on the test data
        :param model: loaded model
        :param loss: loaded loss
        """
        self.data_loader = load_dataset(self.test_data_dir, self.batch_size)
        correct_test, total_test, error_test = self.test_accuracy(model, loss)
        test_accuracy = (correct_test / total_test) * 100

        logger.info(f"Test Error of the model on the test images: {(error_test / total_test)} %")
        logger.info(f"Test Accuracy of the model on the test images: {test_accuracy} %")

    def test_accuracy(self, model: CNNModel, loss: nn.CrossEntropyLoss) -> tuple:
        """
        Function for the get correct_test, total_test, error_test from test data
        :param model: loaded model
        :param loss: loaded loss
        :return: tuple (correct_test, total_test, error_test)
        """
        correct_test, total_test, error_test = 0, 0, 0
        for _, (images, labels) in enumerate(self.data_loader):
            images = images.to(self.device)
            labels = labels.to(self.device)
            outputs_test = model(images)
            error_test = loss(outputs_test, labels)
            _, predicted_test = torch.max(outputs_test.data, 1)
            total_test += labels.size(0)
            correct_test += (predicted_test == labels).sum().item()
            error_test += error_test
        return correct_test, total_test, error_test


class LidModel:
    def __init__(self, device: str = "cpu"):
        self.lid_settings = LanguageIdentificationSettings()
        self.model_file_path = self.lid_settings.model_file_path
        self.languages = self.lid_settings.languages
        self.language_tags = self.lid_settings.language_tags

        self.model = CNNModel(len(self.languages)).to(device)
        self.model.load_state_dict(torch.load(self.model_file_path))
        logger.success(f"Model '{os.path.basename(self.model_file_path)}' is loaded")

    def predict_language(self, path_to_audio: str, folder_name: str) -> tuple:
        """
        Method to detect language from audio file
        :param folder_name: name of the folder where the audio file is located
        :param path_to_audio: path of audio file
        :return: tuple (language_probabilities, language, language_tags)
        """
        import json

        filename = os.path.basename(path_to_audio)
        filename = f"{os.path.splitext(filename)[0]}.png"

        try:
            image_path = generate_spectrogram(filename, path_to_audio, folder_name)
            image_data = image_loader(image_path)
            outputs_from_model = self.model(image_data)

            probabilities = torch.nn.functional.softmax(outputs_from_model, dim=1)[0] * 100
            probabilities = probabilities.detach().numpy().tolist()
            prediction_language_index = outputs_from_model.argmax().item()

            language_probabilities = dict(zip(self.languages, probabilities))
            language = self.languages[prediction_language_index]
            language_tags = self.language_tags[language]

            language_json_path = Path(self.lid_settings.data_store_path,
                                      folder_name,
                                      "language",
                                      f"prediction_{os.path.splitext(filename)[0]}.json")
            with open(language_json_path, "w") as file:
                language_json_data = json.dumps({
                    "language_probabilities": language_probabilities,
                    "language": language,
                    "language_tags": language_tags
                }, indent=2)
                file.write(language_json_data)
                logger.success(f"Prediction saved to {language_json_path}")

            return (language_probabilities, language, language_tags)
        except Exception as err:
            logger.exception(f"{err=}")
