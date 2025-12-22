## 1.Создайте файл sales.csv у себя на рабочем столе и наполните его данными
echo "order_id,product,amount,date
1,Book,500,2025-08-01
2,Laptop,75000,2025-08-02
3,Pen,50,2025-08-02" > sales.csv
## 2. Cкопируй файл в работающий контейнер datanode
docker cp sales.csv hdfs_3_node-datanode2-1:/tmp/sales.csv
## 3. Зайдите в контейнер и загрузите файл в HDFS. Создай директорию /user/student/sales
hdfs dfs -mkdir -p /user/student/sales
hdfs dfs -put /tmp/sales.csv /user/student/sales
## 4. Удостоверься, что файл загружен
hdfs dfs -ls -h /user/student/sales
## 5.1 Посмотрите содержимое нашего файла, взяв только первые 20 строк.
hdfs dfs -cat /user/student/sales/sales.csv | head -20
## 5.2 Скопируйте файл обратно на локальный диск.
hdfs dfs -get /user/student/sales/sales.csv ./sales_from_hdfs.csv
## 5.3. Проверить размер файла
hdfs dfs -ls -h /user/student/sales/
hdfs dfs -du -h /user/student/sales/sales.csv
## 5.4. Посчиать кол-во строк в файле
hdfs dfs -cat /user/student/sales/sales.csv | wc -l 
## 5.5 Вывести уникальные данные в первом столбце - заголовок считается
hdfs dfs -cat /user/student/sales/sales.csv | cut -d',' -f1 | sort | uniq
## 5.6. Посчитайте сколько раз встречается каждый product. Шапка считается!
hdfs dfs -cat /user/student/sales/sales.csv | cut -d',' -f2 | sort | uniq -c
## 5.7. Найдите максимальную сумму покупки.
hdfs dfs -cat /user/student/sales/sales.csv | tail -n +2 | awk -F',' '{if($3>max) max=$3} END{print max}'
## 5.8 Посчитайте общую сумму по третьей колонке.
hdfs dfs -cat /user/student/sales/sales.csv | tail -n +2 | awk -F',' '{sum+=$3} END{print sum}'
##  6. Удалите файл с которым мы только что работали. Внимание! Здесь необходимо держать 2 команды - одну, которая отправит файл в корзину (если она была бы включена), 
hdfs dfs -rm /user/student/sales/sales.csv
## а вторая удалила бы файл безвозвратно.
hdfs dfs -rm -r -skipTrash /user/student/sales


