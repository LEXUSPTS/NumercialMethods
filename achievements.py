# achievements.py
"""Система достижений и статистики — 30 достижений."""
import json
import os

ACHIEVEMENTS = {
    # === БАЗОВЫЕ ===
    "first_solve": {"name": "Первый шаг", "desc": "Решить первое уравнение", "icon": "🎯", "category": "Базовые"},
    "ten_solves": {"name": "Десяточка", "desc": "Решить 10 уравнений", "icon": "🔟", "category": "Базовые"},
    "hundred_solves": {"name": "Сотня", "desc": "Решить 100 уравнений", "icon": "💯", "category": "Базовые"},
    "thousand_solves": {"name": "Тысячник", "desc": "Решить 1000 уравнений", "icon": "🏆", "category": "Базовые"},

    # === МЕТОДЫ ===
    "newton_master": {"name": "Мастер Ньютона", "desc": "Ньютон сошёлся за <5 итераций 10 раз", "icon": "🚀",
                      "category": "Методы"},
    "brent_fan": {"name": "Фанат Брента", "desc": "Использовать метод Брента 20 раз", "icon": "🎯",
                  "category": "Методы"},
    "bisection_pro": {"name": "Бисектор", "desc": "Использовать бисекцию 50 раз", "icon": "✂️", "category": "Методы"},
    "all_methods": {"name": "Полиметодист", "desc": "Использовать все 6 методов хотя бы по разу", "icon": "🧭",
                    "category": "Методы"},
    "secant_speed": {"name": "Секатор", "desc": "Метод секущих за <10 итераций", "icon": "⚡", "category": "Методы"},
    "mpi_patience": {"name": "Терпеливый", "desc": "МПИ сошёлся за >100 итераций", "icon": "🐢", "category": "Методы"},

    # === СКОРОСТЬ ===
    "speed_demon": {"name": "Скорострел", "desc": "Решить уравнение быстрее 100 мс", "icon": "⚡",
                    "category": "Скорость"},
    "lightning": {"name": "Молния", "desc": "Решить 10 уравнений быстрее 100 мс", "icon": "🌩️", "category": "Скорость"},
    "marathon": {"name": "Марафонец", "desc": "Работать в программе более 1 часа", "icon": "🏃", "category": "Скорость"},
    "night_owl": {"name": "Сова", "desc": "Решать уравнения после полуночи", "icon": "🦉", "category": "Скорость"},

    # === ТОЧНОСТЬ ===
    "precision": {"name": "Точность", "desc": "Использовать σ < 1e-12", "icon": "🎯", "category": "Точность"},
    "ultra_precision": {"name": "Ультра-точность", "desc": "Использовать σ < 1e-15", "icon": "💎",
                        "category": "Точность"},
    "rough_estimate": {"name": "Грубая оценка", "desc": "Использовать σ > 0.01", "icon": "🎲", "category": "Точность"},

    # === ЭКСПОРТ ===
    "exporter": {"name": "Экспортёр", "desc": "Сохранить отчёт в 3 разных форматах", "icon": "📤",
                 "category": "Экспорт"},
    "pdf_master": {"name": "PDF-мастер", "desc": "Экспортировать 10 PDF-отчётов", "icon": "📕", "category": "Экспорт"},
    "excel_guru": {"name": "Excel-гуру", "desc": "Экспортировать 10 Excel-файлов", "icon": "📗", "category": "Экспорт"},
    "latex_scholar": {"name": "LaTeX-учёный", "desc": "Экспортировать отчёт в LaTeX", "icon": "📝",
                      "category": "Экспорт"},
    "svg_artist": {"name": "SVG-художник", "desc": "Сохранить график в SVG", "icon": "🎨", "category": "Экспорт"},

    # === ОБУЧЕНИЕ ===
    "student": {"name": "Студент", "desc": "Открыть учебник", "icon": "📚", "category": "Обучение"},
    "quiz_master": {"name": "Викторинщик", "desc": "Правильно ответить на 5 задач в учебнике", "icon": "🧠",
                    "category": "Обучение"},
    "reference_reader": {"name": "Справочник", "desc": "Открыть справочник формул", "icon": "📘",
                         "category": "Обучение"},
    "glossary_expert": {"name": "Терминовед", "desc": "Открыть словарь терминов", "icon": "📖", "category": "Обучение"},

    # === ГРАФИКА ===
    "graph_explorer": {"name": "Исследователь графика", "desc": "Использовать зум и перемещение", "icon": "🔍",
                       "category": "Графика"},
    "extrema_hunter": {"name": "Охотник за экстремумами", "desc": "Найти 10 экстремумов", "icon": "📍",
                       "category": "Графика"},
    "3d_pioneer": {"name": "3D-первопроходец", "desc": "Открыть 3D-график", "icon": "🎲", "category": "Графика"},
    "contour_artist": {"name": "Контурный художник", "desc": "Создать контурный график", "icon": "🗺️",
                       "category": "Графика"},
    "vector_visionary": {"name": "Векторный визионер", "desc": "Визуализировать векторное поле", "icon": "➤",
                         "category": "Графика"},

    # === ПРОДВИНУТЫЕ ===
    "cloud_syncer": {"name": "Облачный синхронизатор", "desc": "Загрузить данные в облако", "icon": "☁️",
                     "category": "Продвинутые"},
    "batch_processor": {"name": "Пакетный обработчик", "desc": "Обработать CSV с 10+ уравнениями", "icon": "📦",
                        "category": "Продвинутые"},
    "symPy_user": {"name": "SymPy-пользователь", "desc": "Решить уравнение аналитически", "icon": "🔬",
                   "category": "Продвинутые"},
    "parameter_animator": {"name": "Аниматор параметров", "desc": "Анимировать параметр формулы", "icon": "🎬",
                           "category": "Продвинутые"},
    "multi_formula": {"name": "Мульти-формулист", "desc": "Добавить 5+ дополнительных формул", "icon": "➕",
                      "category": "Продвинутые"},
}


