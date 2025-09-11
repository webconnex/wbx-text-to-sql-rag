#!/usr/bin/env python3
"""
Mock Data Generator for Webconnex Text-to-SQL Testing
Generates realistic test data for all tables with proper relationships
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from faker import Faker

fake = Faker()


class WebconnexDataGenerator:
    """Generate mock data for Webconnex tables"""
    
    def __init__(self, account_id: int = 12345):
        self.account_id = account_id
        self.fake = Faker()
        self.data = {
            "accounts": [],
            "customers": [],
            "invoices": [],
            "registrations": [],
            "forms": []
        }
        
    def generate_accounts(self, count: int = 5) -> List[Dict]:
        """Generate mock account data"""
        accounts = []
        for i in range(count):
            account = {
                "id": self.account_id + i,
                "name": self.fake.company(),
                "email": self.fake.company_email(),
                "date_created": self.fake.date_time_between(
                    start_date="-2y", end_date="now"
                ).isoformat(),
                "organization_id": random.randint(1, 10),
                "status": random.choice(["active", "trial", "suspended"])
            }
            accounts.append(account)
        
        self.data["accounts"] = accounts
        return accounts
    
    def generate_customers(self, count: int = 100) -> List[Dict]:
        """Generate mock customer data"""
        customers = []
        for i in range(count):
            # 5% of customers are soft-deleted
            date_deleted = None
            if random.random() < 0.05:
                date_deleted = self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                ).isoformat()
            
            customer = {
                "id": 1000 + i,
                "account_id": self.account_id,
                "email": self.fake.email(),
                "mobile_phone": self.fake.phone_number(),
                "date_created": self.fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
                "date_last_login": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                ).isoformat(),
                "date_deleted": date_deleted,
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "city": self.fake.city(),
                "state": self.fake.state_abbr(),
                "country": "US"
            }
            customers.append(customer)
        
        self.data["customers"] = customers
        return customers
    
    def generate_invoices(self, count: int = 200) -> List[Dict]:
        """Generate mock invoice data"""
        invoices = []
        
        # Generate invoices across the last 2 years
        for i in range(count):
            billing_date = self.fake.date_time_between(
                start_date="-2y", end_date="now"
            )
            
            # 85% completed, 15% pending
            status = "completed" if random.random() < 0.85 else "pending"
            
            invoice = {
                "id": 5000 + i,
                "billing_id": random.randint(1, 20),
                "account_id": self.account_id,
                "amount": round(random.uniform(50, 5000), 2),
                "status": status,
                "invoice_number": f"INV-{2024000 + i}",
                "billing_date": billing_date.isoformat(),
                "start_date": billing_date.isoformat(),
                "end_date": (billing_date + timedelta(days=30)).isoformat(),
                "payment_method": random.choice(["credit_card", "ach", "check"]),
                "currency": "USD"
            }
            invoices.append(invoice)
        
        self.data["invoices"] = invoices
        return invoices
    
    def generate_forms(self, count: int = 20) -> List[Dict]:
        """Generate mock form data"""
        forms = []
        
        form_types = [
            "Event Registration",
            "Donation Form",
            "Membership Signup",
            "Product Purchase",
            "Class Enrollment",
            "Volunteer Signup",
            "Newsletter Subscription",
            "Contact Form"
        ]
        
        for i in range(count):
            form = {
                "id": 3000 + i,
                "account_id": self.account_id,
                "name": f"{random.choice(form_types)} - {self.fake.catch_phrase()}",
                "type": random.choice(["event", "donation", "membership", "product"]),
                "status": random.choice(["active", "draft", "archived"]),
                "date_created": self.fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat()
            }
            forms.append(form)
        
        self.data["forms"] = forms
        return forms
    
    def generate_registrations(self, count: int = 500) -> List[Dict]:
        """Generate mock registration data with proper relationships"""
        registrations = []
        
        if not self.data["customers"]:
            self.generate_customers()
        if not self.data["forms"]:
            self.generate_forms()
        
        customer_ids = [c["id"] for c in self.data["customers"] if c["date_deleted"] is None]
        form_ids = [f["id"] for f in self.data["forms"]]
        
        for i in range(count):
            date_created = self.fake.date_time_between(
                start_date="-1y", end_date="now"
            )
            
            # 90% completed, 10% pending
            status = 1 if random.random() < 0.9 else 0
            date_completed = None
            if status == 1:
                date_completed = (date_created + timedelta(
                    minutes=random.randint(1, 60)
                )).isoformat()
            
            registration = {
                "id": 10000 + i,
                "account_id": self.account_id,
                "customer_id": random.choice(customer_ids),
                "form_id": random.choice(form_ids),
                "total": round(random.uniform(25, 1000), 2),
                "status": status,
                "order_number": f"ORD-{datetime.now().year}-{10000 + i}",
                "date_created": date_created.isoformat(),
                "date_completed": date_completed,
                "event_date": (date_created + timedelta(
                    days=random.randint(1, 90)
                )).isoformat(),
                "payment_status": "paid" if status == 1 else "pending",
                "tickets": random.randint(1, 5)
            }
            registrations.append(registration)
        
        self.data["registrations"] = registrations
        return registrations
    
    def generate_time_series_data(self) -> pd.DataFrame:
        """Generate time series data for trend analysis"""
        dates = pd.date_range(start="2023-01-01", end=datetime.now(), freq="D")
        
        # Generate daily metrics with realistic patterns
        daily_data = []
        for date in dates:
            # Add weekly seasonality (weekends are slower)
            weekday_factor = 1.5 if date.weekday() < 5 else 0.7
            
            # Add monthly seasonality
            month_factor = 1.2 if date.month in [3, 9, 11] else 1.0
            
            # Base metrics with noise
            base_registrations = 50 * weekday_factor * month_factor
            base_revenue = 5000 * weekday_factor * month_factor
            
            daily_data.append({
                "date": date,
                "registrations": int(base_registrations + random.gauss(0, 10)),
                "revenue": round(base_revenue + random.gauss(0, 500), 2),
                "new_customers": int(10 * weekday_factor + random.gauss(0, 3)),
                "avg_order_value": round(100 + random.gauss(0, 20), 2)
            })
        
        return pd.DataFrame(daily_data)
    
    def generate_customer_segments(self) -> List[Dict]:
        """Generate customer segmentation data"""
        segments = []
        
        segment_types = [
            ("VIP", 5, 10000, 50000),
            ("Frequent", 10, 5000, 10000),
            ("Regular", 25, 1000, 5000),
            ("Occasional", 35, 100, 1000),
            ("New", 25, 0, 100)
        ]
        
        for seg_name, percentage, min_value, max_value in segment_types:
            count = int((percentage / 100) * len(self.data["customers"]))
            segments.append({
                "segment": seg_name,
                "customer_count": count,
                "percentage": percentage,
                "avg_lifetime_value": round(random.uniform(min_value, max_value), 2),
                "avg_orders": random.randint(1, 20),
                "retention_rate": round(random.uniform(0.3, 0.95), 2)
            })
        
        return segments
    
    def generate_query_response(self, query_type: str) -> Dict[str, Any]:
        """Generate mock response for different query types"""
        
        responses = {
            "count": {
                "query": "SELECT COUNT(*) as count FROM wbx_data.webconnex.customer WHERE account_id = 12345 AND date_deleted IS NULL LIMIT 1000",
                "data": [{"count": len([c for c in self.data["customers"] if c["date_deleted"] is None])}],
                "execution_time": round(random.uniform(0.5, 2.0), 3)
            },
            "revenue": {
                "query": "SELECT SUM(amount) as total_revenue FROM wbx_data.webconnex.invoice WHERE account_id = 12345 AND status = 'completed' LIMIT 1000",
                "data": [{"total_revenue": sum(i["amount"] for i in self.data["invoices"] if i["status"] == "completed")}],
                "execution_time": round(random.uniform(0.8, 2.5), 3)
            },
            "top_customers": {
                "query": """SELECT c.email, COUNT(r.id) as orders, SUM(r.total) as lifetime_value 
                          FROM wbx_data.webconnex.customer c 
                          JOIN wbx_data.webconnex.registration r ON c.id = r.customer_id 
                          WHERE c.account_id = 12345 
                          GROUP BY c.email 
                          ORDER BY lifetime_value DESC 
                          LIMIT 10""",
                "data": self._generate_top_customers(),
                "execution_time": round(random.uniform(1.0, 3.0), 3)
            },
            "monthly_trend": {
                "query": """SELECT DATE_TRUNC('month', billing_date) as month, 
                          SUM(amount) as revenue, COUNT(*) as invoice_count 
                          FROM wbx_data.webconnex.invoice 
                          WHERE account_id = 12345 
                          GROUP BY month 
                          ORDER BY month DESC 
                          LIMIT 12""",
                "data": self._generate_monthly_trend(),
                "execution_time": round(random.uniform(1.2, 3.5), 3)
            }
        }
        
        return responses.get(query_type, responses["count"])
    
    def _generate_top_customers(self) -> List[Dict]:
        """Generate top customers data"""
        top_customers = []
        for i in range(10):
            top_customers.append({
                "email": self.fake.email(),
                "orders": random.randint(5, 50),
                "lifetime_value": round(random.uniform(1000, 10000), 2)
            })
        return sorted(top_customers, key=lambda x: x["lifetime_value"], reverse=True)
    
    def _generate_monthly_trend(self) -> List[Dict]:
        """Generate monthly trend data"""
        monthly_data = []
        current_date = datetime.now()
        
        for i in range(12):
            month = current_date - timedelta(days=30 * i)
            monthly_data.append({
                "month": month.strftime("%Y-%m-01"),
                "revenue": round(random.uniform(50000, 150000), 2),
                "invoice_count": random.randint(100, 300)
            })
        
        return monthly_data
    
    def save_to_json(self, filename: str = "mock_data.json"):
        """Save generated data to JSON file"""
        with open(filename, "w") as f:
            json.dump(self.data, f, indent=2, default=str)
        print(f"✅ Mock data saved to {filename}")
    
    def generate_all(self):
        """Generate all mock data"""
        print("🔄 Generating mock data...")
        
        self.generate_accounts(5)
        print(f"  ✅ Generated {len(self.data['accounts'])} accounts")
        
        self.generate_customers(100)
        print(f"  ✅ Generated {len(self.data['customers'])} customers")
        
        self.generate_forms(20)
        print(f"  ✅ Generated {len(self.data['forms'])} forms")
        
        self.generate_invoices(200)
        print(f"  ✅ Generated {len(self.data['invoices'])} invoices")
        
        self.generate_registrations(500)
        print(f"  ✅ Generated {len(self.data['registrations'])} registrations")
        
        return self.data


def generate_sample_responses():
    """Generate sample API responses for testing"""
    generator = WebconnexDataGenerator()
    generator.generate_all()
    
    print("\n📊 Generating Sample Query Responses...")
    
    # Generate different types of responses
    response_types = ["count", "revenue", "top_customers", "monthly_trend"]
    responses = {}
    
    for response_type in response_types:
        response = generator.generate_query_response(response_type)
        responses[response_type] = response
        print(f"  ✅ Generated {response_type} response")
    
    # Save responses
    with open("sample_responses.json", "w") as f:
        json.dump(responses, f, indent=2, default=str)
    
    print("\n✅ Sample responses saved to sample_responses.json")
    
    # Generate time series data
    print("\n📈 Generating Time Series Data...")
    time_series = generator.generate_time_series_data()
    time_series.to_csv("time_series_data.csv", index=False)
    print(f"  ✅ Generated {len(time_series)} days of time series data")
    
    # Generate customer segments
    print("\n👥 Generating Customer Segments...")
    segments = generator.generate_customer_segments()
    segments_df = pd.DataFrame(segments)
    segments_df.to_csv("customer_segments.csv", index=False)
    print(f"  ✅ Generated {len(segments)} customer segments")
    
    return generator


def main():
    """Main function"""
    print("=" * 60)
    print("WEBCONNEX MOCK DATA GENERATOR")
    print("=" * 60)
    
    # Generate all data
    generator = generate_sample_responses()
    
    # Save main dataset
    generator.save_to_json("mock_webconnex_data.json")
    
    # Print statistics
    print("\n📊 Data Statistics:")
    print(f"  Accounts: {len(generator.data['accounts'])}")
    print(f"  Customers: {len(generator.data['customers'])}")
    print(f"    - Active: {len([c for c in generator.data['customers'] if c['date_deleted'] is None])}")
    print(f"    - Deleted: {len([c for c in generator.data['customers'] if c['date_deleted'] is not None])}")
    print(f"  Forms: {len(generator.data['forms'])}")
    print(f"  Invoices: {len(generator.data['invoices'])}")
    print(f"    - Completed: {len([i for i in generator.data['invoices'] if i['status'] == 'completed'])}")
    print(f"    - Pending: {len([i for i in generator.data['invoices'] if i['status'] == 'pending'])}")
    print(f"  Registrations: {len(generator.data['registrations'])}")
    print(f"    - Completed: {len([r for r in generator.data['registrations'] if r['status'] == 1])}")
    print(f"    - Pending: {len([r for r in generator.data['registrations'] if r['status'] == 0])}")
    
    # Calculate totals
    total_revenue = sum(i["amount"] for i in generator.data["invoices"] if i["status"] == "completed")
    avg_order_value = sum(r["total"] for r in generator.data["registrations"]) / len(generator.data["registrations"])
    
    print(f"\n💰 Financial Summary:")
    print(f"  Total Revenue: ${total_revenue:,.2f}")
    print(f"  Average Order Value: ${avg_order_value:.2f}")
    
    print("\n✅ Mock data generation complete!")
    print("\nGenerated files:")
    print("  - mock_webconnex_data.json (main dataset)")
    print("  - sample_responses.json (API response samples)")
    print("  - time_series_data.csv (daily metrics)")
    print("  - customer_segments.csv (customer segmentation)")


if __name__ == "__main__":
    main()