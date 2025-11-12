from paraview.simple import *
import os
import sys

# Путь к сохранённому state (замени, если нужно)
pvsm = "1.pvsm"

# Путь и шаблон выходных файлов
out_dir = "frames"
out_template = os.path.join(out_dir, "frame.png")  # ParaView создаст frame_0000.png ...

# Разрешение и fps
image_res = [1280, 720]
fps = 10

# --- load state and prepare view ---
if not os.path.exists(pvsm):
    print("ERROR: pvsm not found:", pvsm)
    sys.exit(1)

LoadState(pvsm)
view = GetActiveViewOrCreate('RenderView')

# Обновляем список таймстепов
animationScene = GetAnimationScene()
animationScene.UpdateAnimationUsingDataTimeSteps()

# Вычисляем диапазон кадров
tk = animationScene.TimeKeeper
try:
    nsteps = len(tk.TimestepValues)
except Exception:
    nsteps = 0

if nsteps == 0:
    print("WARNING: no timesteps found; saving a single frame.")
    frame_window = [0, 0]
else:
    frame_window = [0, nsteps-1]

# Создаём папку
os.makedirs(out_dir, exist_ok=True)

# Сохраняем последовательность PNG
SaveAnimation(
    out_template,
    view,
    ImageResolution=image_res,
    FrameRate=fps,
    FrameWindow=frame_window
)

print("Saved frames to:", out_dir)
