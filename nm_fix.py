# nm_fix.py — точечный патч. Подключается двумя строками, старый код не меняется.
import math, re, ast, time, threading, random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

METHODS = ["bisection", "chord", "newton", "secant", "brent", "mpi"]
MNAME = {"bisection": "Бисекция", "chord": "Хорды", "newton": "Ньютон",
         "secant": "Секущие", "brent": "Брент", "mpi": "МПИ"}


def _info(ok=False, reason="", it=0, err=float("inf")):
    return {"converged": ok, "reason": reason, "iterations": it, "error": err}


def _norm(res):
    """Приводит любой результат (2-tuple или 3-tuple) к (root, hist, info)."""
    if res is None:
        return None, [], _info(reason="метод упал с исключением")
    if len(res) == 3 and isinstance(res[2], dict):
        return res
    root, hist = res[0], res[1]
    ok = root is not None and bool(hist)
    return root, hist, _info(ok, "сошёлся" if ok else "корень не найден",
                             len(hist), abs(hist[-1][-1]) if hist else float("inf"))


# ══════════════════════════ математика (все возвращают 3-tuple) ══════════════
def _safe_eval(self, f, x):
    try:
        y = f(x)
        if isinstance(y, complex):
            return math.nan
        y = float(y)
        return y if math.isfinite(y) else math.nan
    except Exception:
        return math.nan


def _bisection_v2(self, f, a, b, tol, limit=200000):
    H = []
    fa, fb = self.safe_eval(f, a), self.safe_eval(f, b)
    if math.isnan(fa) or math.isnan(fb):
        return None, H, _info(reason="f не определена на границах")
    if fa == 0: return a, H, _info(True, "точный корень в a", 0, 0.0)
    if fb == 0: return b, H, _info(True, "точный корень в b", 0, 0.0)
    if fa * fb > 0:
        return None, H, _info(reason="f(a)·f(b) > 0 — знак не меняется")
    k = 0
    while k < limit:
        c = (a + b) * .5
        fc = self.safe_eval(f, c)
        w = abs(b - a)
        H.append((k + 1, a, b, c, fc, w)); k += 1
        if math.isnan(fc):
            return None, H, _info(reason="разрыв внутри отрезка", it=k, err=w)
        if fc == 0 or w <= tol:
            return c, H, _info(True, "достигнута точность σ", k, w)
        if fa * fc < 0: b, fb = c, fc
        else: a, fa = c, fc
        if w <= 4e-16 * max(1.0, abs(c)):
            return c, H, _info(True, "машинная точность", k, w)
    return (a + b) * .5, H, _info(reason="лимит итераций %d — НЕ сошёлся" % limit,
                                 it=k, err=abs(b - a))


def _chord_v2(self, f, a, b, tol, limit=5000):
    H = []
    fa, fb = self.safe_eval(f, a), self.safe_eval(f, b)
    if math.isnan(fa) or math.isnan(fb) or fa * fb > 0:
        return None, H, _info(reason="нет смены знака на [a,b]")
    x0 = a if fa * self.d2f(f, a) > 0 else b
    fx0 = self.safe_eval(f, x0)
    xm = b if x0 == a else a
    for k in range(1, limit + 1):
        fxm = self.safe_eval(f, xm)
        den = fxm - fx0
        if abs(den) < 1e-300:
            return xm, H, _info(reason="вырожденная хорда", it=k, err=0.0)
        xn = xm - fxm * (xm - x0) / den
        d = abs(xn - xm)
        H.append((k, x0, xm, xn, self.safe_eval(f, xn), d))
        if not math.isfinite(xn):
            return None, H, _info(reason="расходимость", it=k, err=d)
        if d < tol:
            return xn, H, _info(True, "достигнута точность σ", k, d)
        xm = xn
    return xm, H, _info(reason="лимит итераций %d" % limit, it=limit, err=tol * 1e3)


