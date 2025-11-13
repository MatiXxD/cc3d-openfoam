import shutil
from pathlib import Path
import os



def copy_and_clean(msc):

    # Исходная директория OpenFOAM-кейса
    src_case = Path("../OpenFoamProject")

    # Папка, куда нужно скопировать
    dst_case = Path("../OF_dumps/ts" + str(msc))

    # Создаём папку назначения (если её нет)
    dst_case.mkdir(parents=True, exist_ok=True)

    # Получаем все подпапки
    dirs = [d.name for d in src_case.iterdir() if d.is_dir()]

    # Базовые папки
    base_dirs = {'system', 'constant', '0'}

    # Ищем числовые директории
    time_dirs = []
    for d in dirs:
        try:
            time_dirs.append(float(d))
        except ValueError:
            pass

    # Выбираем максимальный таймстеп
    max_time = str(max(time_dirs)) if time_dirs else None

    # Список директорий для копирования
    dirs_to_copy = [src_case / d for d in base_dirs if (src_case / d).exists()]
    if max_time:
        dirs_to_copy.append(src_case / max_time)

    # Копируем
    for d in dirs_to_copy:
        dst = dst_case / d.name
        print(f"→ Копирую {d} → {dst}")
        if dst.exists():
            shutil.rmtree(dst)  # удаляем, если уже существует
        shutil.copytree(d, dst)

    # Проходим по всем элементам в целевой папке
    for item in os.listdir(src_case):
        item_path = os.path.join(src_case, item)
        # Если это папка и она не в base_dirs, удаляем
        if os.path.isdir(item_path) and item not in base_dirs:
            shutil.rmtree(item_path)
