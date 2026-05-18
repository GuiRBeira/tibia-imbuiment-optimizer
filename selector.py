import tkinter as tk
from PIL import Image, ImageTk
import mss

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        
        # Tirar print de todas as telas juntas e "congelar"
        with mss.MSS() as sct:
            mon = sct.monitors[0]
            self.width = mon["width"]
            self.height = mon["height"]
            self.left = mon["left"]
            self.top = mon["top"]
            sct_img = sct.grab(mon)
            # Converter a imagem do MSS (BGRA) para imagem do Pillow (RGB)
            self.pil_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        self.root.geometry(f"{self.width}x{self.height}+{self.left}+{self.top}")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(cursor="cross")
        
        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Coloca a print screen da tela como fundo (Fica 100% opaco e não depende do OS)
        self.tk_img = ImageTk.PhotoImage(self.pil_img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        
        # Escurecer levemente a imagem para dar destaque à seleção
        self.overlay = self.canvas.create_rectangle(0, 0, self.width, self.height, fill="black", stipple="gray50", outline="")
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bbox = None

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='cyan', width=2)

    def on_drag(self, event):
        curX, curY = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        
        self.bbox = {
            "top": self.top + y1,
            "left": self.left + x1,
            "width": x2 - x1,
            "height": y2 - y1
        }
        self.root.destroy()

def select_region():
    selector = RegionSelector()
    selector.root.mainloop()
    return selector.bbox

if __name__ == "__main__":
    print("A tela ficará escura. Clique e arraste para selecionar uma área.")
    bbox = select_region()
    print("Região selecionada para o MSS:", bbox)
