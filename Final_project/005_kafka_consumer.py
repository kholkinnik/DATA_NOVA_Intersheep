import os
import glob
import subprocess
from dotenv import load_dotenv

load_dotenv()

# == PRODUCER- KAFKA запуск Python скриптов ==
def run_python_scripts():
    scripts_folder = 'scripts_consumer'
    if not os.path.exists(scripts_folder):
        print(f"❌ Папка {scripts_folder} не найдена")
        return
    
    # Путь к python из виртуального окружения
    venv_python = os.path.join('venv', 'Scripts', 'python.exe')
    if not os.path.exists(venv_python):
        print("❌ Виртуальное окружение не найдено! Создайте: python -m venv venv")
        print("Затем: venv\\Scripts\\activate && pip install -r requirements.txt")
        return
    
    py_files = glob.glob(os.path.join(scripts_folder, '*.py'))
    if not py_files:
        print(f"❌ Python скрипты в папке {scripts_folder} не найдены")
        return
    
    print(f"\n🔍 Найдено {len(py_files)} Python скриптов")
    
    for py_file in sorted(py_files):
        try:
            print(f"\n🐍 Запускаю: {os.path.basename(py_file)}")
            filename = os.path.basename(py_file)
            
            # ✅ КОД С VENV
            result = subprocess.run([
                venv_python,  # запуск из venv (библиотеки установлены)
                filename
            ], 
            cwd=scripts_folder,
            timeout=60
            )
            
            if result.returncode == 0:
                print("✅ загрузка успешна")
                if result.stdout:
                    print(f"   Вывод: {result.stdout[:200]}...")
            else:
                print(f"❌ Ошибка (код {result.returncode})")
                if result.stderr:
                    print(f"   Ошибка: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            print("❌ Таймаут (1 мин)")
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    run_python_scripts()
print("\n🏁 Все топики c данными прочитаны!")
