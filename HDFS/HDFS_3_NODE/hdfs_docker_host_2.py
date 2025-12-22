#Файл так же перкидывает файл из hdfs-docker-host
import subprocess
import os
hdfs_path = "/user/hdfs/testfile/big_file.csv"
local_path_in_container = "/tmp/big_file.csv"
local_output_path = "C:/Users/xiaomi/Desktop/DATA_NOVA/HDFS/HDFS_3_NODE/big_file_from_hdfs_2.csv"
container = "hdfs_3_node-datanode2-1"

# Удаляем файл, если он есть внутри контейнера
subprocess.run([
    "docker", "exec", container, "rm", "-f", local_path_in_container
], check=True)

# Копируем из HDFS в контейнер
subprocess.run([
    "docker", "exec", container, "hdfs", "dfs", "-get", hdfs_path, local_path_in_container
], check=True)

# Копируем из контейнера на хост
subprocess.run([
    "docker", "cp", f"{container}:{local_path_in_container}", local_output_path
], check=True)

# Подтверждение
if os.path.exists(local_output_path):
    print(f" Файл успешно скопирован в: {local_output_path}")