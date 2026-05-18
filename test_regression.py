import os
from scanner import extract_text, parse_market_prices

# Aqui você cadastra suas imagens de teste e o que o OCR *DEVE* ler nelas
# Formato: ("caminho_da_imagem", Sell_Esperado, Buy_Esperado)
TEST_CASES = [
    ("tests/vampire_teeth.png", 853, 648),
    ("tests/bloody_pincer.png", 22000, 15071),
]

def run_tests():
    print("🧪 Iniciando Testes de Regressão do Tibia Scanner OCR...\n")
    
    passed = 0
    failed = 0
    
    for img_path, exp_sell, exp_buy in TEST_CASES:
        print(f"👉 Testando: {os.path.basename(img_path)}")
        if not os.path.exists(img_path):
            print(f"   ❌ ARQUIVO NÃO ENCONTRADO! Pulei o teste.\n")
            failed += 1
            continue
            
        try:
            # Roda o nosso OCR na imagem de teste
            ocr_result = extract_text(img_path)
            sell, buy = parse_market_prices(ocr_result)
            
            # Compara se o robô leu exatamente o que a gente mandou
            if sell == exp_sell and buy == exp_buy:
                print(f"   ✅ PASSOU! (Sell: {sell}, Buy: {buy})\n")
                passed += 1
            else:
                print(f"   ❌ FALHOU!")
                print(f"      Esperado: Sell: {exp_sell}, Buy: {exp_buy}")
                print(f"      O Robô Leu: Sell: {sell}, Buy: {buy}\n")
                failed += 1
        except Exception as e:
            print(f"   ❌ ERRO DE EXECUÇÃO: {e}\n")
            failed += 1
            
    print("📊 Resumo dos Testes:")
    print(f"   Total de Casos: {len(TEST_CASES)}")
    print(f"   ✅ Sucesso: {passed}")
    print(f"   ❌ Falhas:  {failed}")
    
    if failed > 0:
        print("\n⚠️  CUIDADO: Você quebrou algo no OCR! Desfaça a alteração no scanner.py")
    else:
        print("\n🚀 CÓDIGO SEGURO! Todas as otimizações funcionaram perfeitamente.")

if __name__ == "__main__":
    run_tests()
