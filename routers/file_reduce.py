from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from ultis.ultis import process_image

# Router for single file processing
file_router = APIRouter(
    prefix="/reduce/file",
    tags=["file"]
)

# Temporary folder path
TEMP_FOLDER = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)  # Create the folder if it does not exist

# Allowed file extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

@file_router.post("/process-image/")
async def process_single_image(file: UploadFile = File(...), width: int = Form(None)):
    # Clear the TEMP_FOLDER before starting
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER)  # Recreate TEMP_FOLDER

    file_ext = os.path.splitext(file.filename)[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(content={"info": "Invalid file format."}, status_code=400)

    temp_path = os.path.join(TEMP_FOLDER, file.filename)

    # Save and process the image
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    process_image(temp_path, temp_path, width)

    # Return the download link
    return JSONResponse(content={"download_link": f"/reduce/file/download/{file.filename}"})


@file_router.get("/download/{filename}")
async def download_single_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(TEMP_FOLDER, filename)

    if os.path.exists(file_path):
        # Use BackgroundTasks to remove the file after download
        background_tasks.add_task(os.remove, file_path)
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        return JSONResponse(content={"error": "File does not exist or has been deleted."}, status_code=404)



























# from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
# from fastapi.responses import FileResponse, JSONResponse
# import os
# import shutil
# from zipfile import ZipFile
# from ultis.ultis import process_image

# # Khởi tạo router reduce
# router = APIRouter(
#     prefix="/reduce",
#     tags=["reduce"]
# )

# # Đường dẫn đến thư mục tạm 'temp'
# TEMP_FOLDER = os.path.join(os.getcwd(), "temp")
# os.makedirs(TEMP_FOLDER, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

# # Chỉ chấp nhận các phần mở rộng file này
# ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# @router.post("/process-images/")
# async def process_images(files: list[UploadFile] = File(...), width: int = Form(None)):
#     # Xóa tất cả nội dung trong thư mục temp trước khi bắt đầu
#     if os.path.exists(TEMP_FOLDER):
#         shutil.rmtree(TEMP_FOLDER)
#     os.makedirs(TEMP_FOLDER)  # Tạo lại thư mục tạm

#     valid_files = []

#     # Lọc các file có định dạng hợp lệ
#     for file in files:
#         file_ext = os.path.splitext(file.filename)[-1].lower()
#         if file_ext in ALLOWED_EXTENSIONS:
#             valid_files.append(file)

#     if len(valid_files) == 0:
#         return JSONResponse(content={"info": "Không có file hợp lệ để xử lý."}, status_code=400)

#     if len(valid_files) == 1:
#         # Xử lý một file ảnh
#         file = valid_files[0]
#         temp_path = os.path.join(TEMP_FOLDER, file.filename)
        
#         # Lưu và xử lý ảnh
#         with open(temp_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         process_image(temp_path, temp_path, width)

#         # Trả về link tải file
#         return JSONResponse(content={"download_link": f"/reduce/download/{file.filename}"})

#     else:
#         # Xử lý nhiều file, lưu thành file ZIP
#         zip_filename = "processed_images.zip"
#         zip_path = os.path.join(TEMP_FOLDER, zip_filename)
#         with ZipFile(zip_path, 'w') as zipf:
#             for file in valid_files:
#                 temp_file_path = os.path.join(TEMP_FOLDER, file.filename)

#                 # Tạo thư mục con nếu cần
#                 os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

#                 with open(temp_file_path, "wb") as buffer:
#                     shutil.copyfileobj(file.file, buffer)

#                 process_image(temp_file_path, temp_file_path, width)
#                 zipf.write(temp_file_path, arcname=file.filename)
#                 os.remove(temp_file_path)  # Xóa file sau khi đã thêm vào zip

#         # Trả về link tải file zip
#         return JSONResponse(content={"download_link": f"/reduce/download/{zip_filename}"})

# @router.get("/download/{filename}")
# async def download_file(filename: str, background_tasks: BackgroundTasks):
#     file_path = os.path.join(TEMP_FOLDER, filename)

#     if os.path.exists(file_path):
#         # Sử dụng BackgroundTasks để xóa file sau khi tải xuống
#         background_tasks.add_task(os.remove, file_path)
#         return FileResponse(
#             path=file_path,
#             media_type='application/octet-stream',
#             filename=filename,
#             headers={"Content-Disposition": f"attachment; filename={filename}"}
#         )
#     else:
#         return JSONResponse(content={"error": "File not exists or deleted."}, status_code=404)