def _newton_v2(self, f, a, b, tol, limit=2000):
    H = []
    x = a if self.safe_eval(f, a) * self.d2f(f, a) > 0 else b
    if math.isnan(self.safe_eval(f, x)): x = (a + b) * .5
    for k in range(1, limit + 1):
        fx = self.safe_eval(f, x)
        d1 = self.df(f, x)
        if math.isnan(fx) or math.isnan(d1) or abs(d1) < 1e-14:
            return None, H, _info(reason="f′(x) ≈ 0 — касательная горизонтальна", it=k)
        xn = x - fx / d1
        d = abs(xn - x)
        H.append((k, x, fx, d1, xn, d))
        if not math.isfinite(xn) or abs(xn) > 1e12:
            return None, H, _info(reason="метод «выстрелил» за пределы", it=k, err=d)
        if d < tol:
            return xn, H, _info(True, "квадратичная сходимость", k, d)
        x = xn
    return x, H, _info(reason="лимит итераций %d" % limit, it=limit, err=tol * 1e3)


def _secant_v2(self, f, a, b, tol, limit=2000):
    H = []
    x0, x1 = a, b
    f0, f1 = self.safe_eval(f, x0), self.safe_eval(f, x1)
    for k in range(1, limit + 1):
        if abs(f1 - f0) < 1e-300:
            return x1, H, _info(reason="вырожденная секущая", it=k, err=0.0)
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        d = abs(x2 - x1)
        H.append((k, x0, x1, f1, x2, d))
        if not math.isfinite(x2) or abs(x2) > 1e12:
            return None, H, _info(reason="расходимость", it=k, err=d)
        if d < tol:
            return x2, H, _info(True, "сверхлинейная сходимость", k, d)
        x0, f0 = x1, f1
        x1, f1 = x2, self.safe_eval(f, x2)
    return x1, H, _info(reason="лимит итераций %d" % limit, it=limit, err=tol * 1e3)


def _mpi_v2(self, f, a, b, tol, limit=20000):
    H = []
    n = 64
    ds = [abs(self.df(f, a + i * (b - a) / n)) for i in range(n + 1)]
    ds = [v for v in ds if math.isfinite(v) and v > 0]
    M = max(ds) if ds else 1.0
    q = abs(1 - min(ds) / M) if ds else 1.0
    x = (a + b) * .5
    for k in range(1, limit + 1):
        fx = self.safe_eval(f, x)
        phi = x - fx / M
        d = abs(phi - x)
        H.append((k, x, phi, fx, q, d))
        if not math.isfinite(phi) or abs(phi) > 1e12:
            return None, H, _info(reason="расходимость (|φ′| ≥ 1)", it=k, err=d)
        if d < tol:
            return phi, H, _info(True, "сошлось, |φ′|≈%.3f" % q, k, d)
        x = phi
    return x, H, _info(reason="лимит итераций %d" % limit, it=limit, err=tol * 1e3)


# ══════════════════════════ новый solve ══════════════════════════════════════
def _solve_v2(self):
    if getattr(self, "is_calculating", False):
        return
    self.stop_animation()
    self.is_calculating = True
    self.btn_solve.config(state=tk.DISABLED, text="⏳ ...")
    self.status_var.set("Вычисление…")
    self.progress_var.set(0)
    t0 = time.perf_counter()
    eq = self.eq_entry.get()
    try:
        fp, vars_ = self.parse_equation(eq)
        mv = getattr(self, "multi_vars", {})
        if getattr(self, "var_mode", None) and self.var_mode.get() == "multi":
            for v in vars_:
                if v != "x" and v not in mv:
                    mv[v] = 0.0
            def f(x):
                d = {"x": x}; d.update(mv); return fp(d)
        else:
            f = lambda x: fp({"x": x})
        f(0.0)
        a = float(self.a_entry.get().replace(",", "."))
        b = float(self.b_entry.get().replace(",", "."))
        tol = max(float(self.sigma_entry.get().replace(",", ".")), 1e-15)
    except Exception as e:
        self._handle_calc_error(str(e)); return
    if a >= b:
        self._handle_calc_error("Требуется a < b"); return

    engine = {"bisection": self.bisection_v2, "chord": self.chord_v2,
              "newton": self.newton_v2, "secant": self.secant_v2}
    try:
        from methods_extra import brent_method, simple_iteration, find_all_roots
    except Exception:
        brent_method = simple_iteration = find_all_roots = None
    if brent_method: engine["brent"] = brent_method
    if simple_iteration: engine["mpi"] = simple_iteration

    def worker():
        try:
            res = {}
            for i, key in enumerate(METHODS):
                fn = engine.get(key)
                if fn is None:
                    res[key] = (None, [], _info(reason="метод недоступен"))
                else:
                    try:
                        res[key] = _norm(fn(f, a, b, tol))
                    except Exception as ex:
                        res[key] = (None, [], _info(reason="исключение: %s" % ex))
                self.root.after(0, lambda v=10 + i * 13: self.progress_var.set(v))
            try:
                roots = find_all_roots(f, a, b, tol, n_segments=400, method="brent") if find_all_roots else []
            except Exception:
                roots = []
            ms = (time.perf_counter() - t0) * 1000
            self.nm_infos = {k: v[2] for k, v in res.items()}
            g = lambda k, i: res[k][i]
            self.root.after(0, lambda: self.finish_solve(
                f, a, b, tol,
                g("bisection", 0), g("bisection", 1),
                g("chord", 0), g("chord", 1),
                g("newton", 0), g("newton", 1),
                g("secant", 0), g("secant", 1),
                g("brent", 0), g("brent", 1),
                g("mpi", 0), g("mpi", 1),
                roots, eq, ms))
        except Exception as ex:
            msg = str(ex)
            self.root.after(0, lambda m=msg: self._handle_calc_error(m))
    threading.Thread(target=worker, daemon=True).start()


