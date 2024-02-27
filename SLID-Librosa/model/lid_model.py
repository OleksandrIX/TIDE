import os
import time
import torch
import torch.nn as nn
import torchvision
import numpy as np
from loguru import logger
from pathlib import Path


class CNNModel(nn.Module):
    def __init__(self):
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
        self.fc2 = nn.Linear(1000, 3)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.reshape(x.size(0), -1)
        x = self.fc1(x)
        x = self.fc2(x)
        return x


def load_dataset(data_path_train, data_path_test):
    dataset_train = torchvision.datasets.ImageFolder(
        root=data_path_train,
        transform=torchvision.transforms.ToTensor()
    )

    dataset_test = torchvision.datasets.ImageFolder(
        root=data_path_test,
        transform=torchvision.transforms.ToTensor()
    )

    test_loader = torch.utils.data.DataLoader(
        dataset_test,
        batch_size=16,
        num_workers=0,
        shuffle=True
    )

    train_loader = torch.utils.data.DataLoader(
        dataset_train,
        batch_size=16,
        num_workers=0,
        shuffle=True
    )

    return train_loader, test_loader, dataset_test


def training_model(data_path_train, data_path_test, epochs, saved_model_path):
    device_training = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNNModel().to(device_training)
    loss = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())

    train_loader, test_loader, dataset = load_dataset(
        data_path_train=data_path_train,
        data_path_test=data_path_test
    )

    loss_history = []
    accuracy_history = []
    batches = len(train_loader)
    performance = [0]

    for epoch in range(0, epochs):
        correct_train, total_train, error_train = 0, 0, 0
        for step, (images, labels) in enumerate(train_loader):
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

            logger.info(f"Epoch [{epoch + 1}/{epochs}], "
                        f"Step [{step + 1}/{batches}], "
                        f"Loss: {error.item():.4f}, "
                        f"Accuracy: {(correct / total) * 100:.2f}%")

        correct_test, total_test, error_test = 0, 0, 0
        for i, (images_test, labels_test) in enumerate(test_loader):
            outputs_test = model(images_test)
            error_test = loss(outputs_test, labels_test)
            _, predicted_test = torch.max(outputs_test.data, 1)
            total_test += labels_test.size(0)
            correct_test += (predicted_test == labels_test).sum().item()
            error_test += error_test

        test_accuracy = (correct_test / total_test) * 100
        named_tuple = time.localtime()
        time_string = time.strftime("%Y-%m-%d_%H-%M-%S", named_tuple)
        performance.append(test_accuracy)

        flag = True
        for i in performance:
            if test_accuracy < i:
                flag = False

        if flag is True:
            torch.save(model.state_dict(), f"{saved_model_path}/CNNModel-{time_string}-{test_accuracy:.2f}.pth")
            logger.info("Saved the updated model")

        logger.info(f"Test Error of the model on the test images: {(error_test / total_test)} %")
        logger.info(f"Test Accuracy of the model on the test images: {test_accuracy} %")
        logger.info(f"Train Error of the model on the test images: {(error_train / total_train)} %")
        logger.info(f"Train Accuracy of the model on the test images: {(correct_train / total_train) * 100} %")


def test_accuracy(data_path_test, path_to_model):
    dataset_test = torchvision.datasets.ImageFolder(
        root=data_path_test,
        transform=torchvision.transforms.ToTensor()
    )

    test_loader = torch.utils.data.DataLoader(
        dataset_test,
        batch_size=16,
        num_workers=0,
        shuffle=True
    )

    loss = nn.CrossEntropyLoss()
    device = torch.device("cpu")
    model = CNNModel().to(device)
    model.load_state_dict(torch.load(path_to_model))

    # checkpoint = torch.load(path_to_model, map_location=device)
    # model.load_state_dict(checkpoint["model_state_dict"])
    # model.to(device)
    # model.eval()

    # model = torch.load(path_to_model, map_location=device)

    correct_test, total_test, error_test = 0, 0, 0
    for i, (images_test, labels_test) in enumerate(test_loader):
        outputs_test = model(images_test)
        error_test = loss(outputs_test, labels_test)
        _, predicted_test = torch.max(outputs_test.data, 1)
        total_test += labels_test.size(0)
        correct_test += (predicted_test == labels_test).sum().item()
        error_test += error_test

    logger.debug(f"{correct_test}; {total_test}; {error_test}")

    test_accuracy = (correct_test / total_test) * 100
    logger.info(test_accuracy)


def predict(path_to_predict, path_to_model):
    from PIL import Image
    device = torch.device("cpu")
    model = CNNModel()
    model.load_state_dict(torch.load(path_to_model))

    languages = ['German', 'English', 'Spanish']
    list_of_images_in_prediction_folder = os.listdir(path_to_predict)

    for image in list_of_images_in_prediction_folder:
        image_path = Path.joinpath(path_to_predict, image)
        image_data = (torchvision.transforms.ToTensor()
                      (Image.open(image_path).convert("RGB")).unsqueeze(0))
        outputs_from_model = model(image_data)
        prediction = outputs_from_model.argmax().item()
        logger.success(f"For {image} detected language: {languages[prediction]}")
