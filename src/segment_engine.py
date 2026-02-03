"""
CDP Demo - Segmentasyon Motoru
Müşteri verisi üzerinde segment tanımlama ve çalıştırma
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class SegmentDefinition:
    """Segment tanımı"""
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    logic: str = "AND"  # AND veya OR


class SegmentEngine:
    """CDP Segmentasyon Motoru"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.customers = []
        self.transactions = []
        self.events = []
        self._load_data()
    
    def _load_data(self):
        """Veriyi yükle"""
        with open(self.data_dir / "customers.json", "r", encoding="utf-8") as f:
            self.customers = json.load(f)
        
        with open(self.data_dir / "transactions.json", "r", encoding="utf-8") as f:
            self.transactions = json.load(f)
        
        with open(self.data_dir / "events.json", "r", encoding="utf-8") as f:
            self.events = json.load(f)
        
        # Müşteri bazlı indexler oluştur
        self._build_indexes()
    
    def _build_indexes(self):
        """Hızlı erişim için indexler oluştur"""
        # Müşteri ID -> Müşteri
        self.customer_map = {c["customer_id"]: c for c in self.customers}
        
        # Müşteri ID -> İşlemler
        self.customer_transactions = {}
        for tx in self.transactions:
            cid = tx["customer_id"]
            if cid not in self.customer_transactions:
                self.customer_transactions[cid] = []
            self.customer_transactions[cid].append(tx)
        
        # Müşteri ID -> Events
        self.customer_events = {}
        for ev in self.events:
            cid = ev["customer_id"]
            if cid not in self.customer_events:
                self.customer_events[cid] = []
            self.customer_events[cid].append(ev)
    
    def _evaluate_condition(self, customer: Dict, condition: Dict) -> bool:
        """Tek bir koşulu değerlendir"""
        field = condition["field"]
        operator = condition["operator"]
        value = condition["value"]
        
        # Profil alanları
        if field in customer:
            customer_value = customer[field]
            return self._compare(customer_value, operator, value)
        
        # Agregasyon alanları (işlem bazlı)
        if field.startswith("tx_"):
            return self._evaluate_transaction_condition(customer, field, operator, value, condition)
        
        # Event alanları
        if field.startswith("event_"):
            return self._evaluate_event_condition(customer, field, operator, value, condition)
        
        return False
    
    def _evaluate_transaction_condition(self, customer: Dict, field: str, operator: str, value: Any, condition: Dict) -> bool:
        """İşlem bazlı koşulları değerlendir"""
        cid = customer["customer_id"]
        transactions = self.customer_transactions.get(cid, [])
        
        # Zaman filtresi
        if "days" in condition:
            cutoff = datetime.now() - timedelta(days=condition["days"])
            transactions = [
                tx for tx in transactions 
                if datetime.strptime(tx["timestamp"], "%Y-%m-%d %H:%M:%S") >= cutoff
            ]
        
        # Ek filtre (örn: sadece premium yakıt)
        if "filter" in condition:
            filter_field = condition["filter"]["field"]
            filter_value = condition["filter"]["value"]
            transactions = [tx for tx in transactions if tx.get(filter_field) == filter_value]
        
        if field == "tx_count":
            return self._compare(len(transactions), operator, value)
        
        elif field == "tx_total_amount":
            total = sum(tx["total_amount"] for tx in transactions)
            return self._compare(total, operator, value)
        
        elif field == "tx_avg_amount":
            if not transactions:
                return False
            avg = sum(tx["total_amount"] for tx in transactions) / len(transactions)
            return self._compare(avg, operator, value)
        
        elif field == "tx_last_days":
            if not transactions:
                return self._compare(9999, operator, value)  # Hiç işlem yoksa çok eski say
            last_tx = max(transactions, key=lambda x: x["timestamp"])
            days_since = (datetime.now() - datetime.strptime(last_tx["timestamp"], "%Y-%m-%d %H:%M:%S")).days
            return self._compare(days_since, operator, value)
        
        return False
    
    def _evaluate_event_condition(self, customer: Dict, field: str, operator: str, value: Any, condition: Dict) -> bool:
        """Event bazlı koşulları değerlendir"""
        cid = customer["customer_id"]
        events = self.customer_events.get(cid, [])
        
        # Zaman filtresi
        if "days" in condition:
            cutoff = datetime.now() - timedelta(days=condition["days"])
            events = [
                ev for ev in events 
                if datetime.strptime(ev["timestamp"], "%Y-%m-%d %H:%M:%S") >= cutoff
            ]
        
        # Event tipi filtresi
        if "event_type" in condition:
            events = [ev for ev in events if ev["event_type"] == condition["event_type"]]
        
        if field == "event_count":
            return self._compare(len(events), operator, value)
        
        return False
    
    def _compare(self, actual: Any, operator: str, expected: Any) -> bool:
        """Karşılaştırma operatörleri"""
        if operator == "eq" or operator == "==":
            return actual == expected
        elif operator == "ne" or operator == "!=":
            return actual != expected
        elif operator == "gt" or operator == ">":
            return actual > expected
        elif operator == "gte" or operator == ">=":
            return actual >= expected
        elif operator == "lt" or operator == "<":
            return actual < expected
        elif operator == "lte" or operator == "<=":
            return actual <= expected
        elif operator == "in":
            return actual in expected
        elif operator == "contains":
            return expected in actual if isinstance(actual, str) else False
        return False
    
    def run_segment(self, segment: SegmentDefinition) -> List[Dict]:
        """Segment tanımını çalıştır ve eşleşen müşterileri döndür"""
        results = []
        
        for customer in self.customers:
            condition_results = [
                self._evaluate_condition(customer, cond) 
                for cond in segment.conditions
            ]
            
            if segment.logic == "AND":
                match = all(condition_results)
            else:  # OR
                match = any(condition_results)
            
            if match:
                results.append(customer)
        
        return results
    
    def get_segment_stats(self, segment_results: List[Dict]) -> Dict:
        """Segment için istatistikler"""
        if not segment_results:
            return {"count": 0}
        
        customer_ids = {c["customer_id"] for c in segment_results}
        
        # İşlem istatistikleri
        segment_transactions = [
            tx for tx in self.transactions 
            if tx["customer_id"] in customer_ids
        ]
        
        return {
            "count": len(segment_results),
            "percentage": round(len(segment_results) / len(self.customers) * 100, 1),
            "cities": self._count_by_field(segment_results, "city"),
            "avg_age": round(sum(c["age"] for c in segment_results) / len(segment_results), 1),
            "gender_split": self._count_by_field(segment_results, "gender"),
            "has_app_pct": round(sum(1 for c in segment_results if c["has_app"]) / len(segment_results) * 100, 1),
            "total_transactions": len(segment_transactions),
            "total_revenue": round(sum(tx["total_amount"] for tx in segment_transactions), 2),
        }
    
    def _count_by_field(self, data: List[Dict], field: str) -> Dict:
        """Alan bazında sayım"""
        counts = {}
        for item in data:
            val = item.get(field)
            counts[val] = counts.get(val, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


# Hazır segment tanımları
PREDEFINED_SEGMENTS = {
    "premium_fuel_lovers": SegmentDefinition(
        name="Premium Yakıt Severler",
        description="Son 90 günde 3+ kez premium yakıt alan müşteriler",
        conditions=[
            {"field": "tx_count", "operator": ">=", "value": 3, "days": 90, "filter": {"field": "is_premium_fuel", "value": True}},
        ]
    ),
    
    "high_value_customers": SegmentDefinition(
        name="Yüksek Değerli Müşteriler",
        description="Son 90 günde 5000 TL üzeri harcama yapan müşteriler",
        conditions=[
            {"field": "tx_total_amount", "operator": ">=", "value": 5000, "days": 90},
        ]
    ),
    
    "app_active_users": SegmentDefinition(
        name="Aktif App Kullanıcıları",
        description="App'i olan ve son 30 günde 5+ event üreten müşteriler",
        conditions=[
            {"field": "has_app", "operator": "==", "value": True},
            {"field": "event_count", "operator": ">=", "value": 5, "days": 30},
        ]
    ),
    
    "churn_risk": SegmentDefinition(
        name="Churn Riski",
        description="Eskiden düzenli gelip son 60 günde gelmeyen müşteriler",
        conditions=[
            {"field": "segment", "operator": "in", "value": ["premium", "regular"]},
            {"field": "tx_last_days", "operator": ">", "value": 60},
        ]
    ),
    
    "istanbul_premium": SegmentDefinition(
        name="İstanbul Premium",
        description="İstanbul'da yaşayan premium segment müşteriler",
        conditions=[
            {"field": "city", "operator": "==", "value": "İstanbul"},
            {"field": "segment", "operator": "==", "value": "premium"},
        ]
    ),
    
    "market_shoppers": SegmentDefinition(
        name="Market Alışverişçileri",
        description="Son 30 günde 3+ kez market alışverişi yapan müşteriler",
        conditions=[
            {"field": "tx_count", "operator": ">=", "value": 3, "days": 30, "filter": {"field": "market_amount", "value": True}},
        ]
    ),
    
    "email_reachable": SegmentDefinition(
        name="Email ile Ulaşılabilir",
        description="Email opt-in vermiş ve premium segment müşteriler",
        conditions=[
            {"field": "email_opted_in", "operator": "==", "value": True},
            {"field": "segment", "operator": "==", "value": "premium"},
        ]
    ),
}


if __name__ == "__main__":
    print("🎯 CDP Demo - Segmentasyon Motoru")
    print("=" * 60)
    
    # Motor başlat
    engine = SegmentEngine("data")
    print(f"\n📊 Yüklenen veri:")
    print(f"   - {len(engine.customers)} müşteri")
    print(f"   - {len(engine.transactions)} işlem")
    print(f"   - {len(engine.events)} event")
    
    # Tüm hazır segmentleri çalıştır
    print("\n" + "=" * 60)
    print("📋 Hazır Segmentler:")
    print("=" * 60)
    
    for key, segment in PREDEFINED_SEGMENTS.items():
        results = engine.run_segment(segment)
        stats = engine.get_segment_stats(results)
        
        print(f"\n🏷️  {segment.name}")
        print(f"   {segment.description}")
        print(f"   ├── Müşteri sayısı: {stats['count']} ({stats.get('percentage', 0)}%)")
        if stats['count'] > 0:
            print(f"   ├── Toplam gelir: {stats.get('total_revenue', 0):,.0f} TL")
            print(f"   └── App kullanım: %{stats.get('has_app_pct', 0)}")
