# diagnose.py — показывает ВСЕ проблемы с точными номерами строк
import re, ast, sys, io
from pathlib import Path

SRC = Path("numerical_methods.py")
REPORT = Path("diagnose_report.txt")

if not SRC.exists():
    print(f"❌ Не найден {SRC.resolve()}")
    sys.exit(1)

lines = SRC.read_text(encoding="utf-8").splitlines()
out = io.StringIO()

def w(s=""):
    print(s)
    out.write(s + "\n")

w("=" * 78)
w(f"ДИАГНОСТИКА: {SRC.resolve()}")
w(f"Всего строк: {len(lines)}")
w("=" * 78)

critical = []   # (строка, категория, было, надо)
warn = []

# ---------- 1. Синтаксис (даёт точную строку) ----------
w("\n### 1. СИНТАКСИС")
try:
    ast.parse("\n".join(lines))
    w("✅ Синтаксических ошибок нет")
except SyntaxError as e:
    w(f"❌ Строка {e.lineno}, символ {e.offset}: {e.msg}")
    if e.text:
        w(f"   ТЕКСТ: {e.text.rstrip()}")
    for i in range(max(0, (e.lineno or 1) - 4), min(len(lines), (e.lineno or 1) + 3)):
        mark = ">>>" if i + 1 == e.lineno else "   "
        w(f" {mark} {i+1:5d} | {lines[i]}")
    critical.append((e.lineno, "SyntaxError", e.text or "", e.msg))

# ---------- 2. Магические методы / точка входа ----------
w("\n### 2. МАГИЧЕСКИЕ ИМЕНА И ТОЧКА ВХОДА")
rules = [
    (r'def\s+init\s*\(',                 'def __init__(',        "нет __ у __init__"),
    (r'def\s+<strong>init</strong>\s*\(','def __init__(',        "HTML-тег вместо __init__"),
    (r'abspath\(\s*file\s*\)',           'abspath(__file__)',    "file вместо __file__"),
    (r'abspath\(<strong>file</strong>\)','abspath(__file__)',    "HTML-тег вместо __file__"),
    (r'^\s*if\s+name\s*==',              'if __name__ ==',       "нет __ у __name__"),
    (r'" ?main ?"',                      '"__main__"',           "нет __ у __main__"),
    (r'<strong>|</strong>|<em>|</em>',   '(удалить тег)',        "HTML-тег в коде"),
]
for n, line in enumerate(lines, 1):
    for pat, fix, why in rules:
        if re.search(pat, line):
            critical.append((n, why, line.strip(), fix))
            w(f"❌ {n:5d} | {why}")
            w(f"        БЫЛО : {line.strip()[:100]}")
            w(f"        НАДО : {fix}")

# ---------- 3. Пробелы внутри идентификаторов ----------
w("\n### 3. РАЗОРВАННЫЕ ИДЕНТИФИКАТОРЫ")
ident_rules = [
    (r'\bself\.\s+\w',        "self. имя"),
    (r'\w\s+\.\w',            "имя . имя"),
    (r'\bv\s+alue\s*=',       "v alue= → value="),
    (r'\blamb\s+da\b',        "lamb da → lambda"),
    (r'\bprogress\s+_var\b',  "progress _var → progress_var"),
    (r'\bLaT\s+eX\b',         "LaT eX → LaTeX"),
    (r'\bcente?\s+e\s+r\b',   "cent e r → center"),
    (r'\bpady\s+=',           "pady = → pady="),
    (r'\bf\s+"',              'f " → f"'),
    (r"\bf\s+'",              "f ' → f'"),
    (r'GROOVE\s+,',           "GROOVE , → GROOVE,"),
]
for n, line in enumerate(lines, 1):
    for pat, why in ident_rules:
        if re.search(pat, line):
            critical.append((n, why, line.strip(), "убрать пробел"))
            w(f"❌ {n:5d} | {why}")
            w(f"        {line.strip()[:110]}")

