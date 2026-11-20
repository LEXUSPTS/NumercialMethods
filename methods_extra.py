# methods_extra.py
"""Расширенные численные методы."""
import math
import cmath
import random


def brent_method(f, a, b, sigma=1e-8, max_step=500):
    """Метод Брента — гибрид бисекции, секущих и ОКИ."""
    history = []
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None, history
    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb = fb, fa
    c, fc = a, fa
    mflag = True
    s, d = 0.0, 0.0
    for k in range(1, max_step + 1):
        if abs(fb) < 1e-15 or abs(b - a) < sigma:
            history.append((k, a, b, b, fb, abs(b - a)))
            return b, history
        if abs(fa - fc) > 1e-15 and abs(fb - fc) > 1e-15:
            s = (a * fb * fc) / ((fa - fb) * (fa - fc)) + \
                (b * fa * fc) / ((fb - fa) * (fb - fc)) + \
                (c * fa * fb) / ((fc - fa) * (fc - fb))
        else:
            s = b - fb * (b - a) / (fb - fa)
        cond1 = not ((3 * a + b) / 4 <= s <= b if b < (3 * a + b) / 4 else b <= s <= (3 * a + b) / 4)
        cond2 = mflag and abs(s - b) >= abs(b - c) / 2
        cond3 = (not mflag) and abs(s - b) >= abs(c - d) / 2
        cond4 = mflag and abs(b - c) < sigma
        cond5 = (not mflag) and abs(c - d) < sigma
        if cond1 or cond2 or cond3 or cond4 or cond5:
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False
        fs = f(s)
        d = c
        c, fc = b, fb
        history.append((k, a, b, s, fs, abs(b - a)))
        if fa * fs < 0:
            b, fb = s, fs
        else:
            a, fa = s, fs
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa
    return b, history


def simple_iteration(f, a, b, sigma=1e-8, max_step=500):
    """Метод простой итерации."""
    history = []
    x = (a + b) / 2
    h = (b - a) / 20
    M = 0.0
    for i in range(21):
        xi = a + i * h
        try:
            dfx = (f(xi + 1e-6) - f(xi - 1e-6)) / 2e-6
            M = max(M, abs(dfx))
        except Exception:
            pass
    if M < 1e-12:
        M = 1.0
    for k in range(1, max_step + 1):
        fx = f(x)
        x_new = x - fx / M
        history.append((k, x, x_new, f(x_new), abs(x_new - x)))
        if abs(x_new - x) < sigma:
            return x_new, history
        x = x_new
    return x, history


def muller_method(f, x0, x1, x2, sigma=1e-8, max_step=200):
    """Метод Мюллера — квадратичная интерполяция."""
    history = []
    for k in range(1, max_step + 1):
        f0, f1, f2 = f(x0), f(x1), f(x2)
        h1 = x1 - x0
        h2 = x2 - x1
        d1 = (f1 - f0) / h1 if abs(h1) > 1e-15 else 0
        d2 = (f2 - f1) / h2 if abs(h2) > 1e-15 else 0
        a_coef = (d2 - d1) / (h2 + h1) if abs(h2 + h1) > 1e-15 else 0
        b_coef = d2 + a_coef * h2
        c_coef = f2
        disc = cmath.sqrt(b_coef * b_coef - 4 * a_coef * c_coef)
        if abs(b_coef + disc) > abs(b_coef - disc):
            denom = b_coef + disc
        else:
            denom = b_coef - disc
        if abs(denom) < 1e-15:
            break
        dx = -2 * c_coef / denom
        x3 = x2 + dx
        history.append((k, x2, x3, f(x3) if isinstance(x3, (int, float)) else abs(f(x3)),
                        abs(dx) if isinstance(dx, (int, float)) else abs(dx)))
        if abs(dx) < sigma:
            return x3 if isinstance(x3, (int, float)) else x3.real, history
        x0, x1, x2 = x1, x2, x3
    return x2, history


