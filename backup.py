#!/usr/bin/env python3
import os
import json
import tarfile
import oss2
from datetime import datetime
import argparse
import logging

# 配置文件路径使用绝对路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup_config.json')

# 设置日志
logging.basicConfig(filename='/tmp/backup_script.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """加载配置文件"""
    logging.info(f"尝试加载配置文件: {CONFIG_FILE}")
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            logging.info(f"成功加载配置文件，包含 {len(config['folders'])} 个文件夹")
            return config
    logging.warning("配置文件不存在，使用默认配置")
    return {
        "folders": [],
        "oss_config": {
            "access_key_id": "",
            "access_key_secret": "",
            "bucket_name": "",
            "endpoint": ""
        }
    }

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    logging.info("配置已保存")

def create_backup(folders):
    """创建多个文件夹的压缩备份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_files = []
    for folder in folders:
        if not os.path.exists(folder):
            logging.warning(f"文件夹不存在: {folder}")
            continue
        folder_name = os.path.basename(folder)
        sanitized_path = folder.replace('/', '_').replace('\\', '_').replace(':', '_')
        backup_filename = f'backup_{sanitized_path}_{timestamp}.tar.gz'
        backup_path = os.path.join('/tmp', backup_filename)
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(folder, arcname=folder_name)
        backup_files.append(backup_path)
        logging.info(f"创建备份文件: {backup_path}")
    return backup_files

def upload_to_oss(local_file, oss_config):
    """将文件上传到 OSS"""
    auth = oss2.Auth(oss_config['access_key_id'], oss_config['access_key_secret'])
    bucket = oss2.Bucket(auth, oss_config['endpoint'], oss_config['bucket_name'])
    remote_file = os.path.basename(local_file)
    bucket.put_object_from_file(remote_file, local_file)
    logging.info(f"文件已上传到 OSS: {remote_file}")

def delete_local_backup(filename):
    """删除本地备份文件"""
    os.remove(filename)
    logging.info(f"删除本地备份文件: {filename}")

def backup_job():
    """执行备份任务"""
    logging.info("开始备份任务...")
    config = load_config()
    if not config["folders"]:
        logging.error("没有配置备份文件夹，备份任务终止")
        return
    if not all(config["oss_config"].values()):
        logging.error("OSS 配置不完整，备份任务终止")
        return
    backup_files = create_backup(config["folders"])
    for backup_file in backup_files:
        upload_to_oss(backup_file, config["oss_config"])
        delete_local_backup(backup_file)
    logging.info("备份任务完成")

# ... 其他函数保持不变 ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSS 备份脚本")
    parser.add_argument("--list", action="store_true", help="列出所有正在备份的文件夹")
    parser.add_argument("--add", type=str, help="添加需要备份的文件夹")
    parser.add_argument("--backup", action="store_true", help="执行备份任务")
    parser.add_argument("--configure", action="store_true", help="配置 OSS 信息")
    args = parser.parse_args()

    if args.list:
        list_folders()
    elif args.add:
        add_folder(args.add)
    elif args.backup:
        backup_job()
    elif args.configure:
        configure_oss()
    else:
        parser.print_help()