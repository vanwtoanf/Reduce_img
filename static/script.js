let selectedFiles = [];
let isFolder = false;

const fileInput = document.getElementById('fileElem');
const folderInput = document.getElementById('folderElem');
const selectedFileInfo = document.getElementById('selectedFileInfo');
const downloadLinkDiv = document.getElementById('downloadLink');

// Nghe sự kiện chọn file
fileInput.addEventListener('change', (event) => {
    selectedFiles = Array.from(event.target.files);
    isFolder = false;
    document.getElementById('widthInput').value = "";   // Xóa width khi chọn file mới
    document.getElementById('message').innerText = "";
    displaySelectedInfo();
    downloadLinkDiv.innerHTML = "";
});

// Nghe sự kiện chọn thư mục
folderInput.addEventListener('change', (event) => {
    selectedFiles = Array.from(event.target.files);
    isFolder = true;
    document.getElementById('widthInput').value = "";
    document.getElementById('message').innerText = "";
    displaySelectedInfo();
    downloadLinkDiv.innerHTML = "";
});

// Hiển thị thông tin file hoặc thư mục đã chọn
function displaySelectedInfo() {
    if (isFolder && selectedFiles.length > 0) {
        // Hiển thị tên thư mục nếu là thư mục
        const folderPath = selectedFiles[0].webkitRelativePath;
        const folderName = folderPath.split("/")[0];
        selectedFileInfo.innerText = `Folder selected: ${folderName}`;
    } 

    else if (selectedFiles.length === 1) {
        selectedFileInfo.innerText = `File selected: ${selectedFiles[0].name}`;
    }

    else {
        selectedFileInfo.innerText = `Selected ${selectedFiles.length} files.`;
    }
}

// Xử lý sự kiện khi nhấn nút tải lên
document.getElementById('uploadBtn').addEventListener('click', async () => {
if (selectedFiles.length === 0) {
    document.getElementById('message').innerText = "Please select a file or folder.";
    return;
}

const formData = new FormData();
selectedFiles.forEach(file => formData.append('files', file));

const widthInput = document.getElementById('widthInput').value;
    if (widthInput) formData.append('width', widthInput);

// Thêm tên thư mục vào formData nếu đang xử lý thư mục
if (isFolder && selectedFiles.length > 0) {
    const folderPath = selectedFiles[0].webkitRelativePath;
    const folderName = folderPath.split("/")[0];
    formData.append('directory_name', folderName);
}

// Hiển thị trạng thái "Đang xử lý..."
document.getElementById('message').innerText = "Loading...";

const response = await fetch('/reduce/process-images/', {
    method: 'POST',
    body: formData,
});

const result = await response.json();
document.getElementById('message').innerText = result.info;

if (result.download_link) {
    // Hiển thị link tải về khi backend trả về link
    downloadLinkDiv.innerHTML = `<a href="${result.download_link}" target="_blank" rel="noopener noreferrer">Click here to download</a>`;
    downloadLinkDiv.style.display = "block";
    document.getElementById('message').innerText = "Ok!";
  }
});



// Xóa giá trị width khi tải lại trang
window.onload = function() {
    resetForm();
};


