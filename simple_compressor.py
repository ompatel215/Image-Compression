import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import os

class SimpleCompressor:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Simple Image Compressor")
        self.root.geometry("800x600")
        
        # Variables
        self.image_path = None
        self.preview_image = None
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Left panel for controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=10)
        
        # Right panel for preview
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Controls
        ttk.Label(left_frame, text="Image Controls", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Select image button
        ttk.Button(left_frame, text="Select Image", command=self.select_image, width=20).pack(pady=10)
        
        # Quality control
        quality_frame = ttk.LabelFrame(left_frame, text="Compression Quality", padding="5")
        quality_frame.pack(fill="x", pady=10)
        
        self.quality = tk.DoubleVar(value=0.8)
        ttk.Scale(quality_frame, from_=0.1, to=1.0, variable=self.quality, 
                 orient=tk.HORIZONTAL, length=200).pack(pady=5)
        self.quality_label = ttk.Label(quality_frame, text=f"Quality: {self.quality.get():.1f}")
        self.quality_label.pack()
        
        # Compress button
        ttk.Button(left_frame, text="Compress Image", command=self.compress, width=20).pack(pady=10)
        
        # Status
        self.status = ttk.Label(left_frame, text="Ready", wraplength=200)
        self.status.pack(pady=10)
        
        # Preview area
        preview_frame = ttk.LabelFrame(right_frame, text="Image Preview", padding="5")
        preview_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(preview_frame, width=500, height=500, bg='white')
        self.canvas.pack(fill="both", expand=True)
        
        # Bind quality slider update
        self.quality.trace_add("write", self.update_quality_label)
    
    def update_quality_label(self, *args):
        self.quality_label.config(text=f"Quality: {self.quality.get():.1f}")
    
    def select_image(self):
        filetypes = (('Image files', '*.jpg *.jpeg *.png'), ('All files', '*.*'))
        self.image_path = filedialog.askopenfilename(filetypes=filetypes)
        if self.image_path:
            self.status.config(text=f"Selected: {os.path.basename(self.image_path)}")
            self.display_image(self.image_path)
    
    def display_image(self, image_path):
        try:
            # Load and resize image for preview
            img = Image.open(image_path)
            img.thumbnail((500, 500))
            photo = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(250, 250, image=photo)
            self.canvas.image = photo  # Keep a reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def compress(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            self.status.config(text="Compressing...")
            self.root.update()
            
            # Load image
            img = Image.open(self.image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Simple compression: reduce quality
            quality = int(self.quality.get() * 100)
            
            # Save compressed image
            output_path = f"compressed_{os.path.basename(self.image_path)}"
            img.save(output_path, quality=quality)
            
            # Show results
            original_size = os.path.getsize(self.image_path)
            compressed_size = os.path.getsize(output_path)
            ratio = original_size / compressed_size
            
            self.status.config(
                text=f"Compression complete!\n"
                     f"Ratio: {ratio:.1f}x\n"
                     f"Original: {original_size/1024:.1f}KB\n"
                     f"Compressed: {compressed_size/1024:.1f}KB\n"
                     f"Saved as: {output_path}"
            )
            
            # Display compressed image
            self.display_image(output_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {str(e)}")
            self.status.config(text="Compression failed")

if __name__ == "__main__":
    app = SimpleCompressor()
    app.root.mainloop() 