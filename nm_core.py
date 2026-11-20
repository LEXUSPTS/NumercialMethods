# nm_core.py — корректность: парсер, невязка, полюса, статистика, настройки.
import ast, math, re
import tkinter as tk
from tkinter import messagebox

MAX_LEN, MAX_NODES, MAX_DEPTH, MAX_POW = 400, 300, 40, 1000

FUNCS = {n: getattr(math, n) for n in dir(math)
         if not n.startswith("_") and n not in ("factorial", "comb", "perm")}
FUNCS.update({"abs": abs, "min": min, "max": max, "round": round})
CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


# ─────────────────────────── парсер ───────────────────────────
def normalize(src):
    if len(src) > MAX_LEN:
        raise ValueError("Выражение длиннее %d символов" % MAX_LEN)
    s = src.strip().replace("^", "**").replace("−", "-").replace("·", "*")
    s = re.sub(r"\bmath\.", "", s)
    vault = []

    def hide(m):
        vault.append(m.group(0))
        return "\x00%d\x00" % (len(vault) - 1)

    # защищаем 1e-5 и log10 от порчи неявным умножением
    s = re.sub(r"\d+\.?\d*[eE][+-]?\d+", hide, s)
    s = re.sub(r"\b(log10|log2|atan2|exp2|hypot|fmod)\b", hide, s)
    s = re.sub(r"(\d)([a-zA-Z(])", r"\1*\2", s)
    s = re.sub(r"\)([a-zA-Z0-9(])", r")*\1", s)
    for i, t in enumerate(vault):
        s = s.replace("\x00%d\x00" % i, t)
    if "=" in s:
        l, r = s.split("=", 1)
        s = "(%s)-(%s)" % (l, r)
    return s


def _guard(tree):
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise ValueError("Слишком сложное выражение")

    def depth(n):
        ch = list(ast.iter_child_nodes(n))
        return 1 + (max(depth(c) for c in ch) if ch else 0)
    if depth(tree) > MAX_DEPTH:
        raise ValueError("Слишком глубокая вложенность")

    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and not isinstance(n.value, (int, float)):
            raise ValueError("Разрешены только числа")
        if isinstance(n, ast.Attribute):
            raise ValueError("Пишите sin(x), а не math.sin(x)")
        if isinstance(n, ast.Call):
            if n.keywords:
                raise ValueError("Именованные аргументы не поддержаны")
            if not isinstance(n.func, ast.Name):
                raise ValueError("Недопустимый вызов")
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow):
            if isinstance(n.right, ast.BinOp) and isinstance(n.right.op, ast.Pow):
                raise ValueError("Степень в степени запрещена (9**9**9)")
            if isinstance(n.right, ast.Constant) and abs(n.right.value) > MAX_POW:
                raise ValueError("Показатель степени > %d" % MAX_POW)
        if isinstance(n, (ast.Lambda, ast.Compare, ast.Subscript, ast.IfExp,
                          ast.ListComp, ast.GeneratorExp, ast.Dict, ast.List)):
            raise ValueError("Конструкция запрещена")


def compile_expr(src, variables=None):
    if not src or not src.strip():
        raise ValueError("Пустое выражение")
    try:
        tree = ast.parse(normalize(src), mode="eval")
    except SyntaxError as ex:
        raise ValueError("Синтаксис, позиция %s" % (ex.offset or "?"))
    _guard(tree)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    vs = sorted(n for n in names if n not in FUNCS and n not in CONSTS)
    if not vs:
        vs = ["x"]
    code = compile(tree, "<equation>", "eval")
    G = {"__builtins__": {}}
    G.update(FUNCS)
    G.update(CONSTS)
    return (lambda env: eval(code, G, env)), vs


# ──────────────────── производные и проверка корня ────────────────────
def safe_eval(f, x):
    try:
        y = f(x)
        if isinstance(y, complex):
            return math.nan
        y = float(y)
        return y if math.isfinite(y) else math.nan
    except Exception:
        return math.nan


