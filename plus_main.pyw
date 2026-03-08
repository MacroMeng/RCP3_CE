
import chardet
global load, screensize

version='3.32(build260305.332.0)'
packagename='随机点名Plus_Ⅲ'
titleofprogramme=f"随机点名Plus_Ⅲ v{version}"

def function_loader(func_file=None ):
    import ast
#     with open('function_file_list.txt', 'r') as f:
#         function_file_list = [line.strip() for line in f]
    
    function_file_list = []
    important_function_list = ["config_loader.py","init.py"]
    
    if not func_file:
        for function_file in important_function_list:
            try:
                # 强制使用 UTF-8 编码，忽略错误
                with open(function_file, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        file_content = f.read()
                        if "import *" in file_content:
                            exec(file_content, globals())
                        else:
                            node = ast.parse(file_content)
                            funcs = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                            for func in funcs:
                                code = compile(ast.Module(body=[func], type_ignores=[]), '<string>', 'exec')
                                exec(code, globals())
                    except SyntaxError as e:
                        print(f"文件 {function_file} 包含语法错误: {e}")
                        continue
            except Exception as e:
                print(f"加载文件 {function_file} 时出错: {e}")
                continue
    else:
        try:
            # 强制使用 UTF-8 编码，忽略错误
            with open(func_file, 'r', encoding='utf-8', errors='ignore') as f:
                try:
                    file_content = f.read()
                    if "import *" in file_content:
                        exec(file_content, globals())
                    else:
                        node = ast.parse(file_content)
                        funcs = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        for func in funcs:
                            code = compile(ast.Module(body=[func], type_ignores=[]), '<string>', 'exec')
                            exec(code, globals())
                except SyntaxError as e:
                    print(f"文件 {func_file} 包含语法错误: {e}")
        except Exception as e:
            print(f"加载文件 {func_file} 时出错: {e}")

def create_mutex(mutex_name):
    """
    创建并检测互斥体
    参数:
        mutex_name: 互斥体名称(字符串)
    返回:
        tuple: (互斥体句柄, 是否首次创建)
    """
    mutex = win32event.CreateMutex(None, False, mutex_name)
    is_first = win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS
    return (mutex, is_first)

def find_and_send_message_to_floating_button():
    """
    查找悬浮按钮并发送恢复消息
    """
    try:
        # 查找悬浮按钮的消息窗口
        def enum_windows_callback(hwnd, _):
            try:
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                # 查找包含特定类名的窗口（悬浮按钮的消息窗口）
                if "FloatingButtonMessageWindow" in class_name:
                    # 发送自定义恢复消息
                    custom_message = win32con.WM_USER + 1000
                    win32gui.SendMessage(hwnd, custom_message, 0, 0)
                    print("已向悬浮按钮发送恢复消息")
                    return False  # 停止枚举
            except:
                pass
            return True  # 继续枚举
        
        win32gui.EnumWindows(enum_windows_callback, None)
        return True
        
    except Exception as e:
        print(f"发送消息给悬浮按钮时出错: {e}")
        return False

def find_and_activate_main_window(window_title):
    """
    查找并激活指定标题的窗口，使用多种方法确保成功
    """
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            print("未找到主程序窗口")
            return False
            
        print(f"找到窗口: {hwnd}, 标题: {window_title}")
        
        # 方法1: 使用 GetWindowPlacement 检查状态
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            print(f"窗口状态: {placement[1]}")
            
            # 如果最小化，先恢复
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                print("窗口最小化，正在恢复...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except:
            print("无法获取窗口状态")
        
        # 方法2: 强制显示窗口
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        
        # 方法3: 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        
        # 方法4: 发送系统命令
        win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
        
        # 方法5: 强制重绘
        win32gui.UpdateWindow(hwnd)
        win32gui.RedrawWindow(hwnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW)
        
        # 方法6: 模拟 Alt+Tab 行为（备用方案）
        def force_foreground(hwnd):
            """强制窗口到前台"""
            # 保存当前前景窗口
            foreground = win32gui.GetForegroundWindow()
            
            # 临时附加到当前线程
            current_thread = win32api.GetCurrentThreadId()
            window_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
            win32process.AttachThreadInput(window_thread, current_thread, True)
            
            # 设置前景窗口
            win32gui.SetForegroundWindow(hwnd)
            
            # 恢复线程附加状态
            win32process.AttachThreadInput(window_thread, current_thread, False)
            
            # 如果失败，尝试设置前景窗口为原来的
            if win32gui.GetForegroundWindow() != hwnd:
                win32gui.SetForegroundWindow(foreground)
        
        # 尝试强制前景
        force_foreground(hwnd)
        
        print("窗口激活完成")
        return True
        
    except Exception as e:
        print(f"激活窗口时出错: {e}")
        return False

def restore_minimized_window(window_title):
    """
    专门恢复最小化的窗口
    """
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            # 检查是否真的最小化了
            if win32gui.IsIconic(hwnd):
                print("检测到窗口最小化，正在恢复...")
                # 方法1: 标准恢复
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # 方法2: 发送恢复消息
                win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                
                # 等待一下让窗口恢复
                import time
                time.sleep(0.1)
                
                # 再次激活
                win32gui.SetForegroundWindow(hwnd)
                return True
        return False
    except Exception as e:
        print(f"恢复最小化窗口时出错: {e}")
        return False

def release_mutex(mutex_handle):
    """
    释放互斥体资源
    """
    if mutex_handle:
        win32api.CloseHandle(mutex_handle)




load = 0
screensize = (960, 540)
MUTEX_NAME = "RCP_3"
import win32api
import win32event
import winerror

mutex, is_first = create_mutex(MUTEX_NAME)
# 优先使用以前的稳定逻辑，同时保留暴力激活作为备用
if not is_first:
    from pipe_receiver import PipeReceiver
    import win32gui
    import win32con
    import win32process
    print("程序已在运行中！正在尝试激活窗口...")
    
    # 第一步：优先尝试以前的稳定方法 - 管道通信
    try:
        from pipe_sender import send_pipe_message
        print("🔄 优先尝试管道通信...")
        success, response = send_pipe_message(r'\\.\pipe\FloatingButtonPipe', "SHOW_WINDOW")
        
        if success:
            print(f"✅ 管道消息发送成功，响应: {response}")
            if "WINDOW_SHOW_COMMAND_RECEIVED" in response:
                print("✅ 悬浮按钮已收到恢复指令")
                # 等待一下让窗口恢复
                time.sleep(0.5)
                # 再尝试激活确保窗口在前台
                find_and_activate_main_window(titleofprogramme)
                sys.exit(0)
            else:
                print("⚠️ 悬浮按钮响应异常，继续尝试其他方法")
        else:
            print(f"❌ 管道消息发送失败: {response}")
    except Exception as e:
        print(f'❌ 发送管道消息出错: {e}')
        
    # 第二步：尝试窗口消息（以前的稳定方法）
    print("🔄 尝试窗口消息...")
    if find_and_send_message_to_floating_button():
        print("✅ 窗口消息发送成功")
        # 等待一下让窗口恢复
        time.sleep(0.5)
        # 再尝试激活确保窗口在前台
        find_and_activate_main_window(titleofprogramme)
        sys.exit(0)
    else:
        print("❌ 未找到悬浮按钮")
        
    # 第三步：如果以上方法都失败，使用暴力激活方法
    print("🔄 稳定方法失败，尝试暴力激活...")
        
    # 暴力激活方法（简化版）
    activation_attempts = [
        ("恢复最小化窗口", lambda: restore_minimized_window(titleofprogramme)),
        ("直接激活主窗口", lambda: find_and_activate_main_window(titleofprogramme)),
    ]
        
    success = False
    for method_name, method_func in activation_attempts:
        print(f"尝试: {method_name}")
        try:
            if method_func():
                print(f"✅ {method_name} 成功！")
                success = True
                break
        except Exception as e:
            print(f"💥 {method_name} 出错: {e}")
        time.sleep(0.1)
        
    if success:
        print("🎉 窗口激活成功！")
        sys.exit(0)
    else:
        print("😵 所有方法都失败了...")
        win32gui.MessageBox(0, 
            "🧠 随机点名Plus 已在运行！\n\n💡 如果找不到窗口：\n• 检查系统托盘区\n• 或已打包为悬浮按钮\n• 尝试按 Ctrl+Shift+Esc 查看进程", 
            "程序已运行 - 随机点名Plus", 
            win32con.MB_OK | win32con.MB_ICONWARNING)
        sys.exit(1)

def _k_():
    global k,window_width, window_height
    k=min(window_width/960,window_height/540)
    return k

def proportional_scale(img, max_width, max_height):
    global window_width, window_height, bg
    ratio = max(window_width/img.get_width(), window_height/img.get_height())
    bg= pygame.transform.smoothscale(img, 
        (int(img.get_width()*ratio), int(img.get_height()*ratio)))
    return bg

def background():
    global window_width, window_height,background_image,bg
    try:
        screen.blit(bg,((window_width-bg.get_width())/2,(window_height-bg.get_height())/2))
    except :
        screen.fill((0,0,0))
        errorbackground=pygame.font.SysFont("MicrosoftYaHei UI",int(20*k)).render("加载背景失败，已使用黑色背景",True,(255,255,255))
        screen.blit(errorbackground,(0,0))
        pygame.display.update((0,0,errorbackground.get_width(),errorbackground.get_height()))


def showclock(flush=True):
    global screen,k,window_width, window_height,clocksurface
    clock_time=pygame.font.SysFont("MicrosoftYaHei UI",int(30*k)).render(datetime.datetime.now().strftime("%H:%M:%S"),True,(255,255,255))
    screen.blit(clocksurface,((window_width-130*k),0))
    screen.blit(clock_time,((130*k-clock_time.get_width())/2-2*k+(window_width-130*k),(40*k-clock_time.get_height())/2))
    if flush:
        pygame.display.update(((window_width-130*k),0,140*k,40*k))

def draw_lastname(flush=True,temp=False):
    global tempsurface_2,namesurface,k
    text=pygame.font.SysFont("MicrosoftYaHei UI",size=int(150*k)).render(lastname,True,(255,255,255))
    if temp:
        k=_k_()
        namesurface=pygame.Surface((4.5*150*k+30*k,150*k+60*k),SRCALPHA | HWSURFACE )
        pygame.draw.rect(namesurface, (0,0,0,155), (0,0,4.5*150*k+30*k,150*k+60*k), border_radius=int(33*k))
        tempsurface_2.blit(namesurface,((window_width-4.5*150*k)/2+8*k,(window_height-150*k)/2-30*k))
        tempsurface_2.blit(text, ((4.5*150*k+30*k-text.get_width())/2-2*k+(window_width-4.5*150*k)/2+8*k,(150*k+60*k-text.get_height())/2-10*k+(window_height-150*k)/2-30*k))
        return 
    screen.blit(namesurface,((window_width-4.5*150*k)/2+8*k,(window_height-150*k)/2-30*k))
    screen.blit(text, ((4.5*150*k+30*k-text.get_width())/2-2*k+(window_width-4.5*150*k)/2+8*k,(150*k+60*k-text.get_height())/2-10*k+(window_height-150*k)/2-30*k))
    if flush:
        pygame.display.update(((window_width-4.5*150*k)/2+8*k,(window_height-150*k)/2-30*k,4.5*150*k+30*k,150*k+60*k))

def message(text,flush=True,temp=False):
    global k,size,messagesurface,pos,updatearea,tempsurface_2
    window_width, window_height = pygame.display.get_surface().get_size()
    if text!='':
        window_width, window_height = pygame.display.get_surface().get_size()
        textfont=pygame.font.SysFont("MicrosoftYaHei UI",int(20*k))
        _text_=textfont.render(text,True,(255,255,255))
        size=(_text_.get_width()+20*k,_text_.get_height()+10*k)
        messagesurface=pygame.Surface(size,SRCALPHA)
        messagesurface.fill((0,0,0,0))
        pygame.draw.rect(messagesurface, (0,0,0,127), (0,0,_text_.get_width()+20*k,_text_.get_height()+10*k), border_radius=int(5*k))
        messagesurface.blit(_text_,(10*k,5*k))
        pos=((window_width-(_text_.get_width()+20*k))/2,60*k)
        if temp:
            tempsurface_2.blit(messagesurface,pos)
        screen.blit(messagesurface,pos)
        updatearea=((window_width-(_text_.get_width()+20*k))/2,60*k,_text_.get_width()+20*k,_text_.get_height()+10*k)
    else:
        messagesurface.fill((0,0,0,0))
        screen.blit(messagesurface,pos)
    if flush:
        pygame.display.update(updatearea)



try:
    import pygame,sys,os,configparser,random
    from pygame.locals import *
    function_loader()
    init()

except Exception as e:
    import win32gui
    import win32con
    #import win32process
    print(f'哎呀！出错啦！\f{e}')
    win32gui.MessageBox(0, str(e),  "哎呀！出错啦！", win32con.MB_OK | win32con.MB_ICONWARNING)
    sys.exit(114514)