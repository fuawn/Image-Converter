import os
from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar, OptionMenu
from tkinter import font as tkFont
from PIL import Image, UnidentifiedImageError

# Display Name -> (PIL Code, Extension)
SUPPORTED_FORMATS = {
    "JPEG (.jpg)": ("JPEG", "jpg"),
    "PNG (.png)": ("PNG", "png"),
    "BMP (.bmp)": ("BMP", "bmp"),
    "GIF (.gif)": ("GIF", "gif"),
    "TIFF (.tiff)": ("TIFF", "tiff"),
    "WEBP (.webp)": ("WEBP", "webp")
}

class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("450x320")

        # Configure grid expansion
        self.root.columnconfigure(0, weight=1)
        self.bold_font = tkFont.Font(family="Arial", size=10, weight="bold")

        # Variables
        self.file_path = ""
        self.output_format_display = StringVar(value="PNG (.png)") # Default format
        self.output_folder = ""

        # --- Widget Layout ---
        current_row = 0

        # 1. Select Image Section
        Label(root, text="1. Choose Image File:", font=self.bold_font, anchor="w").grid(
            row=current_row, column=0, padx=10, pady=(10, 2), sticky="w")
        current_row += 1

        self.select_button = Button(root, text="Browse...", command=self.select_image)
        self.select_button.grid(row=current_row, column=0, padx=10, pady=2, sticky="ew")
        current_row += 1

        self.selected_file_label = Label(root, text="No image selected", fg="grey", wraplength=400, anchor="w", justify="left")
        self.selected_file_label.grid(row=current_row, column=0, padx=10, pady=(2, 10), sticky="ew")
        current_row += 1

        # 2. Choose Format Section
        Label(root, text="2. Choose Output Format:", font=self.bold_font, anchor="w").grid(
            row=current_row, column=0, padx=10, pady=(5, 2), sticky="w")
        current_row += 1

        self.format_dropdown = OptionMenu(root, self.output_format_display, *SUPPORTED_FORMATS.keys())
        self.format_dropdown.grid(row=current_row, column=0, padx=10, pady=(2, 10), sticky="ew")
        current_row += 1

        # 3. Choose Folder Section
        Label(root, text="3. Choose Output Folder:", font=self.bold_font, anchor="w").grid(
            row=current_row, column=0, padx=10, pady=(5, 2), sticky="w")
        current_row += 1

        self.folder_button = Button(root, text="Browse...", command=self.select_folder)
        self.folder_button.grid(row=current_row, column=0, padx=10, pady=2, sticky="ew")
        current_row += 1

        self.selected_folder_label = Label(root, text="No folder selected", fg="grey", wraplength=400, anchor="w", justify="left")
        self.selected_folder_label.grid(row=current_row, column=0, padx=10, pady=(2, 15), sticky="ew")
        current_row += 1

        # Convert Button
        self.convert_button = Button(root, text="Convert Image", command=self.convert_image, state="disabled", font=("Arial", 11, "bold"))
        self.convert_button.grid(row=current_row, column=0, padx=10, pady=5, ipady=4, sticky="ew") # ipady adds vertical padding inside the button
        current_row += 1

        # Status Label
        self.status_label = Label(root, text="", font=("Arial", 9), anchor="w")
        self.status_label.grid(row=current_row, column=0, padx=10, pady=(5, 10), sticky="ew")
        current_row += 1

    def select_image(self):
        # Prepare file type list for the dialog
        extensions = set(ext for code, ext in SUPPORTED_FORMATS.values())
        if 'jpg' in extensions: extensions.add('jpeg') 
        if 'tiff' in extensions: extensions.add('tif')
        filetypes_str = " ".join(f"*.{ext}" for ext in sorted(extensions))

        filepath = filedialog.askopenfilename(
            title="Select image file",
            filetypes=[("Image files", filetypes_str), ("All files", "*.*")]
        )
        if filepath:
            self.file_path = filepath
            # Show only filename in the label
            self.selected_file_label.config(text=os.path.basename(filepath), fg="black")
            self.status_label.config(text="")
        elif not self.file_path: # Reset only if dialog cancelled and nothing was selected before
            self.selected_file_label.config(text="No image selected", fg="grey")
        self.update_convert_button_state()

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_folder = folder
            self.selected_folder_label.config(text=folder, fg="black")
            self.status_label.config(text="") # Clear status
        elif not self.output_folder: # Reset only if dialog cancelled and nothing was selected before
             self.selected_folder_label.config(text="No folder selected", fg="grey")
        self.update_convert_button_state()

    def update_convert_button_state(self):
        """Enable Convert button only if both file and folder are selected."""
        if self.file_path and self.output_folder:
            self.convert_button.config(state="normal")
        else:
            self.convert_button.config(state="disabled")

    def convert_image(self):
        """Performs the image conversion."""
        if not self.file_path or not self.output_folder:
            messagebox.showwarning("Input Missing", "Please select an image and output folder.")
            return

        img = None
        try:
            self.status_label.config(text="Converting...", fg="blue")
            self.root.update_idletasks() # Refresh UI to show status

            img = Image.open(self.file_path)
            format_display_name = self.output_format_display.get()
            format_code, output_extension = SUPPORTED_FORMATS[format_display_name]

            if format_code in ("JPEG", "BMP") and img.mode in ("RGBA", "LA", "PA"):
                 print(f"Converting image mode from {img.mode} to RGB for {format_code}")
                 img = img.convert("RGB")

            base_filename = os.path.splitext(os.path.basename(self.file_path))[0]
            output_path = os.path.join(self.output_folder, f"{base_filename}.{output_extension}")

            img.save(output_path, format_code)

            self.status_label.config(text=f"Saved: {os.path.basename(output_path)}", fg="green")
            messagebox.showinfo("Success", f"Image converted successfully!\nSaved as: {output_path}")

        except UnidentifiedImageError:
             messagebox.showerror("Error", f"Cannot open image file.\n'{os.path.basename(self.file_path)}' might be corrupted or not a supported format.")
             self.status_label.config(text="Error: Invalid image file", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
            self.status_label.config(text=f"Error: {e}", fg="red")
        finally:
            if img:
                img.close()


if __name__ == "__main__":
    app_root = Tk()
    gui = ImageConverterGUI(app_root)
    app_root.mainloop()