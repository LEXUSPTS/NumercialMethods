# fix_entry.py
import re

with open("numerical_methods.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Находим строку с if __name__ или if name
entry_line = None
for i, line in enumerate(lines):
    if "__name__" in line and "main" in line:
        entry_line = i
        break
    if re.match(r'^\s*if\s+name\s*==', line) and "main" in line:
        entry_line = i
        break

if entry_line is None:
    print("❌ Блок if __name__ не найден!")
else:
    print(f"✅ Найден блок точки входа на строке {entry_line + 1}")

    # Убираем отступ у блока if __name__ и всего что после него
    fixed = []
    in_entry = False
    for i, line in enumerate(lines):
        if i == entry_line:
            in_entry = True
            # Убираем все ведущие пробелы/табы
            fixed.append(line.lstrip())
        elif in_entry:
            # Если строка пустая — оставляем как есть
            if line.strip() == "":
                fixed.append(line)
            else:
                # Убираем 4 пробела отступа (возвращаем на уровень модуля)
                if line.startswith("    "):
                    fixed.append(line[4:])
                else:
                    fixed.append(line.lstrip())
        else:
            fixed.append(line)

    with open("numerical_methods.py", "w", encoding="utf-8") as f:
        f.writelines(fixed)

    print("✅ Отступы блока точки входа исправлены!")
    print("🚀 Теперь запусти: python numerical_methods.py")