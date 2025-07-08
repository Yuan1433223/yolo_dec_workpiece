# 🔧 智能工件检测系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-green.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-2.3+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于深度学习YOLOv11算法的智能工件检测系统，专注于电子元件的自动化识别与分类。

## ✨ 项目特色

- 🎯 **高精度检测**: 基于YOLOv11模型，支持三种电子元件识别
- 🚀 **实时处理**: 毫秒级检测响应，支持批量处理
- 🎨 **美观界面**: 现代化Web界面，支持拖拽上传
- 📊 **可视化结果**: 直观的检测结果展示和统计分析
- 💾 **历史记录**: 完整的检测历史和数据管理
- 📱 **响应式设计**: 完美适配PC和移动端

## 🔍 支持检测的工件类型

| 类型 | 描述 | 应用场景 |
|------|------|----------|
| 🔋 聚酯电容 | 常用的电容器元件 | 电路板质检、库存管理 |
| 🌡️ 热敏电阻 | 温度敏感电阻器 | 传感器识别、分拣 |
| ⚡ 三端稳压管 | 电压调节器件 | 功率电路检测 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- CUDA支持的GPU (可选，CPU也可运行)
- 至少4GB内存

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/Yuan1433223/yolo_dec_workpiece.git
cd yolo_dec_workpiece

2. **安装依赖**
```bash
pip install -r requirements.txt```

3. **启动系统**
```bash
python app.py```

4. **访问系统**
```arduino
本地访问: http://localhost:5000
公网访问: http://your-ip:port```

## 📁 项目结构
```bash
yolo_detection_system/
├── 📄 app.py                 # Flask后端主程序
├── 📄 requirements.txt       # Python依赖列表
├── 🗂️ runs/detect/train4/weights/best.pt  # 训练好的模型
├── 🗂️ static/               # 前端静态资源
│   ├── 🎨 css/style.css      # 样式文件
│   ├── ⚡ js/main.js         # JavaScript逻辑
│   └── 📷 uploads/           # 上传图片存储
├── 🗂️ templates/            # HTML模板
│   └── 📄 index.html         # 主页面
├── 🗂️ results/              # 检测结果存储
│   ├── 🖼️ images/           # 结果图片
│   └── 📊 records/          # 检测记录JSON
└── 🗂️ utils/
    └── 📄 detector.py        # 检测器工具类
```

## 🎯 使用指南
基本操作
上传图片: 支持拖拽或点击上传，格式包括 JPG、PNG、BMP
调整置信度: 使用滑块调节检测敏感度 (0.1-1.0)
查看结果: 实时显示检测结果和统计信息
历史记录: 查看之前的检测记录

## API接口
```python
# 上传检测
POST /upload
Content-Type: multipart/form-data
参数: file (图片文件), confidence (置信度)

# 获取历史
GET /history
返回: JSON格式的检测历史记录

# 获取结果图片
GET /result/<record_id>
返回: 检测结果图片```

## 📊 性能指标
指标	数值
检测精度	95.2% mAP@0.5
处理速度	~200ms/张 (GPU)
支持分辨率	640×640 (可调整)
最大文件大小	16MB

## 🛠️ 自定义配置
修改检测类别
编辑 app.py 中的类别映射：

```python
CLASS_NAMES = {
    0: '你的类别1',
    1: '你的类别2', 
    2: '你的类别3'
}```

调整模型参数
```python
# 修改置信度阈值
conf_threshold = 0.5

# 修改图片尺寸
img_size = 640

# 修改设备
device = 'cuda:0'  # 或 'cpu'```

## 🤝 贡献指南
欢迎提交Pull Request！请确保：
代码符合PEP8规范
添加适当的注释和文档
通过所有测试用例
更新相关文档

## 📄 许可证
本项目采用MIT许可证 - 详见 LICENSE 文件

## 🙏 致谢
Ultralytics YOLOv11 - 优秀的目标检测框架
Flask - 轻量级Web框架
OpenCV - 计算机视觉库

## 📞 联系方式
📧 Email: 1249484533@qq.com
🐛 Issues: GitHub Issues
📖 Wiki: 项目文档

## ⭐ 如果这个项目对您有帮助，请给我们一个星标！
