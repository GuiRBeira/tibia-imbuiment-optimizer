import sys
import os
import glob
import time
import numpy as np
import cv2
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt, Confirm
from models import load_imbuements
from calculator import cost_by_materials, cost_by_tokens, cost_per_hour, break_even_token_price
from storage import init_db, save_prices, get_average_prices_last_days, get_daily_average_prices
from scanner import extract_text, parse_market_prices

console = Console()

def get_latest_screenshot(folder):
    files = glob.glob(os.path.join(folder, "*.png"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def wait_for_screenshot(item_name, screenshot_dir, last_file):
    console.print(f"👉 Pesquise [cyan]{item_name}[/cyan] no Market e aperte [bold yellow]Print Screen (PrtScn)[/bold yellow]")
    while True:
        current_latest = get_latest_screenshot(screenshot_dir)
        if current_latest and current_latest != last_file:
            time.sleep(0.3)  # Dá tempo do sistema operacional salvar o arquivo
            # Lemos direto com o caminho do arquivo para o Tesseract
            ocr_result = extract_text(current_latest)
            inst, ord = parse_market_prices(ocr_result)
            console.print(f"   [green]✅ Lido: Inst. {inst:,} gp | Pedido {ord:,} gp[/green]\n")
            return (inst, ord), current_latest
        time.sleep(0.5)

def auto_scan_prices(imbuements_data, world: str):
    screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")
    if not os.path.exists(screenshot_dir):
        console.print(f"[bold red]❌ Pasta de Screenshots não encontrada: {screenshot_dir}[/bold red]")
        console.print("Por favor, tire uma print para que o Ubuntu crie a pasta, e reinicie o programa.")
        sys.exit(1)

    console.print("\n[bold green]🥷 Modo Auto-Scan (Wayland Ninja) Ativado![/bold green]")
    console.print("Como usar: Basta olhar o item pedido, pesquisar no Tibia, e apertar sua tecla de [yellow]Print Screen[/yellow]!\n")
    
    last_file = get_latest_screenshot(screenshot_dir)
    
    token_prices, last_file = wait_for_screenshot("Gold Token", screenshot_dir, last_file)
    
    all_materials = set()
    for tiers in imbuements_data.values():
        for tier_info in tiers.values():
            for material in tier_info.materials:
                all_materials.add(material.name)
    
    material_prices = {}
    for mat in sorted(all_materials):
        prices, last_file = wait_for_screenshot(mat, screenshot_dir, last_file)
        material_prices[mat] = prices
            
    return token_prices, material_prices

def get_prices(imbuements_data, world: str):
    avg_tokens = get_average_prices_last_days(world, "Gold Token")
    avg_inst = avg_tokens[0] if avg_tokens else None
    avg_ord = avg_tokens[1] if avg_tokens else None
    
    console.print("\n[bold yellow]💰 Gold Tokens[/bold yellow]")
    msg_inst = f"  Compra Instantânea (Sell Offer) [dim](média: {avg_inst:,.0f})[/dim]" if avg_inst else "  Compra Instantânea (Sell Offer)"
    token_inst = IntPrompt.ask(msg_inst, default=10000)
    
    msg_ord = f"  Pedido de Compra (Buy Offer) [dim](média: {avg_ord:,.0f})[/dim]" if avg_ord else "  Pedido de Compra (Buy Offer)"
    token_ord = IntPrompt.ask(msg_ord, default=10000)
    
    token_prices = (token_inst, token_ord)
    
    all_materials = set()
    for tiers in imbuements_data.values():
        for tier_info in tiers.values():
            for material in tier_info.materials:
                all_materials.add(material.name)
    
    material_prices = {}
    console.print("\n📦 Agora os preços dos materiais:")
    for mat in sorted(all_materials):
        console.print(f"\n[cyan]{mat}[/cyan]")
        avg_mats = get_average_prices_last_days(world, mat)
        avg_mat_inst = avg_mats[0] if avg_mats else None
        avg_mat_ord = avg_mats[1] if avg_mats else None
        
        msg_inst = f"  Compra Instantânea [dim](média: {avg_mat_inst:,.0f})[/dim]" if avg_mat_inst else f"  Compra Instantânea"
        price_inst = IntPrompt.ask(msg_inst, default=0)
        
        msg_ord = f"  Pedido de Compra [dim](média: {avg_mat_ord:,.0f})[/dim]" if avg_mat_ord else f"  Pedido de Compra"
        price_ord = IntPrompt.ask(msg_ord, default=0)
        
        material_prices[mat] = (price_inst, price_ord)
    
    return token_prices, material_prices

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
    
    use_auto_scan = Confirm.ask("\n🤖 Deseja usar a Mágica do Auto-Scan (Ler a tela ao invés de digitar)?", default=True)
    
    if use_auto_scan:
        token_prices, mat_prices = auto_scan_prices(imbuements, world)
    else:
        token_prices, mat_prices = get_prices(imbuements, world)
    
    save_prices(world, token_prices, mat_prices)
    print_trend_chart(world, "Gold Token")
    
    mat_prices_inst = {mat: prices[0] for mat, prices in mat_prices.items()}
    mat_prices_ord = {mat: prices[1] for mat, prices in mat_prices.items()}
    token_price_inst = token_prices[0]
    
    for imb_name, tiers in imbuements.items():
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