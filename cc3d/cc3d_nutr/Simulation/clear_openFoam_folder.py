import shutil
from pathlib import Path
import os

def copy_last_OF_tms(msc, path_OF_project, path_OF_dump):
    # Исходная директория OpenFOAM-кейса
    src_case = Path(path_OF_project)

    # Директория, куда нужно копировать
    dst_case = Path(path_OF_dump + str(msc))
    dst_case.mkdir(parents=True, exist_ok=True)

    # Базовые папки OpenFOAM
    base_dirs = {"system", "constant", "0"}

    # Собираем все директории
    dirs = [d for d in src_case.iterdir() if d.is_dir()]

    # Фильтруем только временные директории (числа)
    time_dirs = []
    for d in dirs:
        try:
            float(d.name)  # просто проверка, что имя — число
            time_dirs.append(d)
        except ValueError:
            pass

    # Находим папку, созданную позже всех
    latest_time_dir = max(time_dirs, key=lambda d: d.stat().st_mtime) if time_dirs else None

    # Готовим список папок для копирования
    dirs_to_copy = [src_case / d for d in base_dirs if (src_case / d).exists()]

    if latest_time_dir is not None:
        dirs_to_copy.append(latest_time_dir)

    # Копируем
    for d in dirs_to_copy:
        dst = dst_case / d.name
        print(f"→ Копирую {d} → {dst}")

        if dst.exists():
            shutil.rmtree(dst)  # если уже есть — удаляем
        shutil.copytree(d, dst)


def clear_OF_project(msc, path_OF_project, path_OF_dump):
    src_case = Path(path_OF_project)

    base_dirs = {"system", "constant", "0"}
    for item in os.listdir(src_case):
        item_path = os.path.join(src_case, item)
        if os.path.isdir(item_path) and item not in base_dirs:
            shutil.rmtree(item_path)

def write_boundary_for_OFD(source, target):
    src = Path(source)   # исходный файл
    dst = Path(target)   # итоговый файл

    # Удаляем старый файл, если он есть
    if dst.exists():
        os.remove(dst)

    # Копируем под новым именем
    shutil.copy2(src, dst)

# write_boundary_for_OFD("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/chto_nado_vstavit",
#                        "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/Diffusion/constant/polyMesh/boundary")
