# step_by_step.py
"""Пошаговое решение численных методов с объяснениями."""
import math


def bisection_steps(f, a, b, sigma, max_steps=10):
    """Пошаговая демонстрация метода бисекции."""
    steps = []
    fa, fb = f(a), f(b)
    if fa * fb >= 0:
        return [{"type": "error", "text": "f(a)·f(b) ≥ 0 — корень не отделён"}]

    steps.append({
        "type": "info",
        "title": "Начальные условия",
        "text": f"Интервал: [{a}; {b}]\n"
                f"f(a) = {fa:.6f}\n"
                f"f(b) = {fb:.6f}\n"
                f"Знаки разные → корень на отрезке ✓",
        "formula": "f(a) · f(b) < 0"
    })

    k = 0
    while (b - a) > sigma and k < max_steps:
        k += 1
        c = (a + b) / 2
        fc = f(c)
        if fa * fc <= 0:
            note = f"f(a)·f(c) = {fa:.4f}·{fc:.4f} ≤ 0 → корень в [{a:.6f}; {c:.6f}]"
            b = c
            fb = fc
        else:
            note = f"f(a)·f(c) = {fa:.4f}·{fc:.4f} > 0 → корень в [{c:.6f}; {b:.6f}]"
            a = c
            fa = fc
        steps.append({
            "type": "step",
            "title": f"Шаг {k}",
            "text": f"c = (a + b) / 2 = {c:.6f}\n"
                    f"f(c) = {fc:.6f}\n"
                    f"|b - a| = {abs(b - a):.6f}\n\n"
                    f"{note}",
            "formula": "c = (a + b) / 2",
            "values": {"a": a, "b": b, "c": c, "fc": fc}
        })

    steps.append({
        "type": "result",
        "title": "Результат",
        "text": f"Корень: x ≈ {(a + b) / 2:.10f}\n"
                f"Погрешность: |b - a| = {abs(b - a):.2e} < σ = {sigma}",
        "formula": f"x ≈ (a + b) / 2 = {(a + b) / 2:.10f}"
    })
    return steps


def newton_steps(f, df, x0, sigma, max_steps=10):
    """Пошаговая демонстрация метода Ньютона."""
    steps = []
    steps.append({
        "type": "info",
        "title": "Начальные условия",
        "text": f"x₀ = {x0}\n"
                f"f(x₀) = {f(x0):.6f}\n"
                f"f'(x₀) = {df(x0):.6f}",
        "formula": "x_{n+1} = x_n - f(x_n) / f'(x_n)"
    })

    x = x0
    for k in range(1, max_steps + 1):
        fx = f(x)
        dfx = df(x)
        if abs(dfx) < 1e-15:
            steps.append({"type": "error", "text": f"f'(x_{k}) = 0 — деление на ноль"})
            break
        x_new = x - fx / dfx
        steps.append({
            "type": "step",
            "title": f"Шаг {k}",
            "text": f"x_{k} = {x:.6f}\n"
                    f"f(x_{k}) = {fx:.6f}\n"
                    f"f'(x_{k}) = {dfx:.6f}\n"
                    f"x_{k+1} = {x:.6f} - ({fx:.6f}) / ({dfx:.6f}) = {x_new:.6f}\n"
                    f"|x_{k+1} - x_{k}| = {abs(x_new - x):.2e}",
            "formula": f"x_{{{k+1}}} = x_{{{k}}} - f(x_{{{k}}}) / f'(x_{{{k}}})",
            "values": {"x_prev": x, "x_new": x_new, "fx": fx, "dfx": dfx}
        })
        if abs(x_new - x) < sigma:
            break
        x = x_new

    steps.append({
        "type": "result",
        "title": "Результат",
        "text": f"Корень: x ≈ {x:.10f}\n"
                f"f(x) = {f(x):.2e}",
        "formula": f"x ≈ {x:.10f}"
    })
    return steps


def chord_steps(f, a, b, sigma, max_steps=10):
    """Пошаговая демонстрация метода хорд."""
    steps = []
    fa, fb = f(a), f(b)
    if fa * fb >= 0:
        return [{"type": "error", "text": "f(a)·f(b) ≥ 0"}]

    h = 1e-5
    d2f_a = (f(a + h) - 2 * f(a) + f(a - h)) / (h * h)
    d2f_b = (f(b + h) - 2 * f(b) + f(b - h)) / (h * h)
    if fa * d2f_a > 0:
        x_fixed, x_moving = a, b
        f_fixed = fa
    else:
        x_fixed, x_moving = b, a
        f_fixed = fb

    steps.append({
        "type": "info",
        "title": "Начальные условия",
        "text": f"Закреплённый конец: x₀ = {x_fixed:.6f}\n"
                f"Подвижный конец: x₁ = {x_moving:.6f}\n"
                f"Правило выбора: f(x₀)·f''(x₀) > 0",
        "formula": "x_{n+1} = x₀ - f(x₀)·(x_n - x₀) / (f(x_n) - f(x₀))"
    })

    x_prev = x_moving
    for k in range(1, max_steps + 1):
        fx_prev = f(x_prev)
        denom = fx_prev - f_fixed
        if abs(denom) < 1e-15:
            break
        x_new = x_fixed - f_fixed * (x_prev - x_fixed) / denom
        steps.append({
            "type": "step",
            "title": f"Шаг {k}",
            "text": f"x_{k} = {x_prev:.6f}\n"
                    f"f(x_{k}) = {fx_prev:.6f}\n"
                    f"x_{k+1} = {x_fixed:.6f} - ({f_fixed:.6f})·({x_prev:.6f} - {x_fixed:.6f}) / "
                    f"({fx_prev:.6f} - {f_fixed:.6f})\n"
                    f"x_{k+1} = {x_new:.6f}\n"
                    f"|x_{k+1} - x_{k}| = {abs(x_new - x_prev):.2e}",
            "formula": "x_{n+1} = x₀ - f(x₀)·(x_n - x₀) / (f(x_n) - f(x₀))",
            "values": {"x_prev": x_prev, "x_new": x_new}
        })
        if abs(x_new - x_prev) < sigma:
            break
        x_prev = x_new

    steps.append({
        "type": "result",
        "title": "Результат",
        "text": f"Корень: x ≈ {x_prev:.10f}\n"
                f"f(x) = {f(x_prev):.2e}",
        "formula": f"x ≈ {x_prev:.10f}"
    })
    return steps