from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from zipfile import ZipFile
from ultis.ultis import process_image
from concurrent.futures import ProcessPoolExecutor
import asyncio
import uuid

# Khởi tạo router reduce
router = APIRouter(
    prefix="/reduce",
    tags=["reduce"]
)

# Chỉ chấp nhận các phần mở rộng file này
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# Tạo Executor cho các tiến trình song song
executor = ProcessPoolExecutor()

async def process_and_save_image_async(file_path: str, output_path: str, width: int):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, process_image, file_path, output_path, width)

@router.post("/process-images/")
async def process_images(
    files: list[UploadFile] = File(...), 
    width: int = Form(None),
    directory_name: str = Form(None)
    ):
    # Tạo thư mục tạm riêng cho mỗi yêu cầu
    session_id = str(uuid.uuid4())  # Tạo ID duy nhất cho mỗi phiên
    temp_folder = os.path.join(os.getcwd(), "temp", session_id)
    os.makedirs(temp_folder, exist_ok=True)  # Tạo thư mục tạm riêng

    valid_files = []

    # Lọc các file có định dạng hợp lệ
    for file in files:
        file_ext = os.path.splitext(file.filename)[-1].lower()
        if file_ext in ALLOWED_EXTENSIONS:
            valid_files.append(file)

    if len(valid_files) == 0:
        shutil.rmtree(temp_folder)  # Xóa thư mục tạm khi không có file hợp lệ
        return JSONResponse(content={"info": "No valid file to process."}, status_code=400)

    if len(valid_files) == 1:
        # Xử lý một file ảnh
        file = valid_files[0]
        temp_path = os.path.join(temp_folder, file.filename)
        
        # Lưu ảnh vào đường dẫn tạm
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Thực hiện xử lý ảnh không đồng bộ
        await process_and_save_image_async(temp_path, temp_path, width)

        # Trả về link tải file sau khi xử lý xong
        return JSONResponse(content={"download_link": f"/reduce/download/{session_id}/{file.filename}"})

    else:
        # Xử lý nhiều file, lưu thành file ZIP
        zip_filename = f"{directory_name or session_id}.zip"
        zip_path = os.path.join(temp_folder, zip_filename)
        tasks = []  # Danh sách các tác vụ xử lý ảnh

        # Tạo danh sách các tác vụ xử lý ảnh không đồng bộ
        for file in valid_files:
            temp_file_path = os.path.join(temp_folder, file.filename)

            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

            # Lưu file vào thư mục tạm
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Thêm tác vụ xử lý ảnh không đồng bộ vào danh sách
            tasks.append(process_and_save_image_async(temp_file_path, temp_file_path, width))

        # Chạy tất cả các tác vụ xử lý ảnh đồng thời
        await asyncio.gather(*tasks)

        # Nén tất cả các file đã xử lý xong vào zip
        with ZipFile(zip_path, 'w') as zipf:
            for file in valid_files:
                processed_file_path = os.path.join(temp_folder, file.filename)
                zipf.write(processed_file_path, arcname=os.path.basename(processed_file_path))
                os.remove(processed_file_path)  # Xóa file sau khi đã thêm vào zip

        # Trả về link tải file zip
        return JSONResponse(content={"download_link": f"/reduce/download/{session_id}/{zip_filename}"})

@router.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(os.getcwd(), "temp", session_id, filename)

    if os.path.exists(file_path):
        # Sử dụng BackgroundTasks để xóa thư mục sau khi tải xuống
        background_tasks.add_task(shutil.rmtree, os.path.dirname(file_path))
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        return JSONResponse(content={"error": "File not exists or deleted."}, status_code=404)



