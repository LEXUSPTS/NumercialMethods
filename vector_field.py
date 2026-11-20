# vector_field.py
"""Векторное поле — визуализация градиента функции f(x, y)."""
import math
import tkinter as tk


class VectorField:
    """Виджет векторного поля."""

    def __init__(self, parent, width=800, height=600, bg="white"):
        self.canvas = tk.Canvas(parent, width=width, height=height,
                                bg=bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.width = width
        self.height = height
        self.bg = bg

        self.f = None
        self.x_range = (-5, 5)
        self.y_range = (-5, 5)
        self.grid_size = 20
        self.scale = 1.0

    def set_function(self, f, x_range=(-5, 5), y_range=(-5, 5),
                     grid_size=20, scale=1.0):
        self.f = f
        self.x_range = x_range
        self.y_range = y_range
        self.grid_size = grid_size
        self.scale = scale
        self.render()

    def _numerical_gradient(self, x, y, h=1e-4):
        try:
            df_dx = (self.f(x + h, y) - self.f(x - h, y)) / (2 * h)
            df_dy = (self.f(x, y + h) - self.f(x, y - h)) / (2 * h)
            return df_dx, df_dy
        except Exception:
            return None, None

    def render(self):
        self.canvas.delete("all")
        if not self.f:
            self.canvas.create_text(self.width / 2, self.height / 2,
                                    text="Нет функции", font=("Segoe UI", 12))
            return

        x_min, x_max = self.x_range
        y_min, y_max = self.y_range
        n = self.grid_size

        vectors = []
        max_mag = 0
        for i in range(n):
            for j in range(n):
                x = x_min + (i + 0.5) * (x_max - x_min) / n
                y = y_min + (j + 0.5) * (y_max - y_min) / n
                df_dx, df_dy = self._numerical_gradient(x, y)
                if df_dx is not None and math.isfinite(df_dx) and math.isfinite(df_dy):
                    mag = math.sqrt(df_dx ** 2 + df_dy ** 2)
                    vectors.append((x, y, df_dx, df_dy, mag))
                    if mag > max_mag:
                        max_mag = mag

        if max_mag < 1e-15:
            max_mag = 1.0

        cell_w = self.width / n
        cell_h = self.height / n
        arrow_len = min(cell_w, cell_h) * 0.4 * self.scale

        for x, y, df_dx, df_dy, mag in vectors:
            nx = df_dx / max_mag
            ny = df_dy / max_mag

            px = (x - x_min) / (x_max - x_min) * self.width
            py = self.height - (y - y_min) / (y_max - y_min) * self.height

            ex = px + nx * arrow_len
            ey = py - ny * arrow_len

            t = min(1.0, mag / max_mag)
            r = int(220 * t + 30 * (1 - t))
            color = f"#{r:02x}2626"

            self.canvas.create_line(px, py, ex, ey, fill=color, width=1.5,
                                    arrow=tk.LAST, arrowshape=(6, 8, 3))
            self.canvas.create_oval(px - 1.5, py - 1.5, px + 1.5, py + 1.5,
                                    fill=color, outline="")

        self.canvas.create_text(10, 10, anchor=tk.NW,
                                text=f"Векторное поле: ∇f(x, y)  |  Сетка {n}×{n}",
                                font=("Segoe UI", 9), fill="black")

        legend_y = self.height - 30
        for i in range(5):
            t = i / 4
            x_px = self.width - 150 + i * 30
            r = int(220 * t + 30 * (1 - t))
            color = f"#{r:02x}2626"
            self.canvas.create_rectangle(x_px, legend_y, x_px + 30, legend_y + 15,
                                         fill=color, outline="black")
            self.canvas.create_text(x_px + 15, legend_y + 25,
                                    text=f"{t * max_mag:.2f}",
                                    font=("Segoe UI", 7), fill="black")
        self.canvas.create_text(self.width - 150, legend_y - 10, anchor=tk.W,
                                text="|∇f|:", font=("Segoe UI", 8))