# ---------- 4. Пробелы в строковых литералах ----------
w("\n### 4. ПРОБЕЛЫ В СТРОКАХ (ключи тем, цвета, биндинги)")
for n, line in enumerate(lines, 1):
    hits = []
    if re.search(r'"(light|dark|ocean|forest|bg|panel|header|text|muted|canvas_bg|grid|axis)\s+"', line):
        hits.append("ключ темы с пробелом")
    if re.search(r'"#[0-9a-fA-F]{6}\s+"', line):
        hits.append("HEX-цвет с пробелом")
    if re.search(r'"\s*<<?\s*\w[\w-]*\s*>?\s*"', line) and "bind" in line:
        hits.append("биндинг с пробелами")
    if re.search(r'"\s+(single|multi|ru|en|readonly|white|bold)\s*"', line):
        hits.append("значение с пробелом")
    if hits:
        critical.append((n, "; ".join(hits), line.strip(), "убрать пробелы внутри кавычек"))
        w(f"❌ {n:5d} | {'; '.join(hits)}")
        w(f"        {line.strip()[:110]}")

# ---------- 5. Методы вне класса ----------
w("\n### 5. МЕТОДЫ С self, НО БЕЗ ОТСТУПА (вне класса)")
for n, line in enumerate(lines, 1):
    if re.match(r'^def\s+\w+\s*\(\s*self', line):
        critical.append((n, "метод вне класса", line.strip(), "отступ 4 пробела"))
        w(f"❌ {n:5d} | {line.strip()[:100]}")

# ---------- 6. Дубликаты методов ----------
w("\n### 6. ДУБЛИКАТЫ def (одинаковый отступ + имя)")
seen = {}
for n, line in enumerate(lines, 1):
    m = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
    if not m:
        continue
    key = (len(m.group(1)), m.group(2))
    if key in seen:
        critical.append((n, f"дубликат {m.group(2)}", line.strip(),
                         f"удалить (первый на строке {seen[key]})"))
        w(f"❌ {n:5d} | дубликат '{m.group(2)}' (первый: строка {seen[key]})")
    else:
        seen[key] = n

# ---------- 7. Мусор после mainloop ----------
w("\n### 7. КОД ПОСЛЕ root.mainloop()")
ml = [n for n, l in enumerate(lines, 1)
      if l.strip() == "root.mainloop()" and not l.startswith((" ", "\t"))]
if ml:
    last = ml[-1]
    tail = [(n, lines[n-1]) for n in range(last+1, len(lines)+1)
            if lines[n-1].strip() and not lines[n-1].strip().startswith("#")]
    if tail:
        w(f"❌ После строки {last} (root.mainloop) есть {len(tail)} непустых строк:")
        for n, t in tail[:15]:
            w(f"   {n:5d} | {t.strip()[:100]}")
        if len(tail) > 15:
            w(f"   ... и ещё {len(tail)-15}")
        critical.append((last, "мусор после mainloop", f"{len(tail)} строк", "удалить хвост"))
    else:
        w(f"✅ mainloop на строке {last}, хвоста нет")
else:
    w("⚠️ root.mainloop() на уровне модуля не найден")

# ---------- 8. safe_eval / safe_f ----------
w("\n### 8. safe_eval / safe_f")
for n, line in enumerate(lines, 1):
    if re.match(r'^def\s+safe_(eval|f)\s*\(', line):
        critical.append((n, "safe_* вне класса", line.strip(), "перенести в класс (отступ 4)"))
        w(f"❌ {n:5d} | {line.strip()} — вне класса, а вызывается как self.*")
calls = [n for n, l in enumerate(lines, 1) if "self.safe_eval" in l or "self.safe_f" in l]
defs  = [n for n, l in enumerate(lines, 1) if re.match(r'^\s+def\s+safe_(eval|f)\s*\(', l)]
w(f"   вызовов self.safe_*: {len(calls)} | определений внутри класса: {len(defs)}")
if calls and not defs:
    w("   ❌ Вызывается, но не определён как метод класса!")

# ---------- ИТОГ ----------
w("\n" + "=" * 78)
w(f"ИТОГО КРИТИЧНЫХ: {len(critical)}")
w("=" * 78)
w("\nСПИСОК ДЛЯ ИСПРАВЛЕНИЯ (строка | проблема):")
for n, why, was, fix in sorted(set(critical)):
    w(f"  {n:5d} | {why}")

REPORT.write_text(out.getvalue(), encoding="utf-8")
print(f"\n💾 Отчёт сохранён: {REPORT.resolve()}")
print("Пришли мне файл diagnose_report.txt — дам правки по этим номерам.")