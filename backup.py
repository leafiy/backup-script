import os
import sys
import json
import tarfile
import oss2
from datetime import datetime
import argparse

# 配置文件路径
CONFIG_FILE = 'backup_config.json'

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
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

def create_backup(folders):
    """创建多个文件夹的压缩备份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    backup_files = []
    for folder in folders:
        # 使用文件夹名和路径创建唯一的备份名称
        folder_name = os.path.basename(folder)
        sanitized_path = folder.replace('/', '_').replace('\\', '_').replace(':', '_')
        backup_filename = f'backup_{sanitized_path}_{timestamp}.tar.gz'
        
        with tarfile.open(backup_filename, "w:gz") as tar:
            tar.add(folder, arcname=folder_name)
        
        backup_files.append(backup_filename)
    
    return backup_files

def upload_to_oss(local_file, oss_config):
    """将文件上传到 OSS"""
    auth = oss2.Auth(oss_config['access_key_id'], oss_config['access_key_secret'])
    bucket = oss2.Bucket(auth, oss_config['endpoint'], oss_config['bucket_name'])
    
    remote_file = os.path.basename(local_file)
    bucket.put_object_from_file(remote_file, local_file)

def delete_local_backup(filename):
    """删除本地备份文件"""
    os.remove(filename)

def backup_job():
    """执行备份任务"""
    print("开始备份任务...")
    config = load_config()
    if not config["folders"]:
        print("没有配置备份文件夹，备份任务终止")
        return
    
    if not all(config["oss_config"].values()):
        print("OSS 配置不完整，备份任务终止")
        return

    backup_files = create_backup(config["folders"])
    for backup_file in backup_files:
        print(f"创建了备份文件: {backup_file}")
        
        upload_to_oss(backup_file, config["oss_config"])
        print(f"上传了备份文件到 OSS: {backup_file}")
        
        delete_local_backup(backup_file)
        print(f"删除了本地备份文件: {backup_file}")
    
    print("备份任务完成")

def list_folders():
    """列出所有正在备份的文件夹"""
    config = load_config()
    if config["folders"]:
        print("正在备份的文件夹：")
        for folder in config["folders"]:
            print(f"- {folder}")
    else:
        print("当前没有配置任何备份文件夹")

def add_folder(folder):
    """添加需要备份的文件夹"""
    if not os.path.isdir(folder):
        print(f"错误：{folder} 不是一个有效的文件夹")
        return

    config = load_config()
    if folder not in config["folders"]:
        config["folders"].append(folder)
        save_config(config)
        print(f"已添加文件夹到备份列表：{folder}")
    else:
        print(f"文件夹已在备份列表中：{folder}")

def configure_oss():
    """配置 OSS 信息"""
    config = load_config()
    oss_config = config["oss_config"]
    
    oss_config["access_key_id"] = input("请输入 Access Key ID: ") or oss_config["access_key_id"]
    oss_config["access_key_secret"] = input("请输入 Access Key Secret: ") or oss_config["access_key_secret"]
    oss_config["bucket_name"] = input("请输入 Bucket 名称: ") or oss_config["bucket_name"]
    oss_config["endpoint"] = input("请输入 Endpoint: ") or oss_config["endpoint"]
    
    save_config(config)
    print("OSS 配置已更新")

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