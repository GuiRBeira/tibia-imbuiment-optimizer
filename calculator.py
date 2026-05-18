from models import TierInfo

IMBUEMENT_DURATION_HOURS = 20

def cost_by_materials(tier_info: TierInfo, material_prices: dict) -> int:
    material_cost = 0
    for material in tier_info.materials:
        if material.name not in material_prices:
            raise ValueError(f"Missing price for {material.name}")
        material_cost += material.amount * material_prices[material.name]
    
    return material_cost + tier_info.fee

def cost_by_tokens(tier_info: TierInfo, token_price: int) -> int:
    return tier_info.token_cost_qty * token_price + tier_info.fee

def cost_per_hour(total_cost: int) -> float:
    return total_cost / IMBUEMENT_DURATION_HOURS

def break_even_token_price(tier_info: TierInfo, material_prices: dict) -> float:
    mat_cost = cost_by_materials(tier_info, material_prices)
    return (mat_cost - tier_info.fee) / tier_info.token_cost_qty