from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt
from models import load_imbuements
from calculator import cost_by_materials, cost_by_tokens, cost_per_hour, break_even_token_price
from storage import init_db, save_prices, get_average_price_last_days, get_daily_average_prices

console = Console()

def get_prices(imbuements_data, world: str):
    avg_token = get_average_price_last_days(world, "Gold Token")
    token_msg = f"💰 Preço do Gold Token (por unidade) [dim](média 7d: {avg_token:,.0f})[/dim]" if avg_token else "💰 Preço do Gold Token (por unidade)"
    token_price = IntPrompt.ask(token_msg, default=10000)
    
    if avg_token and token_price > avg_token * 1.2:
        console.print(f"  [yellow]🔴 Alerta: Gold Token está {(token_price/avg_token - 1)*100:.1f}% acima da média! Considere esperar.[/yellow]")
    
    all_materials = set()
    for tiers in imbuements_data.values():
        for tier_info in tiers.values():
            for material in tier_info.materials:
                all_materials.add(material.name)
    
    material_prices = {}
    console.print("\n📦 Agora os preços dos materiais:")
    for mat in sorted(all_materials):
        avg_mat = get_average_price_last_days(world, mat)
        mat_msg = f"  {mat} [dim](média 7d: {avg_mat:,.0f})[/dim]" if avg_mat else f"  {mat}"
        price = IntPrompt.ask(mat_msg, default=0)
        
        if avg_mat and price > avg_mat * 1.2:
            console.print(f"    [yellow]🔴 Alerta: {mat} está {(price/avg_mat - 1)*100:.1f}% acima da média![/yellow]")
            
        material_prices[mat] = price
    
    return token_price, material_prices

def print_trend_chart(world: str, item_name: str):
    data = get_daily_average_prices(world, item_name, 7)
    if not data or len(data) < 2:
        return
        
    console.print(f"\n[bold cyan]📊 Tendência de {item_name} (Últimos dias em {world})[/bold cyan]")
    max_price = max(data.values())
    min_price = min(data.values())
    baseline = min_price * 0.9  # Ajuste para visualizar diferenças menores
    
    for date_str, price in data.items():
        range_val = max_price - baseline
        if range_val == 0:
            bar_len = 20
        else:
            bar_len = int(((price - baseline) / range_val) * 40)
            
        bar = "█" * max(1, bar_len)
        console.print(f"{date_str} | [green]{bar}[/green] {price:,.0f} gp")

def main():
    console.print("[bold green]⚔️ Tibia Imbuement Optimizer - Basic / Intricate / Powerful[/bold green]")
    
    init_db()
    
    imbuements = load_imbuements("data/immy_data.json")
    world = Prompt.ask("🌍 Qual o nome do seu mundo (ex: Yonabra)", default="Unknown")
    token_price, mat_prices = get_prices(imbuements, world)
    
    save_prices(world, token_price, mat_prices)
    print_trend_chart(world, "Gold Token")
    
    for imb_name, tiers in imbuements.items():
        console.print(f"\n[bold cyan]📌 {imb_name}[/bold cyan]")
        table = Table(title=f"{imb_name}")
        table.add_column("Tier", style="yellow")
        table.add_column("Via Materiais", style="white")
        table.add_column("Via Gold Tokens", style="white")
        table.add_column("Melhor", style="green")
        table.add_column("Custo/hora", style="blue")
        table.add_column("Break-even Token", style="magenta")
        
        for tier_name, tier_info in tiers.items():
            cost_mat = cost_by_materials(tier_info, mat_prices)
            cost_token = cost_by_tokens(tier_info, token_price)
            
            diff = abs(cost_mat - cost_token)
            if max(cost_mat, cost_token) > 0:
                pct = (diff / max(cost_mat, cost_token)) * 100
            else:
                pct = 0.0
                
            best = ("Materiais" if cost_mat < cost_token else "Gold Tokens") + f" (-{pct:.1f}%)"
            
            best_cost = min(cost_mat, cost_token)
            hourly = cost_per_hour(best_cost)
            break_even = break_even_token_price(tier_info, mat_prices)
            
            table.add_row(
                tier_name,
                f"{cost_mat:,.0f} gp",
                f"{cost_token:,.0f} gp",
                best,
                f"{hourly:,.0f} gp/h",
                f"até {break_even:,.0f} gp"
            )
        console.print(table)
    
    console.print("\n[dim]✨ Imbuements duram 20 horas de uso. Use Gold Token = 2/4/6 conforme o tier.[/dim]")

if __name__ == "__main__":
    main()