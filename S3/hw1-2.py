import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import json
import time
# библиотеки для переменных окружения
import os
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
endpoint = os.getenv("ENDPOINT")
access_key = os.getenv("ACCESS_KEY")
secret_key = os.getenv("SECRET_KEY")

#save_path = 'C:/Users/xiaomi/Desktop/S3/tex.txt'
# переопределяю класс 
class S3Client:
    def __init__(self, endpoint, access_key, secret_key, bucket):
        """
        Инициализация клиента для работы с S3-совместимым хранилищем.
        """
        self.bucket = bucket

        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint,            # URL S3-хранилища у меня Docker-Образ
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
            region_name="us-east-1"
        )
    
    # Метод - Загружает файл в бакет.
    def upload(self, file_path, object_name):

        self.s3.upload_file(file_path, self.bucket, object_name)
        print(f"Загружен файл: {object_name} в бакет {self.bucket}")

    def download(self, object_name, save_path):
        """
        Скачивает объект из S3.
        """
        self.s3.download_file(self.bucket, object_name, save_path)
        print(f"Скачано: {object_name}")

    # Метод из задания- выводит список объектов в бакете 
    def list_files(self):
        response = self.s3.list_objects_v2(Bucket=self.bucket)
        if "Contents" not in response:
            return []

        print ([obj["Key"] for obj in response["Contents"]])
        
   
    # Метод из задания- Проверяет существование объекта в бакете. Возвращает True/False.
    def file_exists(self, object_name):
        try:
            self.s3.head_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError:
            return False
    
    # Настройка Bucket policy
    def setup_bucket_policy(self):
        """Любой может читать, только владелец (я) пишу"""
        policy = {
            "Version": "2012-10-17",   # указываю текущую стабильныую версию
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket}/*"
                },
                {
                    "Sid": "OwnerFullAccess",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam:::{access_key}:user/{access_key}"},
                    "Action": "s3:*",
                    "Resource": [f"arn:aws:s3:::{self.bucket}", f"arn:aws:s3:::{self.bucket}/*"]
                }
            ]
        }
        self.s3.put_bucket_policy(Bucket=self.bucket, Policy=json.dumps(policy))
        print(f"✅ Bucket policy настроена для {self.bucket}")

    # Добавление- включение версионирования
    def enable_versioning(self):
        
        self.s3.put_bucket_versioning(
            Bucket=self.bucket,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✅ Версионирование включено")

    
    # Удаление объектов из бакета через 3 дн
    def setup_lifecycle_policy(self):
            """Удаление объектов через 3 дня"""
            lifecycle = {
                "Rules": [
                    {
                        "ID": "DeleteAfter3Days",
                        "Status": "Enabled",
                        "Filter": {"Prefix": ""},
                        "Expiration": {"Days": 3}
                    }
                ]
            }
            self.s3.put_bucket_lifecycle_configuration(
                Bucket=self.bucket,
                LifecycleConfiguration=lifecycle
            )
            print("✅ Lifecycle policy: удаление через 3 дня")
        
        
# создаём экземпляр класса
s3 = S3Client(
    endpoint=endpoint,
    access_key=access_key,
    secret_key=secret_key,
    bucket='my-bucket',          # имя существующего бакета
)

 
# вызываем метод download
#s3.upload('C:/Users/xiaomi/Desktop/S3/text1.txt', 'text1-s3.txt')
#

# создаем несколько весрисий файла и загружаю на s3

# 1. Настройка политик версионирования и правил удаленя для объекта
s3.setup_bucket_policy()
s3.enable_versioning()
s3.setup_lifecycle_policy()

# 2. Создаём несколько версий файла и загружаем
n = 5 # 
for i in range(n):
    with open('test-version.txt', 'w') as f:
        f.write(f'Version {i+1}')

    s3.upload('test-version.txt', 'test-version.txt')
    print(f"📤 Загружена версия {i+1}")
    time.sleep(1) 

# 3. Список версий
versions = s3.s3.list_object_versions(Bucket=s3.bucket)
print("📋 Версии файла test-version.txt:")
for ver in versions.get('Versions', []):
    if ver['Key'] == 'test-version.txt':
        print(f"  ID: {ver['VersionId']}... | Текущая: {ver['IsLatest']}")

# 4. Скачиваем предыдущую версию
old_version_id = next(v['VersionId'] for v in versions['Versions'] 
                     if v['Key'] == 'test-version.txt' and not v['IsLatest'])

response = s3.s3.get_object(
    Bucket=s3.bucket,
    Key='test-version.txt',
    VersionId=old_version_id
)
old_content = response['Body'].read().decode('utf-8', errors='replace')
print(f"📥 Предыдущая версия: {old_content}")


