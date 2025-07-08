from flask import Flask, request, jsonify, render_template, send_file
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from ultralytics import YOLO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 配置路径
UPLOAD_FOLDER = 'static/uploads'
RESULTS_FOLDER = 'results'
RESULTS_IMAGES_FOLDER = os.path.join(RESULTS_FOLDER, 'images')
RECORDS_FOLDER = os.path.join(RESULTS_FOLDER, 'records')
MODEL_PATH = '../runs/detect/train4/weights/best.pt'

# 创建必要的目录
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER, RESULTS_IMAGES_FOLDER, RECORDS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}

# 类别映射（根据您的模型）
CLASS_NAMES = {
    0: '聚酯电容',
    1: '热敏电阻', 
    2: '三端稳压管'
}

class YOLODetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        
    def predict(self, image_path, conf_threshold=0.5):
        """执行预测"""
        results = self.model(image_path, conf=conf_threshold)
        return results
    
    def draw_results(self, image_path, results, output_path):
        """绘制检测结果"""
        # 读取原图
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        detections = []
        
        if results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                # 获取坐标和类别信息
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = CLASS_NAMES.get(class_id, f'Class_{class_id}')
                
                # 记录检测结果
                detections.append({
                    'class_name': class_name,
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2]
                })
                
                # 绘制边界框
                color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)][class_id % 3]
                cv2.rectangle(image_rgb, (x1, y1), (x2, y2), color, 2)
                
                # 添加标签
                label = f'{class_name}: {confidence:.2f}'
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(image_rgb, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                cv2.putText(image_rgb, label, (x1, y1 - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # 保存结果图片
        result_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_image)
        
        return detections

# 初始化检测器
detector = YOLODetector(MODEL_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_record(filename, detections, processing_time):
    """保存检测记录"""
    record = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'detections': detections,
        'processing_time': processing_time,
        'detection_count': len(detections)
    }
    
    record_file = os.path.join(RECORDS_FOLDER, f"{record['id']}.json")
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    
    return record

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    confidence = float(request.form.get('confidence', 0.5))
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{file_id}.{file_extension}"
            
            # 保存上传的文件
            upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(upload_path)
            
            # 执行检测
            start_time = datetime.now()
            results = detector.predict(upload_path, conf_threshold=confidence)
            
            # 生成结果图片
            result_filename = f"result_{file_id}.{file_extension}"
            result_path = os.path.join(RESULTS_IMAGES_FOLDER, result_filename)
            detections = detector.draw_results(upload_path, results, result_path)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # 保存检测记录
            record = save_record(filename, detections, processing_time)
            
            # 转换图片为base64以便前端显示
            with open(result_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            return jsonify({
                'success': True,
                'record_id': record['id'],
                'filename': filename,
                'detections': detections,
                'detection_count': len(detections),
                'processing_time': processing_time,
                'result_image': f"data:image/{file_extension};base64,{img_base64}"
            })
            
        except Exception as e:
            return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/history')
def get_history():
    """获取检测历史记录"""
    try:
        records = []
        for filename in os.listdir(RECORDS_FOLDER):
            if filename.endswith('.json'):
                with open(os.path.join(RECORDS_FOLDER, filename), 'r', encoding='utf-8') as f:
                    record = json.load(f)
                    records.append(record)
        
        # 按时间倒序排列
        records.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify({'success': True, 'records': records[:20]})  # 返回最近20条记录
    
    except Exception as e:
        return jsonify({'error': f'获取历史记录失败: {str(e)}'}), 500

@app.route('/result/<record_id>')
def get_result_image(record_id):
    """获取结果图片"""
    try:
        # 查找对应的记录文件
        record_file = os.path.join(RECORDS_FOLDER, f"{record_id}.json")
        if not os.path.exists(record_file):
            return jsonify({'error': '记录不存在'}), 404
        
        # 查找结果图片
        for filename in os.listdir(RESULTS_IMAGES_FOLDER):
            if record_id in filename:
                image_path = os.path.join(RESULTS_IMAGES_FOLDER, filename)
                return send_file(image_path)
        
        return jsonify({'error': '结果图片不存在'}), 404
    
    except Exception as e:
        return jsonify({'error': f'获取图片失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 启动工件检测系统...")
    print(f"📁 上传目录: {UPLOAD_FOLDER}")
    print(f"📁 结果目录: {RESULTS_FOLDER}")
    print(f"🤖 模型路径: {MODEL_PATH}")
    print("🌐 访问地址: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
