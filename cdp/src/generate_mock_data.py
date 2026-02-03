"""
CDP Demo - Mock Veri Oluşturucu
Petrol Ofisi benzeri senaryo için gerçekçi müşteri ve işlem verisi
"""

import random
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import csv

# Türk isimleri
FIRST_NAMES = [
    "Ahmet", "Mehmet", "Mustafa", "Ali", "Hüseyin", "Hasan", "İbrahim", "Ömer", "Osman", "Yusuf",
    "Ayşe", "Fatma", "Emine", "Hatice", "Zeynep", "Elif", "Merve", "Zehra", "Esra", "Büşra",
    "Can", "Emre", "Burak", "Murat", "Serkan", "Tolga", "Kaan", "Onur", "Barış", "Cem",
    "Selin", "Deniz", "İrem", "Gizem", "Ceren", "Pınar", "Ebru", "Özge", "Sibel", "Derya"
]

LAST_NAMES = [
    "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
    "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek",
    "Polat", "Korkmaz", "Erdoğan", "Güneş", "Aksoy", "Aktaş", "Tekin", "Kaplan", "Uçar", "Güler"
]

CITIES = [
    ("İstanbul", ["Kadıköy", "Beşiktaş", "Şişli", "Üsküdar", "Bakırköy", "Ataşehir", "Maltepe"]),
    ("Ankara", ["Çankaya", "Keçiören", "Yenimahalle", "Mamak", "Etimesgut"]),
    ("İzmir", ["Konak", "Karşıyaka", "Bornova", "Buca", "Bayraklı"]),
    ("Bursa", ["Nilüfer", "Osmangazi", "Yıldırım"]),
    ("Antalya", ["Muratpaşa", "Konyaaltı", "Kepez"])
]

# Petrol Ofisi ürünleri
FUEL_TYPES = [
    {"name": "Eurodizel", "price_per_liter": 42.50, "is_premium": False},
    {"name": "Kurşunsuz 95", "price_per_liter": 44.20, "is_premium": False},
    {"name": "Premium Dizel", "price_per_liter": 45.80, "is_premium": True},
    {"name": "Premium 97", "price_per_liter": 47.50, "is_premium": True},
]

MARKET_PRODUCTS = [
    {"category": "İçecek", "name": "Su 0.5L", "price": 12},
    {"category": "İçecek", "name": "Kola 330ml", "price": 25},
    {"category": "İçecek", "name": "Enerji İçeceği", "price": 45},
    {"category": "Atıştırmalık", "name": "Çikolata", "price": 35},
    {"category": "Atıştırmalık", "name": "Cips", "price": 40},
    {"category": "Atıştırmalık", "name": "Kuruyemiş", "price": 55},
    {"category": "Kahve", "name": "Filtre Kahve", "price": 35},
    {"category": "Kahve", "name": "Latte", "price": 50},
    {"category": "Kahve", "name": "Americano", "price": 45},
    {"category": "Market", "name": "Ekmek", "price": 15},
    {"category": "Market", "name": "Süt 1L", "price": 35},
    {"category": "Market", "name": "Sigara", "price": 75},
]

DIGITAL_EVENTS = [
    "page_view_homepage",
    "page_view_stations",
    "page_view_campaigns",
    "page_view_loyalty",
    "app_open",
    "app_loyalty_check",
    "app_station_search",
    "app_fuel_price_check",
    "email_open",
    "email_click",
    "push_received",
    "push_clicked",
]


def generate_email(first_name, last_name):
    """Gerçekçi email oluştur"""
    domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com"]
    patterns = [
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name.lower()}{random.randint(1, 99)}",
        f"{first_name.lower()}_{last_name.lower()}{random.randint(1, 99)}",
    ]
    return f"{random.choice(patterns)}@{random.choice(domains)}".replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ş", "s").replace("ç", "c").replace("ğ", "g")


