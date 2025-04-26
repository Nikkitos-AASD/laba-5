import re
import tkinter as tk
from tkinter import messagebox, filedialog, PhotoImage
from tkinter import ttk
import os

def update_line_numbers(text_area, line_numbers):
    """Обновление номеров строк."""
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete("1.0", tk.END)
    line_count = text_area.index(tk.END).split(".")[0]
    line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, int(line_count))))
    line_numbers.config(state=tk.DISABLED)

def on_text_change(event=None, text_area=None, line_numbers=None):
    """Обработчик изменения текста."""
    update_line_numbers(text_area, line_numbers)

def create_document():
    """Создание нового документа."""
    new_tab = ttk.Frame(notebook)
    notebook.add(new_tab, text="Новый документ")
    
    frame = tk.Frame(new_tab)
    frame.pack(fill=tk.BOTH, expand=True)
    
    line_numbers = tk.Text(frame, width=4, padx=3, takefocus=0, border=0, background="lightgray", state=tk.DISABLED)
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)
    
    text_area = tk.Text(frame, undo=True, font=("Arial", selected_size.get()))
    text_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
    text_area.bind("<KeyRelease>", lambda event: on_text_change(event, text_area, line_numbers))

    new_tab.text_area = text_area
    new_tab.file_path = None
    
    update_line_numbers(text_area, line_numbers)

def open_document():
    """Открытие документа."""
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        new_tab = ttk.Frame(notebook)
        notebook.add(new_tab, text=file_path.split("/")[-1])
        
        frame = tk.Frame(new_tab)
        frame.pack(fill=tk.BOTH, expand=True)
        
        line_numbers = tk.Text(frame, width=4, padx=3, takefocus=0, border=0, background="lightgray", state=tk.DISABLED)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        text_area = tk.Text(frame, undo=True, font=("Arial", selected_size.get()))
        text_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        text_area.bind("<KeyRelease>", lambda event: on_text_change(event, text_area, line_numbers))
        
        with open(file_path, "r", encoding="utf-8") as file:
            text_area.insert(tk.END, file.read())
        
        new_tab.text_area = text_area
        new_tab.file_path = file_path
        
        update_line_numbers(text_area, line_numbers)

def save_document():
    """Сохранить документ."""
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text_area = current_tab.text_area
        file_path = current_tab.file_path
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
        else:
            save_document_as()

def save_document_as():
    """Сохранить документ с новым именем."""
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text_area = current_tab.text_area
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                   filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            notebook.tab(current_tab, text=file_path.split("/")[-1])
            current_tab.file_path = file_path

def update_font_size(*args):
    """Обновить размер шрифта в активной вкладке, не меняя размер окна."""
    size = selected_size.get()
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        current_tab.text_area.config(font=("Arial", size))

def get_active_text_area():
    """Получить текстовое поле активной вкладки."""
    current_tab = notebook.nametowidget(notebook.select())
    return current_tab.text_area if current_tab and hasattr(current_tab, "text_area") else None

def setup_hotkeys(root):
    root.bind("<Control-n>", lambda event: create_document())  
    root.bind("<Control-o>", lambda event: open_document())  
    root.bind("<Control-s>", lambda event: save_document())  
    root.bind("<Control-Shift-S>", lambda event: save_document_as())  
    root.bind("<Control-q>", lambda event: exit_program())  

    root.bind("<Control-z>", lambda event: undo(get_active_text_area()))  
    root.bind("<Control-y>", lambda event: redo(get_active_text_area()))  
    root.bind("<Control-x>", lambda event: cut_text(get_active_text_area()))  
    root.bind("<Control-c>", lambda event: copy_text(get_active_text_area()))  
    root.bind("<Control-v>", lambda event: paste_text(get_active_text_area()))  
    root.bind("<Control-a>", lambda event: select_all(get_active_text_area()))  




