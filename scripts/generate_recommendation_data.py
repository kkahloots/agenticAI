"""
Generate synthetic recommendation data:
- 200 products across 10 categories
- 5000 interactions (view/click/purchase) across existing customers
- Saves to data/products.json and data/interactions.json
"""
from __future__ import annotations

import json
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent.parent / "data"

CATEGORIES = [
    "electronics", "clothing", "home", "sports", "beauty",
    "books", "food", "travel", "automotive", "toys",
]

PRODUCT_NAMES = {
    "electronics": ["Wireless Headphones", "Smart Watch", "Bluetooth Speaker", "Laptop Stand",
                    "USB-C Hub", "Webcam HD", "Mechanical Keyboard", "Gaming Mouse",
                    "Portable Charger", "LED Desk Lamp", "Smart Plug", "Tablet Case",
                    "Screen Protector", "Cable Organiser", "Noise Cancelling Earbuds",
                    "Smart Home Hub", "Action Camera", "E-Reader", "VR Headset", "Drone"],
    "clothing": ["Running Shoes", "Casual T-Shirt", "Denim Jacket", "Yoga Pants",
                 "Winter Coat", "Formal Shirt", "Sneakers", "Leather Belt",
                 "Wool Scarf", "Baseball Cap", "Swimwear", "Hiking Boots",
                 "Polo Shirt", "Cargo Shorts", "Raincoat", "Dress Shoes",
                 "Sports Socks", "Thermal Underwear", "Sunglasses", "Backpack"],
    "home": ["Coffee Maker", "Air Purifier", "Robot Vacuum", "Blender",
             "Toaster Oven", "Bed Sheets", "Throw Pillow", "Scented Candle",
             "Wall Clock", "Picture Frame", "Storage Basket", "Desk Organiser",
             "Plant Pot", "Kitchen Scale", "Cutting Board", "Knife Set",
             "Shower Curtain", "Bath Towel Set", "Laundry Basket", "Doormat"],
    "sports": ["Yoga Mat", "Resistance Bands", "Dumbbell Set", "Jump Rope",
               "Water Bottle", "Gym Bag", "Foam Roller", "Pull-Up Bar",
               "Cycling Gloves", "Tennis Racket", "Football", "Basketball",
               "Swimming Goggles", "Protein Shaker", "Fitness Tracker", "Knee Brace",
               "Trekking Poles", "Camping Tent", "Sleeping Bag", "Climbing Harness"],
    "beauty": ["Face Moisturiser", "Vitamin C Serum", "Shampoo", "Conditioner",
               "Lip Balm", "Sunscreen SPF50", "Eye Cream", "Body Lotion",
               "Perfume", "Nail Polish", "Makeup Brush Set", "Mascara",
               "Foundation", "Toner", "Face Mask", "Hair Dryer",
               "Electric Toothbrush", "Razor", "Deodorant", "Hand Cream"],
    "books": ["Python Programming", "Data Science Handbook", "Business Strategy",
              "Self-Help Guide", "History of AI", "Cooking Masterclass",
              "Travel Photography", "Mindfulness Journal", "Finance 101",
              "Leadership Essentials", "Science Fiction Novel", "Mystery Thriller",
              "Children's Atlas", "Language Learning", "Art History",
              "Yoga for Beginners", "Gardening Guide", "Nutrition Bible",
              "Startup Playbook", "Creative Writing"],
    "food": ["Organic Coffee Beans", "Green Tea Pack", "Protein Bars", "Olive Oil",
             "Dark Chocolate", "Honey Jar", "Granola Mix", "Pasta Set",
             "Hot Sauce", "Spice Collection", "Dried Fruits", "Nut Butter",
             "Kombucha", "Coconut Water", "Energy Drink", "Herbal Tea",
             "Quinoa Pack", "Oat Milk", "Vegan Snacks", "Gourmet Salt"],
    "travel": ["Travel Pillow", "Luggage Lock", "Packing Cubes", "Travel Adapter",
               "Passport Holder", "Compression Socks", "Portable Scale", "Neck Wallet",
               "Travel Towel", "Waterproof Bag", "Sunscreen Stick", "Insect Repellent",
               "First Aid Kit", "Travel Umbrella", "Noise Cancelling Earplugs", "Eye Mask",
               "Reusable Water Bottle", "Snack Pack", "Travel Journal", "City Map"],
    "automotive": ["Car Phone Mount", "Dash Cam", "Tyre Inflator", "Car Vacuum",
                   "Seat Covers", "Steering Wheel Cover", "Car Air Freshener", "Jump Starter",
                   "Windscreen Sunshade", "Car Organiser", "LED Interior Lights", "Parking Sensor",
                   "Car Wax", "Microfibre Cloth", "Tyre Pressure Gauge", "Emergency Kit",
                   "Car Charger", "Blind Spot Mirror", "Roof Rack", "Tow Rope"],
    "toys": ["LEGO Set", "Board Game", "Puzzle 1000pc", "Remote Control Car",
             "Stuffed Animal", "Art Kit", "Science Experiment Kit", "Card Game",
             "Wooden Blocks", "Play-Doh Set", "Doll House", "Action Figure",
             "Magnetic Tiles", "Coding Robot", "Telescope", "Microscope",
             "Slime Kit", "Kinetic Sand", "Water Guns", "Frisbee"],
}


