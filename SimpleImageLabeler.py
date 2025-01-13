import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
                           QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog,
                           QLabel, QInputDialog, QMessageBox, QDialog, QLineEdit, QListWidget,
                           QSlider, QGraphicsItem)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt5.QtGui import QImage, QPixmap, QPen, QColor, QFont, QTextOption, QCursor, QTransform
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

class LabelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("输入标签")
        layout = QVBoxLayout()
        
        # 标签提示
        self.label = QLabel("请输入这个区域的标签:")
        layout.addWidget(self.label)
        
        # 输入框
        self.text_edit = QLineEdit()
        self.text_edit.setMinimumWidth(200)
        # 设置从右到左的文本方向
        self.text_edit.setLayoutDirection(Qt.RightToLeft)
        # 设置文本右对齐
        self.text_edit.setAlignment(Qt.AlignRight)
        layout.addWidget(self.text_edit)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 确定按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def getText(self):
        return self.text_edit.text()
    
    def setText(self, text):
        self.text_edit.setText(text)

class ResizableRectItem:
    """可调整大小的矩形项"""
    
    HANDLE_SIZE = 8
    HANDLE_SPACE = HANDLE_SIZE + 1
    MIN_SIZE = 10  # 添加最小尺寸常量
    HANDLE_CURSORS = {
        'topleft': Qt.SizeFDiagCursor,
        'topright': Qt.SizeBDiagCursor,
        'bottomleft': Qt.SizeBDiagCursor,
        'bottomright': Qt.SizeFDiagCursor,
        'top': Qt.SizeVerCursor,
        'bottom': Qt.SizeVerCursor,
        'left': Qt.SizeHorCursor,
        'right': Qt.SizeHorCursor,
    }

    def __init__(self, scene, rect, label, text_item):
        self.scene = scene
        self.rect_item = rect
        self.label = label
        self.text_item = text_item
        # 设置文本项不随视图变换
        self.text_item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.handles = {}
        self.selected = False
        self.current_handle = None
        self.create_handles()
        self.update_handles()
        self.hide_handles()

    def create_handles(self):
        """创建调整大小的手柄"""
        for pos in ['topleft', 'topright', 'bottomleft', 'bottomright',
                   'top', 'bottom', 'left', 'right']:
            handle = self.scene.addRect(0, 0, self.HANDLE_SIZE, self.HANDLE_SIZE,
                                      QPen(Qt.black), QColor(255, 255, 255))
            handle.setZValue(1)  # 确保手柄在矩形上方
            self.handles[pos] = handle

    def update_handles(self):
        """更新手柄位置"""
        rect = self.rect_item.rect()
        handles_pos = {
            'topleft': (rect.left(), rect.top()),
            'topright': (rect.right() - self.HANDLE_SIZE, rect.top()),
            'bottomleft': (rect.left(), rect.bottom() - self.HANDLE_SIZE),
            'bottomright': (rect.right() - self.HANDLE_SIZE, rect.bottom() - self.HANDLE_SIZE),
            'top': (rect.center().x() - self.HANDLE_SIZE/2, rect.top()),
            'bottom': (rect.center().x() - self.HANDLE_SIZE/2, rect.bottom() - self.HANDLE_SIZE),
            'left': (rect.left(), rect.center().y() - self.HANDLE_SIZE/2),
            'right': (rect.right() - self.HANDLE_SIZE, rect.center().y() - self.HANDLE_SIZE/2)
        }
        for pos, handle in self.handles.items():
            x, y = handles_pos[pos]
            handle.setRect(x, y, self.HANDLE_SIZE, self.HANDLE_SIZE)

    def show_handles(self):
        """显示手柄"""
        for handle in self.handles.values():
            handle.show()
        self.selected = True

    def hide_handles(self):
        """隐藏手柄"""
        for handle in self.handles.values():
            handle.hide()
        self.selected = False

    def contains_point(self, point):
        """检查点是否在矩形内"""
        return self.rect_item.contains(point) or self.text_item.contains(point)

    def get_handle_at(self, point):
        """获取点击的手柄"""
        for pos, handle in self.handles.items():
            if handle.isVisible() and handle.contains(point):
                return pos
        return None

    def resize(self, handle_pos, delta):
        """调整矩形大小"""
        rect = self.rect_item.rect()
        new_rect = QRectF(rect)

        if 'top' in handle_pos:
            new_rect.setTop(rect.top() + delta.y())
        if 'bottom' in handle_pos:
            new_rect.setBottom(rect.bottom() + delta.y())
        if 'left' in handle_pos:
            new_rect.setLeft(rect.left() + delta.x())
        if 'right' in handle_pos:
            new_rect.setRight(rect.right() + delta.x())

        # 确保矩形不会太小
        if new_rect.width() < self.MIN_SIZE:
            if 'right' in handle_pos:
                new_rect.setRight(new_rect.left() + self.MIN_SIZE)
            elif 'left' in handle_pos:
                new_rect.setLeft(new_rect.right() - self.MIN_SIZE)
                
        if new_rect.height() < self.MIN_SIZE:
            if 'bottom' in handle_pos:
                new_rect.setBottom(new_rect.top() + self.MIN_SIZE)
            elif 'top' in handle_pos:
                new_rect.setTop(new_rect.bottom() - self.MIN_SIZE)

        self.rect_item.setRect(new_rect)
        # 更新文本位置到矩形框内部
        self.text_item.setPos(new_rect.topLeft() + QPointF(5, 5))
        self.update_handles()

    def delete(self):
        """删除矩形及相关项"""
        for handle in self.handles.values():
            self.scene.removeItem(handle)
        self.scene.removeItem(self.rect_item)
        self.scene.removeItem(self.text_item)
        self.handles.clear()

    def edit_label(self):
        """编辑标签文本"""
        dialog = LabelDialog()
        dialog.setFont(self.scene.label_font)
        dialog.setText(self.label)  # 设置当前标签文本
        
        if dialog.exec_() == QDialog.Accepted:
            new_label = dialog.getText()
            if new_label and new_label != self.label:
                self.label = new_label
                # 更新文本显示
                self.scene.removeItem(self.text_item)
                self.text_item = self.scene.addLabelText(new_label, 
                                                       self.rect_item.rect().topLeft())
                # 更新标签缓存
                self.scene.update_labels()

