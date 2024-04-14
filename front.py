import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from modules.file2 import code_2
from modules.file3 import code_3

# Глобальные переменные
directory_path = ""
filter_vars = []
filter_mapping = {
    "Паспорт": "passport",
    "Номер телефона": "phone",
    "Банковский счет": "account",
    "СНИЛС": "snils",
    "Номер карты": "card"
}
selected_filters = []
standard_filters = []  # Дополнительная переменная для хранения выбранных стандартных фильтров
custom_filters = {}


# Функция для выбора директории
def select_directory():
    global directory_path
    directory_path = filedialog.askdirectory()
    if directory_path:
        directory_label.config(text="Выбранная директория: " + directory_path)
        directory_frame.pack_forget()
        filters_frame.pack()
        custom_filter_button.pack()
        continue_button.pack()
        select_filters()
    else:
        directory_label.config(text="Директория не выбрана")

def select_filters():
    global selected_filters

    filter_labels = []
    filter_entries = []

    filter_options = ["Паспорт", "Номер телефона", "Банковский счет", "СНИЛС", "Номер карты"]

    selected_filters = []

    def on_filter_selection():
        selected_filters.clear()
        selected_filters.extend([filter_mapping[option] for option, var in zip(filter_options, filter_vars) if var.get()])

    for i, option in enumerate(filter_options):
        filter_label = tk.Label(filters_frame, text=option, font=("Helvetica", 12), fg="black")
        filter_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        filter_labels.append(filter_label)

        filter_var = tk.IntVar()
        filter_vars.append(filter_var)

        filter_entry = tk.Checkbutton(filters_frame, variable=filter_var, onvalue=1, offvalue=0, font=("Helvetica", 12), command=on_filter_selection)
        filter_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        filter_entries.append(filter_entry)

    def continue_button_click_after_filters():
        global selected_filters, standard_filters
        if not selected_filters and not custom_filters:
            tk.messagebox.showwarning("Предупреждение", "Выберите хотя бы один фильтр!")
            return
        standard_filters = selected_filters.copy()  # Копируем выбранные фильтры в стандартные
        continue_button_click(selected_filters)


    continue_button.config(command=continue_button_click_after_filters)


def create_custom_filter():
    def save_custom_filter():
        custom_filter_name = custom_filter_name_entry.get()
        custom_filter_pattern = custom_filter_pattern_entry.get()
        if custom_filter_name and custom_filter_pattern:
            filter_option_label = tk.Label(filters_frame, text=custom_filter_name, font=("Helvetica", 12), fg="black")
            filter_option_label.grid(row=len(filter_mapping)+1, column=0, padx=10, pady=5, sticky="w")

            filter_var = tk.IntVar()
            filter_option_entry = tk.Checkbutton(filters_frame, variable=filter_var, onvalue=1, offvalue=0, font=("Helvetica", 12))
            filter_option_entry.grid(row=len(filter_mapping)+1, column=1, padx=10, pady=5, sticky="w")

            filter_mapping[custom_filter_name] = custom_filter_name.lower().replace(" ", "_")

            custom_filters[custom_filter_name] = custom_filter_pattern  # Добавляем кастомный фильтр в словарь

            standard_filters.clear()  # Очищаем стандартные фильтры

        custom_filter_window.destroy()

    custom_filter_window = tk.Toplevel(root)
    custom_filter_window.title("Свой фильтр")

    custom_filter_name_label = tk.Label(custom_filter_window, text="Название фильтра:", font=("Helvetica", 14), fg="black")
    custom_filter_name_label.pack(pady=5)

    custom_filter_name_entry = tk.Entry(custom_filter_window, font=("Helvetica", 12))
    custom_filter_name_entry.pack(pady=5)

    custom_filter_pattern_label = tk.Label(custom_filter_window, text="Образец данных:", font=("Helvetica", 14), fg="black")
    custom_filter_pattern_label.pack(pady=5)

    custom_filter_pattern_entry = tk.Entry(custom_filter_window, font=("Helvetica", 12))
    custom_filter_pattern_entry.pack(pady=5)

    save_custom_filter_button = tk.Button(custom_filter_window, text="Продолжить", command=save_custom_filter, font=("Helvetica", 12), bg="gray", fg="black")
    save_custom_filter_button.pack(pady=5)


def continue_button_click(selected_filters):
    global standard_filters
    if standard_filters:  # Проверяем, есть ли выбранные стандартные фильтры
        results = code_2(directory_path, standard_filters)
    elif selected_filters:  # Если стандартных фильтров нет, но есть выбранные фильтры, используем их
        results = code_2(directory_path, selected_filters)
    elif custom_filters:  # Если есть кастомные фильтры, применяем их по очереди
        for filter_name, example_data in custom_filters.items():
            results = code_3(directory_path, filter_name, example_data)
    show_results(results)

# Функция для отображения результатов
def show_results(results):
    result_window = tk.Toplevel(root)
    result_window.title("Результаты анализа")
    result_window.geometry("800x600")
    global selected_filters, custom_filters
    if not custom_filters:
        selected_filters_tags = [filter_name for filter_name in standard_filters if filter_name in results['total_leaks']] 
    elif selected_filters:
        selected_filters_tags = [filter_name for filter_name in selected_filters if filter_name in results['total_leaks']]
    elif custom_filters:
        selected_filters_tags = [filter_name for filter_name in custom_filters if filter_name in results['total_leaks']]
    else:
        selected_filters_tags = [filter_name for filter_name in standard_filters if filter_name in results['total_leaks']]

    tree = ttk.Treeview(result_window, columns=("Файл", *selected_filters_tags), show="headings")
    tree.heading("#0", text="Файл")
    for i, filter_name in enumerate(selected_filters_tags, start=1):
        tree.heading("#"+str(i+1), text=filter_name)
        tree.column("#"+str(i+1), width=30, anchor="center")

    for filename, leaks in results["files_with_selected_leaks"]:
        values = [filename]
        for filter_name in selected_filters_tags:
            values.append(leaks.get(filter_name, 0))
        tree.insert("", "end", text="", values=values, tags=('centered',))

    for tag in ['centered']:
        tree.tag_configure(tag, anchor='center')

    tree.pack(expand=True, fill=tk.BOTH)


# Создание главного окна
root = tk.Tk()
root.title("Выбор директории и фильтров")
root.geometry("600x400")

# Создание рамки для выбора директории
directory_frame = tk.Frame(root)
directory_frame.pack(padx=20, pady=20)

# Метка для отображения выбранной директории
directory_label = tk.Label(directory_frame, text="Директория не выбрана", font=("Helvetica", 14), fg="red")
directory_label.pack(pady=10)

# Кнопка выбора директории
select_button = tk.Button(directory_frame, text="Выбрать директорию", command=select_directory, font=("Helvetica", 12), bg="gray", fg="black")
select_button.pack(pady=10)

# Создание фрейма для фильтров
filters_frame = tk.Frame(root)

# Кнопка создания своего фильтра
custom_filter_button = tk.Button(root, text="Создать свой фильтр", command=create_custom_filter, font=("Helvetica", 12), bg="gray", fg="black")
custom_filter_button.pack_forget()

# Кнопка "Продолжить"
continue_button = tk.Button(root, text="Продолжить", font=("Helvetica", 12), bg="gray", fg="black", command=lambda: continue_button_click(selected_filters))
continue_button.pack_forget()

# Запуск основного цикла приложения
root.mainloop()
