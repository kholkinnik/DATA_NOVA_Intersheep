# Данный скрипт удаляет файл в контейнере, копирует его из hdfs в контейнер  а потом из контейнера на хост
import subprocess

hdfs_path = "/user/hdfs/testfile/big_file.csv"
local_path_in_container = "/tmp/big_file.csv"
local_output_path = "C:/Users/xiaomi/Desktop/DATA_NOVA/HDFS/HDFS_3_NODE/big_file_from_hdfs_1.csv"
container = "hdfs_3_node-datanode2-1"

# Удаляем старый файл внутри контейнера (если есть)
subprocess.run([
    "docker", "exec", container, "rm", "-f", local_path_in_container
], check=True)

# Копируем файл из HDFS внутрь контейнера
subprocess.run([
    "docker", "exec", container, "hdfs", "dfs", "-get", hdfs_path, local_path_in_container
], check=True)

# Копируем файл из контейнера на хост
subprocess.run([
    "docker", "cp", f"{container}:{local_path_in_container}", local_output_path
], check=True)
print("Файл на хосте  - 💻 ща почитаем")
# Читаем файл на хосте
with open(local_output_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        print(line.strip())
        if i >= 10:
            break
