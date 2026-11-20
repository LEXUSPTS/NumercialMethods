import os

input_file = "numerical_methods.py"
output_file = "numerical_methods_clean.py"

if not os.path.exists(input_file):
    print(f"❌ Ошибка: Файл '{input_file}' не найден!")
    print("Убедитесь, что скрипт запущен в той же папке, что и ваш код.")
    exit()

print(f"⏳ Читаем файл '{input_file}'...")
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

original_count = len(lines)
print(f"📊 Найдено строк: {original_count}")

cleaned_lines = []

# ШАГ 1: Удаляем строго подряд идущие идентичные строки
for i, line in enumerate(lines):
    if i > 0 and line == lines[i-1]:
        continue  # Пропускаем, если строка полностью совпадает с предыдущей
    cleaned_lines.append(line)

# ШАГ 2: Удаляем лишние пустые строки (оставляем максимум 2 подряд)
final_lines = []
empty_count = 0
for line in cleaned_lines:
    if line.strip() == "":
        empty_count += 1
        if empty_count <= 2:
            final_lines.append(line)
    else:
        empty_count = 0
        final_lines.append(line)

# ШАГ 3: (Опционально) Убираем дубликаты 'def ' и 'class ', если они идут подряд
# Это лечит ситуацию, когда вы случайно вставили весь метод дважды
safe_final_lines = []
for i, line in enumerate(final_lines):
    stripped = line.lstrip()
    if stripped.startswith("def ") or stripped.startswith("class "):
        # Проверяем, не была ли предыдущая очищенная строка таким же объявлением
        if safe_final_lines and safe_final_lines[-1].lstrip() == stripped:
            continue
    safe_final_lines.append(line)

# Сохраняем результат
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(safe_final_lines)

final_count = len(safe_final_lines)
removed_count = original_count - final_count

print("✅ Очистка завершена успешно!")
print(f"📉 Удалено дубликатов: {removed_count} строк")
print(f"📈 Осталось строк: {final_count}")
print(f"💾 Результат сохранён в: '{output_file}'")
print("\n🔄 Теперь замените старый 'numerical_methods.py' на 'numerical_methods_clean.py' и проверьте работу.")