class Stats:
    def __init__(self, data_dir):
        self.path = os.path.join(data_dir, "stats.json")
        self.data = self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "total_solves": 0,
                "methods_used": {},
                "unlocked": [],
                "exports": [],
                "fast_solves": 0,
                "newton_fast": 0,
                "brent_count": 0,
                "bisection_count": 0,
                "secant_fast": 0,
                "mpi_slow": 0,
                "total_time_ms": 0,
                "quiz_correct": 0,
                "extrema_found": 0,
                "extra_formulas_added": 0,
                "pdf_exports": 0,
                "excel_exports": 0,
                "tutorial_opened": False,
                "reference_opened": False,
                "glossary_opened": False,
                "graph_zoomed": False,
                "graph_3d_opened": False,
                "contour_opened": False,
                "vector_opened": False,
                "cloud_uploaded": False,
                "batch_processed": 0,
                "sympy_used": False,
                "param_animated": False,
                "sessions": [],
            }

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def record_solve(self, method, iters, time_ms, sigma):
        self.data["total_solves"] = self.data.get("total_solves", 0) + 1
        if "methods_used" not in self.data:
            self.data["methods_used"] = {}
        self.data["methods_used"][method] = self.data["methods_used"].get(method, 0) + 1
        self.data["total_time_ms"] = self.data.get("total_time_ms", 0) + time_ms

        # Скорость
        if time_ms < 100:
            self.data["fast_solves"] = self.data.get("fast_solves", 0) + 1

        # Методы — используем .get() с дефолтом 0
        if method == "newton" and iters < 5:
            self.data["newton_fast"] = self.data.get("newton_fast", 0) + 1
        if method == "brent":
            self.data["brent_count"] = self.data.get("brent_count", 0) + 1
        if method == "bisection":
            self.data["bisection_count"] = self.data.get("bisection_count", 0) + 1
        if method == "secant" and iters < 10:
            self.data["secant_fast"] = self.data.get("secant_fast", 0) + 1
        if method == "mpi" and iters > 100:
            self.data["mpi_slow"] = self.data.get("mpi_slow", 0) + 1

        # Точность
        if sigma < 1e-12:
            self.data["precision"] = True
        if sigma < 1e-15:
            self.data["ultra_precision"] = True
        if sigma > 0.01:
            self.data["rough_estimate"] = True

        # Время суток
        from datetime import datetime
        hour = datetime.now().hour
        if hour >= 0 and hour < 6:
            self.data["night_owl"] = True

        self.save()

    def record_export(self, fmt):
        if fmt not in self.data["exports"]:
            self.data["exports"].append(fmt)
        if fmt == "pdf":
            self.data["pdf_exports"] = self.data.get("pdf_exports", 0) + 1
        if fmt == "xlsx":
            self.data["excel_exports"] = self.data.get("excel_exports", 0) + 1
        self.save()

    def record_quiz_correct(self):
        self.data["quiz_correct"] = self.data.get("quiz_correct", 0) + 1
        self.save()

    def record_extrema(self):
        self.data["extrema_found"] = self.data.get("extrema_found", 0) + 1
        self.save()

    def record_extra_formula(self):
        self.data["extra_formulas_added"] = self.data.get("extra_formulas_added", 0) + 1
        self.save()

    def record_batch(self, count):
        self.data["batch_processed"] = self.data.get("batch_processed", 0) + count
        self.save()

    def check_achievements(self):
        new = []
        d = self.data
        checks = [
            # Базовые
            ("first_solve", d["total_solves"] >= 1),
            ("ten_solves", d["total_solves"] >= 10),
            ("hundred_solves", d["total_solves"] >= 100),
            ("thousand_solves", d["total_solves"] >= 1000),
            # Методы
            ("newton_master", d.get("newton_fast", 0) >= 10),
            ("brent_fan", d.get("brent_count", 0) >= 20),
            ("bisection_pro", d.get("bisection_count", 0) >= 50),
            ("all_methods", len(d.get("methods_used", {})) >= 6),
            ("secant_speed", d.get("secant_fast", 0) >= 5),
            ("mpi_patience", d.get("mpi_slow", 0) >= 3),
            # Скорость
            ("speed_demon", d.get("fast_solves", 0) >= 1),
            ("lightning", d.get("fast_solves", 0) >= 10),
            ("marathon", d.get("total_time_ms", 0) >= 3600000),
            ("night_owl", d.get("night_owl", False)),
            # Точность
            ("precision", d.get("precision", False)),
            ("ultra_precision", d.get("ultra_precision", False)),
            ("rough_estimate", d.get("rough_estimate", False)),
            # Экспорт
            ("exporter", len(d.get("exports", [])) >= 3),
            ("pdf_master", d.get("pdf_exports", 0) >= 10),
            ("excel_guru", d.get("excel_exports", 0) >= 10),
            ("latex_scholar", "tex" in d.get("exports", [])),
            ("svg_artist", "svg" in d.get("exports", [])),
            # Обучение
            ("student", d.get("tutorial_opened", False)),
            ("quiz_master", d.get("quiz_correct", 0) >= 5),
            ("reference_reader", d.get("reference_opened", False)),
            ("glossary_expert", d.get("glossary_opened", False)),
            # Графика
            ("graph_explorer", d.get("graph_zoomed", False)),
            ("extrema_hunter", d.get("extrema_found", 0) >= 10),
            ("3d_pioneer", d.get("graph_3d_opened", False)),
            ("contour_artist", d.get("contour_opened", False)),
            ("vector_visionary", d.get("vector_opened", False)),
            # Продвинутые
            ("cloud_syncer", d.get("cloud_uploaded", False)),
            ("batch_processor", d.get("batch_processed", 0) >= 10),
            ("symPy_user", d.get("sympy_used", False)),
            ("parameter_animator", d.get("param_animated", False)),
            ("multi_formula", d.get("extra_formulas_added", 0) >= 5),
        ]
        for key, cond in checks:
            if cond and key not in d.get("unlocked", []):
                if "unlocked" not in d:
                    d["unlocked"] = []
                d["unlocked"].append(key)
                new.append(ACHIEVEMENTS[key])
        if new:
            self.save()
        return new