def df1(f, x, h=None):
    h = 1e-6 * max(1.0, abs(x))
    a, b = safe_eval(f, x + h), safe_eval(f, x - h)
    return math.nan if (math.isnan(a) or math.isnan(b)) else (a - b) / (2 * h)


def df2(f, x, h=None):
    h = 1e-4 * max(1.0, abs(x))
    a, b, c = safe_eval(f, x + h), safe_eval(f, x), safe_eval(f, x - h)
    if any(math.isnan(v) for v in (a, b, c)):
        return math.nan
    return (a - 2 * b + c) / (h * h)


def is_pole(f, r):
    """|f| растёт при уменьшении шага → полюс, а не корень."""
    vals = []
    for h in (1e-2, 1e-3, 1e-4, 1e-5):
        l, rr = abs(safe_eval(f, r - h)), abs(safe_eval(f, r + h))
        if math.isnan(l) or math.isnan(rr):
            return True
        vals.append(min(l, rr))
    return all(vals[i + 1] > vals[i] * 3 for i in range(3)) and vals[-1] > 1e3


def check_root(f, r, tol):
    """→ (годен, причина, невязка)."""
    if r is None:
        return False, "корень не найден", math.inf
    fr = safe_eval(f, r)
    if math.isnan(fr):
        return False, "f(root) не определена — разрыв/полюс", math.inf
    if is_pole(f, r):
        return False, "полюс, а не корень", abs(fr)
    h = max(tol * 100, 1e-9)
    scale = max(1.0, abs(safe_eval(f, r + h)), abs(safe_eval(f, r - h)))
    if abs(fr) <= max(tol * 100, 1e-9) * scale:
        return True, "невязка |f| = %.2e" % abs(fr), abs(fr)
    return False, "невязка велика: |f| = %.2e" % abs(fr), abs(fr)


