import tkinter as tk
import ttkbootstrap as ttk
import threading
import tkinter.filedialog as fd
import pytesseract

from ttkbootstrap.constants import *
from core import execute_command
from voice_utils import get_voice_command
from PIL import Image, ImageTk
from config import client, GOOGLE_KG_SEARCH_API
from logo_vision import detect_logo
from web_utils import get_brand_website
from web_utils import insert_link

# === Interface ===
def run_jarvis_gui():

    window = ttk.Window(themename="darkly")
    window.title("Jarvis Assistant")
    window.geometry("1200x800")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12))

    label = ttk.Label(window, text="Your request", font=("Arial", 16))
    label.pack(pady=10)

    image_label = ttk.Label(window)
    image_label.pack(pady=5)

    output_box = tk.Text(window, font=("Consolas", 12), height=18, wrap=tk.WORD, bg="#2c2c2c", fg="white")
    output_box.pack(pady=10, padx=10, fill=BOTH, expand=True)

    def on_insert_image():
        output_box.delete(1.0, tk.END)
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        filepath = fd.askopenfilename(title="Select an image", filetypes=filetypes)
        if not filepath:
            return

        img = Image.open(filepath)
        img.thumbnail((320, 200))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk

        def worker():
            logo, score = detect_logo(filepath)
            
            def update_gui():
                if logo and score and score > 0.5:
                    output_box.insert(tk.END, f"Detected logo: {logo} (confidence: {score:.2f})\n")
                    gpt_input = f"Describe what '{logo}' is. This name was detected as a logo in the image."
                    website = get_brand_website(logo, GOOGLE_KG_SEARCH_API)
                    if website:
                        insert_link(output_box, website)
                    else:
                        output_box.insert(tk.END, "Website not found\n")
                    output_box.insert(tk.END, "Generating description via GPT...\n")

                    # Call GPT
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Provide a brief description of the website, brand, or service by its name."},
                            {"role": "user", "content": gpt_input}
                        ]
                    )
                    summary = response.choices[0].message.content.strip()
                    output_box.insert(tk.END, f"Summary:\n{summary}\n\n")
                else:
                    output_box.insert(tk.END, "Logo not detected in the image\n")
                    try:
                        text = pytesseract.image_to_string(img, lang="rus+eng")
                        output_box.insert(tk.END, f"Text in the image:\n{text}\n\n")
                        last_ocr_text["text"] = text
                        if text.strip():
                            output_box.insert(tk.END, "⏳ Analyzing the meaning of the text via GPT...\n")
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "Briefly explain what is written in the image or guess the meaning if it is unclear."},
                                    {"role": "user", "content": text}
                                ]
                            )
                            summary = response.choices[0].message.content.strip()
                            output_box.insert(tk.END, f"Summary:\n{summary}\n\n")
                    except Exception as e:
                        output_box.insert(tk.END, f"Error analyzing image: {e}\n")
                        last_ocr_text["text"] = ""

            # Updating GUI from the main thread
            window.after(0, update_gui)

        # Starting worker in a separate thread
        threading.Thread(target=worker).start()


    entry_frame = ttk.Frame(window)
    entry_frame.pack(pady=5)

    entry = ttk.Entry(entry_frame, font=("Arial", 14), width=65)
    entry.pack(side='left', fill='x', expand=True)

    insert_image_btn = ttk.Button(entry_frame, text="🖼️", command=on_insert_image, width=2)
    insert_image_btn.pack(side='left', padx=(5, 0))

    last_ocr_text = {"text": ""}

    def on_submit():
        command = entry.get()
        output_box.insert(tk.END, f"> {command}\n")
        response = execute_command(command)
        output_box.insert(tk.END, response + "\n\n")
        entry.delete(0, tk.END)

    def on_voice():
        def process_voice():
            command = get_voice_command(output_box)
            output_box.insert(tk.END, f"> (Голос): {command}\n")
            response = execute_command(command)
            output_box.insert(tk.END, response + "\n\n")
        threading.Thread(target=process_voice).start()

    frame = ttk.Frame(window)
    frame.pack(pady=5)

    submit_btn = ttk.Button(frame, text="Выполнить", command=on_submit)
    submit_btn.pack(side=LEFT, padx=10)

    voice_btn = ttk.Button(frame, text="Voice", command=on_voice)
    voice_btn.pack(side=LEFT)

    window.mainloop()