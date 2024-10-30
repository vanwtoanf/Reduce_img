from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from zipfile import ZipFile
from ultis.ultis import process_image

# Router for multiple file (folder) processing
folder_router = APIRouter(
    prefix="/reduce/folder",
    tags=["folder"]
)

# Temporary folder path
TEMP_FOLDER = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)  # Create the folder if it does not exist

# Allowed file extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

@folder_router.post("/process-images/")
async def process_multiple_images(files: list[UploadFile] = File(...), width: int = Form(None)):
    # Clear the TEMP_FOLDER before starting
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER)  # Recreate TEMP_FOLDER

    valid_files = []
    
    # Filter files with valid extensions
    for file in files:
        file_ext = os.path.splitext(file.filename)[-1].lower()
        if file_ext in ALLOWED_EXTENSIONS:
            valid_files.append(file)

    if len(valid_files) == 0:
        return JSONResponse(content={"info": "No valid files to process."}, status_code=400)

    zip_filename = "processed_images.zip"
    zip_path = os.path.join(TEMP_FOLDER, zip_filename)

    # Process each valid file and add to ZIP
    with ZipFile(zip_path, 'w') as zipf:
        for file in valid_files:
            temp_file_path = os.path.join(TEMP_FOLDER, file.filename)

            # Tạo thư mục con nếu cần
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            process_image(temp_file_path, temp_file_path, width)
            zipf.write(temp_file_path, arcname=file.filename)
            os.remove(temp_file_path)  # Remove the file after adding to zip

    # Return the download link for the zip file
    return JSONResponse(content={"download_link": f"/reduce/folder/download/{zip_filename}"})


@folder_router.get("/download/{filename}")
async def download_folder_file(filename: str, background_tasks: BackgroundTasks):
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