def ridders_method(f, a, b, sigma=1e-8, max_step=200):
    """Метод Риддерса."""
    history = []
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None, history
    for k in range(1, max_step + 1):
        c = (a + b) / 2
        fc = f(c)
        if abs(fc) < 1e-15:
            history.append((k, a, b, c, fc, abs(b - a)))
            return c, history
        s = math.sqrt(fc * fc - fa * fb)
        if s < 1e-15:
            history.append((k, a, b, c, fc, abs(b - a)))
            return c, history
        sign = 1 if fa > fb else -1
        x_new = c + (c - a) * sign * fc / s
        f_new = f(x_new)
        history.append((k, a, b, x_new, f_new, abs(b - a)))
        if abs(f_new) < 1e-15 or abs(b - a) < sigma:
            return x_new, history
        if fc * f_new < 0:
            a, b = c, x_new
            fa, fb = fc, f_new
        elif fa * f_new < 0:
            b = x_new
            fb = f_new
        else:
            a = x_new
            fa = f_new
    return (a + b) / 2, history


def inverse_quadratic_interpolation(f, a, b, sigma=1e-8, max_step=200):
    """Обратная квадратичная интерполяция."""
    history = []
    c = (a + b) / 2
    x0, x1, x2 = a, b, c
    f0, f1, f2 = f(x0), f(x1), f(x2)
    for k in range(1, max_step + 1):
        if abs(f0 - f1) < 1e-15 or abs(f1 - f2) < 1e-15 or abs(f0 - f2) < 1e-15:
            if abs(f2 - f1) > 1e-15:
                x_new = x2 - f2 * (x2 - x1) / (f2 - f1)
            else:
                break
        else:
            x_new = (x0 * f1 * f2) / ((f0 - f1) * (f0 - f2)) + \
                    (x1 * f0 * f2) / ((f1 - f0) * (f1 - f2)) + \
                    (x2 * f0 * f1) / ((f2 - f0) * (f2 - f1))
        f_new = f(x_new)
        history.append((k, x2, x_new, f_new, abs(x_new - x2)))
        if abs(x_new - x2) < sigma:
            return x_new, history
        x0, x1, x2 = x1, x2, x_new
        f0, f1, f2 = f1, f2, f_new
    return x2, history


def _bisection_simple(f, a, b, sigma):
    """Простая бисекция без истории."""
    history = []
    fa, fb = f(a), f(b)
    if fa * fb >= 0:
        return None, history
    k = 0
    while (b - a) > sigma and k < 1000:
        c = (a + b) / 2
        fc = f(c)
        history.append((k + 1, a, b, c, fc, abs(b - a)))
        if fa * fc <= 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        k += 1
    return (a + b) / 2, history


def find_all_roots(f, a, b, sigma=1e-8, n_segments=100, method="brent"):
    """Поиск всех корней на отрезке."""
    roots = []
    h = (b - a) / n_segments
    for i in range(n_segments):
        a_i = a + i * h
        b_i = a + (i + 1) * h
        try:
            fa, fb = f(a_i), f(b_i)
        except Exception:
            continue
        if fa * fb <= 0:
            if method == "brent":
                root, _ = brent_method(f, a_i, b_i, sigma)
            elif method == "ridders":
                root, _ = ridders_method(f, a_i, b_i, sigma)
            else:
                root, _ = _bisection_simple(f, a_i, b_i, sigma)
            if root is not None:
                if not any(abs(root - r) < sigma * 100 for r in roots):
                    roots.append(root)
    return sorted(roots)


def golden_section_minimum(f, a, b, sigma=1e-8, max_step=500):
    """Поиск минимума методом золотого сечения."""
    history = []
    phi = (math.sqrt(5) - 1) / 2
    x1 = b - phi * (b - a)
    x2 = a + phi * (b - a)
    f1, f2 = f(x1), f(x2)
    for k in range(1, max_step + 1):
        history.append((k, a, b, (a + b) / 2, f((a + b) / 2), abs(b - a)))
        if abs(b - a) < sigma:
            return (a + b) / 2, history
        if f1 < f2:
            b = x2
            x2, f2 = x1, f1
            x1 = b - phi * (b - a)
            f1 = f(x1)
        else:
            a = x1
            x1, f1 = x2, f2
            x2 = a + phi * (b - a)
            f2 = f(x2)
    return (a + b) / 2, history


def integrate_trapezoid(f, a, b, n=1000):
    """Метод трапеций."""
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h


def integrate_simpson(f, a, b, n=1000):
    """Метод Симпсона."""
    if n % 2 != 0:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n, 2):
        s += 4 * f(a + i * h)
    for i in range(2, n - 1, 2):
        s += 2 * f(a + i * h)
    return s * h / 3


