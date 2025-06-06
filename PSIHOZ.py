import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from tkinter.font import Font

# Инициализация NLP
try:
    nltk.data.find('vader_lexicon')
except:
    nltk.download('vader_lexicon')

class PsihozApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Psihoz - Дневник психического здоровья")
        self.root.geometry("1000x750")
        self.root.configure(bg="#FDDBB4")
        
        # Установка иконки приложения (замените путь на свой)
        try:
            self.root.iconbitmap('psihoz_icon.ico')  # Для Windows
        except:
            pass

        # Цвета из ТЗ
        self.bg_color = "#FDDBB4"
        self.button_color = "#96976B"
        self.text_color = "#FFFFFF"
        self.accent_color = "#80815A"
        self.text_dark = "#333333"

        # Шрифты
        self.title_font = Font(family="Arial", size=18, weight="bold")
        self.subtitle_font = Font(family="Arial", size=14, weight="bold")
        self.text_font = Font(family="Arial", size=12)
        self.small_font = Font(family="Arial", size=11)

        # Инициализация анализатора настроения
        self.sia = SentimentIntensityAnalyzer()

        # Подключение к базе данных
        self.conn = sqlite3.connect('psihoz.db')
        self.create_tables()

        # Создание интерфейса
        self.configure_styles()
        self.create_widgets()

        # Загрузка данных пользователя
        self.load_data()

    def configure_styles(self):
        # Настройка стилей
        style = ttk.Style()
        
        # Общий стиль для виджетов
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_dark, font=self.text_font)
        style.configure('TButton', font=self.text_font)
        
        # Стиль для акцентных кнопок (исправлен цвет текста)
        style.configure('Accent.TButton', 
                       background=self.button_color,
                       foreground=self.text_dark,  # Изменено на темный текст
                       font=self.subtitle_font,
                       padding=10,
                       relief='flat',
                       borderwidth=0,
                       focuscolor=self.bg_color)
        
        style.map('Accent.TButton',
                 background=[('active', self.accent_color)],
                 foreground=[('active', self.text_dark)])  # Изменено на темный текст
        
        # Стиль для радиокнопок
        style.configure('TRadiobutton', 
                      background=self.bg_color,
                      foreground=self.text_dark,
                      font=self.text_font)
        
        # Стиль для Treeview (таблицы)
        style.configure('Treeview', 
                      rowheight=30,
                      font=self.small_font,
                      background="#96976B",
                      fieldbackground="#FFFFFF")
        
        style.configure('Treeview.Heading', 
                      background=self.button_color,
                      foreground=self.text_color,  # Белый текст для заголовков
                      font=self.text_font,
                      padding=5)
        
        style.map('Treeview', 
                 background=[('selected', self.accent_color)],
                 foreground=[('selected', self.text_color)])

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mood TEXT NOT NULL,
                note TEXT,
                symptoms TEXT,
                sentiment_score REAL
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок с логотипом
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Логотип
        logo_label = tk.Label(header_frame, 
                             text="PSIHOZ", 
                             font=("Arial", 24, "bold"), 
                             bg=self.bg_color,
                             fg=self.button_color)
        logo_label.pack(side=tk.LEFT)
        
        # Подзаголовок
        subtitle_label = tk.Label(header_frame,
                                text="Дневник психического здоровья",
                                font=self.subtitle_font,
                                bg=self.bg_color,
                                fg=self.text_dark)
        subtitle_label.pack(side=tk.LEFT, padx=10)

        # Notebook для разделов
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка "Новая запись"
        self.create_new_entry_tab()

        # Вкладка "История"
        self.create_history_tab()

        # Вкладка "Аналитика"
        self.create_analytics_tab()

        # Вкладка "Экстренная помощь" (улучшенная)
        self.create_emergency_tab()

    def create_new_entry_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="✏️ Новая запись")

        # Основной контейнер
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Карточка для формы
        form_card = ttk.Frame(container)
        form_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Дата
        date_frame = ttk.Frame(form_card)
        date_frame.pack(fill=tk.X, pady=10)
        ttk.Label(date_frame, text="Дата:").pack(side=tk.LEFT, padx=5)
        self.entry_date = ttk.Entry(date_frame, font=self.text_font)
        self.entry_date.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

        # Настроение
        mood_frame = ttk.Frame(form_card)
        mood_frame.pack(fill=tk.X, pady=15)
        ttk.Label(mood_frame, text="Настроение:").pack(side=tk.LEFT, padx=5)
        
        mood_container = ttk.Frame(mood_frame)
        mood_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.mood_var = tk.StringVar()
        moods = ["Отлично 😊", "Хорошо 🙂", "Нормально 😐", "Плохо 🙁", "Ужасно 😞"]
        for mood in moods:
            rb = ttk.Radiobutton(mood_container, 
                                text=mood, 
                                variable=self.mood_var, 
                                value=mood,
                                style='TRadiobutton')
            rb.pack(side=tk.LEFT, padx=10)

        # Симптомы
        symptoms_frame = ttk.Frame(form_card)
        symptoms_frame.pack(fill=tk.X, pady=10)
        ttk.Label(symptoms_frame, text="Симптомы (через запятую):").pack(side=tk.LEFT, padx=5)
        self.entry_symptoms = ttk.Entry(symptoms_frame, font=self.text_font)
        self.entry_symptoms.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Заметка
        note_frame = ttk.Frame(form_card)
        note_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        ttk.Label(note_frame, text="Заметка:").pack(anchor='w', padx=5)
        
        note_container = ttk.Frame(note_frame)
        note_container.pack(fill=tk.BOTH, expand=True)
        
        self.text_note = tk.Text(note_container, 
                                font=self.text_font, 
                                wrap=tk.WORD,
                                padx=10,
                                pady=10,
                                height=8)  # Установлена высота
        self.text_note.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для заметки
        scrollbar = ttk.Scrollbar(note_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_note.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_note.yview)

        # Кнопка сохранения (теперь видимая и с правильными цветами)
        button_frame = ttk.Frame(form_card)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = tk.Button(button_frame, 
                              text="💾 Сохранить запись", 
                              command=self.save_entry,
                              bg=self.button_color,
                              fg=self.text_dark,  # Темный текст для контраста
                              activebackground=self.accent_color,
                              activeforeground=self.text_dark,
                              font=self.text_font,
                              relief='flat',
                              padx=10,
                              pady=5)
        save_button.pack(fill=tk.X, ipady=5)

    def create_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📜 История")

        # Основной контейнер
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Таблица с записями
        columns = ("date", "mood", "symptoms", "note")
        self.history_tree = ttk.Treeview(container, 
                                       columns=columns, 
                                       show="headings", 
                                       height=15,
                                       selectmode='browse')
        
        # Настройка колонок
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("mood", text="Настроение")
        self.history_tree.heading("symptoms", text="Симптомы")
        self.history_tree.heading("note", text="Заметка")
        
        self.history_tree.column("date", width=150, anchor='center')
        self.history_tree.column("mood", width=120, anchor='center')
        self.history_tree.column("symptoms", width=180)
        self.history_tree.column("note", width=400)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        # Скроллбар
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_tree.yview)

        # Кнопка удаления (с правильными цветами)
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=10)
        
        delete_button = tk.Button(button_frame, 
                                text="🗑️ Удалить выбранное", 
                                command=self.delete_entry,
                                bg=self.button_color,
                                fg=self.text_dark,
                                activebackground=self.accent_color,
                                activeforeground=self.text_dark,
                                font=self.text_font,
                                relief='flat',
                                padx=10,
                                pady=5)
        delete_button.pack(fill=tk.X, ipady=5)

    def create_analytics_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Аналитика")

        # Основной контейнер
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # График настроения
        mood_frame = ttk.Frame(container)
        mood_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(mood_frame, 
                 text="Распределение настроения", 
                 font=self.subtitle_font).pack(anchor='w')
        
        self.figure_mood = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_mood = self.figure_mood.add_subplot(111)
        self.canvas_mood = FigureCanvasTkAgg(self.figure_mood, mood_frame)
        self.canvas_mood.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # График симптомов
        symptoms_frame = ttk.Frame(container)
        symptoms_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(symptoms_frame, 
                 text="Динамика эмоционального состояния", 
                 font=self.subtitle_font).pack(anchor='w')
        
        self.figure_symptoms = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_symptoms = self.figure_symptoms.add_subplot(111)
        self.canvas_symptoms = FigureCanvasTkAgg(self.figure_symptoms, symptoms_frame)
        self.canvas_symptoms.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления (с правильными цветами)
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=10)
        
        update_button = tk.Button(button_frame, 
                                text="🔄 Обновить аналитику", 
                                command=self.update_analytics,
                                bg=self.button_color,
                                fg=self.text_dark,
                                activebackground=self.accent_color,
                                activeforeground=self.text_dark,
                                font=self.text_font,
                                relief='flat',
                                padx=10,
                                pady=5)
        update_button.pack(fill=tk.X, ipady=5)

    def create_emergency_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🆘 Экстренная помощь")

        # Основной контейнер с прокруткой
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=self.bg_color)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заголовок
        header = tk.Label(scrollable_frame, 
                        text="Экстренная помощь", 
                        font=self.title_font,
                        bg=self.bg_color,
                        fg=self.button_color)
        header.pack(fill=tk.X, pady=10)

        # Дыхательные упражнения
        breathing_frame = ttk.LabelFrame(scrollable_frame, 
                                       text="Дыхательные упражнения для снятия стресса",
                                       padding=20,
                                       style='TFrame')
        breathing_frame.pack(fill=tk.X, pady=15, padx=10)
        
        exercises = [
            "1. Медленное дыхание: вдох на 4 счета, задержка на 4, выдох на 6",
            "2. Квадратное дыхание: вдох 4, задержка 4, выдох 4, пауза 4",
            "3. Диафрагмальное дыхание: глубокие вдохи животом",
            "4. Дыхание 4-7-8: вдох через нос на 4 счета, задержка на 7, выдох через рот на 8",
            "5. Попеременное дыхание: зажмите правую ноздрю, вдохните левой, зажмите левую, выдохните правой"
        ]
        
        for ex in exercises:
            lbl = tk.Label(breathing_frame, 
                    text=ex, 
                    font=self.text_font,
                    bg=self.bg_color,
                    fg=self.text_dark,
                    anchor='w',
                    justify=tk.LEFT)
            lbl.pack(fill=tk.X, pady=5)

        # Техники заземления
        grounding_frame = ttk.LabelFrame(scrollable_frame, 
                                       text="Техники заземления",
                                       padding=20)
        grounding_frame.pack(fill=tk.X, pady=15, padx=10)
        
        techniques = [
            "1. Техника 5-4-3-2-1: назовите 5 вещей, которые видите, 4 которые можете потрогать, "
            "3 которые слышите, 2 которые чувствуете на запах, 1 которую можете попробовать на вкус",
            
            "2. Физическое заземление: сожмите кулаки, потопайте ногами, "
            "почувствуйте контакт тела с поверхностью",
            
            "3. Ментальное заземление: опишите детально окружающую обстановку, "
            "назовите предметы вокруг вас по порядку"
        ]
        
        for tech in techniques:
            lbl = tk.Label(grounding_frame, 
                    text=tech, 
                    font=self.text_font,
                    bg=self.bg_color,
                    fg=self.text_dark,
                    anchor='w',
                    justify=tk.LEFT,
                    wraplength=800)
            lbl.pack(fill=tk.X, pady=5)

        # Контакты экстренной помощи
        contacts_frame = ttk.LabelFrame(scrollable_frame, 
                                      text="Экстренные контакты",
                                      padding=20)
        contacts_frame.pack(fill=tk.X, pady=15, padx=10)
        
        contacts = [
            ("Общероссийский телефон доверия", "8-800-333-44-34 (круглосуточно)"),
            ("Единый экстренный канал помощи", "112 (с мобильного)"),
            ("Московская служба психологической помощи", "8-495-989-50-50"),
            ("Санкт-Петербургский кризисный центр", "8-812-708-40-41"),
            ("Горячая линия для подростков", "8-800-2000-122")
        ]
        
        for name, number in contacts:
            contact_frame = ttk.Frame(contacts_frame)
            contact_frame.pack(fill=tk.X, pady=8)
            
            name_label = tk.Label(contact_frame, 
                    text=f"{name}:", 
                    font=self.text_font,
                    bg=self.bg_color,
                    fg=self.text_dark,
                    anchor='w')
            name_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            number_label = tk.Label(contact_frame, 
                    text=number, 
                    font=Font(family="Arial", size=12, weight="bold"),
                    bg=self.bg_color,
                    fg=self.button_color,
                    anchor='w')
            number_label.pack(side=tk.LEFT, padx=5)
            
            call_button = tk.Button(contact_frame, 
                                  text="📞 Позвонить", 
                                  command=lambda n=number: self.call_number(n),
                                  bg=self.button_color,
                                  fg=self.text_dark,
                                  activebackground=self.accent_color,
                                  activeforeground=self.text_dark,
                                  font=self.text_font,
                                  relief='flat',
                                  padx=10)
            call_button.pack(side=tk.RIGHT, padx=5)

        # Ресурсы
        resources_frame = ttk.LabelFrame(scrollable_frame, 
                                       text="Полезные ресурсы",
                                       padding=20)
        resources_frame.pack(fill=tk.X, pady=15, padx=10)
        
        resources = [
            ("PsyJournals", "https://psyjournals.ru/ - Публикации по психологии"),
            ("Понимающая психотерапия", "https://psychotherapy.ru/ - Информация о терапии"),
            ("B17.ru", "https://www.b17.ru/ - Сообщество психологов"),
            ("Ясное утро", "https://www.clear-morning.ru/ - Помощь в кризисных ситуациях")
        ]
        
        for name, url in resources:
            resource_frame = ttk.Frame(resources_frame)
            resource_frame.pack(fill=tk.X, pady=5)
            
            name_label = tk.Label(resource_frame, 
                    text=f"• {name}:", 
                    font=self.text_font,
                    bg=self.bg_color,
                    fg=self.text_dark,
                    anchor='w')
            name_label.pack(side=tk.LEFT, padx=5)
            
            url_label = tk.Label(resource_frame, 
                    text=url, 
                    font=Font(family="Arial", size=11, underline=True),
                    bg=self.bg_color,
                    fg="#1a0dab",
                    anchor='w',
                    cursor="hand2")
            url_label.pack(side=tk.LEFT, padx=5)
            url_label.bind("<Button-1>", lambda e, u=url: self.open_url(u))

    def save_entry(self):
        date = self.entry_date.get()
        mood = self.mood_var.get()
        symptoms = self.entry_symptoms.get()
        note = self.text_note.get("1.0", tk.END).strip()
        
        if not mood:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите настроение")
            return
        
        # Анализ настроения из текста
        sentiment = self.sia.polarity_scores(note)
        sentiment_score = sentiment['compound']
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO entries (date, mood, note, symptoms, sentiment_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, mood, note, symptoms, sentiment_score))
            self.conn.commit()
            
            messagebox.showinfo("Успех", "Запись успешно сохранена")
            self.clear_entry_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {str(e)}")

    def clear_entry_fields(self):
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.mood_var.set("")
        self.entry_symptoms.delete(0, tk.END)
        self.text_note.delete("1.0", tk.END)

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT date, mood, symptoms, note FROM entries ORDER BY date DESC")
        rows = cursor.fetchall()
        
        # Очистка дерева
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Заполнение данными
        for row in rows:
            self.history_tree.insert("", tk.END, values=row)

    def delete_entry(self):
        selected_item = self.history_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для удаления")
            return
        
        date = self.history_tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить запись от {date}?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM entries WHERE date = ?", (date,))
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить запись: {str(e)}")

    def update_analytics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT date, mood, sentiment_score, symptoms FROM entries ORDER BY date")
        data = cursor.fetchall()
        
        if not data:
            messagebox.showinfo("Информация", "Нет данных для анализа")
            return
        
        # Подготовка данных
        df = pd.DataFrame(data, columns=['date', 'mood', 'sentiment', 'symptoms'])
        df['date'] = pd.to_datetime(df['date'])
        
        # График настроения
        self.ax_mood.clear()
        mood_counts = df['mood'].value_counts()
        mood_counts.plot(kind='bar', ax=self.ax_mood, color=self.button_color, edgecolor='black')
        self.ax_mood.set_title('Распределение настроения', fontsize=14, fontweight='bold')
        self.ax_mood.set_xlabel('Настроение', fontsize=12)
        self.ax_mood.set_ylabel('Количество записей', fontsize=12)
        self.figure_mood.tight_layout()
        self.canvas_mood.draw()
        
        # График динамики настроения
        self.ax_symptoms.clear()
        df['sentiment'].plot(ax=self.ax_symptoms, color=self.button_color, linewidth=2)
        self.ax_symptoms.set_title('Динамика эмоционального состояния', fontsize=14, fontweight='bold')
        self.ax_symptoms.set_xlabel('Дата', fontsize=12)
        self.ax_symptoms.set_ylabel('Оценка настроения (-1 до 1)', fontsize=12)
        self.figure_symptoms.tight_layout()
        self.canvas_symptoms.draw()

    def call_number(self, number):
        messagebox.showinfo("Звонок", f"Имитация звонка на номер {number}")

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PsihozApp(root)
    app.run()