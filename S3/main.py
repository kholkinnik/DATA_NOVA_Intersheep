import boto3

session = boto3.Session(
    aws_access_key_id='admin',
    aws_secret_access_key='StrongPassword123!',
)
# Создаем клиент
s3_client = session.client('s3', endpoint_url='http://localhost:9000')

# Создаю Бакет
# s3_client.create_bucket(Bucket='my-bucket')

# # Загрузка файла
s3_client.put_object(Bucket='my-bucket', Key='file.txt', Body=b'Hello, S3!')

# # Чтение файла
response = s3_client.get_object(Bucket='my-bucket', Key='file.txt')
data = response['Body'].read()  # Получаем байты