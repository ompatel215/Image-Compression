# Import necessary libraries
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # PIL for image processing
import numpy as np  # NumPy for numerical operations
import os  # OS for file operations
import rawpy  # For handling RAW image files

class SimpleCompressor:
    def __init__(self):
        """
        Initialize the SimpleCompressor application.
        Sets up the main window and initializes variables.
        """
        # Create main window
        self.root = tk.Tk()
        self.root.title("Simple Image Compressor")
        self.root.geometry("800x600")
        
        # Variables
        self.image_path = None  # Path to the currently selected image
        self.preview_image = None  # Reference to the preview image
        self.block_size = 8  # Size of blocks for compression (8x8 pixels)
        self.threshold = tk.DoubleVar(value=0.2)  # Compression threshold (0.0 to 1.0)
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """
        Creates the user interface with all necessary controls and displays.
        """
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Left panel for controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=10)
        
        # Right panel for preview
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Controls section
        ttk.Label(left_frame, text="Image Controls", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Button to select an image
        ttk.Button(left_frame, text="Select Image", command=self.select_image, width=20).pack(pady=10)
        
        # Threshold control slider
        threshold_frame = ttk.LabelFrame(left_frame, text="Compression Threshold", padding="5")
        threshold_frame.pack(fill="x", pady=10)
        
        # Slider for adjusting compression threshold (0.0 to 1.0)
        ttk.Scale(threshold_frame, from_=0.0, to=1.0, variable=self.threshold, 
                 orient=tk.HORIZONTAL, length=200).pack(pady=5)
        self.threshold_label = ttk.Label(threshold_frame, text=f"Threshold: {self.threshold.get():.2f}")
        self.threshold_label.pack()
        
        # Button to start compression
        ttk.Button(left_frame, text="Compress Image", command=self.compress, width=20).pack(pady=10)
        
        # Status display
        self.status = ttk.Label(left_frame, text="Ready", wraplength=200)
        self.status.pack(pady=10)
        
        # Preview area for images
        preview_frame = ttk.LabelFrame(right_frame, text="Image Preview", padding="5")
        preview_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(preview_frame, width=500, height=500, bg='white')
        self.canvas.pack(fill="both", expand=True)
        
        # Bind threshold slider update to update the label
        self.threshold.trace_add("write", self.update_threshold_label)
    
    def update_threshold_label(self, *args):
        """
        Updates the threshold label when the slider is moved.
        """
        self.threshold_label.config(text=f"Threshold: {self.threshold.get():.2f}")
    
    def select_image(self):
        """
        Opens a file dialog to select an image file.
        Updates the preview when an image is selected.
        """
        filetypes = (('Image files', '*.jpg *.jpeg *.png *.NEF'), ('All files', '*.*'))
        self.image_path = filedialog.askopenfilename(filetypes=filetypes)
        if self.image_path:
            self.status.config(text=f"Selected: {os.path.basename(self.image_path)}")
            self.display_image(self.image_path)
    
    def load_image(self, image_path):
        """
        Loads an image file, handling both regular images and RAW (NEF) files.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object
        """
        try:
            if image_path.lower().endswith('.nef'):
                # Handle NEF files using rawpy
                with rawpy.imread(image_path) as raw:
                    # Convert RAW to RGB
                    rgb = raw.postprocess()
                    # Convert to PIL Image
                    return Image.fromarray(rgb)
            else:
                # Handle regular image files
                img = Image.open(image_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return img
        except Exception as e:
            raise Exception(f"Failed to load image: {str(e)}")
    
    def display_image(self, image_path):
        """
        Displays the selected or compressed image in the preview area.
        """
        try:
            # Load image (handles both regular and NEF files)
            img = self.load_image(image_path)
            img.thumbnail((500, 500))  # Resize to fit preview area
            photo = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(250, 250, image=photo)
            self.canvas.image = photo  # Keep a reference to prevent garbage collection
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def greedy_compress(self, img_array):
        """
        Compresses the image using a greedy block-based algorithm.
        
        Args:
            img_array: numpy array of the image to compress
            
        Returns:
            compressed: numpy array of the compressed image
        """
        height, width = img_array.shape[:2]
        compressed = np.zeros_like(img_array)
        
        # Process image in blocks of size block_size x block_size
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
                    # Keep original block if variation is high
                    compressed[i:min(i+self.block_size, height), 
                             j:min(j+self.block_size, width)] = block
        
        return compressed
    
    def compress(self):
        """
        Main compression function that handles the entire compression process.
        """
        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            self.status.config(text="Compressing...")
            self.root.update()
            
            # Load image (handles both regular and NEF files)
            img = self.load_image(self.image_path)
            
            # Convert to numpy array and compress
            img_array = np.array(img)
            compressed_array = self.greedy_compress(img_array)
            
            # Convert back to PIL Image and save as PNG
            compressed_img = Image.fromarray(compressed_array.astype(np.uint8))
            output_path = f"compressed_{os.path.basename(self.image_path)}"
            if output_path.lower().endswith(('.jpg', '.jpeg', '.nef')):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
            compressed_img.save(output_path, format='PNG')
            
            # Calculate and display compression results
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
    # Create and run the application
    app = SimpleCompressor()
    app.root.mainloop() 