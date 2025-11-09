# Перенос файла- json в контейнер с mongo_db
docker cp products.json mongo_db:/products.json

# распарсим документ на 5 
docker exec -it mongo_db mongoimport --db alcomarket --collection products --file /products.json --jsonArray


#  как загрузить все через Python смотри в скрипте
установи mongo через pip install pymongo
