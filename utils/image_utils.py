from PIL import Image, ImageDraw


class ImageUtils:
    def __init__(self) -> None:
        pass
        
    def resize_image(self, input_path, output_path, size=1024):
        image = Image.open(input_path)
        resized_image = image.resize((size, size))
        converted_image = resized_image.convert('RGBA')
        converted_image.save(output_path, format='PNG')
        return converted_image
