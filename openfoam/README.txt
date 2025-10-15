0) pimpleFoamScalar - решатель
sphereInBox - проект

сейчас моделька решена до 0.84с(как пример, какие файлы выдает решение) 
С - концентрация
U - скорость
p - давление
phi - поток через грани ячеек


1)Чтобы запустить этот проект надо установить исходники и новую версию OF

Подготовка — установить зависимости (Ubuntu/Debian)
Открой терминал и выполни:

# обновить пакеты
sudo apt update

# минимум для сборки (git, компиляторы, cmake, flex)
sudo apt install -y build-essential cmake git ca-certificates flex

# (рекомендуется) добавить репозиторий OpenFOAM и установить "meta-пакеты" зависимостей
sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc"
sudo add-apt-repository "http://dl.openfoam.org/ubuntu"
sudo apt update
sudo apt install -y openfoam-deps paraview-dev

Создать папку установки и клонировать исходники
Реши, куда ставить. Рекомендуется ~/OpenFOAM (не требуется root):

# делаем директорию и переходим в неё
mkdir -p $HOME/OpenFOAM
cd $HOME/OpenFOAM

# Клонируем выбранную версию. Пример: OpenFOAM-10 (замени на нужную версию, например OpenFOAM-dev или OpenFOAM-13)
git clone https://github.com/OpenFOAM/OpenFOAM-10.git
git clone https://github.com/OpenFOAM/ThirdParty-10.git

Настроить окружение (чтобы переменные типа $FOAM_SRC появились)
После
 клонирования нужно подключить окружение OpenFOAM (каждый новый терминал
 должен это делать — обычно добавляют строку в ~/.bashrc):

# для текущего терминала (замени путь, если клонировал в другое место)
source $HOME/OpenFOAM/OpenFOAM-10/etc/bashrc

# чтобы всегда было в новых терминалах, добавь:
echo 'source $HOME/OpenFOAM/OpenFOAM-10/etc/bashrc' >> ~/.bashrc
# и загрузить изменения сейчас:
source ~/.bashrc


Проверь, что переменные установились:

echo "WM_PROJECT_DIR = $WM_PROJECT_DIR"
echo "FOAM_SRC = $FOAM_SRC"


Ожидаемый
 пример: WM_PROJECT_DIR=/home/youruser/OpenFOAM/OpenFOAM-10, 
FOAM_SRC=/home/youruser/OpenFOAM/OpenFOAM-10/src. Если пусто — файл 
etc/bashrc не был sourced. (OpenFOAM)

Cобрать ThirdParty или установить нужные библиотеки

cd $HOME/OpenFOAM/ThirdParty-10
./Allwmake    # или ./Allwmake -j 8 -q для параллельной быстрой сборки

Сборка ThirdParty может занять много времени (особенно ParaView). Док: скрипты ThirdParty и порядок сборки описаны в репозитории. (GitHub)

Собрать OpenFOAM (Allwmake)
После того, как зависимости готовы:

cd $HOME/OpenFOAM/OpenFOAM-10
./Allwmake        # последовательная сборка — легче отлавливать ошибки
# или быстрый режим (параллельно), например на 4 ядрах:
./Allwmake -q -j 4

Если нужно обновить после git pull — используйте ./Allwmake -update (или делайте wcleanPlatform и потом ./Allwmake). (OpenFOAM)

Где именно лежит fvCFD.H — и как убедиться
Официальное место в исходниках:

$FOAM_SRC/finiteVolume/cfdTools/general/include/fvCFD.H
# а также симлинк в:
$FOAM_SRC/finiteVolume/lnInclude/fvCFD.H  (обычно символическая ссылка на реальный файл)

Проверим наличие и откроем файл:

# Найти файл (в $WM_PROJECT_DIR)
find $WM_PROJECT_DIR -iname "fvCFD.H" -print

# Список и права
ls -l $FOAM_SRC/finiteVolume/cfdTools/general/include/fvCFD.H
ls -l $FOAM_SRC/finiteVolume/lnInclude/fvCFD.H

# Просмотреть начало файла
sed -n '1,60p' $FOAM_SRC/finiteVolume/cfdTools/general/include/fvCFD.H
# или просто
less $FOAM_SRC/finiteVolume/cfdTools/general/include/fvCFD.H

Если файл найден — отлично. 

Дальше перемещаем папку pimpleFoamScalar в /home/имя_пользователя/OpenFOAM/OpenFOAM-10/applications/solvers/incompressible
открыть в терминале ее и в bash команда 
wmake

2)По поводу запуска проекта
терминал открыть в проекте
blockMesh – создает сетку вокруг
snappyHexMesh –overwrite –интеграции .stl в сетку(уточни команду) (настроена заебато) (.stl можно менять
в папке constant/triSurface
pimpleFoamScalar – запуск решателя 
paraFoam -builtin – запуск визуализации 
foamCleanTutorials - очистка всего
3)По поводу папок
Изначально 
/0
/Constant
/System
Вот эта структура стандартная для openfoam