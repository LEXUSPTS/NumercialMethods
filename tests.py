import math
from methods_extra import (
    brent_method, simple_iteration, golden_section_minimum,
    integrate_trapezoid, integrate_simpson, integrate_gauss,
    lagrange_interpolation, least_squares_linear
)

def run_all_tests():
    results = []

    def check(name, got, expected, tol=1e-4):
        if got is None:
            results.append((name, False, f"Получено None, ожидалось {expected}"))
            return
        if abs(got - expected) < tol:
            results.append((name, True, f"{got:.6f} ≈ {expected:.6f}"))
        else:
            results.append((name, False, f"{got:.6f} != {expected:.6f}"))

    f1 = lambda x: x**2 - 4
    a, b = 0, 3
    while (b - a) > 1e-8:
        c = (a + b) / 2
        if f1(a) * f1(c) <= 0: b = c
        else: a = c
    check("Бисекция: x²-4 на [0,3]", (a + b) / 2, 2.0)

    root, _ = brent_method(f1, 0, 3, 1e-8)
    check("Брент: x²-4 на [0,3]", root, 2.0)

    root, _ = simple_iteration(f1, 0, 3, 1e-8)
    check("МПИ: x²-4 на [0,3]", root, 2.0)

    x = 1.5
    for _ in range(50):
        fx = x**2 - 4
        dfx = 2 * x
        if abs(dfx) < 1e-15: break
        x = x - fx / dfx
    check("Ньютон: x²-4, старт 1.5", x, 2.0)

    x0, x1 = 0.0, 3.0
    for _ in range(50):
        f0, f1_ = x0**2 - 4, x1**2 - 4
        if abs(f1_ - f0) < 1e-15: break
        x2 = x1 - f1_ * (x1 - x0) / (f1_ - f0)
        if abs(x2 - x1) < 1e-8: break
        x0, x1 = x1, x2
    check("Секущих: x²-4", x1, 2.0)

    f_int = lambda x: x**2
    check("Трапеции: ∫₀¹ x² dx", integrate_trapezoid(f_int, 0, 1, 1000), 1/3, 1e-4)
    check("Симпсон: ∫₀¹ x² dx", integrate_simpson(f_int, 0, 1, 100), 1/3, 1e-8)
    check("Гаусс: ∫₀¹ x² dx", integrate_gauss(f_int, 0, 1, 5), 1/3, 1e-8)

    f_sin = math.sin
    check("Симпсон: ∫₀^π sin(x) dx", integrate_simpson(f_sin, 0, math.pi, 100), 2.0, 1e-8)

    points = [(0, 0), (1, 1), (2, 4)]
    check("Лагранж: f(1.5) для x²", lagrange_interpolation(points, 1.5), 2.25, 1e-10)

    points = [(0, 1), (1, 3), (2, 5), (3, 7)]
    a_coef, b_coef = least_squares_linear(points)
    check("МНК: a (наклон)", a_coef, 2.0, 1e-10)
    check("МНК: b (сдвиг)", b_coef, 1.0, 1e-10)

    f_min = lambda x: (x - 2)**2
    x_min, _ = golden_section_minimum(f_min, 0, 5, 1e-8)
    check("Золотое сечение: min (x-2)²", x_min, 2.0, 1e-4)

    return results