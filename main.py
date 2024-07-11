import json
import logging
import os
import re
import shutil
from pathlib import Path

# 切换到脚本所在目录
os.chdir(Path(__file__).resolve().parent)

# 配置logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建文件handler以写入日志文件
file_handler = logging.FileHandler('bangumi.log', mode='a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

global BANGUMI_LIST, TRADITION_KEYS


def read_config():
    if not os.path.isfile('bangumi.conf'):
        raise Exception('番剧配置不存在')
    with open('bangumi.conf', 'r', encoding='utf-8') as file:
        config = json.load(file)
        logger.info("config loaded: " + str(config))
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
                if any(tradition_key in file for tradition_key in TRADITION_KEYS) and "Baha" not in file:
                    os.remove(file)
                    logger.info(f"删除繁体番剧 {file}")
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
                    logger.info(f"Moved {old_path} to {new_path}")
                else:
                    logger.error(f"无法匹配文件名集数 {file}")


if __name__ == '__main__':
    read_config()
    rename_and_move()
