import tkinter as tk
import mss

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        
        # Obter o tamanho total de todos os monitores somados para cobrir tudo
        with mss.mss() as sct:
            mon = sct.monitors[0]
            self.width = mon["width"]
            self.height = mon["height"]
            self.left = mon["left"]
            self.top = mon["top"]

        # Configurar a janela para ser sem bordas e semi-transparente
        self.root.geometry(f"{self.width}x{self.height}+{self.left}+{self.top}")
        self.root.overrideredirect(True) # Remove barra de título
        self.root.attributes('-alpha', 0.3) # Transparência 30%
        self.root.attributes('-topmost', True) # Sempre no topo
        self.root.configure(cursor="cross")
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Pressione ESC para cancelar
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bbox = None

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # Cria um retângulo que vai sendo desenhado na tela
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='cyan', width=2, fill="white")

    def on_drag(self, event):
        curX, curY = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        
        # O mss precisa do top e left absolutos, então somamos o offset do monitor 0
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
