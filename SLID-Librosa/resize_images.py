from PIL import Image


def resize_image(input_path, output_path, new_size=(432, 432)):
    img = Image.open(input_path)
    resized_img = img.resize(new_size)
    resized_img.save(output_path)


if __name__ == "__main__":
    src_img = "dataset/test_img/src.png"
    resize_img = "dataset/test_img/resize.png"

    resize_image(src_img, resize_img, new_size=(432, 432))