def integrate_gauss(f, a, b, n=5):
    """Метод Гаусса (5-точечный)."""
    nodes = [-0.90618, -0.53847, 0, 0.53847, 0.90618]
    weights = [0.23693, 0.47863, 0.56889, 0.47863, 0.23693]
    mid = (a + b) / 2
    half = (b - a) / 2
    s = 0.0
    for xi, wi in zip(nodes[:n], weights[:n]):
        s += wi * f(mid + half * xi)
    return s * half


def integrate_monte_carlo(f, a, b, n=10000):
    """Метод Монте-Карло."""
    total = 0.0
    for _ in range(n):
        x = random.uniform(a, b)
        total += f(x)
    return (b - a) * total / n


def integrate_adaptive_simpson(f, a, b, sigma=1e-8, max_depth=20):
    """Адаптивный Симпсон."""
    def _simpson(a, b):
        c = (a + b) / 2
        h = (b - a) / 6
        return h * (f(a) + 4 * f(c) + f(b))

    def _recursive(a, b, whole, fa, fb, fc, depth, sigma):
        c = (a + b) / 2
        d = (a + c) / 2
        e = (c + b) / 2
        fd = f(d)
        fe = f(e)
        left = (c - a) / 6 * (fa + 4 * fd + fc)
        right = (b - c) / 6 * (fc + 4 * fe + fb)
        total = left + right
        if depth <= 0 or abs(total - whole) <= 15 * sigma:
            return total + (total - whole) / 15
        return (_recursive(a, c, left, fa, fc, fd, depth - 1, sigma / 2) +
                _recursive(c, b, right, fc, fb, fe, depth - 1, sigma / 2))

    fa, fb = f(a), f(b)
    fc = f((a + b) / 2)
    whole = _simpson(a, b)
    return _recursive(a, b, whole, fa, fb, fc, max_depth, sigma)


def lagrange_interpolation(points, x):
    """Интерполяция Лагранжа."""
    n = len(points)
    result = 0.0
    for i in range(n):
        xi, yi = points[i]
        term = yi
        for j in range(n):
            if i != j:
                xj = points[j][0]
                term *= (x - xj) / (xi - xj)
        result += term
    return result


def cubic_spline(points):
    """Кубический сплайн."""
    points = sorted(points, key=lambda p: p[0])
    n = len(points) - 1
    if n < 1:
        return lambda x: points[0][1] if points else 0
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    h = [x[i + 1] - x[i] for i in range(n)]
    alpha = [0] * (n + 1)
    for i in range(1, n):
        alpha[i] = (3 / h[i]) * (y[i + 1] - y[i]) - (3 / h[i - 1]) * (y[i] - y[i - 1])
    l = [1] + [0] * n
    mu = [0] * (n + 1)
    z = [0] * (n + 1)
    for i in range(1, n):
        l[i] = 2 * (x[i + 1] - x[i - 1]) - h[i - 1] * mu[i - 1]
        mu[i] = h[i] / l[i]
        z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]
    l[n] = 1
    z[n] = 0
    c = [0] * (n + 1)
    b = [0] * n
    d = [0] * n
    for j in range(n - 1, -1, -1):
        c[j] = z[j] - mu[j] * c[j + 1]
        b[j] = (y[j + 1] - y[j]) / h[j] - h[j] * (c[j + 1] + 2 * c[j]) / 3
        d[j] = (c[j + 1] - c[j]) / (3 * h[j])
    a_coef = y[:-1]

    def S(xi):
        if xi <= x[0]:
            return y[0]
        if xi >= x[-1]:
            return y[-1]
        for i in range(n):
            if x[i] <= xi <= x[i + 1]:
                dx = xi - x[i]
                return a_coef[i] + b[i] * dx + c[i] * dx ** 2 + d[i] * dx ** 3
        return y[-1]

    return S


def least_squares_linear(points):
    """Линейная аппроксимация y = a*x + b."""
    n = len(points)
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sxx = sum(p[0] ** 2 for p in points)
    sxy = sum(p[0] * p[1] for p in points)
    det = n * sxx - sx * sx
    if abs(det) < 1e-15:
        return None, None
    a = (n * sxy - sx * sy) / det
    b = (sy * sxx - sx * sxy) / det
    return a, b