# ══════════════════════════ новые функции ════════════════════════════════════
def _auto_interval(self):
    try:
        fp, vs = self.parse_equation(self.eq_entry.get())
        mv = getattr(self, "multi_vars", {})
        def f(x):
            d = {"x": x}; d.update(mv); return fp(d)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e)); return
    found, R, N = [], 60.0, 3000
    px, py = -R, self.safe_eval(f, -R)
    for i in range(1, N + 1):
        x = -R + 2 * R * i / N
        y = self.safe_eval(f, x)
        if not (math.isnan(py) or math.isnan(y)):
            if py == 0: found.append((px, px))
            elif py * y < 0: found.append((px, x))
        px, py = x, y
    if not found:
        messagebox.showinfo("Результат",
            "На [−60, 60] смен знака нет.\n"
            "Возможно: корней нет, они комплексные или кратные (касание оси).")
        return
    win = tk.Toplevel(self.root); win.title("🔍 Найденные интервалы")
    win.geometry("560x420"); win.transient(self.root)
    tk.Label(win, text="Интервалов со сменой знака: %d" % len(found),
             font=("Segoe UI", 11, "bold")).pack(pady=10)
    tv = ttk.Treeview(win, columns=("a", "b", "fa", "fb"), show="headings")
    for c, t in [("a", "a"), ("b", "b"), ("fa", "f(a)"), ("fb", "f(b)")]:
        tv.heading(c, text=t); tv.column(c, width=125, anchor=tk.E)
    tv.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
    for a_, b_ in found:
        tv.insert("", tk.END, values=("%.6g" % a_, "%.6g" % b_,
                                      "%.3e" % self.safe_eval(f, a_),
                                      "%.3e" % self.safe_eval(f, b_)))
    def use(_=None):
        s = tv.selection()
        if not s: return
        v = tv.item(s[0], "values")
        self.a_entry.delete(0, tk.END); self.a_entry.insert(0, v[0])
        self.b_entry.delete(0, tk.END); self.b_entry.insert(0, v[1])
        win.destroy(); self.solve()
    tk.Button(win, text="✓ Использовать интервал", command=use,
              bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"),
              padx=16, pady=6).pack(pady=10)
    tv.bind("<Double-1>", use)


