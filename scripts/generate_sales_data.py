"""Generate sales transaction data for UC7 — Sales Analytics (online store)."""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

customers = json.load(open("data/customers.json"))
customer_ids = [c["customer_id"] for c in customers]

CATEGORIES = {
    "electronics":    ["Laptop", "Smartphone", "Tablet", "Headphones", "Smart Watch",
                       "Bluetooth Speaker", "Camera", "Gaming Console", "Fitness Tracker", "Dash Cam"],
    "clothing":       ["T-Shirt", "Jeans", "Dress", "Jacket", "Sneakers",
                       "Blouse", "Shorts", "Sweater", "Running Shoes"],
    "home_garden":    ["Vacuum Cleaner", "Coffee Maker", "Kitchen Knife Set", "Bedding Set",
                       "Lamp", "Cushions", "Plant Pot", "Garden Tools"],
    "sports_outdoors":["Yoga Mat", "Bicycle", "Camping Tent", "Hiking Backpack",
                       "Basketball", "Water Bottle", "Running Shoes"],
    "books":          ["Fiction Novel", "Self-Help Book", "Cookbook", "Biography",
                       "Textbook", "Art Book", "Technical Manual", "Children's Book"],
    "beauty_health":  ["Skincare Set", "Hair Dryer", "Makeup Kit", "Perfume",
                       "Vitamins", "Shampoo", "Face Mask", "Moisturizer"],
    "toys_games":     ["Board Game", "Puzzle", "Action Figure", "Building Blocks",
                       "Remote Control Car", "Doll", "Video Game", "Art Supplies"],
    "automotive":     ["Car Charger", "Dash Cam", "Tire Pressure Gauge", "Car Cover",
                       "Jump Starter", "Floor Mats", "Car Phone Mount"],
}

PRICE_RANGES = {
    "electronics":    (50, 1500),
    "clothing":       (15, 200),
    "home_garden":    (20, 400),
    "sports_outdoors":(10, 500),
    "books":          (5, 60),
    "beauty_health":  (8, 150),
    "toys_games":     (10, 120),
    "automotive":     (10, 250),
}

CHANNELS = ["website", "mobile_app", "social_media", "email_campaign", "affiliate"]
CHANNEL_WEIGHTS = [0.40, 0.30, 0.15, 0.10, 0.05]

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "apple_pay", "bank_transfer"]

# Category weights — electronics dominates, books/automotive are niche
CATEGORY_WEIGHTS = [0.28, 0.18, 0.14, 0.14, 0.07, 0.08, 0.07, 0.04]

transactions = []
start_date = datetime(2025, 1, 1)
end_date   = datetime(2026, 3, 31)
date_range = (end_date - start_date).days

txn_id = 1
for cid in customer_ids:
    n = random.choices([1, 2, 3, 4, 5, 6, 8, 10], weights=[5, 10, 20, 25, 20, 10, 6, 4])[0]
    for _ in range(n):
        category = random.choices(list(CATEGORIES.keys()), weights=CATEGORY_WEIGHTS)[0]
        product  = random.choice(CATEGORIES[category])
        lo, hi   = PRICE_RANGES[category]
        unit_price = round(random.uniform(lo, hi), 2)
        quantity   = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
        subtotal   = round(unit_price * quantity, 2)
        discount_pct = random.choices([0, 5, 10, 15, 20], weights=[50, 20, 15, 10, 5])[0]
        discount_amt = round(subtotal * discount_pct / 100, 2)
        shipping     = 0 if subtotal > 50 else round(random.uniform(3, 8), 2)
        total        = round(subtotal - discount_amt + shipping, 2)
        days_offset  = random.randint(0, date_range)
        ts           = start_date + timedelta(days=days_offset,
                                              hours=random.randint(6, 22),
                                              minutes=random.randint(0, 59))
        status = random.choices(["completed", "completed", "completed", "returned", "cancelled"],
                                weights=[80, 0, 0, 12, 8])[0]

        transactions.append({
            "transaction_id":   f"TXN-{txn_id:06d}",
            "customer_id":      cid,
            "date":             ts.strftime("%Y-%m-%d"),
            "timestamp":        ts.isoformat(),
            "product_category": category,
            "product_name":     product,
            "quantity":         quantity,
            "unit_price":       unit_price,
            "subtotal":         subtotal,
            "discount_percent": discount_pct,
            "discount_amount":  discount_amt,
            "shipping_cost":    shipping,
            "total_amount":     total,
            "channel":          random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0],
            "payment_method":   random.choice(PAYMENT_METHODS),
            "status":           status,
            "currency":         "EUR",
        })
        txn_id += 1

random.shuffle(transactions)

Path("data").mkdir(exist_ok=True)
with open("data/sales_transactions.json", "w") as f:
    json.dump(transactions, f, indent=2)

completed = [t for t in transactions if t["status"] == "completed"]
revenue   = sum(t["total_amount"] for t in completed)
by_cat    = {}
for t in completed:
    by_cat[t["product_category"]] = by_cat.get(t["product_category"], 0) + t["total_amount"]

print(f"✅ Generated {len(transactions)} transactions across {len(customer_ids)} customers")
print(f"   Completed: {len(completed)} | Revenue: ${revenue:,.2f}")
print(f"   Date range: {min(t['date'] for t in transactions)} → {max(t['date'] for t in transactions)}")
print("   Revenue by category:")
for cat, rev in sorted(by_cat.items(), key=lambda x: -x[1]):
    print(f"     {cat:<20} ${rev:>10,.2f}")
