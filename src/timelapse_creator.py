import cv2
import os
import rawpy
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, Scale, messagebox
from PIL import Image, ImageTk
import threading
from datetime import datetime

class TimeLapseCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Time Lapse Creator")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.image_files = []
        self.fps = 24
        self.output_size = "Original"
        self.is_processing = False
        
        # Available output sizes
        self.size_options = [
            "Original", "4K (3840x2160)", "1080p (1920x1080)", 
            "720p (1280x720)", "480p (854x480)"
        ]
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_gui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure styles for the GUI"""
        style = ttk.Style()
        style.configure('TButton', padding=5, font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        
    def setup_gui(self):
        """Setup all GUI elements"""
        # File selection section
        self.file_frame = ttk.LabelFrame(self.main_frame, text="File Selection", padding="5")
        self.file_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.upload_btn = ttk.Button(
            self.file_frame, 
            text="Upload Photos", 
            command=self.upload_photos
        )
        self.upload_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.file_count_label = ttk.Label(self.file_frame, text="No files selected")
        self.file_count_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Settings section
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="5")
        self.settings_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        
        # FPS settings
        ttk.Label(self.settings_frame, text="Frame Rate (FPS):").grid(row=0, column=0, padx=5, pady=5)
        self.fps_slider = Scale(
            self.settings_frame, 
            from_=1, to=60, 
            orient=tk.HORIZONTAL, 
            length=200,
            command=self.update_fps
        )
        self.fps_slider.set(24)
        self.fps_slider.grid(row=0, column=1, padx=5, pady=5)
        
        # Output size settings
        ttk.Label(self.settings_frame, text="Output Size:").grid(row=1, column=0, padx=5, pady=5)
        self.size_var = tk.StringVar(value="Original")
        self.size_dropdown = ttk.Combobox(
            self.settings_frame,
            textvariable=self.size_var,
            values=self.size_options,
            state="readonly"
        )
        self.size_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # Create button
        self.create_btn = ttk.Button(
            self.main_frame,
            text="Create Time Lapse",
            command=self.start_timelapse_thread
        )
        self.create_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Progress section
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding="5")
        self.progress_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress_bar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, padx=5, pady=5)
        
    def upload_photos(self):
        """Handle photo upload"""
        self.image_files = filedialog.askopenfilenames(
            title="Select Photos",
            filetypes=[
                ("All supported formats", "*.jpg *.jpeg *.png *.arw *.raw *.cr2 *.nef *.dng"),
                ("RAW files", "*.arw *.raw *.cr2 *.nef *.dng"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png")
            ]
        )
        
        if self.image_files:
            self.file_count_label.config(text=f"Selected {len(self.image_files)} photos")
            # Sort files by name to ensure correct sequence
            self.image_files = sorted(self.image_files)
    
    def update_fps(self, value):
        """Update FPS value"""
        self.fps = int(value)
    
    def get_output_dimensions(self, img_shape):
        """Calculate output dimensions based on selected size"""
        size_map = {
            "4K (3840x2160)": (3840, 2160),
            "1080p (1920x1080)": (1920, 1080),
            "720p (1280x720)": (1280, 720),
            "480p (854x480)": (854, 480),
            "Original": img_shape[:2][::-1]  # Original size (width, height)
        }
        return size_map[self.size_var.get()]
    
    def read_image(self, image_path):
        """Read and process image files (both RAW and regular formats)"""
        try:
            file_extension = os.path.splitext(image_path)[1].lower()
            
            if file_extension in ['.arw', '.raw', '.cr2', '.nef', '.dng']:
                with rawpy.imread(image_path) as raw:
                    rgb = raw.postprocess(use_camera_wb=True)
                    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            else:
                return cv2.imread(image_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file {image_path}: {str(e)}")
            return None
    
    def start_timelapse_thread(self):
        """Start timelapse creation in a separate thread"""
        if not self.image_files:
            messagebox.showwarning("Warning", "Please upload photos first!")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Already processing!")
            return
            
        thread = threading.Thread(target=self.create_timelapse)
        thread.start()
    
    def create_timelapse(self):
        """Create the timelapse video"""
        self.is_processing = True
        self.create_btn.config(state='disabled')
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")]
        )
        
        if not output_path:
            self.is_processing = False
            self.create_btn.config(state='normal')
            return
            
        try:
            # Get first image dimensions
            first_img = self.read_image(self.image_files[0])
            if first_img is None:
                raise Exception("Could not read first image")
                
            # Get output dimensions
            output_width, output_height = self.get_output_dimensions(first_img.shape)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                output_path, 
                fourcc, 
                self.fps, 
                (output_width, output_height)
            )
            
            total_images = len(self.image_files)
            self.progress_bar["maximum"] = total_images
            
            for i, image_path in enumerate(self.image_files, 1):
                self.status_label.config(text=f"Processing image {i}/{total_images}")
                self.progress_bar["value"] = i
                self.root.update()
                
                img = self.read_image(image_path)
                if img is not None:
                    # Resize image if needed
                    if img.shape[1] != output_width or img.shape[0] != output_height:
                        img = cv2.resize(img, (output_width, output_height))
                    out.write(img)
            
            out.release()
            self.status_label.config(text="Time lapse created successfully!")
            messagebox.showinfo("Success", "Time lapse created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Error occurred during processing")
            
        finally:
            self.is_processing = False
            self.create_btn.config(state='normal')
            self.progress_bar["value"] = 0

def main():
    root = tk.Tk()
    app = TimeLapseCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main() 