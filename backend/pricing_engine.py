from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from backend.config import settings

def to_decimal(val: Any) -> Decimal:
    """Helper to safely convert any numeric or string value to Decimal."""
    if val is None:
        return Decimal("0.00")
    if isinstance(val, (int, float, str)):
        return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal("0.00")

class UniversalPricingEngine:
    """
    Centralized, event-independent pricing engine with precise Decimal arithmetic.
    Calculates item subtotals, GST taxes, discounts, and advance booking amounts.
    """
    
    @staticmethod
    def calculate_item_cost(
        unit_type: str,
        unit_price: float,
        quantity: float,
        attendees: int = 1,
        duration_hours: float = 1.0,
        duration_days: float = 1.0
    ) -> Decimal:
        price_dec = to_decimal(unit_price)
        qty_dec = to_decimal(quantity)
        
        unit = unit_type.lower()
        if unit == "per_person" or unit == "per_seat":
            # For per_person, if qty is passed as 1, default to attendees count or qty
            effective_count = qty_dec if qty_dec > Decimal("1.00") else to_decimal(attendees)
            return (effective_count * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        elif unit == "per_hour":
            return (qty_dec * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        elif unit == "per_day":
            return (qty_dec * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        elif unit == "per_worker":
            return (qty_dec * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        elif unit == "per_item":
            return (qty_dec * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        elif unit == "per_event":
            return (qty_dec * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        else:
            return (qty_dec * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_quotation(
        items: List[Dict[str, Any]],
        attendees: int = 50,
        tax_rate: float = settings.DEFAULT_GST_RATE,
        discount_amount: float = 0.0,
        advance_percentage: float = settings.DEFAULT_ADVANCE_PERCENTAGE
    ) -> Dict[str, Any]:
        """
        Calculates line-by-line total and aggregated quotation breakdown.
        """
        calculated_items = []
        subtotal = Decimal("0.00")
        
        for item in items:
            unit_type = item.get("unit_type", "per_event")
            unit_price = item.get("unit_price", 0.0)
            quantity = item.get("quantity", 1.0)
            
            line_cost = UniversalPricingEngine.calculate_item_cost(
                unit_type=unit_type,
                unit_price=unit_price,
                quantity=quantity,
                attendees=attendees
            )
            
            subtotal += line_cost
            
            calculated_items.append({
                "service_id": item.get("service_id"),
                "service_name": item.get("service_name", "Service Item"),
                "category_name": item.get("category_name", "General"),
                "unit_type": unit_type,
                "quantity": float(quantity),
                "unit_price": float(to_decimal(unit_price)),
                "total_price": float(line_cost)
            })
            
        tax_rate_dec = to_decimal(tax_rate)
        discount_dec = to_decimal(discount_amount)
        
        # Subtotal minus discount
        discounted_subtotal = max(Decimal("0.00"), subtotal - discount_dec)
        
        # 18% GST (9% CGST + 9% SGST)
        tax_amount = (discounted_subtotal * tax_rate_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        grand_total = (discounted_subtotal + tax_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Advance payment required
        advance_pct_dec = to_decimal(advance_percentage)
        advance_required = (grand_total * advance_pct_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        balance_due = (grand_total - advance_required).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return {
            "items": calculated_items,
            "subtotal": float(subtotal),
            "discount_amount": float(discount_dec),
            "tax_rate": float(tax_rate_dec),
            "tax_amount": float(tax_amount),
            "cgst_amount": float((tax_amount / Decimal("2.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "sgst_amount": float((tax_amount / Decimal("2.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "grand_total": float(grand_total),
            "advance_required": float(advance_required),
            "balance_due": float(balance_due),
            "currency": settings.CURRENCY_CODE,
            "currency_symbol": settings.CURRENCY_SYMBOL
        }

pricing_engine = UniversalPricingEngine()
