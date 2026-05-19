import sys
import os
import glob
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt, Confirm
from models import load_imbuements
from calculator import cost_by_materials, cost_by_tokens, cost_per_hour
from storage import init_db, save_prices, get_daily_average_prices, get_latest_prices
from scanner import extract_text, parse_market_prices, detect_item_name

console = Console()

def get_latest_screenshot(folder):
    files = glob.glob(os.path.join(folder, "*.png"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def auto_scan_prices(imbuements_data, world: str, clean_screenshots: bool = False, session_prices: dict = None):
    screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")
    if not os.path.exists(screenshot_dir):
        console.print(f"[bold red]❌ Pasta de Screenshots não encontrada: {screenshot_dir}[/bold red]")
        console.print("Por favor, tire uma print para que o Ubuntu crie a pasta, e reinicie o programa.")
        sys.exit(1)

    # Obter a lista de itens conhecidos
    all_items = set(["Gold Token"])
    for tiers in imbuements_data.values():
        for tier_info in tiers.values():
            for material in tier_info.materials:
                all_items.add(material.name)
    known_items = sorted(list(all_items))

    console.print("\n[bold green]🥷 Modo Auto-Scan Livre (Wayland Ninja) Ativado![/bold green]")
    console.print("Como usar:")
    console.print("  1. Abra o Tibia e pesquise o item desejado no Market.")
    console.print("  2. Aperte [bold yellow]Print Screen (PrtScn)[/bold yellow] no teclado.")
    console.print("  3. Repita para quantos itens quiser e em qualquer ordem!")
    console.print("  4. Quando terminar de escanear, pressione [bold red]Ctrl+C[/bold red] no terminal para calcular.\n")
    
    last_file = get_latest_screenshot(screenshot_dir)
    console.print("👀 [cyan]Aguardando prints (pressione Ctrl+C para encerrar)...[/cyan]")
    
    updated_items = set()
    
    try:
        while True:
            current_latest = get_latest_screenshot(screenshot_dir)
            if current_latest and current_latest != last_file:
                time.sleep(0.3)  # tempo para salvar o arquivo
                
                ocr_result = extract_text(current_latest)
                item_detected = detect_item_name(ocr_result, known_items)
                
                if item_detected:
                    inst, ord = parse_market_prices(ocr_result)
                    session_prices[item_detected] = (inst, ord)
                    updated_items.add(item_detected)
                    console.print(f"   [green]✅ Lido: [bold]{item_detected}[/bold] -> Inst. {inst:,} gp | Pedido {ord:,} gp[/green]\n")
                else:
                    console.print("   [yellow]⚠️ Imagem detectada, mas não consegui identificar qual item de Imbuement é este.[/yellow]\n")
                    
                if clean_screenshots:
                    try:
                        os.remove(current_latest)
                        current_latest = get_latest_screenshot(screenshot_dir)
                    except Exception as e:
                        console.print(f"   [dim red]⚠️ Não foi possível apagar a screenshot: {e}[/dim red]")
                        
                last_file = current_latest
            time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[bold green]🏁 Escaneamento encerrado com sucesso! Calculando otimizações...[/bold green]\n")
        
    return updated_items

def manual_update_prices(session_prices: dict, known_items: list):
    console.print("\n[bold yellow]✍️ Modo de Edição Manual[/bold yellow]")
    while True:
        table = Table(title="Preços Atuais (Selecione para Editar)")
        table.add_column("Índice", style="yellow")
        table.add_column("Item", style="cyan")
        table.add_column("Instantâneo", justify="right")
        table.add_column("Pedido de Compra", justify="right")
        
        for i, item in enumerate(known_items):
            inst, ord = session_prices[item]
            table.add_row(str(i), item, f"{inst:,} gp", f"{ord:,} gp")
            
        console.print(table)
        choice = Prompt.ask("\nDigite o número do item para editar, ou [bold red]S[/bold red] para Salvar e Calcular", default="S")
        if choice.upper() == "S":
            break
            
        try:
            idx = int(choice)
            if 0 <= idx < len(known_items):
                item = known_items[idx]
                inst = IntPrompt.ask(f"Novo preço Instantâneo para [bold cyan]{item}[/bold cyan]", default=session_prices[item][0])
                ord = IntPrompt.ask(f"Novo preço sob Pedido (Order) para [bold cyan]{item}[/bold cyan]", default=session_prices[item][1])
                session_prices[item] = (inst, ord)
                console.print(f"[green]✅ {item} atualizado![/green]\n")
            else:
                console.print("[red]Índice inválido.[/red]")
        except ValueError:
            console.print("[red]Entrada inválida. Digite um número ou 'S'.[/red]")

def print_trend_chart(world: str, item_name: str):
    data = get_daily_average_prices(world, item_name, 7)
    if not data or len(data) < 2:
        return
        
    console.print(f"\n[bold cyan]📊 Tendência de {item_name} (Últimos dias em {world})[/bold cyan]")
    inst_data = {k: v[0] for k, v in data.items()}
    max_price = max(inst_data.values())
    min_price = min(inst_data.values())
    baseline = min_price * 0.9
    
    for date_str, price in inst_data.items():
        range_val = max_price - baseline
        if range_val == 0:
            bar_len = 20
        else:
            bar_len = int(((price - baseline) / range_val) * 40)
            
        bar = "█" * max(1, bar_len)
        console.print(f"{date_str} | [green]{bar}[/green] {price:,.0f} gp (Instant)")

def main():
    console.print("[bold green]⚔️ Tibia Imbuement Optimizer - Basic / Intricate / Powerful[/bold green]")
    
    init_db()
    
    imbuements = load_imbuements("data/immy_data.json")
    world = Prompt.ask("🌍 Qual o nome do seu mundo (ex: Yonabra)", default="Unknown")
    
    # 1. Carregar lista de itens conhecidos
    all_items = set(["Gold Token"])
    for tiers in imbuements.values():
        for tier_info in tiers.values():
            for material in tier_info.materials:
                all_items.add(material.name)
    known_items = sorted(list(all_items))
    
    # 2. Carregar últimos preços do banco de dados
    db_prices = get_latest_prices(world)
    session_prices = {}
    for item in known_items:
        if item in db_prices:
            session_prices[item] = db_prices[item]
        else:
            session_prices[item] = (10000 if item == "Gold Token" else 0, 10000 if item == "Gold Token" else 0)
            
    # 3. Mostrar tabela inicial de preços carregados
    console.print(f"\n[bold green]📦 Preços mais recentes no banco de dados para {world}:[/bold green]")
    price_table = Table(show_header=True, header_style="bold magenta")
    price_table.add_column("Item", style="cyan")
    price_table.add_column("Instantâneo (Sell Offer)", justify="right")
    price_table.add_column("Pedido (Buy Offer)", justify="right")
    price_table.add_column("Status / Origem", style="dim")
    
    for item in known_items:
        inst, ord = session_prices[item]
        is_from_db = item in db_prices
        status = "Histórico (BD)" if is_from_db else "Padrão (Sem Histórico)"
        price_table.add_row(item, f"{inst:,} gp", f"{ord:,} gp", status)
        
    console.print(price_table)
    
    # 4. Oferecer opções de atualização
    updated_items = set()
    update_option = Prompt.ask(
        "\n🔄 Deseja atualizar os preços?",
        choices=["auto", "manual", "no"],
        default="auto"
    )
    
    if update_option == "auto":
        clean_screenshots = Confirm.ask("🧹 Deseja apagar automaticamente os screenshots após a leitura (Garbage Collector)?", default=True)
        updated_items = auto_scan_prices(imbuements, world, clean_screenshots, session_prices)
    elif update_option == "manual":
        manual_update_prices(session_prices, known_items)
        updated_items = set(known_items) # consider all updated so they save to db
        
    # 5. Salvar novos preços se houver atualizações
    if updated_items:
        token_prices = session_prices["Gold Token"]
        mat_prices = {k: v for k, v in session_prices.items() if k != "Gold Token"}
        save_prices(world, token_prices, mat_prices)
        console.print("[green]💾 Preços da sessão salvos com sucesso no banco de dados![/green]")
        
    print_trend_chart(world, "Gold Token")
    
    # 6. Realizar cálculos
    available_imbs = list(imbuements.keys())
    console.print("\n[bold yellow]🎯 Filtro de Imbuements[/bold yellow]")
    console.print("Selecione quais imbuements deseja calcular e exibir (ex: 0,1 ou ENTER para todos):")
    for i, imb in enumerate(available_imbs):
        console.print(f"  [{i}] {imb}")
        
    selected_input = Prompt.ask("Índices separados por vírgula", default="all")
    selected_imbs = []
    if selected_input.lower() == "all" or not selected_input.strip():
        selected_imbs = available_imbs
    else:
        try:
            indices = [int(x.strip()) for x in selected_input.split(",") if x.strip()]
            for idx in indices:
                if 0 <= idx < len(available_imbs):
                    selected_imbs.append(available_imbs[idx])
        except ValueError:
            console.print("[yellow]⚠️ Entrada inválida. Calculando todos os imbuements por padrão.[/yellow]\n")
            selected_imbs = available_imbs
            
    if not selected_imbs:
        selected_imbs = available_imbs

    mat_prices_inst = {mat: prices[0] for mat, prices in session_prices.items() if mat != "Gold Token"}
    mat_prices_ord = {mat: prices[1] for mat, prices in session_prices.items() if mat != "Gold Token"}
    token_price_inst = session_prices["Gold Token"][0]

    for imb_name in selected_imbs:
        tiers = imbuements[imb_name]
        console.print(f"\n[bold cyan]📌 {imb_name}[/bold cyan]")
        table = Table(title=f"{imb_name}")
        table.add_column("Tier", style="yellow")
        table.add_column("Mat. (Order)", style="white")
        table.add_column("Mat. (Instant)", style="white")
        table.add_column("Tokens (Instant)", style="white")
        table.add_column("Melhor", style="green")
        table.add_column("Custo/hora (Melhor)", style="blue")
        
        for tier_name, tier_info in tiers.items():
            cost_mat_ord = cost_by_materials(tier_info, mat_prices_ord)
            cost_mat_inst = cost_by_materials(tier_info, mat_prices_inst)
            cost_token_inst = cost_by_tokens(tier_info, token_price_inst)
            
            costs = {
                "Mat. (Order)": cost_mat_ord,
                "Mat. (Instant)": cost_mat_inst,
                "Tokens (Instant)": cost_token_inst
            }
            
            valid_costs = {k: v for k, v in costs.items() if v > tier_info.fee}
            
            if valid_costs:
                best_name = min(valid_costs, key=valid_costs.get)
                best_cost = valid_costs[best_name]
            else:
                best_name = "N/A"
                best_cost = tier_info.fee
                
            hourly = cost_per_hour(best_cost)
            
            table.add_row(
                tier_name,
                f"{cost_mat_ord:,.0f}",
                f"{cost_mat_inst:,.0f}",
                f"{cost_token_inst:,.0f}",
                f"{best_name}",
                f"{hourly:,.0f} gp/h"
            )
        console.print(table)
    
    console.print("\n[dim]✨ Imbuements duram 20 horas de uso. Use Gold Token = 2/4/6 conforme o tier.[/dim]")

if __name__ == "__main__":
    main()