def _diagnostics(self):
    infos = getattr(self, "nm_infos", None)
    if not infos:
        messagebox.showinfo("Диагностика", "Сначала нажмите «ВЫЧИСЛИТЬ»."); return
    try:
        a = float(self.a_entry.get()); b = float(self.b_entry.get())
    except Exception:
        return
    f = self.last_f
    L = ["ДИАГНОСТИКА СХОДИМОСТИ", "─" * 48]
    fa, fb = self.safe_eval(f, a), self.safe_eval(f, b)
    L += ["f(a) = %.8e" % fa, "f(b) = %.8e" % fb, ""]
    if math.isnan(fa) or math.isnan(fb):
        L.append("✕ f не определена на границах — все методы отвалятся.")
    elif fa * fb > 0:
        L += ["✕ f(a)·f(b) > 0 → бисекция, хорды, Брент не запустятся.",
              "  Совет: кнопка «🔍 Интервал»."]
    else:
        L.append("✓ Смена знака есть → бисекция и Брент сойдутся гарантированно.")
    n = 200
    d1 = [abs(self.df(f, a + i * (b - a) / n)) for i in range(n + 1)]
    d1 = [v for v in d1 if math.isfinite(v)]
    if d1:
        m1, M1 = min(d1), max(d1)
        L += ["", "|f′(x)|:  min = %.3e   max = %.3e" % (m1, M1)]
        L.append("✓ f′ ≠ 0 → Ньютон безопасен." if m1 > 1e-10
                 else "⚠ f′ ≈ 0 внутри → Ньютон может «выстрелить».")
        q = abs(1 - m1 / M1) if M1 > 0 else 1.0
        L += ["", "МПИ:  |φ′| ≈ %.4f" % q,
              "✓ |φ′| < 1 → сойдётся." if q < 1 else "⚠ |φ′| ≥ 1 → может расходиться."]
        cond = M1 / m1 if m1 > 0 else float("inf")
        L += ["", "Обусловленность ≈ %.2e" % cond,
              "Задача хорошо обусловлена." if cond < 1e6 else "⚠ Возможна потеря точности."]
    L += ["", "РЕЗУЛЬТАТЫ МЕТОДОВ", "─" * 48]
    for k in METHODS:
        i = infos.get(k, {})
        L.append("%s %-10s итераций %6d   ε=%.2e   %s" %
                 ("✓" if i.get("converged") else "✕", MNAME[k],
                  i.get("iterations", 0), i.get("error", float("inf")),
                  i.get("reason", "")))
    win = tk.Toplevel(self.root); win.title("🩺 Диагностика"); win.geometry("760x600")
    win.transient(self.root)
    t = tk.Text(win, font=("Consolas", 10), wrap=tk.WORD, padx=14, pady=14)
    sb = ttk.Scrollbar(win, orient="vertical", command=t.yview)
    t.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y); t.pack(fill=tk.BOTH, expand=True)
    t.insert("1.0", "\n".join(L)); t.config(state=tk.DISABLED)


# ══════════════════════════ Excel с живыми формулами ═════════════════════════
_XLF = {"sin": "SIN", "cos": "COS", "tan": "TAN", "asin": "ASIN", "acos": "ACOS",
        "atan": "ATAN", "sinh": "SINH", "cosh": "COSH", "tanh": "TANH",
        "sqrt": "SQRT", "exp": "EXP", "fabs": "ABS", "abs": "ABS",
        "floor": "INT", "ceil": "CEILING", "degrees": "DEGREES",
        "radians": "RADIANS", "log": "LN", "log10": "LOG10", "pow": "POWER"}
_XLC = {"pi": "PI()", "e": "EXP(1)", "tau": "(2*PI())"}


def _to_excel(src, cell="$B$5", sep=";"):
    s = re.sub(r"\bmath\.", "", (src or "").strip().replace("^", "**"))
    s = re.sub(r"(\d)([a-zA-Z\(])", r"\1*\2", s)
    s = re.sub(r"(\))([a-zA-Z0-9\(])", r"\1*\2", s)
    if "=" in s:
        l, r = s.split("=", 1); s = "(%s)-(%s)" % (l, r)
    def nd(n):
        if isinstance(n, ast.Constant): return repr(n.value)
        if isinstance(n, ast.Name):
            if n.id == "x": return cell
            if n.id in _XLC: return _XLC[n.id]
            raise ValueError("символ «%s»" % n.id)
        if isinstance(n, ast.UnaryOp):
            v = nd(n.operand)
            return "(-%s)" % v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.BinOp):
            L, R = nd(n.left), nd(n.right)
            for t, f in ((ast.Add, "(%s+%s)"), (ast.Sub, "(%s-%s)"),
                         (ast.Mult, "(%s*%s)"), (ast.Div, "(%s/%s)"), (ast.Pow, "(%s^%s)")):
                if isinstance(n.op, t): return f % (L, R)
            if isinstance(n.op, ast.Mod): return "MOD(%s%s%s)" % (L, sep, R)
            raise ValueError("операция")
        if isinstance(n, ast.Call):
            nm = n.func.id if isinstance(n.func, ast.Name) else None
            ar = [nd(a) for a in n.args]
            if nm == "log2": return "LOG(%s%s2)" % (ar[0], sep)
            if nm == "log" and len(ar) == 2: return "LOG(%s%s%s)" % (ar[0], sep, ar[1])
            if nm not in _XLF: raise ValueError("функция %s" % nm)
            return "%s(%s)" % (_XLF[nm], sep.join(ar))
        raise ValueError("конструкция")
    return nd(ast.parse(s, mode="eval").body)


