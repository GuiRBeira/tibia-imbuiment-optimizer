# Tibia Imbuement Optimizer ⚔️

O **Tibia Imbuement Optimizer** é uma ferramenta definitiva para jogadores de Tibia calcularem os custos de Imbuements (Basic, Intricate e Powerful). Ele compara o custo de comprar os materiais brutos diretamente no Market vs. o custo de comprar Gold Tokens e trocá-los pelos materiais.

Mais do que uma calculadora, este projeto conta com um **Banco de Dados Histórico** (SQLite) e um **Motor de Visão Computacional (OCR)** capaz de extrair os preços automaticamente direto da sua tela do jogo, driblando até mesmo as restrições de segurança do Linux Wayland!

## 🚀 Funcionalidades

- **Calculadora de Imbuements**: Determina automaticamente a forma mais barata de fazer suas imbuements (Gold Token vs Materiais).
- **Auto-Scan de Mercado (OCR)**: Inteligência Espacial que lê pixels da tela do Tibia, extraindo preços com altíssima precisão sem você digitar nada.
- **Wayland Ninja Watchdog**: Suporte nativo e indetectável para Ubuntu/Wayland. Basta apertar *Print Screen* no jogo e o programa capta a imagem em tempo real.
- **Histórico e Gráficos**: Salva médias diárias num banco de dados e plota gráficos de tendência dos preços no próprio terminal (ex: variação do Gold Token nos últimos 7 dias).
- **Testes de Regressão**: Suíte automatizada para garantir que o motor de visão computacional não seja quebrado em futuras atualizações.

## 🛠️ Tecnologias Utilizadas
- **Python 3**
- **OpenCV & Tesseract OCR** (Engenharia de Imagem, Spatial Lógica, Max RGB Channel)
- **Rich** (Interfaces maravilhosas no terminal)
- **SQLite3** (Armazenamento histórico)

## 🎮 Como Usar

1. Clone o repositório e ative a venv:
   ```bash
   source venv/bin/activate
   ```
2. Instale as dependências (se não tiver):
   ```bash
   pip install -r requirements.txt
   sudo apt install tesseract-ocr
   ```
3. Rode a aplicação principal:
   ```bash
   python main.py
   ```
4. Ao ser questionado, aceite a "Mágica do Auto-Scan".
5. Abra o Tibia, pesquise o item pedido no Market, e aperte o botão de **Print Screen (PrtScn)** do seu teclado. O terminal lerá os preços instantaneamente!

## 🧪 Testes

Para garantir que o OCR está saudável, execute a nossa bateria de testes de regressão automatizados:
```bash
python test_regression.py
```

## 🗺️ TODO (Roadmap de Evolução)
O projeto chegou a uma maturidade incrível no terminal, mas o céu é o limite. Aqui estão algumas ideias para a evolução natural:

- [ ] **Filtro Sob Demanda**: Permitir que o usuário selecione quais imbuements específicos ele deseja calcular naquela sessão, evitando escanear dezenas de materiais desnecessários.
- [ ] **Limpeza Automática (Garbage Collector)**: Apagar o arquivo nativo de Print Screen do Ubuntu assim que o OCR terminar de ler, para não lotar o HD do usuário em ambiente de produção.
- [ ] **Interface Gráfica (Web/Electron)**: Mudar do Terminal para um Dashboard Bonito em React ou PyQt.
- [ ] **Multi-World Arbitrage**: Comparar os preços do seu banco de dados entre servidores diferentes para buscar oportunidades de Arbitragem.
- [ ] **Alarme de Preços (Webhook)**: Ficar rodando em segundo plano e apitar/mandar mensagem no Discord se um Gold Token aparecer abaixo do preço alvo.
- [ ] **Paging Automático**: Integrar com a biblioteca `pyautogui` para simular o clique na seta "Next Page" do Tibia Market e ler o histórico completo de transações em vez de só o Top 10.
- [ ] **Cloud Sync**: Sincronizar o `prices.db` na nuvem (Supabase/Firebase) para guildas compartilharem a mesma base de inteligência do Market.

### 🧠 Regras de Negócio Avançadas (Wall Street Mode)
- [ ] **Market Depth (Liquidez)**: Ler não só o preço, mas também a coluna "Amount", somando matematicamente o livro de ofertas para encontrar o custo médio real (evitando ilusões de itens com volume = 1).
- [ ] **Integração de Stash (Inventário)**: Abater do cálculo do OCR a quantidade de materiais que o jogador já tem guardados no DP.
- [ ] **Market Creation Fee**: Embutir automaticamente a taxa percentual do Tibia Market no cálculo final ao simular a viabilidade de abrir centenas de Buy Offers (Pedidos de Compra).