def least_squares_polynomial(points, degree):
    """Полиномиальная аппроксимация."""
    n = len(points)
    if degree >= n:
        degree = n - 1
    A = [[0] * (degree + 1) for _ in range(degree + 1)]
    b_vec = [0] * (degree + 1)
    for i in range(degree + 1):
        for j in range(degree + 1):
            s = sum(p[0] ** (i + j) for p in points)
            A[i][j] = s
        b_vec[i] = sum((p[0] ** i) * p[1] for p in points)
    return gauss_elimination(A, b_vec)


def gauss_elimination(A, b_vec):
    """Метод Гаусса."""
    n = len(b_vec)
    M = [row[:] + [b_vec[i]] for i, row in enumerate(A)]
    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[max_row] = M[max_row], M[i]
        if abs(M[i][i]) < 1e-15:
            raise ValueError("Матрица вырождена")
        for j in range(i + 1, n):
            factor = M[j][i] / M[i][i]
            for k in range(i, n + 1):
                M[j][k] -= factor * M[i][k]
    x = [0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def jacobi_method(A, b_vec, x0=None, sigma=1e-8, max_iter=1000):
    """Метод Якоби."""
    n = len(b_vec)
    x = x0[:] if x0 else [0] * n
    history = []
    for k in range(1, max_iter + 1):
        x_new = [0] * n
        for i in range(n):
            s = sum(A[i][j] * x[j] for j in range(n) if j != i)
            if abs(A[i][i]) < 1e-15:
                raise ValueError("Нуль на диагонали")
            x_new[i] = (b_vec[i] - s) / A[i][i]
        err = max(abs(x_new[i] - x[i]) for i in range(n))
        history.append((k, x[:], x_new[:], err))
        if err < sigma:
            return x_new, history
        x = x_new
    return x, history


def seidel_method(A, b_vec, x0=None, sigma=1e-8, max_iter=1000):
    """Метод Зейделя."""
    n = len(b_vec)
    x = x0[:] if x0 else [0] * n
    history = []
    for k in range(1, max_iter + 1):
        x_old = x[:]
        for i in range(n):
            s1 = sum(A[i][j] * x[j] for j in range(i))
            s2 = sum(A[i][j] * x[j] for j in range(i + 1, n))
            if abs(A[i][i]) < 1e-15:
                raise ValueError("Нуль на диагонали")
            x[i] = (b_vec[i] - s1 - s2) / A[i][i]
        err = max(abs(x[i] - x_old[i]) for i in range(n))
        history.append((k, x_old[:], x[:], err))
        if err < sigma:
            return x, history
    return x, history


def tridiagonal_solver(a, b, c, d):
    """Метод прогонки."""
    n = len(d)
    alpha = [0] * n
    beta = [0] * n
    if abs(b[0]) < 1e-15:
        raise ValueError("Нуль на диагонали")
    alpha[0] = -c[0] / b[0]
    beta[0] = d[0] / b[0]
    for i in range(1, n - 1):
        denom = b[i] + a[i] * alpha[i - 1]
        if abs(denom) < 1e-15:
            raise ValueError("Нулевой знаменатель")
        alpha[i] = -c[i] / denom
        beta[i] = (d[i] - a[i] * beta[i - 1]) / denom
    x = [0] * n
    if abs(b[n - 1] + a[n - 1] * alpha[n - 2]) < 1e-15:
        raise ValueError("Нулевой знаменатель")
    x[n - 1] = (d[n - 1] - a[n - 1] * beta[n - 2]) / (b[n - 1] + a[n - 1] * alpha[n - 2])
    for i in range(n - 2, -1, -1):
        x[i] = alpha[i] * x[i + 1] + beta[i]
    return x


def newton_system(F, J, x0, sigma=1e-8, max_iter=100):
    """Метод Ньютона для системы."""
    x = x0[:]
    n = len(x)
    history = []
    for k in range(1, max_iter + 1):
        Fx = F(x)
        Jx = J(x)
        try:
            delta = gauss_elimination(Jx, [-fx for fx in Fx])
        except ValueError:
            break
        x_new = [x[i] + delta[i] for i in range(n)]
        err = max(abs(delta[i]) for i in range(n))
        history.append((k, x[:], x_new[:], err))
        if err < sigma:
            return x_new, history
        x = x_new
    return x, history


def numerical_derivative(f, x, h=1e-5, order=1):
    """Численная производная."""
    if order == 1:
        return (f(x + h) - f(x - h)) / (2 * h)
    elif order == 2:
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)
    elif order == 3:
        return (-f(x - 2 * h) + 2 * f(x - h) - 2 * f(x + h) + f(x + 2 * h)) / (2 * h ** 3)
    elif order == 4:
        return (f(x - 2 * h) - 4 * f(x - h) + 6 * f(x) - 4 * f(x + h) + f(x + 2 * h)) / (h ** 4)
    else:
        raise ValueError(f"Порядок {order} не поддерживается")


