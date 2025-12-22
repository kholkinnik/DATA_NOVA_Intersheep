# Клонирую репозиторий
git clone https://github.com/mentorops/hadoop.git
# Поднимай контейнер
docker compose up -d
# Заходим в контейнер
docker exec -it hive bash
# Подключение к клиенту JDBC - beeline
beeline -u 'jdbc:hive2://localhost:10000' -n root   --(краткий обзор hdfs кластера)

# РАБОТА С ФАЙЛАМИ  
## Посмотреть репорт по нодам
hdfs dfsadmin -report
## 1. Создай файл.csv скопируй его из хоста -> контейнер Docker -> потом в hdfs
docker cp big_file.csv hive:/tmp/big_file.csv
## 2. Проверяем файл в контейнере (-lh - удобочитаемый формат)
docker exec hive ls -h /tmp/big_file.csv
## 3.Создай папку user/hdfs/testfile
hdfs dfs -mkdir -p /user/hdfs/testfile/
## 4.Заходим в контейнер и копируем (переносим в HDFS)
hdfs dfs -put /tmp/big_file.csv /user/hdfs/testfile/
## 4.1. Перенос из hdfs в контейнер 
hdfs dfs -get /user/hdfs/testfile/big_file.csv /tmp/big_file.csv
## 4.2. Перенос из контейнера на хост 
docker cp hdfs_3_node-datanode2-1:/tmp/big_file.csv .\big_file_host.csv
## 5. проверяем наличие файлов на hdfs (-h - в человекочитаемом виде для hdfs!)
hdfs dfs -ls -h /user/hdfs/testfile/
## 6. как выглядит файл в hdfs
hdfs fsck /user/hdfs/testfile/big_file.csv -files -blocks -locations
## 7.Удалить файл с hdfs (сначала отключаем safe mode)
hdfs dfsadmin -safemode get      -- посмотреть режим для Safe mode
hdfs dfsadmin -safemode leave    -- отключить safe mode
hdfs dfsadmin -safemode enter    -- включить safe mode
hdfs dfs -rm /user/hdfs/testfile/big_file.csv
## 8.Останавливаю Дата Ноду
docker stop hdfs_3_node-datanode1-1 hdfs_3_node-datanode3-1
