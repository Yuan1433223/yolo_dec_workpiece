// DOM元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const confidenceSlider = document.getElementById('confidence');
const confidenceValue = document.getElementById('confidenceValue');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const messageContainer = document.getElementById('messageContainer');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadHistory();
});

// 设置事件监听器
function setupEventListeners() {
    // 拖拽上传
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);
    
    // 置信度滑块
    confidenceSlider.addEventListener('input', function() {
        confidenceValue.textContent = this.value;
    });
    
    // 上传区域点击
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
}

// 拖拽事件处理
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// 文件选择处理
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// 处理文件上传
function handleFile(file) {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/gif', 'image/tiff'];
    if (!allowedTypes.includes(file.type)) {
        showMessage('请选择有效的图片文件 (JPG, PNG, BMP)', 'error');
        return;
    }
    
    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showMessage('文件大小不能超过16MB', 'error');
        return;
    }
    
    // 显示原始图片预览
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('originalImage').src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    // 上传文件
    uploadFile(file);
}

// 上传文件到服务器
function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('confidence', confidenceSlider.value);
    
    showLoading(true);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            displayResults(data);
            showMessage('检测完成！', 'success');
            loadHistory(); // 刷新历史记录
        } else {
            showMessage(data.error || '处理失败', 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showMessage('网络错误: ' + error.message, 'error');
    });
}

// 显示检测结果
function displayResults(data) {
    // 显示结果区域
    resultsSection.style.display = 'block';
    
    // 更新统计信息
    document.getElementById('detectionCount').textContent = data.detection_count;
    document.getElementById('processingTime').textContent = data.processing_time.toFixed(2);
    
    // 显示结果图片
    document.getElementById('resultImage').src = data.result_image;
    
    // 显示检测详情
    const detectionList = document.getElementById('detectionList');
    detectionList.innerHTML = '';
    
    if (data.detections.length > 0) {
        data.detections.forEach((detection, index) => {
            const item = document.createElement('div');
            item.className = 'detection-item';
            item.innerHTML = `
                <div>
                    <span class="class-name">${detection.class_name}</span>
                    <span class="confidence">置信度: ${(detection.confidence * 100).toFixed(1)}%</span>
                </div>
                <div style="margin-top: 5px; font-size: 0.9rem; color: #666;">
                    位置: [${detection.bbox.map(x => Math.round(x)).join(', ')}]
                </div>
            `;
            detectionList.appendChild(item);
        });
    } else {
        detectionList.innerHTML = '<div style="text-align: center; color: #666;">未检测到任何目标</div>';
    }
    
    // 滚动到结果区域
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// 加载历史记录
function loadHistory() {
    fetch('/history')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayHistory(data.records);
        } else {
            showMessage(data.error || '加载历史记录失败', 'error');
        }
    })
    .catch(error => {
        showMessage('加载历史记录失败: ' + error.message, 'error');
    });
}

// 显示历史记录
function displayHistory(records) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';
    
    if (records.length === 0) {
        historyList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">暂无检测记录</div>';
        return;
    }
    
    records.forEach(record => {
        const item = document.createElement('div');
        item.className = 'history-item';
        
        const timestamp = new Date(record.timestamp).toLocaleString('zh-CN');
        
        item.innerHTML = `
            <div class="history-header">
                <div class="history-filename">${record.filename}</div>
                <div class="history-time">${timestamp}</div>
            </div>
            <div class="history-stats">
                <div><i class="fas fa-bullseye"></i> ${record.detection_count} 个目标</div>
                <div><i class="fas fa-clock"></i> ${record.processing_time.toFixed(2)}s</div>
            </div>
        `;
        
        // 点击查看详情
        item.addEventListener('click', () => {
            viewHistoryDetail(record);
        });
        
        historyList.appendChild(item);
    });
}

// 查看历史记录详情
function viewHistoryDetail(record) {
    // 这里可以实现查看历史记录详情的功能
    // 比如显示结果图片、检测详情等
    showMessage(`查看记录: ${record.filename}`, 'info');
}

// 显示/隐藏加载动画
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    messageContainer.appendChild(messageDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 3000);
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 工具函数：格式化时间
function formatTime(seconds) {
    if (seconds < 1) {
        return (seconds * 1000).toFixed(0) + 'ms';
    }
    return seconds.toFixed(2) + 's';
}
