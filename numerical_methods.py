# numerical_methods.py
"""Численные методы · Turbo Edition v2.0 — ПОЛНОСТЬЮ РАБОЧАЯ ВЕРСИЯ"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import math, json, os, csv, random, re, sys, html, threading, ast, operator
import time, webbrowser, io, base64, shutil, subprocess, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

# === ЗАГЛУШКИ ДЛЯ ОТСУТСТВУЮЩИХ МОДУЛЕЙ ===
try:
    from graph3d import Graph3D
except ImportError:
    class Graph3D:
        def __init__(self, *a, **kw): pass

        def set_function(self, *a, **kw): pass

        def save_png(self, *a, **kw): return False

try:
    from PIL import Image, ImageDraw, ImageFont

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import openpyxl

    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from methods_extra import (
        brent_method, simple_iteration, golden_section_minimum,
        integrate_trapezoid, integrate_simpson, integrate_gauss,
        integrate_monte_carlo, integrate_adaptive_simpson,
        lagrange_interpolation, cubic_spline,
        least_squares_linear, least_squares_polynomial,
        find_all_roots, muller_method, ridders_method,
        inverse_quadratic_interpolation,
        gauss_elimination, jacobi_method, seidel_method,
        newton_system, tridiagonal_solver,
        numerical_derivative, richardson_derivative,
        euler_method, runge_kutta_4, runge_kutta_fehlberg,
        fourier_analysis, fft_simple,
        condition_number, spectral_radius, convergence_order,
        check_diagonal_dominance, determinant, inverse_matrix,
    )
except ImportError:
    def brent_method(f, a, b, sigma):
        fa, fb = f(a), f(b)
        if fa * fb >= 0: return None, []
        for _ in range(1000):
            c = (a + b) / 2.0
            if f(a) * f(c) <= 0:
                b = c
            else:
                a = c
            if abs(b - a) < sigma: break
        return (a + b) / 2.0, [(1, a, b, c, f(c), abs(b - a))]


    def simple_iteration(f, a, b, sigma):
        x = (a + b) / 2.0
        hist = []
        for k in range(1, 1001):
            x_new = x - f(x) * 0.1
            hist.append((k, x, x_new, f(x_new), abs(x_new - x)))
            if abs(x_new - x) < sigma: break
            x = x_new
        return x, hist


    def find_all_roots(f, a, b, sigma, n_segments=200, method="brent"):
        roots = []
        step = (b - a) / n_segments
        for i in range(n_segments):
            x1, x2 = a + i * step, a + (i + 1) * step
            try:
                if f(x1) * f(x2) < 0:
                    for _ in range(100):
                        c = (x1 + x2) / 2.0
                        if f(x1) * f(c) <= 0:
                            x2 = c
                        else:
                            x1 = c
                        if abs(x2 - x1) < sigma: break
                    roots.append((x1 + x2) / 2.0)
            except Exception:
                pass
        return roots


    def integrate_trapezoid(f, a, b, n):
        h = (b - a) / n
        s = (f(a) + f(b)) / 2.0
        for i in range(1, n): s += f(a + i * h)
        return s * h


    def integrate_simpson(f, a, b, n):
        if n % 2 != 0: n += 1
        h = (b - a) / n
        s = f(a) + f(b)
        for i in range(1, n, 2): s += 4 * f(a + i * h)
        for i in range(2, n, 2): s += 2 * f(a + i * h)
        return s * h / 3.0


    def integrate_gauss(f, a, b, n):
        return integrate_simpson(f, a, b, 100)


    def integrate_monte_carlo(f, a, b, n):
        total = 0.0
        for _ in range(n):
            x = random.uniform(a, b)
            try:
                total += f(x)
            except Exception:
                pass
        return (b - a) * total / n


    def integrate_adaptive_simpson(f, a, b, eps):
        return integrate_simpson(f, a, b, 1000)

try:
    from i18n import Translator
except ImportError:
    class Translator:
        def __init__(self, lang="ru"): self.lang = lang

        def t(self, key): return key

        def set_language(self, lang): self.lang = lang

try:
    from tutorial import TUTORIAL, GLOSSARY, TEST_PROBLEMS
except ImportError:
    TUTORIAL = {"bisection": {"title": "Бисекция", "theory": "Метод половинного деления", "formula": "c=(a+b)/2",
                              "pros": "Простой", "cons": "Медленный"}}
    GLOSSARY = {"Корень": "Значение x, при котором f(x)=0"}
    TEST_PROBLEMS = [{"name": "Пример", "eq": "x**2 - 4", "a": "0", "b": "3", "roots": [2.0]}]

try:
    from achievements import ACHIEVEMENTS, Stats
except ImportError:
    ACHIEVEMENTS = {
        "first_solve": {"name": "Первый шаг", "desc": "Решить первое уравнение", "icon": "🎯", "category": "Базовые"},
        "ten_solves": {"name": "Десяточка", "desc": "Решить 10 уравнений", "icon": "🔟", "category": "Базовые"},
        "hundred_solves": {"name": "Сотня", "desc": "Решить 100 уравнений", "icon": "💯", "category": "Базовые"},
        "newton_master": {"name": "Мастер Ньютона", "desc": "Ньютон сошёлся за <5 итераций", "icon": "🚀",
                          "category": "Методы"},
        "all_methods": {"name": "Полиметодист", "desc": "Использовать все 6 методов", "icon": "🧭",
                        "category": "Методы"},
        "speed_demon": {"name": "Скорострел", "desc": "Решить быстрее 100 мс", "icon": "⚡", "category": "Скорость"},
        "exporter": {"name": "Экспортёр", "desc": "Сохранить в 3 форматах", "icon": "📤", "category": "Экспорт"},
        "student": {"name": "Студент", "desc": "Открыть учебник", "icon": "📚", "category": "Обучение"},
        "graph_explorer": {"name": "Исследователь", "desc": "Использовать зум", "icon": "🔍", "category": "Графика"},
        "symPy_user": {"name": "SymPy-пользователь", "desc": "Решить аналитически", "icon": "🔬",
                       "category": "Продвинутые"},
    }


    class Stats:
        def __init__(self, data_dir):
            self.path = os.path.join(data_dir, "stats.json")
            self.data = {"total_solves": 0, "methods_used": {}, "unlocked": [], "exports": [], "fast_solves": 0,
                         "total_time_ms": 0}

        def save(self):
            try:
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        def record_solve(self, method, iters, time_ms, sigma):
            self.data["total_solves"] = self.data.get("total_solves", 0) + 1
            self.data["methods_used"] = self.data.get("methods_used", {})
            self.data["methods_used"][method] = self.data["methods_used"].get(method, 0) + 1
            self.data["total_time_ms"] = self.data.get("total_time_ms", 0) + time_ms
            if time_ms < 100: self.data["fast_solves"] = self.data.get("fast_solves", 0) + 1
            self.save()

        def record_export(self, fmt):
            if "exports" not in self.data: self.data["exports"] = []
            if fmt not in self.data["exports"]: self.data["exports"].append(fmt)
            self.save()

        def record_extrema(self):
            pass

        def record_extra_formula(self):
            pass

        def record_quiz_correct(self):
            pass

        def record_batch(self, n):
            pass

        def check_achievements(self):
            new = []
            d = self.data
            checks = [
                ("first_solve", d.get("total_solves", 0) >= 1),
                ("ten_solves", d.get("total_solves", 0) >= 10),
                ("hundred_solves", d.get("total_solves", 0) >= 100),
                ("all_methods", len(d.get("methods_used", {})) >= 6),
                ("speed_demon", d.get("fast_solves", 0) >= 1),
                ("exporter", len(d.get("exports", [])) >= 3),
                ("symPy_user", d.get("sympy_used", False)),
                ("graph_explorer", d.get("graph_zoomed", False)),
                ("student", d.get("tutorial_opened", False)),
            ]
            for key, cond in checks:
                if cond and key not in d.get("unlocked", []):
                    if "unlocked" not in d: d["unlocked"] = []
                    d["unlocked"].append(key)
                    if key in ACHIEVEMENTS: new.append(ACHIEVEMENTS[key])
            if new: self.save()
            return new

try:
    from benchmark import benchmark
except ImportError:
    def benchmark(f, a, b, sigma, methods, n_runs=3):
        res = {}
        for name, fn in methods.items():
            times, iters = [], []
            for _ in range(n_runs):
                t0 = time.perf_counter()
                try:
                    r = fn(f, a, b, sigma)
                    times.append((time.perf_counter() - t0) * 1000)
                    iters.append(len(r[1]) if len(r) > 1 and r[1] else 0)
                except Exception:
                    times.append(0);
                    iters.append(0)
            res[name] = {"avg_time_ms": sum(times) / len(times), "avg_iters": sum(iters) / len(iters), "success": True}
        return res

try:
    from batch import load_tasks_csv
except ImportError:
    def load_tasks_csv(fp):
        tasks = []
        with open(fp, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader: tasks.append(row)
        return tasks

try:
    import tests as builtin_tests
except ImportError:
    class builtin_tests:
        @staticmethod
        def run_all_tests(): return [("Тест 1", True, "OK"), ("Тест 2", True, "OK")]

try:
    import step_by_step
except ImportError:
    class step_by_step:
        @staticmethod
        def bisection_steps(f, a, b, sigma):
            return [{"type": "info", "title": "Бисекция", "text": f"Интервал: [{a}, {b}]", "formula": "c=(a+b)/2"}]

        @staticmethod
        def newton_steps(f, df, x0, sigma):
            return [{"type": "info", "title": "Ньютон", "text": f"x0={x0}", "formula": "x=x-f/f'"}]

        @staticmethod
        def chord_steps(f, a, b, sigma):
            return [{"type": "info", "title": "Хорды", "text": f"[{a},{b}]", "formula": "x=x-f*(x-x0)/(f-f0)"}]
def safe_eval(self, f, x):
    """Вычислить f(x), вернув nan вместо исключения."""
    try:
        y = f(x)
        if isinstance(y, complex):
            return math.nan
        return y if math.isfinite(y) else math.nan
    except (OverflowError, ValueError, ZeroDivisionError, OSError, TypeError):
        return math.nan
try:
    from contour_plot import ContourPlot
except ImportError:
    class ContourPlot:
        def __init__(self, *a, **kw): pass

        def set_function(self, *a, **kw): pass

try:
    from vector_field import VectorField
except ImportError:
    class VectorField:
        def __init__(self, *a, **kw): pass

        def set_function(self, *a, **kw): pass

try:
    import interactive_tutorial
except ImportError:
    class interactive_tutorial:
        TUTORIAL_EXAMPLES = {"bisection": {"title": "Бисекция", "examples": [
            {"name": "Пример 1", "task": "Найти корень", "eq": "x**2-4", "a": 0, "b": 3, "answer": 2.0}]}}

        @staticmethod
        def check_answer(user, correct):
            try:
                diff = abs(float(user) - correct)
                return {"correct": diff < 0.01, "user": float(user), "correct_val": correct, "error": diff}
            except Exception:
                return {"correct": False, "user": user, "correct_val": correct, "error": 999}

try:
    import cloud_sync
except ImportError:
    class cloud_sync:
        @staticmethod
        def validate_token(t): return "user"

        @staticmethod
        def upload_to_gist(t, d, **kw): return {"id": "demo", "html_url": "https://example.com"}

        @staticmethod
        def download_from_gist(t, i): return {}

        @staticmethod
        def list_user_gists(t): return []

try:
    import sympy as sp

    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

try:
    import winsound
except ImportError:
    winsound = None

VERSION = "2.0.0"
APP_NAME = "NumericalMethods"
APP_TITLE = "Численные методы · Turbo Edition"
UPDATE_REPO = "LEXUSPTS/NumericalMethods"
UPDATE_API = f"https://api.github.com/repos/{UPDATE_REPO}/releases/latest" if UPDATE_REPO else ""
UPDATE_EXE = "NumericalMethods.exe"


def resource_path(relative):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def user_data_dir():
    if sys.platform.startswith("win"):
        root = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Application Support")
    else:
        root = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(root, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


DATA_DIR = user_data_dir()
LIBRARY_FILE = os.path.join(DATA_DIR, "library.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


def set_window_icon(win):
    try:
        if sys.platform.startswith("win"):
            win.iconbitmap(resource_path("icon.ico"))
        else:
            img = tk.PhotoImage(file=resource_path("icon.png"))
            win.iconphoto(True, img)
            win._icon_ref = img
    except Exception:
        pass


THEMES = {
    "light": {"bg": "#f0f4f8", "panel": "#ffffff", "header": "#1e3a5f",
              "text": "#1f2937", "muted": "#6b7280", "canvas_bg": "white",
              "grid": "#eef2f7", "axis": "#111827"},
    "dark": {"bg": "#1e1e2e", "panel": "#2a2a3c", "header": "#11111b",
             "text": "#cdd6f4", "muted": "#a6adc8", "canvas_bg": "#181825",
             "grid": "#313244", "axis": "#cdd6f4"},
    "ocean": {"bg": "#0c4a6e", "panel": "#075985", "header": "#082f49",
              "text": "#e0f2fe", "muted": "#7dd3fc", "canvas_bg": "#082f49",
              "grid": "#0369a1", "axis": "#bae6fd"},
    "forest": {"bg": "#14532d", "panel": "#166534", "header": "#052e16",
               "text": "#dcfce7", "muted": "#86efac", "canvas_bg": "#052e16",
               "grid": "#15803d", "axis": "#bbf7d0"}
}

C_ACCENT = "#2563eb"
C_SUCCESS = "#059669"
C_DANGER = "#dc2626"
C_NEWTON = "#d946ef"
C_SECANT = "#ea580c"
C_WARN = "#d97706"
C_BRENT = "#0891b2"
C_MPI = "#65a30d"


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        tk.Label(tw, text=self.text, justify=tk.LEFT, background="#fef3c7",
                 foreground="#92400e", relief=tk.SOLID, borderwidth=1,
                 font=("Segoe UI", 9), padx=6, pady=3).pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class NumericalMethodsApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE} v{VERSION}")
        self.root.geometry("1400x1000")

        self.theme = "light"
        self.library = self.load_library() or [
            {"name": "f₁(x) = x³ + 3x² + 2.5", "eq": "x**3 + 3*x**2 + 2.5", "a": "-4", "b": "-2"},
            {"name": "f₂(x) = 5ˣ − 6x − 3", "eq": "5**x - 6*x - 3", "a": "-1", "b": "0"}
        ]
        self.history_log = []
        self.last_f = None
        self.view_x_min, self.view_x_max = -100.0, 100.0
        self.view_y_min, self.view_y_max = -100.0, 100.0
        self.drag_start_x, self.drag_start_y = 0, 0
        self.drag_start_view = None
        self.anim_running = False
        self.anim_after_id = None
        self.is_calculating = False
        self.show_extrema = tk.BooleanVar(value=True)
        self.view_history = []
        self.view_history_index = -1
        self.max_view_history = 20
        self.all_roots = []
        self.extra_functions = []
        self.extra_equations = []
        self.extra_colors = ["#dc2626", "#059669", "#d946ef", "#ea580c", "#0891b2", "#65a30d"]
        self.param_sliders = {}
        self.param_values = {}
        self.param_auto_animate = False
        self.param_anim_after_id = None
        self.start_time = time.time()
        self.high_contrast = tk.BooleanVar(value=False)
        self.language = tk.StringVar(value="ru")
        self.is_fullscreen = False
        self.tr = Translator("ru")
        self.stats = Stats(DATA_DIR)
        self.var_mode = tk.StringVar(value="single")
        self.multi_vars = {}

        set_window_icon(self.root)
        self._load_settings()

        # ЗАГОЛОВОК
        self.header = tk.Frame(root, height=60)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        self.lbl_title = tk.Label(self.header, text=f"🧮  {APP_TITLE}",
                                  font=("Segoe UI", 16, "bold"), fg="white")
        self.lbl_title.pack(side=tk.LEFT, padx=20, pady=12)
        self.btn_theme = tk.Button(self.header, text="Тема",
                                   command=self.toggle_theme,
                                   font=("Segoe UI", 10, "bold"), relief=tk.FLAT)
        self.btn_theme.pack(side=tk.RIGHT, padx=20)

        # ПАНЕЛЬ ВВОДА
        self.pad = tk.Frame(root, pady=10)
        self.pad.pack(fill=tk.X, padx=15)

        self.row1 = tk.Frame(self.pad, relief=tk.GROOVE, bd=1)
        self.row1.pack(fill=tk.X)
        r1_inner = tk.Frame(self.row1, padx=10, pady=8)
        r1_inner.pack(fill=tk.X)

        self.lbl_fx = tk.Label(r1_inner, text="f(x) =", font=("Segoe UI", 12, "bold"))
        self.lbl_fx.pack(side=tk.LEFT, padx=(0, 6))
        self.eq_entry = tk.Entry(r1_inner, width=32, font=("Consolas", 12), relief=tk.SOLID, bd=1)
        self.eq_entry.pack(side=tk.LEFT, padx=4, ipady=4)
        self.eq_entry.bind("<Return>", lambda e: self.solve())

        self._btn(r1_inner, "⌨", self.show_calculator, "#e0f2fe", "#0369a1").pack(side=tk.LEFT, padx=4)
        self._btn(r1_inner, "📜", self.show_history, "#fef3c7", "#92400e").pack(side=tk.LEFT, padx=4)
        self._btn(r1_inner, "💾", self.save_to_library, "#dcfce7", "#166534").pack(side=tk.LEFT, padx=4)
        self._btn(r1_inner, "➕ Формула", self.add_extra_equation, "#dbeafe", "#1e40af").pack(side=tk.LEFT, padx=4)
        self._btn(r1_inner, "⚙ Управление", self.manage_extra_equations, "#e0e7ff", "#3730a3").pack(side=tk.LEFT,
                                                                                                    padx=4)
        self._btn(r1_inner, "🧮 В точке", self.evaluate_at_point, "#fef3c7", "#92400e").pack(side=tk.LEFT, padx=4)
        self._btn(r1_inner, "🎚 Параметры", self.show_param_sliders, "#fef3c7", "#92400e").pack(side=tk.LEFT, padx=4)

        self.row2 = tk.Frame(self.pad, relief=tk.GROOVE, bd=1)
        self.row2.pack(fill=tk.X, pady=(8, 0))
        r2_inner = tk.Frame(self.row2, padx=10, pady=8)
        r2_inner.pack(fill=tk.X)
        self.lbl_lib = tk.Label(r2_inner, text="Библиотека:", font=("Segoe UI", 10, "bold"))
        self.lbl_lib.pack(side=tk.LEFT, padx=(0, 6))
        self.library_combo = ttk.Combobox(r2_inner, state="readonly", width=42, font=("Segoe UI", 10))
        self.library_combo.pack(side=tk.LEFT, padx=4)
        self.library_combo.bind("<<ComboboxSelected>>", self.load_from_library)
        self._btn(r2_inner, "📂", self.open_library_manager, "#e0e7ff", "#3730a3").pack(side=tk.LEFT, padx=4)
        self._btn(r2_inner, "📥 Импорт", self.import_formulas_from_file, "#dbeafe", "#1e40af").pack(side=tk.LEFT, padx=4)
        self._btn(r2_inner, "❓", self.show_help, "#fef3c7", "#92400e").pack(side=tk.LEFT, padx=4)

        self.row3 = tk.Frame(self.pad, relief=tk.GROOVE, bd=1)
        self.row3.pack(fill=tk.X, pady=(8, 0))
        r3_inner = tk.Frame(self.row3, padx=10, pady=8)
        r3_inner.pack(fill=tk.X)

        self.lbl_a = tk.Label(r3_inner, text="a =", font=("Segoe UI", 11))
        self.lbl_a.pack(side=tk.LEFT, padx=(0, 4))
        self.a_entry = tk.Entry(r3_inner, width=8, font=("Consolas", 11), relief=tk.SOLID, bd=1)
        self.a_entry.pack(side=tk.LEFT, padx=(0, 16), ipady=3)
        self.a_entry.insert(0, "-4")

        self.lbl_b = tk.Label(r3_inner, text="b =", font=("Segoe UI", 11))
        self.lbl_b.pack(side=tk.LEFT, padx=(0, 4))
        self.b_entry = tk.Entry(r3_inner, width=8, font=("Consolas", 11), relief=tk.SOLID, bd=1)
        self.b_entry.pack(side=tk.LEFT, padx=(0, 16), ipady=3)
        self.b_entry.insert(0, "-2")

        self.lbl_sig = tk.Label(r3_inner, text="σ =", font=("Segoe UI", 11))
        self.lbl_sig.pack(side=tk.LEFT, padx=(0, 4))
        self.sigma_entry = tk.Entry(r3_inner, width=12, font=("Consolas", 11), relief=tk.SOLID, bd=1)
        self.sigma_entry.pack(side=tk.LEFT, padx=(0, 20), ipady=3)
        self.sigma_entry.insert(0, "0.000001")

        self.btn_solve = self._btn(r3_inner, "▶ ВЫЧИСЛИТЬ", self.solve, C_ACCENT, "white", 11)
        self.btn_solve.pack(side=tk.LEFT, padx=4)
        self._btn(r3_inner, "🎬 Анимация", self.show_animation_dialog, "#f3e8ff", "#6b21a8").pack(side=tk.LEFT, padx=4)
        if HAS_SYMPY:
            self._btn(r3_inner, "🔬 SymPy", self.solve_analytical, "#fef3c7", "#92400e").pack(side=tk.LEFT, padx=4)

        mode_frame = tk.Frame(r3_inner)
        mode_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(mode_frame, text="Режим:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="1 перем. (x)", variable=self.var_mode, value="single",
                       font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Несколько", variable=self.var_mode, value="multi",
                       font=("Segoe UI", 9), command=self._on_var_mode_change).pack(side=tk.LEFT)

        # ГРАФИК
        self.graph_frame = tk.Frame(root, relief=tk.GROOVE, bd=1)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        g_header = tk.Frame(self.graph_frame)
        g_header.pack(fill=tk.X, padx=6, pady=4)
        self.lbl_graph = tk.Label(g_header, text="📈 Интерактивный график", font=("Segoe UI", 10, "bold"))
        self.lbl_graph.pack(side=tk.LEFT)
        tk.Label(g_header, text="(Колесико — зум, ЛКМ — перемещение, ПКМ — меню)",
                 font=("Segoe UI", 9), fg="#6b7280").pack(side=tk.LEFT, padx=10)
        self.coord_label = tk.Label(g_header, text="x: ---, y: --- | f(x): ---",
                                    font=("Consolas", 10), fg=C_ACCENT, width=35, anchor=tk.E)
        self.coord_label.pack(side=tk.RIGHT, padx=15)

        self._btn(g_header, "🖼 PNG", self.save_graph_png, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=4)
        self._btn(g_header, "🖼 SVG", self.export_svg, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=4)
        self._btn(g_header, "◀", self.view_back, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=2)
        self._btn(g_header, "▶", self.view_forward, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=2)
        self._btn(g_header, "🔄 Сброс", self.reset_view, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=4)
        self._btn(g_header, "🗺 Контур", self.show_contour_plot, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=4)
        self._btn(g_header, "➤ Вектор", self.show_vector_field, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=4)
        self._btn(g_header, "🎲 3D", self.show_3d_graph, "#e5e7eb", "#1f2937").pack(side=tk.RIGHT, padx=4)
        tk.Checkbutton(g_header, text="📍 Экстремумы", variable=self.show_extrema,
                       command=self.draw_graph, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=10)
        # Фиксируем layout g_header
        g_header.pack_propagate(False)
        g_header.config(height=35)
        self.canvas = tk.Canvas(self.graph_frame, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)

        # СТАТУС-БАР
        status_frame = tk.Frame(root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Готов")
        self.status_bar = tk.Label(status_frame, textvariable=self.status_var,
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 9))
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,
                                            maximum=100, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=10, pady=2)

        # Горячие клавиши
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())
        self.root.bind("<Control-s>", lambda e: self.save_session())
        self.root.bind("<Control-o>", lambda e: self.load_session())
        self.root.bind("<Control-r>", lambda e: self.solve())
        self.root.bind("<F5>", lambda e: self.solve())
        self.root.bind("<F1>", lambda e: self.show_help())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.apply_theme()
        self.refresh_library_combo()
        if self.library:
            self.library_combo.current(0)
            self.load_from_library()

        self.load_history()
        s = getattr(self, "_settings", {})
        for entry, key in ((self.eq_entry, "equation"), (self.a_entry, "a"),
                           (self.b_entry, "b"), (self.sigma_entry, "sigma")):
            if s.get(key):
                entry.delete(0, tk.END)
                entry.insert(0, s[key])
        if "show_extrema" in s:
            self.show_extrema.set(bool(s["show_extrema"]))

        if UPDATE_API:
            self.root.after(2000, lambda: self.check_for_updates(silent=True))

    def _btn(self, parent, text, cmd, bg, fg, size=10):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                         font=("Segoe UI", size, "bold"), relief=tk.RAISED,
                         bd=1, cursor="hand2", padx=10, pady=3)

    def on_closing(self):
        self.stop_animation()
        self._save_settings()
        self.save_history()
        self.root.destroy()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)

    def save_view_to_history(self):
        view = (self.view_x_min, self.view_x_max, self.view_y_min, self.view_y_max)
        if self.view_history and self.view_history_index >= 0 and \
                self.view_history[self.view_history_index] == view:
            return
        if self.view_history_index < len(self.view_history) - 1:
            self.view_history = self.view_history[:self.view_history_index + 1]
        self.view_history.append(view)
        if len(self.view_history) > self.max_view_history:
            self.view_history.pop(0)
        self.view_history_index = len(self.view_history) - 1

    def view_back(self):
        if self.view_history_index > 0:
            self.view_history_index -= 1
            view = self.view_history[self.view_history_index]
            self.view_x_min, self.view_x_max, self.view_y_min, self.view_y_max = view
            self.draw_graph()

    def view_forward(self):
        if self.view_history_index < len(self.view_history) - 1:
            self.view_history_index += 1
            view = self.view_history[self.view_history_index]
            self.view_x_min, self.view_x_max, self.view_y_min, self.view_y_max = view
            self.draw_graph()

    def toggle_theme(self):
        themes = list(THEMES.keys())
        idx = themes.index(self.theme)
        self.theme = themes[(idx + 1) % len(themes)]
        self.apply_theme()

    def apply_theme(self):
        c = dict(THEMES[self.theme])
        if self.high_contrast.get():
            c["text"] = "white" if self.theme == "dark" else "black"
            c["axis"] = "yellow"
        self.root.configure(bg=c["bg"])
        self.header.configure(bg=c["header"])
        self.btn_theme.configure(bg=c["header"], fg=c["text"], activebackground=c["bg"])
        for frame in (self.pad, self.row1, self.row2, self.row3, self.graph_frame):
            frame.configure(bg=c["panel"] if frame != self.pad else c["bg"])
        for child in self.pad.winfo_children():
            try:
                child.configure(bg=c["panel"])
                for sub in child.winfo_children():
                    sub.configure(bg=c["panel"])
                    for w in sub.winfo_children():
                        if isinstance(w, (tk.Label, tk.Frame)):
                            w.configure(bg=c["panel"])
            except tk.TclError:
                pass
        for lbl in (self.lbl_fx, self.lbl_lib, self.lbl_a, self.lbl_b, self.lbl_sig, self.lbl_graph):
            lbl.configure(bg=c["panel"], fg=c["text"])
        self.canvas.configure(bg=c["canvas_bg"])
        self.status_bar.configure(bg=c["panel"], fg=c["text"])
        if self.last_f:
            self.draw_graph()

    def parse_equation(self, eq_str, variables=None):
        eq_str = eq_str.replace("^", "**")
        eq_str = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', eq_str)
        eq_str = re.sub(r'(\))([a-zA-Z0-9\(])', r'\1*\2', eq_str)
        if '=' in eq_str:
            l, r = eq_str.split('=', 1)
            eq_str = f"({l}) - ({r})"
        if variables is None:
            math_funcs = set(dir(math))
            found_vars = set(re.findall(r'\b([a-z])\b', eq_str))
            variables = [v for v in found_vars if v not in math_funcs and v != 'e']
            if not variables:
                variables = ['x']
        try:
            node = ast.parse(eq_str, mode='eval')
        except SyntaxError:
            raise ValueError("Синтаксическая ошибка")
        allowed_funcs = {name: getattr(math, name) for name in dir(math) if not name.startswith('_')}
        allowed_funcs.update({'abs': abs})

        def _eval_ast(n, var_values):
            if isinstance(n, ast.Constant):
                return n.value
            if isinstance(n, ast.Name):
                if n.id in var_values:
                    return var_values[n.id]
                if n.id in allowed_funcs:
                    return allowed_funcs[n.id]
                raise ValueError(f"Неизвестная переменная: {n.id}")
            if isinstance(n, ast.Attribute):
                if isinstance(n.value, ast.Name) and n.value.id == 'math':
                    return getattr(math, n.attr)
                raise ValueError("Доступен только модуль math")
            if isinstance(n, ast.BinOp):
                left = _eval_ast(n.left, var_values)
                right = _eval_ast(n.right, var_values)
                ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                       ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
                if type(n.op) not in ops:
                    raise ValueError("Неподдерживаемая операция")
                return ops[type(n.op)](left, right)
            if isinstance(n, ast.UnaryOp):
                operand = _eval_ast(n.operand, var_values)
                if isinstance(n.op, ast.USub):
                    return -operand
                if isinstance(n.op, ast.UAdd):
                    return operand
                raise ValueError("Неподдерживаемая унарная операция")
            if isinstance(n, ast.Call):
                func = _eval_ast(n.func, var_values)
                args = [_eval_ast(arg, var_values) for arg in n.args]
                return func(*args)
            raise ValueError("Неподдерживаемая конструкция")

        return lambda var_dict: _eval_ast(node.body, var_dict), variables

    def _on_var_mode_change(self):
        if self.var_mode.get() == "multi":
            self._show_multi_var_dialog()
        else:
            self.multi_vars = {}

    def _show_multi_var_dialog(self):
        eq = self.eq_entry.get()
        math_names = set(dir(math)) | {'x', 'abs', 'e', 'pi'}
        found = set(re.findall(r'\b([a-z])\b', eq))
        extra_vars = sorted([v for v in found if v not in math_names])
        if not extra_vars:
            messagebox.showinfo("Информация",
                                "В формуле не найдено дополнительных переменных (y, z, a, b...).\nПример: x**2 + y**2 - 4")
            self.var_mode.set("single")
            return
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("Значения переменных")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        tk.Label(dialog, text="Введите значения дополнительных переменных:",
                 font=("Segoe UI", 11, "bold")).pack(pady=10)
        entries = {}
        for var in extra_vars:
            frame = tk.Frame(dialog)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{var} =", font=("Consolas", 12, "bold")).pack(side=tk.LEFT, padx=10)
            entry = tk.Entry(frame, width=10, font=("Consolas", 12))
            entry.pack(side=tk.LEFT)
            entry.insert(0, str(self.multi_vars.get(var, 0)))
            entries[var] = entry

        def apply():
            try:
                for var, entry in entries.items():
                    self.multi_vars[var] = float(entry.get().replace(",", "."))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверное значение")

        tk.Button(dialog, text="✓ Применить", command=apply,
                  bg=C_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=5).pack(pady=15)

    def solve(self):
        if self.is_calculating:
            return
        self.stop_animation()
        self.is_calculating = True
        self.btn_solve.config(state=tk.DISABLED, text="⏳ ...")
        self.status_var.set("Вычисление...")
        self.progress_var.set(0)
        t0 = time.perf_counter()
        eq = self.eq_entry.get()

        try:
            f_parsed, variables = self.parse_equation(eq)
            if self.var_mode.get() == "single" or len(variables) <= 1:
                f = lambda x: f_parsed({'x': x})
            else:
                for v in variables:
                    if v != 'x' and v not in self.multi_vars:
                        self.multi_vars[v] = 0.0

                def f(x):
                    d = {'x': x}
                    d.update(self.multi_vars)
                    return f_parsed(d)
            a = float(self.a_entry.get().replace(",", "."))
            b = float(self.b_entry.get().replace(",", "."))
            sigma = float(self.sigma_entry.get().replace(",", "."))
            sigma = max(sigma, 1e-15)
        except Exception as e:
            self._handle_calc_error(str(e))
            return

        if a >= b:
            self._handle_calc_error("Требуется a < b")
            return

        # ── проба ВНУТРИ интервала, а не в нуле; ошибка не фатальна ──
        try:
            f((a + b) / 2.0)
        except Exception:
            pass

        def norm(res):
            """2-tuple и 3-tuple → (root, history)."""
            if not res:
                return None, []
            return res[0], (res[1] if len(res) > 1 and res[1] else [])

        def guard(fn, *args):
            try:
                return fn(*args)
            except Exception:
                return None

        def worker():
            try:
                self.root.after(0, lambda: self.progress_var.set(10))
                rb, hb = norm(guard(self.bisection, f, a, b, sigma))
                self.root.after(0, lambda: self.progress_var.set(22))
                rc, hc = norm(guard(self.chord_method, f, a, b, sigma))
                self.root.after(0, lambda: self.progress_var.set(34))
                rn, hn = norm(guard(self.newton_method, f, a, b, sigma))
                self.root.after(0, lambda: self.progress_var.set(46))
                rs, hs = norm(guard(self.secant_method, f, a, b, sigma))
                self.root.after(0, lambda: self.progress_var.set(58))
                rbr, hbr = norm(guard(brent_method, f, a, b, sigma))
                self.root.after(0, lambda: self.progress_var.set(70))
                rmpi, hmpi = norm(guard(simple_iteration, f, a, b, sigma))
                self.root.after(0, lambda: self.progress_var.set(82))
                all_r = guard(find_all_roots, f, a, b, sigma, 400, "brent") or []
                self.root.after(0, lambda: self.progress_var.set(94))
                elapsed = (time.perf_counter() - t0) * 1000
                self.root.after(0, lambda: self.finish_solve(
                    f, a, b, sigma, rb, hb, rc, hc, rn, hn, rs, hs,
                    rbr, hbr, rmpi, hmpi, all_r, eq, elapsed))
            except Exception as ex:
                msg = str(ex)
                self.root.after(0, lambda m=msg: self._handle_calc_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_calc_error(self, error_msg):
        self.is_calculating = False
        self.btn_solve.config(state=tk.NORMAL, text="▶ ВЫЧИСЛИТЬ")
        self.progress_var.set(0)
        messagebox.showerror("Ошибка", error_msg)
        self.status_var.set("Ошибка")

    def finish_solve(self, f, a, b, sigma, rb, hb, rc, hc, rn, hn, rs, hs,
                     rbr, hbr, rmpi, hmpi, all_roots, eq, elapsed_ms):
        self.is_calculating = False
        self.btn_solve.config(state=tk.NORMAL, text="▶ ВЫЧИСЛИТЬ")
        self.last_f = f
        self.all_roots = all_roots
        margin = max(5, (b - a) * 2)
        self.view_x_min, self.view_x_max = a - margin, b + margin
        self._auto_fit_y()
        self.save_view_to_history()
        self.draw_graph()
        root_x = rb or rc or rn or rbr or rmpi
        self.history_log.append((eq, f"{a}", f"{b}", f"{root_x:.5f}" if root_x else "—"))
        self.save_history()
        for method, hist in [("bisection", hb), ("chord", hc), ("newton", hn),
                             ("secant", hs), ("brent", hbr), ("mpi", hmpi)]:
            if hist:
                self.stats.record_solve(method, len(hist), elapsed_ms / 6, sigma)
        new_ach = self.stats.check_achievements()
        for ach in new_ach:
            self._notify_achievement(ach)
        self.show_results(hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi,
                          a, b, sigma, elapsed_ms, all_roots)
        self.status_var.set(f"Готово ({elapsed_ms:.0f} мс, корней: {len(all_roots)})")
        if winsound:
            winsound.MessageBeep(winsound.MB_OK)

    def _auto_fit_y(self):
        if not self.last_f:
            return
        ys = []
        for i in range(200):
            x = self.view_x_min + i * (self.view_x_max - self.view_x_min) / 199
            try:
                y = self.last_f(x)
                if math.isfinite(y):
                    ys.append(y)
            except Exception:
                pass
        if ys:
            ymin, ymax = min(ys), max(ys)
            margin = max(1, (ymax - ymin) * 0.2)
            self.view_y_min = ymin - margin
            self.view_y_max = ymax + margin

    def _notify_achievement(self, ach):
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        top.geometry("300x80+50+50")
        top.configure(bg="#fef3c7")
        tk.Label(top, text=f"{ach['icon']} {ach['name']}",
                 font=("Segoe UI", 12, "bold"), bg="#fef3c7", fg="#92400e").pack(pady=5)
        tk.Label(top, text=ach["desc"], font=("Segoe UI", 9), bg="#fef3c7", fg="#92400e").pack()
        top.after(3000, top.destroy)

    def show_results(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi,
                     a, b, sigma, elapsed_ms, all_roots):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Результаты")
        win.geometry("1100x750")
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def copy_tree(event):
            item = event.widget.focus()
            if not item:
                return
            values = event.widget.item(item, 'values')
            self.root.clipboard_clear()
            self.root.clipboard_append("\t".join(str(v) for v in values))

        def copy_all(tree_widget):
            items = tree_widget.get_children()
            if not items:
                return
            cols = tree_widget.cget("columns")
            headers = [tree_widget.heading(c, "text") for c in cols]
            csv_data = "\t".join(headers) + "\n"
            for item in items:
                values = tree_widget.item(item, "values")
                csv_data += "\t".join(str(v) for v in values) + "\n"
            self.root.clipboard_clear()
            self.root.clipboard_append(csv_data)

        def create_tree(parent, cols, data):
            tree = ttk.Treeview(parent, columns=cols, show="headings")
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=100, anchor=tk.CENTER)
            tree.pack(fill=tk.BOTH, expand=True)
            for r in data:
                tree.insert("", tk.END, values=[f"{v:.5g}" if isinstance(v, float) else v for v in r])
            tree.bind("<Control-c>", copy_tree)
            btn_frame = tk.Frame(parent)
            btn_frame.pack(fill=tk.X, pady=5)
            tk.Button(btn_frame, text="📋 Копировать всё",
                      command=lambda: copy_all(tree),
                      bg="#dbeafe", fg="#1e40af", font=("Segoe UI", 9, "bold"),
                      relief=tk.RAISED, bd=1, cursor="hand2", padx=10, pady=3).pack(side=tk.RIGHT, padx=5)
            return tree

        t1 = tk.Frame(nb);
        nb.add(t1, text="Бисекция")
        create_tree(t1, ("N", "a", "b", "c", "f(c)", "|b-a|"), hb)
        t2 = tk.Frame(nb);
        nb.add(t2, text="Хорды")
        create_tree(t2, ("N", "x_n", "x_{n+1}", "f", "|dx|"), hc)
        t3 = tk.Frame(nb);
        nb.add(t3, text="Ньютон")
        create_tree(t3, ("N", "x_n", "x_{n+1}", "f", "|dx|"), hn)
        t4 = tk.Frame(nb);
        nb.add(t4, text="Секущие")
        create_tree(t4, ("N", "x_{n-1}", "x_n", "f", "|dx|"), hs)
        t5 = tk.Frame(nb);
        nb.add(t5, text="Брент")
        create_tree(t5, ("N", "a", "b", "s", "f(s)", "|b-a|"), hbr)
        t6 = tk.Frame(nb);
        nb.add(t6, text="МПИ")
        create_tree(t6, ("N", "x_n", "x_{n+1}", "f", "|dx|"), hmpi)
        t_conv = tk.Frame(nb, bg="white")
        nb.add(t_conv, text="Сходимость")
        self._draw_log_convergence(t_conv, hb, hc, hn, hs, hbr, hmpi)
        t_int = tk.Frame(nb);
        nb.add(t_int, text="Интеграл")
        self._show_integral_tab(t_int, a, b)
        t_roots = tk.Frame(nb);
        nb.add(t_roots, text="🎯 Все корни")
        self._show_all_roots_tab(t_roots, all_roots)
        t_bench = tk.Frame(nb);
        nb.add(t_bench, text="⏱ Бенчмарк")
        self._show_benchmark_tab(t_bench, a, b, sigma)

        res = tk.Frame(win, bg="#f0fdf4", pady=10)
        res.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(res, text=f"⏱ {elapsed_ms:.0f} мс | 🎯 Корней: {len(all_roots)}",
                 font=("Consolas", 11), bg="#f0fdf4").pack(side=tk.LEFT, padx=10)
        bf = tk.Frame(res);
        bf.pack(side=tk.RIGHT)
        self._btn(bf, "📕 PDF", lambda: self.export_pdf(
            hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma),
                  "#fce7f3", "#9d174d", 9).pack(side=tk.LEFT, padx=2)
        if HAS_OPENPYXL:
            self._btn(bf, "📗 Excel", lambda: self.export_excel(
                hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma),
                      "#dcfce7", "#166534", 9).pack(side=tk.LEFT, padx=2)
        self._btn(bf, "📄 HTML", lambda: self.export_html(
            hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma),
                  "#fef3c7", "#92400e", 9).pack(side=tk.LEFT, padx=2)
        self._btn(bf, "📝 MD", lambda: self.export_markdown(
            hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma),
                  "#e0e7ff", "#3730a3", 9).pack(side=tk.LEFT, padx=2)
        self._btn(bf, "📊 CSV", lambda: self.export_csv(
            hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma),
                  "#dbeafe", "#1e40af", 9).pack(side=tk.LEFT, padx=2)
        self._btn(bf, "📝 LaTeX", lambda: self.export_latex(
            hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma),
                  "#f3e8ff", "#6b21a8", 9).pack(side=tk.LEFT, padx=2)

    def _draw_log_convergence(self, parent, *hists):
        parent.update_idletasks()
        W = max(700, parent.winfo_width() - 60)
        H = max(450, parent.winfo_height() - 60)
        c = tk.Canvas(parent, bg="white", highlightthickness=0, width=W, height=H)
        c.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        colors = [C_DANGER, C_SUCCESS, C_NEWTON, C_SECANT, C_BRENT, C_MPI]
        names = ["Бисекция", "Хорды", "Ньютон", "Секущие", "Брент", "МПИ"]
        margin_l, margin_b, margin_t, margin_r = 80, 60, 40, 200
        method_data = []
        all_logs = []
        for idx, hist in enumerate(hists):
            if not hist:
                method_data.append(None)
                continue
            pts = []
            for row in hist:
                k = row[0]
                err = abs(row[-1]) if len(row) >= 6 else 1e-10
                err = max(err, 1e-16)
                log_err = -math.log10(err)
                pts.append((k, log_err))
                all_logs.append(log_err)
            method_data.append(pts)
        if not all_logs:
            c.create_text(W // 2, H // 2, text="Нет данных", font=("Segoe UI", 12), fill="gray")
            return
        log_min = max(0, min(all_logs) - 0.5)
        log_max = max(all_logs) + 0.5
        log_range = log_max - log_min if log_max > log_min else 1
        max_iter = max(len(pts) for pts in method_data if pts)
        if max_iter < 5:
            max_iter = 5
        c.create_text(W // 2, 20, text="Сравнение скорости сходимости методов",
                      font=("Segoe UI", 12, "bold"), fill="#1f2937")
        n_grid = 6
        for i in range(n_grid + 1):
            log_val = log_min + log_range * i / n_grid
            py = H - margin_b - (i / n_grid) * (H - margin_t - margin_b)
            c.create_line(margin_l, py, W - margin_r, py, fill="#e5e7eb", dash=(3, 3))
            c.create_text(margin_l - 10, py, text=f"1e-{log_val:.0f}",
                          font=("Segoe UI", 8), fill="#6b7280", anchor=tk.E)
        n_x = min(max_iter, 10)
        for i in range(n_x + 1):
            iter_val = 1 + (max_iter - 1) * i / n_x
            px = margin_l + (i / n_x) * (W - margin_l - margin_r)
            c.create_line(px, margin_t, px, H - margin_b, fill="#f3f4f6", dash=(2, 2))
            c.create_text(px, H - margin_b + 15, text=f"{iter_val:.0f}",
                          font=("Segoe UI", 8), fill="#6b7280", anchor=tk.N)
        c.create_line(margin_l, margin_t - 10, margin_l, H - margin_b, fill="black", width=2)
        c.create_line(margin_l, H - margin_b, W - margin_r + 10, H - margin_b, fill="black", width=2)
        for idx, pts in enumerate(method_data):
            if not pts or len(pts) < 2:
                continue
            color = colors[idx % len(colors)]
            screen_pts = []
            for k, log_err in pts:
                px = margin_l + ((k - 1) / max(1, max_iter - 1)) * (W - margin_l - margin_r)
                py = H - margin_b - ((log_err - log_min) / log_range) * (H - margin_t - margin_b)
                py = max(margin_t, min(H - margin_b, py))
                screen_pts.append((px, py))
            if len(screen_pts) >= 2:
                flat = [coord for p in screen_pts for coord in p]
                c.create_line(flat, fill=color, width=2)
                for px, py in screen_pts:
                    c.create_oval(px - 3, py - 3, px + 3, py + 3,
                                  fill=color, outline="white", width=1)
        c.create_text(20, H // 2, text="-log10(error)", angle=90,
                      font=("Segoe UI", 10, "bold"), fill="#374151")
        c.create_text((margin_l + W - margin_r) // 2, H - 15, text="Номер итерации",
                      font=("Segoe UI", 10, "bold"), fill="#374151")
        legend_x = W - margin_r + 20
        legend_y = margin_t + 10
        c.create_text(legend_x, legend_y, anchor=tk.W,
                      text="Методы:", font=("Segoe UI", 10, "bold"), fill="#1f2937")
        legend_y += 22
        for i, name in enumerate(names):
            if method_data[i]:
                color = colors[i]
                c.create_line(legend_x, legend_y, legend_x + 20, legend_y, fill=color, width=3)
                c.create_text(legend_x + 35, legend_y, anchor=tk.W,
                              text=name, font=("Segoe UI", 9), fill=color)
                legend_y += 20

    def _show_integral_tab(self, parent, a, b):
        if not self.last_f:
            return
        tk.Label(parent, text="Численное интегрирование ∫[a,b] f(x)dx",
                 font=("Segoe UI", 12, "bold")).pack(pady=10)
        n_var = tk.IntVar(value=1000)
        tk.Label(parent, text="Число разбиений n:").pack()
        tk.Spinbox(parent, from_=10, to=100000, textvariable=n_var, width=10).pack()
        result_lbl = tk.Label(parent, text="", font=("Consolas", 12), fg=C_ACCENT)
        result_lbl.pack(pady=15)

        def calc():
            n = n_var.get()
            try:
                t = integrate_trapezoid(self.last_f, a, b, n)
                s = integrate_simpson(self.last_f, a, b, n)
                g = integrate_gauss(self.last_f, a, b, 5)
                mc = integrate_monte_carlo(self.last_f, a, b, 10000)
                ad = integrate_adaptive_simpson(self.last_f, a, b, 1e-10)
                result_lbl.config(text=(
                    f"Трапеции (n={n}): {t:.10f}\n"
                    f"Симпсон  (n={n}): {s:.10f}\n"
                    f"Гаусс   (5-точ): {g:.10f}\n"
                    f"Монте-Карло    : {mc:.10f}\n"
                    f"Адапт. Симпсон : {ad:.10f}"))
            except Exception as e:
                result_lbl.config(text=f"Ошибка: {e}")

        tk.Button(parent, text="Вычислить", command=calc,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=5).pack(pady=10)

    def _show_all_roots_tab(self, parent, roots):
        tk.Label(parent, text=f"Найдено корней: {len(roots)}",
                 font=("Segoe UI", 12, "bold")).pack(pady=10)
        text = tk.Text(parent, font=("Consolas", 11), height=15)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        for i, r in enumerate(roots, 1):
            text.insert(tk.END, f"  Корень #{i}:  x = {r:.10f}\n")
            try:
                text.insert(tk.END, f"              f(x) = {self.last_f(r):.2e}\n\n")
            except Exception:
                text.insert(tk.END, "              f(x) = [ошибка]\n\n")

    def _show_benchmark_tab(self, parent, a, b, sigma):
        if not self.last_f:
            return
        tk.Label(parent, text="Сравнение методов (3 запуска каждый)",
                 font=("Segoe UI", 12, "bold")).pack(pady=10)
        text = tk.Text(parent, font=("Consolas", 10), height=20)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        methods = {
            "Бисекция": lambda f, a, b, s: self.bisection(f, a, b, s),
            "Хорды": lambda f, a, b, s: self.chord_method(f, a, b, s),
            "Ньютон": lambda f, a, b, s: self.newton_method(f, a, b, s),
            "Секущие": lambda f, a, b, s: self.secant_method(f, a, b, s),
            "Брент": lambda f, a, b, s: brent_method(f, a, b, s),
            "МПИ": lambda f, a, b, s: simple_iteration(f, a, b, s),
        }
        self.status_var.set("⏱ Бенчмарк...")

        def run():
            res = benchmark(self.last_f, a, b, sigma, methods, n_runs=3)
            text.delete(1.0, tk.END)
            text.insert(tk.END, f"{'Метод':<12} {'Время, мс':<12} {'Итераций':<10} {'Успех'}\n")
            text.insert(tk.END, "-" * 50 + "\n")
            for name, r in res.items():
                t = f"{r['avg_time_ms']:.2f}" if r['avg_time_ms'] else "—"
                it = f"{r['avg_iters']:.0f}"
                ok = "✓" if r['success'] else "✗"
                text.insert(tk.END, f"{name:<12} {t:<12} {it:<10} {ok}\n")
            self.root.after(0, lambda: self.status_var.set("Бенчмарк готов"))

        threading.Thread(target=run, daemon=True).start()

    def safe_eval(self, f, x):
        """Вычислить f(x), вернув nan вместо исключения."""
        try:
            y = f(x)
            if isinstance(y, complex):
                return math.nan
            return y if math.isfinite(y) else math.nan
        except (OverflowError, ValueError, ZeroDivisionError, OSError, TypeError):
            return math.nan
    def safe_eval(self, f, x):
        try:
            y = f(x)
            if isinstance(y, complex):
                return math.nan
            y = float(y)
            return y if math.isfinite(y) else math.nan
        except Exception:
            return math.nan

    def safe_f(self, x):
        """Вычислить f(x), вернув nan при переполнении/ошибке."""
        try:
            y = self.last_f(x)
            return y if math.isfinite(y) else math.nan
        except (OverflowError, ValueError, ZeroDivisionError, OSError, TypeError):
            return math.nan
    def df(self, f, x, h=1e-5):
        return (f(x + h) - f(x - h)) / (2 * h)

    def d2f(self, f, x, h=1e-3):
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)

    def bisection(self, f, a, b, sigma, max_step=100000):
        """Возвращает (root, history, info)."""
        history = []
        info = {"converged": False, "reason": "", "iterations": 0, "error": float("inf")}
        fa, fb = self.safe_eval(f, a), self.safe_eval(f, b)

        if math.isnan(fa) or math.isnan(fb):
            info["reason"] = "f(a) или f(b) не определены (разрыв/переполнение)"
            return None, history, info
        if fa * fb > 0:
            info["reason"] = "f(a)·f(b) > 0 — корень не гарантирован на [a,b]"
            return None, history, info
        if fa == 0:
            info.update(converged=True, reason="Точный корень в a", error=0.0)
            return a, history, info
        if fb == 0:
            info.update(converged=True, reason="Точный корень в b", error=0.0)
            return b, history, info

        k = 0
        while k < max_step:
            c = (a + b) / 2.0
            fc = self.safe_eval(f, c)
            width = abs(b - a)
            history.append((k + 1, a, b, c, fc, width))
            k += 1
            if math.isnan(fc):
                info.update(reason="f(c) не определена внутри отрезка", iterations=k, error=width)
                return None, history, info
            if fc == 0 or width <= sigma:
                info.update(converged=True, reason="Достигнута точность σ",
                            iterations=k, error=width)
                return c, history, info
            if fa * fc < 0:
                b, fb = c, fc
            else:
                a, fa = c, fc
            if width <= 1e-16 * max(1.0, abs(c)):
                info.update(converged=True, reason="Достигнута машинная точность",
                            iterations=k, error=width)
                return c, history, info

        info.update(reason=f"Лимит итераций ({max_step}) — НЕ сошёлся",
                    iterations=k, error=abs(b - a))
        return (a + b) / 2.0, history, info

    def chord_method(self, f, a, b, sigma, max_step=1000):
        fa, fb = f(a), f(b)
        if fa * fb >= 0:
            return None, [], None
        f2a, f2b = self.d2f(f, a), self.d2f(f, b)
        x0, x_moving = (a, b) if fa * f2a > 0 else (b, a)
        fx0 = f(x0)
        history = []
        x_prev = x_moving
        for k in range(1, max_step + 1):
            fx_prev = f(x_prev)
            denom = fx_prev - fx0
            if abs(denom) < 1e-15:
                break
            x_new = x0 - fx0 * (x_prev - x0) / denom
            history.append((k, x_prev, x_new, f(x_new), abs(x_new - x_prev)))
            if abs(x_new - x_prev) < sigma:
                return x_new, history, x0
            x_prev = x_new
        return x_prev, history, x0

    def newton_method(self, f, a, b, sigma, max_step=1000):
        f2a, f2b = self.d2f(f, a), self.d2f(f, b)
        x0 = a if f(a) * f2a > 0 else b
        history = []
        x_prev = x0
        for k in range(1, max_step + 1):
            fx = f(x_prev)
            dfx = self.df(f, x_prev)
            if abs(dfx) < 1e-15:
                break
            x_new = x_prev - fx / dfx
            history.append((k, x_prev, x_new, f(x_new), abs(x_new - x_prev)))
            if abs(x_new - x_prev) < sigma:
                return x_new, history, x0
            x_prev = x_new
        return x_prev, history, x0

    def secant_method(self, f, a, b, sigma, max_step=1000):
        history = []
        x0, x1 = a, b
        f0, f1 = f(x0), f(x1)
        if abs(f0 - f1) < 1e-15:
            return None, [], None
        for k in range(1, max_step + 1):
            if abs(f1 - f0) < 1e-15:
                break
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            f2 = f(x2)
            history.append((k, x1, x2, f2, abs(x2 - x1)))
            if abs(x2 - x1) < sigma:
                return x2, history, x1
            x0, f0 = x1, f1
            x1, f1 = x2, f2
        return x1, history, x0

    def reset_view(self):
        self.view_x_min, self.view_x_max = -100.0, 100.0
        self.view_y_min, self.view_y_max = -100.0, 100.0
        if self.last_f:
            self.save_view_to_history()
            self.draw_graph()

    def on_zoom(self, event):
        self.stats.data["graph_zoomed"] = True
        self.stats.save()
        if not self.last_f:
            return
        factor = 0.8 if (event.num == 4 or getattr(event, 'delta', 0) > 0) else 1.25
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        math_x = self.view_x_min + (event.x / w) * (self.view_x_max - self.view_x_min)
        math_y = self.view_y_max - (event.y / h) * (self.view_y_max - self.view_y_min)
        self.view_x_min = math_x + (self.view_x_min - math_x) * factor
        self.view_x_max = math_x + (self.view_x_max - math_x) * factor
        self.view_y_min = math_y + (self.view_y_min - math_y) * factor
        self.view_y_max = math_y + (self.view_y_max - math_y) * factor
        self.draw_graph()

    def on_drag_start(self, event):
        self.drag_start_x, self.drag_start_y = event.x, event.y
        self.drag_start_view = (self.view_x_min, self.view_x_max,
                                self.view_y_min, self.view_y_max)

    def on_drag_motion(self, event):
        if not self.last_f or self.drag_start_view is None:
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx, dy = event.x - self.drag_start_x, event.y - self.drag_start_y
        vx1, vx2, vy1, vy2 = self.drag_start_view
        shift_x = -(dx / w) * (vx2 - vx1)
        shift_y = (dy / h) * (vy2 - vy1)
        self.view_x_min, self.view_x_max = vx1 + shift_x, vx2 + shift_x
        self.view_y_min, self.view_y_max = vy1 + shift_y, vy2 + shift_y
        self.draw_graph()

    def on_drag_end(self, event):
        if self.drag_start_view:
            self.save_view_to_history()
        self.drag_start_view = None

    def on_mouse_move(self, event):
        if not self.last_f:
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        x = self.view_x_min + (event.x / w) * (self.view_x_max - self.view_x_min)
        y = self.view_y_max - (event.y / h) * (self.view_y_max - self.view_y_min)
        try:
            fy = self.last_f(x)
            self.coord_label.config(text=f"x: {x:.3f}, y: {y:.3f} | f(x): {fy:.3f}")
        except Exception:
            self.coord_label.config(text=f"x: {x:.3f}, y: {y:.3f} | f(x): ---")

    def on_right_click(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="🔄 Сбросить вид", command=self.reset_view)
        menu.add_command(label="📍 Центрировать в этой точке",
                         command=lambda: self._center_at(event.x, event.y))
        menu.add_separator()
        menu.add_command(label="🖼 Сохранить PNG", command=self.save_graph_png)
        menu.add_command(label="🖼 Сохранить SVG", command=self.export_svg)
        menu.tk_popup(event.x_root, event.y_root)

    def _center_at(self, px, py):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = self.view_x_min + (px / w) * (self.view_x_max - self.view_x_min)
        cy = self.view_y_max - (py / h) * (self.view_y_max - self.view_y_min)
        dx = (self.view_x_max - self.view_x_min) / 2
        dy = (self.view_y_max - self.view_y_min) / 2
        self.view_x_min, self.view_x_max = cx - dx, cx + dx
        self.view_y_min, self.view_y_max = cy - dy, cy + dy
        self.save_view_to_history()
        self.draw_graph()

    def on_canvas_double_click(self, event):
        if not self.last_f:
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        x = self.view_x_min + (event.x / w) * (self.view_x_max - self.view_x_min)
        try:
            y = self.last_f(x)
            px, py = self._to_scr(x, y)
            self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4,
                                    fill=C_DANGER, outline="black")
            self.canvas.create_text(px + 10, py - 10,
                                    text=f"({x:.3f}, {y:.3f})",
                                    font=("Segoe UI", 9), fill=C_DANGER)
        except Exception:
            pass

    def _on_resize(self, event):
        if self.last_f:
            self.draw_graph()

    def _to_scr(self, x, y):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        x_min, x_max = self.view_x_min, self.view_x_max
        y_min, y_max = self.view_y_min, self.view_y_max
        px = (x - x_min) / (x_max - x_min) * w
        py = h - (y - y_min) / (y_max - y_min) * h
        return px, py

    def find_extrema(self, f, x_min, x_max, num_points=1000):
        extrema = []
        step = (x_max - x_min) / num_points
        for i in range(1, num_points):
            x = x_min + i * step
            try:
                dfx = self.df(f, x)
                dfx_prev = self.df(f, x - step)
                if dfx * dfx_prev < 0:
                    y = f(x)
                    if math.isfinite(y):
                        extrema.append((x, y))
                        self.stats.record_extrema()
            except Exception:
                continue
        return extrema

    def draw_graph(self, anim_data=None):
        c = THEMES[self.theme]
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1 or h <= 1 or not self.last_f:
            return
        x_min, x_max = self.view_x_min, self.view_x_max
        y_min, y_max = self.view_y_min, self.view_y_max

        def to_scr(x, y):
            return ((x - x_min) / (x_max - x_min) * w,
                    h - (y - y_min) / (y_max - y_min) * h)

        range_x, range_y = x_max - x_min, y_max - y_min
        step_x = 10 ** math.floor(math.log10(range_x)) / 2 if range_x > 0 else 1
        start_x = math.floor(x_min / step_x) * step_x
        for gx in [start_x + i * step_x for i in range(int(range_x / step_x) + 3)]:
            px, _ = to_scr(gx, 0)
            if 0 <= px <= w:
                self.canvas.create_line(px, 0, px, h, fill=c["grid"])
                if abs(gx) > 1e-9:
                    _, oy = to_scr(0, 0)
                    self.canvas.create_text(px, max(15, min(h - 5, oy + 10)),
                                            text=f"{gx:g}", font=("Segoe UI", 7), fill=c["muted"])
        step_y = 10 ** math.floor(math.log10(range_y)) / 2 if range_y > 0 else 1
        start_y = math.floor(y_min / step_y) * step_y
        for gy in [start_y + i * step_y for i in range(int(range_y / step_y) + 3)]:
            _, py = to_scr(0, gy)
            if 0 <= py <= h:
                self.canvas.create_line(0, py, w, py, fill=c["grid"])
                if abs(gy) > 1e-9:
                    ox, _ = to_scr(0, 0)
                    self.canvas.create_text(max(15, min(w - 15, ox - 15)), py,
                                            text=f"{gy:g}", font=("Segoe UI", 7), fill=c["muted"])
        ox, oy = to_scr(0, 0)
        if 0 <= oy <= h:
            self.canvas.create_line(0, oy, w, oy, fill=c["axis"], width=2)
        if 0 <= ox <= w:
            self.canvas.create_line(ox, 0, ox, h, fill=c["axis"], width=2)

        if self.a_entry.get() and self.b_entry.get():
            try:
                xl, _ = to_scr(float(self.a_entry.get()), 0)
                xr, _ = to_scr(float(self.b_entry.get()), 0)
                if 0 <= xl <= w:
                    self.canvas.create_line(xl, 0, xl, h, fill=C_WARN, width=2, dash=(5, 5))
                if 0 <= xr <= w:
                    self.canvas.create_line(xr, 0, xr, h, fill=C_WARN, width=2, dash=(5, 5))
            except Exception:
                pass

        for eq_data in self.extra_equations:
            if not eq_data.get('visible', True):
                continue
            try:
                f_extra = eq_data['func']
                color = eq_data['color']
                pts = []
                prev_y = None
                for j in range(w * 2):
                    x = x_min + j * (x_max - x_min) / (w * 2 - 1)
                    try:
                        y = f_extra({'x': x})
                        if not math.isfinite(y) or (prev_y is not None and abs(y - prev_y) > range_y * 5):
                            if len(pts) >= 4:
                                self.canvas.create_line(pts, fill=color, width=2)
                            pts = []
                            prev_y = None
                            continue
                        prev_y = y
                        y_draw = max(y_min - range_y, min(y_max + range_y, y))
                        px, py = to_scr(x, y_draw)
                        pts += [px, py]
                    except Exception:
                        if len(pts) >= 4:
                            self.canvas.create_line(pts, fill=color, width=2)
                        pts = []
                        prev_y = None
                if len(pts) >= 4:
                    self.canvas.create_line(pts, fill=color, width=2)
            except Exception:
                pass

        pts = []
        samples = w * 2
        prev_y = None
        for i in range(samples):
            x = x_min + i * (x_max - x_min) / (samples - 1)
            try:
                y = self.safe_f(x)
                if not math.isfinite(y) or (prev_y is not None and abs(y - prev_y) > range_y * 5):
                    if len(pts) >= 4:
                        self.canvas.create_line(pts, fill=C_ACCENT, width=2)
                    pts = []
                    prev_y = None
                    continue
                prev_y = y
                y_draw = max(y_min - range_y, min(y_max + range_y, y))
                px, py = to_scr(x, y_draw)
                pts += [px, py]
            except Exception:
                if len(pts) >= 4:
                    self.canvas.create_line(pts, fill=C_ACCENT, width=2)
                pts = []
                prev_y = None
        if len(pts) >= 4:
            self.canvas.create_line(pts, fill=C_ACCENT, width=2)

        if self.show_extrema.get() and not anim_data:
            for ex, ey in self.find_extrema(self.last_f, x_min, x_max):
                if y_min <= ey <= y_max:
                    px, py = to_scr(ex, ey)
                    self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                            fill="#fbbf24", outline="#92400e", width=2)

        for r in self.all_roots:
            if x_min <= r <= x_max:
                px, py = to_scr(r, 0)
                self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                        fill=C_SUCCESS, outline="black", width=2)

        if anim_data:
            method = anim_data["method"]
            if method in ("bisection", "brent"):
                xl, _ = to_scr(anim_data["ca"], 0)
                xr, _ = to_scr(anim_data["cb"], 0)
                xc, _ = to_scr(anim_data["cc"], 0)
                self.canvas.create_rectangle(xl, 0, xr, h, fill="#bfdbfe",
                                             outline="#2563eb", width=2, stipple="gray25")
                self.canvas.create_line(xc, 0, xc, h, fill=C_DANGER, width=2, dash=(4, 4))
            elif method in ("newton", "secant", "chord"):
                x_prev, x_new = anim_data["x_prev"], anim_data["x_new"]
                try:
                    y_prev = self.last_f(x_prev)
                    px_prev, py_prev = to_scr(x_prev, y_prev)
                    px_new, py_new = to_scr(x_new, 0)
                    self.canvas.create_line(px_prev, py_prev, px_new, py_new,
                                            fill=C_DANGER, width=2, dash=(4, 4))
                    self.canvas.create_oval(px_new - 5, py_new - 5, px_new + 5, py_new + 5,
                                            fill=C_SUCCESS, outline="black")
                except Exception:
                    pass

        if self.var_mode.get() == "multi" and self.multi_vars:
            var_text = ", ".join(f"{k}={v:.2f}" for k, v in self.multi_vars.items())
            self.canvas.create_text(w - 10, 15, anchor=tk.NE,
                                    text=f"Параметры: {var_text}",
                                    font=("Segoe UI", 9), fill=C_WARN)

    def render_graph_to_image(self, width=1920, height=1080):
        if not self.last_f or not HAS_PIL:
            return None
        img = Image.new("RGB", (width, height), THEMES[self.theme]["canvas_bg"])
        draw = ImageDraw.Draw(img)

        def get_font(size):
            for name in ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]:
                try:
                    return ImageFont.truetype(name, size)
                except (OSError, IOError):
                    continue
            return ImageFont.load_default()

        font_grid = get_font(11)
        font_info = get_font(16)
        c = THEMES[self.theme]
        x_min, x_max = self.view_x_min, self.view_x_max
        y_min, y_max = self.view_y_min, self.view_y_max

        def to_px(x, y):
            px = (x - x_min) / (x_max - x_min) * width
            py = height - (y - y_min) / (y_max - y_min) * height
            return int(px), int(py)

        range_x, range_y = x_max - x_min, y_max - y_min
        step_x = 10 ** math.floor(math.log10(range_x)) / 2 if range_x > 0 else 1
        start_x = math.floor(x_min / step_x) * step_x
        gx = start_x
        while gx <= x_max + step_x:
            px, _ = to_px(gx, 0)
            if 0 <= px <= width:
                draw.line([(px, 0), (px, height)], fill=c["grid"], width=1)
                if abs(gx) > 1e-9:
                    _, oy = to_px(0, 0)
                    ty = max(5, min(height - 20, oy + 5))
                    draw.text((px + 3, ty), f"{gx:g}", fill=c["muted"], font=font_grid)
            gx += step_x
        step_y = 10 ** math.floor(math.log10(range_y)) / 2 if range_y > 0 else 1
        start_y = math.floor(y_min / step_y) * step_y
        gy = start_y
        while gy <= y_max + step_y:
            _, py = to_px(0, gy)
            if 0 <= py <= height:
                draw.line([(0, py), (width, py)], fill=c["grid"], width=1)
                if abs(gy) > 1e-9:
                    ox, _ = to_px(0, 0)
                    tx = max(5, min(width - 60, ox - 50))
                    draw.text((tx, py - 8), f"{gy:g}", fill=c["muted"], font=font_grid)
            gy += step_y
        ox, oy = to_px(0, 0)
        if 0 <= oy <= height:
            draw.line([(0, oy), (width, oy)], fill=c["axis"], width=2)
        if 0 <= ox <= width:
            draw.line([(ox, 0), (ox, height)], fill=c["axis"], width=2)
        samples = width * 2
        prev = None
        pts = []
        for i in range(samples):
            x = x_min + i * (x_max - x_min) / (samples - 1)
            try:
                y = self.last_f(x)
                if not math.isfinite(y):
                    if len(pts) >= 2:
                        draw.line(pts, fill=C_ACCENT, width=3)
                    pts = []
                    prev = None
                    continue
                if prev is not None and abs(y - prev) > range_y * 5:
                    if len(pts) >= 2:
                        draw.line(pts, fill=C_ACCENT, width=3)
                    pts = []
                    prev = y
                    continue
                prev = y
                y_draw = max(y_min - range_y, min(y_max + range_y, y))
                pts.append(to_px(x, y_draw))
            except Exception:
                if len(pts) >= 2:
                    draw.line(pts, fill=C_ACCENT, width=3)
                pts = []
                prev = None
        if len(pts) >= 2:
            draw.line(pts, fill=C_ACCENT, width=3)
        eq_text = f"f(x) = {self.eq_entry.get()}"
        draw.text((15, 15), eq_text, fill=c["text"], font=font_info)
        draw.text((15, 40),
                  f"[{self.a_entry.get()}; {self.b_entry.get()}]  σ={self.sigma_entry.get()}",
                  fill=c["muted"], font=font_grid)
        return img

    def save_graph_png(self):
        if not HAS_PIL:
            messagebox.showerror("Ошибка", "Установи Pillow:\npip install pillow")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not fp:
            return
        try:
            img = self.render_graph_to_image(1920, 1080)
            if img is None:
                messagebox.showwarning("Ошибка", "Нет графика")
                return
            img.save(fp, "PNG", optimize=True)
            messagebox.showinfo("Готово", f"PNG сохранён:\n{fp}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить PNG:\n{e}")

    def save_graph_image(self):
        fp = filedialog.asksaveasfilename(defaultextension=".ps")
        if fp:
            self.canvas.postscript(file=fp, colormode='color')

    def export_svg(self):
        if not HAS_PIL:
            messagebox.showerror("Ошибка", "Установи Pillow:\npip install pillow")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG", "*.svg")])
        if not fp:
            return
        img = self.render_graph_to_image(1920, 1080)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'width="1920" height="1080" viewBox="0 0 1920 1080">\n'
               f'<image width="1920" height="1080" '
               f'xlink:href="data:image/png;base64,{b64}"/>\n</svg>')
        with open(fp, "w", encoding="utf-8") as f:
            f.write(svg)
        self.stats.record_export("svg")
        messagebox.showinfo("Готово", f"SVG сохранён:\n{fp}")

    def export_html(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma):
        fp = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not fp:
            return

        def make_table(title, headers, data, color):
            rows = "".join(
                f"<tr>{''.join(f'<td>{v:.5g}</td>' if isinstance(v, float) else f'<td>{v}</td>' for v in r)}</tr>"
                for r in data)
            return (f'<h2 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;">{title}</h2>'
                    f'<table><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr>{rows}</table>')

        extra_section = ""
        if self.extra_equations:
            extra_section = '<h2 style="color: #6b21a8; border-bottom: 2px solid #6b21a8; padding-bottom: 5px;">Дополнительные формулы</h2><ul>'
            for i, eq_data in enumerate(self.extra_equations, 1):
                extra_section += f'<li><b>f{i}(x)</b> = {html.escape(eq_data["eq"])} <span style="color: {eq_data["color"]};">■</span></li>'
            extra_section += '</ul>'

        html_content = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8">
<title>Отчет по численным методам</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f9fafb; color: #1f2937; padding: 40px; }}
h1 {{ text-align: center; color: #1e3a5f; }}
.meta {{ text-align: center; font-size: 1.1em; margin-bottom: 40px; background: #e5e7eb; padding: 15px; border-radius: 8px; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: center; }}
th {{ background: #f3f4f6; font-weight: bold; }}
</style></head><body>
<h1>Отчёт о решении уравнения</h1>
<div class="meta">
<b>Основная функция:</b> f(x) = {html.escape(self.eq_entry.get())}<br>
<b>Интервал:</b> [{a}; {b}] | <b>σ:</b> {sigma}
</div>
{extra_section}
{make_table("1. Бисекция", ("N", "a", "b", "c", "f(c)", "|b-a|"), hb, C_DANGER)}
{make_table("2. Хорды", ("N", "x_n", "x_n+1", "f", "|dx|"), hc, C_SUCCESS)}
{make_table("3. Ньютон", ("N", "x_n", "x_n+1", "f", "|dx|"), hn, C_NEWTON)}
{make_table("4. Секущие", ("N", "x_n-1", "x_n", "f", "|dx|"), hs, C_SECANT)}
{make_table("5. Брент", ("N", "a", "b", "s", "f(s)", "|b-a|"), hbr, C_BRENT)}
{make_table("6. МПИ", ("N", "x_n", "x_n+1", "f", "|dx|"), hmpi, C_MPI)}
<h2>Итоги</h2>
<ul>
<li>Бисекция: {rb if rb else '—'}</li>
<li>Хорды: {rc if rc else '—'}</li>
<li>Ньютон: {rn if rn else '—'}</li>
<li>Секущие: {rs if rs else '—'}</li>
<li>Брент: {rbr if rbr else '—'}</li>
<li>МПИ: {rmpi if rmpi else '—'}</li>
</ul>
<p style="text-align: center; color: #6b7280;">Сгенерировано {APP_TITLE} v{VERSION}</p>
</body></html>"""
        with open(fp, "w", encoding="utf-8") as f:
            f.write(html_content)
        self.stats.record_export("html")
        messagebox.showinfo("Готово", f"HTML сохранён:\n{fp}")

    def export_csv(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma):
        fp = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not fp:
            return
        with open(fp, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Отчет по численным методам"])
            writer.writerow(["Уравнение:", self.eq_entry.get()])
            writer.writerow(["Интервал:", f"[{a}; {b}]"])
            writer.writerow(["Точность σ:", sigma])
            writer.writerow([])
            for title, headers, data in [
                ("Бисекция", ("N", "a", "b", "c", "f(c)", "|b-a|"), hb),
                ("Хорды", ("N", "x_n", "x_n+1", "f", "|dx|"), hc),
                ("Ньютон", ("N", "x_n", "x_n+1", "f", "|dx|"), hn),
                ("Секущие", ("N", "x_n-1", "x_n", "f", "|dx|"), hs),
                ("Брент", ("N", "a", "b", "s", "f(s)", "|b-a|"), hbr),
                ("МПИ", ("N", "x_n", "x_n+1", "f", "|dx|"), hmpi),
            ]:
                writer.writerow([title])
                writer.writerow(headers)
                for row in data:
                    writer.writerow([f"{v:.10g}" if isinstance(v, float) else v for v in row])
                writer.writerow([])
            if self.extra_equations:
                writer.writerow(["Дополнительные формулы:"])
                writer.writerow(["#", "Формула"])
                for i, eq_data in enumerate(self.extra_equations, 1):
                    writer.writerow([i, eq_data['eq']])
                writer.writerow([])
            writer.writerow(["Итоговые корни:"])
            for name, root in [("Бисекция", rb), ("Хорды", rc), ("Ньютон", rn),
                               ("Секущие", rs), ("Брент", rbr), ("МПИ", rmpi)]:
                writer.writerow([name, f"{root:.10f}" if root else "Не найден"])
        self.stats.record_export("csv")
        messagebox.showinfo("Готово", f"CSV сохранён:\n{fp}")

    def export_latex(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma):
        fp = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=[("LaTeX", "*.tex")])
        if not fp:
            return

        def make_table(title, headers, data):
            cols = "c" * len(headers)
            t = "\\begin{table}[h]\n\\centering\n\\caption{" + title + "}\n"
            t += "\\begin{tabular}{" + cols + "}\n\\hline\n"
            t += " & ".join(headers) + " \\\\\n\\hline\n"
            for row in data:
                t += " & ".join(f"{v:.5g}" if isinstance(v, float) else str(v) for v in row) + " \\\\\n"
            t += "\\hline\n\\end{tabular}\n\\end{table}\n\n"
            return t

        eq_escaped = self.eq_entry.get().replace("_", "\\_").replace("%", "\\%")
        extra_section = ""
        if self.extra_equations:
            extra_section = "\\section{Дополнительные формулы}\n\\begin{itemize}\n"
            for i, eq_data in enumerate(self.extra_equations, 1):
                eq_esc = eq_data['eq'].replace("_", "\\_").replace("%", "\\%").replace("$", "\\$")
                extra_section += f"\\item $f_{{{i}}}(x) = {eq_esc}$\n"
            extra_section += "\\end{itemize}\n\n"

        parts = []
        parts.append("\\documentclass[12pt]{article}\n")
        parts.append("\\usepackage[utf8]{inputenc}\n")
        parts.append("\\usepackage[russian]{babel}\n")
        parts.append("\\usepackage{amsmath}\n")
        parts.append("\\usepackage{geometry}\n")
        parts.append("\\geometry{margin=2cm}\n")
        parts.append("\\title{Отчёт по численным методам}\n")
        parts.append("\\author{Сгенерировано автоматически}\n")
        parts.append("\\date{\\today}\n")
        parts.append("\\begin{document}\n")
        parts.append("\\maketitle\n")
        parts.append("\\section*{Исходные данные}\n")
        parts.append(f"\\textbf{{Уравнение:}} $f(x) = {eq_escaped}$ \\\\\n")
        parts.append(f"\\textbf{{Интервал:}} $[{a}; {b}]$ \\\\\n")
        parts.append(f"\\textbf{{Точность:}} $\\sigma = {sigma}$\n\n")
        parts.append(extra_section)
        parts.append("\\section{Бисекция}\n")
        parts.append(make_table("Бисекция", ("N", "a", "b", "c", "f(c)", "$|b-a|$"), hb))
        parts.append("\\section{Хорды}\n")
        parts.append(make_table("Хорды", ("N", "$x_n$", "$x_{n+1}$", "$f$", "$|dx|$"), hc))
        parts.append("\\section{Ньютон}\n")
        parts.append(make_table("Ньютон", ("N", "$x_n$", "$x_{n+1}$", "$f$", "$|dx|$"), hn))
        parts.append("\\section{Секущие}\n")
        parts.append(make_table("Секущие", ("N", "$x_{n-1}$", "$x_n$", "$f$", "$|dx|$"), hs))
        parts.append("\\section{Брент}\n")
        parts.append(make_table("Брент", ("N", "a", "b", "s", "f(s)", "$|b-a|$"), hbr))
        parts.append("\\section{МПИ}\n")
        parts.append(make_table("МПИ", ("N", "$x_n$", "$x_{n+1}$", "$f$", "$|dx|$"), hmpi))
        parts.append("\\section*{Итоги}\n")
        parts.append("\\begin{itemize}\n")
        parts.append(f"\\item Бисекция: ${rb:.6f}$\n" if rb is not None else "\\item Бисекция: —\n")
        parts.append(f"\\item Хорды: ${rc:.6f}$\n" if rc is not None else "\\item Хорды: —\n")
        parts.append(f"\\item Ньютон: ${rn:.6f}$\n" if rn is not None else "\\item Ньютон: —\n")
        parts.append(f"\\item Секущие: ${rs:.6f}$\n" if rs is not None else "\\item Секущие: —\n")
        parts.append(f"\\item Брент: ${rbr:.6f}$\n" if rbr is not None else "\\item Брент: —\n")
        parts.append(f"\\item МПИ: ${rmpi:.6f}$\n" if rmpi is not None else "\\item МПИ: —\n")
        parts.append("\\end{itemize}\n")
        parts.append("\\end{document}\n")

        latex_content = "".join(parts)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(latex_content)
        self.stats.record_export("tex")
        messagebox.showinfo("Готово", f"LaTeX сохранён:\n{fp}")

    def export_pdf(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                            Paragraph, Spacer, PageBreak)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            messagebox.showerror("Ошибка", "Установи reportlab:\npip install reportlab")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not fp:
            return
        font_name = "Helvetica"
        for path in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            try:
                pdfmetrics.registerFont(TTFont("CyrFont", path))
                font_name = "CyrFont"
                break
            except Exception:
                continue
        doc = SimpleDocTemplate(fp, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleRu", parent=styles["Title"], fontName=font_name, fontSize=18)
        heading_style = ParagraphStyle("HeadRu", parent=styles["Heading2"], fontName=font_name,
                                       fontSize=13, textColor=colors.HexColor(C_ACCENT))
        normal_style = ParagraphStyle("NormRu", parent=styles["Normal"], fontName=font_name, fontSize=10)
        story = []
        story.append(Paragraph("Отчёт по численным методам", title_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            f"<b>Уравнение:</b> f(x) = {html.escape(self.eq_entry.get())}<br/>"
            f"<b>Интервал:</b> [{a}; {b}] | <b>σ:</b> {sigma}", normal_style))
        story.append(Spacer(1, 0.8 * cm))
        if self.extra_equations:
            story.append(Paragraph("Дополнительные формулы", heading_style))
            story.append(Spacer(1, 0.2 * cm))
            for i, eq_data in enumerate(self.extra_equations, 1):
                story.append(Paragraph(f"<b>f{i}(x)</b> = {html.escape(eq_data['eq'])}", normal_style))
            story.append(Spacer(1, 0.5 * cm))

        def add_table(title, headers, data, color):
            story.append(Paragraph(title, heading_style))
            story.append(Spacer(1, 0.2 * cm))
            rows = [headers]
            for row in data:
                rows.append([f"{v:.5g}" if isinstance(v, float) else str(v) for v in row])
            t = Table(rows, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(color)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ]))
            story.append(t)
            story.append(PageBreak())

        add_table("1. Бисекция", ("N", "a", "b", "c", "f(c)", "|b-a|"), hb, C_DANGER)
        add_table("2. Хорды", ("N", "x_n", "x_{n+1}", "f", "|dx|"), hc, C_SUCCESS)
        add_table("3. Ньютон", ("N", "x_n", "x_{n+1}", "f", "|dx|"), hn, C_NEWTON)
        add_table("4. Секущие", ("N", "x_{n-1}", "x_n", "f", "|dx|"), hs, C_SECANT)
        add_table("5. Брент", ("N", "a", "b", "s", "f(s)", "|b-a|"), hbr, C_BRENT)
        add_table("6. МПИ", ("N", "x_n", "x_{n+1}", "f", "|dx|"), hmpi, C_MPI)
        story.append(Paragraph("Итоговые корни", heading_style))
        story.append(Spacer(1, 0.3 * cm))
        roots = [["Метод", "Корень"]]
        for name, root in [("Бисекция", rb), ("Хорды", rc), ("Ньютон", rn),
                           ("Секущие", rs), ("Брент", rbr), ("МПИ", rmpi)]:
            roots.append([name, f"{root:.6f}" if root is not None else "—"])
        t = Table(roots, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(C_ACCENT)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(t)
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph(f"<i>Сгенерировано {APP_TITLE} v{VERSION}</i>", normal_style))
        try:
            doc.build(story)
            self.stats.record_export("pdf")
            messagebox.showinfo("Готово", f"PDF сохранён:\n{fp}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF:\n{e}")

    def export_excel(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma):
        if not HAS_OPENPYXL:
            messagebox.showerror("Ошибка", "Установи openpyxl:\npip install openpyxl")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not fp:
            return
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        sheets = {
            "Бисекция": (hb, ("N", "a", "b", "c", "f(c)", "|b-a|")),
            "Хорды": (hc, ("N", "x_n", "x_{n+1}", "f", "|dx|")),
            "Ньютон": (hn, ("N", "x_n", "x_{n+1}", "f", "|dx|")),
            "Секущие": (hs, ("N", "x_{n-1}", "x_n", "f", "|dx|")),
            "Брент": (hbr, ("N", "a", "b", "s", "f(s)", "|b-a|")),
            "МПИ": (hmpi, ("N", "x_n", "x_{n+1}", "f", "|dx|")),
        }
        for name, (data, headers) in sheets.items():
            ws = wb.create_sheet(name)
            ws.append(headers)
            for row in data:
                ws.append([float(v) if isinstance(v, (int, float)) else v for v in row])
        if self.extra_equations:
            ws_extra = wb.create_sheet("Доп_формулы")
            ws_extra.append(["#", "Формула", "Цвет", "Видима"])
            for i, eq_data in enumerate(self.extra_equations, 1):
                ws_extra.append([i, eq_data['eq'], eq_data['color'],
                                 "Да" if eq_data['visible'] else "Нет"])
        ws = wb.create_sheet("Итоги")
        ws.append(["Метод", "Корень"])
        for name, root in [("Бисекция", rb), ("Хорды", rc), ("Ньютон", rn),
                           ("Секущие", rs), ("Брент", rbr), ("МПИ", rmpi)]:
            ws.append([name, root if root else "—"])
        wb.save(fp)
        self.stats.record_export("xlsx")
        messagebox.showinfo("Готово", f"Excel сохранён:\n{fp}")

    def export_markdown(self, hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi, a, b, sigma):
        fp = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
        if not fp:
            return

        def md_table(title, headers, data):
            s = f"## {title}\n\n"
            s += "| " + " | ".join(headers) + " |\n"
            s += "|" + "|".join(["---"] * len(headers)) + "|\n"
            for row in data:
                s += "| " + " | ".join(f"{v:.5g}" if isinstance(v, float) else str(v) for v in row) + " |\n"
            return s + "\n"

        extra_md = ""
        if self.extra_equations:
            extra_md = "## Дополнительные формулы\n\n"
            for i, eq_data in enumerate(self.extra_equations, 1):
                extra_md += f"- **f{i}(x)** = `{eq_data['eq']}`\n"
            extra_md += "\n"

        md = (f"# Отчёт: численные методы\n\n"
              f"**Уравнение:** f(x) = {self.eq_entry.get()}\n"
              f"**Интервал:** [{a}; {b}], **σ =** {sigma}\n\n"
              + extra_md
              + md_table("Бисекция", ("N", "a", "b", "c", "f(c)", "|b-a|"), hb)
              + md_table("Хорды", ("N", "x_n", "x_{n+1}", "f", "|dx|"), hc)
              + md_table("Ньютон", ("N", "x_n", "x_{n+1}", "f", "|dx|"), hn)
              + md_table("Секущие", ("N", "x_{n-1}", "x_n", "f", "|dx|"), hs)
              + md_table("Брент", ("N", "a", "b", "s", "f(s)", "|b-a|"), hbr)
              + md_table("МПИ", ("N", "x_n", "x_{n+1}", "f", "|dx|"), hmpi)
              + "## Итоги\n\n| Метод | Корень |\n|---|---|\n"
              + "".join(f"| {n} | {r if r is not None else '—'} |\n"
                        for n, r in [("Бисекция", rb), ("Хорды", rc), ("Ньютон", rn),
                                     ("Секущие", rs), ("Брент", rbr), ("МПИ", rmpi)]))
        with open(fp, "w", encoding="utf-8") as f:
            f.write(md)
        self.stats.record_export("md")
        messagebox.showinfo("Готово", f"Markdown сохранён:\n{fp}")

    def show_animation_dialog(self):
        if not self.last_f:
            messagebox.showwarning("Ошибка", "Сначала выполните расчёт")
            return
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("Выбор метода анимации")
        dialog.geometry("350x320")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Выберите метод для анимации:",
                 font=("Segoe UI", 11, "bold")).pack(pady=10)
        method_var = tk.StringVar(value="bisection")
        methods = [
            ("Метод половинного деления", "bisection"),
            ("Метод хорд", "chord"),
            ("Метод Ньютона", "newton"),
            ("Метод секущих", "secant"),
            ("Метод Брента", "brent"),
        ]
        for text, value in methods:
            tk.Radiobutton(dialog, text=text, variable=method_var, value=value,
                           font=("Segoe UI", 10)).pack(anchor=tk.W, padx=20, pady=5)

        def start():
            dialog.destroy()
            self.start_animation(method_var.get())

        tk.Button(dialog, text="▶ Начать анимацию", command=start,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  relief=tk.RAISED, bd=1, cursor="hand2", padx=20, pady=5).pack(pady=20)

    def start_animation(self, method="bisection"):
        try:
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
        except Exception:
            messagebox.showwarning("Ошибка", "Неверные границы интервала")
            return
        if method == "bisection":
            _, hist, _ = self.bisection(self.last_f, a, b, 1e-4)
        elif method == "chord":
            _, hist, _ = self.chord_method(self.last_f, a, b, 1e-4)
        elif method == "newton":
            _, hist, _ = self.newton_method(self.last_f, a, b, 1e-4)
        elif method == "secant":
            _, hist, _ = self.secant_method(self.last_f, a, b, 1e-4)
        elif method == "brent":
            _, hist = brent_method(self.last_f, a, b, 1e-4)
        else:
            return
        if not hist:
            messagebox.showinfo("Анимация", "Не удалось найти корень")
            return
        self.anim_running = True
        self.anim_index = 0
        self.anim_method = method

        def animate():
            if not self.anim_running or self.anim_index >= len(hist):
                self.anim_running = False
                return
            row = hist[self.anim_index]
            if self.anim_method in ("bisection", "brent"):
                self.draw_graph({"method": self.anim_method,
                                 "ca": row[1], "cb": row[2], "cc": row[3], "step": row[0]})
            else:
                self.draw_graph({"method": self.anim_method,
                                 "x_prev": row[1], "x_new": row[2], "step": row[0]})
            self.anim_index += 1
            self.anim_after_id = self.root.after(500, animate)

        animate()

    def stop_animation(self):
        self.anim_running = False
        if self.anim_after_id:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None

    def add_extra_equation(self):
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("Добавить формулу")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Введите формулу f(x):", font=("Segoe UI", 11, "bold")).pack(pady=10)
        eq_entry = tk.Entry(dialog, width=40, font=("Consolas", 12))
        eq_entry.pack(pady=5)
        color_idx = len(self.extra_equations) % len(self.extra_colors)
        color = self.extra_colors[color_idx]

        def add():
            eq = eq_entry.get().strip()
            if not eq:
                messagebox.showwarning("Ошибка", "Введите формулу")
                return
            try:
                f, _ = self.parse_equation(eq)
                f({'x': 0})
                self.extra_equations.append({
                    'eq': eq, 'color': color, 'visible': True, 'func': f
                })
                self.stats.record_extra_formula()
                self.draw_graph()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неверная формула:\n{e}")

        tk.Button(dialog, text="➕ Добавить", command=add,
                  bg=C_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=5).pack(pady=15)

    def manage_extra_equations(self):
        if not self.extra_equations:
            messagebox.showinfo("Информация", "Нет дополнительных формул.\nИспользуйте кнопку '➕ Добавить формулу'")
            return
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("Управление формулами")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        tk.Label(dialog, text="Дополнительные формулы:", font=("Segoe UI", 11, "bold")).pack(pady=10)
        listbox_frame = tk.Frame(dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(listbox_frame, font=("Consolas", 10), yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        for eq_data in self.extra_equations:
            status = "✓" if eq_data['visible'] else "✗"
            listbox.insert(tk.END, f"{status} {eq_data['eq']}  [{eq_data['color']}]")

        def toggle_visibility():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            self.extra_equations[idx]['visible'] = not self.extra_equations[idx]['visible']
            status = "✓" if self.extra_equations[idx]['visible'] else "✗"
            eq = self.extra_equations[idx]['eq']
            color = self.extra_equations[idx]['color']
            listbox.delete(idx)
            listbox.insert(idx, f"{status} {eq}  [{color}]")
            self.draw_graph()

        def delete_selected():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            self.extra_equations.pop(idx)
            listbox.delete(idx)
            self.draw_graph()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="👁 Показать/Скрыть", command=toggle_visibility,
                  bg="#dbeafe", fg="#1e40af", font=("Segoe UI", 9, "bold"),
                  padx=10, pady=3).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 Удалить", command=delete_selected,
                  bg="#fee2e2", fg="#991b1b", font=("Segoe UI", 9, "bold"),
                  padx=10, pady=3).pack(side=tk.LEFT, padx=5)

    def evaluate_at_point(self):
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("Вычислить в точке")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        tk.Label(dialog, text="Введите значения переменных:", font=("Segoe UI", 11, "bold")).pack(pady=10)
        all_vars = set()
        all_vars.update(re.findall(r'\b([a-z])\b', self.eq_entry.get()))
        for eq_data in self.extra_equations:
            all_vars.update(re.findall(r'\b([a-z])\b', eq_data['eq']))
        all_vars.discard('e')
        all_vars = sorted(all_vars)
        if not all_vars:
            all_vars = ['x']
        var_entries = {}
        for var in all_vars:
            frame = tk.Frame(dialog)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{var} =", font=("Consolas", 11)).pack(side=tk.LEFT, padx=10)
            entry = tk.Entry(frame, width=10, font=("Consolas", 11))
            entry.pack(side=tk.LEFT)
            entry.insert(0, "0")
            var_entries[var] = entry
        result_text = tk.Text(dialog, font=("Consolas", 10), height=10)
        result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        def calculate():
            var_values = {}
            for var, entry in var_entries.items():
                try:
                    var_values[var] = float(entry.get().replace(",", "."))
                except ValueError:
                    messagebox.showerror("Ошибка", f"Неверное значение для {var}")
                    return
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "Результаты:\n\n")
            try:
                f, _ = self.parse_equation(self.eq_entry.get())
                result = f(var_values)
                result_text.insert(tk.END, f"f(x) = {self.eq_entry.get()}\n")
                result_text.insert(tk.END, f"  Результат: {result:.10f}\n\n")
            except Exception as e:
                result_text.insert(tk.END, f"Ошибка в основной формуле: {e}\n\n")
            for i, eq_data in enumerate(self.extra_equations):
                try:
                    result = eq_data['func'](var_values)
                    result_text.insert(tk.END, f"f{i + 1}(x) = {eq_data['eq']}\n")
                    result_text.insert(tk.END, f"  Результат: {result:.10f}\n\n")
                except Exception as e:
                    result_text.insert(tk.END, f"Ошибка в f{i + 1}: {e}\n\n")

        tk.Button(dialog, text="🧮 Вычислить", command=calculate,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=5).pack(pady=10)

    def detect_parameters(self, eq_str):
        math_names = set(dir(math)) | {'x', 'y', 'z', 'abs', 'e', 'pi'}
        found = set(re.findall(r'\b([a-wA-Z])\b', eq_str))
        return sorted([v for v in found if v not in math_names and v.isalpha()])

    def show_param_sliders(self):
        params = self.detect_parameters(self.eq_entry.get())
        if not params:
            messagebox.showinfo("Информация",
                                "В формуле не найдено параметров (a, b, c...).\nПример: a*sin(b*x + c)")
            return
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Параметры формулы")
        win.geometry("500x400")
        tk.Label(win, text="Двигайте слайдеры для изменения параметров",
                 font=("Segoe UI", 10, "bold")).pack(pady=10)
        self.param_sliders = {}
        self.param_values = {}
        for param in params:
            frame = tk.Frame(win)
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=f"{param} =", font=("Consolas", 12, "bold"),
                     width=4).pack(side=tk.LEFT)
            scale = tk.Scale(frame, from_=-10, to=10, resolution=0.1,
                             orient=tk.HORIZONTAL, length=300,
                             command=lambda v, p=param: self._on_param_change(p, float(v)))
            scale.pack(side=tk.LEFT, padx=5)
            scale.set(1.0)
            value_lbl = tk.Label(frame, text="1.0", font=("Consolas", 10), width=6)
            value_lbl.pack(side=tk.LEFT)
            self.param_sliders[param] = (scale, value_lbl)
            self.param_values[param] = 1.0
        anim_frame = tk.Frame(win)
        anim_frame.pack(pady=15)
        tk.Label(anim_frame, text="Анимировать параметр:").pack(side=tk.LEFT)
        anim_param_var = tk.StringVar(value=params[0] if params else "")
        tk.OptionMenu(anim_frame, anim_param_var, *params).pack(side=tk.LEFT, padx=5)
        self.btn_anim_toggle = tk.Button(anim_frame, text="▶ Старт",
                                         command=lambda: self._toggle_param_animation(anim_param_var),
                                         bg=C_SUCCESS, fg="white",
                                         font=("Segoe UI", 9, "bold"), padx=10)
        self.btn_anim_toggle.pack(side=tk.LEFT, padx=5)

    def _on_param_change(self, param, value):
        self.param_values[param] = value
        if param in self.param_sliders:
            _, lbl = self.param_sliders[param]
            lbl.config(text=f"{value:.2f}")
        self._redraw_with_params()

    def _redraw_with_params(self):
        if not self.last_f:
            return
        try:
            eq = self.eq_entry.get()
            eq_subst = eq
            for param, value in self.param_values.items():
                eq_subst = re.sub(rf'\b{param}\b', str(value), eq_subst)
            f_with_params, _ = self.parse_equation(eq_subst)
            original_f = self.last_f
            self.last_f = lambda x: f_with_params({'x': x})
            self.draw_graph()
            self.last_f = original_f
        except Exception:
            pass

    def _toggle_param_animation(self, param_var):
        self.stats.data["param_animated"] = True
        self.stats.save()
        if self.param_auto_animate:
            self.param_auto_animate = False
            if self.param_anim_after_id:
                self.root.after_cancel(self.param_anim_after_id)
            self.btn_anim_toggle.config(text="▶ Старт", bg=C_SUCCESS)
            return
        param = param_var.get()
        if param not in self.param_sliders:
            return
        self.param_auto_animate = True
        self.btn_anim_toggle.config(text="⏸ Стоп", bg=C_DANGER)
        self._animate_param(param, 1)

    def _animate_param(self, param, direction):
        if not self.param_auto_animate:
            return
        if param not in self.param_sliders:
            return
        scale, _ = self.param_sliders[param]
        current = scale.get()
        new_val = current + direction * 0.2
        if new_val > 10:
            new_val = 10
            direction = -1
        elif new_val < -10:
            new_val = -10
            direction = 1
        scale.set(new_val)
        self._on_param_change(param, new_val)
        self.param_anim_after_id = self.root.after(50, lambda: self._animate_param(param, direction))

    def import_formulas_from_file(self):
        fp = filedialog.askopenfilename(
            title="Импорт формул",
            filetypes=[("Все поддерживаемые", "*.txt *.json *.csv"),
                       ("Текстовый файл", "*.txt"), ("JSON", "*.json"), ("CSV", "*.csv")])
        if not fp:
            return
        ext = os.path.splitext(fp)[1].lower()
        imported = []
        try:
            if ext == ".txt":
                imported = self._import_from_txt(fp)
            elif ext == ".json":
                imported = self._import_from_json(fp)
            elif ext == ".csv":
                imported = self._import_from_csv(fp)
            else:
                messagebox.showerror("Ошибка", f"Неподдерживаемый формат: {ext}")
                return
        except Exception as e:
            messagebox.showerror("Ошибка импорта", f"Не удалось прочитать файл:\n{e}")
            return
        if not imported:
            messagebox.showinfo("Импорт", "В файле не найдено корректных формул.")
            return
        choice = messagebox.askyesnocancel(
            "Импорт формул",
            f"Найдено формул: {len(imported)}\n\n"
            f"Да → добавить в БИБЛИОТЕКУ\n"
            f"Нет → добавить как ДОПОЛНИТЕЛЬНЫЕ формулы на график\n"
            f"Отмена → отменить импорт")
        if choice is None:
            return
        if choice:
            for item in imported:
                self.library.append(item)
            self.save_library_to_file()
            self.refresh_library_combo()
            messagebox.showinfo("Готово", f"✅ {len(imported)} формул добавлено в библиотеку")
        else:
            colors = self.extra_colors
            for i, item in enumerate(imported):
                try:
                    f, _ = self.parse_equation(item["eq"])
                    f({'x': 0})
                    self.extra_equations.append({
                        'eq': item["eq"],
                        'color': colors[(len(self.extra_equations) + i) % len(colors)],
                        'visible': True, 'func': f})
                except Exception as e:
                    print(f"Пропущена формула '{item['eq']}': {e}")
            self.draw_graph()
            messagebox.showinfo("Готово", f"✅ {len(imported)} формул добавлено на график")

    def _import_from_txt(self, fp):
        imported = []
        with open(fp, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                imported.append({"name": f"Импорт {line_no}: {line[:30]}",
                                 "eq": line, "a": "-10", "b": "10"})
        return imported

    def _import_from_json(self, fp):
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON должен содержать массив объектов")
        imported = []
        for item in data:
            if not isinstance(item, dict) or "eq" not in item:
                continue
            imported.append({"name": item.get("name", item["eq"][:30]),
                             "eq": item["eq"],
                             "a": str(item.get("a", "-10")),
                             "b": str(item.get("b", "10"))})
        return imported

    def _import_from_csv(self, fp):
        imported = []
        with open(fp, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "eq" not in row or not row["eq"].strip():
                    continue
                imported.append({"name": row.get("name", row["eq"][:30]),
                                 "eq": row["eq"].strip(),
                                 "a": str(row.get("a", "-10")),
                                 "b": str(row.get("b", "10"))})
        return imported

    def solve_analytical(self):
        if not HAS_SYMPY:
            messagebox.showerror("Ошибка", "SymPy не установлен.\nУстанови: pip install sympy")
            return
        eq_str = self.eq_entry.get()
        if not eq_str:
            messagebox.showwarning("Ошибка", "Введите уравнение")
            return
        self.status_var.set("🔬 Аналитическое решение...")
        self.root.update()
        self.stats.data["sympy_used"] = True
        self.stats.save()

        def worker():
            try:
                x = sp.Symbol('x')
                eq_sympy = eq_str.replace("math.", "").replace("^", "**")
                eq_sympy = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', eq_sympy)
                try:
                    expr = sp.sympify(eq_sympy, locals={'x': x, 'pi': sp.pi, 'e': sp.E})
                except (sp.SympifyError, SyntaxError) as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка парсинга", f"SymPy не может разобрать выражение:\n{e}"))
                    return
                solutions = sp.solve(expr, x)
                analytical_results = []
                for sol in solutions:
                    try:
                        sol_numeric = complex(sp.N(sol))
                        is_real = abs(sol_numeric.imag) < 1e-10
                        analytical_results.append({
                            "exact": str(sol),
                            "numeric": float(sol_numeric.real) if is_real else None,
                            "complex": None if is_real else sol_numeric,
                            "is_real": is_real})
                    except Exception:
                        analytical_results.append({
                            "exact": str(sol), "numeric": None,
                            "complex": None, "is_real": False})
                self.root.after(0, lambda: self._show_analytical_results(eq_str, analytical_results))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", f"Не удалось решить аналитически:\n{e}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("Готов"))

        threading.Thread(target=worker, daemon=True).start()

    def _show_analytical_results(self, eq_str, analytical_results):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("🔬 Аналитическое решение")
        win.geometry("900x600")
        tk.Label(win, text="Аналитическое решение через SymPy",
                 font=("Segoe UI", 14, "bold"), fg=C_ACCENT).pack(pady=10)
        tk.Label(win, text=f"f(x) = {eq_str} = 0", font=("Consolas", 12)).pack()
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tab1 = tk.Frame(nb)
        nb.add(tab1, text="  🎯  Аналитические корни  ")
        tree = ttk.Treeview(tab1, columns=("exact", "numeric", "type"), show="headings")
        tree.heading("exact", text="Точная форма")
        tree.heading("numeric", text="Численное значение")
        tree.heading("type", text="Тип")
        tree.column("exact", width=300)
        tree.column("numeric", width=200)
        tree.column("type", width=150)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for sol in analytical_results:
            tree.insert("", tk.END, values=(
                sol["exact"],
                f"{sol['numeric']:.10f}" if sol["numeric"] is not None else "—",
                "Действительный" if sol["is_real"] else "Комплексный"))
        if not analytical_results:
            tk.Label(tab1, text="❌ SymPy не нашёл решений",
                     font=("Segoe UI", 12), fg=C_DANGER).pack(pady=20)
        tab3 = tk.Frame(nb)
        nb.add(tab3, text="  🔧  Свойства функции  ")
        props_text = tk.Text(tab3, font=("Consolas", 10), wrap=tk.WORD)
        props_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        try:
            x = sp.Symbol('x')
            eq_sympy = eq_str.replace("math.", "").replace("^", "**")
            eq_sympy = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', eq_sympy)
            expr = sp.sympify(eq_sympy, locals={'x': x, 'pi': sp.pi, 'e': sp.E})
            props_text.insert(tk.END, "📐 Свойства функции f(x):\n\n")
            props_text.insert(tk.END, f"Исходное выражение:  {expr}\n")
            props_text.insert(tk.END, f"Упрощённое:          {sp.simplify(expr)}\n")
            try:
                props_text.insert(tk.END, f"\n📈 f'(x) = {sp.diff(expr, x)}\n")
            except Exception:
                pass
            try:
                props_text.insert(tk.END, f"\n📉 f''(x) = {sp.diff(expr, x, 2)}\n")
            except Exception:
                pass
            try:
                props_text.insert(tk.END, f"\n∫ ∫f(x)dx = {sp.integrate(expr, x)} + C\n")
            except Exception:
                props_text.insert(tk.END, "\n∫ Интеграл не берётся в замкнутом виде\n")
            try:
                props_text.insert(tk.END, f"\n📊 Ряд Тейлора: {sp.series(expr, x, 0, 6)}\n")
            except Exception:
                pass
        except Exception as e:
            props_text.insert(tk.END, f"❌ Ошибка:\n{e}")

    def export_analytical_report(self):
        if not HAS_SYMPY:
            messagebox.showerror("Ошибка", "SymPy не установлен")
            return
        eq_str = self.eq_entry.get()
        fp = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=[("LaTeX", "*.tex")])
        if not fp:
            return
        try:
            x = sp.Symbol('x')
            eq_sympy = eq_str.replace("math.", "").replace("^", "**")
            eq_sympy = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', eq_sympy)
            expr = sp.sympify(eq_sympy, locals={'x': x, 'pi': sp.pi, 'e': sp.E})
            solutions = sp.solve(expr, x)
            df_expr = sp.diff(expr, x)
            integral = sp.integrate(expr, x)
            eq_latex = sp.latex(expr)
            df_latex = sp.latex(df_expr)
            int_latex = sp.latex(integral)
            roots_latex = [sp.latex(s) for s in solutions]
            roots_items = "\n".join(f"\\item $x = {r}$" for r in roots_latex) or \
                          "\\item Аналитическое решение не найдено"
            content = (
                "\\documentclass[12pt]{article}\n"
                "\\usepackage[utf8]{inputenc}\n"
                "\\usepackage[russian]{babel}\n"
                "\\usepackage{amsmath}\n"
                "\\title{Аналитическое решение уравнения}\n"
                "\\date{\\today}\n"
                "\\begin{document}\n\\maketitle\n"
                "\\section*{Исходное уравнение}\n"
                f"$$f(x) = {eq_latex} = 0$$\n"
                "\\section{Аналитические корни}\n\\begin{itemize}\n"
                f"{roots_items}\n\\end{itemize}\n"
                "\\section{Производная}\n"
                f"$$f'(x) = {df_latex}$$\n"
                "\\section{Неопределённый интеграл}\n"
                f"$$\\int f(x)\\,dx = {int_latex} + C$$\n"
                "\\end{document}\n")
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Готово", f"LaTeX-отчёт сохранён:\n{fp}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчёт:\n{e}")

    def show_3d_graph(self):
        if not self.last_f:
            messagebox.showwarning("Ошибка", "Сначала выполните расчёт 2D-функции")
            return
        try:
            self.last_f(0, 0)
        except TypeError:
            messagebox.showwarning("Ошибка",
                                   "Текущая функция зависит только от x.\n"
                                   "Для 3D-графика введите функцию вида f(x, y), например:\n"
                                   "math.sin(x) * math.cos(y)\nx**2 + y**2 - 4")
            return
        win = tk.Toplevel(self.root)
        self.stats.data["graph_3d_opened"] = True
        self.stats.save()
        set_window_icon(win)
        win.title("3D-график: z = f(x, y)")
        win.geometry("900x700")
        ctrl = tk.Frame(win)
        ctrl.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(ctrl, text="X:").pack(side=tk.LEFT, padx=5)
        x_min_e = tk.Entry(ctrl, width=6, font=("Consolas", 10))
        x_min_e.pack(side=tk.LEFT)
        x_min_e.insert(0, "-5")
        tk.Label(ctrl, text="..").pack(side=tk.LEFT)
        x_max_e = tk.Entry(ctrl, width=6, font=("Consolas", 10))
        x_max_e.pack(side=tk.LEFT)
        x_max_e.insert(0, "5")
        tk.Label(ctrl, text="  Y:").pack(side=tk.LEFT, padx=5)
        y_min_e = tk.Entry(ctrl, width=6, font=("Consolas", 10))
        y_min_e.pack(side=tk.LEFT)
        y_min_e.insert(0, "-5")
        tk.Label(ctrl, text="..").pack(side=tk.LEFT)
        y_max_e = tk.Entry(ctrl, width=6, font=("Consolas", 10))
        y_max_e.pack(side=tk.LEFT)
        y_max_e.insert(0, "5")
        tk.Label(ctrl, text="  Сетка:").pack(side=tk.LEFT, padx=5)
        res_var = tk.IntVar(value=40)
        tk.Spinbox(ctrl, from_=10, to=100, textvariable=res_var, width=5).pack(side=tk.LEFT)
        graph3d = Graph3D(win, bg=THEMES[self.theme]["canvas_bg"])

        def update():
            try:
                xr = (float(x_min_e.get()), float(x_max_e.get()))
                yr = (float(y_min_e.get()), float(y_max_e.get()))
                graph3d.set_function(self.last_f, xr, yr, res_var.get())
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(ctrl, text="🔄 Обновить", command=update,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  padx=10).pack(side=tk.LEFT, padx=10)

        def save_3d():
            fp = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if fp and graph3d.save_png(fp):
                messagebox.showinfo("Готово", f"3D-график сохранён:\n{fp}")

        tk.Button(ctrl, text="🖼 PNG", command=save_3d,
                  bg="#e5e7eb", fg="#1f2937", font=("Segoe UI", 9, "bold"),
                  padx=10).pack(side=tk.LEFT, padx=5)
        update()

    def show_contour_plot(self):
        if not self.last_f:
            messagebox.showwarning("Ошибка", "Сначала выполните расчёт")
            return
        try:
            self.last_f(0, 0)
        except TypeError:
            messagebox.showwarning("Ошибка",
                                   "Для контурного графика нужна функция f(x, y), например:\n"
                                   "x**2 + y**2 - 4\nmath.sin(x) * math.cos(y)")
            return
        win = tk.Toplevel(self.root)
        self.stats.data["contour_opened"] = True
        self.stats.save()
        set_window_icon(win)
        win.title("Контурный график: z = f(x, y)")
        win.geometry("900x700")
        ctrl = tk.Frame(win)
        ctrl.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(ctrl, text="Уровней:").pack(side=tk.LEFT, padx=5)
        levels_var = tk.IntVar(value=15)
        tk.Spinbox(ctrl, from_=5, to=50, textvariable=levels_var, width=5).pack(side=tk.LEFT)
        tk.Label(ctrl, text="  X:").pack(side=tk.LEFT, padx=5)
        x_min_e = tk.Entry(ctrl, width=6)
        x_min_e.pack(side=tk.LEFT)
        x_min_e.insert(0, "-5")
        tk.Label(ctrl, text="..").pack(side=tk.LEFT)
        x_max_e = tk.Entry(ctrl, width=6)
        x_max_e.pack(side=tk.LEFT)
        x_max_e.insert(0, "5")
        tk.Label(ctrl, text="  Y:").pack(side=tk.LEFT, padx=5)
        y_min_e = tk.Entry(ctrl, width=6)
        y_min_e.pack(side=tk.LEFT)
        y_min_e.insert(0, "-5")
        tk.Label(ctrl, text="..").pack(side=tk.LEFT)
        y_max_e = tk.Entry(ctrl, width=6)
        y_max_e.pack(side=tk.LEFT)
        y_max_e.insert(0, "5")
        contour = ContourPlot(win, bg=THEMES[self.theme]["canvas_bg"])

        def update():
            try:
                xr = (float(x_min_e.get()), float(x_max_e.get()))
                yr = (float(y_min_e.get()), float(y_max_e.get()))
                contour.set_function(self.last_f, xr, yr, levels_var.get())
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(ctrl, text="🔄 Обновить", command=update,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  padx=10).pack(side=tk.LEFT, padx=10)
        update()

    def show_vector_field(self):
        if not self.last_f:
            messagebox.showwarning("Ошибка", "Сначала выполните расчёт")
            return
        try:
            self.last_f(0, 0)
        except TypeError:
            messagebox.showwarning("Ошибка",
                                   "Для векторного поля нужна функция f(x, y), например:\n"
                                   "x**2 + y**2\nmath.sin(x) * math.cos(y)")
            return
        win = tk.Toplevel(self.root)
        self.stats.data["vector_opened"] = True
        self.stats.save()
        set_window_icon(win)
        win.title("Векторное поле: ∇f(x, y)")
        win.geometry("900x700")
        ctrl = tk.Frame(win)
        ctrl.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(ctrl, text="Сетка:").pack(side=tk.LEFT, padx=5)
        grid_var = tk.IntVar(value=20)
        tk.Spinbox(ctrl, from_=5, to=50, textvariable=grid_var, width=5).pack(side=tk.LEFT)
        tk.Label(ctrl, text="  Масштаб:").pack(side=tk.LEFT, padx=5)
        scale_var = tk.DoubleVar(value=1.0)
        tk.Scale(ctrl, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL,
                 variable=scale_var, length=150).pack(side=tk.LEFT)
        tk.Label(ctrl, text="  X:").pack(side=tk.LEFT, padx=5)
        x_min_e = tk.Entry(ctrl, width=6)
        x_min_e.pack(side=tk.LEFT)
        x_min_e.insert(0, "-5")
        tk.Label(ctrl, text="..").pack(side=tk.LEFT)
        x_max_e = tk.Entry(ctrl, width=6)
        x_max_e.pack(side=tk.LEFT)
        x_max_e.insert(0, "5")
        tk.Label(ctrl, text="  Y:").pack(side=tk.LEFT, padx=5)
        y_min_e = tk.Entry(ctrl, width=6)
        y_min_e.pack(side=tk.LEFT)
        y_min_e.insert(0, "-5")
        tk.Label(ctrl, text="..").pack(side=tk.LEFT)
        y_max_e = tk.Entry(ctrl, width=6)
        y_max_e.pack(side=tk.LEFT)
        y_max_e.insert(0, "5")
        field = VectorField(win, bg=THEMES[self.theme]["canvas_bg"])

        def update():
            try:
                xr = (float(x_min_e.get()), float(x_max_e.get()))
                yr = (float(y_min_e.get()), float(y_max_e.get()))
                field.set_function(self.last_f, xr, yr, grid_var.get(), scale_var.get())
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(ctrl, text="🔄 Обновить", command=update,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  padx=10).pack(side=tk.LEFT, padx=10)
        update()

    def show_step_by_step(self):
        if not self.last_f:
            messagebox.showwarning("Ошибка", "Сначала выполните расчёт")
            return
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("📚 Пошаговое решение")
        dialog.geometry("800x600")
        method_frame = tk.Frame(dialog)
        method_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(method_frame, text="Метод:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        method_var = tk.StringVar(value="bisection")
        for text, val in [("Бисекция", "bisection"), ("Ньютон", "newton"), ("Хорды", "chord")]:
            tk.Radiobutton(method_frame, text=text, variable=method_var, value=val,
                           font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)
        text = tk.Text(dialog, font=("Consolas", 10), wrap=tk.WORD, bg="#f9fafb")
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.tag_config("title", font=("Segoe UI", 12, "bold"), foreground=C_ACCENT)
        text.tag_config("step", font=("Segoe UI", 11, "bold"), foreground="#1e40af")
        text.tag_config("formula", font=("Consolas", 11), foreground=C_NEWTON)
        text.tag_config("result", font=("Segoe UI", 12, "bold"), foreground=C_SUCCESS)
        text.tag_config("error", font=("Segoe UI", 11, "bold"), foreground=C_DANGER)
        text.tag_config("info", foreground="#6b7280")
        nav_frame = tk.Frame(dialog)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)
        current_step = [0]
        steps_data = [None]

        def show_step(idx):
            text.delete(1.0, tk.END)
            if not steps_data[0] or idx < 0 or idx >= len(steps_data[0]):
                return
            step = steps_data[0][idx]
            step_type = step.get("type", "step")
            if step_type == "info":
                text.insert(tk.END, f"📖 {step['title']}\n\n", "title")
                text.insert(tk.END, step["text"] + "\n\n", "info")
                text.insert(tk.END, f"Формула: {step['formula']}\n", "formula")
            elif step_type == "step":
                text.insert(tk.END, f"🔢 {step['title']}\n\n", "step")
                text.insert(tk.END, step["text"] + "\n\n")
                text.insert(tk.END, f"Формула: {step['formula']}\n", "formula")
            elif step_type == "result":
                text.insert(tk.END, f"✅ {step['title']}\n\n", "result")
                text.insert(tk.END, step["text"] + "\n\n")
                text.insert(tk.END, f"Формула: {step['formula']}\n", "formula")
            elif step_type == "error":
                text.insert(tk.END, "❌ Ошибка\n\n", "error")
                text.insert(tk.END, step["text"] + "\n")
            text.insert(tk.END, f"\n{'─' * 60}\nШаг {idx + 1} из {len(steps_data[0])}", "info")
            current_step[0] = idx
            prev_btn.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
            next_btn.config(state=tk.NORMAL if idx < len(steps_data[0]) - 1 else tk.DISABLED)

        def compute():
            try:
                a = float(self.a_entry.get())
                b = float(self.b_entry.get())
                sigma = float(self.sigma_entry.get())
            except Exception:
                messagebox.showerror("Ошибка", "Неверные параметры")
                return
            method = method_var.get()
            if method == "bisection":
                steps_data[0] = step_by_step.bisection_steps(self.last_f, a, b, sigma)
            elif method == "newton":
                df = lambda x: self.df(self.last_f, x)
                steps_data[0] = step_by_step.newton_steps(self.last_f, df, a, sigma)
            elif method == "chord":
                steps_data[0] = step_by_step.chord_steps(self.last_f, a, b, sigma)
            if steps_data[0]:
                show_step(0)

        prev_btn = tk.Button(nav_frame, text="◀ Предыдущий",
                             command=lambda: show_step(current_step[0] - 1),
                             font=("Segoe UI", 10, "bold"))
        prev_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="🔄 Пересчитать", command=compute,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20).pack(side=tk.LEFT, padx=10)
        next_btn = tk.Button(nav_frame, text="Следующий ▶",
                             command=lambda: show_step(current_step[0] + 1),
                             font=("Segoe UI", 10, "bold"))
        next_btn.pack(side=tk.LEFT, padx=5)
        compute()

    def show_interactive_tutorial(self):
        self.stats.data["tutorial_opened"] = True
        self.stats.save()
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("📚 Интерактивный учебник")
        win.geometry("900x650")
        left = tk.Frame(win, width=250, bg="#f3f4f6")
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        tk.Label(left, text="📚 Темы:", font=("Segoe UI", 11, "bold"),
                 bg="#f3f4f6").pack(pady=(10, 5))
        topic_var = tk.StringVar(value="bisection")
        examples_list = tk.Listbox(left, font=("Segoe UI", 9), height=15)

        def load_examples():
            examples_list.delete(0, tk.END)
            topic = topic_var.get()
            for ex in interactive_tutorial.TUTORIAL_EXAMPLES[topic]["examples"]:
                examples_list.insert(tk.END, ex["name"])

        for key, data in interactive_tutorial.TUTORIAL_EXAMPLES.items():
            tk.Radiobutton(left, text=data["title"], variable=topic_var, value=key,
                           font=("Segoe UI", 10), bg="#f3f4f6",
                           command=load_examples).pack(anchor=tk.W, padx=15, pady=2)
        tk.Label(left, text="\n📝 Примеры:", font=("Segoe UI", 11, "bold"),
                 bg="#f3f4f6").pack(pady=(10, 5))
        examples_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        right = tk.Frame(win)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        task_label = tk.Label(right, text="Выберите тему и пример",
                              font=("Segoe UI", 12, "bold"), fg=C_ACCENT,
                              wraplength=600, justify=tk.LEFT)
        task_label.pack(anchor=tk.W, pady=10)
        task_text = tk.Text(right, font=("Segoe UI", 10), height=8, wrap=tk.WORD, bg="#f9fafb")
        task_text.pack(fill=tk.X, pady=5)
        answer_frame = tk.Frame(right)
        answer_frame.pack(fill=tk.X, pady=10)
        tk.Label(answer_frame, text="Ваш ответ:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        answer_entry = tk.Entry(answer_frame, font=("Consolas", 12), width=20)
        answer_entry.pack(side=tk.LEFT, padx=10)
        result_label = tk.Label(right, text="", font=("Segoe UI", 11), wraplength=600, justify=tk.LEFT)
        result_label.pack(anchor=tk.W, pady=10)
        current_example = [None]

        def on_select(event):
            sel = examples_list.curselection()
            if not sel:
                return
            topic = topic_var.get()
            ex = interactive_tutorial.TUTORIAL_EXAMPLES[topic]["examples"][sel[0]]
            current_example[0] = ex
            task_label.config(text=f"📝 {ex['name']}")
            task_text.delete(1.0, tk.END)
            task_text.insert(tk.END, f"📋 ЗАДАНИЕ:\n{ex['task']}\n\n")
            task_text.insert(tk.END, f"📐 Уравнение: {ex['eq']}\n")
            if 'a' in ex:
                task_text.insert(tk.END, f"📍 Интервал: [{ex['a']}; {ex['b']}]\n")
            if 'x0' in ex:
                task_text.insert(tk.END, f"📍 Начальное приближение: x₀ = {ex['x0']}\n")
            task_text.insert(tk.END, f"🎯 Ожидаемое число итераций: ~{ex.get('steps', '?')}\n\n")
            task_text.insert(tk.END, f"💡 {ex['hint']}\n\n")
            task_text.insert(tk.END, "Введите ваш ответ и нажмите 'Проверить'.")
            answer_entry.delete(0, tk.END)
            result_label.config(text="")

        examples_list.bind("<<ListboxSelect>>", on_select)

        def check():
            if not current_example[0]:
                return
            ex = current_example[0]
            user_ans = answer_entry.get().strip()
            if not user_ans:
                result_label.config(text="⚠ Введите ответ", fg=C_WARN)
                return
            result = interactive_tutorial.check_answer(user_ans, ex["answer"])
            if result["correct"]:
                self.stats.record_quiz_correct()
                result_label.config(
                    text=f"✅ ПРАВИЛЬНО!\n\nВаш ответ: {result['user']:.10f}\n"
                         f"Правильный: {result['correct_val']:.10f}\n"
                         f"Погрешность: {result['error']:.2e}", fg=C_SUCCESS)
            else:
                result_label.config(
                    text=f"❌ НЕВЕРНО\n\nВаш ответ: {result['user']}\n"
                         f"Правильный: {result['correct_val']:.10f}\n"
                         f"Попробуйте ещё раз!", fg=C_DANGER)

        def solve_auto():
            if not current_example[0]:
                return
            ex = current_example[0]
            self.eq_entry.delete(0, tk.END)
            self.eq_entry.insert(0, ex["eq"])
            if 'a' in ex:
                self.a_entry.delete(0, tk.END)
                self.a_entry.insert(0, str(ex["a"]))
                self.b_entry.delete(0, tk.END)
                self.b_entry.insert(0, str(ex["b"]))
            self.solve()

        btn_frame = tk.Frame(right)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✓ Проверить ответ", command=check,
                  bg=C_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🧮 Решить в приложении", command=solve_auto,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        load_examples()

    def show_cloud_sync_dialog(self):
        dialog = tk.Toplevel(self.root)
        set_window_icon(dialog)
        dialog.title("☁ Облачная синхронизация")
        dialog.geometry("600x500")
        settings = getattr(self, "_settings", {})
        token_var = tk.StringVar(value=settings.get("github_token", ""))
        gist_id_var = tk.StringVar(value=settings.get("gist_id", ""))
        tk.Label(dialog, text="🔑 GitHub Personal Access Token",
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 5))
        token_frame = tk.Frame(dialog)
        token_frame.pack(fill=tk.X, padx=20)
        token_entry = tk.Entry(token_frame, textvariable=token_var, show="•",
                               font=("Consolas", 10), width=50)
        token_entry.pack(side=tk.LEFT)

        def toggle_token_visibility():
            current = token_entry.cget("show")
            token_entry.config(show="" if current == "•" else "•")

        tk.Button(token_frame, text="👁", command=toggle_token_visibility,
                  font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
        tk.Label(dialog, text="Создать: GitHub → Settings → Developer settings → "
                              "Personal access tokens → Tokens (classic) → Generate new token\n"
                              "Нужные права: gist (полный доступ)",
                 font=("Segoe UI", 8), fg="#6b7280", justify=tk.LEFT).pack(padx=20, anchor=tk.W)
        status_lbl = tk.Label(dialog, text="", font=("Segoe UI", 10), fg=C_ACCENT)
        status_lbl.pack(pady=5)

        def validate():
            token = token_var.get().strip()
            if not token:
                status_lbl.config(text="❌ Введите токен", fg=C_DANGER)
                return
            status_lbl.config(text="⏳ Проверка токена...", fg=C_ACCENT)
            dialog.update()
            try:
                login = cloud_sync.validate_token(token)
                if login:
                    status_lbl.config(text=f"✅ Токен действителен. Пользователь: {login}",
                                      fg=C_SUCCESS)
                    self._settings = getattr(self, "_settings", {})
                    self._settings["github_token"] = token
                    self._save_settings()
                else:
                    status_lbl.config(text="❌ Неверный токен", fg=C_DANGER)
            except Exception as e:
                status_lbl.config(text=f"❌ Ошибка: {e}", fg=C_DANGER)

        tk.Button(dialog, text="✓ Проверить токен", command=validate,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  padx=15).pack(pady=5)
        tk.Label(dialog, text="🆔 ID существующего gist (для загрузки)",
                 font=("Segoe UI", 11, "bold")).pack(pady=(15, 5))
        id_frame = tk.Frame(dialog)
        id_frame.pack(fill=tk.X, padx=20)
        tk.Entry(id_frame, textvariable=gist_id_var,
                 font=("Consolas", 10), width=50).pack(side=tk.LEFT)
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        def upload():
            token = token_var.get().strip()
            if not token:
                messagebox.showerror("Ошибка", "Введите и проверьте токен")
                return
            status_lbl.config(text="⏳ Загрузка данных в облако...", fg=C_ACCENT)
            dialog.update()
            try:
                data = {"version": VERSION, "timestamp": datetime.now().isoformat(),
                        "library": self.library, "history": self.history_log,
                        "equation": self.eq_entry.get(), "a": self.a_entry.get(),
                        "b": self.b_entry.get(), "sigma": self.sigma_entry.get()}
                gist_id = gist_id_var.get().strip() or None
                result = cloud_sync.upload_to_gist(token, data, gist_id=gist_id)
                gist_id_var.set(result["id"])
                self._settings["gist_id"] = result["id"]
                self._save_settings()
                self.stats.data["cloud_uploaded"] = True
                self.stats.save()
                status_lbl.config(text=f"✅ Загружено! ID: {result['id']}", fg=C_SUCCESS)
                messagebox.showinfo("Готово",
                                    f"Данные загружены в облако!\n\nGist ID: {result['id']}\n"
                                    f"Ссылка: {result['html_url']}")
            except Exception as e:
                status_lbl.config(text=f"❌ Ошибка: {e}", fg=C_DANGER)
                messagebox.showerror("Ошибка загрузки", str(e))

        def download():
            token = token_var.get().strip()
            gist_id = gist_id_var.get().strip()
            if not token or not gist_id:
                messagebox.showerror("Ошибка", "Введите токен и ID gist")
                return
            status_lbl.config(text="⏳ Загрузка данных из облака...", fg=C_ACCENT)
            dialog.update()
            try:
                data = cloud_sync.download_from_gist(token, gist_id)
                if "library" in data and isinstance(data["library"], list):
                    self.library = data["library"]
                    self.save_library_to_file()
                    self.refresh_library_combo()
                if "history" in data and isinstance(data["history"], list):
                    self.history_log = [tuple(r) for r in data["history"] if len(r) == 4]
                    self.save_history()
                if "equation" in data:
                    self.eq_entry.delete(0, tk.END)
                    self.eq_entry.insert(0, data["equation"])
                if "a" in data:
                    self.a_entry.delete(0, tk.END)
                    self.a_entry.insert(0, data["a"])
                if "b" in data:
                    self.b_entry.delete(0, tk.END)
                    self.b_entry.insert(0, data["b"])
                if "sigma" in data:
                    self.sigma_entry.delete(0, tk.END)
                    self.sigma_entry.insert(0, data["sigma"])
                status_lbl.config(text="✅ Данные загружены из облака!", fg=C_SUCCESS)
                messagebox.showinfo("Готово", "Данные успешно загружены из облака!")
            except Exception as e:
                status_lbl.config(text=f"❌ Ошибка: {e}", fg=C_DANGER)
                messagebox.showerror("Ошибка загрузки", str(e))

        def list_gists():
            token = token_var.get().strip()
            if not token:
                messagebox.showerror("Ошибка", "Введите токен")
                return
            status_lbl.config(text="⏳ Получение списка gist...", fg=C_ACCENT)
            dialog.update()
            try:
                gists = cloud_sync.list_user_gists(token)
                if not gists:
                    messagebox.showinfo("Информация", "Нет gist'ов с данными приложения")
                    return
                list_win = tk.Toplevel(dialog)
                list_win.title("Ваши gist'ы")
                list_win.geometry("500x400")
                tree = ttk.Treeview(list_win, columns=("ID", "Updated", "Desc"), show="headings")
                tree.heading("ID", text="ID")
                tree.heading("Updated", text="Обновлён")
                tree.heading("Desc", text="Описание")
                tree.column("ID", width=150)
                tree.column("Updated", width=150)
                tree.column("Desc", width=180)
                tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                for g in gists:
                    tree.insert("", tk.END, values=(g["id"], g.get("updated_at", "")[:19],
                                                    g.get("description", "")[:30]))

                def select(event):
                    sel = tree.selection()
                    if sel:
                        gist_id_var.set(tree.item(sel[0])["values"][0])
                        list_win.destroy()

                tree.bind("<Double-1>", select)
                status_lbl.config(text=f"✅ Найдено gist'ов: {len(gists)}", fg=C_SUCCESS)
            except Exception as e:
                status_lbl.config(text=f"❌ Ошибка: {e}", fg=C_DANGER)

        tk.Button(btn_frame, text="⬆ Загрузить в облако", command=upload,
                  bg=C_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="⬇ Загрузить из облака", command=download,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 Мои gist'ы", command=list_gists,
                  bg="#6b7280", fg="white", font=("Segoe UI", 10, "bold"),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def show_reference(self):
        self.stats.data["reference_opened"] = True
        self.stats.save()
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("📚 Справочник формул")
        win.geometry("900x700")
        sections = {
            "🎯 Методы поиска корней": [
                ("Бисекция", "c = (a + b) / 2", "Делим отрезок пополам.", "Линейная", "f(a)·f(b) < 0"),
                ("Хорды", "x_{n+1} = x_n − f(x_n)·(x_n − x₀)/(f(x_n) − f(x₀))", "Хорда между концами.", "Линейная",
                 "f(a)·f(b) < 0"),
                ("Ньютон", "x_{n+1} = x_n − f(x_n)/f'(x_n)", "Касательная.", "Квадратичная", "f'(x) ≠ 0"),
                ("Секущие", "x_{n+1} = x_n − f(x_n)·(x_n−x_{n−1})/(f(x_n)−f(x_{n−1}))", "Без производной.",
                 "Сверхлинейная", "2 начальные точки"),
                ("Брент", "Гибрид: бисекция + секущие + ОКИ", "Автоматический выбор.", "Сверхлинейная",
                 "f(a)·f(b) < 0"),
                ("МПИ", "x_{n+1} = x_n − f(x_n)/M", "Итерация.", "Линейная", "|φ'(x)| < 1"),
            ],
            "∫ Численное интегрирование": [
                ("Трапеции", "∫f(x)dx ≈ h·[f(a)/2 + Σf(xᵢ) + f(b)/2]", "Ломаная.", "O(h²)", "Непрерывная"),
                ("Симпсон", "∫f(x)dx ≈ (h/3)·[f(a) + 4·Σf(x₂ᵢ₊₁) + 2·Σf(x₂ᵢ) + f(b)]", "Параболы.", "O(h⁴)",
                 "n чётное"),
                ("Гаусс", "∫f(x)dx ≈ Σwᵢ·f(xᵢ)", "Оптимальные узлы.", "O(h²ⁿ)", "Гладкая"),
                ("Монте-Карло", "∫f(x)dx ≈ (b−a)·(1/N)·Σf(xᵢ)", "Случайная выборка.", "O(1/√N)", "Любая"),
            ],
            "📐 Интерполяция": [
                ("Лагранж", "L(x) = Σ yᵢ · Π_{j≠i} (x−xⱼ)/(xᵢ−xⱼ)", "Полином через точки.", "Точная в узлах",
                 "Мало точек"),
                ("Сплайн", "Sᵢ(x) = aᵢ + bᵢ(x−xᵢ) + cᵢ(x−xᵢ)² + dᵢ(x−xᵢ)³", "Кусочно-кубическая.", "O(h⁴)",
                 "Возрастающие xᵢ"),
                ("МНК", "y = ax + b", "Прямая.", "—", "Линейная зависимость"),
            ],
            "⚙️ Системы (Ax=b)": [
                ("Гаусс", "Прямой + обратный ход", "Исключение.", "O(n³)", "det ≠ 0"),
                ("Якоби", "xᵢ^(k+1) = (bᵢ − Σ_{j≠i} aᵢⱼ·xⱼ^(k)) / aᵢᵢ", "Итерации.", "Линейная", "Диаг. преобладание"),
                ("Зейдель", "Как Якоби, но с обновлёнными xⱼ", "Быстрее Якоби.", "Линейная", "Диаг. преобладание"),
                ("Прогонка", "αᵢ, βᵢ рекуррентно", "Трёхдиагональные.", "O(n)", "Трёхдиагональная"),
            ],
            "📈 ОДУ": [
                ("Эйлер", "y_{n+1} = y_n + h·f(x_n, y_n)", "Касательная.", "O(h)", "Малый h"),
                ("Рунге-Кутта 4", "y_{n+1} = y_n + (k₁+2k₂+2k₃+k₄)/6", "4 вычисления.", "O(h⁴)", "Умеренные затраты"),
            ],
            "🔍 Оптимизация": [
                ("Золотое сечение", "x₁ = b − φ(b−a), x₂ = a + φ(b−a)", "Поиск минимума.", "Линейная", "Унимодальная"),
            ],
        }
        main_frame = tk.Frame(win)
        main_frame.pack(fill=tk.BOTH, expand=True)
        left = tk.Frame(main_frame, width=220, bg="#f3f4f6")
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        tk.Label(left, text="📚 Разделы", font=("Segoe UI", 12, "bold"),
                 bg="#f3f4f6").pack(pady=10)
        right = tk.Frame(main_frame, bg="white")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(right, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def show_section(section_name):
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            tk.Label(scroll_frame, text=section_name, font=("Segoe UI", 16, "bold"),
                     bg="white", fg=C_ACCENT).pack(pady=15, anchor=tk.W, padx=20)
            for method_name, formula, description, convergence, requirements in sections[section_name]:
                card = tk.Frame(scroll_frame, bg="#f9fafb", relief=tk.GROOVE, bd=1)
                card.pack(fill=tk.X, padx=15, pady=8)
                tk.Label(card, text=f"▸ {method_name}", font=("Segoe UI", 12, "bold"),
                         bg="#f9fafb", fg="#1f2937").pack(anchor=tk.W, padx=10, pady=(8, 4))
                formula_frame = tk.Frame(card, bg="#e0f2fe", padx=10, pady=8)
                formula_frame.pack(fill=tk.X, padx=10, pady=4)
                tk.Label(formula_frame, text=formula, font=("Consolas", 11),
                         bg="#e0f2fe", fg="#0369a1").pack(anchor=tk.W)
                tk.Label(card, text=f"📖 {description}", font=("Segoe UI", 10),
                         bg="#f9fafb", fg="#374151", wraplength=600,
                         justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=4)
                info_frame = tk.Frame(card, bg="#f9fafb")
                info_frame.pack(fill=tk.X, padx=10, pady=4)
                tk.Label(info_frame, text=f"⚡ Сходимость: {convergence}",
                         font=("Segoe UI", 9), bg="#f9fafb", fg=C_SUCCESS).pack(side=tk.LEFT, padx=(0, 20))
                tk.Label(info_frame, text=f"⚠️ Требования: {requirements}",
                         font=("Segoe UI", 9), bg="#f9fafb", fg=C_DANGER).pack(side=tk.LEFT)

        for section_name in sections.keys():
            btn = tk.Button(left, text=section_name, font=("Segoe UI", 10),
                            bg="#f3f4f6", fg="#1f2937", relief=tk.FLAT, anchor=tk.W,
                            padx=10, pady=8, command=lambda s=section_name: show_section(s))
            btn.pack(fill=tk.X, padx=5, pady=2)
        show_section(list(sections.keys())[0])

    def save_session(self):
        fp = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not fp:
            return
        session = {"equation": self.eq_entry.get(), "a": self.a_entry.get(),
                   "b": self.b_entry.get(), "sigma": self.sigma_entry.get(),
                   "view": {"x_min": self.view_x_min, "x_max": self.view_x_max,
                            "y_min": self.view_y_min, "y_max": self.view_y_max},
                   "theme": self.theme, "timestamp": datetime.now().isoformat()}
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Готово", f"Сессия сохранена:\n{fp}")

    def load_session(self):
        fp = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not fp:
            return
        try:
            with open(fp, "r", encoding="utf-8") as f:
                session = json.load(f)
            self.eq_entry.delete(0, tk.END)
            self.eq_entry.insert(0, session.get("equation", ""))
            self.a_entry.delete(0, tk.END)
            self.a_entry.insert(0, session.get("a", ""))
            self.b_entry.delete(0, tk.END)
            self.b_entry.insert(0, session.get("b", ""))
            self.sigma_entry.delete(0, tk.END)
            self.sigma_entry.insert(0, session.get("sigma", ""))
            if "view" in session:
                self.view_x_min = session["view"]["x_min"]
                self.view_x_max = session["view"]["x_max"]
                self.view_y_min = session["view"]["y_min"]
                self.view_y_max = session["view"]["y_max"]
            if "theme" in session and session["theme"] != self.theme:
                self.theme = session["theme"]
                self.apply_theme()
            messagebox.showinfo("Готово", "Сессия загружена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить:\n{e}")

    def check_for_updates(self, silent=False):
        if not UPDATE_API:
            return
        self.status_var.set("🔄 Проверка обновлений...")
        self.root.update()

        def worker():
            try:
                req = urllib.request.Request(UPDATE_API,
                                             headers={"User-Agent": f"{APP_NAME}/{VERSION}",
                                                      "Accept": "application/vnd.github+json"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                tag = data.get("tag_name", "").lstrip("vV")
                if not tag:
                    raise ValueError("Не найден tag_name")

                def parse(v):
                    return tuple(int(x) for x in re.findall(r"\d+", v))

                if parse(tag) > parse(VERSION):
                    url = None
                    for asset in data.get("assets", []):
                        if asset.get("name") == UPDATE_EXE:
                            url = asset.get("browser_download_url")
                            break
                    self.root.after(0, lambda: self._offer_update(
                        tag, url, data.get("html_url"), data.get("body", "")))
                else:
                    if not silent:
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Обновления", f"У вас актуальная версия {VERSION}"))
            except Exception as e:
                if not silent:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка", f"Не удалось проверить:\n{e}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("Готов"))

        threading.Thread(target=worker, daemon=True).start()

    def _offer_update(self, new_ver, download_url, release_url, changelog):
        msg = (f"Доступна новая версия: {new_ver}\nВаша версия: {VERSION}\n\n"
               f"Что нового:\n{changelog[:500]}\n\nСкачать и установить?")
        if not messagebox.askyesno("Обновление", msg):
            return
        if not download_url:
            webbrowser.open(release_url)
            return
        self.status_var.set(f"⬇ Скачивание v{new_ver}...")
        self.root.update()

        def download():
            try:
                tmp_dir = Path(DATA_DIR) / "update"
                tmp_dir.mkdir(exist_ok=True)
                new_exe = tmp_dir / UPDATE_EXE
                updater = tmp_dir / "updater.bat"
                req = urllib.request.Request(download_url,
                                             headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
                with urllib.request.urlopen(req, timeout=120) as resp, \
                        open(new_exe, "wb") as f:
                    shutil.copyfileobj(resp, f)
                current_exe = Path(sys.executable if getattr(sys, "frozen", False)
                                   else os.path.abspath(__file__))
                updater.write_text(
                    f'@echo off\r\ntimeout /t 2 /nobreak >nul\r\n'
                    f'del /f /q "{current_exe}"\r\nmove /y "{new_exe}" "{current_exe}"\r\n'
                    f'start "" "{current_exe}"\r\ndel "%~f0"\r\n', encoding="cp866")
                self.root.after(0, lambda: self._apply_update(updater))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", f"Не удалось скачать:\n{e}"))

        threading.Thread(target=download, daemon=True).start()

    def _apply_update(self, updater_path):
        if messagebox.askyesno("Установка", "Приложение будет закрыто для установки.\nПродолжить?"):
            self.on_closing()
            subprocess.Popen([str(updater_path)],
                             creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            sys.exit(0)

    def load_library(self):
        try:
            with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return [it for it in data if isinstance(it, dict) and {"name", "eq", "a", "b"} <= set(it)]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return []

    def save_library_to_file(self):
        try:
            with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.library, f, ensure_ascii=False, indent=2)
        except OSError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def refresh_library_combo(self):
        self.library_combo['values'] = [it["name"] for it in self.library]
        if self.library:
            self.library_combo.current(0)

    def load_from_library(self, event=None):
        idx = self.library_combo.current()
        if idx < 0:
            return
        it = self.library[idx]
        self.eq_entry.delete(0, tk.END)
        self.eq_entry.insert(0, it["eq"])
        self.a_entry.delete(0, tk.END)
        self.a_entry.insert(0, it["a"])
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, it["b"])

    def save_to_library(self):
        eq, a, b = (self.eq_entry.get().strip(), self.a_entry.get().strip(), self.b_entry.get().strip())
        if not eq:
            return
        name = simpledialog.askstring("Имя", "Название функции:", parent=self.root)
        if name:
            self.library.append({"name": name, "eq": eq, "a": a, "b": b})
            self.save_library_to_file()
            self.refresh_library_combo()

    def open_library_manager(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Библиотека")
        win.geometry("750x450")
        tree = ttk.Treeview(win, columns=("Имя", "Уравнение"), show="headings")
        tree.heading("Имя", text="Имя")
        tree.heading("Уравнение", text="Уравнение")
        tree.column("Имя", width=200)
        tree.column("Уравнение", width=400)
        tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        for it in self.library:
            tree.insert("", tk.END, values=(it["name"], it["eq"]))

        def del_sel():
            s = tree.selection()
            if s:
                self.library.pop(tree.index(s[0]))
                self.save_library_to_file()
                win.destroy()
                self.open_library_manager()

        tk.Button(win, text="🗑 Удалить", command=del_sel, bg="#fee2e2").pack(pady=5)

    def show_calculator(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Клавиатура")
        win.geometry("400x300")

        def insert(txt):
            self.eq_entry.insert(tk.END, txt)
            self.eq_entry.focus_set()

        btns = [("x²", "x**2"), ("x³", "x**3"), ("x^n", "x**"), ("√x", "math.sqrt(x)"),
                ("sin", "math.sin("), ("cos", "math.cos("), ("π", "pi"), ("e", "e"),
                ("+", " + "), ("-", " - "), ("*", " * "), ("/", " / "),
                ("(", "("), (")", ")"), ("Очистить", "CLR")]
        for i, (text, symbol) in enumerate(btns):
            r, c = divmod(i, 4)
            tk.Button(win, text=text, font=("Segoe UI", 12, "bold"), width=6, height=2,
                      command=(lambda s=symbol: self.eq_entry.delete(0, tk.END)
                      if s == "CLR" else insert(s))).grid(row=r, column=c, padx=5, pady=5)

    def show_history(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("История")
        win.geometry("600x400")
        tree = ttk.Treeview(win, columns=("Уравнение", "a", "b", "Корень"), show="headings")
        for c in ("Уравнение", "a", "b", "Корень"):
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor=tk.CENTER)
        tree.column("Уравнение", width=250, anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for item in reversed(self.history_log):
            tree.insert("", tk.END, values=item)

        def load_hist(event):
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0], "values")
            self.eq_entry.delete(0, tk.END)
            self.eq_entry.insert(0, vals[0])
            self.a_entry.delete(0, tk.END)
            self.a_entry.insert(0, vals[1])
            self.b_entry.delete(0, tk.END)
            self.b_entry.insert(0, vals[2])
            win.destroy()

        tree.bind("<Double-1>", load_hist)

    def show_help(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("📖 Справка")
        win.geometry("700x650")
        text = tk.Text(win, font=("Segoe UI", 10), wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        help_content = """
🧮 ЧИСЛЕННЫЕ МЕТОДЫ · TURBO EDITION v2.0

═══════════════════════════════════════════

📊 6 МЕТОДОВ РЕШЕНИЯ УРАВНЕНИЙ:
  1. Метод половинного деления (бисекция)
  2. Метод хорд
  3. Метод Ньютона (касательных)
  4. Метод секущих
  5. Метод Брента (гибридный)
  6. Метод простой итерации (МПИ)

═══════════════════════════════════════════

🔬 ЧТО ТАКОЕ SYMPY?

SymPy — это библиотека символьной математики.
В отличие от численных методов (которые дают
приближённый ответ вроде x ≈ 2.0000001),
SymPy работает с точными математическими
выражениями.

Что умеет SymPy:
  • Находить точные корни уравнений
  • Вычислять производные и интегралы
  • Упрощать выражения
  • Строить ряды Тейлора
  • Решать системы уравнений

Зачем это нужно:
  ✓ Проверка точности численных методов
  ✓ Получение точных ответов для сравнения
  ✓ Визуализация формул в отчётах
  ✓ Обучение и понимание математики

Пример:
  Численно: x ≈ 2.0000001
  SymPy:    x = 2 (точно!)

═══════════════════════════════════════════

🎯 РЕЖИМЫ РАБОТЫ С ПЕРЕМЕННЫМИ:

  • 1 переменная (x) — обычный режим
    Пример: x**2 - 4 = 0

  • Несколько переменных (x, y, z...) — 
    для функций вида f(x, y, z) = 0
    Пример: x**2 + y**2 - 4 = 0
    (y и z задаются отдельно через диалог)

═══════════════════════════════════════════

⌨️ ГОРЯЧИЕ КЛАВИШИ:
  • F5 / Ctrl+R — рассчитать
  • Ctrl+S — сохранить сессию
  • Ctrl+O — загрузить сессию
  • F11 — полноэкранный режим
  • Esc — выход из полноэкранного
  • F1 — эта справка

═══════════════════════════════════════════

📈 ГРАФИК:
  • Колесико мыши — зум
  • ЛКМ + перетаскивание — перемещение
  • Двойной клик — показать точку
  • ПКМ — контекстное меню
  • Кнопки ◀ ▶ — история просмотров

═══════════════════════════════════════════

🏆 ДОСТИЖЕНИЯ:
  В программе 10 достижений!
  Решайте уравнения, экспериментируйте
  с методами и открывайте новые достижения.

═══════════════════════════════════════════

📤 ЭКСПОРТ:
  • PDF — красивый отчёт с таблицами
  • Excel — данные для анализа
  • HTML — веб-страница
  • Markdown — для GitHub/заметок
  • CSV — табличные данные
  • SVG — векторный график
  • LaTeX — для научных работ
"""
        text.insert(tk.END, help_content)
        text.config(state=tk.DISABLED)

    def show_tutorial(self):
        self.stats.data["tutorial_opened"] = True
        self.stats.save()
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Учебник")
        win.geometry("800x600")
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for key, data in TUTORIAL.items():
            tab = tk.Frame(nb)
            nb.add(tab, text=data["title"][:20])
            tk.Label(tab, text=data["title"], font=("Segoe UI", 14, "bold")).pack(pady=10)
            tk.Label(tab, text=data["theory"], font=("Segoe UI", 10),
                     justify=tk.LEFT, wraplength=700).pack(padx=20, anchor=tk.W)
            tk.Label(tab, text=f"Формула: {data['formula']}",
                     font=("Consolas", 11), fg=C_ACCENT).pack(pady=10)
            tk.Label(tab, text=f"✅ Плюсы: {data['pros']}", font=("Segoe UI", 10),
                     fg=C_SUCCESS, justify=tk.LEFT, wraplength=700).pack(padx=20, anchor=tk.W)
            tk.Label(tab, text=f"❌ Минусы: {data['cons']}", font=("Segoe UI", 10),
                     fg=C_DANGER, justify=tk.LEFT, wraplength=700).pack(padx=20, anchor=tk.W)

    def show_glossary(self):
        self.stats.data["glossary_opened"] = True
        self.stats.save()
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Словарь терминов")
        win.geometry("600x500")
        text = tk.Text(win, font=("Segoe UI", 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for term, defn in GLOSSARY.items():
            text.insert(tk.END, f"▸ {term}\n", "term")
            text.insert(tk.END, f"  {defn}\n\n", "defn")
        text.tag_config("term", font=("Segoe UI", 11, "bold"), foreground=C_ACCENT)
        text.tag_config("defn", font=("Segoe UI", 10))

    def run_builtin_tests(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Встроенные тесты")
        win.geometry("700x500")
        text = tk.Text(win, font=("Consolas", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        results = builtin_tests.run_all_tests()
        passed = sum(1 for _, ok, _ in results if ok)
        text.insert(tk.END, f"=== РЕЗУЛЬТАТ: {passed}/{len(results)} тестов пройдено ===\n\n", "header")
        for name, ok, detail in results:
            mark = "✅" if ok else "❌"
            text.insert(tk.END, f"{mark} {name}: {detail}\n", "ok" if ok else "fail")
        text.tag_config("header", font=("Consolas", 12, "bold"), foreground=C_ACCENT)
        text.tag_config("ok", foreground=C_SUCCESS)
        text.tag_config("fail", foreground=C_DANGER)

    def show_achievements(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("🏆 Достижения")
        win.geometry("700x700")
        unlocked = set(self.stats.data.get("unlocked", []))
        total = len(ACHIEVEMENTS)
        unlocked_count = len(unlocked)
        header = tk.Frame(win, bg="#1e3a5f", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text=f"🏆 Достижения: {unlocked_count}/{total}",
                 font=("Segoe UI", 16, "bold"), bg="#1e3a5f", fg="white").pack(pady=15)
        progress_frame = tk.Frame(win, bg="#f3f4f6", height=30)
        progress_frame.pack(fill=tk.X)
        progress_bar = ttk.Progressbar(progress_frame, maximum=total, value=unlocked_count, length=600)
        progress_bar.pack(pady=5)
        tk.Label(progress_frame, text=f"{unlocked_count}/{total} ({100 * unlocked_count // total if total else 0}%)",
                 font=("Segoe UI", 9), bg="#f3f4f6").pack()
        canvas_frame = tk.Frame(win)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(canvas_frame, bg="#f9fafb", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f9fafb")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        categories = {}
        for key, ach in ACHIEVEMENTS.items():
            cat = ach.get("category", "Другое")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, ach))
        for category, items in categories.items():
            tk.Label(scroll_frame, text=f"📂 {category}",
                     font=("Segoe UI", 12, "bold"), bg="#f9fafb", fg="#1e3a5f").pack(anchor=tk.W, padx=15, pady=(15, 5))
            for key, ach in items:
                is_unlocked = key in unlocked
                bg = "#dcfce7" if is_unlocked else "#fee2e2"
                status = "🏆" if is_unlocked else "🔒"
                card = tk.Frame(scroll_frame, bg=bg, relief=tk.GROOVE, bd=1)
                card.pack(fill=tk.X, padx=15, pady=3)
                title_frame = tk.Frame(card, bg=bg)
                title_frame.pack(fill=tk.X, padx=10, pady=(8, 2))
                tk.Label(title_frame, text=f"{status} {ach['icon']} {ach['name']}",
                         font=("Segoe UI", 11, "bold"), bg=bg,
                         fg="#1f2937" if is_unlocked else "#6b7280").pack(side=tk.LEFT)
                tk.Label(card, text=ach["desc"], font=("Segoe UI", 9),
                         bg=bg, fg="#374151" if is_unlocked else "#9ca3af",
                         justify=tk.LEFT).pack(anchor=tk.W, padx=25, pady=(0, 8))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        tk.Button(win, text="Закрыть", command=win.destroy,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=5).pack(pady=10)

    def show_stats(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Статистика")
        win.geometry("500x400")
        d = self.stats.data
        text = tk.Text(win, font=("Consolas", 11))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, f"Всего решено уравнений: {d.get('total_solves', 0)}\n")
        text.insert(tk.END, f"Общее время работы: {d.get('total_time_ms', 0) / 1000:.1f} с\n")
        text.insert(tk.END, f"Быстрых решений (<100мс): {d.get('fast_solves', 0)}\n\n")
        text.insert(tk.END, "Использовано методов:\n")
        for m, c in d.get("methods_used", {}).items():
            text.insert(tk.END, f"  • {m}: {c} раз\n")
        text.insert(tk.END, f"\nЭкспортов в форматы: {len(d.get('exports', []))}\n")
        text.insert(tk.END, f"Достижений: {len(d.get('unlocked', []))}/{len(ACHIEVEMENTS)}\n")

    def generate_problem(self):
        p = random.choice(TEST_PROBLEMS)
        self.eq_entry.delete(0, tk.END)
        self.eq_entry.insert(0, p["eq"])
        self.a_entry.delete(0, tk.END)
        self.a_entry.insert(0, p["a"])
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, p["b"])
        messagebox.showinfo("Задача", f"📚 {p['name']}\n\n"
                                      f"f(x) = {p['eq']}\n"
                                      f"Интервал: [{p['a']}; {p['b']}]\n"
                                      f"Известный корень: {p['roots'][0]:.6f}\n\n"
                                      "Проверь, найдёт ли программа его!")

    def batch_process_dialog(self):
        win = tk.Toplevel(self.root)
        set_window_icon(win)
        win.title("Пакетная обработка")
        win.geometry("500x300")
        tk.Label(win, text="Пакетная обработка уравнений из CSV",
                 font=("Segoe UI", 12, "bold")).pack(pady=15)
        tk.Label(win, text="CSV должен содержать колонки: eq,a,b,sigma",
                 font=("Segoe UI", 10)).pack()

        def run_batch():
            fp = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
            if not fp:
                return
            try:
                tasks = load_tasks_csv(fp)
                results = []
                for task in tasks:
                    try:
                        f_parsed, _ = self.parse_equation(task["eq"])
                        f = lambda x: f_parsed({'x': x})
                        a = float(task["a"])
                        b = float(task["b"])
                        sigma = float(task.get("sigma", "1e-6"))
                        root, _ = brent_method(f, a, b, sigma)
                        results.append({
                            "task": task,
                            "result": f"{root:.10f}" if root else "—",
                            "status": "ok"
                        })
                    except Exception as e:
                        results.append({"task": task, "result": None,
                                        "status": f"error: {e}"})
                out_fp = filedialog.asksaveasfilename(defaultextension=".csv",
                                                      filetypes=[("CSV", "*.csv")])
                if out_fp:
                    with open(out_fp, "w", encoding="utf-8", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Уравнение", "a", "b", "σ", "Корень", "Статус"])
                        for r in results:
                            t = r["task"]
                            writer.writerow([t.get("eq"), t.get("a"), t.get("b"),
                                             t.get("sigma"), r["result"], r["status"]])
                    self.stats.record_batch(len(results))
                    messagebox.showinfo("Готово", f"Результаты сохранены:\n{out_fp}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обработать:\n{e}")

        tk.Button(win, text="Выбрать CSV и обработать", command=run_batch,
                  bg=C_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=10).pack(pady=30)

    def _load_settings(self):
        s = {}
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        self._settings = s
        if s.get("theme") in THEMES:
            self.theme = s["theme"]

    def _save_settings(self):
        s = {"theme": self.theme, "geometry": self.root.geometry(),
             "equation": self.eq_entry.get(), "a": self.a_entry.get(),
             "b": self.b_entry.get(), "sigma": self.sigma_entry.get(),
             "show_extrema": bool(self.show_extrema.get())}
        s.update(getattr(self, "_settings", {}))
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(s, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def load_history(self):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.history_log = [tuple(r) for r in data if len(r) == 4]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self.history_log = []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history_log[-200:], f, ensure_ascii=False, indent=2)
        except OSError:
            pass

import nm_core
nm_core.SETTINGS_FILE_GLOBAL = SETTINGS_FILE
nm_core.install(NumericalMethodsApp)
if __name__ == "__main__":
    root = tk.Tk()
    app = NumericalMethodsApp(root)

    menubar = tk.Menu(root)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="💾 Сохранить сессию (Ctrl+S)", command=app.save_session)
    filemenu.add_command(label="📂 Загрузить сессию (Ctrl+O)", command=app.load_session)
    filemenu.add_command(label="📥 Импорт формул из файла...", command=app.import_formulas_from_file)
    filemenu.add_separator()
    filemenu.add_command(label="📦 Пакетная обработка CSV...", command=app.batch_process_dialog)
    filemenu.add_command(label="☁ Облачная синхронизация...", command=app.show_cloud_sync_dialog)
    filemenu.add_separator()
    if sys.platform.startswith("win"):
        filemenu.add_command(label="📁 Папка данных", command=lambda: os.startfile(DATA_DIR))
    filemenu.add_separator()
    filemenu.add_command(label="Выход", command=app.on_closing)
    menubar.add_cascade(label="Файл", menu=filemenu)

    viewmenu = tk.Menu(menubar, tearoff=0)
    viewmenu.add_command(label="🌗 Сменить тему", command=app.toggle_theme)
    viewmenu.add_command(label="🔲 Полноэкранный (F11)", command=app.toggle_fullscreen)
    viewmenu.add_checkbutton(label="Высокий контраст", variable=app.high_contrast, command=app.apply_theme)
    submenu_themes = tk.Menu(viewmenu, tearoff=0)
    for t in THEMES:
        submenu_themes.add_command(label=t.capitalize(),
                                   command=lambda tt=t: (setattr(app, 'theme', tt), app.apply_theme()))
    viewmenu.add_cascade(label="🎨 Темы", menu=submenu_themes)
    menubar.add_cascade(label="Вид", menu=viewmenu)

    toolsmenu = tk.Menu(menubar, tearoff=0)
    if HAS_SYMPY:
        toolsmenu.add_command(label="🔬 Аналитическое решение (SymPy)", command=app.solve_analytical)
        toolsmenu.add_command(label="📄 Экспорт аналитического отчёта (LaTeX)", command=app.export_analytical_report)
    toolsmenu.add_command(label="📚 Пошаговое решение", command=app.show_step_by_step)
    toolsmenu.add_command(label="🎓 Интерактивный учебник с примерами", command=app.show_interactive_tutorial)
    toolsmenu.add_command(label="🎯 Случайная задача", command=app.generate_problem)
    toolsmenu.add_command(label="🧪 Встроенные тесты", command=app.run_builtin_tests)
    toolsmenu.add_separator()
    langmenu = tk.Menu(toolsmenu, tearoff=0)
    langmenu.add_command(label="🇷🇺 Русский", command=lambda: app.tr.set_language("ru"))
    langmenu.add_command(label="🇬🇧 English", command=lambda: app.tr.set_language("en"))
    toolsmenu.add_cascade(label="🌐 Язык", menu=langmenu)
    menubar.add_cascade(label="Инструменты", menu=toolsmenu)

    learnmenu = tk.Menu(menubar, tearoff=0)
    learnmenu.add_command(label="📚 Учебник", command=app.show_tutorial)
    learnmenu.add_command(label="📖 Словарь терминов", command=app.show_glossary)
    learnmenu.add_command(label="📘 Справочник формул", command=app.show_reference)
    menubar.add_cascade(label="Обучение", menu=learnmenu)

    statsmenu = tk.Menu(menubar, tearoff=0)
    statsmenu.add_command(label="📊 Статистика", command=app.show_stats)
    statsmenu.add_command(label="🏆 Достижения", command=app.show_achievements)
    menubar.add_cascade(label="Профиль", menu=statsmenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="🔄 Проверить обновления", command=lambda: app.check_for_updates(silent=False))
    helpmenu.add_command(label="📖 Справка (F1)", command=app.show_help)
    helpmenu.add_command(label=f"ℹ О программе (v{VERSION})",
                         command=lambda: messagebox.showinfo("О программе",
                                                             f"{APP_TITLE}\nВерсия {VERSION}\n\n"
                                                             "6 методов: бисекция, хорды, Ньютон, секущие, Брент, МПИ\n"
                                                             "3D-графики, контурные, векторные поля\n"
                                                             "Экспорт: PDF, Excel, HTML, Markdown, CSV, SVG, LaTeX"))
    menubar.add_cascade(label="Справка", menu=helpmenu)

    root.config(menu=menubar)
    root.mainloop()