import cv2
import pytesseract
import sys
import os
import re
import numpy as np

# Modo Debug (coloque True se quiser ver as imagens processadas na sua pasta)
DEBUG_MODE = False

def preprocess_image_for_tibia(image_source):
    if isinstance(image_source, str):
        img = cv2.imread(image_source)
        if img is None:
            raise FileNotFoundError(f"Imagem '{image_source}' não encontrada.")
    else:
        img = image_source
        
    h, w = img.shape[:2]
    
    # Smart Crop: Se a imagem for muito larga (tela inteira), recorta só o miolo.
    if w >= 1600:
        img = img[int(h*0.20):int(h*0.80), int(w*0.24):int(w*0.76)]
        
    # O Segredo do Texto Colorido (Vermelho/Verde):
    gray = np.max(img, axis=2).astype(np.uint8)
    
    # Para fontes pixeladas sem anti-aliasing (como o Tibia)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    
    # Threshold de Otsu
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    if DEBUG_MODE:
        if isinstance(image_source, str):
            cv2.imwrite(f"debug_processed_{os.path.basename(image_source)}", thresh)
        else:
            cv2.imwrite("debug_processed_auto.png", thresh)
        
    return thresh

def extract_text(image_source):
    # Agora retorna os dados espaciais (coordenadas) em vez de apenas uma string plana
    processed_img = preprocess_image_for_tibia(image_source)
    # PSM 6 (Assume a single uniform block of text) força o Tesseract a ler a tela 
    # como uma "planilha" tabular, parando de quebrar números no meio da vírgula!
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(processed_img, config=custom_config, output_type=pytesseract.Output.DICT)
    return data, processed_img.shape

def parse_market_prices(ocr_result):
    data, img_shape = ocr_result
    h, w = img_shape
    
    # 1. Encontra a linha "Buy Offers" para dividir o que é Compra do que é Venda
    buy_y = h
    for i, text in enumerate(data['text']):
        if 'Buy' in text or 'Offers' in text:
            if h * 0.4 < data['top'][i] < h * 0.7:
                buy_y = data['top'][i]
                break
                
    # 2. Encontra a linha do cabeçalho "Piece Price" para ignorar lixo no topo
    piece_price_y = 0
    for i, text in enumerate(data['text']):
        if 'Piece' in text or 'Price' in text:
            if data['top'][i] < h * 0.4:  # Cabeçalho do topo (Sell Offers)
                piece_price_y = data['top'][i]
                break
                
    sell_prices = []
    buy_prices = []

    min_x = w * 0.58
    max_x = w * 0.76

    for i, text in enumerate(data['text']):
        text = text.strip().replace(',', '')
        left = data['left'][i]
        top = data['top'][i]
        
        # Só pega o que está dentro da coluna X E abaixo do cabeçalho Y!
        if min_x < left < max_x and top > piece_price_y + 15:
            if text.isdigit():
                val = int(text)
                if val > 0:
                    if top < buy_y:
                        sell_prices.append(val)
                    else:
                        buy_prices.append(val)
                        
    instant_price = sell_prices[0] if sell_prices else 0
    order_price = buy_prices[0] if buy_prices else 0
    
    return instant_price, order_price

if __name__ == "__main__":
    img_path = "image.png" if len(sys.argv) == 1 else sys.argv[1]
    
    if not os.path.exists(img_path):
        print(f"❌ Imagem não encontrada: {img_path}")
        sys.exit(1)
        
    print(f"Lendo a imagem: {img_path}...")
    try:
        texto = extract_text(img_path)
        instant, order = parse_market_prices(texto)
        
        print("\n=== Resultado da Leitura Automática ===")
        print(f"💰 Compra Instantânea (Sell Offer): {instant:,} gp")
        print(f"📉 Pedido de Compra (Buy Offer):   {order:,} gp")
        print("=======================================\n")
        
    except Exception as e:
        print(f"Erro: {e}")
