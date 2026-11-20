LANGUAGES = {
    "ru": {
        "app_title": "Численные методы · Turbo Edition",
        "fx": "f(x) =", "interval_a": "a =", "interval_b": "b =", "sigma": "σ =",
        "solve": "▶ ВЫЧИСЛИТЬ ВСЁ", "animate": "🎬 Анимация", "theme": "🌗 Сменить тему",
        "keyboard": "🧮 Клавиатура", "history": "📜 История", "save": "💾 Сохранить",
        "library": "📚 Библиотека:", "manage": "⚙ Управление", "help": "📖 Справка",
        "graph": "📈  Интерактивный график", "reset": "🔄 Сброс",
        "ready": "Готово к работе", "calculating": "⏳ Идет расчет...",
        "done": "✅ Расчет завершен!", "error": "Ошибка",
        "tab_bisection": "  ⚖  Половинное  ", "tab_chord": "  📐  Хорды  ",
        "tab_newton": "  🚀  Ньютон  ", "tab_secant": "  ✂  Секущие  ",
        "tab_brent": "  🎯  Брент  ", "tab_mpi": "  🔄  МПИ  ",
        "tab_convergence": "  📊  Скорость сходимости  ", "tab_integral": "  ∫  Интеграл  ",
    },
    "en": {
        "app_title": "Numerical Methods · Turbo Edition",
        "fx": "f(x) =", "interval_a": "a =", "interval_b": "b =", "sigma": "σ =",
        "solve": "▶ SOLVE ALL", "animate": "🎬 Animate", "theme": "🌗 Theme",
        "keyboard": "🧮 Keyboard", "history": "📜 History", "save": "💾 Save",
        "library": "📚 Library:", "manage": "⚙ Manage", "help": "📖 Help",
        "graph": "📈  Interactive Graph", "reset": "🔄 Reset",
        "ready": "Ready", "calculating": "⏳ Calculating...",
        "done": "✅ Done!", "error": "Error",
        "tab_bisection": "  ⚖  Bisection  ", "tab_chord": "  📐  Chord  ",
        "tab_newton": "  🚀  Newton  ", "tab_secant": "  ✂  Secant  ",
        "tab_brent": "  🎯  Brent  ", "tab_mpi": "  🔄  MPI  ",
        "tab_convergence": "  📊  Convergence  ", "tab_integral": "  ∫  Integral  ",
    }
}

class Translator:
    def __init__(self, lang="ru"):
        self.lang = lang if lang in LANGUAGES else "ru"
    def set_language(self, lang):
        if lang in LANGUAGES: self.lang = lang
    def t(self, key):
        return LANGUAGES[self.lang].get(key, key)