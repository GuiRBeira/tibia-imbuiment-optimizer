import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Material:
    name: str
    amount: int

@dataclass
class TierInfo:
    fee: int
    token_cost_qty: int
    materials: List[Material]

TIER_FEES = {"Basic": 50000, "Intricate": 150000, "Powerful": 250000}
TOKEN_QTY = {"Basic": 2, "Intricate": 4, "Powerful": 6}

def load_imbuements(json_path="data/immy_data.json") -> Dict[str, Dict[str, TierInfo]]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result = {}
    for imb_name, tiers in data.items():
        result[imb_name] = {}
        for tier_name, materials in tiers.items():
            parsed_materials = [Material(name=m["name"], amount=m["amount"]) for m in materials]
            result[imb_name][tier_name] = TierInfo(
                fee=TIER_FEES[tier_name],
                token_cost_qty=TOKEN_QTY[tier_name],
                materials=parsed_materials
            )
    return result