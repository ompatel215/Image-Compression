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
        self.block_size = 8  # Size of blocks for compression
        self.threshold = tk.DoubleVar(value=0.2)  # Threshold for compression
        
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
        
        # Threshold control
        threshold_frame = ttk.LabelFrame(left_frame, text="Compression Threshold", padding="5")
        threshold_frame.pack(fill="x", pady=10)
        
        ttk.Scale(threshold_frame, from_=0.0, to=1.0, variable=self.threshold, 
                 orient=tk.HORIZONTAL, length=200).pack(pady=5)
        self.threshold_label = ttk.Label(threshold_frame, text=f"Threshold: {self.threshold.get():.2f}")
        self.threshold_label.pack()
        
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
        
        # Bind threshold slider update
        self.threshold.trace_add("write", self.update_threshold_label)
    
    def update_threshold_label(self, *args):
        self.threshold_label.config(text=f"Threshold: {self.threshold.get():.2f}")
    
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
            
            # Convert to numpy array and compress
            img_array = np.array(img)
            compressed_array = self.greedy_compress(img_array)
            
            # Convert back to PIL Image and save as PNG to avoid JPEG compression
            compressed_img = Image.fromarray(compressed_array.astype(np.uint8))
            output_path = f"compressed_{os.path.basename(self.image_path)}"
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
            compressed_img.save(output_path, format='PNG')
            
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

    def greedy_compress(self, img_array):
        height, width = img_array.shape[:2]
        compressed = np.zeros_like(img_array)
        
        # Process in blocks
        for i in range(0, height, self.block_size):
            for j in range(0, width, self.block_size):
                # Get current block
                block = img_array[i:min(i+self.block_size, height), 
                                j:min(j+self.block_size, width)]
                
                # Calculate mean and standard deviation for each color channel
                mean = np.mean(block, axis=(0, 1))
                std = np.std(block, axis=(0, 1))
                
                # Greedy decision - compress if any channel has low variation
                if np.any(std < self.threshold.get() * 255):
                    # Create a block filled with the mean values
                    mean_block = np.ones_like(block) * mean
                    compressed[i:min(i+self.block_size, height), 
                             j:min(j+self.block_size, width)] = mean_block
                else:
                    compressed[i:min(i+self.block_size, height), 
                             j:min(j+self.block_size, width)] = block
        
        return compressed

if __name__ == "__main__":
    app = SimpleCompressor()
    app.root.mainloop() 