# WINDOWS Powershell
$headers = @{ "Content-Type" = "application/json" }
$body = '{
    "name": "pg-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "user",
      "database.password": "password",
      "database.dbname": "source_db",
      "topic.prefix": "pgserver1",
      "table.include.list": "public.my_table",
      "plugin.name": "pgoutput",
      "slot.name": "debezium_slot"
    }
}'

Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method POST -Headers $headers -Body $body

# Linux MacOS
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pg-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "user",
      "database.password": "password",
      "database.dbname": "source_db",
      "topic.prefix": "pgserver1",
      "table.include.list": "public.my_table",
      "plugin.name": "pgoutput",
      "slot.name": "debezium_slot"
    }
  }'