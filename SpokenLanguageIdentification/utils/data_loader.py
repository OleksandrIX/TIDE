import torch
from torchvision import transforms, datasets
from PIL import Image


def load_dataset(path_to_dataset: str,
                 batch_size: int = 32,
                 shuffle: bool = True) -> torch.utils.data.DataLoader:
    """
    Loads dataset from path and returns it as a torch.utils.data.DataLoader
    :param path_to_dataset: path to dataset
    :param batch_size: batch size for dataset
    :param shuffle: shuffle dataset
    :return: returns torch.utils.data.DataLoader
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        transforms.Resize((482, 484))
    ])
    dataset = datasets.ImageFolder(root=path_to_dataset,
                                   transform=transform)
    return torch.utils.data.DataLoader(dataset,
                                       batch_size=batch_size,
                                       num_workers=0,
                                       shuffle=shuffle)


def image_loader(image_path: str) -> torch.Tensor:
    """
    Loads image from path and returns it as a torch.Tensor
    :param image_path: path to image
    :return: Tensor image of size (H, W, C)
    """
    image = Image.open(image_path)
    image = image.convert("RGB")
    image = transforms.ToTensor()(image).float()
    return image.unsqueeze(0)
