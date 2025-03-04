import os
import shutil
import datetime

# Source and destination paths
source = 'C:/path/to/source_directory'
destination = 'C:/path/to/backup_directory'

# Create a timestamp for the backup folder
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

# Create a backup folder
backup_folder = os.path.join(destination, f'backup_{timestamp}')

# Copy all contents from source to backup folder
shutil.copytree(source, backup_folder)

print(f"Backup successful! Files backed up to: {backup_folder}")

