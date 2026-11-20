# fix_indent.py
"""Автоматически исправляет отступы в numerical_methods.py"""
import re

with open("numerical_methods.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Методы, которые должны быть внутри класса (отступ 4)
METHODS_TO_FIX = [
    "render_graph_to_image", "save_graph_png", "save_graph_image",
    "export_svg", "export_html", "export_csv", "export_latex",
    "export_pdf", "export_excel", "export_markdown",
    "show_animation_dialog", "start_animation", "stop_animation",
    "show_step_by_step", "show_contour_plot", "show_vector_field",
    "show_interactive_tutorial", "show_cloud_sync_dialog",
    "solve_analytical", "_show_analytical_results",
    "add_extra_equation", "manage_extra_equations", "evaluate_at_point",
    "detect_parameters", "show_param_sliders", "_on_param_change",
    "_redraw_with_params", "_toggle_param_animation", "_animate_param",
    "import_formulas_from_file", "_import_from_txt", "_import_from_json",
    "_import_from_csv", "save_session", "load_session",
    "check_for_updates", "_offer_update", "_apply_update",
    "load_library", "save_library_to_file", "refresh_library_combo",
    "load_from_library", "save_to_library", "open_library_manager",
    "show_calculator", "show_history", "show_help", "show_tutorial",
    "show_glossary", "run_builtin_tests", "show_achievements",
    "show_stats", "generate_problem", "batch_process_dialog",
    "_load_settings", "_save_settings", "load_history", "save_history",
]

fixed_lines = []
in_class = False
fix_mode = False

for i, line in enumerate(lines):
    stripped = line.lstrip()

    # Определяем начало класса
    if stripped.startswith("class NumericalMethodsApp:"):
        in_class = True
        fix_mode = False
        fixed_lines.append(line)
        continue

    # Определяем конец класса (if __name__)
    if stripped.startswith("if __name__") or stripped.startswith("if name"):
        fix_mode = False
        in_class = False
        fixed_lines.append(line)
        continue

    # Проверяем, является ли строка определением метода
    match = re.match(r'^def (\w+)\(', stripped)
    if match and in_class:
        method_name = match.group(1)
        if method_name in METHODS_TO_FIX:
            # Если отступ 0 — добавляем 4 пробела
            if not line.startswith("    ") and not line.startswith("\t"):
                line = "    " + line
                print(f"Исправлен отступ: {method_name} (строка {i + 1})")

    fixed_lines.append(line)

with open("numerical_methods.py", "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print("✅ Готово! Отступы исправлены.")