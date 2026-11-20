# contour_plot.py
"""Контурный график (линии уровня) для функции z = f(x, y)."""
import math
import colorsys
import tkinter as tk


class ContourPlot:
    """Виджет контурного графика."""

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
        self.n_levels = 15
        self.resolution = 80

        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.zoom = 1.0

    def set_function(self, f, x_range=(-5, 5), y_range=(-5, 5),
                     n_levels=15, resolution=80):
        self.f = f
        self.x_range = x_range
        self.y_range = y_range
        self.n_levels = n_levels
        self.resolution = resolution
        self.render()

    def _color_for_level(self, t):
        """Цвет от синего (мин) до красного (макс)."""
        hue = 0.66 - t * 0.66
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def render(self):
        self.canvas.delete("all")
        if not self.f:
            self.canvas.create_text(self.width / 2, self.height / 2,
                                    text="Нет функции", font=("Segoe UI", 12))
            return

        nx = ny = self.resolution
        x_min, x_max = self.x_range
        y_min, y_max = self.y_range

        grid = [[None] * ny for _ in range(nx)]
        z_vals = []
        for i in range(nx):
            for j in range(ny):
                x = x_min + i * (x_max - x_min) / (nx - 1)
                y = y_min + j * (y_max - y_min) / (ny - 1)
                try:
                    z = self.f(x, y)
                    if math.isfinite(z):
                        grid[i][j] = z
                        z_vals.append(z)
                except Exception:
                    pass

        if not z_vals:
            self.canvas.create_text(self.width / 2, self.height / 2,
                                    text="Нет данных", font=("Segoe UI", 12))
            return

        z_min, z_max = min(z_vals), max(z_vals)
        if z_max - z_min < 1e-10:
            z_max = z_min + 1

        cell_w = self.width / nx
        cell_h = self.height / ny

        # Тепловая карта
        for i in range(nx):
            for j in range(ny):
                if grid[i][j] is not None:
                    t = (grid[i][j] - z_min) / (z_max - z_min)
                    color = self._color_for_level(t)
                    x1 = i * cell_w
                    y1 = self.height - (j + 1) * cell_h
                    self.canvas.create_rectangle(x1, y1, x1 + cell_w, y1 + cell_h,
                                                 fill=color, outline="")

        # Линии уровня (marching squares)
        levels = [z_min + k * (z_max - z_min) / (self.n_levels - 1)
                  for k in range(self.n_levels)]

        for level_idx, level in enumerate(levels):
            for i in range(nx - 1):
                for j in range(ny - 1):
                    corners_vals = [grid[i][j], grid[i+1][j],
                                    grid[i+1][j+1], grid[i][j+1]]
                    if any(c is None for c in corners_vals):
                        continue
                    corners = corners_vals
                    bits = sum(1 << k for k, c in enumerate(corners) if c >= level)
                    if bits == 0 or bits == 15:
                        continue

                    px = [i * cell_w, (i + 1) * cell_w, (i + 1) * cell_w, i * cell_w]
                    py = [self.height - j * cell_h, self.height - j * cell_h,
                          self.height - (j + 1) * cell_h, self.height - (j + 1) * cell_h]

                    def interp(k1, k2):
                        v1, v2 = corners[k1], corners[k2]
                        if abs(v2 - v1) < 1e-15:
                            t = 0.5
                        else:
                            t = (level - v1) / (v2 - v1)
                        return (px[k1] + t * (px[k2] - px[k1]),
                                py[k1] + t * (py[k2] - py[k1]))

                    segments = []
                    if bits in (1, 14):
                        segments.append((interp(0, 3), interp(0, 1)))
                    elif bits in (2, 13):
                        segments.append((interp(0, 1), interp(1, 2)))
                    elif bits in (3, 12):
                        segments.append((interp(0, 3), interp(1, 2)))
                    elif bits in (4, 11):
                        segments.append((interp(1, 2), interp(2, 3)))
                    elif bits in (5, 10):
                        segments.append((interp(0, 3), interp(2, 3)))
                        segments.append((interp(0, 1), interp(1, 2)))
                    elif bits in (6, 9):
                        segments.append((interp(0, 1), interp(2, 3)))
                    elif bits in (7, 8):
                        segments.append((interp(0, 3), interp(2, 3)))

                    for p1, p2 in segments:
                        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                                fill="white", width=1.5)

        # Легенда
        for level_idx in range(0, self.n_levels, 3):
            t = level_idx / (self.n_levels - 1)
            color = self._color_for_level(t)
            level_val = levels[level_idx]
            x_px = self.width - 80
            y_px = 20 + (level_idx // 3) * 20
            self.canvas.create_rectangle(x_px - 5, y_px - 5, x_px + 10, y_px + 5,
                                         fill=color, outline="black")
            self.canvas.create_text(x_px + 25, y_px, anchor=tk.W,
                                    text=f"{level_val:.2f}",
                                    font=("Segoe UI", 8), fill="black")

        self.canvas.create_text(10, 10, anchor=tk.NW,
                                text=f"Контурный график: z = f(x, y)  |  {self.n_levels} уровней",
                                font=("Segoe UI", 9), fill="black")

    def on_zoom(self, event):
        factor = 1.1 if (event.num == 4 or getattr(event, 'delta', 0) > 0) else 0.9
        self.zoom *= factor
        xr = (self.x_range[1] - self.x_range[0]) / factor
        yr = (self.y_range[1] - self.y_range[0]) / factor
        cx = (self.x_range[0] + self.x_range[1]) / 2
        cy = (self.y_range[0] + self.y_range[1]) / 2
        self.x_range = (cx - xr / 2, cx + xr / 2)
        self.y_range = (cy - yr / 2, cy + yr / 2)
        self.render()

    def save_png(self, filepath):
        try:
            ps_file = filepath + ".ps"
            self.canvas.postscript(file=ps_file, colormode='color')
            import os
            os.remove(ps_file)
            return True
        except Exception:
            return False