def generate_phone():
    """Türk telefon numarası oluştur"""
    prefixes = ["530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
                "540", "541", "542", "543", "544", "545", "546", "547", "548", "549",
                "550", "551", "552", "553", "554", "555", "556", "557", "558", "559"]
    return f"+90{random.choice(prefixes)}{random.randint(1000000, 9999999)}"


def hash_value(value):
    """SHA256 hash - Meta/Google için"""
    return hashlib.sha256(value.lower().strip().encode()).hexdigest()


def generate_customers(n=1000):
    """Müşteri profilleri oluştur"""
    customers = []
    
    for i in range(n):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        city, districts = random.choice(CITIES)
        
        # Müşteri segmenti belirle
        segment_roll = random.random()
        if segment_roll < 0.15:
            segment = "premium"  # %15 premium müşteri
            avg_monthly_visits = random.randint(8, 15)
            prefers_premium_fuel = random.random() < 0.8
        elif segment_roll < 0.45:
            segment = "regular"  # %30 düzenli müşteri
            avg_monthly_visits = random.randint(4, 8)
            prefers_premium_fuel = random.random() < 0.3
        else:
            segment = "occasional"  # %55 ara sıra gelen
            avg_monthly_visits = random.randint(1, 4)
            prefers_premium_fuel = random.random() < 0.1
        
        customer = {
            "customer_id": f"PO{100000 + i}",
            "first_name": first_name,
            "last_name": last_name,
            "email": generate_email(first_name, last_name),
            "phone": generate_phone(),
            "city": city,
            "district": random.choice(districts),
            "age": random.randint(22, 65),
            "gender": random.choice(["M", "F"]),
            "registration_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "loyalty_card": random.random() < 0.6,  # %60 sadakat kartı var
            "segment": segment,
            "avg_monthly_visits": avg_monthly_visits,
            "prefers_premium_fuel": prefers_premium_fuel,
            "has_app": random.random() < 0.35,  # %35 app kullanıcısı
            "email_opted_in": random.random() < 0.7,
            "sms_opted_in": random.random() < 0.5,
            # Hash'lenmiş değerler (Meta/Google için)
            "email_hash": hash_value(generate_email(first_name, last_name)),
            "phone_hash": hash_value(generate_phone()),
        }
        customers.append(customer)
    
    return customers


def generate_transactions(customers, days=90):
    """Son N gün için satın alma işlemleri oluştur"""
    transactions = []
    
    start_date = datetime.now() - timedelta(days=days)
    
    for customer in customers:
        # Bu müşteri için kaç işlem olacak
        expected_visits = customer["avg_monthly_visits"] * (days / 30)
        num_transactions = max(0, int(random.gauss(expected_visits, expected_visits * 0.3)))
        
        for _ in range(num_transactions):
            tx_date = start_date + timedelta(
                days=random.randint(0, days),
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59)
            )
            
            # Yakıt alımı
            if customer["prefers_premium_fuel"]:
                fuel = random.choice([f for f in FUEL_TYPES if f["is_premium"]] + [random.choice(FUEL_TYPES)])
            else:
                fuel = random.choice([f for f in FUEL_TYPES if not f["is_premium"]] + [random.choice(FUEL_TYPES)])
            
            liters = random.randint(20, 60)
            fuel_amount = liters * fuel["price_per_liter"]
            
            # Market alımı (%40 olasılık)
            market_items = []
            market_amount = 0
            if random.random() < 0.4:
                num_items = random.randint(1, 4)
                market_items = random.sample(MARKET_PRODUCTS, num_items)
                market_amount = sum(item["price"] for item in market_items)
            
            transaction = {
                "transaction_id": f"TX{random.randint(10000000, 99999999)}",
                "customer_id": customer["customer_id"],
                "timestamp": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                "date": tx_date.strftime("%Y-%m-%d"),
                "station_id": f"ST{random.randint(100, 500)}",
                "city": customer["city"],
                "fuel_type": fuel["name"],
                "fuel_liters": liters,
                "fuel_amount": round(fuel_amount, 2),
                "is_premium_fuel": fuel["is_premium"],
                "market_items": [item["name"] for item in market_items],
                "market_amount": market_amount,
                "total_amount": round(fuel_amount + market_amount, 2),
                "payment_method": random.choice(["card", "cash", "loyalty_points"]),
                "loyalty_points_earned": int((fuel_amount + market_amount) * 0.01) if customer["loyalty_card"] else 0,
            }
            transactions.append(transaction)
    
    return sorted(transactions, key=lambda x: x["timestamp"])


