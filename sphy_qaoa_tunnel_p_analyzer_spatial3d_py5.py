# -*- coding: utf-8 -*-
# ============================================================
# SPHY QAOA Tunnel CSV Visualizer (py5 + File Dialog)
# ============================================================
# Requisitos:
#
# pip install py5 pandas numpy
#
# ============================================================

import py5
import pandas as pd
import numpy as np

from tkinter import Tk
from tkinter.filedialog import askopenfilename

# ============================================================
# FILE PICKER UI
# ============================================================

print("\n🌀 Abrindo seletor de arquivo CSV...\n")

root = Tk()
root.withdraw()

CSV_PATH = askopenfilename(
    title="Selecione o CSV SPHY/QAOA",
    filetypes=[("CSV Files", "*.csv")]
)

if not CSV_PATH:
    print("❌ Nenhum arquivo selecionado.")
    raise SystemExit

print(f"\n✅ Arquivo carregado:\n{CSV_PATH}\n")

# ============================================================
# LOAD CSV
# ============================================================

try:
    df = pd.read_csv(CSV_PATH)

except Exception as e:
    print(f"\n❌ Erro ao carregar CSV:\n{e}")
    raise SystemExit

# ============================================================
# PARSE DATA
# ============================================================

points = []

for _, row in df.iterrows():

    try:

        parts = [float(x) for x in str(row["psi0_noise"]).split(";")]

        if len(parts) != 6:
            continue

        px, py, pz = parts[:3]
        vx, vy, vz = parts[3:]

        energy = float(row.get("energy", 0))
        f_opt = float(row.get("f_opt", 0))
        time_value = float(row.get("time", 0))

        points.append({
            "pos": np.array([px, py, pz]),
            "vel": np.array([vx, vy, vz]),
            "energy": energy,
            "f_opt": f_opt,
            "time": time_value
        })

    except:
        continue

if len(points) == 0:
    print("❌ Nenhum dado válido encontrado.")
    raise SystemExit

print(f"✅ {len(points)} vetores carregados.\n")

# ============================================================
# GLOBALS
# ============================================================

frame_index = 0

SCALE = 140

AUTO_ROTATE = True

SHOW_TRAIL = True

SHOW_ALL_POINTS = False

PAUSED = False

# ============================================================
# PY5 SETUP
# ============================================================

def setup():

    py5.size(1400, 900, py5.P3D)

    py5.smooth(8)

    py5.frame_rate(60)

    py5.window_title("SPHY Quantum Tunnel Visualizer")

# ============================================================
# DRAW LOOP
# ============================================================

def draw():

    global frame_index

    py5.background(0)

    py5.lights()

    # ========================================================
    # CAMERA
    # ========================================================

    py5.translate(py5.width / 2, py5.height / 2, -500)

    if AUTO_ROTATE:
        py5.rotate_y(py5.frame_count * 0.005)
        py5.rotate_x(py5.frame_count * 0.002)

    draw_axis()

    # ========================================================
    # DRAW ALL POINTS MODE
    # ========================================================

    if SHOW_ALL_POINTS:

        for p in points:

            render_particle(p, draw_vector=False)

    # ========================================================
    # ANIMATED PLAYBACK MODE
    # ========================================================

    else:

        idx = frame_index % len(points)

        p = points[idx]

        render_particle(p, draw_vector=True)

        if SHOW_TRAIL:

            draw_trail(idx)

        draw_hud(idx, p)

        if not PAUSED:
            frame_index += 1

# ============================================================
# PARTICLE RENDER
# ============================================================

def render_particle(p, draw_vector=True):

    pos = p["pos"] * SCALE

    vel = p["vel"]

    energy = p["energy"]

    speed = np.linalg.norm(vel)

    x, y, z = pos

    # ========================================================
    # COLOR BY ENERGY
    # ========================================================

    intensity = min(255, int(abs(energy) * 255))

    py5.push_matrix()

    py5.translate(x, y, z)

    py5.no_stroke()

    py5.fill(
        intensity,
        120,
        255 - intensity
    )

    radius = 8 + speed * 10

    py5.sphere(radius)

    py5.pop_matrix()

    # ========================================================
    # VECTOR
    # ========================================================

    if draw_vector:

        py5.stroke_weight(2)

        py5.stroke(0, 255, 255)

        py5.line(
            x, y, z,
            x + vel[0] * 120,
            y + vel[1] * 120,
            z + vel[2] * 120
        )

# ============================================================
# TRAIL
# ============================================================

def draw_trail(idx):

    py5.no_fill()

    py5.stroke(255, 0, 140, 100)

    py5.stroke_weight(2)

    py5.begin_shape()

    start = max(0, idx - 150)

    for i in range(start, idx):

        p = points[i]["pos"] * SCALE

        py5.vertex(p[0], p[1], p[2])

    py5.end_shape()

# ============================================================
# AXIS
# ============================================================

def draw_axis():

    py5.stroke_weight(3)

    # X
    py5.stroke(255, 0, 0)
    py5.line(0, 0, 0, 250, 0, 0)

    # Y
    py5.stroke(0, 255, 0)
    py5.line(0, 0, 0, 0, 250, 0)

    # Z
    py5.stroke(0, 120, 255)
    py5.line(0, 0, 0, 0, 0, 250)

# ============================================================
# HUD
# ============================================================

def draw_hud(idx, p):

    py5.camera()

    py5.fill(255)

    py5.text_size(16)

    py5.text(f"Frame: {idx}", 20, 30)

    py5.text(f"Energy: {p['energy']:.6f}", 20, 55)

    py5.text(f"f_opt: {p['f_opt']:.6f}", 20, 80)

    py5.text(f"time: {p['time']:.6f}", 20, 105)

    py5.text("SPACE = Pause", 20, 150)

    py5.text("A = Mostrar Todos", 20, 175)

    py5.text("T = Trail", 20, 200)

    py5.text("R = Auto Rotate", 20, 225)

# ============================================================
# KEYBOARD
# ============================================================

def key_pressed():

    global PAUSED
    global SHOW_TRAIL
    global SHOW_ALL_POINTS
    global AUTO_ROTATE

    if py5.key == ' ':
        PAUSED = not PAUSED

    elif py5.key == 't':
        SHOW_TRAIL = not SHOW_TRAIL

    elif py5.key == 'a':
        SHOW_ALL_POINTS = not SHOW_ALL_POINTS

    elif py5.key == 'r':
        AUTO_ROTATE = not AUTO_ROTATE

# ============================================================
# RUN
# ============================================================

py5.run_sketch()
