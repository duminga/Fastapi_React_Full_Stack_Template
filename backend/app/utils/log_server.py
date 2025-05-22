import logging
import os
import sys
import colorlog
from datetime import datetime

class logServer:
    _instance = None

    def __init__(self):
        # 如果是打包的可执行文件，获取当前可执行文件的路径
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            executable_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 未打包时，获取当前脚本路径的上层文件夹
            executable_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
        # 将反斜杠替换为正斜杠
        executable_path = executable_path.replace('\\', '/')
        # 定位到日志文件夹
        logs_folder = os.path.join(executable_path, "logs")
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

        current_time = datetime.now().strftime('%Y%m%d_%H%M')  # 获取当前时间
        self.filename = os.path.join(logs_folder, f'日记记录_{current_time}.log')
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def run(self):
        # 创建 logger
        logger = logging.getLogger('日记记录器')
        logger.setLevel(logging.DEBUG)  # 设置日志级别
        # 检查是否已经有文件处理器和流处理器被添加
        if not logger.handlers:  # 如果没有处理器被添加
            # 创建一个文件处理器，用于写入日志文件
            file_handler = logging.FileHandler(self.filename, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # 修改为 DEBUG，记录所有级别的日志

            # 创建一个流处理器，用于输出到控制台
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)  # 控制台输出所有级别的日志

            # 创建日志格式
            formatter = logging.Formatter(
                f'%(asctime)s - %(levelname)s - [%(filename)s-%(lineno)s] - [%(funcName)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
            console_handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(levelname)s - [%(filename)s-%(lineno)s] - [%(funcName)s]  - %(message)s%(reset)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            ))
            file_handler.setFormatter(formatter)

            # 将处理器添加到 logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return logger

if __name__ == '__main__':
    logger = logServer().run()
    # 测试日志
    logger.debug('这是一个 debug 级别的消息')
    logger.info('这是一个 info 级别的消息')
    logger.warning('这是一个 warning 级别的消息')
    logger.error('这是一个 error 级别的消息')
    logger.critical('这是一个 critical 级别的消息')
