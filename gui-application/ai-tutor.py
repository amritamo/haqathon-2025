import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, Toplevel, ttk
import os
import json
import fitz  # PyMuPDF
import docx
import requests
import traceback
from database_ops import *
import re


class AiTutorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db_conn = get_connection_to_db()
        init_database_tables(self.db_conn)
        # for now -- change this later \
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.show_landing_page()

    def __del__(self):
        close_connection(self.db_conn)

    def get_chapters(self):
        chapters = get_all_chapters(self.db_conn)
        return [{"id": str(ch[0]), "name": ch[1], "progress": ch[2]} for ch in chapters]

    def show_landing_page(self):
        # Clear previous widgets from the main container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Title label
        tk.Label(self.container, text="Your Chapters", font=("Arial", 18)).pack(pady=10)

        # Frame for chapter tiles
        chapters_frame = tk.Frame(self.container)
        chapters_frame.pack(fill="both", expand=True, padx=20, pady=10)

        chapters = self.get_chapters()
        # self.progress = {"1": 50, "2": 60, "3": 70}
        # Display chapters as tiles in a grid
        columns = 3  # Number of columns in the grid
        for idx, chapter in enumerate(chapters):
            tile_text = f"{chapter['name']}\nProgress: {chapter['progress']}%"
            tile = tk.Button(
                chapters_frame,
                text=tile_text,
                width=25,
                height=5,
                command=lambda c=chapter: self.show_chapter_view(chapter['id'])
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
        
        tk.Button(
            self.container,
            text="Show Confidence",
            command=self.show_confidence,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white"
        ).pack(pady=15)

    def show_confidence(self):
        win = Toplevel(self)
        win.title("Confidence Meter")
        win.geometry("400x300")
        win.resizable(False, False)

        # --- Section Scores (replace with real data if needed) ---
        chapter_scores = {
            "Section 1": 60,
            "Section 2": 60,
            "Section 3": 100
        }

        # --- Calculate Average for Overall Confidence ---
        confidence_score = int(sum(chapter_scores.values()) / len(chapter_scores))

        # --- Overall Confidence Section ---
        tk.Label(win, text="Overall", font=("Arial", 13)).pack(pady=10)

        overall_frame = tk.Frame(win)
        overall_frame.pack(pady=5)

        progress = ttk.Progressbar(overall_frame, orient="horizontal", length=300, mode="determinate")
        progress['value'] = confidence_score
        progress.pack()

        tk.Label(win, text=f"{confidence_score}%", font=("Arial", 11)).pack(pady=5)

        tk.Label(win, text="Per Chapter", font=("Arial", 13)).pack(pady=(20, 10))

        for title, score in chapter_scores.items():
            frame = tk.Frame(win)
            frame.pack(fill="x", padx=30, pady=5)

            tk.Label(frame, text=title, width=12, anchor="w").pack(side="left")
            bar = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
            bar['value'] = score
            bar.pack(side="left", padx=5)
            tk.Label(frame, text=f"{score}%", width=5).pack(side="left")

    def show_chapter_view(self, chapter):
        self.current_chapter = chapter

        # Clear previous widgets from the main container
        for widget in self.container.winfo_children():
            widget.destroy()

        # --- Load sections for this chapter from the database ---
        # Example:
        # self.sections = db_load_sections(chapter['id'])
        # --------------------------------------------------------
        # For now, use placeholder if elf.sections is empty
        # print("here")
        sections = get_sections_by_chapter(self.db_conn, chapter)
        # if not hasattr(self, 'sections') or not self.sections:
        #     self.sections = [
        #         {'title': 'Section 1', 'content': 'Cricket is a bat-and-ball game that is played between two teams of eleven players on a field, at the centre of which is a 22-yard (20-metre; 66-foot) pitch with a wicket at each end, each comprising two bails (small sticks) balanced on three stumps. Two players from the batting team, the striker and nonstriker, stand in front of either wicket holding bats, while one player from the fielding team, the bowler, bowls the ball toward the striker\'s wicket from the opposite end of the pitch. The striker\'s goal is to hit the bowled ball with the bat and then switch places with the nonstriker, with the batting team scoring one run for each of these swaps. Runs are also scored when the ball reaches the boundary of the field or when the ball is bowled illegally.'},
        #         {'title': 'Section 2', 'content': 'Content for section 2.'},
        #         {'title': 'Section 3', 'content': 'Content for section 3.'},
        #     ]
        self.sections = [
                {
                    'title': f"Section {item[0]}",
                    'content': item[1]
                }
                for item in sections
            ]
        # print("HEREHERHERHEHREHHREH")

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
        main_panel = tk.Frame(self.container)
        main_panel.pack(side="right", fill="both", expand=True)
        self.content_frame = tk.Frame(main_panel)
        self.content_frame.pack(fill="both", expand=True)
        btn_frame = tk.Frame(main_panel)
        btn_frame.pack(fill="x", side="bottom", pady=10)

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

        # Bottom button frame
        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(side="bottom", fill="x", pady=10)

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


        def send_query():
            user_query = entry.get().strip()
            if not user_query:
                return

            chat_log.config(state="normal")
            chat_log.insert("end", f"You: {user_query}\n")
            chat_log.config(state="disabled")
            chat_log.see("end")
            entry.delete(0, "end")

            try:
                import requests
                import json
                import traceback

                payload = {
                "model": "qnn-deepseek-r1-distill-qwen-1.5b",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI tutor. Respond with brief, structured, and beginner-friendly explanations. Avoid internal thoughts, planning steps, or filler language. Use bullet points or short paragraphs. Focus only on the essential concepts. Keep responses under 150 words unless asked to elaborate."
                    },

                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 10,
                "max_tokens": 400,
                "stream": False
            }


                response = requests.post(
                    "http://127.0.0.1:5272/v1/chat/completions", # change this based on your ONNX runtime server's endpoint
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=400
                )
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"].strip()

            except Exception as e:
                reply = f"Error: {str(e)}\n{traceback.format_exc()}"
            # print("here")
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
        
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

            elif file_path.endswith('.pdf'):
                text = ""
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text += page.get_text()

            else:
                messagebox.showerror("Unsupported File", "Please select a .txt or .pdf file.")
                return

        except Exception as e:
            messagebox.showerror("Error", str(e))

        # Prompt for chapter name and confidence score
        score_win = tk.Toplevel(self)
        score_win.title("Chapter Info")
        score_win.geometry("350x200")
        score_win.grab_set()

        # Chapter name input
        tk.Label(score_win, text="Enter chapter name:", font=("Arial", 11)).pack(pady=(10, 5))
        name_entry = tk.Entry(score_win, font=("Arial", 11))
        name_entry.pack(pady=5)

        # Confidence score input
        tk.Label(score_win, text="Enter confidence score (0-100):", font=("Arial", 11)).pack(pady=5)
        score_entry = tk.Entry(score_win, font=("Arial", 11))
        score_entry.pack(pady=5)

        #break text into sections
        try:
                import requests
                import json
                import traceback

                payload = {
                    "model": "qnn-deepseek-r1-distill-qwen-1.5b",
                    "messages": [
                        {
                        "role": "system",
                        "content": "You are an AI that restructures raw text into a structured JSON format. Infer logical section headings and divide the text accordingly. Return a JSON list, where each item has a 'heading' and 'content'. The content should be a short paragraph or a list of bullet points. Do not include explanations or extra commentary. Respond only with valid JSON."
                        },
                        {
                        "role": "user",
                        "content": text
                        }
                    ],
                    "max_tokens": 4000
                }

                response = requests.post(
                    "http://127.0.0.1:5272/v1/chat/completions", # change this based on your ONNX runtime server's endpoint
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=400
                )
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"].strip()

        except Exception as e:
            reply = f"Error: {str(e)}\n{traceback.format_exc()}"
        # print(reply)

        def extract_first_array(text):
            match = re.search(r'\[[^\[\]]*?\]', text)
            if match:
                return match.group()
            return None
        try:
            data = json.loads(extract_first_array(reply))
        except (e):
            print(e)
            return
        print(data)
        def submit_score():
            chapter_name = name_entry.get().strip()
            if not chapter_name:
                messagebox.showerror("Missing Input", "Please enter a chapter name.")
                return

            try:
                score = int(score_entry.get())
                if not (0 <= score <= 100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a number between 0 and 100.")
                return

            score_win.destroy()

            chapter_id = insert_chapter(self.db_conn, chapter_name, score)
            for idx, section in enumerate(data):
                print(section)
                insert_section(self.db_conn, chapter_id, idx+1, section["content"], 0)
            # this must also trigger section processing

            # ---------------------------------------------------------------

            # --- Use LLM to break chapter into sections and store in DB ---
            # sections = llm_split_chapter_into_sections(file_path)
            # db_insert_sections(chapter_id, sections)
            # ------------------------------------------------------------

            # Refresh landing page to show new chapter
            self.show_landing_page()

        tk.Button(score_win, text="Submit", command=submit_score, font=("Arial", 11)).pack(pady=10)

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

        text_widget = tk.Text(
            self.content_frame,
            wrap="word",
            height=18,
            font=("Arial", 12)
        )
        text_widget.insert("1.0", section['content'])
        text_widget.pack(fill="both", expand=True, padx=10, pady=5)

        popup_menu = tk.Menu(self, tearoff=0)
        popup_menu.add_command(label="Ask AI Tutor", command=lambda: self.ask_ai_about_selection(text_widget))

        def show_popup(event):
            popup_menu.tk_popup(event.x_root, event.y_root)

        text_widget.bind("<Button-3>", show_popup)  # Right-click on Windows/Linux

    def remove_think_blocks(text):
        # Remove everything between <think>...</think> including tags
        print(text)
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)



    def ask_ai_about_selection(self, text_widget):
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please select some text to ask about.")
            return

        if not selected_text:
            return

        try:
            payload = {
                "model": "qnn-deepseek-r1-distill-qwen-1.5b",
                "messages": [{"role": "user", "content": selected_text}],
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 10,
                "max_tokens": 10000,
                "stream": False
            }

            response = requests.post(
                "http://127.0.0.1:5272/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=400
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"].strip()
            
            messagebox.showinfo("AI Tutor Response", self.remove_think_blocks(reply))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get response:\n{str(e)}")


if __name__ == "__main__":
    app = AiTutorApp()
    app.mainloop()