class LabelingScene(QGraphicsScene):
    # 添加光标定义
    HANDLE_CURSORS = {
        'topleft': Qt.SizeFDiagCursor,
        'topright': Qt.SizeBDiagCursor,
        'bottomleft': Qt.SizeBDiagCursor,
        'bottomright': Qt.SizeFDiagCursor,
        'top': Qt.SizeVerCursor,
        'bottom': Qt.SizeVerCursor,
        'left': Qt.SizeHorCursor,
        'right': Qt.SizeHorCursor,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.start_point = None
        self.current_rect = None
        self.rectangles = []  # 存储 ResizableRectItem 对象
        self.selected_item = None
        self.resizing = False
        self.current_handle = None
        
        # 添加双击检测相关的属性
        self.last_click_time = None
        self.last_click_pos = None
        self.double_click_interval = 300  # 毫秒
        
        # 设置字体
        self.label_font = QFont()
        # 尝试使用叙利亚文字体
        font_families = [
            "Estrangelo Edessa",     # 叙利亚文 Estrangelo 字体
            "Noto Sans Syriac",      # Google Noto 叙利亚文字体
            "East Syriac Adiabene",  # 东叙利亚文字体
            "Serto Jerusalem",       # Serto 风格叙利亚文字体
            "Microsoft Sans Serif",   # 后备字体
            "Arial Unicode MS",      # 后备 Unicode 字体
            "Arial"                  # 最终后备字体
        ]
        
        for family in font_families:
            self.label_font.setFamily(family)
            if QFont(family).exactMatch():
                break
                
        self.label_font.setPointSize(18)
        self.label_font.setStyleStrategy(QFont.PreferAntialias)
        
        self.current_image_path = None
        self.labels = set()  # 保存当前图片的标签集合

    def set_image_path(self, path):
        """设置当前图片路径"""
        self.current_image_path = path
        if path:
            # 加载对应的JSON文件中的标签
            json_path = os.path.splitext(path)[0] + '.json'
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.labels = set(item['label'] for item in data if 'label' in item)
                except Exception as e:
                    print(f"加载JSON文件时出错: {str(e)}")

    def save_annotations(self):
        """保存标注到JSON文件"""
        if not self.current_image_path:
            return
            
        try:
            annotations = []
            for item in self.rectangles:
                rect = item.rect_item.rect()
                annotations.append({
                    'label': item.label,
                    'x': rect.x(),
                    'y': rect.y(),
                    'width': rect.width(),
                    'height': rect.height()
                })
            
            json_path = os.path.splitext(self.current_image_path)[0] + '.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, ensure_ascii=False, indent=2)
            print(f"标注已保存到: {json_path}")
        except Exception as e:
            print(f"保存标注时出错: {str(e)}")

    def update_labels(self):
        """更新标签集合并保存"""
        # 收集当前所有标签
        current_labels = set()
        for item in self.rectangles:
            if hasattr(item, 'label'):
                current_labels.add(item.label)
        
        # 更新标签集合
        self.labels = current_labels
        # 保存标注
        self.save_annotations()
        print(f"标签已更新: {sorted(self.labels)}")

    def add_label(self, label):
        """添加新标签并保存"""
        if label:
            self.labels.add(label)
            self.save_annotations()
            print(f"新标签已添加: {label}")

    def remove_label(self, label):
        """删除标签并保存"""
        if label in self.labels:
            if not any(item.label == label for item in self.rectangles):
                self.labels.remove(label)
                self.save_annotations()
                print(f"标签已删除: {label}")

    def addLabelText(self, text, pos):
        # 创建文本项
        text_item = self.addText(text, self.label_font)
        text_item.setDefaultTextColor(QColor(255, 0, 0))
        
        # 设置文本不随视图变换
        text_item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        
        # 设置文本方向和对齐方式
        document = text_item.document()
        option = QTextOption()
        option.setAlignment(Qt.AlignRight)
        option.setTextDirection(Qt.RightToLeft)
        document.setDefaultTextOption(option)
        
        # 将文本放在矩形框内部的顶部
        text_height = text_item.boundingRect().height()
        text_item.setPos(pos.x() + 5, pos.y() + 5)  # 添加 5 像素的内边距
        return text_item
            
    def mousePressEvent(self, event):
        pos = event.scenePos()
        current_time = QApplication.instance().startTimer(0)  # 获取当前时间戳
        
        # 检查是否是双击
        if (self.last_click_time is not None and 
            self.last_click_pos is not None and
            (current_time - self.last_click_time) <= self.double_click_interval and
            (pos - self.last_click_pos).manhattanLength() < 5):
            
            # 检查是否点击了已有矩形
            clicked_item = None
            for item in self.rectangles:
                if item.contains_point(pos):
                    clicked_item = item
                    break
            
            if clicked_item:
                clicked_item.edit_label()
                event.accept()
                self.last_click_time = None
                self.last_click_pos = None
                return
        
        # 更新最后点击时间和位置
        self.last_click_time = current_time
        self.last_click_pos = pos
        
        # 检查是否点击了已有矩形的手柄
        if self.selected_item:
            handle = self.selected_item.get_handle_at(pos)
            if handle:
                self.resizing = True
                self.current_handle = handle
                event.accept()
                return

        # 检查是否点击了已有矩形
        clicked_item = None
        for item in self.rectangles:
            if item.contains_point(pos):
                clicked_item = item
                break

        # 右键点击删除矩形
        if event.button() == Qt.RightButton and clicked_item:
            label = clicked_item.label
            clicked_item.delete()
            self.rectangles.remove(clicked_item)
            # 检查并更新标签
            self.remove_label(label)
            event.accept()
            return

        # 左键点击选择或开始绘制新矩形
        if event.button() == Qt.LeftButton:
            if clicked_item:
                if self.selected_item and self.selected_item != clicked_item:
                    self.selected_item.hide_handles()
                self.selected_item = clicked_item
                clicked_item.show_handles()
            else:
                if self.selected_item:
                    self.selected_item.hide_handles()
                    self.selected_item = None
                self.drawing = True
                self.start_point = pos
                self.current_rect = self.addRect(QRectF(pos, pos),
                                               QPen(QColor(255, 0, 0), 2))

    def mouseMoveEvent(self, event):
        if self.resizing and self.selected_item and self.current_handle:
            cursor = self.HANDLE_CURSORS.get(self.current_handle, Qt.ArrowCursor)
            QApplication.setOverrideCursor(cursor)
            delta = event.scenePos() - event.lastScenePos()
            self.selected_item.resize(self.current_handle, delta)
        elif self.drawing and self.current_rect:
            current_pos = event.scenePos()
            rect = QRectF(self.start_point, current_pos).normalized()
            self.current_rect.setRect(rect)

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        if self.resizing:
            self.resizing = False
            self.current_handle = None
        elif event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_rect:
                # 获取当前矩形的尺寸
                rect = self.current_rect.rect()
                # 如果宽度或高度小于最小值，调整大小
                if rect.width() < ResizableRectItem.MIN_SIZE or rect.height() < ResizableRectItem.MIN_SIZE:
                    new_rect = QRectF(rect)
                    if rect.width() < ResizableRectItem.MIN_SIZE:
                        new_rect.setWidth(ResizableRectItem.MIN_SIZE)
                    if rect.height() < ResizableRectItem.MIN_SIZE:
                        new_rect.setHeight(ResizableRectItem.MIN_SIZE)
                    self.current_rect.setRect(new_rect)

                dialog = LabelDialog()
                dialog.setFont(self.label_font)
                
                if dialog.exec_() == QDialog.Accepted:
                    label = dialog.getText()
                    if label:
                        text_item = self.addLabelText(label, self.current_rect.rect().topLeft())
                        resizable_rect = ResizableRectItem(self, self.current_rect, label, text_item)
                        self.rectangles.append(resizable_rect)
                        # 立即添加新标签
                        self.add_label(label)
                    else:
                        self.removeItem(self.current_rect)
                else:
                    self.removeItem(self.current_rect)
            self.current_rect = None

    def saveAnnotations(self):
        """保存当前标注"""
        self.save_annotations()

    def loadAnnotations(self, file_path=None):
        """加载标注文件
        Args:
            file_path: 可选的标注文件路径。如果未提供，则弹出文件选择对话框
        """
        if not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先打开一张图片！")
            return
            
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(self, "加载标注",
                                                     "", "JSON文件 (*.json)")
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 清除当前场景中的标注
                self.clear()
                self.rectangles.clear()
                # 重新添加图片
                if self.current_image_path:
                    image = QImage(self.current_image_path)
                    if not image.isNull():
                        pixmap = QPixmap.fromImage(image)
                        self.addPixmap(pixmap)
                        self.setSceneRect(QRectF(pixmap.rect()))
                
                # 简化数据格式处理
                annotations = []
                if isinstance(data, list):
                    annotations = data
                elif isinstance(data, dict) and "shapes" in data:
                    for shape in data["shapes"]:
                        if shape.get("shape_type") == "rectangle":
                            points = shape["points"]
                            x1, y1 = points[0]
                            x2, y2 = points[1]
                            annotations.append({
                                "label": shape["label"],
                                "x": min(x1, x2),
                                "y": min(y1, y2),
                                "width": abs(x2 - x1),
                                "height": abs(y2 - y1)
                            })
                
                # 添加标注到场景
                for ann in annotations:
                    if not all(key in ann for key in ['label', 'x', 'y', 'width', 'height']):
                        continue
                    
                    try:
                        rect = self.addRect(
                            QRectF(ann['x'], ann['y'], ann['width'], ann['height']),
                            QPen(QColor(255, 0, 0), 2))
                        text_item = self.addLabelText(
                            ann['label'], 
                            QPointF(ann['x'], ann['y'])
                        )
                        resizable_rect = ResizableRectItem(
                            self.scene, 
                            rect, 
                            ann['label'], 
                            text_item
                        )
                        self.rectangles.append(resizable_rect)
                        # 立即添加新标签
                        self.add_label(ann['label'])
                    except (ValueError, TypeError) as e:
                        print(f"跳过无效的标注数据: {e}")
                        continue
                
                self.view.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
                
                # 保存更新后的标签
                self.save_annotations()
                
            except Exception as e:
                error_msg = f"加载标注文件时出错: {str(e)}"
                print(error_msg)
                QMessageBox.warning(self, "错误", error_msg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.sceneRect().width() > 0:
            self.view.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def mouseDoubleClickEvent(self, event):
        """处理双击事件"""
        pos = event.scenePos()
        
        # 检查是否双击了已有矩形
        clicked_item = None
        for item in self.rectangles:
            if item.contains_point(pos):
                clicked_item = item
                break
        
        if clicked_item:
            clicked_item.edit_label()
            event.accept()
            return
        
        super().mouseDoubleClickEvent(event)

class ImageLabeler(QMainWindow):
    def __init__(self):
        super().__init__()
        # 修改应用程序字体设置
        app_font = QFont()
        app_font.setPointSize(12)
        QApplication.setFont(app_font)
        
        self.current_dir = self.load_last_directory()  # 加载上次的目录
        self.current_image_path = None
        self.zoom_factor = 1.0
        self.initUI()
        
        # 如果有上次的目录，自动加载
        if self.current_dir:
            self.load_directory(self.current_dir)
    
    def load_last_directory(self):
        """加载上次打开的目录"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_dir = config.get('last_directory')
                    if last_dir and os.path.exists(last_dir):
                        return last_dir
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
        return None
    
    def save_last_directory(self, directory):
        """保存当前目录到配置文件"""
        try:
            config = {'last_directory': directory}
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
    
    def load_directory(self, dir_path):
        """加载指定目录的图片和标注"""
        self.file_list.clear()
        
        # 获取所有支持的图片文件
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            image_files.extend([f for f in os.listdir(dir_path) if f.lower().endswith(ext)])
        
        # 排序并添加到列表
        image_files.sort()
        for file in image_files:
            self.file_list.addItem(file)
        
        # 加载标注文件
        label_file = os.path.join(dir_path, 'Label.txt')
        if os.path.exists(label_file):
            self.scene.label_file = label_file
            self.scene.load_labels()
            
            # 如果列表中有文件，自动加载第一个文件的标注
            if self.file_list.count() > 0:
                first_file = os.path.join(dir_path, self.file_list.item(0).text())
                self.loadImage(first_file)
                
                # 检查并加载对应的JSON标注文件
                json_path = os.path.splitext(first_file)[0] + '.json'
                if os.path.exists(json_path):
                    self.loadAnnotations(json_path)
    
    def initUI(self):
        self.setWindowTitle('简单图片标注工具')
        self.setGeometry(100, 100, 1200, 800)  # 增加窗口大小
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)  # 改用水平布局
        
        # 创建左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(200)  # 设置固定宽度
        
        # 添加目录浏览按钮
        self.open_dir_btn = QPushButton('打开目录', self)
        self.open_dir_btn.clicked.connect(self.openDirectory)
        left_layout.addWidget(self.open_dir_btn)
        
        # 添加文件列表
        self.file_list = QListWidget()
        self.file_list.currentRowChanged.connect(self.loadImageFromList)
        left_layout.addWidget(self.file_list)
        
        main_layout.addWidget(left_panel)
        
        # 创建右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 创建工具栏
        toolbar = QHBoxLayout()
        
        # 添加保存按钮
        self.save_btn = QPushButton('保存Json', self)
        self.save_btn.clicked.connect(self.saveAnnotations)
        
        # 添加缩放滑动条
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10% 缩放
        self.zoom_slider.setMaximum(200)  # 200% 缩放
        self.zoom_slider.setValue(100)  # 默认 100%
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        
        # 添加缩放标签
        self.zoom_label = QLabel('100%')
        self.zoom_label.setMinimumWidth(50)
        
        toolbar.addWidget(self.save_btn)
        toolbar.addWidget(QLabel('缩放:'))  # 添加标签
        toolbar.addWidget(self.zoom_slider)
        toolbar.addWidget(self.zoom_label)
        
        # 创建场景和视图
        self.scene = LabelingScene()
        self.view = QGraphicsView(self.scene)
        
        right_layout.addLayout(toolbar)
        right_layout.addWidget(self.view)
        
        main_layout.addWidget(right_panel)
        
    def openDirectory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片目录", 
                                                  self.current_dir or "")  # 使用当前目录作为起始目录
        if dir_path:
            self.current_dir = dir_path
            self.save_last_directory(dir_path)  # 保存新的目录
            self.load_directory(dir_path)
    
    def loadImageFromList(self, row):
        if row >= 0 and self.current_dir:
            file_name = self.file_list.item(row).text()
            file_path = os.path.join(self.current_dir, file_name)
            self.loadImage(file_path)
            
            # 自动加载对应的标注文件（如果存在）
            json_path = os.path.splitext(file_path)[0] + '.json'
            if os.path.exists(json_path):
                self.loadAnnotations(json_path)
    
    def loadImage(self, file_path):
        self.current_image_path = file_path
        self.scene.set_image_path(file_path)
        image = QImage(file_path)
        if not image.isNull():
            self.scene.clear()
            self.scene.rectangles.clear()
            pixmap = QPixmap.fromImage(image)
            self.scene.addPixmap(pixmap)
            rect = pixmap.rect()
            self.scene.setSceneRect(QRectF(rect))
            
            # 重置缩放
            self.zoom_slider.setValue(100)
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            
            # 加载对应的JSON标注文件
            json_path = os.path.splitext(file_path)[0] + '.json'
            if os.path.exists(json_path):
                self.loadAnnotations(json_path)
            else:
                # 如果JSON文件不存在，创建空的标注文件
                self.scene.save_annotations()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene.sceneRect().width() > 0:
            # 保持当前缩放比例
            self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))
            self.view.centerOn(self.scene.sceneRect().center())

    def saveAnnotations(self):
        """保存当前标注"""
        self.scene.save_annotations()

    def loadAnnotations(self, file_path=None):
        """加载标注文件
        Args:
            file_path: 可选的标注文件路径。如果未提供，则弹出文件选择对话框
        """
        if not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先打开一张图片！")
            return
            
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(self, "加载标注",
                                                     "", "JSON文件 (*.json)")
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 清除当前场景中的标注
                self.scene.clear()
                self.scene.rectangles.clear()
                # 重新添加图片
                if self.current_image_path:
                    image = QImage(self.current_image_path)
                    if not image.isNull():
                        pixmap = QPixmap.fromImage(image)
                        self.scene.addPixmap(pixmap)
                        self.scene.setSceneRect(QRectF(pixmap.rect()))
                
                # 简化数据格式处理
                annotations = []
                if isinstance(data, list):
                    annotations = data
                elif isinstance(data, dict) and "shapes" in data:
                    for shape in data["shapes"]:
                        if shape.get("shape_type") == "rectangle":
                            points = shape["points"]
                            x1, y1 = points[0]
                            x2, y2 = points[1]
                            annotations.append({
                                "label": shape["label"],
                                "x": min(x1, x2),
                                "y": min(y1, y2),
                                "width": abs(x2 - x1),
                                "height": abs(y2 - y1)
                            })
                
                # 添加标注到场景
                for ann in annotations:
                    if not all(key in ann for key in ['label', 'x', 'y', 'width', 'height']):
                        continue
                    
                    try:
                        rect = self.scene.addRect(
                            QRectF(ann['x'], ann['y'], ann['width'], ann['height']),
                            QPen(QColor(255, 0, 0), 2))
                        text_item = self.scene.addLabelText(
                            ann['label'], 
                            QPointF(ann['x'], ann['y'])
                        )
                        resizable_rect = ResizableRectItem(
                            self.scene, 
                            rect, 
                            ann['label'], 
                            text_item
                        )
                        self.scene.rectangles.append(resizable_rect)
                        # 立即添加新标签
                        self.scene.add_label(ann['label'])
                    except (ValueError, TypeError) as e:
                        print(f"跳过无效的标注数据: {e}")
                        continue
                
                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                
                # 保存更新后的标签
                self.scene.save_annotations()
                
            except Exception as e:
                error_msg = f"加载标注文件时出错: {str(e)}"
                print(error_msg)
                QMessageBox.warning(self, "错误", error_msg)

    def zoom_changed(self, value):
        """处理缩放滑动条值变化"""
        self.zoom_factor = value / 100.0
        self.zoom_label.setText(f'{value}%')
        
        # 更新视图
        if self.scene.sceneRect().width() > 0:
            self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))
            # 确保视图居中
            self.view.centerOn(self.scene.sceneRect().center())

    def loadAnnotationsFromLines(self, annotation_lines):
        """从标注行加载标注"""
        for line in annotation_lines:
            try:
                parts = line.split(',')
                if len(parts) >= 5:
                    x, y, right, bottom = map(float, parts[:4])
                    label = parts[4]
                    
                    rect = self.scene.addRect(
                        QRectF(x, y, right - x, bottom - y),
                        QPen(QColor(255, 0, 0), 2))
                    text_item = self.scene.addLabelText(
                        label,
                        QPointF(x, y)
                    )
                    resizable_rect = ResizableRectItem(
                        self.scene,
                        rect,
                        label,
                        text_item
                    )
                    self.scene.rectangles.append(resizable_rect)
                    self.scene.add_label(label)
            except Exception as e:
                print(f"加载标注行时出错: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 