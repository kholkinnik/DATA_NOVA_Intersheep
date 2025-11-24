# Создаю Alarm Оповещение yf gjxne если данные не прилетели из кафка за определенный промежуток времени

# запусти docker-compose
docker- compose up -d

# создай таблицы 
python create_table.py

# создай данные и передай в топик kafka
python producer.py

# забери данные из топика Kafka  и переложи в таблицу customer.sales а информацию об отправке в customer.imports
python consumer.py

# проверь есть ли данные за кокретную дату {today}
test_data.ipynb

# создай пароль прилоежений для отправки письма на почту через протокол SMTP, и отправь ALARM если данных нет
send_ALARM.ipynb