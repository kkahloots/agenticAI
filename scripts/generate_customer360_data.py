"""Generate sample sales, social, and support data for Customer 360 view."""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Load existing customers
customers_path = Path("data/customers.json")
with open(customers_path) as f:
    customers = json.load(f)

customer_ids = [c["customer_id"] for c in customers[:20]]  # Use first 20 for demo

# Generate sales transactions
sales_data = []
for i, cid in enumerate(customer_ids):
    num_transactions = random.randint(3, 15)
    for j in range(num_transactions):
        days_ago = random.randint(1, 365)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        sales_data.append({
            "transaction_id": f"TXN-{i:03d}-{j:03d}",
            "customer_id": cid,
            "date": date,
            "amount": round(random.uniform(10, 5000), 2),
            "product": random.choice(["savings", "investment", "insurance", "loan", "credit_card"]),
            "channel": random.choice(["online", "branch", "mobile_app", "phone"]),
            "status": random.choice(["completed", "completed", "completed", "pending", "failed"])
        })

# Generate social media interactions
social_data = []
sentiments = ["positive", "neutral", "negative"]
platforms = ["twitter", "facebook", "instagram", "linkedin"]
for i, cid in enumerate(customer_ids[:15]):  # Not all customers are on social
    num_posts = random.randint(2, 8)
    for j in range(num_posts):
        days_ago = random.randint(1, 180)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        sentiment = random.choice(sentiments)
        
        # Generate realistic feedback based on sentiment
        if sentiment == "positive":
            texts = [
                "Great service! Very satisfied with my account.",
                "Love the new mobile app features!",
                "Quick response from customer support team.",
                "Best banking experience I've had."
            ]
        elif sentiment == "negative":
            texts = [
                "Disappointed with the long wait times.",
                "App keeps crashing, very frustrating.",
                "Hidden fees are not acceptable.",
                "Poor customer service experience."
            ]
        else:
            texts = [
                "The new update is okay, nothing special.",
                "Standard banking services.",
                "Average experience overall.",
                "It works fine for basic needs."
            ]
        
        social_data.append({
            "post_id": f"POST-{i:03d}-{j:03d}",
            "customer_id": cid,
            "platform": random.choice(platforms),
            "date": date,
            "text": random.choice(texts),
            "sentiment": sentiment,
            "engagement": random.randint(0, 500)
        })

# Generate support tickets
support_data = []
ticket_types = ["technical", "billing", "account", "product_inquiry", "complaint"]
priorities = ["low", "medium", "high"]
statuses = ["open", "in_progress", "resolved", "closed"]

for i, cid in enumerate(customer_ids):
    num_tickets = random.randint(1, 5)
    for j in range(num_tickets):
        days_ago = random.randint(1, 365)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        ticket_type = random.choice(ticket_types)
        
        # Generate realistic ticket descriptions
        descriptions = {
            "technical": [
                "Unable to login to mobile app. Getting error code 401.",
                "Transaction failed but amount was debited from account.",
                "Cannot reset password, verification email not received.",
                "App crashes when trying to view transaction history."
            ],
            "billing": [
                "Unexpected charges on my account statement.",
                "Need clarification on monthly maintenance fees.",
                "Refund not processed for cancelled transaction.",
                "Incorrect interest calculation on savings account."
            ],
            "account": [
                "Need to update my contact information.",
                "Request to close dormant account.",
                "Unable to link new card to account.",
                "Account locked after multiple failed login attempts."
            ],
            "product_inquiry": [
                "What are the benefits of upgrading to premium account?",
                "Interest rates for fixed deposit accounts?",
                "Eligibility criteria for personal loan.",
                "How to apply for credit card?"
            ],
            "complaint": [
                "Very poor customer service at branch.",
                "Long wait times on customer support hotline.",
                "Rude behavior from support agent.",
                "Issue not resolved after multiple follow-ups."
            ]
        }
        
        support_data.append({
            "ticket_id": f"TICKET-{i:03d}-{j:03d}",
            "customer_id": cid,
            "date": date,
            "type": ticket_type,
            "priority": random.choice(priorities),
            "status": random.choice(statuses),
            "description": random.choice(descriptions[ticket_type]),
            "resolution_time_hours": random.randint(1, 72) if random.random() > 0.3 else None
        })

# Save to files
Path("data").mkdir(exist_ok=True)

with open("data/sales_transactions.json", "w") as f:
    json.dump(sales_data, f, indent=2)

with open("data/social_media.json", "w") as f:
    json.dump(social_data, f, indent=2)

with open("data/support_tickets.json", "w") as f:
    json.dump(support_data, f, indent=2)

print(f"✅ Generated {len(sales_data)} sales transactions")
print(f"✅ Generated {len(social_data)} social media posts")
print(f"✅ Generated {len(support_data)} support tickets")
print(f"📁 Files saved to data/ directory")
