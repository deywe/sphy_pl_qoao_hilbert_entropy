# -*- coding: utf-8 -*-
# ============================================================
# File: sphy_csv_py5_renderer.py
# Purpose: Renderizador 3D CSV → PY5
# Author: deywe@QLZ
# ============================================================

# ============================================================
# INSTALL
# ============================================================
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
# FILE PICKER
# ============================================================

root = Tk()
root.withdraw()

CSV_PATH = askopenfilename(
    title="Selecione o CSV SPHY",
    filetypes=[("CSV Files", "*.csv")]
)

if not CSV_PATH:
    print("❌ Nenhum CSV selecionado.")
    raise SystemExit

print(f"\n✅ CSV carregado:\n{CSV_PATH}\n")

# ============================================================
# LOAD CSV
# ============================================================

df = pd.read_csv(CSV_PATH)

# ============================================================
# DETECT Q COLUMNS
# ============================================================

q_cols = [c for c in df.columns if c.startswith("Q")]

if len(q_cols) == 0:
    print("❌ Nenhuma coluna Q encontrada.")
    raise SystemExit

print(f"🧠 Colunas detectadas: {q_cols}")

# ============================================================
# BUILD POINT CLOUD
# ============================================================

points = []

for i, row in df.iterrows():

    try:

        q_values = np.array([
            float(row[q]) for q in q_cols
        ])

        # ====================================================
        # MAPEAMENTO ESPACIAL
        # ====================================================

        x = q_values[0] if len(q_values) > 0 else 0
        y = q_values[1] if len(q_values) > 1 else 0
        z = q_values[2] if len(q_values) > 2 else 0

        # ====================================================
        # VELOCIDADE / DIREÇÃO
        # ====================================================

        vx = np.sin(i * 0.02)
        vy = np.cos(i * 0.02)
        vz = np.sin(i * 0.01)

        # ====================================================
        # ENERGIA
        # ====================================================

        energy = np.mean(np.abs(q_values))

        points.append({
            "pos": np.array([x, y, z]),
            "vel": np.array([vx, vy, vz]),
            "energy": energy,
            "index": i
        })

    except:
        pass

if len(points) == 0:
    print("❌ Nenhum ponto válido.")
    raise SystemExit

print(f"✅ {len(points)} pontos carregados.")

# ============================================================
# GLOBALS
# ============================================================

SCALE = 240

frame_index = 0

AUTO_ROTATE = True

SHOW_TRAIL = True

SHOW_ALL = False

PAUSED = False

# ============================================================
# SETUP
# ============================================================

def setup():

    py5.size(1600, 900, py5.P3D)

    py5.smooth(8)

    py5.frame_rate(60)

    py5.window_title("SPHY CSV Quantum Renderer")

# ============================================================
# DRAW
# ============================================================

def draw():

    global frame_index

    py5.background(0)

    py5.lights()

    # ========================================================
    # CAMERA
    # ========================================================

    py5.translate(py5.width / 2, py5.height / 2, -600)

    if AUTO_ROTATE:

        py5.rotate_y(py5.frame_count * 0.003)

        py5.rotate_x(py5.frame_count * 0.001)

    draw_axis()

    # ========================================================
    # ALL MODE
    # ========================================================

    if SHOW_ALL:

        for p in points:

            render_particle(p, vector=False)

    # ========================================================
    # PLAYBACK MODE
    # ========================================================

    else:

        idx = frame_index % len(points)

        p = points[idx]

        render_particle(p, vector=True)

        if SHOW_TRAIL:

            draw_trail(idx)

        draw_hud(idx, p)

        if not PAUSED:

            frame_index += 1

# ============================================================
# PARTICLE
# ============================================================

def render_particle(p, vector=True):

    pos = p["pos"] * SCALE

    vel = p["vel"]

    energy = p["energy"]

    x, y, z = pos

    intensity = min(255, int(energy * 255))

    radius = 6 + energy * 18

    # ========================================================
    # GLOW SPHERE
    # ========================================================

    py5.push_matrix()

    py5.translate(x, y, z)

    py5.no_stroke()

    py5.fill(
        intensity,
        100,
        255 - intensity
    )

    py5.sphere(radius)

    py5.pop_matrix()

    # ========================================================
    # VECTOR
    # ========================================================

    if vector:

        py5.stroke_weight(2)

        py5.stroke(0, 255, 255)

        py5.line(
            x,
            y,
            z,
            x + vel[0] * 120,
            y + vel[1] * 120,
            z + vel[2] * 120
        )

# ============================================================
# TRAIL
# ============================================================

def draw_trail(idx):

    py5.no_fill()

    py5.stroke(255, 0, 140, 120)

    py5.stroke_weight(2)

    py5.begin_shape()

    start = max(0, idx - 150)

    for i in range(start, idx):

        p = points[i]["pos"] * SCALE

        py5.vertex(
            p[0],
            p[1],
            p[2]
        )

    py5.end_shape()

# ============================================================
# AXIS
# ============================================================

def draw_axis():

    py5.stroke_weight(3)

    # X
    py5.stroke(255, 0, 0)
    py5.line(0, 0, 0, 300, 0, 0)

    # Y
    py5.stroke(0, 255, 0)
    py5.line(0, 0, 0, 0, 300, 0)

    # Z
    py5.stroke(0, 120, 255)
    py5.line(0, 0, 0, 0, 0, 300)

# ============================================================
# HUD
# ============================================================

def draw_hud(idx, p):

    py5.camera()

    py5.fill(255)

    py5.text_size(18)

    py5.text(f"Frame: {idx}", 20, 30)

    py5.text(f"Energy: {p['energy']:.6f}", 20, 60)

    py5.text(f"Particles: {len(points)}", 20, 90)

    py5.text("SPACE = Pause", 20, 150)

    py5.text("A = Show All", 20, 180)

    py5.text("T = Trail", 20, 210)

    py5.text("R = Rotate", 20, 240)

# ============================================================
# KEYBOARD
# ============================================================

def key_pressed():

    global PAUSED
    global SHOW_TRAIL
    global SHOW_ALL
    global AUTO_ROTATE

    if py5.key == ' ':

        PAUSED = not PAUSED

    elif py5.key == 't':

        SHOW_TRAIL = not SHOW_TRAIL

    elif py5.key == 'a':

        SHOW_ALL = not SHOW_ALL

    elif py5.key == 'r':

        AUTO_ROTATE = not AUTO_ROTATE

# ============================================================
# START
# ============================================================

py5.run_sketch()
