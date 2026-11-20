# fix_all.py — автоматическое исправление отступов
import re

with open("numerical_methods.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Методы, которые должны быть внутри класса (отступ 4)
METHODS_IN_CLASS = {
    '_btn', 'on_closing', 'toggle_fullscreen', 'exit_fullscreen',
    'save_view_to_history', 'view_back', 'view_forward', 'toggle_theme',
    'apply_theme', 'parse_equation', 'solve', '_handle_calc_error',
    'finish_solve', '_auto_fit_y', '_notify_achievement', 'show_results',
    '_draw_log_convergence', '_show_integral_tab', '_show_all_roots_tab',
    '_show_benchmark_tab', 'df', 'd2f', 'bisection', 'chord_method',
    'newton_method', 'secant_method', 'reset_view', 'on_zoom',
    'on_drag_start', 'on_drag_motion', 'on_drag_end', 'on_mouse_move',
    'on_right_click', '_center_at', 'on_canvas_double_click', '_on_resize',
    '_to_scr', 'find_extrema', 'draw_graph', 'render_graph_to_image',
    'save_graph_png', 'save_graph_image', 'export_svg', 'export_html',
    'export_csv', 'export_latex', 'export_pdf', 'export_excel',
    'export_markdown', 'show_animation_dialog', 'start_animation',
    'stop_animation', 'add_extra_equation', 'manage_extra_equations',
    'evaluate_at_point', 'detect_parameters', 'show_param_sliders',
    '_on_param_change', '_redraw_with_params', '_toggle_param_animation',
    '_animate_param', 'import_formulas_from_file', '_import_from_txt',
    '_import_from_json', '_import_from_csv', 'solve_analytical',
    '_show_analytical_results', 'export_analytical_report',
    'show_3d_graph', 'show_contour_plot', 'show_vector_field',
    'show_step_by_step', 'show_interactive_tutorial',
    'show_cloud_sync_dialog', 'show_reference', 'save_session',
    'load_session', 'check_for_updates', '_offer_update', '_apply_update',
    'load_library', 'save_library_to_file', 'refresh_library_combo',
    'load_from_library', 'save_to_library', 'open_library_manager',
    'show_calculator', 'show_history', 'show_help', 'show_tutorial',
    'show_glossary', 'run_builtin_tests', 'show_achievements',
    'show_stats', 'generate_problem', 'batch_process_dialog',
    '_load_settings', '_save_settings', 'load_history', 'save_history',
    '_on_var_mode_change', '_show_multi_var_dialog',
}

fixed = []
in_class = False

for i, line in enumerate(lines):
    stripped = line.lstrip()

    # Начало класса
    if stripped.startswith("class NumericalMethodsApp:"):
        in_class = True
        fixed.append(line)
        continue

    # Конец класса (if __name__ или if name)
    if stripped.startswith("if ") and ("__name__" in stripped or 'name' in stripped and 'main' in stripped):
        in_class = False
        fixed.append(line)
        continue

    # Проверяем метод
    match = re.match(r'^def (\w+)\(', stripped)
    if match and in_class:
        method_name = match.group(1)
        if method_name in METHODS_IN_CLASS:
            # Если отступ 0 — добавляем 4 пробела
            if not line.startswith("    ") and not line.startswith("\t"):
                line = "    " + line
                print(f"✅ Исправлен отступ: {method_name} (строка {i + 1})")

    fixed.append(line)

content = '\n'.join(fixed)

# Исправляем HTML-теги
content = content.replace("<strong>__", "__")
content = content.replace("__</strong>", "__")
content = content.replace("<strong>file</strong>", "__file__")
content = content.replace("<strong>name</strong>", "__name__")
content = content.replace("<strong>main</strong>", "__main__")
content = content.replace("<strong>init</strong>", "__init__")
content = content.replace("if name == ", "if __name__ == ")
content = content.replace('" main "', '"__main__"')

with open("numerical_methods.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n🎉 Готово! Отступы и теги исправлены.")