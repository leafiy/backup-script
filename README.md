# OSS 备份脚本

这是一个用 Python 编写的自动化脚本，用于将指定文件夹备份到阿里云对象存储服务（OSS）。脚本支持多文件夹备份、自定义备份名称，并可以通过系统定时任务进行自动化备份。

## 功能特点

- 支持多个文件夹的备份
- 自定义备份文件名，包含文件夹路径信息
- 将备份文件上传到阿里云 OSS
- 上传后自动删除本地备份文件
- 支持通过命令行参数进行操作
- 配置信息存储在 JSON 文件中，便于管理

## 安装

1. 克隆此仓库：

   ```
   git clone https://github.com/yourusername/oss-backup-script.git
   cd oss-backup-script
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 配置

首次使用前，需要配置 OSS 信息：

```
python backup_script.py --configure
```

按照提示输入您的 OSS Access Key ID、Access Key Secret、Bucket 名称和 Endpoint。

## 使用方法

1. 添加需要备份的文件夹：

   ```
   python backup_script.py --add /path/to/folder
   ```

2. 列出当前配置的备份文件夹：

   ```
   python backup_script.py --list
   ```

3. 执行备份任务：
   ```
   python backup_script.py --backup
   ```

## 自动化备份

要设置自动化备份，可以使用系统的定时任务工具。

### 在 Linux 上使用 cron：

1. 编辑 crontab：

   ```
   crontab -e
   ```

2. 添加以下行来在每天凌晨 1 点运行脚本：
   ```
   0 1 * * * /usr/bin/python3 /path/to/your/backup_script.py --backup
   ```

### 在 Windows 上使用任务计划程序：

1. 打开任务计划程序
2. 创建一个新任务
3. 在"操作"选项卡中，添加程序：`python`
4. 添加参数：`C:\path\to\your\backup_script.py --backup`
5. 设置运行时间为每天凌晨 1 点

## 注意事项

- 确保 `backup_config.json` 文件的权限设置正确，因为它包含敏感信息。
- 建议将 `backup_config.json` 添加到 `.gitignore` 文件中，以避免意外提交敏感信息。
- 如果备份的文件夹路径很长，可能会生成很长的文件名。在某些文件系统中可能会遇到限制。
