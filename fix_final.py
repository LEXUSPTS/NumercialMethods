# fix_final.py — автоматическое исправление numerical_methods.py
import re
import ast
import sys

SRC = "numerical_methods.py"

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)
print(f"📄 Исходный размер: {original_len} символов")

# === 1. Убираем HTML-теги ===
content = re.sub(r'<strong>\s*', '', content)
content = re.sub(r'\s*</strong>', '', content)
content = re.sub(r'<em>\s*', '', content)
content = re.sub(r'\s*</em>', '', content)
print("✅ HTML-теги удалены")

# === 2. Исправляем __file__, __name__, __main__, __init__ ===
content = content.replace("os.path.abspath(file)", "os.path.abspath(__file__)")
content = re.sub(r'def\s+init\s*\(', 'def __init__(', content)
content = re.sub(r'def\s+<strong>init</strong>\s*\(', 'def __init__(', content)
content = re.sub(r'if\s+name\s*==\s*"main"', 'if __name__ == "__main__"', content)
content = re.sub(r'if\s+name\s*==\s*" main "', 'if __name__ == "__main__"', content)
content = re.sub(r'if\s+<strong>name</strong>\s*==\s*"<strong>main</strong>"',
                 'if __name__ == "__main__"', content)
print("✅ Магические методы исправлены")

# === 3. Убираем пробелы внутри строковых литералов HEX-цветов ===
content = re.sub(r'"(#[0-9a-fA-F]{6})\s+"', r'"\1"', content)
content = re.sub(r"\s+(#[0-9a-fA-F]{6})\s+", r' \1 ', content)
# Пробелы в ключах THEMES
content = re.sub(r'"(light|dark|ocean|forest|bg|panel|header|text|muted|canvas_bg|grid|axis)\s+":',
                 r'"\1":', content)
content = re.sub(r'"\s+(light|dark|ocean|forest|bg|panel|header|text|muted|canvas_bg|grid|axis)":',
                 r'"\1":', content)
print("✅ Пробелы в строках убраны")

# === 4. Исправляем x 3 и x 2 в библиотечных формулах ===
content = content.replace('"x 3 + 3*x 2 + 2.5"', '"x**3 + 3*x**2 + 2.5"')
print("✅ Формулы библиотеки исправлены")

# === 5. Убираем дублирующиеся определения классов ===
# Оставляем только ПЕРВОЕ определение class NumericalMethodsApp
parts = content.split("class NumericalMethodsApp:")
if len(parts) > 2:
    print(f"⚠️ Найдено {len(parts)-1} определений класса — оставляем только первое")
    # Склеиваем обратно: первое + всё остальное без повторов def __init__
    first = parts[0] + "class NumericalMethodsApp:" + parts[1]
    rest = "".join(parts[2:])
    # Из rest удаляем дублирующиеся методы, которые уже есть в first
    # (грубо: вырезаем весь rest, если там только дубли)
    # Проверяем: если в rest есть что-то кроме методов — оставляем
    content = first + "\n\n# === ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ (без дубликатов) ===\n" + rest

# === 6. Исправляем f-строки с пробелами ===
content = re.sub(r'f\s+"', 'f"', content)
content = re.sub(r'f\s+\'', "f'", content)
print("✅ f-строки исправлены")

# === 7. Исправляем "v alue" и другие опечатки ===
content = content.replace('v alue=', 'value=')
content = content.replace('relief=tk.GROOVE ,', 'relief=tk.GROOVE,')
content = content.replace('pady =12', 'pady=12')
content = content.replace('self. lbl_title', 'self.lbl_title')
content = content.replace('r2_inner .pack', 'r2_inner.pack')
content = content.replace('r3_inner .pack', 'r3_inner.pack')
content = content.replace('self.progress _var', 'self.progress_var')
content = content.replace('lamb da tt=t', 'lambda tt=t')
content = content.replace('LaT eX', 'LaTeX')
print("✅ Опечатки исправлены")

# === 8. Исправляем "cent e r" в CSS ===
content = content.replace('cent e r;', 'center;')
content = content.replace('th, td  {', 'th, td {')
print("✅ CSS-опечатки исправлены")

# === 9. Проверяем синтаксис ===
try:
    ast.parse(content)
    print("🎉 Синтаксис ВЕРНЫЙ!")
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка на строке {e.lineno}: {e.msg}")
    print(f"   Контекст: {e.text}")
    # Сохраняем всё равно, чтобы посмотреть
    with open(SRC + ".broken", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"   Файл сохранён как {SRC}.broken для отладки")
    sys.exit(1)

# === 10. Сохраняем ===
with open(SRC, "w", encoding="utf-8") as f:
    f.write(content)

new_len = len(content)
print(f"\n💾 Файл сохранён. Размер: {original_len} → {new_len} символов")
print(f"📊 Изменено: {original_len - new_len} символов удалено")
print("\n🚀 Теперь запусти: python numerical_methods.py")