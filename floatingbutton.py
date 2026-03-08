# floatingbutton.py
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, pyqtProperty, QSize, QTimer
from PyQt5.QtGui import QMouseEvent
import win32gui,win32con,win32pipe,win32file,threading


class FloatingButton(QPushButton):
    def __init__(self, text, title, click_function, 
                 opacity=0.7, hover_opacity=0.9, 
                 button_color=(100, 100, 100), 
                 text_color=(255, 255, 255),
                 parent=None):
        

        super().__init__(text, parent)
        
        # 设置窗口标题
        self.setWindowTitle(title)
        
        self.setMouseTracking(True)
        self.click_function = click_function
        self.normal_opacity = opacity
        self.hover_opacity = hover_opacity
        self.button_color = button_color
        self.text_color = text_color
        self.main_window_title = title
        
        # 消息监听相关
        self.message_listening = True
        self.custom_message_id = win32con.WM_USER + 1000
        self.message_hwnd = None
        
        # 管道相关 - 使用统一的管道名称
        self.pipe_name = r'\\.\pipe\FloatingButtonPipe'
        self.pipe_listening = True
        
        # 设置初始大小
        self.setMinimumSize(100, 40)
        self.adjustSize()
        
        # 设置按钮样式
        self.update_style()
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # 设置初始位置
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(64, screen_geo.height() - self.height() - 64)
        
        # 动画设置
        self.press_animation = QPropertyAnimation(self, b"size")
        self.press_animation.setDuration(100)
        self.press_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self.hover_animation = QPropertyAnimation(self, b"opacity")
        self.hover_animation.setDuration(200)
        
        # 初始化拖动位置和状态
        self.drag_start_position = QPoint(0, 0)
        self.drag_button_position = QPoint(0, 0)
        self.is_dragging = False
        self.drag_threshold = 5  # 拖动阈值（像素）
        
        # 启动消息监听线程（包含管道）
        self.start_message_listener()
        
        # 定期检查主程序状态的定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_main_program_status)
        self.status_timer.start(3000)  # 3秒检查一次
        
        self.show()
        print("悬浮按钮已显示，等待触发...")
    
    def start_message_listener(self):
        """启动消息监听线程（包含窗口消息和管道消息）"""
        def message_loop():
            # 启动管道服务器
            pipe_thread = threading.Thread(target=self.start_pipe_server, daemon=True)
            pipe_thread.start()
            print("✓ 管道服务器线程已启动")
            
            # 原有的窗口消息循环
            try:
                # 使用唯一的窗口类名
                class_name = f"FloatingButtonMessageWindow_{int(time.time()*1000)}"
                
                # 注册窗口类
                wc = win32gui.WNDCLASS()
                wc.lpfnWndProc = self.message_handler
                wc.lpszClassName = class_name
                wc.hInstance = win32gui.GetModuleHandle(None)
                class_atom = win32gui.RegisterClass(wc)
                
                # 创建消息窗口
                self.message_hwnd = win32gui.CreateWindow(
                    class_atom,
                    "FloatingButtonMsg",
                    0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
                )
                
                print(f"✓ 消息窗口已创建: {self.message_hwnd}")
                
                # 简化的消息循环
                while self.message_listening:
                    try:
                        # 处理窗口消息
                        result, msg = win32gui.PeekMessage(self.message_hwnd, 0, 0, win32con.PM_REMOVE)
                        if result:
                            if msg[1] == win32con.WM_QUIT:
                                break
                            win32gui.TranslateMessage(msg)
                            win32gui.DispatchMessage(msg)
                        else:
                            time.sleep(0.01)  # 短暂休眠避免CPU占用过高
                    except Exception as e:
                        print(f"消息处理错误: {e}")
                        time.sleep(0.1)
                        
            except Exception as e:
                print(f"✗ 消息循环初始化错误: {e}")
        
        self.message_thread = threading.Thread(target=message_loop, daemon=True)
        self.message_thread.start()
        print("✓ 消息监听线程已启动")
    
    def start_pipe_server(self):
        """启动命名管道服务器"""
        print(f"🚀 启动管道服务器: {self.pipe_name}")
        
        while self.pipe_listening:
            try:
                # 创建命名管道
                pipe_handle = win32pipe.CreateNamedPipe(
                    self.pipe_name,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,  # 最多1个实例
                    65536, 65536,  # 输入输出缓冲区
                    0,  # 默认超时
                    None  # 默认安全属性
                )
                
                print(f"✅ 管道创建成功，等待客户端连接...")
                # 等待客户端连接
                win32pipe.ConnectNamedPipe(pipe_handle, None)
                print("✅ 管道客户端已连接")
                
                try:
                    # 读取消息
                    result, data = win32file.ReadFile(pipe_handle, 4096)
                    message = data.decode('utf-8').strip()
                    print(f"📨 收到管道消息: {message}")
                    
                    # 处理管道消息
                    response = self.handle_pipe_message(message)
                    
                    # 发送响应
                    response_bytes = response.encode('utf-8')
                    win32file.WriteFile(pipe_handle, response_bytes)
                    print(f"📤 发送管道响应: {response}")
                    
                    # 等待一下确保响应发送完成
                    time.sleep(0.05)
                    
                except Exception as e:
                    print(f"❌ 处理管道消息时出错: {e}")
                    # 发送错误响应
                    try:
                        error_response = f"ERROR: {str(e)}"
                        win32file.WriteFile(pipe_handle, error_response.encode('utf-8'))
                    except:
                        pass
                finally:
                    # 断开连接
                    win32pipe.DisconnectNamedPipe(pipe_handle)
                    win32file.CloseHandle(pipe_handle)
                    print("🔌 管道连接已关闭")
                    
            except Exception as e:
                print(f"❌ 管道服务器错误: {e}")
                time.sleep(1)  # 出错时等待1秒再重试
    
    def handle_pipe_message(self, message):
        """处理管道消息"""
        print(f"🔄 处理管道消息: {message}")
        
        if message == "SHOW_WINDOW":
            # 收到显示窗口命令，先发送响应，再立即执行退出
            print("🎯 收到SHOW_WINDOW命令，准备恢复窗口")
            
            # 立即执行退出，不要延迟
            self.click_function()
            
            return "WINDOW_SHOW_COMMAND_RECEIVED"
        elif message == "PING":
            return "PONG_FROM_FLOATING_BUTTON"
        elif message == "QUIT":
            # 收到退出命令，立即执行
            self.quit_floating_state()
            return "QUIT_COMMAND_RECEIVED"
        elif message == "GET_STATUS":
            return "FLOATING_BUTTON_RUNNING"
        elif message.startswith("MOVE_TO:"):
            # 移动按钮位置，格式: MOVE_TO:x,y
            try:
                coords = message[8:].split(',')
                x, y = int(coords[0]), int(coords[1])
                QTimer.singleShot(0, lambda: self.move(x, y))
                return f"MOVED_TO_{x}_{y}"
            except:
                return "MOVE_COMMAND_ERROR"
        else:
            return f"UNKNOWN_COMMAND: {message}"
    
    def message_handler(self, hwnd, msg, wparam, lparam):
        """处理接收到的Windows消息"""
        try:
            if msg == self.custom_message_id:
                # 收到主程序的恢复消息
                print("📩 收到主程序恢复消息，退出折叠状态")
                # 使用QTimer在主线程中执行退出操作
                QTimer.singleShot(200, self.quit_floating_state)  # 延迟执行
                return 0
                
            elif msg == win32con.WM_CLOSE:
                # 收到关闭消息
                self.message_listening = False
                self.pipe_listening = False
                return 0
                
        except Exception as e:
            print(f"❌ 消息处理错误: {e}")
        
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def check_main_program_status(self):
        """检查主程序状态"""
        try:
            # 查找主程序窗口
            hwnd = win32gui.FindWindow(None, self.main_window_title)
            if hwnd:
                visible = win32gui.IsWindowVisible(hwnd)
                if visible:
                    print("🔍 主程序窗口可见（悬浮按钮保持显示）")
                else:
                    print("🔍 主程序窗口不可见")
            else:
                print("🔍 未找到主程序窗口")
                
        except Exception as e:
            print(f"❌ 检查主程序状态错误: {e}")
    
    def quit_floating_state(self):
        """退出悬浮按钮状态"""
        print("🔄 正在退出悬浮按钮状态...")
        
        # 停止消息监听
        self.message_listening = False
        self.pipe_listening = False
        
        # 停止状态检查定时器
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        
        # 发送退出消息到消息窗口
        try:
            if self.message_hwnd:
                win32gui.PostMessage(self.message_hwnd, win32con.WM_QUIT, 0, 0)
        except Exception as e:
            print(f"❌ 发送退出消息错误: {e}")
        
        # 关闭按钮
        self.close()
        
        # 强制退出Qt应用
        app = QApplication.instance()
        if app:
            print("🔚 正在退出Qt应用...")
            app.quit()
    
    def update_style(self):
        """更新按钮样式"""
        r, g, b = self.button_color
        tr, tg, tb = self.text_color
        
        # 使用固定圆角半径
        border_radius = min(self.width(), self.height()) // 2
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, {int(self.normal_opacity * 255)});
                color: rgb({tr}, {tg}, {tb});
                border-radius: {border_radius}px;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid rgba(255, 255, 255, 100);
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: rgba({r+20}, {g+20}, {b+20}, {int(self.hover_opacity * 255)});
            }}
        """)
    
    def get_opacity(self):
        """获取当前透明度"""
        return self.windowOpacity()
    
    def set_opacity(self, value):
        """设置透明度"""
        self.setWindowOpacity(value)
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖动/点击动画"""
        if event.button() == Qt.LeftButton:
            # 记录拖动起始位置
            self.drag_start_position = event.globalPos()
            # 记录按钮当前位置
            self.drag_button_position = self.pos()
            self.is_dragging = False
            self.start_press_animation()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖动按钮"""
        if event.buttons() == Qt.LeftButton:
            # 检查是否超过拖动阈值
            if not self.is_dragging:
                delta = (event.globalPos() - self.drag_start_position).manhattanLength()
                if delta > self.drag_threshold:
                    self.is_dragging = True
            
            # 如果确定是拖动操作，则移动按钮
            if self.is_dragging:
                # 计算正确的移动偏移量
                offset = event.globalPos() - self.drag_start_position
                # 应用偏移量到按钮的原始位置
                new_pos = self.drag_button_position + offset
                self.move(new_pos)
                event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 执行点击函数"""
        if event.button() == Qt.LeftButton:
            # 只有当不是拖动操作时才执行点击函数
            if not self.is_dragging:
                print("🎯 用户点击悬浮按钮，唤起主程序...")
                self.click_function()
            
            # 重置拖动状态
            self.is_dragging = False
            self.end_press_animation()
            event.accept()
    
    def enterEvent(self, event):
        """鼠标进入事件 - 悬停动画"""
        self.start_hover_animation(self.hover_opacity)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件 - 恢复动画"""
        self.start_hover_animation(self.normal_opacity)
        super().leaveEvent(event)
    
    def start_hover_animation(self, target_opacity):
        """启动悬停透明度动画"""
        self.hover_animation.stop()
        self.hover_animation.setStartValue(self.windowOpacity())
        self.hover_animation.setEndValue(target_opacity)
        self.hover_animation.start()
    
    def start_press_animation(self):
        """启动按下动画（缩小效果）"""
        self.press_animation.stop()
        self.press_animation.setStartValue(self.size())
        self.press_animation.setEndValue(QSize(int(self.width() * 0.9), int(self.height() * 0.9)))
        self.press_animation.start()
    
    def end_press_animation(self):
        """结束按下动画（恢复大小）"""
        self.press_animation.stop()
        # 直接设置回原始大小
        self.resize(self.sizeHint())
    
    def sizeHint(self):
        """设置按钮大小"""
        hint = super().sizeHint()
        return QSize(max(100, hint.width() + 30), max(40, hint.height() + 10))
    
    def resizeEvent(self, event):
        """当按钮大小改变时更新样式"""
        super().resizeEvent(event)
        self.update_style()
    
    def closeEvent(self, event):
        """关闭事件 - 清理资源"""
        print("🔚 关闭悬浮按钮...")
        self.message_listening = False
        self.pipe_listening = False
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        super().closeEvent(event)

def show_floating_button(titleofprogramme):
    """显示悬浮按钮的函数"""
    global app, button
    
    # 如果应用实例不存在，则创建
    if 'app' not in globals() or app is None:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    
    # 创建悬浮按钮
    button = FloatingButton(
        text="想点名就点我~",
        title=titleofprogramme,
        click_function=handle_button_click,
        opacity=0.7,
        hover_opacity=0.9,
        button_color=(70, 130, 180),  # 钢蓝色
        text_color=(255, 255, 255)    # 白色
    )
    
    print("🎉 悬浮按钮已完全启动，等待消息...")
    # 启动事件循环
    app.exec_()

def handle_button_click():
    """处理按钮点击事件"""
    print("🎯 悬浮按钮被点击了，通知主程序恢复窗口...")
    
    # 退出折叠状态 - 确保完全退出
    if 'button' in globals():
        button.quit_floating_state()
    else:
        # 如果没有 button 对象，直接退出应用
        app = QApplication.instance()
        if app:
            print("🔚 直接退出Qt应用...")
            app.quit()