def generate_products() -> list[dict]:
    products = []
    pid = 1
    for cat, names in PRODUCT_NAMES.items():
        for name in names:
            price = round(random.uniform(5.0, 500.0), 2)
            products.append({
                "product_id": f"PROD-{pid:03d}",
                "name": name,
                "category": cat,
                "price": price,
                "tags": [cat, random.choice(CATEGORIES)],
                "popularity_rank": random.randint(1, 200),
            })
            pid += 1
    return products


def generate_interactions(customers: list[dict], products: list[dict], n: int = 5000) -> list[dict]:
    interaction_types = ["view", "click", "purchase"]
    weights = [0.6, 0.3, 0.1]

    # Category affinity: customers tend to interact with their purchase categories
    interactions = []
    for _ in range(n):
        customer = random.choice(customers)
        cid = customer["customer_id"]
        cats = customer.get("purchase_categories", [])

        # 60% chance to pick a product from their category affinity
        if cats and random.random() < 0.6:
            cat = random.choice(cats)
            cat_products = [p for p in products if p["category"] == cat]
            product = random.choice(cat_products) if cat_products else random.choice(products)
        else:
            product = random.choice(products)

        itype = random.choices(interaction_types, weights=weights)[0]
        interactions.append({
            "customer_id": cid,
            "product_id": product["product_id"],
            "interaction_type": itype,
            "category": product["category"],
        })

    return interactions


def main():
    # Load existing customers
    customers_path = DATA_DIR / "customers.json"
    if not customers_path.exists():
        print("❌ data/customers.json not found. Run cust_dataset_generator.py first.")
        return

    with open(customers_path) as f:
        customers = json.load(f)

    print(f"✅ Loaded {len(customers)} customers")

    products = generate_products()
    print(f"✅ Generated {len(products)} products")

    interactions = generate_interactions(customers, products, n=5000)
    print(f"✅ Generated {len(interactions)} interactions")

    with open(DATA_DIR / "products.json", "w") as f:
        json.dump(products, f, indent=2)
    print("✅ Saved data/products.json")

    with open(DATA_DIR / "interactions.json", "w") as f:
        json.dump(interactions, f, indent=2)
    print("✅ Saved data/interactions.json")

    # Stats
    from collections import Counter
    type_counts = Counter(i["interaction_type"] for i in interactions)
    print(f"\n📊 Interaction breakdown:")
    for t, c in type_counts.items():
        print(f"   {t}: {c}")
    print(f"\n🎯 Unique users with interactions: {len(set(i['customer_id'] for i in interactions))}")
    print(f"🛍️  Unique products interacted with: {len(set(i['product_id'] for i in interactions))}")


if __name__ == "__main__":
    main()
