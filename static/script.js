document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('file-info');
    const dropZone = document.getElementById('dropZone');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const promptText = dropZone.querySelector('.drop-zone__prompt');
    let currentFile = null;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    // Remove highlight when item is dragged away
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle click on drop zone
    dropZone.addEventListener('click', () => fileInput.click());

    // Handle file selection via input
    fileInput.addEventListener('change', handleFileSelect);


    // Handle upload button click
    uploadBtn.addEventListener('click', () => {
        if (currentFile) {
            uploadForm.submit();
        }
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            fileInput.files = files;
            handleFileSelect({ target: fileInput });
        }
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        
        if (files.length > 0) {
            const file = files[0];
            
            // Check file extension
            if (!file.name.endsWith('.xls')) {
                fileInfo.textContent = 'Будь ласка, виберіть файл з розширенням .xls';
                fileInfo.style.color = '#d32f2f';
                uploadBtn.disabled = true;
                currentFile = null;
                return;
            }
            
            fileInfo.textContent = file.name;
            fileInfo.style.color = '';
            uploadBtn.disabled = false;
            currentFile = file;
        } else {
            fileInfo.textContent = 'Файл не вибрано';
            fileInfo.style.color = '';
            uploadBtn.disabled = true;
            currentFile = null;
        }
    }

    // Initialize file info text on page load
    if (fileInput.files.length > 0) {
        handleFileSelect({ target: fileInput });
    } else {
        fileInfo.textContent = 'Файл не вибрано';
        uploadBtn.disabled = true;
    }
});
