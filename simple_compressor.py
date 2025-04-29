import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import os
import rawpy

class SimpleCompressor:
    def __init__(self):
        # create the main window
        self.root = tk.Tk()
        self.root.title("Simple Image Compressor")
        self.root.geometry("800x600")
        
        # variables
        self.image_path = None  # path to current image
        self.preview_image = None  # preview image
        self.block_size = 8  # compression block size = 8x8
        self.threshold = tk.DoubleVar(value=0.2)  # compression threshold
        
        # create UI
        self.create_ui()
    
    def create_ui(self):
        # create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # left panel
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=10)
        
        # right panel
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # controls
        ttk.Label(left_frame, text="Image Controls", font=("Arial", 12, "bold")).pack(pady=10)
        
        # image select button
        ttk.Button(left_frame, text="Select Image", command=self.select_image, width=20).pack(pady=10)
        
        # threshold slider
        threshold_frame = ttk.LabelFrame(left_frame, text="Compression Threshold", padding="5")
        threshold_frame.pack(fill="x", pady=10)
        
        # compression threshold slider
        ttk.Scale(threshold_frame, from_=0.0, to=1.0, variable=self.threshold, 
                 orient=tk.HORIZONTAL, length=200).pack(pady=5)
        self.threshold_label = ttk.Label(threshold_frame, text=f"Threshold: {self.threshold.get():.2f}")
        self.threshold_label.pack()
        
        # start compression button
        ttk.Button(left_frame, text="Compress Image", command=self.compress, width=20).pack(pady=10)
        
        # status display
        self.status = ttk.Label(left_frame, text="Ready", wraplength=200)
        self.status.pack(pady=10)
        
        # image preview
        preview_frame = ttk.LabelFrame(right_frame, text="Image Preview", padding="5")
        preview_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(preview_frame, width=500, height=500, bg='white')
        self.canvas.pack(fill="both", expand=True)
        
        self.threshold.trace_add("write", self.update_threshold_label)
    
    def update_threshold_label(self, *args):

        self.threshold_label.config(text=f"Threshold: {self.threshold.get():.2f}")
    
    def select_image(self):

        filetypes = (('Image files', '*.jpg *.jpeg *.png *.NEF'), ('All files', '*.*'))
        self.image_path = filedialog.askopenfilename(filetypes=filetypes)
        if self.image_path:
            self.status.config(text=f"Selected: {os.path.basename(self.image_path)}")
            self.display_image(self.image_path)
    
    def load_image(self, image_path):

        try:
            if image_path.lower().endswith('.nef'):
                # handle NEF files using rawpy
                with rawpy.imread(image_path) as raw:
                    # convert RAW to RGB
                    rgb = raw.postprocess()
                    # convert to pil image
                    return Image.fromarray(rgb)
            else:
                # handle regular image files
                img = Image.open(image_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return img
        except Exception as e:
            raise Exception(f"Failed to load image: {str(e)}")
    
    def display_image(self, image_path):

        try:
            # load image
            img = self.load_image(image_path)
            img.thumbnail((500, 500))  # resize to fit preview area
            photo = ImageTk.PhotoImage(img)
            
            # update canvas
            self.canvas.delete("all")
            self.canvas.create_image(250, 250, image=photo)
            self.canvas.image = photo  # keep a reference to prevent garbage collection
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def greedy_compress(self, img_array):

        height, width = img_array.shape[:2]
        compressed = np.zeros_like(img_array)
        
        # process image in blocks of size block_size x block_size
        for i in range(0, height, self.block_size):
            for j in range(0, width, self.block_size):
                # get current block
                block = img_array[i:min(i+self.block_size, height), 
                                j:min(j+self.block_size, width)]
                
                # calculate mean and standard deviation for each color channel
                mean = np.mean(block, axis=(0, 1))
                std = np.std(block, axis=(0, 1))
                
                # greedy decision - compress if any channel has low variation
                if np.any(std < self.threshold.get() * 255):
                    # create a block filled with the mean values
                    mean_block = np.ones_like(block) * mean
                    compressed[i:min(i+self.block_size, height), 
                             j:min(j+self.block_size, width)] = mean_block
                else:
                    # keep original block if variation is high
                    compressed[i:min(i+self.block_size, height), 
                             j:min(j+self.block_size, width)] = block
        
        return compressed
    
    def compress(self):

        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            self.status.config(text="Compressing...")
            self.root.update()
            
            # load image (handles both regular and NEF files)
            img = self.load_image(self.image_path)
            
            # convert to numpy array and compress
            img_array = np.array(img)
            compressed_array = self.greedy_compress(img_array)
            
            # convert back to PIL Image and save as PNG
            compressed_img = Image.fromarray(compressed_array.astype(np.uint8))
            output_path = f"compressed_{os.path.basename(self.image_path)}"
            if output_path.lower().endswith(('.jpg', '.jpeg', '.nef')):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
            compressed_img.save(output_path, format='PNG')
            
            # calculate and display compression results
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
            
            # display compressed image
            self.display_image(output_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {str(e)}")
            self.status.config(text="Compression failed")

if __name__ == "__main__":
    app = SimpleCompressor()
    app.root.mainloop() 