# ─────────────────────────── установка ───────────────────────────
def install(cls):
    cls.parse_equation = staticmethod(compile_expr)
    cls.df = staticmethod(df1)
    cls.d2f = staticmethod(df2)
    cls.nm_check_root = staticmethod(check_root)
    cls.nm_is_pole = staticmethod(is_pole)

    # ---- бисекция: добавляем проверку невязки ----
    def bisection(self, f, a, b, sigma, max_step=200000):
        H = []
        info = {"converged": False, "reason": "", "iterations": 0, "error": math.inf}
        fa, fb = safe_eval(f, a), safe_eval(f, b)
        if math.isnan(fa) or math.isnan(fb):
            info["reason"] = "f не определена на границах"
            return None, H, info
        if fa == 0:
            ok, why, _ = check_root(f, a, sigma)
            info.update(converged=ok, reason="точный корень в a · " + why, error=0.0)
            return (a if ok else None), H, info
        if fb == 0:
            ok, why, _ = check_root(f, b, sigma)
            info.update(converged=ok, reason="точный корень в b · " + why, error=0.0)
            return (b if ok else None), H, info
        if (fa < 0) == (fb < 0):
            info["reason"] = "f(a)·f(b) > 0 — знак не меняется"
            return None, H, info
        k = 0
        while k < max_step:
            c = (a + b) * .5
            fc = safe_eval(f, c)
            w = abs(b - a)
            H.append((k + 1, a, b, c, fc, w))
            k += 1
            if math.isnan(fc):
                info.update(reason="разрыв внутри отрезка", iterations=k, error=w)
                return None, H, info
            if fc == 0 or w <= sigma or w <= 4e-16 * max(1.0, abs(c)):
                ok, why, _ = check_root(f, c, sigma)
                info.update(converged=ok, reason=why, iterations=k, error=w * .5)
                return (c if ok else None), H, info
            if (fa < 0) != (fc < 0):
                b, fb = c, fc
            else:
                a, fa = c, fc
        info.update(reason="лимит %d — НЕ сошёлся" % max_step, iterations=k, error=abs(b - a))
        return None, H, info
    cls.bisection = bisection

    # ---- finish_solve: корень 0.0 + статистика + невязки ----
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

        pairs = [("bisection", rb, hb), ("chord", rc, hc), ("newton", rn, hn),
                 ("secant", rs, hs), ("brent", rbr, hbr), ("mpi", rmpi, hmpi)]

        self.nm_info = {}
        for name, root, hist in pairs:
            ok, why, res = check_root(f, root, sigma)
            self.nm_info[name] = {"root": root, "ok": ok, "why": why,
                                  "residual": res, "iters": len(hist)}

        # КОРЕНЬ 0.0 БОЛЬШЕ НЕ ТЕРЯЕТСЯ
        best = None
        for name in ("brent", "bisection", "newton", "secant", "chord", "mpi"):
            d = self.nm_info[name]
            if d["ok"] and d["root"] is not None:
                best = (name, d["root"])
                break
        self.history_log.append((eq, f"{a}", f"{b}",
                                 f"{best[1]:.5f}" if best else "—"))
        self.save_history()

        # СТАТИСТИКА: 1 уравнение = 1 запись (было ×6)
        if best:
            try:
                self.stats.record_solve(best[0], self.nm_info[best[0]]["iters"],
                                        elapsed_ms, sigma)
            except Exception:
                pass
        try:
            for ach in self.stats.check_achievements():
                self._notify_achievement(ach)
        except Exception:
            pass

        self.show_results(hb, hc, hn, hs, hbr, hmpi, rb, rc, rn, rs, rbr, rmpi,
                          a, b, sigma, elapsed_ms, all_roots)
        if best:
            self.status_var.set("Готово (%.0f мс) · %s → x = %.10f"
                                % (elapsed_ms, best[0], best[1]))
        else:
            self.status_var.set("Корень не подтверждён — нажмите «🩺 Диагностика»")
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            pass
        if hasattr(self, "mark_dirty"):
            self.mark_dirty()
    cls.finish_solve = finish_solve

    # ---- график сходимости: дополняем 5-колоночные истории до 6 ----
    _orig_conv = cls._draw_log_convergence
    def conv(self, parent, *hists):
        fixed = []
        for h in hists:
            fixed.append([r if len(r) >= 6 else tuple(r) + (abs(r[-1]),)
                          for r in (h or [])])
        return _orig_conv(self, parent, *fixed)
    cls._draw_log_convergence = conv

    # ---- настройки: правильное слияние ----
    def _save_settings(self):
        s = dict(getattr(self, "_settings", {}))
        s.update({"theme": self.theme, "geometry": self.root.geometry(),
                  "equation": self.eq_entry.get(), "a": self.a_entry.get(),
                  "b": self.b_entry.get(), "sigma": self.sigma_entry.get(),
                  "show_extrema": bool(self.show_extrema.get())})
        s.pop("github_token", None)
        self._settings = s
        try:
            import json
            with open(SETTINGS_FILE_GLOBAL, "w", encoding="utf-8") as fh:
                json.dump(s, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass
    cls._save_settings = _save_settings

    _orig_load = cls._load_settings
    def _load_settings(self):
        _orig_load(self)
        g = getattr(self, "_settings", {}).get("geometry")
        if g:
            try:
                self.root.geometry(g)
            except Exception:
                pass
        self.root.minsize(1100, 720)
    cls._load_settings = _load_settings

    # ---- диагностика ----
    def diagnostics(self):
        info = getattr(self, "nm_info", None)
        if not info:
            messagebox.showinfo("Диагностика", "Сначала нажмите «ВЫЧИСЛИТЬ».")
            return
        try:
            a = float(self.a_entry.get()); b = float(self.b_entry.get())
        except Exception:
            return
        f = self.last_f
        L = ["ДИАГНОСТИКА РЕЗУЛЬТАТА", "─" * 52]
        fa, fb = safe_eval(f, a), safe_eval(f, b)
        L += ["f(a) = %.8e" % fa, "f(b) = %.8e" % fb, ""]
        if math.isnan(fa) or math.isnan(fb):
            L.append("✕ f не определена на границах.")
        elif (fa < 0) == (fb < 0):
            L.append("✕ Знак не меняется → бисекция/хорды/Брент не работают.")
        else:
            L.append("✓ Смена знака есть → бисекция и Брент сойдутся.")
        n = 200
        d1 = [abs(df1(f, a + i * (b - a) / n)) for i in range(n + 1)]
        d1 = [v for v in d1 if math.isfinite(v)]
        if d1:
            m1, M1 = min(d1), max(d1)
            L += ["", "|f′(x)|:  min = %.3e   max = %.3e" % (m1, M1)]
            L.append("✓ f′ ≠ 0 → Ньютон безопасен." if m1 > 1e-10
                     else "⚠ f′ ≈ 0 → Ньютон может «выстрелить».")
            q = abs(1 - m1 / M1) if M1 > 0 else 1.0
            L += ["", "МПИ:  |φ′| ≈ %.4f" % q,
                  "✓ |φ′| < 1 → сойдётся." if q < 1 else "⚠ |φ′| ≥ 1 → может расходиться."]
            cond = M1 / m1 if m1 > 0 else math.inf
            L += ["", "Обусловленность ≈ %.2e" % cond,
                  "Хорошо обусловлена." if cond < 1e6 else "⚠ Возможна потеря точности."]
        L += ["", "ПРОВЕРКА КОРНЕЙ ПО НЕВЯЗКЕ", "─" * 52,
              "%-10s %-18s %10s  %s" % ("метод", "корень", "|f(root)|", "вердикт")]
        for name in ("bisection", "chord", "newton", "secant", "brent", "mpi"):
            d = info.get(name, {})
            r = d.get("root")
            rs_ = d.get("residual", math.inf)
            L.append("%-10s %-18s %10s  %s %s" % (
                name,
                "%.10f" % r if r is not None else "—",
                "%.2e" % rs_ if math.isfinite(rs_) else "—",
                "✓" if d.get("ok") else "✕",
                d.get("why", "")))
        L += ["", "Полюс ≠ корень: если |f| растёт при приближении,",
              "это разрыв (например 1/x в нуле), а не решение f(x)=0."]
        win = tk.Toplevel(self.root)
        win.title("🩺 Диагностика"); win.geometry("780x620")
        t = tk.Text(win, font=("Consolas", 10), wrap=tk.WORD, padx=14, pady=14)
        sb = tk.Scrollbar(win, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y); t.pack(fill=tk.BOTH, expand=True)
        t.insert("1.0", "\n".join(L)); t.config(state=tk.DISABLED)
    cls.diagnostics = diagnostics

    # ---- кнопка диагностики отдельной строкой ----
    _orig_init = cls.__init__
    def __init__(self, root):
        _orig_init(self, root)
        try:
            row = tk.Frame(self.pad, relief=tk.GROOVE, bd=1)
            row.pack(fill=tk.X, pady=(8, 0))
            inner = tk.Frame(row, padx=10, pady=6); inner.pack(fill=tk.X)
            tk.Button(inner, text="🩺 Диагностика", command=self.diagnostics,
                      bg="#e0e7ff", fg="#3730a3", font=("Segoe UI", 9, "bold"),
                      relief=tk.RAISED, bd=1, cursor="hand2",
                      padx=12, pady=4).pack(side=tk.LEFT, padx=4)
            tk.Label(inner, text="проверка корня по невязке · полюса · сходимость",
                     fg="#6b7280", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=8)
        except Exception:
            pass
    cls.__init__ = __init__
    return cls