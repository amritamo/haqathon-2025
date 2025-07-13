import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import os
import json
import fitz  # PyMuPDF
import docx


class AiTutorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.show_landing_page()

    def show_landing_page(self):
        # Clear previous widgets from the main container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Title label
        tk.Label(self.container, text="Your Chapters", font=("Arial", 18)).pack(pady=10)

        # Frame for chapter tiles
        chapters_frame = tk.Frame(self.container)
        chapters_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Load chapters and progress from the database here ---
        # Example:
        # self.chapters = db_load_chapters()
        # self.progress = db_load_progress()
        # --------------------------------------------------------

        self.chapters = [{"id": "1", "name": "ch1"}, {"id": "2", "name": "ch2"}, {"id": "3", "name": "ch3"}]
        self.progress = {"1": 50, "2": 60, "3": 70}
        # Display chapters as tiles in a grid
        columns = 3  # Number of columns in the grid
        for idx, chapter in enumerate(self.chapters):
            progress = self.progress.get(chapter['id'], 0)
            tile_text = f"{chapter['name']}\nProgress: {progress}%"
            tile = tk.Button(
                chapters_frame,
                text=tile_text,
                width=25,
                height=5,
                command=lambda c=chapter: self.show_chapter_view(c)
            )
            row, col = divmod(idx, columns)
            tile.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Make the grid cells expand evenly
        for col in range(columns):
            chapters_frame.grid_columnconfigure(col, weight=1)

        # Upload button
        tk.Button(
            self.container,
            text="Upload New Chapter",
            command=self.upload_chapter,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white"
        ).pack(pady=15)

    def show_chapter_view(self, chapter):
        self.current_chapter = chapter

        # Clear previous widgets from the main container
        for widget in self.container.winfo_children():
            widget.destroy()

        # --- Load sections for this chapter from the database ---
        # Example:
        # self.sections = db_load_sections(chapter['id'])
        # --------------------------------------------------------
        # For now, use placeholder if self.sections is empty
        if not hasattr(self, 'sections') or not self.sections:
            self.sections = [
                {'title': 'Section 1', 'content': 'Content for section 1.'},
                {'title': 'Section 2', 'content': 'Content for section 2.'},
                {'title': 'Section 3', 'content': 'Content for section 3.'},
            ]

        # Sidebar for section navigation
        sidebar = tk.Frame(self.container, width=200, bg="#f0f0f0")
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Sections", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        section_listbox = tk.Listbox(sidebar, font=("Arial", 11))
        for idx, section in enumerate(self.sections):
            section_listbox.insert(idx, section['title'])
        section_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        def on_section_select(event):
            sel = section_listbox.curselection()
            if sel:
                self.display_section_content(sel[0])
        section_listbox.bind("<<ListboxSelect>>", on_section_select)

        # Main content area
        content_frame = tk.Frame(self.container)
        content_frame.pack(side="right", fill="both", expand=True)
        self.content_frame = content_frame

        # Determine which section to display (first unread or resume progress)
        # section_idx = db_get_next_section_idx(chapter['id'])
        section_idx = 0  # Placeholder for first section

        self.display_section_content(section_idx)

        # Bottom button frame
        btn_frame = tk.Frame(content_frame)
        btn_frame.pack(side="bottom", fill="x", pady=10)

        tk.Button(
            btn_frame,
            text="Take Quiz",
            command=self.show_quiz,
            font=("Arial", 11),
            bg="#1976D2",
            fg="white"
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="Ask AI Tutor",
            command=self.show_conversation,
            font=("Arial", 11),
            bg="#388E3C",
            fg="white"
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="Back to Chapters",
            command=self.show_landing_page,
            font=("Arial", 11)
        ).pack(side="right", padx=10)


    def show_quiz(self):
        # Clear the main container
        for widget in self.container.winfo_children():
            widget.destroy()

        # --- Load quiz questions for the current chapter from the database ---
        # Example:
        # self.quiz_questions = db_load_quiz_questions(self.current_chapter['id'])
        # --------------------------------------------------------
        # Placeholder questions for demonstration
        self.quiz_questions = [
            {"question": "What is Python?", "choices": ["A snake", "A programming language", "A car", "A fruit"], "correct": 1},
            {"question": "Which library is used for GUIs in Python?", "choices": ["NumPy", "Tkinter", "Pandas", "Requests"], "correct": 1},
            {"question": "What does AI stand for?", "choices": ["Artificial Intelligence", "Automatic Input", "Apple Inc.", "Analog Interface"], "correct": 0}
        ]

        self.quiz_idx = 0
        self.quiz_answers = []

        # Helper function to display each question
        def display_question():
            # Clear previous question widgets
            for widget in self.container.winfo_children():
                widget.destroy()

            if self.quiz_idx >= len(self.quiz_questions):
                finish_quiz()
                return

            q = self.quiz_questions[self.quiz_idx]
            tk.Label(self.container, text=f"Question {self.quiz_idx + 1} of {len(self.quiz_questions)}", font=("Arial", 14)).pack(pady=10)
            tk.Label(self.container, text=q['question'], font=("Arial", 12)).pack(pady=10)

            var = tk.IntVar(value=-1)
            for idx, choice in enumerate(q['choices']):
                tk.Radiobutton(self.container, text=choice, variable=var, value=idx, font=("Arial", 11)).pack(anchor="w", padx=30)

            def next_question():
                if var.get() == -1:
                    tk.messagebox.showwarning("No Answer", "Please select an answer before continuing.")
                    return
                self.quiz_answers.append(var.get())
                self.quiz_idx += 1
                display_question()

            tk.Button(self.container, text="Next", command=next_question, font=("Arial", 11)).pack(pady=15)
            tk.Button(self.container, text="Cancel Quiz", command=lambda: self.show_chapter_view(self.current_chapter), font=("Arial", 10)).pack(pady=2)

        # Helper function to finish the quiz
        def finish_quiz():
            # Calculate score
            correct = 0
            for idx, q in enumerate(self.quiz_questions):
                if idx < len(self.quiz_answers) and self.quiz_answers[idx] == q['correct']:
                    correct += 1
            total = len(self.quiz_questions)
            score_percent = int((correct / total) * 100)

            # --- Update confidence score in the database here ---
            # db_update_confidence(self.current_chapter['id'], score_percent)
            # Optionally, record quiz results in the DB as well
            # ---------------------------------------------------

            # Show result
            for widget in self.container.winfo_children():
                widget.destroy()
            tk.Label(self.container, text="Quiz Complete!", font=("Arial", 16)).pack(pady=15)
            tk.Label(self.container, text=f"You scored {score_percent}% ({correct} out of {total})", font=("Arial", 13)).pack(pady=10)
            tk.Button(self.container, text="Back to Chapter", command=lambda: self.show_chapter_view(self.current_chapter), font=("Arial", 11)).pack(pady=20)

        # Start the quiz
        display_question()


    def show_conversation(self):
        # Clear previous widgets from the main container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Title label
        tk.Label(self.container, text="AI Tutor Conversation", font=("Arial", 16)).pack(pady=10)

        # Frame for chat log and input
        chat_frame = tk.Frame(self.container)
        chat_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Chat log (read-only text widget)
        chat_log = tk.Text(chat_frame, state="disabled", height=15, wrap="word")
        chat_log.pack(fill="both", expand=True, padx=5, pady=5)

        # Entry for user input
        entry = tk.Entry(chat_frame, font=("Arial", 11))
        entry.pack(fill="x", padx=5, pady=5)

        import requests
        import traceback

        def send_query():
            user_query = entry.get().strip()
            if not user_query:
                return

            # Display user message
            chat_log.config(state="normal")
            chat_log.insert("end", f"You: {user_query}\n")
            chat_log.config(state="disabled")
            chat_log.see("end")
            entry.delete(0, "end")

            try:
                response = requests.post(
                    "http://localhost:5000/generate",
                    json={"prompt": user_query},
                    timeout=400  # prevent hanging
                )
                response.raise_for_status()
                reply = response.json().get("reply", "").strip()

                # Optional: truncate if too long
                if len(reply) > 1000:
                    reply = reply[:1000] + "..."

            except Exception as e:
                reply = f"Error: {str(e)}\n{traceback.format_exc()}"

            # Display AI response
            chat_log.config(state="normal")
            chat_log.insert("end", f"AI Tutor: {reply}\n")
            chat_log.config(state="disabled")
            chat_log.see("end")


        # Send button
        tk.Button(chat_frame, text="Send", command=send_query, font=("Arial", 11)).pack(pady=5)

        # Back button to return to chapter view
        tk.Button(
            self.container,
            text="Back to Chapter",
            command=lambda: self.show_chapter_view(self.current_chapter),
            font=("Arial", 11)
        ).pack(pady=10)

    def upload_chapter(self):
        # Open file dialog for .txt or .pdf files
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")]
        )
        if not file_path:
            return  # User cancelled

        # Prompt for confidence score in a modal dialog
        score_win = tk.Toplevel(self)
        score_win.title("Confidence Score")
        score_win.geometry("300x120")
        score_win.grab_set()  # Make modal

        tk.Label(score_win, text="Enter confidence score (0-100):", font=("Arial", 11)).pack(pady=8)
        score_entry = tk.Entry(score_win, font=("Arial", 11))
        score_entry.pack(pady=5)

        def submit_score():
            try:
                score = int(score_entry.get())
                if not (0 <= score <= 100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a number between 0 and 100.")
                return

            score_win.destroy()

            # --- Save chapter metadata and confidence score to the database ---
            # chapter_id = db_insert_chapter(file_path, score)
            # ---------------------------------------------------------------

            # --- Use LLM to break chapter into sections and store in DB ---
            # sections = llm_split_chapter_into_sections(file_path)
            # db_insert_sections(chapter_id, sections)
            # ------------------------------------------------------------

            # --- Reload chapters from the database ---
            # self.chapters = db_load_chapters()
            # self.progress = db_load_progress()
            # ----------------------------------------

            # Refresh landing page to show new chapter
            self.show_landing_page()

        tk.Button(score_win, text="Submit", command=submit_score, font=("Arial", 11)).pack(pady=8)

    def display_section_content(self, section_idx):
        # Clear previous section content widgets in the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # --- Retrieve the section data ---
        # Example: section = self.sections[section_idx]
        # If using DB, ensure self.sections is up-to-date
        section = self.sections[section_idx]

        # Section Title
        tk.Label(
            self.content_frame,
            text=section['title'],
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))

        # Section Content
        text_widget = tk.Text(
            self.content_frame,
            wrap="word",
            height=18,
            font=("Arial", 12)
        )
        text_widget.insert("1.0", section['content'])
        text_widget.config(state="disabled")  # Make read-only
        text_widget.pack(fill="both", expand=True, padx=10, pady=5)




if __name__ == "__main__":
    app = AiTutorApp()
    app.mainloop()