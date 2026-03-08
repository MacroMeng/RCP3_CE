# random_choose_plus.exe.py
"""
双击即可的启动器 - 编译后直接运行plus_main.pyw的内容
"""
import sys
import os

# 设置当前目录为exe所在目录
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# 直接导入plus_main.pyw并运行
sys.path.insert(0, os.getcwd())

try:
    # 直接执行plus_main.pyw的代码
    with open('plus_main.pyw', 'r', encoding='utf-8') as f:
        code = f.read()

    # 创建执行环境
    exec_globals = {
        '__name__': '__main__',
        '__file__': 'plus_main.pyw',
        '__builtins__': __builtins__,
    }

    # 执行
    exec(code, exec_globals)

except FileNotFoundError:
    import ctypes

    ctypes.windll.user32.MessageBoxW(
        0, '找不到 plus_main.pyw 文件\n请确保exe和主程序在同一目录', '错误', 0x10
    )
except Exception as e:
    error_msg = f'启动错误:\n{str(e)}'
    import ctypes

    ctypes.windll.user32.MessageBoxW(0, error_msg, '随机点名Plus错误', 0x10)