def richardson_derivative(f, x, h=0.1, order=1, steps=5):
    """Производная с экстраполяцией Ричардсона."""
    table = [[0] * steps for _ in range(steps)]
    for i in range(steps):
        hi = h / (2 ** i)
        if order == 1:
            table[i][0] = (f(x + hi) - f(x - hi)) / (2 * hi)
        else:
            table[i][0] = (f(x + hi) - 2 * f(x) + f(x - hi)) / (hi * hi)
    for j in range(1, steps):
        for i in range(steps - j):
            factor = 4 ** j
            table[i][j] = (factor * table[i + 1][j - 1] - table[i][j - 1]) / (factor - 1)
    return table[0][steps - 1]


def euler_method(f, x0, y0, x_end, n=100):
    """Метод Эйлера."""
    h = (x_end - x0) / n
    x, y = x0, y0
    points = [(x, y)]
    for _ in range(n):
        y = y + h * f(x, y)
        x = x + h
        points.append((x, y))
    return points


def runge_kutta_4(f, x0, y0, x_end, n=100):
    """Метод Рунге-Кутты 4-го порядка."""
    h = (x_end - x0) / n
    x, y = x0, y0
    points = [(x, y)]
    for _ in range(n):
        k1 = h * f(x, y)
        k2 = h * f(x + h / 2, y + k1 / 2)
        k3 = h * f(x + h / 2, y + k2 / 2)
        k4 = h * f(x + h, y + k3)
        y = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x = x + h
        points.append((x, y))
    return points


def runge_kutta_fehlberg(f, x0, y0, x_end, sigma=1e-6, h0=0.1):
    """Метод Рунге-Кутты-Фельберга."""
    x, y = x0, y0
    h = h0
    points = [(x, y)]
    steps = 0
    while x < x_end and steps < 10000:
        if x + h > x_end:
            h = x_end - x
        k1 = h * f(x, y)
        k2 = h * f(x + h / 4, y + k1 / 4)
        k3 = h * f(x + 3 * h / 8, y + 3 * k1 / 32 + 9 * k2 / 32)
        k4 = h * f(x + 12 * h / 13, y + 1932 * k1 / 2197 - 7200 * k2 / 2197 + 7296 * k3 / 2197)
        k5 = h * f(x + h, y + 439 * k1 / 216 - 8 * k2 + 3680 * k3 / 513 - 845 * k4 / 4104)
        k6 = h * f(x + h / 2, y - 8 * k1 / 27 + 2 * k2 - 3544 * k3 / 2565 + 1859 * k4 / 4104 - 11 * k5 / 40)
        y4 = y + 25 * k1 / 216 + 1408 * k3 / 2565 + 2197 * k4 / 4104 - k5 / 5
        y5 = y + 16 * k1 / 135 + 6656 * k3 / 12825 + 28561 * k4 / 56430 - 9 * k5 / 50 + 2 * k6 / 55
        err = abs(y5 - y4)
        if err < sigma or h < 1e-10:
            y = y5
            x = x + h
            points.append((x, y))
            h = min(h * 1.2, (x_end - x0) / 10)
        else:
            h = max(h * 0.5, 1e-10)
        steps += 1
    return points, steps