# === Основной анализатор ===
def lexical_analyzer(text, file_path):
    # --- Очистка текста и удаление невалидных символов ---
    def clean_and_report_invalid_fragments(text):
        result = ''
        invalid_fragments = []
        buffer = ''
        i = 0

        def is_valid_char(c):
            return c.isalnum() or c == '_' or c in 'аА' or c in "+-*/()"

        while i < len(text):
            c = text[i]

            if c in '+-':
                if i + 1 < len(text) and text[i + 1].isdigit():
                    buffer += c
                    i += 1
                    buffer += text[i]
                    i += 1
                    while i < len(text) and text[i].isdigit():
                        buffer += text[i]
                        i += 1
                    result += buffer
                    buffer = ''
                    continue
                else:
                    buffer += c
                    i += 1
                    continue

            if is_valid_char(c):
                buffer += c
            else:
                if buffer:
                    result += buffer
                    buffer = ''

                if c.isspace() or c in ":=;":
                    result += c
                else:
                    invalid_segment = ''
                    while i < len(text) and not is_valid_char(text[i]) and not text[i].isspace() and text[i] not in ":=;":
                        invalid_segment += text[i]
                        i += 1
                    if invalid_segment:
                        invalid_fragments.append(invalid_segment)
                    continue
            i += 1

        if buffer:
            result += buffer

        report = ""
        for idx, fragment in enumerate(invalid_fragments, 1):
            report += f"{idx} удалённый фрагмент - {fragment}\n"

        return report, result

    # --- Проверка ключевых слов и структуры ---
    def check_keywords_and_report_errors(cleaned_text):
        keywords = ['const', 'val', 'int']
        required_symbols = [':', '=', ';']
        tokens = cleaned_text.split()
        errors = []
        found_keywords = set()
        mistaken_keywords = set()

        has_equal = '=' in cleaned_text
        value_token = None
        if has_equal:
            parts = cleaned_text.split('=')
            if len(parts) > 1:
                expr_part = parts[1]
                expr_part = expr_part.split(';')[0].strip()
                value_token = expr_part
        else:
            errors.append("нет токена (=)")

        for token in tokens:
            if token in keywords:
                found_keywords.add(token)
                continue

            if token in [':', '=', ';']:
                continue

            if value_token and token in value_token:
                continue

            if token and token[0].isdigit():
                errors.append(f"токен не может начинаться с числа ({token})")

            for kw in keywords:
                if kw in token and any(char.isdigit() for char in token):
                    errors.append(f"ожидалось ключевое слово ({kw}) – встретился идентификатор '{token}'")
                    mistaken_keywords.add(kw)
                    break
                elif len(token) >= len(kw) - 1 and levenshtein(token, kw) <= 2:
                    errors.append(f"ожидалось ключевое слово ({kw}) – встретился идентификатор '{token}'")
                    mistaken_keywords.add(kw)
                    break

        for kw in keywords:
            if kw not in found_keywords and kw not in mistaken_keywords:
                errors.append(f"нет токена ({kw})")

        for symbol in required_symbols:
            if symbol not in cleaned_text:
                errors.append(f"нет токена ({symbol})")

        return errors

    # --- Расстояние Левенштейна ---
    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            return levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    # --- Безопасное вычисление выражения ---
    def parse_and_evaluate_expression(expression):
        try:
            if not re.fullmatch(r'[\d+\-*/().\s]+', expression):
                return "Выражение содержит недопустимые символы."
            result = eval(expression)
            return result
        except ZeroDivisionError:
            return "Ошибка: деление на ноль."
        except Exception as e:
            return f"Ошибка вычисления: {str(e)}"

    # === Этап анализа ===
    report, cleaned_text = clean_and_report_invalid_fragments(text)
    errors = check_keywords_and_report_errors(cleaned_text)

    for row in output_table.get_children():
        output_table.delete(row)

    for idx, line in enumerate(report.strip().split('\n'), start=1):
        if line.strip():
            output_table.insert("", "end", values=(
                "E001", "невалидный фрагмент",
                line.split(" - ")[-1],
                f"{idx}", file_path, "1"
            ))

    for idx, err in enumerate(errors, start=1):
        output_table.insert("", "end", values=(
            "E002", "Ошибка",
            err,
            f"{idx}", file_path, "1"
        ))

    if not report.strip() and not errors:
        if '=' in cleaned_text:
            expression = cleaned_text.split('=')[1].split(';')[0].strip()
            result = parse_and_evaluate_expression(expression)
            messagebox.showinfo("Результат", f"Ошибок не обнаружено.\n\nРезультат выражения: {result}")
        else:
            messagebox.showinfo("Результат", "Ошибок не обнаружено.")

# === Функция запуска анализа из GUI ===
def syntax_analysis():
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text = current_tab.text_area.get("1.0", tk.END).rstrip()
        file_path = getattr(current_tab, "file_path", "Без имени")
        lexical_analyzer(text, file_path)
    else:
        messagebox.showerror("Ошибка", "Нет активного документа!") 





def undo(text_area):
    """Отменить действие."""
    if text_area:
        text_area.event_generate("<<Undo>>")

def redo(text_area):
    """Повторить действие."""
    if text_area:
        text_area.event_generate("<<Redo>>")

def cut_text(text_area):
    """Вырезать текст."""
    if text_area:
        text_area.event_generate("<<Cut>>")

def copy_text(text_area):
    """Копировать текст."""
    if text_area:
        text_area.event_generate("<<Copy>>")

def paste_text(text_area):
    """Вставить текст."""
    if text_area:
        text_area.event_generate("<<Paste>>")

