import cv2
import pytesseract
import sys
import os
import re
import numpy as np

def preprocess_image_for_tibia(image_source):
    if isinstance(image_source, str):
        img = cv2.imread(image_source)
        if img is None:
            raise FileNotFoundError(f"Imagem '{image_source}' não encontrada.")
    else:
        img = image_source
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Para fontes pixeladas sem anti-aliasing (como o Tibia), INTER_LINEAR ou NEAREST
    # costumam evitar distorções que transformam "3" em "5".
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    
    # Threshold de Otsu para calcular o melhor ponto de corte automaticamente
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    if isinstance(image_source, str):
        cv2.imwrite(f"debug_processed_{os.path.basename(image_source)}", thresh)
    else:
        cv2.imwrite("debug_processed_auto.png", thresh)
        
    return thresh

def extract_text(image_source):
    processed_img = preprocess_image_for_tibia(image_source)
    # psm 6 ou 11. Vamos tentar o 6 (bloco único) ou manter 11
    custom_config = r'--oem 3 --psm 11'
    text = pytesseract.image_to_string(processed_img, config=custom_config)
    return text

def parse_market_prices(text):
    # Limpa as datas e horários (ex: 2026-06-16, 21:50) para que o ano 
    # não seja lido acidentalmente como um preço de 2026 gps!
    text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)
    text = re.sub(r'\d{2}[:-]?\d{2}[:-]?\d{2}', '', text)
    
    # Divide o texto na palavra "Buy Offers" (ou algo parecido)
    parts = re.split(r'Buy Offers', text, flags=re.IGNORECASE)
    
    sell_text = parts[0]
    buy_text = parts[1] if len(parts) > 1 else ""
    
    # Regex para achar números (com ou sem vírgula), ignorando datas
    # Ex: 50,000 ou 50000
    pattern = re.compile(r'\b(\d{1,3}(?:,\d{3})+|\d{3,})\b')
    
    # Busca todos os números grandes (> 100) no bloco de Sell Offers
    sell_matches = pattern.findall(sell_text)
    sell_prices = [int(m.replace(',', '')) for m in sell_matches]
    
    # Busca todos os números grandes (> 100) no bloco de Buy Offers
    buy_matches = pattern.findall(buy_text)
    buy_prices_raw = [int(m.replace(',', '')) for m in buy_matches]
    
    instant_price = sell_prices[0] if sell_prices else 0
    
    # Filtro de Ouro do Tibia Market:
    # Um Pedido de Compra (Buy Offer) NUNCA é maior que a Compra Instantânea (Sell Offer).
    # Se o Tesseract ler um "Total Price" gigantesco antes do "Piece Price", a gente ignora ele!
    valid_buy_prices = []
    if instant_price > 0:
        valid_buy_prices = [p for p in buy_prices_raw if p <= instant_price]
    else:
        # Se por acaso o item não tiver Sell Offers, pegamos o primeiro número 
        # que não seja absurdamente alto (> 100k para um material normal).
        # (Isso é um fallback caso o market esteja vazio)
        valid_buy_prices = [p for p in buy_prices_raw if p < 100000]
        
    order_price = valid_buy_prices[0] if valid_buy_prices else (buy_prices_raw[0] if buy_prices_raw else 0)
    
    return instant_price, order_price

if __name__ == "__main__":
    img_path = "market.png" if len(sys.argv) == 1 else sys.argv[1]
    
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