def generate_digital_events(customers, days=90):
    """Dijital etkileşim eventleri oluştur"""
    events = []
    
    start_date = datetime.now() - timedelta(days=days)
    
    for customer in customers:
        # App kullanıcıları daha çok event üretir
        if customer["has_app"]:
            num_events = random.randint(10, 50)
        else:
            num_events = random.randint(0, 10)
        
        for _ in range(num_events):
            event_date = start_date + timedelta(
                days=random.randint(0, days),
                hours=random.randint(7, 23),
                minutes=random.randint(0, 59)
            )
            
            # App kullanıcıları app eventleri üretir
            if customer["has_app"] and random.random() < 0.6:
                event_type = random.choice([e for e in DIGITAL_EVENTS if "app" in e])
            else:
                event_type = random.choice(DIGITAL_EVENTS)
            
            event = {
                "event_id": f"EV{random.randint(10000000, 99999999)}",
                "customer_id": customer["customer_id"],
                "timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
                "event_type": event_type,
                "platform": "app" if "app" in event_type else random.choice(["web", "email", "push"]),
                "device": random.choice(["mobile", "desktop", "tablet"]) if "app" not in event_type else "mobile",
            }
            events.append(event)
    
    return sorted(events, key=lambda x: x["timestamp"])


def save_data(customers, transactions, events, output_dir="data"):
    """Veriyi JSON ve CSV olarak kaydet"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # JSON
    with open(output_path / "customers.json", "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)
    
    with open(output_path / "transactions.json", "w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)
    
    with open(output_path / "events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    
    # CSV
    if customers:
        with open(output_path / "customers.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=customers[0].keys())
            writer.writeheader()
            writer.writerows(customers)
    
    if transactions:
        # Market items'ı string'e çevir
        tx_for_csv = []
        for tx in transactions:
            tx_copy = tx.copy()
            tx_copy["market_items"] = "|".join(tx_copy["market_items"])
            tx_for_csv.append(tx_copy)
        
        with open(output_path / "transactions.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=tx_for_csv[0].keys())
            writer.writeheader()
            writer.writerows(tx_for_csv)
    
    if events:
        with open(output_path / "events.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=events[0].keys())
            writer.writeheader()
            writer.writerows(events)
    
    print(f"✅ Veri kaydedildi: {output_path}")
    print(f"   - {len(customers)} müşteri")
    print(f"   - {len(transactions)} işlem")
    print(f"   - {len(events)} dijital event")


if __name__ == "__main__":
    print("🚀 CDP Demo - Mock Veri Oluşturuluyor...")
    print("-" * 50)
    
    # Veri oluştur
    customers = generate_customers(1000)
    transactions = generate_transactions(customers, days=90)
    events = generate_digital_events(customers, days=90)
    
    # Kaydet
    save_data(customers, transactions, events, "data")
    
    # Özet istatistikler
    print("\n📊 Özet İstatistikler:")
    print(f"   Premium müşteri: {len([c for c in customers if c['segment'] == 'premium'])}")
    print(f"   Regular müşteri: {len([c for c in customers if c['segment'] == 'regular'])}")
    print(f"   Occasional müşteri: {len([c for c in customers if c['segment'] == 'occasional'])}")
    print(f"   Premium yakıt işlemleri: {len([t for t in transactions if t['is_premium_fuel']])}")
    print(f"   Market alışverişi olan: {len([t for t in transactions if t['market_amount'] > 0])}")
    print(f"   App kullanıcısı: {len([c for c in customers if c['has_app']])}")
