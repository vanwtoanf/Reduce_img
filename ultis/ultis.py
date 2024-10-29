import os
from PIL import Image


# Resize width
def resize_image(input_image_path, new_width=None):
    image = Image.open(input_image_path)

    if new_width == None:
        return image

    # Original size
    original_width, original_height = image.size

    # New height
    aspect_ratio = original_height / original_width
    new_height = int(new_width * aspect_ratio)

    # Resize
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    return resized_image


# Adaptive Color Quantization
def adaptive_color_quantization(image, num_colors=256):
    # Giu lai kenh alpha (neu co)
    image_reduced = image.convert("RGBA")

    # Giam mau anh
    image_reduced = image_reduced.convert("P", palette=Image.ADAPTIVE, colors=num_colors)

    return image_reduced

def process_image(input_image_path, output_image_path, new_width=None, num_colors=256):
    # Resize image
    resized_image = resize_image(input_image_path, new_width)

    # Kiểm tra dung lượng ảnh, nếu dưới 1 MB thì chỉ copy mà không xử lý
    file_size = os.path.getsize(input_image_path)
    if file_size < 1.5 * 1024 * 1024:  # 1 MB = 1,048,576 bytes
        Image.open(input_image_path).save(output_image_path, format="PNG")
        return  # Thoát sớm nếu không cần xử lý

    # Nen anh
    compressed_image = adaptive_color_quantization(resized_image, num_colors)

    # Luu anh dang .png
    compressed_image.save(output_image_path, format="PNG")


# input_image_path = "./test2.png"
# output_image_path = "./test2_new2.png"
# new_width = 1576

# process_image(input_image_path, output_image_path, new_width=new_width)




