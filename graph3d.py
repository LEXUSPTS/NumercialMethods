# graph3d.py
"""Простой 3D-рендерер на базе Tkinter Canvas (без matplotlib).
Поддерживает:
  • Ортографическую проекцию с вращением мышью
  • Цветовую карту по высоте (z)
  • Сетку и оси
  • Экспорт в PNG через Pillow
"""
import math
import colorsys


class Graph3D:
    """Виджет 3D-графика для функции z = f(x, y)."""

    def __init__(self, parent, width=800, height=600, bg="white"):
        import tkinter as tk
        self.canvas = tk.Canvas(parent, width=width, height=height,
                                bg=bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.width = width
        self.height = height
        self.bg = bg

        # Параметры камеры
        self.rot_x = 0.5   # наклон (радианы)
        self.rot_z = 0.7   # поворот вокруг Z
        self.zoom = 1.0
        self.center_x = width / 2
        self.center_y = height / 2

        # Данные
        self.f = None
        self.x_range = (-5, 5)
        self.y_range = (-5, 5)
        self.z_range = (-5, 5)
        self.resolution = 40  # сетка NxN

        # События мыши
        self.drag_start = None
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)

    def set_function(self, f, x_range=(-5, 5), y_range=(-5, 5), resolution=40):
        """Установить функцию и диапазоны."""
        self.f = f
        self.x_range = x_range
        self.y_range = y_range
        self.resolution = resolution
        self._compute_z_range()
        self.render()

    def _compute_z_range(self):
        """Вычислить диапазон Z по значениям функции."""
        if not self.f:
            return
        z_vals = []
        nx, ny = self.resolution, self.resolution
        for i in range(nx):
            for j in range(ny):
                x = self.x_range[0] + i * (self.x_range[1] - self.x_range[0]) / (nx - 1)
                y = self.y_range[0] + j * (self.y_range[1] - self.y_range[0]) / (ny - 1)
                try:
                    z = self.f(x, y)
                    if math.isfinite(z):
                        z_vals.append(z)
                except Exception:
                    pass
        if z_vals:
            self.z_range = (min(z_vals), max(z_vals))
        else:
            self.z_range = (-1, 1)

    def project(self, x, y, z):
        """3D → 2D проекция (ортографическая)."""
        # Нормализация координат в [-1, 1]
        nx = 2 * (x - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) - 1
        ny = 2 * (y - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) - 1
        nz = 2 * (z - self.z_range[0]) / (self.z_range[1] - self.z_range[0]) - 1 if \
             self.z_range[1] != self.z_range[0] else 0

        # Поворот вокруг Z
        cos_z, sin_z = math.cos(self.rot_z), math.sin(self.rot_z)
        x1 = nx * cos_z - ny * sin_z
        y1 = nx * sin_z + ny * cos_z
        z1 = nz

        # Наклон вокруг X
        cos_x, sin_x = math.cos(self.rot_x), math.sin(self.rot_x)
        y2 = y1 * cos_x - z1 * sin_x
        z2 = y1 * sin_x + z1 * cos_x

        # Масштаб и центр
        scale = min(self.width, self.height) * 0.35 * self.zoom
        sx = self.center_x + x1 * scale
        sy = self.center_y - y2 * scale
        return sx, sy, z2

    def _z_to_color(self, z):
        """Цвет по высоте (синий → зелёный → красный)."""
        if self.z_range[1] == self.z_range[0]:
            t = 0.5
        else:
            t = (z - self.z_range[0]) / (self.z_range[1] - self.z_range[0])
        t = max(0, min(1, t))
        # Hue: 0.66 (синий) → 0.33 (зелёный) → 0 (красный)
        hue = 0.66 - t * 0.66
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def render(self):
        """Отрисовать 3D-график."""
        self.canvas.delete("all")
        if not self.f:
            self.canvas.create_text(self.width / 2, self.height / 2,
                                    text="Нет функции для отображения",
                                    font=("Segoe UI", 12), fill="gray")
            return

        nx = ny = self.resolution

        # Собираем все полигоны сетки
        polygons = []
        for i in range(nx - 1):
            for j in range(ny - 1):
                pts_3d = []
                z_avg = 0
                valid = True
                for di, dj in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                    x = self.x_range[0] + (i + di) * (self.x_range[1] - self.x_range[0]) / (nx - 1)
                    y = self.y_range[0] + (j + dj) * (self.y_range[1] - self.y_range[0]) / (ny - 1)
                    try:
                        z = self.f(x, y)
                        if not math.isfinite(z):
                            valid = False
                            break
                    except Exception:
                        valid = False
                        break
                    pts_3d.append((x, y, z))
                    z_avg += z
                if not valid:
                    continue
                z_avg /= 4

                # Проецируем
                pts_2d = [self.project(x, y, z) for x, y, z in pts_3d]
                depth = sum(p[2] for p in pts_2d) / 4
                color = self._z_to_color(z_avg)
                polygons.append((depth, pts_2d, color))

        # Сортируем по глубине (художник)
        polygons.sort(key=lambda p: p[0])

        # Рисуем
        for depth, pts_2d, color in polygons:
            flat = [coord for p in pts_2d for coord in (p[0], p[1])]
            self.canvas.create_polygon(flat, fill=color, outline="#333333", width=0.5)

        # Рисуем оси
        self._draw_axes()

        # Подпись
        self.canvas.create_text(10, 10, anchor=tk.NW,
                                text=f"z = f(x, y)  |  X:{self.x_range}  Y:{self.y_range}",
                                font=("Segoe UI", 9), fill="black")
        self.canvas.create_text(10, 28, anchor=tk.NW,
                                text="ЛКМ — вращение  |  Колесо — зум",
                                font=("Segoe UI", 8), fill="gray")

    def _draw_axes(self):
        """Нарисовать оси X, Y, Z."""
        x0, y0, z0 = self.x_range[0], self.y_range[0], self.z_range[0]
        x1, y1, z1 = self.x_range[1], self.y_range[1], self.z_range[1]

        axes = [
            ((x0, y0, z0), (x1, y0, z0), "red", "X"),
            ((x0, y0, z0), (x0, y1, z0), "green", "Y"),
            ((x0, y0, z0), (x0, y0, z1), "blue", "Z"),
        ]
        for p1, p2, color, label in axes:
            sx1, sy1, _ = self.project(*p1)
            sx2, sy2, _ = self.project(*p2)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=2)
            self.canvas.create_text(sx2 + 5, sy2 - 5, text=label, fill=color,
                                    font=("Segoe UI", 10, "bold"))

    def on_drag(self, event):
        if self.drag_start is None:
            self.drag_start = (event.x, event.y, self.rot_x, self.rot_z)
            return
        _, _, start_rx, start_rz = self.drag_start
        dx = event.x - self.drag_start[0]
        dy = event.y - self.drag_start[1]
        self.rot_z = start_rz + dx * 0.01
        self.rot_x = max(-1.5, min(1.5, start_rx + dy * 0.01))
        self.render()

    def on_drag_end(self, event):
        self.drag_start = None

    def on_zoom(self, event):
        factor = 1.1 if (event.num == 4 or getattr(event, 'delta', 0) > 0) else 0.9
        self.zoom *= factor
        self.zoom = max(0.2, min(5.0, self.zoom))
        self.render()

    def save_png(self, filepath, width=1920, height=1080):
        """Сохранить в PNG через Pillow."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            return False

        img = Image.new("RGB", (width, height), self.bg)
        draw = ImageDraw.Draw(img)

        # Сохраняем текущие размеры и временно меняем
        old_w, old_h = self.width, self.height
        self.width, self.height = width, height
        self.center_x = width / 2
        self.center_y = height / 2

        if not self.f:
            return False

        nx = ny = self.resolution
        polygons = []
        for i in range(nx - 1):
            for j in range(ny - 1):
                pts_3d = []
                z_avg = 0
                valid = True
                for di, dj in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                    x = self.x_range[0] + (i + di) * (self.x_range[1] - self.x_range[0]) / (nx - 1)
                    y = self.y_range[0] + (j + dj) * (self.y_range[1] - self.y_range[0]) / (ny - 1)
                    try:
                        z = self.f(x, y)
                        if not math.isfinite(z):
                            valid = False
                            break
                    except Exception:
                        valid = False
                        break
                    pts_3d.append((x, y, z))
                    z_avg += z
                if not valid:
                    continue
                z_avg /= 4
                pts_2d = [self.project(x, y, z)[:2] for x, y, z in pts_3d]
                polygons.append((sum(p[2] for p in [(self.project(x, y, z)) for x, y, z in pts_3d]) / 4,
                                 pts_2d, self._z_to_color(z_avg)))

        polygons.sort(key=lambda p: p[0])
        for _, pts_2d, color in polygons:
            draw.polygon([tuple(p) for p in pts_2d], fill=color, outline="#333333")

        # Восстанавливаем размеры
        self.width, self.height = old_w, old_h
        self.center_x = old_w / 2
        self.center_y = old_h / 2

        img.save(filepath, "PNG")
        return True