def _export_excel_live(self):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Border, Side
        from openpyxl.chart import LineChart, Reference
        from openpyxl.utils import get_column_letter
    except ImportError:
        messagebox.showerror("Ошибка", "Нужен openpyxl:\npip install openpyxl"); return
    if not getattr(self, "last_f", None):
        messagebox.showwarning("Ошибка", "Сначала выполните расчёт"); return
    fp = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                      filetypes=[("Excel", "*.xlsx")])
    if not fp: return
    eq = self.eq_entry.get()
    a = float(self.a_entry.get()); b = float(self.b_entry.get())
    tol = float(self.sigma_entry.get())
    SEP = ";"
    try:
        fx = _to_excel(eq, "$B$5", SEP); live = True
    except Exception as ex:
        fx = None; live = False
        messagebox.showwarning("Формула не переведена",
            "%s\n\nБудет создан файл со статическими числами." % ex)
    HF = PatternFill("solid", fgColor="1E3A5F")
    HFONT = Font(color="FFFFFF", bold=True)
    IN = PatternFill("solid", fgColor="FEF3C7")
    CAL = PatternFill("solid", fgColor="DCFCE7")
    MONO = Font(name="Consolas", size=10)
    TTL = Font(bold=True, size=15, color="2563EB")
    thin = Side(style="thin", color="D1D5DB")
    BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
    wb = openpyxl.Workbook(); wb.remove(wb.active)

    ws = wb.create_sheet("Пульт")
    ws["A1"] = "ПУЛЬТ УПРАВЛЕНИЯ"; ws["A1"].font = TTL
    ws["A2"] = "f(x)"; ws["B2"] = eq; ws["B2"].font = MONO
    ws["A3"] = "формула Excel"; ws["B3"] = fx or "—"; ws["B3"].font = MONO
    ws["A5"] = "x ="; ws["A5"].font = Font(bold=True, size=12)
    ws["B5"] = a; ws["B5"].fill = IN; ws["B5"].border = BOX
    ws["C5"] = "← МЕНЯЙТЕ ЭТУ ЯЧЕЙКУ"; ws["C5"].font = Font(italic=True, color="6B7280")
    if live:
        ws["A6"] = "f(x) ="; ws["B6"] = "=" + fx
        ws["B6"].fill = CAL; ws["B6"].number_format = "0.0000000000"
        ws["B6"].border = BOX; ws["B6"].font = Font(bold=True, color="059669")
        p_ = fx.replace("$B$5", "($B$5+0.00001)")
        m_ = fx.replace("$B$5", "($B$5-0.00001)")
        ws["A7"] = "f′(x) ≈"; ws["B7"] = "=((%s)-(%s))/0.00002" % (p_, m_)
        ws["B7"].fill = CAL; ws["B7"].number_format = "0.000000E+00"
    for i, (lbl, v) in enumerate([("a =", a), ("b =", b), ("σ =", tol)], start=10):
        ws.cell(i, 1, lbl).font = Font(bold=True)
        c = ws.cell(i, 2, v); c.fill = IN; c.border = BOX
    ws["B12"].number_format = "0.0E+00"
    if live:
        ws["A13"] = "f(a)"; ws["B13"] = "=" + fx.replace("$B$5", "$B$10")
        ws["A14"] = "f(b)"; ws["B14"] = "=" + fx.replace("$B$5", "$B$11")
        ws["A15"] = "f(a)·f(b)"; ws["B15"] = "=$B$13*$B$14"
        ws["A16"] = "корень гарантирован?"
        ws["B16"] = '=IF($B$15<0%s"ДА"%s"НЕТ — смените a/b")' % (SEP, SEP)
        ws["B16"].font = Font(bold=True)
    ws["A18"] = "КАК ПОЛЬЗОВАТЬСЯ"; ws["A18"].font = TTL
    for i, t in enumerate([
        "1. Меняйте жёлтую B5 — зелёная B6 мгновенно пересчитает f(x).",
        "2. Меняйте a, b, σ в B10:B12 — таблицы пересчитаются.",
        "3. На листах методов каждая ячейка — ФОРМУЛА, не число.",
        "4. Кликните ячейку → в строке формул видно, как подставляется x.",
        "5. Excel ругается на формулу? Замените ';' на ',' (EN-локаль)."], start=19):
        ws.cell(i, 1, t)
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 46
    ws.column_dimensions["C"].width = 28
    ws.freeze_panes = "A5"

    if live:
        wv = wb.create_sheet("Таблица f(x)")
        for j, t in enumerate(["№", "x", "f(x)", "знак", "смена знака"], 1):
            c = wv.cell(1, j, t); c.fill = HF; c.font = HFONT; c.border = BOX
        N = 200
        for i in range(N + 1):
            r = i + 2
            wv.cell(r, 1, i + 1)
            wv.cell(r, 2, "=Пульт!$B$10+%d*(Пульт!$B$11-Пульт!$B$10)/%d" % (i, N))
            wv.cell(r, 3, "=" + fx.replace("$B$5", "B%d" % r).replace("$B$", "Пульт!$B$"))
            wv.cell(r, 4, '=IF(C%d>0%s"+"%sIF(C%d<0%s"-"%s"0"))' % (r, SEP, SEP, r, SEP, SEP))
            wv.cell(r, 5, "—" if i == 0 else
                    '=IF(AND(D%d<>D%d%sD%d<>"0"%sD%d<>"0")%s"КОРЕНЬ"%s"")'
                    % (r, r - 1, SEP, r, SEP, r - 1, SEP, SEP, SEP))
            wv.cell(r, 2).number_format = "0.000000"
            wv.cell(r, 3).number_format = "0.0000000000"
            for j in range(1, 6):
                wv.cell(r, j).font = MONO; wv.cell(r, j).border = BOX
        for col, w in zip("ABCDE", [6, 18, 24, 10, 16]):
            wv.column_dimensions[col].width = w
        wv.freeze_panes = "A2"
        ch = LineChart(); ch.title = "f(x) на [a, b]"; ch.height, ch.width = 10, 22
        ch.add_data(Reference(wv, min_col=3, min_row=1, max_row=N + 1), titles_from_data=True)
        ch.set_categories(Reference(wv, min_col=2, min_row=2, max_row=N + 1))
        wv.add_chart(ch, "G2")

        wb_ = wb.create_sheet("Бисекция (живая)")
        for j, t in enumerate(["N", "a", "b", "c=(a+b)/2", "f(c)", "|b−a|"], 1):
            c = wb_.cell(1, j, t); c.fill = HF; c.font = HFONT; c.border = BOX
        for k in range(1, 61):
            r = k + 1
            wb_.cell(r, 1, k)
            if k == 1:
                wb_.cell(r, 2, "=Пульт!$B$10"); wb_.cell(r, 3, "=Пульт!$B$11")
            else:
                p = r - 1
                cond = "E%d*%s<0" % (p, fx.replace("$B$5", "B%d" % p).replace("$B$", "Пульт!$B$"))
                wb_.cell(r, 2, "=IF(%s%sB%d%sD%d)" % (cond, SEP, p, SEP, p))
                wb_.cell(r, 3, "=IF(%s%sD%d%sC%d)" % (cond, SEP, p, SEP, p))
            wb_.cell(r, 4, "=(B%d+C%d)/2" % (r, r))
            wb_.cell(r, 5, "=" + fx.replace("$B$5", "D%d" % r).replace("$B$", "Пульт!$B$"))
            wb_.cell(r, 6, "=ABS(C%d-B%d)" % (r, r))
            for j in range(2, 7):
                cc = wb_.cell(r, j)
                cc.number_format = "0.0000000000"; cc.fill = CAL
                cc.font = MONO; cc.border = BOX
        for col, w in zip("ABCDEF", [6, 20, 20, 20, 22, 20]):
            wb_.column_dimensions[col].width = w
        wb_.freeze_panes = "B2"

        wn = wb.create_sheet("Ньютон (живой)")
        for j, t in enumerate(["N", "x_n", "f(x_n)", "f′(x_n)", "x_n+1", "|Δx|"], 1):
            c = wn.cell(1, j, t); c.fill = HF; c.font = HFONT; c.border = BOX
        for k in range(1, 41):
            r = k + 1
            wn.cell(r, 1, k)
            wn.cell(r, 2, "=Пульт!$B$10" if k == 1 else "=E%d" % (r - 1))
            cell = "B%d" % r
            wn.cell(r, 3, "=" + fx.replace("$B$5", cell).replace("$B$", "Пульт!$B$"))
            p_ = fx.replace("$B$5", "(%s+0.00001)" % cell).replace("$B$", "Пульт!$B$")
            m_ = fx.replace("$B$5", "(%s-0.00001)" % cell).replace("$B$", "Пульт!$B$")
            wn.cell(r, 4, "=((%s)-(%s))/0.00002" % (p_, m_))
            wn.cell(r, 5, "=IF(ABS(D%d)<1E-15%sB%d%sB%d-C%d/D%d)" % (r, SEP, r, SEP, r, r, r))
            wn.cell(r, 6, "=ABS(E%d-B%d)" % (r, r))
            for j in range(2, 7):
                cc = wn.cell(r, j)
                cc.number_format = "0.0000000000"; cc.fill = CAL
                cc.font = MONO; cc.border = BOX
        for col, w in zip("ABCDEF", [6, 20, 22, 22, 24, 20]):
            wn.column_dimensions[col].width = w
        wn.freeze_panes = "B2"
    wb.active = 0
    wb.save(fp)
    try: self.stats.record_export("xlsx")
    except Exception: pass
    messagebox.showinfo("Готово",
        "Excel сохранён%s:\n%s" % (" — с живыми формулами" if live else "", fp))


