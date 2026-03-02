import tkinter as tk
import numpy as np
from tkinter import filedialog, messagebox, colorchooser, Toplevel, simpledialog, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
import math
import cv2
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')

class ModernCollageMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Collage Maker ")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        self.setup_styles()
        
        # Initialize variables
        self.images = []
        self.image_tk_objects = []
        self.selected_image_item = None
        self.selected_image_index = None
        self.image_items = []
        self.image_objects = []
        self.text_items = []
        
        self.bg_color = "#2c3e50"
        self.bg_image = None
        self.paint_color = "#3498db"
        self.painting = False
        self.erasing = False
        self.strokes = []
        self.temp_strokes = []
        self.cropping = False
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect = None
        
        # Create UI
        self.create_sidebar()
        self.create_main_content()
        self.create_canvas()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Sidebar.TFrame', background='#2c3e50')
        style.configure('Modern.TFrame', background='#34495e')
        
        style.configure('Primary.TButton', background='#3498db', foreground='white',
                       borderwidth=0, font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton', 
                 background=[('active', '#2980b9'), ('pressed', '#21618c')])
        
        style.configure('Secondary.TButton', background='#95a5a6', foreground='white',
                       borderwidth=0, font=('Segoe UI', 9))
        style.map('Secondary.TButton',
                 background=[('active', '#7f8c8d'), ('pressed', '#616a6b')])

    def create_sidebar(self):
        self.sidebar = ttk.Frame(self.root, style='Sidebar.TFrame', width=300)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.sidebar.pack_propagate(False)
        
        # Header
        header_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        header_frame.pack(fill=tk.X, padx=15, pady=20)
        
        app_title = tk.Label(header_frame, text=" Image Collage Maker ", 
                           font=('Segoe UI', 16, 'bold'), 
                           bg='#2c3e50', fg='#ecf0f1')
        app_title.pack(anchor='w')
        
        # Create scrollable sidebar
        self.create_sidebar_content()

    def create_sidebar_content(self):
        canvas = tk.Canvas(self.sidebar, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sidebar, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Sidebar.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_control_sections(scrollable_frame)

    def create_control_sections(self, parent):
        sections = [
            ("IMAGE OPERATIONS", [
                ("Upload Images", self.upload_images, "Primary.TButton"),
                ("Crop Selected", self.start_crop, "Secondary.TButton"),
                ("Apply Crop", self.apply_crop, "Secondary.TButton"),
                ("Cancel Crop", self.cancel_crop, "Secondary.TButton")
            ]),
            
            ("TRANSFORM", [
                ("Rotate Image", self.rotate_image, "Secondary.TButton"),
                ("Resize Image", self.resize_image, "Secondary.TButton")
            ]),
            
            ("BACKGROUND", [
                ("Background Color", self.select_bg_color, "Secondary.TButton"),
                ("Background Image", self.upload_bg_image, "Secondary.TButton")
            ]),
            
            ("FILTERS & EFFECTS", [
                ("Apply Filter", self.open_filter_window, "Secondary.TButton"),
                ("Remove Background", self.remove_background, "Primary.TButton")
            ]),
            
            ("PAINTING TOOLS", [
                ("Paint Color", self.select_paint_color, "Secondary.TButton"),
                ("Eraser", self.enable_eraser, "Secondary.TButton"),
                ("Apply Paint", self.apply_paint, "Secondary.TButton"),
                ("Reset Paint", self.reset_paint, "Secondary.TButton")
            ]),
            
            ("TEXT TOOLS", [
                ("Add Text", self.add_text, "Secondary.TButton"),
                ("Text Color", self.select_text_color, "Secondary.TButton"),
                ("Reset Text", self.reset_text, "Secondary.TButton")
            ]),
            
            ("FUNCTIONS", [
                ("Edge Detection", self.run_edge_detection, "Primary.TButton"),
                ("Region Analysis", self.run_region_descriptor, "Primary.TButton"),
                ("Notch Filter", self.run_notch_filter, "Primary.TButton"),
                ("Histogram Enhancement", self.run_histogram_enhancement, "Primary.TButton")  
                
            ]),
            
            ("EXPORT", [
                ("Save Collage", self.save_collage, "Primary.TButton")
            ])
        ]
        
        for section_title, buttons in sections:
            self.create_section(parent, section_title, buttons)

    def create_section(self, parent, title, buttons):
        section_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        section_frame.pack(fill=tk.X, padx=15, pady=12)
        
        title_label = tk.Label(section_frame, text=title, font=('Segoe UI', 10, 'bold'),
                              bg='#2c3e50', fg='#3498db', anchor='w')
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        for btn_text, command, style_name in buttons:
            btn = ttk.Button(section_frame, text=btn_text, command=command, 
                           style=style_name, width=20)
            btn.pack(fill=tk.X, pady=2)
        
        if "TRANSFORM" in title:
            self.create_transform_controls(section_frame)
        elif "PAINTING TOOLS" in title:
            self.create_painting_controls(section_frame)
        elif "TEXT TOOLS" in title:
            self.create_text_controls(section_frame)

    def create_transform_controls(self, parent):
        rotate_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        rotate_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(rotate_frame, text="Rotation Angle:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.rotate_angle_entry = ttk.Entry(rotate_frame, width=10)
        self.rotate_angle_entry.pack(fill=tk.X, pady=2)
        self.rotate_angle_entry.insert(0, "45")
        
        resize_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        resize_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(resize_frame, text="New Size (w,h):", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.resize_entry = ttk.Entry(resize_frame, width=10)
        self.resize_entry.pack(fill=tk.X, pady=2)
        self.resize_entry.insert(0, "300,300")

    def create_painting_controls(self, parent):
        paint_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        paint_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(paint_frame, text="Paint Thickness:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.paint_thickness = tk.Scale(paint_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                      bg='#2c3e50', fg='#ecf0f1', highlightbackground='#2c3e50')
        self.paint_thickness.set(5)
        self.paint_thickness.pack(fill=tk.X, pady=2)
        
        erase_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        erase_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(erase_frame, text="Eraser Thickness:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.erase_thickness = tk.Scale(erase_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                      bg='#2c3e50', fg='#ecf0f1', highlightbackground='#2c3e50')
        self.erase_thickness.set(10)
        self.erase_thickness.pack(fill=tk.X, pady=2)

    def create_text_controls(self, parent):
        text_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        text_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(text_frame, text="Text:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.text_entry = ttk.Entry(text_frame)
        self.text_entry.pack(fill=tk.X, pady=2)
        self.text_entry.insert(0, "Your text here")
        
        size_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        size_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(size_frame, text="Font Size:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.font_size_entry = ttk.Entry(size_frame, width=10)
        self.font_size_entry.pack(fill=tk.X, pady=2)
        self.font_size_entry.insert(0, "24")
        
        font_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        font_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(font_frame, text="Font Family:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 8)).pack(anchor='w')
        self.font_choice = tk.StringVar()
        fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Georgia"]
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_choice, values=fonts,
                                 state="readonly", height=6)
        self.font_choice.set("Arial")
        font_combo.pack(fill=tk.X, pady=2)

    def create_main_content(self):
        self.main_content = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_frame = ttk.Frame(self.main_content, style='Modern.TFrame')
        self.status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.instructions = tk.Label(self.status_frame, text="Welcome to Image Collage Maker ! Start by uploading images.", 
                                   font=('Segoe UI', 10), bg='#34495e', fg='#ecf0f1',
                                   anchor='w', justify='left')
        self.instructions.pack(fill=tk.X)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.main_content, width=800, height=600, bg="#34495e", 
                               highlightthickness=0, relief='flat', cursor="cross")
        self.canvas.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.buffer = Image.new("RGBA", (800, 600), (255, 255, 255, 0))
        self.buffer_draw = ImageDraw.Draw(self.buffer)
        self.buffer_tk = ImageTk.PhotoImage(self.buffer)
        self.buffer_image_item = self.canvas.create_image(0, 0, image=self.buffer_tk, anchor=tk.NW)
        self.image_tk_objects.append(self.buffer_tk)

        self.temp_buffer = Image.new("RGBA", (800, 600), (255, 255, 255, 0))
        self.temp_buffer_draw = ImageDraw.Draw(self.temp_buffer)
        self.temp_buffer_tk = ImageTk.PhotoImage(self.temp_buffer)
        self.temp_buffer_image_item = self.canvas.create_image(0, 0, image=self.temp_buffer_tk, anchor=tk.NW)
        self.image_tk_objects.append(self.temp_buffer_tk)

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)

    def update_status(self, message):
        self.instructions.config(text=message)

    def upload_images(self):
        self.disable_paint()
        image_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if not image_paths:
            return

        new_images = []
        for path in image_paths:
            try:
                img = Image.open(path).convert("RGBA")
                new_images.append(img)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open {path}: {str(e)}")
        
        self.images.extend(new_images)
        self.display_images(new_images)
        self.update_status(f"Uploaded {len(new_images)} images. Drag to position them on canvas.")

    def display_images(self, new_images=None):
        if new_images is None:
            new_images = self.images

        for img in new_images:
            img.thumbnail((400, 400), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_tk_objects.append(img_tk)
            image_item = self.canvas.create_image(100, 100, image=img_tk, anchor=tk.NW)
            self.image_items.append(image_item)
            self.image_objects.append(img)

    def canvas_click(self, event):
        if self.painting or self.erasing:
            self.paint(event)
        else:
            self.select_image(event)
            
    def canvas_drag(self, event):
        if self.painting or self.erasing:
            self.paint(event)
        elif self.cropping:
            self.update_crop(event)
        else:
            self.drag_image(event)

    def select_image(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] in self.image_items:
            self.selected_image_item = item[0]
            self.selected_image_index = self.image_items.index(item[0])
            self.update_status(f"Image selected at position ({event.x}, {event.y})")

    def drag_image(self, event):
        if self.selected_image_item:
            self.canvas.coords(self.selected_image_item, event.x, event.y)
            self.canvas.tag_raise(self.selected_image_item)

    def disable_paint(self):
        self.painting = False
        self.erasing = False

    def start_crop(self):
        self.disable_paint()
        if not self.selected_image_item:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return
            
        self.cropping = True
        self.canvas.bind("<Button-1>", self.initiate_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)
        self.update_status("Cropping mode: Click and drag to select crop area.")

    def initiate_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y, event.x, event.y, 
            outline='#e74c3c', width=2, dash=(4, 2)
        )

    def update_crop(self, event):
        if self.cropping:
            self.canvas.coords(self.crop_rect, self.crop_start_x, self.crop_start_y, event.x, event.y)

    def end_crop(self, event):
        self.cropping = False
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.update_status("Crop area selected. Click 'Apply Crop' or 'Cancel Crop'.")

    def apply_crop(self):
        if self.selected_image_item and self.crop_rect:
            try:
                # x0, y0: Top-left corner coordinates
                # x1, y1: Bottom-right corner coordinates

                x0, y0, x1, y1 = self.canvas.coords(self.crop_rect)
                # Find image index: Locate the position of the selected image in the image_items list
                # This gives us the index to access the corresponding image in other arrays

                index = self.image_items.index(self.selected_image_item)
                
                # Get PIL Image: Retrieve the actual PIL Image object using the found index
                img = self.image_objects[index]
                
                # Get image dimensions: Get the width and height of the original image
                img_width, img_height = img.size
                
                # Get image position: Retrieve the current position of the image on the canvas
 
                canvas_coords = self.canvas.coords(self.selected_image_item)
                
                 
                crop_box = (
                    max(0, int(x0 - canvas_coords[0])),
                    max(0, int(y0 - canvas_coords[1])),
                    min(img_width, int(x1 - canvas_coords[0])),
                    min(img_height, int(y1 - canvas_coords[1]))
                )

                if crop_box[2] > crop_box[0] and crop_box[3] > crop_box[1]:
                    cropped_img = img.crop(crop_box)
                    self.image_objects[index] = cropped_img
                    img_tk = ImageTk.PhotoImage(cropped_img)
                    self.image_tk_objects[index] = img_tk
                    self.canvas.itemconfig(self.selected_image_item, image=img_tk)
                    self.update_status("Image cropped successfully!")
                else:
                    messagebox.showerror("Invalid Crop", "Crop area is too small or invalid.")

            except Exception as e:
                messagebox.showerror("Crop Error", f"Error during cropping: {str(e)}")

            self.canvas.delete(self.crop_rect)
            self.crop_rect = None

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)

    def cancel_crop(self):
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
        self.update_status("Crop cancelled.")
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)

    def rotate_image(self):
        self.disable_paint()
        if not self.selected_image_item:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return
            
        try:
            angle = float(self.rotate_angle_entry.get())
            index = self.image_items.index(self.selected_image_item)
            img = self.image_objects[index]
            rotated_img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
            self.image_objects[index] = rotated_img
            img_tk = ImageTk.PhotoImage(rotated_img)
            self.image_tk_objects[index] = img_tk
            self.canvas.itemconfig(self.selected_image_item, image=img_tk)
            self.update_status(f"Image rotated by {angle} degrees.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for rotation angle.")

    def resize_image(self):
        self.disable_paint()
        if not self.selected_image_item:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return
            
        try:
            size = tuple(map(int, self.resize_entry.get().split(',')))
            if len(size) != 2:
                raise ValueError
                
            index = self.image_items.index(self.selected_image_item)
            img = self.image_objects[index]
            img = img.resize(size, Image.LANCZOS)
            self.image_objects[index] = img
            img_tk = ImageTk.PhotoImage(img)
            self.image_tk_objects[index] = img_tk
            self.canvas.itemconfig(self.selected_image_item, image=img_tk)
            self.update_status(f"Image resized to {size[0]}x{size[1]}.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid size (width,height).")

    def select_bg_color(self):
        self.disable_paint()
        color_code = colorchooser.askcolor(title="Choose Background Color", initialcolor=self.bg_color)
        if color_code[1]:
            self.bg_color = color_code[1]
            self.bg_image = None
            self.canvas.delete("bg")
            self.canvas.config(bg=self.bg_color)
            self.update_status("Background color updated.")

    def upload_bg_image(self):
        self.disable_paint()
        bg_image_path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if bg_image_path:
            try:
                self.bg_image = Image.open(bg_image_path).convert("RGBA")
                self.bg_color = None
                self.display_bg_image()
                self.update_status("Background image loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load background image: {str(e)}")

    def display_bg_image(self):
        if self.bg_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            bg_resized = self.bg_image.resize((canvas_width, canvas_height), Image.LANCZOS)
            self.bg_image_tk = ImageTk.PhotoImage(bg_resized)
            self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor=tk.NW, tags="bg")
            self.canvas.tag_lower("bg")

    def open_filter_window(self):
        self.disable_paint()
        if not self.selected_image_item:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return

        filter_window = Toplevel(self.root)
        filter_window.title("Image Filters")
        filter_window.geometry("400x500")
        filter_window.configure(bg='#2c3e50')
        filter_window.transient(self.root)
        filter_window.grab_set()

        main_frame = ttk.Frame(filter_window, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="Image Filters", font=('Segoe UI', 16, 'bold'),
                bg='#34495e', fg='#ecf0f1').pack(pady=10)

        # Brightness
        brightness_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        brightness_frame.pack(fill=tk.X, pady=10)
        tk.Label(brightness_frame, text="Brightness:", bg='#34495e', fg='#ecf0f1').pack(anchor='w')
        brightness_scale = tk.Scale(brightness_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL,
                                  resolution=0.1, bg='#34495e', fg='#ecf0f1')
        brightness_scale.set(1.0)
        brightness_scale.pack(fill=tk.X, pady=5)

        # Contrast
        contrast_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        contrast_frame.pack(fill=tk.X, pady=10)
        tk.Label(contrast_frame, text="Contrast:", bg='#34495e', fg='#ecf0f1').pack(anchor='w')
        contrast_scale = tk.Scale(contrast_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL,
                                resolution=0.1, bg='#34495e', fg='#ecf0f1')
        contrast_scale.set(1.0)
        contrast_scale.pack(fill=tk.X, pady=5)

        # Sharpness
        sharpness_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        sharpness_frame.pack(fill=tk.X, pady=10)
        tk.Label(sharpness_frame, text="Sharpness:", bg='#34495e', fg='#ecf0f1').pack(anchor='w')
        sharpness_scale = tk.Scale(sharpness_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL,
                                 resolution=0.1, bg='#34495e', fg='#ecf0f1')
        sharpness_scale.set(1.0)
        sharpness_scale.pack(fill=tk.X, pady=5)

        self.current_filters = {
            'brightness': brightness_scale,
            'contrast': contrast_scale,
            'sharpness': sharpness_scale,
        }

        ttk.Button(main_frame, text="Preview Changes", 
                  command=self.update_filter_preview, style='Secondary.TButton').pack(pady=10)

        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Apply Filter", 
                  command=lambda: self.apply_filter(
                      brightness_scale.get(), 
                      contrast_scale.get(), 
                      sharpness_scale.get(), 
                      filter_window),
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_filter, style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)

        self.original_image = self.image_objects[self.image_items.index(self.selected_image_item)].copy()

    def update_filter_preview(self, event=None):
        if self.selected_image_item:
            brightness = self.current_filters['brightness'].get()
            contrast = self.current_filters['contrast'].get()
            sharpness = self.current_filters['sharpness'].get()

            index = self.image_items.index(self.selected_image_item)
            img = self.original_image.copy()

            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)

            img_tk = ImageTk.PhotoImage(img)
            self.image_tk_objects[index] = img_tk
            self.canvas.itemconfig(self.selected_image_item, image=img_tk)

    def apply_filter(self, brightness, contrast, sharpness, filter_window):
     if self.selected_image_item:
        index = self.image_items.index(self.selected_image_item)
        img = self.original_image.copy()
        
        # Convert to RGB if needed (assuming image is in RGB format)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get image dimensions
        width, height = img.size
        
        # Apply brightness, contrast, and sharpness manually
        img_processed = self.apply_brightness_contrast_sharpness(
            img, brightness, contrast, sharpness
        )
        
        self.image_objects[index] = img_processed
        img_tk = ImageTk.PhotoImage(img_processed)
        self.image_tk_objects[index] = img_tk
        self.canvas.itemconfig(self.selected_image_item, image=img_tk)

        filter_window.destroy()
        self.update_status("Filter applied successfully!")

    def apply_brightness_contrast_sharpness(self, img, brightness, contrast, sharpness):
    
    # Apply brightness, contrast, and sharpness adjustments manually
    
    # Get image data
     pixels = img.load()
     width, height = img.size
    
     # Create a new image for the result
     result_img = Image.new('RGB', (width, height))
     result_pixels = result_img.load()
    
     # Apply brightness and contrast first
     for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Apply brightness
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)
            
            # Apply contrast
            r = self.apply_contrast_to_channel(r, contrast)
            g = self.apply_contrast_to_channel(g, contrast)
            b = self.apply_contrast_to_channel(b, contrast)
            
            # Clamp values to 0-255
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            result_pixels[x, y] = (r, g, b)
    
    # Apply sharpness if needed
     if sharpness != 1.0:
        result_img = self.apply_sharpness(result_img, sharpness)
    
        return result_img

    def apply_contrast_to_channel(self, value, contrast):
    
     # Apply contrast adjustment to a single channel value
    
    # Convert contrast factor to a more usable form
    # contrast > 1 increases contrast, < 1 decreases contrast
     if contrast > 1:
        # Enhanced contrast
        factor = 259 * (contrast + 255) / (255 * (259 - contrast))
        value = factor * (value - 128) + 128
     else:
        # Reduced contrast - simple linear interpolation towards 128
        value = 128 + (value - 128) * contrast
    
     return int(value)
 
    def apply_sharpness(self, img, sharpness):
    
    # Apply sharpness adjustment using convolution
    
     if sharpness == 1.0:
        return img
    
     pixels = img.load()
     width, height = img.size
    
     # Create a new image for the sharpened result
     sharp_img = Image.new('RGB', (width, height))
     sharp_pixels = sharp_img.load()
    
     # Sharpening kernel (unsharp mask)
     # The strength of the sharpening is controlled by the sharpness parameter
     kernel = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
     ]
    
     # Adjust kernel based on sharpness
     center_weight = 4.0 * sharpness + 1.0
     edge_weight = -sharpness
    
     kernel[0][1] = edge_weight
     kernel[1][0] = edge_weight
     kernel[1][2] = edge_weight
     kernel[2][1] = edge_weight
     kernel[1][1] = center_weight
    
     # Apply convolution for sharpening
     for y in range(1, height - 1):
        for x in range(1, width - 1):
            r_total, g_total, b_total = 0, 0, 0
            
            # Apply kernel to 3x3 neighborhood
            for ky in range(3):
                for kx in range(3):
                    px = x + kx - 1
                    py = y + ky - 1
                    
                    r, g, b = pixels[px, py]
                    weight = kernel[ky][kx]
                    
                    r_total += r * weight
                    g_total += g * weight
                    b_total += b * weight
            
            # Normalize and clamp values
            r_total = max(0, min(255, int(r_total)))
            g_total = max(0, min(255, int(g_total)))
            b_total = max(0, min(255, int(b_total)))
            
            sharp_pixels[x, y] = (r_total, g_total, b_total)
    
    # Copy border pixels from original (since convolution doesn't work on borders)
     for y in range(height):
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                sharp_pixels[x, y] = pixels[x, y]
    
     return sharp_img

    def simple_sharpness(self, img, sharpness):
    
     # Alternative simpler sharpness implementation
    
     if sharpness == 1.0:
        return img
    
     pixels = img.load()
     width, height = img.size
    
     result_img = Image.new('RGB', (width, height))
     result_pixels = result_img.load()
    
     for y in range(1, height - 1):
        for x in range(1, width - 1):
            # Get current pixel and neighbors
            current_r, current_g, current_b = pixels[x, y]
            
            # Simple edge detection (difference from average of neighbors)
            neighbors_r, neighbors_g, neighbors_b = [], [], []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    r, g, b = pixels[x + dx, y + dy]
                    neighbors_r.append(r)
                    neighbors_g.append(g)
                    neighbors_b.append(b)
            
            avg_r = sum(neighbors_r) // len(neighbors_r)
            avg_g = sum(neighbors_g) // len(neighbors_g)
            avg_b = sum(neighbors_b) // len(neighbors_b)
            
            # Enhance edges based on sharpness
            edge_r = current_r - avg_r
            edge_g = current_g - avg_g
            edge_b = current_b - avg_b
            
            new_r = int(current_r + edge_r * (sharpness - 1))
            new_g = int(current_g + edge_g * (sharpness - 1))
            new_b = int(current_b + edge_b * (sharpness - 1))
            
            new_r = max(0, min(255, new_r))
            new_g = max(0, min(255, new_g))
            new_b = max(0, min(255, new_b))
            
            result_pixels[x, y] = (new_r, new_g, new_b)
    
     # Copy border pixels
     for y in range(height):
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                result_pixels[x, y] = pixels[x, y]
    
     return result_img

    def reset_filter(self):
        if self.selected_image_item and self.original_image:
            index = self.image_items.index(self.selected_image_item)
            self.image_objects[index] = self.original_image
            img_tk = ImageTk.PhotoImage(self.original_image)
            self.image_tk_objects[index] = img_tk
            self.canvas.itemconfig(self.selected_image_item, image=img_tk)
            self.update_status("Filter reset to original.")

    def remove_background(self):
        """Simple background removal using improved algorithm"""
        if not self.selected_image_item:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return

        try:
            index = self.image_items.index(self.selected_image_item)
            img = self.image_objects[index]
            
            # Convert PIL Image to numpy array
            img_array = np.array(img)
            
            # Use improved background removal
            result_img = self.improved_background_removal(img_array)
            
            # Convert back to PIL Image
            new_img = Image.fromarray(result_img).convert("RGBA")
            
            self.image_objects[index] = new_img
            img_tk = ImageTk.PhotoImage(new_img)
            self.image_tk_objects[index] = img_tk
            self.canvas.itemconfig(self.selected_image_item, image=img_tk)
            
            self.update_status("Background removed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove background: {str(e)}")
            
    def improved_background_removal(self, img_array):
    # improved background removal using LAB color space and K-means clustering"""
     try:
        # Get image dimensions
        height, width = img_array.shape[:2]
        
        # Convert to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2BGR)
        
        # Convert to LAB color space - better for color segmentation
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        
        # Reshape image to be a list of pixels
        pixel_values = img_lab.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)
        
        # Define K-means criteria and apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 4  # Number of clusters
        _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to 8-bit values
        centers = np.uint8(centers)
        
        # Flatten the labels array
        labels = labels.flatten()
        
        # Find the dominant cluster (usually background)
        # Count pixels in each cluster
        unique, counts = np.unique(labels, return_counts=True)
        cluster_counts = dict(zip(unique, counts))
        
        # Sort clusters by size (largest first)
        sorted_clusters = sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)
        
        # The largest cluster is typically the background
        background_cluster = sorted_clusters[0][0]
        
        # Create binary mask: 1 for foreground, 0 for background
        segmented_mask = np.where(labels == background_cluster, 0, 1)
        
        # Reshape back to original image dimension and ensure uint8 type
        segmented_mask = segmented_mask.reshape(img_lab.shape[:2]).astype(np.uint8)
        
        # Apply morphological operations to clean up the mask with proper data type
        kernel = np.ones((3, 3), np.uint8)
        segmented_mask = cv2.morphologyEx(segmented_mask, cv2.MORPH_OPEN, kernel)
        segmented_mask = cv2.morphologyEx(segmented_mask, cv2.MORPH_CLOSE, kernel)
        
        # Apply mask to original image
        result = img_bgr * segmented_mask[:, :, np.newaxis]
        
        # Convert back to RGB
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        
        # Create alpha channel
        alpha = (segmented_mask * 255).astype(np.uint8)
        
        # Combine RGB with alpha
        result_with_alpha = np.dstack((result_rgb, alpha))
        
        return result_with_alpha
        
     except Exception as e:
        print(f"K-means segmentation failed: {e}")
        # Fallback to simple color-based method
        return self.simple_color_based_removal(img_array)

 


    def select_paint_color(self):
        self.enable_paint()
        color_code = colorchooser.askcolor(title="Choose Paint Color", initialcolor=self.paint_color)
        if color_code[1]:
            self.paint_color = color_code[1]
            self.update_status("Paint color selected. Click and drag on canvas to paint.")

    def enable_paint(self):
        self.painting = True
        self.erasing = False
        self.canvas.config(cursor="pencil")
        self.update_status("Painting mode enabled. Click and drag to paint.")

    def enable_eraser(self):
        self.painting = True
        self.erasing = True
        self.canvas.config(cursor="circle")
        self.update_status("Eraser mode enabled. Click and drag to erase.")

    def paint(self, event):
        if self.painting:
            x1, y1 = (event.x - 1), (event.y - 1)
            x2, y2 = (event.x + 1), (event.y + 1)
            thickness = self.erase_thickness.get() if self.erasing else self.paint_thickness.get()

            color = (255, 255, 255, 0) if self.erasing else self.paint_color

            self.temp_buffer_draw.ellipse(
                (x1-thickness, y1-thickness, x2+thickness, y2+thickness), 
                fill=color, outline=color
            )
            
            self.update_temp_canvas()
            self.temp_strokes.append((x1, y1, x2, y2, color, thickness))

    def update_temp_canvas(self):
        self.temp_buffer_tk = ImageTk.PhotoImage(self.temp_buffer)
        self.canvas.itemconfig(self.temp_buffer_image_item, image=self.temp_buffer_tk)

    def apply_paint(self):
        self.buffer = Image.alpha_composite(self.buffer, self.temp_buffer)
        self.buffer_draw = ImageDraw.Draw(self.buffer)

        self.temp_buffer = Image.new("RGBA", (800, 600), (255, 255, 255, 0))
        self.temp_buffer_draw = ImageDraw.Draw(self.temp_buffer)
        self.temp_strokes.clear()

        self.update_canvas()
        self.update_temp_canvas()
        self.disable_paint()
        self.strokes.extend(self.temp_strokes)
        self.update_status("Paint applied to canvas.")

    def reset_paint(self):
        self.strokes.clear()
        self.temp_strokes.clear()
        self.buffer = Image.new("RGBA", (800, 600), (255, 255, 255, 0))
        self.buffer_draw = ImageDraw.Draw(self.buffer)
        self.temp_buffer = Image.new("RGBA", (800, 600), (255, 255, 255, 0))
        self.temp_buffer_draw = ImageDraw.Draw(self.temp_buffer)
        self.update_canvas()
        self.update_temp_canvas()
        self.disable_paint()
        self.update_status("All paint cleared.")

    def update_canvas(self):
        self.buffer_tk = ImageTk.PhotoImage(self.buffer)
        self.canvas.itemconfig(self.buffer_image_item, image=self.buffer_tk)

    def select_text_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")
        if color_code[1]:
            self.text_color = color_code[1]

    def add_text(self):
        text = self.text_entry.get()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        try:
            font_size = int(self.font_size_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Font size must be a number.")
            return

        self.text_to_add = text
        self.text_font_name = self.font_choice.get()
        self.text_font_size = font_size
        self.text_color = getattr(self, 'text_color', "#ffffff")

        self.update_status("Click on canvas to place text.")
        self.canvas.bind("<Button-1>", self.place_text_on_click)

    def place_text_on_click(self, event):
        x, y = event.x, event.y

        try:
            text_font = (self.text_font_name, self.text_font_size)
            text_id = self.canvas.create_text(x, y, text=self.text_to_add, 
                                            font=text_font, fill=self.text_color,
                                            anchor='center')
            self.text_items.append(text_id)
            self.update_status("Text placed on canvas.")
        except Exception as e:
            messagebox.showerror("Text Error", f"Could not add text: {str(e)}")

        self.canvas.unbind("<Button-1>")

    def reset_text(self):
        for text_id in self.text_items:
            self.canvas.delete(text_id)
        self.text_items.clear()
        self.update_status("All text removed.")

    def run_edge_detection(self):
        if self.selected_image_index is None:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return
            
        try:
            sigma = simpledialog.askfloat("Edge Detection", 
                                        "Enter Gaussian sigma (0.5-3.0):", 
                                        initialvalue=1.5, minvalue=0.5, maxvalue=3.0)
            if sigma is None: return
            
            threshold = simpledialog.askfloat("Edge Detection", 
                                            "Enter threshold (1-50):", 
                                            initialvalue=10.0, minvalue=1.0, maxvalue=50.0)
            if threshold is None: return
            # Convert to grayscale numpy array
            pil_img = self.image_objects[self.selected_image_index].convert("RGB")
            gray = np.array(pil_img.convert("L"), dtype=np.float32)
            # Calculate kernel size (must be odd) and apply Gaussian blur

            ksize = int(6 * sigma) + 1
            if ksize % 2 == 0:
                ksize += 1
                
            blurred = cv2.GaussianBlur(gray, (ksize, ksize), sigmaX=sigma, sigmaY=sigma)
            # Apply Laplacian filter for edge detection

            lap = cv2.Laplacian(blurred, cv2.CV_32F, ksize=3)
            # Zero-crossing detection: check 8 neighbors

            zc = np.zeros_like(lap, dtype=np.uint8)
            H, W = lap.shape
            
            for y in range(1, H-1):
                for x in range(1, W-1):
                    center = lap[y, x]
                    neighbors = [
                        lap[y-1, x-1], lap[y-1, x], lap[y-1, x+1],
                        lap[y, x-1],                 lap[y, x+1],
                        lap[y+1, x-1], lap[y+1, x], lap[y+1, x+1]
                    ]
                    # Mark as edge if significant zero-crossing found
                    max_diff = 0
                    for n in neighbors:
                        if (center < 0 and n > 0) or (center > 0 and n < 0):
                            diff = abs(center - n)
                            if diff > max_diff:
                                max_diff = diff
                    
                    if max_diff > threshold:
                        zc[y, x] = 255
            
            edge_colored = np.zeros((H, W, 3), dtype=np.uint8)
            edge_colored[zc == 255] = [255, 0, 0]
            
            edge_pil = Image.fromarray(edge_colored).convert("RGBA")
            self._replace_image(edge_pil)
            
            self.update_status("Edge detection completed.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Edge detection failed: {str(e)}")
            
    # Convert to grayscale and apply Otsu's thresholding

    def run_region_descriptor(self):
        if self.selected_image_index is None:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return

        try:
            pil_img = self.image_objects[self.selected_image_index].convert("RGB")
            gray = np.array(pil_img.convert("L"), dtype=np.uint8)
            
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours in binary image

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                messagebox.showinfo("Region Analysis", "No significant regions found.")
                return

            results = []
            labeled_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # Calculate basic region properties

            for i, cnt in enumerate(contours):
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                
            # Fit ellipse and calculate shape properties

                if len(cnt) >= 5:
                    ellipse = cv2.fitEllipse(cnt)
                    (cx, cy), (MA, ma), angle = ellipse
                    major_axis = max(MA, ma)
                    minor_axis = min(MA, ma)
                    eccentricity = math.sqrt(max(0.0, 1.0 - (minor_axis/major_axis)**2)) if major_axis > 0 else 0
                else:
                    major_axis = minor_axis = eccentricity = 0.0
                
                form_factor = (4 * math.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
                compactness = (perimeter ** 2) / (4 * math.pi * area) if area > 0 else 0

                results.append({
                    "region": i + 1,
                    "area": float(area),
                    "perimeter": float(perimeter),
                    "major_axis": float(major_axis),
                    "minor_axis": float(minor_axis),
                    "form_factor": float(form_factor),
                    "compactness": float(compactness),
                    "eccentricity": float(eccentricity)
                })
                
                cv2.drawContours(labeled_img, [cnt], -1, (0, 255, 0), 2)
                
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cv2.putText(labeled_img, str(i+1), (cx, cy), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            self.show_region_results(results)
            
            labeled_pil = Image.fromarray(labeled_img).convert("RGBA")
            self._replace_image(labeled_pil)
            
            self.update_status("Region analysis completed.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Region analysis failed: {str(e)}")

    def show_region_results(self, results):
        top = Toplevel(self.root)
        top.title("Region Analysis Results")
        top.geometry("700x500")
        top.configure(bg='#2c3e50')
        
        main_frame = ttk.Frame(top, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Region Descriptors", font=('Segoe UI', 16, 'bold'),
                bg='#34495e', fg='#ecf0f1').pack(pady=10)
        
        txt = scrolledtext.ScrolledText(main_frame, width=80, height=20, 
                                      bg='#2c3e50', fg='#ecf0f1', font=('Consolas', 9))
        txt.pack(fill=tk.BOTH, expand=True)
        
        txt.insert(tk.END, "Region descriptors for selected image\n\n")
        for r in results:
            txt.insert(tk.END, 
                     f"Region {r['region']}: Area={r['area']:.1f}, "
                     f"Perimeter={r['perimeter']:.1f}, "
                     f"Form Factor={r['form_factor']:.3f}, "
                     f"Eccentricity={r['eccentricity']:.3f}\n")
        
        txt.configure(state='disabled')


    def run_notch_filter(self):
     if self.selected_image_index is None:
        messagebox.showwarning("No Selection", "Please select an image first.")
        return
        
     try:
        # For multiple notch points, you could collect them in a list
        notch_points = []
        
        while True:
            center_x = simpledialog.askinteger("Notch Point", 
                                             "Center X (0-100% of width) or Cancel to finish:",
                                             initialvalue=25, minvalue=0, maxvalue=100)
            if center_x is None: break
            
            center_y = simpledialog.askinteger("Notch Point",
                                             "Center Y (0-100% of height):", 
                                             initialvalue=25, minvalue=0, maxvalue=100)
            if center_y is None: break
            
            notch_points.append((center_x, center_y))
            
            if not messagebox.askyesno("Add Another", "Add another notch point?"):
                break
        
        if not notch_points:
            return
            
        D0 = simpledialog.askinteger("Butterworth Notch Filter",
                                   "Cutoff frequency (D0):",
                                   initialvalue=5, minvalue=1, maxvalue=100)
        if D0 is None: return
        
        n = simpledialog.askinteger("Butterworth Notch Filter",
                                  "Filter order (n):",
                                  initialvalue=2, minvalue=1, maxvalue=10)
        if n is None: return

        # Convert image to grayscale
        pil_img = self.image_objects[self.selected_image_index].convert("L")
        img_array = np.array(pil_img, dtype=np.float32)
        
        # Get image dimensions
        M, N = img_array.shape
        
        # Convert percentage coordinates to frequency domain offsets
        uk_list = []
        vk_list = []
        for center_x, center_y in notch_points:
            center_u = int(N * center_x / 100)
            center_v = int(M * center_y / 100)
            uk_list.append(center_u - N // 2)
            vk_list.append(center_v - M // 2)
        
        # Apply Butterworth notch filter
        filtered_img = self._apply_butterworth_notch_filter(img_array, uk_list, vk_list, D0, n)
        
        # Convert back to PIL image
        filtered_img = (filtered_img - filtered_img.min()) / (filtered_img.max() - filtered_img.min()) * 255
        filtered_img = filtered_img.astype(np.uint8)
        
        result_pil = Image.fromarray(filtered_img).convert("RGBA")
        self._replace_image(result_pil)
        
        self.update_status(f"Butterworth notch filter applied with {len(notch_points)} points (D0={D0}, n={n}).")
        
     except Exception as e:
        messagebox.showerror("Error", f"Butterworth notch filter failed: {str(e)}")
    def _apply_butterworth_notch_filter(self, img, uk_list, vk_list, D0, n):
      """
      Apply Butterworth notch reject filter to image
    
    Args:
        img: Input image array
        uk_list: List of u-coordinate offsets from center in frequency domain
        vk_list: List of v-coordinate offsets from center in frequency domain  
        D0: Cutoff frequency
        n: Filter order
    """
      M, N = img.shape
    
      # Compute Fourier Transform
      ft = np.fft.fft2(img)
      ft_shift = np.fft.fftshift(ft)
    
      # Create Butterworth notch reject filter
      H = self._create_butterworth_notch_filter(M, N, uk_list, vk_list, D0, n)
    
      # Apply filter in frequency domain
      filtered_ft = ft_shift * H
    
      # Inverse Fourier Transform
      filtered_shift = np.fft.ifftshift(filtered_ft)
      filtered_img = np.fft.ifft2(filtered_shift)
      filtered_img = np.real(filtered_img)
    
      return filtered_img

    def _create_butterworth_notch_filter(self, M, N, uk_list, vk_list, D0, n):
      """
    Create Butterworth notch reject filter
    
    Args:
        M, N: Image dimensions (rows, columns)
        uk_list: List of u-coordinate offsets
        vk_list: List of v-coordinate offsets
        D0: Cutoff frequency  
        n: Filter order
    """
      H = np.ones((M, N), dtype=np.float32)
    
      for uk, vk in zip(uk_list, vk_list):
        for u in range(M):
            for v in range(N):
                # Calculate distances to notch points and their symmetric points
                Dk = np.sqrt((u - M//2 - uk)**2 + (v - N//2 - vk)**2)
                D_k = np.sqrt((u - M//2 + uk)**2 + (v - N//2 + vk)**2)
                
                # Avoid division by zero
                if Dk == 0:
                    Dk = 1e-6
                if D_k == 0:
                    D_k = 1e-6
                
                # Butterworth notch reject formula
                Hk = 1 / (1 + (D0 / Dk)**(2 * n))
                H_k = 1 / (1 + (D0 / D_k)**(2 * n))
                H[u, v] = H[u, v] * Hk * H_k
    
      return H


    def run_histogram_enhancement(self):
        """Run histogram equalization on selected image with PDF and CDF displays"""
        if self.selected_image_index is None:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return
        
        # Ask for enhancement type
        enhancement_type = simpledialog.askstring(
            "Histogram Enhancement",
            "Enter enhancement type:\n1 - Grayscale\n2 - RGB\n3 - HSV\n4 - Histogram Matching",
            initialvalue="2"
        )
        
        if not enhancement_type:
            return
            
        try:
            pil_img = self.image_objects[self.selected_image_index].convert("RGB")
            img_array = np.array(pil_img)
            
            if enhancement_type == "1":
                # Grayscale enhancement
                result_img, hist_data = self.grayscale_histogram_equalization(img_array)
            elif enhancement_type == "2":
                # RGB enhancement
                result_img, hist_data = self.rgb_histogram_equalization(img_array)
            elif enhancement_type == "3":
                # HSV enhancement
                result_img, hist_data = self.hsv_histogram_equalization(img_array)
            elif enhancement_type == "4":
                # Histogram matching with double Gaussian
                result_img, hist_data = self.histogram_matching_gaussian(img_array)
            else:
                messagebox.showerror("Error", "Invalid enhancement type. Use 1, 2, 3, or 4.")
                return
            
            # Convert result to PIL
            result_pil = Image.fromarray(result_img).convert("RGBA")
            self._replace_image(result_pil)
            
            # Show histogram results
            self.show_histogram_results(hist_data, enhancement_type)
            
            self.update_status("Histogram enhancement completed.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Histogram enhancement failed: {str(e)}")
    
    def grayscale_histogram_equalization(self, img_array):
        """Apply histogram equalization to grayscale image"""
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply histogram equalization
        equalized = cv2.equalizeHist(gray)
        
        # Convert back to RGB for display
        result_img = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
        
        # Calculate histograms, PDF, CDF
        hist_original = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_equalized = cv2.calcHist([equalized], [0], None, [256], [0, 256])
        
        # Calculate PDF and CDF
        pdf_original = hist_original / (gray.shape[0] * gray.shape[1])
        pdf_equalized = hist_equalized / (equalized.shape[0] * equalized.shape[1])
        
        cdf_original = np.cumsum(pdf_original)
        cdf_equalized = np.cumsum(pdf_equalized)
        
        hist_data = {
            'original': gray,
            'equalized': equalized,
            'hist_original': hist_original,
            'hist_equalized': hist_equalized,
            'pdf_original': pdf_original,
            'pdf_equalized': pdf_equalized,
            'cdf_original': cdf_original,
            'cdf_equalized': cdf_equalized,
            'channels': ['Grayscale']
        }
        
        return result_img, hist_data
    
    def rgb_histogram_equalization(self, img_array):
        """Apply histogram equalization to each RGB channel separately"""
        # Split channels
        b, g, r = cv2.split(img_array)
        
        # Equalize each channel
        b_eq = cv2.equalizeHist(b)
        g_eq = cv2.equalizeHist(g)
        r_eq = cv2.equalizeHist(r)
        
        # Merge channels
        result_img = cv2.merge([b_eq, g_eq, r_eq])
        
        # Calculate histograms for each channel
        hist_data = {
            'channels': ['Blue', 'Green', 'Red'],
            'original_channels': [b, g, r],
            'equalized_channels': [b_eq, g_eq, r_eq]
        }
        
        # Calculate histograms, PDF, CDF for each channel
        for i, channel in enumerate(['Blue', 'Green', 'Red']):
            hist_original = cv2.calcHist([hist_data['original_channels'][i]], [0], None, [256], [0, 256])
            hist_equalized = cv2.calcHist([hist_data['equalized_channels'][i]], [0], None, [256], [0, 256])
            
            pdf_original = hist_original / (b.shape[0] * b.shape[1])
            pdf_equalized = hist_equalized / (b_eq.shape[0] * b_eq.shape[1])
            
            cdf_original = np.cumsum(pdf_original)
            cdf_equalized = np.cumsum(pdf_equalized)
            
            hist_data[f'hist_original_{channel.lower()}'] = hist_original
            hist_data[f'hist_equalized_{channel.lower()}'] = hist_equalized
            hist_data[f'pdf_original_{channel.lower()}'] = pdf_original
            hist_data[f'pdf_equalized_{channel.lower()}'] = pdf_equalized
            hist_data[f'cdf_original_{channel.lower()}'] = cdf_original
            hist_data[f'cdf_equalized_{channel.lower()}'] = cdf_equalized
        
        return result_img, hist_data
    
    def hsv_histogram_equalization(self, img_array):
        """Apply histogram equalization only to Value channel in HSV"""
        # Convert to HSV
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        
        # Equalize only Value channel
        v_eq = cv2.equalizeHist(v)
        
        # Merge channels
        hsv_eq = cv2.merge([h, s, v_eq])
        
        # Convert back to RGB
        result_img = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2RGB)
        
        # Calculate histograms
        hist_data = {
            'channels': ['Hue', 'Saturation', 'Value'],
            'original_channels': [h, s, v],
            'equalized_channels': [h, s, v_eq]
        }
        
        # Calculate histograms, PDF, CDF for each channel
        for i, channel in enumerate(['Hue', 'Saturation', 'Value']):
            hist_original = cv2.calcHist([hist_data['original_channels'][i]], [0], None, [256], [0, 256])
            hist_equalized = cv2.calcHist([hist_data['equalized_channels'][i]], [0], None, [256], [0, 256])
            
            pdf_original = hist_original / (h.shape[0] * h.shape[1])
            pdf_equalized = hist_equalized / (h.shape[0] * h.shape[1])
            
            cdf_original = np.cumsum(pdf_original)
            cdf_equalized = np.cumsum(pdf_equalized)
            
            hist_data[f'hist_original_{channel.lower()}'] = hist_original
            hist_data[f'hist_equalized_{channel.lower()}'] = hist_equalized
            hist_data[f'pdf_original_{channel.lower()}'] = pdf_original
            hist_data[f'pdf_equalized_{channel.lower()}'] = pdf_equalized
            hist_data[f'cdf_original_{channel.lower()}'] = cdf_original
            hist_data[f'cdf_equalized_{channel.lower()}'] = cdf_equalized
        
        return result_img, hist_data
    
    def histogram_matching_gaussian(self, img_array):
        """Apply histogram matching with double Gaussian distribution"""
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Generate target double Gaussian histogram
        target_hist = self.generate_double_gaussian_histogram()
        
        # Perform histogram matching
        matched_img = self.histogram_matching(gray, target_hist)
        
        # Convert back to RGB for display
        result_img = cv2.cvtColor(matched_img, cv2.COLOR_GRAY2RGB)
        
        # Calculate histograms
        hist_original = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_matched = cv2.calcHist([matched_img], [0], None, [256], [0, 256])
        
        # Calculate PDF and CDF
        pdf_original = hist_original / (gray.shape[0] * gray.shape[1])
        pdf_matched = hist_matched / (matched_img.shape[0] * matched_img.shape[1])
        pdf_target = target_hist / np.sum(target_hist)
        
        cdf_original = np.cumsum(pdf_original)
        cdf_matched = np.cumsum(pdf_matched)
        cdf_target = np.cumsum(pdf_target)
        
        hist_data = {
            'original': gray,
            'equalized': matched_img,
            'hist_original': hist_original,
            'hist_equalized': hist_matched,
            'hist_target': target_hist,
            'pdf_original': pdf_original,
            'pdf_equalized': pdf_matched,
            'pdf_target': pdf_target,
            'cdf_original': cdf_original,
            'cdf_equalized': cdf_matched,
            'cdf_target': cdf_target,
            'channels': ['Grayscale'],
            'matching': True
        }
        
        return result_img, hist_data
    
    def generate_double_gaussian_histogram(self):
        """Generate target histogram with double Gaussian distribution"""
        x = np.arange(256)
        
        # Two Gaussian distributions
        gaussian1 = 0.6 * np.exp(-0.5 * ((x - 80) / 30) ** 2)
        gaussian2 = 0.4 * np.exp(-0.5 * ((x - 180) / 25) ** 2)
        
        # Combine and normalize
        target_hist = gaussian1 + gaussian2
        target_hist = target_hist / np.sum(target_hist) * 1000000  # Scale to reasonable values
        
        return target_hist.astype(np.float32)
    
    def histogram_matching(self, source, target_hist):
        """Match source image histogram to target histogram"""
        # Calculate CDF of source image
        source_hist = cv2.calcHist([source], [0], None, [256], [0, 256])
        source_pdf = source_hist / (source.shape[0] * source.shape[1])
        source_cdf = np.cumsum(source_pdf)
        
        # Calculate CDF of target histogram
        target_pdf = target_hist / np.sum(target_hist)
        target_cdf = np.cumsum(target_pdf)
        
        # Create mapping function
        mapping = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            j = 255
            while j > 0 and source_cdf[i] <= target_cdf[j]:
                j -= 1
            mapping[i] = j
        
        # Apply mapping
        matched = cv2.LUT(source, mapping)
        return matched
    
    def show_histogram_results(self, hist_data, enhancement_type):
        """Display histogram results with PDF and CDF in a new window"""
        top = Toplevel(self.root)
        top.title("Histogram Enhancement Results")
        top.geometry("1200x800")
        top.configure(bg='#2c3e50')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(top)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Histogram tab
        hist_frame = ttk.Frame(notebook)
        notebook.add(hist_frame, text="Histograms")
        
        # Create figure for histograms based on enhancement type
        if enhancement_type == "1":  # Grayscale
            fig_hist = self.create_grayscale_histogram_plot(hist_data)
        elif enhancement_type == "2":  # RGB
            fig_hist = self.create_rgb_histogram_plot(hist_data)
        elif enhancement_type == "3":  # HSV
            fig_hist = self.create_hsv_histogram_plot(hist_data)
        elif enhancement_type == "4":  # Histogram Matching
            fig_hist = self.create_matching_histogram_plot(hist_data)
        
        canvas_hist = FigureCanvasTkAgg(fig_hist, hist_frame)
        canvas_hist.draw()
        canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # PDF/CDF tab
        pdf_frame = ttk.Frame(notebook)
        notebook.add(pdf_frame, text="PDF & CDF")
        
        # Create figure for PDF and CDF
        if enhancement_type == "4":  # Histogram Matching
            fig_pdf = self.create_matching_pdf_cdf_plot(hist_data)
        else:
            fig_pdf = self.create_pdf_cdf_plot(hist_data, enhancement_type)
        
        canvas_pdf = FigureCanvasTkAgg(fig_pdf, pdf_frame)
        canvas_pdf.draw()
        canvas_pdf.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_grayscale_histogram_plot(self, hist_data):
        """Create histogram plot for grayscale enhancement"""
        fig = plt.Figure(figsize=(12, 8))
        
        # Set smaller font sizes
        title_fontsize = 7
        label_fontsize = 6
        tick_fontsize = 6
        legend_fontsize = 6
        
        # Histograms
        ax1 = fig.add_subplot(221)
        ax1.plot(hist_data['hist_original'], 'k', label='Original', alpha=0.7, linewidth=1.5)
        ax1.plot(hist_data['hist_equalized'], 'r', label='Equalized', alpha=0.7, linewidth=1.5)
        ax1.set_title('Histograms Comparison', fontsize=title_fontsize)
        ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax1.set_ylabel('Frequency', fontsize=label_fontsize)
        ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax1.legend(fontsize=legend_fontsize)
        ax1.grid(True, alpha=0.3)
        
        # PDF
        ax2 = fig.add_subplot(222)
        ax2.plot(hist_data['pdf_original'], 'k', label='Original PDF', alpha=0.7, linewidth=1.5)
        ax2.plot(hist_data['pdf_equalized'], 'r', label='Equalized PDF', alpha=0.7, linewidth=1.5)
        ax2.set_title('Probability Density Function (PDF)', fontsize=title_fontsize)
        ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax2.set_ylabel('Probability', fontsize=label_fontsize)
        ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax2.legend(fontsize=legend_fontsize)
        ax2.grid(True, alpha=0.3)
        
        # CDF
        ax3 = fig.add_subplot(223)
        ax3.plot(hist_data['cdf_original'], 'k', label='Original CDF', alpha=0.7, linewidth=1.5)
        ax3.plot(hist_data['cdf_equalized'], 'r', label='Equalized CDF', alpha=0.7, linewidth=1.5)
        ax3.set_title('Cumulative Distribution Function (CDF)', fontsize=title_fontsize)
        ax3.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax3.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
        ax3.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax3.legend(fontsize=legend_fontsize)
        ax3.grid(True, alpha=0.3)
        
        # Enhancement Summary
        ax4 = fig.add_subplot(224)
        ax4.text(0.5, 0.5, 
                 'Grayscale Histogram Equalization\n\n'
                 '• Original vs Enhanced Comparison\n'
                 '• PDF shows probability distribution\n'
                 '• CDF shows cumulative distribution',
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax4.transAxes,
                 fontsize=9,  # Smaller font size
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax4.set_title('Enhancement Summary', fontsize=title_fontsize)
        ax4.axis('off')
        
        fig.tight_layout()
        return fig
    
    def create_rgb_histogram_plot(self, hist_data):
        """Create histogram plot for RGB enhancement"""
        fig = plt.Figure(figsize=(15, 10))
        colors = ['b', 'g', 'r']
        
        # Set smaller font sizes
        title_fontsize = 7
        label_fontsize = 6
        tick_fontsize = 5
        legend_fontsize = 6
        
        for i, channel in enumerate(['blue', 'green', 'red']):
            # Histograms
            ax1 = fig.add_subplot(3, 3, i*3 + 1)
            ax1.plot(hist_data[f'hist_original_{channel}'], colors[i], 
                    label=f'Original {channel.title()}', alpha=0.7, linewidth=1.2)
            ax1.plot(hist_data[f'hist_equalized_{channel}'], 'k', 
                    label=f'Equalized {channel.title()}', alpha=0.7, linewidth=1.0)
            ax1.set_title(f'{channel.title()} Channel Histogram', fontsize=title_fontsize)
            ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax1.set_ylabel('Frequency', fontsize=label_fontsize)
            ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax1.legend(fontsize=legend_fontsize)
            ax1.grid(True, alpha=0.3)
            
            # PDF
            ax2 = fig.add_subplot(3, 3, i*3 + 2)
            ax2.plot(hist_data[f'pdf_original_{channel}'], colors[i], 
                    label=f'Original PDF', alpha=0.7, linewidth=1.2)
            ax2.plot(hist_data[f'pdf_equalized_{channel}'], 'k', 
                    label=f'Equalized PDF', alpha=0.7, linewidth=1.0)
            ax2.set_title(f'{channel.title()} Channel PDF', fontsize=title_fontsize)
            ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax2.set_ylabel('Probability', fontsize=label_fontsize)
            ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax2.legend(fontsize=legend_fontsize)
            ax2.grid(True, alpha=0.3)
            
            # CDF
            ax3 = fig.add_subplot(3, 3, i*3 + 3)
            ax3.plot(hist_data[f'cdf_original_{channel}'], colors[i], 
                    label=f'Original CDF', alpha=0.7, linewidth=1.2)
            ax3.plot(hist_data[f'cdf_equalized_{channel}'], 'k', 
                    label=f'Equalized CDF', alpha=0.7, linewidth=1.0)
            ax3.set_title(f'{channel.title()} Channel CDF', fontsize=title_fontsize)
            ax3.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax3.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
            ax3.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax3.legend(fontsize=legend_fontsize)
            ax3.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    def create_hsv_histogram_plot(self, hist_data):
        """Create histogram plot for HSV enhancement"""
        fig = plt.Figure(figsize=(15, 10))
        colors = ['purple', 'orange', 'brown']
        
        # Set smaller font sizes
        title_fontsize = 7
        label_fontsize = 6
        tick_fontsize = 5
        legend_fontsize = 6
        
        for i, channel in enumerate(['hue', 'saturation', 'value']):
            # Histograms
            ax1 = fig.add_subplot(3, 3, i*3 + 1)
            ax1.plot(hist_data[f'hist_original_{channel}'], colors[i], 
                    label=f'Original {channel.title()}', alpha=0.7, linewidth=1.2)
            ax1.plot(hist_data[f'hist_equalized_{channel}'], 'k', 
                    label=f'Equalized {channel.title()}', alpha=0.7, linewidth=1.0)
            ax1.set_title(f'{channel.title()} Channel Histogram', fontsize=title_fontsize)
            ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax1.set_ylabel('Frequency', fontsize=label_fontsize)
            ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax1.legend(fontsize=legend_fontsize)
            ax1.grid(True, alpha=0.3)
            
            # PDF
            ax2 = fig.add_subplot(3, 3, i*3 + 2)
            ax2.plot(hist_data[f'pdf_original_{channel}'], colors[i], 
                    label=f'Original PDF', alpha=0.7, linewidth=1.2)
            ax2.plot(hist_data[f'pdf_equalized_{channel}'], 'k', 
                    label=f'Equalized PDF', alpha=0.7, linewidth=1.0)
            ax2.set_title(f'{channel.title()} Channel PDF', fontsize=title_fontsize)
            ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax2.set_ylabel('Probability', fontsize=label_fontsize)
            ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax2.legend(fontsize=legend_fontsize)
            ax2.grid(True, alpha=0.3)
            
            # CDF
            ax3 = fig.add_subplot(3, 3, i*3 + 3)
            ax3.plot(hist_data[f'cdf_original_{channel}'], colors[i], 
                    label=f'Original CDF', alpha=0.7, linewidth=1.2)
            ax3.plot(hist_data[f'cdf_equalized_{channel}'], 'k', 
                    label=f'Equalized CDF', alpha=0.7, linewidth=1.0)
            ax3.set_title(f'{channel.title()} Channel CDF', fontsize=title_fontsize)
            ax3.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax3.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
            ax3.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax3.legend(fontsize=legend_fontsize)
            ax3.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    def create_matching_histogram_plot(self, hist_data):
        """Create histogram plot for histogram matching"""
        fig = plt.Figure(figsize=(12, 8))
        
        # Set smaller font sizes
        title_fontsize = 7
        label_fontsize = 7
        tick_fontsize = 6
        legend_fontsize = 7
        
        # Histograms
        ax1 = fig.add_subplot(221)
        ax1.plot(hist_data['hist_original'], 'k', label='Original', alpha=0.7, linewidth=1.5)
        ax1.plot(hist_data['hist_equalized'], 'r', label='Matched', alpha=0.7, linewidth=1.5)
        ax1.plot(hist_data['hist_target'], 'b', label='Target', alpha=0.7, linewidth=1.5, linestyle='--')
        ax1.set_title('Histograms Comparison', fontsize=title_fontsize)
        ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax1.set_ylabel('Frequency', fontsize=label_fontsize)
        ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax1.legend(fontsize=legend_fontsize)
        ax1.grid(True, alpha=0.3)
        
        # PDF
        ax2 = fig.add_subplot(222)
        ax2.plot(hist_data['pdf_original'], 'k', label='Original PDF', alpha=0.7, linewidth=1.5)
        ax2.plot(hist_data['pdf_equalized'], 'r', label='Matched PDF', alpha=0.7, linewidth=1.5)
        ax2.plot(hist_data['pdf_target'], 'b', label='Target PDF', alpha=0.7, linewidth=1.5, linestyle='--')
        ax2.set_title('Probability Density Function (PDF)', fontsize=title_fontsize)
        ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax2.set_ylabel('Probability', fontsize=label_fontsize)
        ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax2.legend(fontsize=legend_fontsize)
        ax2.grid(True, alpha=0.3)
        
        # CDF
        ax3 = fig.add_subplot(223)
        ax3.plot(hist_data['cdf_original'], 'k', label='Original CDF', alpha=0.7, linewidth=1.5)
        ax3.plot(hist_data['cdf_equalized'], 'r', label='Matched CDF', alpha=0.7, linewidth=1.5)
        ax3.plot(hist_data['cdf_target'], 'b', label='Target CDF', alpha=0.7, linewidth=1.5, linestyle='--')
        ax3.set_title('Cumulative Distribution Function (CDF)', fontsize=title_fontsize)
        ax3.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax3.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
        ax3.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax3.legend(fontsize=legend_fontsize)
        ax3.grid(True, alpha=0.3)
        
        # Enhancement Summary
        ax4 = fig.add_subplot(224)
        ax4.text(0.5, 0.5, 
                 'Histogram Matching\n\n'
                 '• Original vs Matched vs Target\n'
                 '• Double Gaussian Target Distribution\n'
                 '• PDF shows probability distribution\n'
                 '• CDF shows cumulative distribution',
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax4.transAxes,
                 fontsize=9,  # Smaller font size
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax4.set_title('Enhancement Summary', fontsize=title_fontsize)
        ax4.axis('off')
        
        fig.tight_layout()
        return fig
    
    def create_pdf_cdf_plot(self, hist_data, enhancement_type):
        """Create PDF and CDF plots"""
        fig = plt.Figure(figsize=(12, 5))
        
        # Set smaller font sizes
        title_fontsize = 8
        label_fontsize = 7
        tick_fontsize = 6
        legend_fontsize = 7
        
        if enhancement_type == "1":  # Grayscale
            ax1 = fig.add_subplot(121)
            ax1.plot(hist_data['pdf_original'], 'k', label='Original PDF', alpha=0.7, linewidth=1.5)
            ax1.plot(hist_data['pdf_equalized'], 'r', label='Equalized PDF', alpha=0.7, linewidth=1.5)
            ax1.set_title('Probability Density Function (PDF)', fontsize=title_fontsize)
            ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax1.set_ylabel('Probability', fontsize=label_fontsize)
            ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax1.legend(fontsize=legend_fontsize)
            ax1.grid(True, alpha=0.3)
            
            ax2 = fig.add_subplot(122)
            ax2.plot(hist_data['cdf_original'], 'k', label='Original CDF', alpha=0.7, linewidth=1.5)
            ax2.plot(hist_data['cdf_equalized'], 'r', label='Equalized CDF', alpha=0.7, linewidth=1.5)
            ax2.set_title('Cumulative Distribution Function (CDF)', fontsize=title_fontsize)
            ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
            ax2.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
            ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
            ax2.legend(fontsize=legend_fontsize)
            ax2.grid(True, alpha=0.3)
            
        elif enhancement_type in ["2", "3"]:  # RGB or HSV
            # Even smaller fonts for multi-channel plots
            title_fontsize = 6
            label_fontsize = 6
            tick_fontsize = 5
            legend_fontsize = 6
            
            colors = ['b', 'g', 'r'] if enhancement_type == "2" else ['purple', 'orange', 'brown']
            channels = ['blue', 'green', 'red'] if enhancement_type == "2" else ['hue', 'saturation', 'value']
            
            for i, channel in enumerate(channels):
                ax1 = fig.add_subplot(2, 3, i+1)
                ax1.plot(hist_data[f'pdf_original_{channel}'], colors[i], 
                        label=f'Original PDF', alpha=0.7, linewidth=1.2)
                ax1.plot(hist_data[f'pdf_equalized_{channel}'], 'k', 
                        label=f'Equalized PDF', alpha=0.7, linewidth=1.0)
                ax1.set_title(f'{channel.title()} Channel PDF', fontsize=title_fontsize)
                ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
                ax1.set_ylabel('Probability', fontsize=label_fontsize)
                ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
                ax1.legend(fontsize=legend_fontsize)
                ax1.grid(True, alpha=0.3)
                
                ax2 = fig.add_subplot(2, 3, i+4)
                ax2.plot(hist_data[f'cdf_original_{channel}'], colors[i], 
                        label=f'Original CDF', alpha=0.7, linewidth=1.2)
                ax2.plot(hist_data[f'cdf_equalized_{channel}'], 'k', 
                        label=f'Equalized CDF', alpha=0.7, linewidth=1.0)
                ax2.set_title(f'{channel.title()} Channel CDF', fontsize=title_fontsize)
                ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
                ax2.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
                ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
                ax2.legend(fontsize=legend_fontsize)
                ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    def create_matching_pdf_cdf_plot(self, hist_data):
        """Create PDF and CDF plots for histogram matching"""
        fig = plt.Figure(figsize=(12, 5))
        
        # Set smaller font sizes
        title_fontsize = 8
        label_fontsize = 7
        tick_fontsize = 6
        legend_fontsize = 7
        
        ax1 = fig.add_subplot(121)
        ax1.plot(hist_data['pdf_original'], 'k', label='Original PDF', alpha=0.7, linewidth=1.5)
        ax1.plot(hist_data['pdf_equalized'], 'r', label='Matched PDF', alpha=0.7, linewidth=1.5)
        ax1.plot(hist_data['pdf_target'], 'b', label='Target PDF', alpha=0.7, linewidth=1.5, linestyle='--')
        ax1.set_title('Probability Density Function (PDF)', fontsize=title_fontsize)
        ax1.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax1.set_ylabel('Probability', fontsize=label_fontsize)
        ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax1.legend(fontsize=legend_fontsize)
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(122)
        ax2.plot(hist_data['cdf_original'], 'k', label='Original CDF', alpha=0.7, linewidth=1.5)
        ax2.plot(hist_data['cdf_equalized'], 'r', label='Matched CDF', alpha=0.7, linewidth=1.5)
        ax2.plot(hist_data['cdf_target'], 'b', label='Target CDF', alpha=0.7, linewidth=1.5, linestyle='--')
        ax2.set_title('Cumulative Distribution Function (CDF)', fontsize=title_fontsize)
        ax2.set_xlabel('Pixel Intensity', fontsize=label_fontsize)
        ax2.set_ylabel('Cumulative Probability', fontsize=label_fontsize)
        ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        ax2.legend(fontsize=legend_fontsize)
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    def _replace_image(self, new_image):
        if self.selected_image_index is not None:
            self.image_objects[self.selected_image_index] = new_image
            img_tk = ImageTk.PhotoImage(new_image)
            self.image_tk_objects[self.selected_image_index] = img_tk
            self.canvas.itemconfig(self.selected_image_item, image=img_tk)
            
    #  Get current canvas dimensions

    def save_collage(self):
        self.disable_paint()
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
                
            # Create blank RGBA image

            collage = np.full((canvas_height, canvas_width, 4), 255, dtype=np.uint8)
            # Composite background image if exists

            if self.bg_image:
                bg_resized = self.bg_image.resize((canvas_width, canvas_height), Image.LANCZOS)
                bg_array = np.array(bg_resized)
                if bg_array.shape[2] == 3:
                    bg_array = np.dstack((bg_array, np.full((bg_array.shape[0], bg_array.shape[1]), 255)))
                collage = cv2.addWeighted(collage, 0, bg_array, 1, 0)
            elif self.bg_color:
                bg_color = self.hex_to_bgr(self.bg_color)
                collage[:, :] = list(bg_color) + [255]
            else:
                collage[:, :] = [255, 255, 255, 255]
            
            # Get image position and convert to array

            for item, img in zip(self.image_items, self.image_objects):
                x, y = map(int, self.canvas.coords(item))
                img_array = np.array(img)
                if img_array.shape[2] == 3:
                    img_array = np.dstack((img_array, np.full((img_array.shape[0], img_array.shape[1]), 255)))
                img_height, img_width = img_array.shape[:2]
                
                if x + img_width > canvas_width:
                    img_width = canvas_width - x
                    img_array = img_array[:, :img_width]
                if y + img_height > canvas_height:
                    img_height = canvas_height - y
                    img_array = img_array[:img_height, :]
                
                if img_width <= 0 or img_height <= 0:
                    continue
                # Alpha compositing: blend images with transparency

                alpha_s = img_array[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s
                
                for c in range(0, 3):
                    collage[y:y+img_height, x:x+img_width, c] = (
                        alpha_s * img_array[:, :, c] +
                        alpha_l * collage[y:y+img_height, x:x+img_width, c]
                    )
            
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ],
                title="Save Collage As"
            )
            
            if save_path:
                collage_bgr = cv2.cvtColor(collage, cv2.COLOR_RGBA2BGR)
                
                if save_path.lower().endswith('.jpg') or save_path.lower().endswith('.jpeg'):
                    cv2.imwrite(save_path, collage_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                else:
                    cv2.imwrite(save_path, collage_bgr)
                
                self.update_status(f"Collage saved successfully: {save_path}")
                messagebox.showinfo("Success", f"Collage saved to:\n{save_path}")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save collage: {str(e)}")

    def hex_to_bgr(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCollageMaker(root)
    root.mainloop()
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
  
    
