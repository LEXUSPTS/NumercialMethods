# interactive_tutorial.py
"""Интерактивный учебник с примерами и проверкой ответов."""
import math


TUTORIAL_EXAMPLES = {
    "bisection": {
        "title": "Метод бисекции",
        "examples": [
            {
                "name": "Пример 1: Простая парабола",
                "task": "Найдите корень уравнения x² - 4 = 0 на отрезке [0, 3]",
                "eq": "x**2 - 4",
                "a": 0, "b": 3,
                "answer": 2.0,
                "hint": "f(0) = -4, f(3) = 5. Корень между 0 и 3.",
                "steps": 25,
            },
            {
                "name": "Пример 2: Кубическое уравнение",
                "task": "Найдите корень x³ - 6x² + 11x - 6 = 0 на [0.5, 1.5]",
                "eq": "x**3 - 6*x**2 + 11*x - 6",
                "a": 0.5, "b": 1.5,
                "answer": 1.0,
                "hint": "Корни этого уравнения: 1, 2, 3. На отрезке — корень 1.",
                "steps": 30,
            },
            {
                "name": "Пример 3: Тригонометрия",
                "task": "Решите sin(x) - 0.5 = 0 на [0, 2]",
                "eq": "math.sin(x) - 0.5",
                "a": 0, "b": 2,
                "answer": math.pi / 6,
                "hint": "sin(π/6) = 0.5. π/6 ≈ 0.5236",
                "steps": 28,
            },
        ]
    },
    "newton": {
        "title": "Метод Ньютона",
        "examples": [
            {
                "name": "Пример 1: Квадратное",
                "task": "Найдите корень x² - 4 = 0, начальное приближение x₀ = 3",
                "eq": "x**2 - 4",
                "x0": 3,
                "answer": 2.0,
                "hint": "f'(x) = 2x. Формула: x_{n+1} = x_n - (x_n² - 4) / (2x_n)",
                "steps": 5,
            },
            {
                "name": "Пример 2: Экспонента",
                "task": "Решите eˣ - 2 = 0, x₀ = 1",
                "eq": "math.exp(x) - 2",
                "x0": 1,
                "answer": math.log(2),
                "hint": "Ответ: x = ln(2) ≈ 0.6931",
                "steps": 5,
            },
            {
                "name": "Пример 3: Трансцендентное",
                "task": "Решите x - cos(x) = 0, x₀ = 0.5",
                "eq": "x - math.cos(x)",
                "x0": 0.5,
                "answer": 0.7390851332,
                "hint": "Это уравнение не решается аналитически. Численный ответ ≈ 0.7391",
                "steps": 4,
            },
        ]
    },
    "integral": {
        "title": "Численное интегрирование",
        "examples": [
            {
                "name": "Пример 1: Простой интеграл",
                "task": "Вычислите ∫₀¹ x² dx",
                "eq": "x**2",
                "a": 0, "b": 1,
                "answer": 1 / 3,
                "hint": "Аналитически: [x³/3]₀¹ = 1/3 ≈ 0.3333",
                "method": "simpson",
            },
            {
                "name": "Пример 2: Тригонометрия",
                "task": "Вычислите ∫₀^π sin(x) dx",
                "eq": "math.sin(x)",
                "a": 0, "b": math.pi,
                "answer": 2.0,
                "hint": "Аналитически: [-cos(x)]₀^π = -cos(π) + cos(0) = 1 + 1 = 2",
                "method": "simpson",
            },
            {
                "name": "Пример 3: Экспонента",
                "task": "Вычислите ∫₀¹ eˣ dx",
                "eq": "math.exp(x)",
                "a": 0, "b": 1,
                "answer": math.e - 1,
                "hint": "Аналитически: [eˣ]₀¹ = e - 1 ≈ 1.7183",
                "method": "simpson",
            },
        ]
    },
}


def check_answer(user_answer, correct, tolerance=1e-3):
    """Проверить ответ пользователя."""
    try:
        user_val = float(user_answer)
        error = abs(user_val - correct)
        rel_error = error / max(abs(correct), 1e-10)
        return {
            "correct": error < tolerance or rel_error < 1e-3,
            "error": error,
            "rel_error": rel_error * 100,
            "user": user_val,
            "correct_val": correct,
        }
    except (ValueError, TypeError):
        return {"correct": False, "error": None, "user": user_answer,
                "correct_val": correct}