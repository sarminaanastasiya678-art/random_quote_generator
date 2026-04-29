import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных цитат")
        self.root.geometry("850x650")
        self.root.configure(bg="#f5f5f5")

        # 1. Предопределённые цитаты
        self.default_quotes = [
            {"text": "Жизнь — это то, что случается с тобой, пока ты строишь другие планы.", "author": "Джон Леннон", "topic": "Жизнь"},
            {"text": "Единственный способ делать великую работу — любить то, что ты делаешь.", "author": "Стив Джобс", "topic": "Работа"},
            {"text": "Успех — это не конечный пункт, а путешествие.", "author": "Зиг Зиглар", "topic": "Успех"},
            {"text": "Не бойся идти медленно, бойся стоять на месте.", "author": "Китайская пословица", "topic": "Мудрость"},
            {"text": "Образование — самое мощное оружие, которое вы можете использовать, чтобы изменить мир.", "author": "Нельсон Мандела", "topic": "Образование"},
        ]

        self.all_quotes = list(self.default_quotes)
        self.history = []
        self.history_file = "quotes_history.json"

        self._load_history()
        self._setup_ui()
        self._update_filters()
        self._update_history_view()

        # Автосохранение при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        # --- Блок текущей цитаты ---
        current_frame = ttk.LabelFrame(self.root, text="Текущая цитата", padding=10)
        current_frame.pack(fill="x", padx=10, pady=5)

        self.quote_label = ttk.Label(current_frame, text='Нажмите «Сгенерировать» для начала...', wraplength=750, font=("Arial", 12, "italic"))
        self.quote_label.pack(fill="x")

        self.generate_btn = ttk.Button(current_frame, text="🎲 Сгенерировать цитату", command=self._generate_quote)
        self.generate_btn.pack(pady=8)

        # --- Блок добавления новой цитаты ---
        add_frame = ttk.LabelFrame(self.root, text="Добавить свою цитату", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="Текст:").grid(row=0, column=0, sticky="w", padx=5)
        self.add_text_entry = ttk.Entry(add_frame, width=60)
        self.add_text_entry.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.add_author_entry = ttk.Entry(add_frame, width=30)
        self.add_author_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky="w", padx=5)
        self.add_topic_entry = ttk.Entry(add_frame, width=30)
        self.add_topic_entry.grid(row=2, column=1, sticky="w", padx=5)

        self.add_btn = ttk.Button(add_frame, text="Добавить в базу", command=self._add_quote)
        self.add_btn.grid(row=2, column=2, padx=10, pady=5)

        # --- Блок истории и фильтров ---
        hist_frame = ttk.LabelFrame(self.root, text="История генераций", padding=10)
        hist_frame.pack(fill="both", expand=True, padx=10, pady=5)

        filter_frame = ttk.Frame(hist_frame)
        filter_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(filter_frame, text="Фильтр по автору:").pack(side="left")
        self.author_filter = ttk.Combobox(filter_frame, state="readonly", width=20)
        self.author_filter.pack(side="left", padx=5)
        self.author_filter.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        ttk.Label(filter_frame, text="Фильтр по теме:").pack(side="left", padx=(10, 0))
        self.topic_filter = ttk.Combobox(filter_frame, state="readonly", width=20)
        self.topic_filter.pack(side="left", padx=5)
        self.topic_filter.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить", command=self._reset_filters)
        self.reset_filter_btn.pack(side="left", padx=10)

        self.save_btn = ttk.Button(filter_frame, text="Сохранить историю", command=self._save_history)
        self.save_btn.pack(side="right")

        # Таблица истории
        self.tree = ttk.Treeview(hist_frame, columns=("text", "author", "topic", "time"), show="headings", height=12)
        self.tree.heading("text", text="Текст цитаты")
        self.tree.heading("author", text="Автор")
        self.tree.heading("topic", text="Тема")
        self.tree.heading("time", text="Время генерации")

        self.tree.column("text", width=380)
        self.tree.column("author", width=120)
        self.tree.column("topic", width=90)
        self.tree.column("time", width=130)

        scroll = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # --- Логика ---
    def _generate_quote(self):
        if not self.all_quotes:
            messagebox.showwarning("Пусто", "Список цитат пуст. Добавьте хотя бы одну.")
            return

        selected = random.choice(self.all_quotes)
        self.quote_label.config(text=f"«{selected['text']}»\n— {selected['author']}")

        record = {
            "text": selected["text"],
            "author": selected["author"],
            "topic": selected["topic"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(record)
        self._update_history_view()
        self._update_filters()

    def _add_quote(self):
        text = self.add_text_entry.get().strip()
        author = self.add_author_entry.get().strip()
        topic = self.add_topic_entry.get().strip()

        # 6. Проверка корректности ввода
        if not text or not author or not topic:
            messagebox.showerror("Ошибка ввода", "Все поля (текст, автор, тема) должны быть заполнены!")
            return

        new_quote = {"text": text, "author": author, "topic": topic}
        self.all_quotes.append(new_quote)

        self.add_text_entry.delete(0, tk.END)
        self.add_author_entry.delete(0, tk.END)
        self.add_topic_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Цитата успешно добавлена!")
        self._update_filters()

    def _update_history_view(self, filtered_history=None):
        for i in self.tree.get_children():
            self.tree.delete(i)

        data = filtered_history if filtered_history is not None else self.history
        for item in reversed(data):  # Новые сверху
            self.tree.insert("", "end", values=(item["text"], item["author"], item["topic"], item["time"]))

    def _apply_filters(self):
        author = self.author_filter.get()
        topic = self.topic_filter.get()

        filtered = self.history
        if author and author != "Все":
            filtered = [q for q in filtered if q["author"] == author]
        if topic and topic != "Все":
            filtered = [q for q in filtered if q["topic"] == topic]

        self._update_history_view(filtered)

    def _reset_filters(self):
        self.author_filter.current(0)
        self.topic_filter.current(0)
        self._update_history_view()

    def _update_filters(self):
        # Собираем уникальных авторов и темы из всей базы
        all_authors = sorted(set(q["author"] for q in self.all_quotes + self.history))
        all_topics = sorted(set(q["topic"] for q in self.all_quotes + self.history))

        self.author_filter["values"] = ["Все"] + all_authors
        self.topic_filter["values"] = ["Все"] + all_topics
        if self.author_filter.current() == -1: self.author_filter.current(0)
        if self.topic_filter.current() == -1: self.topic_filter.current(0)

    # 5. Сохранение и загрузка JSON
    def _save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранено", f"История сохранена в {self.history_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Файл истории повреждён: {e}")
                self.history = []

    def _on_close(self):
        self._save_history()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()