def fourier_analysis(signal, sample_rate=1.0):
    """Дискретное преобразование Фурье."""
    N = len(signal)
    freqs, magnitudes, phases = [], [], []
    for k in range(N // 2):
        real = 0.0
        imag = 0.0
        for n in range(N):
            angle = -2 * math.pi * k * n / N
            real += signal[n] * math.cos(angle)
            imag += signal[n] * math.sin(angle)
        mag = math.sqrt(real * real + imag * imag) / N
        phase = math.atan2(imag, real)
        freqs.append(k * sample_rate / N)
        magnitudes.append(mag)
        phases.append(phase)
    return freqs, magnitudes, phases


def fft_simple(x):
    """Быстрое преобразование Фурье."""
    N = len(x)
    if N <= 1:
        return [complex(v) for v in x]
    if N % 2 != 0:
        raise ValueError("Длина должна быть степенью 2")
    even = fft_simple(x[0::2])
    odd = fft_simple(x[1::2])
    T = [cmath.exp(-2j * cmath.pi * k / N) * odd[k] for k in range(N // 2)]
    return [even[k] + T[k] for k in range(N // 2)] + \
           [even[k] - T[k] for k in range(N // 2)]


def ifft_simple(X):
    """Обратное БПФ."""
    N = len(X)
    conjugated = [z.conjugate() for z in X]
    transformed = fft_simple(conjugated)
    return [z.conjugate() / N for z in transformed]


def condition_number(A):
    """Число обусловленности."""
    n = len(A)
    try:
        I_col = [1 if i == 0 else 0 for i in range(n)]
        x = gauss_elimination(A, I_col)
        norm_inv = sum(abs(v) for v in x)
        norm_A = sum(sum(abs(A[i][j]) for j in range(n)) for i in range(n))
        return norm_A * norm_inv
    except Exception:
        return float('inf')


def spectral_radius(A):
    """Спектральный радиус."""
    n = len(A)
    if n == 1:
        return abs(A[0][0])
    if n == 2:
        tr = A[0][0] + A[1][1]
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        disc = tr * tr - 4 * det
        if disc >= 0:
            l1 = (tr + math.sqrt(disc)) / 2
            l2 = (tr - math.sqrt(disc)) / 2
            return max(abs(l1), abs(l2))
        else:
            return math.sqrt(det)
    x = [1] * n
    for _ in range(100):
        x_new = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
        norm = max(abs(v) for v in x_new)
        if norm < 1e-15:
            return 0
        x = [v / norm for v in x_new]
    return norm


def convergence_order(errors):
    """Оценка порядка сходимости."""
    if len(errors) < 3:
        return None
    orders = []
    for i in range(1, len(errors) - 1):
        if errors[i - 1] > 1e-15 and errors[i] > 1e-15 and errors[i + 1] > 1e-15:
            try:
                p = math.log(errors[i + 1] / errors[i]) / math.log(errors[i] / errors[i - 1])
                orders.append(p)
            except (ValueError, ZeroDivisionError):
                pass
    return sum(orders) / len(orders) if orders else None


def check_diagonal_dominance(A):
    """Проверка диагонального преобладания."""
    n = len(A)
    for i in range(n):
        diag = abs(A[i][i])
        off_diag = sum(abs(A[i][j]) for j in range(n) if j != i)
        if diag <= off_diag:
            return False
    return True


def matrix_multiply(A, B):
    """Умножение матриц."""
    n = len(A)
    m = len(B[0])
    k = len(B)
    C = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            C[i][j] = sum(A[i][p] * B[p][j] for p in range(k))
    return C


def determinant(A):
    """Определитель матрицы."""
    n = len(A)
    M = [row[:] for row in A]
    det = 1.0
    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        if i != max_row:
            M[i], M[max_row] = M[max_row], M[i]
            det = -det
        if abs(M[i][i]) < 1e-15:
            return 0.0
        det *= M[i][i]
        for j in range(i + 1, n):
            factor = M[j][i] / M[i][i]
            for k in range(i, n):
                M[j][k] -= factor * M[i][k]
    return det


def inverse_matrix(A):
    """Обратная матрица."""
    n = len(A)
    M = [A[i][:] + [1 if i == j else 0 for j in range(n)] for i in range(n)]
    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[max_row] = M[max_row], M[i]
        if abs(M[i][i]) < 1e-15:
            raise ValueError("Матрица вырождена")
        diag = M[i][i]
        for j in range(2 * n):
            M[i][j] /= diag
        for j in range(n):
            if i != j:
                factor = M[j][i]
                for k in range(2 * n):
                    M[j][k] -= factor * M[i][k]
    return [row[n:] for row in M]