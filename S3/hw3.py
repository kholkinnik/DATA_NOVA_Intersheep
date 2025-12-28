import os
import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List
from dotenv import load_dotenv
import pandas as pd
import watchfiles
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

# Настройка логирования в отдельный файл
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataPipeline")

load_dotenv()
endpoint = os.getenv("ENDPOINT")
access_key = os.getenv("ACCESS_KEY")
secret_key = os.getenv("SECRET_KEY")

WATCH_DIR = Path("watch_folder")
ARCHIVE_DIR = Path("archive")
TEMP_DIR = Path("temp")

# Прописываю класс
class DataPipeline:
    def __init__(self):
        self._auth = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint,
        }
        self._bucket = "bucket-for-clean-csv"
        self._session = get_session()
        self._processed_count = 0

    async def process_file(self, file_path: Path):
        """✅ РАБОЧАЯ обработка файла"""
        try:
            logger.info(f"Processing file {file_path}")
            print(f"Начало обработки {file_path}🚀🚀🚀🚀 ")
            
            # 1. Чтение CSV
            df = pd.read_csv(file_path)
            logger.info(f"Read {len(df)} rows from {file_path.name}")
            
            # 2. Фильтрация (обработка нулевых значений)
            df_filtered = df.dropna()
            logger.info(f"Rows in file {len(df)} after {len(df_filtered)} rows") 
            print(f"Количество строк до фильтрации {len(df)} стало → {len(df_filtered)} строк") 
            
                      
            # 3. Перемещение в папку для временных файлов
            temp_file = TEMP_DIR / f"processed_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_filtered.to_csv(temp_file, index=False)
            logger.info(f"File processed_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv moved in temp")
            print("Файл перемещен в TEMP ✅")
            
            # 4. S3 загрузка
            s3_key = f"{temp_file.name}"
            await self.upload_to_s3(temp_file, s3_key)
            logger.info(f"File {temp_file.name} moved in s3")
            print("Файл перемещен в S3 ✅")
            
            # 5. Архив
            archive_file = ARCHIVE_DIR/file_path.name
            shutil.move(str(file_path), str(archive_file))
            logger.info(f"File archived: {archive_file}")
            print("Файk перемещен в АРХИВ ✅")

            
        except Exception as e:
            logger.error(f"Failed {file_path}: {e}")
            return False

    async def upload_to_s3(self, local_file: Path, s3_key: str):
        async with self._session.create_client("s3", **self._auth) as client:
            with local_file.open("rb") as data:
                await client.put_object(Bucket=self._bucket, Key=s3_key, Body=data)

    async def upload_logs(self):
        log_file = Path("pipeline.log")
        if log_file.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"logs/pipeline_{timestamp}.log"
            await self.upload_to_s3(log_file, s3_key)
            logger.info(f"Logs uploaded: {s3_key}")

# ✅ Проверка папки на наличие новых файлов
async def check_folder(pipeline: DataPipeline):
    files = list(WATCH_DIR.iterdir())
    csv_files = [f for f in files if f.suffix.lower() == '.csv']
    
    if not csv_files:
        logger.info(f"Folder {WATCH_DIR} empty")
        return False
    else:
        logger.info(f"Find {len(csv_files)} CSV in {WATCH_DIR}")
        print("✅Файлы найдены, начала обработки")
        # Обрабатываем ВСЕ существующие CSV
        for csv_file in csv_files:
            await pipeline.process_file(csv_file)
        return True

async def main():
    logger.info("Starting Data Pipeline...")
    print("начало обработки🚀")

    pipeline = DataPipeline()
    
    # 1. Проверяем текущие файлы в папке и запускаем pipeline
    await check_folder(pipeline)

if __name__ == "__main__":
    asyncio.run(main())