
# Simple Image Labeler

## 📖 项目简介  
**Simple Image Labeler** 是一个用于图像标注的简易工具。它可以帮助用户方便地对图像进行分类和标注，为后续的机器学习或深度学习任务提供训练数据。

## 📂 项目结构

```
SimpleImageLabeler/
├── __init__.py               # 初始化文件
├── SimpleImageLabeler.py     # 主程序文件
├── config.json               # 配置文件（存储上次打开的目录）
└── README.md                 # 项目说明文档
```

## ⚙️ 功能介绍
- **图像浏览**：加载本地图像文件夹并逐张查看图像。  
- **图像标注**：为图像添加标签，便于分类和数据集构建。  
- **自动保存**：自动记录上次打开的图像文件夹路径（保存在 `config.json` 中）。  

## 📦 安装与运行

### **1️⃣ 克隆项目**

```bash
git clone https://github.com/chenzhan4321/simplelabel.git
cd simplelabel
```

### **2️⃣ 安装依赖**

```bash
pip install -r requirements.txt
```

### **3️⃣ 运行程序**

```bash
python SimpleImageLabeler.py
```

## ⚙️ 配置说明

`config.json` 用于保存用户的偏好设置：

```json
{
  "last_directory": "/Users/zhanchen/Library/CloudStorage/Dropbox/Downloads/test"
}
```

- **last_directory**：记录上次打开的文件夹路径。  
- 可手动修改路径以设置默认打开的文件夹。

## 📝 TODO  
- [ ] 支持更多标注格式（如 XML、COCO）  
- [ ] 增加多标签分类功能  
- [ ] 支持图像缩放与旋转功能  

## 🤝 贡献指南

欢迎提出建议或提交 PR 改进项目：

1. Fork 本项目  
2. 创建新分支：`git checkout -b feature-xxx`  
3. 提交更改：`git commit -m "添加了 xxx 功能"`  
4. 推送分支：`git push origin feature-xxx`  
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT License。详情请查看 [LICENSE](LICENSE)。

## 📬 联系方式

- 作者：Zhan Chen  
- 邮箱：你的邮箱（可填写）  