def select_all(text_area):
    """Выделить весь текст."""
    if text_area:
        text_area.tag_add("sel", "1.0", tk.END)

def exit_program():
    """Выход из программы."""
    root.quit()

def delete_text(text_area):
    """Удалить текст."""
    text_area.delete("1.0", tk.END)

def show_help():
    """Показать справку."""
    messagebox.showinfo("Справка", "Это руководство пользователя.")

def about():
    """Информация о программе."""
    messagebox.showinfo("О программе", "Информация о программе.")

# Создание окна
root = tk.Tk()
root.title("Редактор")

# Устанавливаем начальные размеры окна
root.geometry("800x600")

# Главное меню
menu_bar = tk.Menu(root)

# Файл
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Создать", command=create_document)
file_menu.add_command(label="Открыть", command=open_document)
file_menu.add_command(label="Сохранить как", command=save_document_as)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=exit_program)
menu_bar.add_cascade(label="Файл", menu=file_menu)

# Правка
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Отменить", command=lambda: undo(get_active_text_area()))
edit_menu.add_command(label="Повторить", command=lambda: redo(get_active_text_area()))
edit_menu.add_separator()
edit_menu.add_command(label="Вырезать", command=lambda: cut_text(get_active_text_area()))
edit_menu.add_command(label="Копировать", command=lambda: copy_text(get_active_text_area()))
edit_menu.add_command(label="Вставить", command=lambda: paste_text(get_active_text_area()))
edit_menu.add_separator()
edit_menu.add_command(label="Удалить", command=lambda: delete_text(get_active_text_area()))
edit_menu.add_command(label="Выделить все", command=lambda: select_all(get_active_text_area()))
menu_bar.add_cascade(label="Правка", menu=edit_menu)

# Пуск
run_menu = tk.Menu(menu_bar, tearoff=0)
run_menu.add_command(label="Синтаксический анализ", command=syntax_analysis)
menu_bar.add_cascade(label="Пуск", menu=run_menu)

# Справка
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Вызов справки", command=show_help)
help_menu.add_separator()
help_menu.add_command(label="О программе", command=about)
menu_bar.add_cascade(label="Справка", menu=help_menu)

root.config(menu=menu_bar)

# Панель инструментов
toolbar = tk.Frame(root)

# Загрузка изображений
icons = {
    "Создать": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/new.png"),
    "Открыть": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/open.png"),
    "Сохранить": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/save.png"),
    "Сохранить как": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/save.png"), 
    "Отменить": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/undo.png"),
    "Повторить": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/redo.png"),
    "Копировать": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/copy.png"),
    "Вырезать": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/cut.png"),
    "Вставить": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/paste.png"),
    "пуск": PhotoImage(file="C:/Users/nikit/Desktop/КР/icons/pusk.png"),
}

buttons = [
    ("Создать", create_document),
    ("Открыть", open_document),
    ("Сохранить как", save_document),
    ("Отменить", lambda: undo(get_active_text_area())),
    ("Повторить", lambda: redo(get_active_text_area())),
    ("Копировать", lambda: copy_text(get_active_text_area())),
    ("Вырезать", lambda: cut_text(get_active_text_area())),
    ("Вставить", lambda: paste_text(get_active_text_area())),
    ("пуск", syntax_analysis),
]

for text, command in buttons:
    btn = tk.Button(toolbar, image=icons.get(text), command=command)
    btn.image = icons.get(text)
    btn.pack(side=tk.LEFT, padx=2, pady=2)

toolbar.pack(fill=tk.X)

# Размер шрифта
font_sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36]
selected_size = tk.IntVar(value=12)
font_size_menu = tk.OptionMenu(toolbar, selected_size, *font_sizes, command=update_font_size)
font_size_menu.pack(side=tk.LEFT, padx=5, pady=2)

# Словарь языков
LANGUAGES = {
    "Русский": {
        "file": "Файл",
        "edit": "Правка",
        "run": "Пуск",
        "help": "Справка",
        "create": "Создать",
        "open": "Открыть",
        "save_as": "Сохранить как",
        "exit": "Выход",
        "undo": "Отменить",
        "redo": "Повторить",
        "cut": "Вырезать",
        "copy": "Копировать",
        "paste": "Вставить",
        "delete": "Удалить",
        "select_all": "Выделить все",
        "syntax_analysis": "Синтаксический анализ",
        "about": "О программе",
        "help_call": "Вызов справки",
    },
    "English": {
        "file": "File",
        "edit": "Edit",
        "run": "Run",
        "help": "Help",
        "create": "New",
        "open": "Open",
        "save_as": "Save As",
        "exit": "Exit",
        "undo": "Undo",
        "redo": "Redo",
        "cut": "Cut",
        "copy": "Copy",
        "paste": "Paste",
        "delete": "Delete",
        "select_all": "Select All",
        "syntax_analysis": "Syntax Analysis",
        "about": "About",
        "help_call": "Help",
    },
}

