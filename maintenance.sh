#!/bin/bash
# 简单的维护脚本：备份数据库与清理旧日志

BACKUP_DIR="./backups"
DB_FILE="data.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 1. Backup DB
if [ -f "$DB_FILE" ]; then
    echo "Backing up database..."
    cp $DB_FILE "$BACKUP_DIR/data_$DATE.db"
    echo "Backup created: $BACKUP_DIR/data_$DATE.db"
else
    echo "Database file not found!"
fi

# 2. Rotate Logs (Simulation)
# In Docker, logs are handled by daemon, but we can clean local temp files
echo "Cleaning up temporary files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} +

echo "Maintenance completed."
