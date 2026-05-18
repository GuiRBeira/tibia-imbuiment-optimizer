import os
import time
import glob
import cv2
from scanner import extract_text, parse_market_prices

def get_latest_screenshot(folder):
    files = glob.glob(os.path.join(folder, "*.png"))
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def test_screen_capture():
    print("=== Teste Isolado de Captura via Print Screen (Wayland Ninja) ===")
    
    screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")
    if not os.path.exists(screenshot_dir):
        print(f"❌ Pasta {screenshot_dir} não encontrada!")
        return

    print("\n👉 Passo a passo:")
    print("Como o Ubuntu bloqueia capturas secretas, vamos usar um truque melhor ainda!")
    print("1. Coloque o Tibia na tela e abra o Market.")
    print("2. Apenas pressione a tecla Print Screen (PrtScn) no teclado (ou seu atalho de print).")
    print("O script vai detectar que a foto chegou na pasta e ler na mesma hora!\n")
    
    last_file = get_latest_screenshot(screenshot_dir)
    print("👀 Vigiando a sua pasta de screenshots...", end="", flush=True)

    try:
        while True:
            current_latest = get_latest_screenshot(screenshot_dir)
            if current_latest and current_latest != last_file:
                print(f"\n\n📸 Nova imagem detectada! ({os.path.basename(current_latest)})")
                time.sleep(0.3)  # Dá um tempinho pro Ubuntu terminar de salvar o arquivo no disco
                
                print("🤖 Lendo a imagem...")
                
                # Lê a imagem
                img = cv2.imread(current_latest)
                
                # Extrai texto usando o caminho do arquivo
                texto = extract_text(current_latest)
                inst, order = parse_market_prices(texto)
                
                print("\n=== Resultado da Leitura Automática ===")
                print(f"💰 Compra Instantânea (Sell Offer): {inst:,} gp")
                print(f"📉 Pedido de Compra (Buy Offer):   {order:,} gp")
                print("=======================================\n")
                
                print("👀 Tire outra print para ler mais um (ou aperte Ctrl+C para sair)...", end="", flush=True)
                last_file = current_latest
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nSaindo do modo de vigia. Teste encerrado!")

if __name__ == "__main__":
    test_screen_capture()