# ══════════════════════════ фикс оформления ══════════════════════════════════
def _fix_ui(self):
    # 1. Координаты не «толкают» кнопки
    try:
        self.coord_label.config(width=38, anchor="e",
                                text="x: —   y: —   f(x): —")
        header = self.coord_label.master
        header.pack_propagate(False)
        header.configure(height=38)
    except Exception:
        pass
    # 2. Дополнительные кнопки — отдельной строкой, ничего не сдвигают
    try:
        row = tk.Frame(self.pad, relief=tk.GROOVE, bd=1)
        row.pack(fill=tk.X, pady=(8, 0))
        inner = tk.Frame(row, padx=10, pady=6); inner.pack(fill=tk.X)
        for txt, cmd, bg, fg in [
            ("🔍 Интервал", self.auto_interval, "#dbeafe", "#1e40af"),
            ("🩺 Диагностика", self.diagnostics, "#e0e7ff", "#3730a3"),
            ("📗⚡ Excel LIVE", self.export_excel_live, "#dcfce7", "#166534")]:
            tk.Button(inner, text=txt, command=cmd, bg=bg, fg=fg,
                      font=("Segoe UI", 9, "bold"), relief=tk.RAISED, bd=1,
                      cursor="hand2", padx=12, pady=4).pack(side=tk.LEFT, padx=4)
        tk.Label(inner, text="← новые функции (nm_fix)", fg="#6b7280",
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=8)
        self.nm_row = row
    except Exception:
        pass


# ══════════════════════════ подключение ══════════════════════════════════════
def apply(cls):
    """Навешивает патч на класс. Старые методы НЕ удаляются."""
    cls.safe_eval      = _safe_eval
    cls.bisection_v2   = _bisection_v2
    cls.chord_v2       = _chord_v2
    cls.newton_v2      = _newton_v2
    cls.secant_v2      = _secant_v2
    cls.mpi_v2         = _mpi_v2
    cls.solve          = _solve_v2          # единственный перекрываемый метод
    cls.auto_interval  = _auto_interval
    cls.diagnostics    = _diagnostics
    cls.export_excel_live = _export_excel_live

    _orig_init = cls.__init__
    def __init__(self, root):
        _orig_init(self, root)
        _fix_ui(self)
    cls.__init__ = __init__
    return cls