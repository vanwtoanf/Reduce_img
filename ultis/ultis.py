import os
from PIL import Image


# Resize width
def resize_image(input_image_path, new_width=None):
    image = Image.open(input_image_path)

    if new_width == None:
        return image

    # Original size
    original_width, original_height = image.size

    if original_width <= new_width:
        return image

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
    # Lấy phần mở rộng của file đầu vào để xác định định dạng
    _, ext = os.path.splitext(input_image_path)
    output_format = "PNG" if ext.lower() == ".png" else "JPEG"

    # Kiểm tra dung lượng ảnh, nếu dưới 1 MB thì chỉ copy mà không xử lý
    file_size = os.path.getsize(input_image_path)
    if file_size < 1 * 1024 * 1024:  # 1 MB
        with Image.open(input_image_path) as img:
            img.save(output_image_path, format=output_format, quality=75, optimize=True)
            return  # Thoát sớm nếu không cần xử lý
    
    # Resize image
    resized_image = resize_image(input_image_path, new_width)

    # Nen anh
    compressed_image = adaptive_color_quantization(resized_image, num_colors)

    # Lưu ảnh với định dạng ban đầu
    if output_format == "JPEG":
        compressed_image = compressed_image.convert("RGB")  # Chuyển đổi nếu ảnh có alpha
    compressed_image.save(output_image_path, format=output_format, optimize=True, quality=90)



# input_image_path = "./test2.png"
# output_image_path = "./test2_new2.png"
# new_width = 1576

# process_image(input_image_path, output_image_path, new_width=new_width)




