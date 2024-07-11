import json
import logging
import os
import re
import shutil
from pathlib import Path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

os.chdir(Path(__file__).resolve().parent)
logging.basicConfig(level=logging.DEBUG,
                    filename='bangumi.log',  # 日志文件名
                    filemode='a',  # 'w' 为覆盖写入，'a' 为追加
                    encoding='utf8',
                    format='%(asctime)s - %(levelname)s - %(message)s')  # 日志格式

global BANGUMI_LIST, TRADITION_KEYS


def read_config():
    if not os.path.isfile('bangumi.conf'):
        raise Exception('番剧配置不存在')
    with open('bangumi.conf', 'r', encoding='utf-8') as file:
        config = json.load(file)
        logging.info("config loaded: " + str(config))
        global BANGUMI_LIST, TRADITION_KEYS
        BANGUMI_LIST = config['bangumi_list']
        TRADITION_KEYS = config['tradition_keys']


def rename_and_move():
    for bangumi in BANGUMI_LIST:
        key = bangumi['key']
        name = bangumi['name']
        season = bangumi['season']
        target_dir = os.path.join(os.getcwd(), name)

        for file in os.listdir(os.getcwd()):
            if os.path.isdir(file):
                continue
            if key in file:
                # 更新集数匹配正则表达式，适配更多文件名格式
                if any(tradition_key in file for tradition_key in TRADITION_KEYS) and "Baha" not in file:
                    os.remove(file)
                    logging.info(f"删除繁体番剧 {file}")
                    print(f"删除繁体番剧 {file}")
                    continue
                episode_match = re.search(r'\[?(\d{2})\]?|[-\s]*(\d{2})[-\s]*', file)
                if episode_match:
                    episode_number = episode_match.group(1) or episode_match.group(2)
                    new_filename = f"{season}E{episode_number}-{file}"
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    old_path = os.path.join(os.getcwd(), file)
                    new_path = os.path.join(target_dir, new_filename)
                    
                    shutil.move(old_path, new_path)
                    logging.info(f"Moved {old_path} to {new_path}")
                    print(f"Moved {old_path} to {new_path}")
                else:
                    logging.error(f"无法匹配文件名集数 {file}")
                    print(f"无法匹配文件名集数 {file}")


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 此方法在检测到文件被创建时调用
        if not event.is_directory:
            print(f'新文件 {event.src_path} 已创建！')
            # 这里可以添加你希望在文件创建时执行的代码
            read_config()
            rename_and_move()


def main():
    path = '.'  # 设置监控的目录为当前目录
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    read_config()
    rename_and_move()
    main()