# Переменная для хранения текущего языка
selected_language = tk.StringVar(value="Русский")

def change_language(event=None):
    """Изменяет язык интерфейса"""
    lang = selected_language.get()
    translation = LANGUAGES[lang]

    # Обновление текста меню
    menu_bar.entryconfig(1, label=translation["file"])
    menu_bar.entryconfig(2, label=translation["edit"])
    menu_bar.entryconfig(3, label=translation["run"])
    menu_bar.entryconfig(4, label=translation["help"])

    file_menu.entryconfig(0, label=translation["create"])
    file_menu.entryconfig(1, label=translation["open"])
    file_menu.entryconfig(2, label=translation["save_as"])
    file_menu.entryconfig(4, label=translation["exit"])

    edit_menu.entryconfig(0, label=translation["undo"])
    edit_menu.entryconfig(1, label=translation["redo"])
    edit_menu.entryconfig(3, label=translation["cut"])
    edit_menu.entryconfig(4, label=translation["copy"])
    edit_menu.entryconfig(5, label=translation["paste"])
    edit_menu.entryconfig(7, label=translation["delete"])
    edit_menu.entryconfig(8, label=translation["select_all"])

    run_menu.entryconfig(0, label=translation["syntax_analysis"])

    help_menu.entryconfig(0, label=translation["help_call"])
    help_menu.entryconfig(2, label=translation["about"])

# Добавляем выпадающий список выбора языка
language_menu = ttk.Combobox(toolbar, textvariable=selected_language, values=list(LANGUAGES.keys()), state="readonly")
language_menu.pack(side=tk.RIGHT, padx=10)
language_menu.bind("<<ComboboxSelected>>", change_language)

# Строка состояния
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor="w")
status_label.pack(side=tk.BOTTOM, fill=tk.X) 

# Создание вкладок
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Окно для вывода результатов
output_frame = tk.Frame(root)
output_frame.pack(fill=tk.BOTH, expand=False)

# Инициализация переменной для отображения статуса
status_label_var = tk.StringVar()

# Инициализация Label для отображения статуса
status_label = tk.Label(root, textvariable=status_label_var)
status_label.pack()

# Создание таблицы
columns = ("code", "type", "lexeme", "position", "file_path", "line")
output_table = ttk.Treeview(output_frame, columns=columns, show="headings")
# Определяем заголовки столбцов
output_table.heading("code", text="Код")
output_table.heading("type", text="Тип лексемы")
output_table.heading("lexeme", text="Лексема")
output_table.heading("position", text="Позиция")
output_table.heading("file_path", text="Файл")
output_table.heading("line", text="Строка")

# Определяем ширину колонок
output_table.column("code", width=50, anchor="center")
output_table.column("type", width=200)
output_table.column("lexeme", width=150)
output_table.column("position", width=100)
output_table.column("file_path", width=200)
output_table.column("line", width=50)

# Добавляем скроллбар
scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=output_table.yview)
output_table.configure(yscroll=scrollbar.set)

# Располагаем элементы
output_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def check_unsaved_changes():
    """Проверяет наличие несохраненных изменений перед выходом или выполнением других операций."""
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text_area = current_tab.text_area
        file_path = current_tab.file_path

        current_text = text_area.get("1.0", tk.END).strip()
        original_text = ""

        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                original_text = file.read().strip()

        if current_text != original_text:  # Если текст изменился
            response = messagebox.askyesnocancel("Несохраненные изменения", "Файл был изменен. Сохранить перед закрытием?")
            if response:  # Если нажата кнопка "Да"
                save_document()
            return response  # True - продолжить, None - отмена действия

    return True  # Если изменений нет

def confirm_exit():
    """Подтверждение выхода из программы."""
    if check_unsaved_changes() is not None:
        root.quit()

def confirm_open_document():
    """Подтверждение открытия нового документа."""
    if check_unsaved_changes() is not None:
        open_document()

def confirm_create_document():
    """Подтверждение создания нового документа."""
    if check_unsaved_changes() is not None:
        create_document()

# Переназначение команд меню для проверки изменений
root.protocol("WM_DELETE_WINDOW", confirm_exit)  # Обработка закрытия окна
file_menu.entryconfig("Открыть", command=confirm_open_document)
file_menu.entryconfig("Создать", command=confirm_create_document)

# Установка иконки
root.iconbitmap("C:/Users/nikit/Desktop/КР/icons/ico.ico")

# Запуск основного цикла приложения
root.mainloop()

 


