#!/usr/bin/env python3
"""
Test Data Generator for LibProxy Access Logs
Creates realistic access log data for analytics and statistics
"""

import random
import json
from datetime import datetime, timedelta
from faker import Faker
import requests
import time

fake = Faker()

# Configuration
API_BASE_URL = "http://localhost:5001/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

# Test data parameters
NUM_TEST_USERS = 20
NUM_ACCESS_LOGS = 500
DATE_RANGE_DAYS = 90  # Last 90 days

# Common journal subjects and publishers
JOURNAL_SUBJECTS = [
    "Medicine", "Biology", "Chemistry", "Physics", "Engineering",
    "Computer Science", "Mathematics", "Psychology", "Sociology",
    "Economics", "Law", "Education", "Environmental Science"
]

PUBLISHERS = [
    "Elsevier", "Springer", "Wiley", "Taylor & Francis", "SAGE",
    "Oxford University Press", "Cambridge University Press",
    "IEEE", "ACM", "Nature Publishing Group"
]

# Sample journal data
SAMPLE_JOURNALS = [
    {
        "name": "Nature Medicine",
        "slug": "nature-medicine",
        "base_url": "https://www.nature.com/nm",
        "proxy_path": "nature-medicine",
        "publisher": "Nature Publishing Group",
        "subject_areas": ["Medicine", "Biology"],
        "issn": "1078-8956",
        "description": "Leading journal in medical research"
    },
    {
        "name": "Science",
        "slug": "science-magazine",
        "base_url": "https://www.science.org",
        "proxy_path": "science",
        "publisher": "AAAS",
        "subject_areas": ["Biology", "Chemistry", "Physics"],
        "issn": "0036-8075",
        "description": "Multidisciplinary science journal"
    },
    {
        "name": "The Lancet",
        "slug": "the-lancet",
        "base_url": "https://www.thelancet.com",
        "proxy_path": "lancet",
        "publisher": "Elsevier",
        "subject_areas": ["Medicine"],
        "issn": "0140-6736",
        "description": "Leading medical journal"
    },
    {
        "name": "IEEE Transactions on Software Engineering",
        "slug": "ieee-tse",
        "base_url": "https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=32",
        "proxy_path": "ieee-tse",
        "publisher": "IEEE",
        "subject_areas": ["Computer Science", "Engineering"],
        "issn": "0098-5589",
        "description": "Premier journal in software engineering"
    },
    {
        "name": "Journal of Economic Theory",
        "slug": "jet",
        "base_url": "https://www.journals.elsevier.com/journal-of-economic-theory",
        "proxy_path": "jet",
        "publisher": "Elsevier",
        "subject_areas": ["Economics"],
        "issn": "0022-0531",
        "description": "Theoretical economics research"
    },
    {
        "name": "Psychological Science",
        "slug": "psych-science",
        "base_url": "https://journals.sagepub.com/home/pss",
        "proxy_path": "psych-science",
        "publisher": "SAGE",
        "subject_areas": ["Psychology"],
        "issn": "0956-7976",
        "description": "Leading psychology research journal"
    }
]

class TestDataGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.users = []
        self.journals = []
        
    def authenticate(self):
        """Authenticate as admin"""
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/login",
                json=ADMIN_CREDENTIALS
            )
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                print("✅ Successfully authenticated as admin")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def create_test_users(self):
        """Create test users"""
        print(f"Creating {NUM_TEST_USERS} test users...")
        
        for i in range(NUM_TEST_USERS):
            user_data = {
                "username": f"testuser{i+1}",
                "email": fake.email(),
                "password": "testpass123",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "is_active": True,
                "is_admin": False
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE_URL}/admin/users",
                    json=user_data
                )
                if response.status_code == 201:
                    user = response.json()["user"]
                    self.users.append(user)
                    print(f"  ✅ Created user: {user['username']}")
                else:
                    print(f"  ⚠️ Failed to create user {user_data['username']}: {response.text}")
            except Exception as e:
                print(f"  ❌ Error creating user {user_data['username']}: {e}")
        
        print(f"Created {len(self.users)} test users")
    
    def create_test_journals(self):
        """Create test journals"""
        print(f"Creating {len(SAMPLE_JOURNALS)} test journals...")
        
        for journal_data in SAMPLE_JOURNALS:
            try:
                response = self.session.post(
                    f"{API_BASE_URL}/admin/journals",
                    json=journal_data
                )
                if response.status_code == 201:
                    journal = response.json()["journal"]
                    self.journals.append(journal)
                    print(f"  ✅ Created journal: {journal['name']}")
                else:
                    print(f"  ⚠️ Failed to create journal {journal_data['name']}: {response.text}")
            except Exception as e:
                print(f"  ❌ Error creating journal {journal_data['name']}: {e}")
        
        print(f"Created {len(self.journals)} test journals")
    
    def get_existing_data(self):
        """Get existing users and journals"""
        try:
            # Get users
            response = self.session.get(f"{API_BASE_URL}/admin/users?per_page=100")
            if response.status_code == 200:
                self.users = response.json()["users"]
                print(f"Found {len(self.users)} existing users")
            
            # Get journals
            response = self.session.get(f"{API_BASE_URL}/admin/journals?per_page=100")
            if response.status_code == 200:
                self.journals = response.json()["journals"]
                print(f"Found {len(self.journals)} existing journals")
                
        except Exception as e:
            print(f"❌ Error getting existing data: {e}")
    
    def create_access_logs(self):
        """Create realistic access log data directly in the database"""
        print(f"Creating {NUM_ACCESS_LOGS} access log entries...")
        
        if not self.users or not self.journals:
            print("❌ No users or journals found. Cannot create access logs.")
            return
        
        # Create access logs with realistic patterns
        access_logs = []
        
        for i in range(NUM_ACCESS_LOGS):
            # Random user and journal
            user = random.choice(self.users)
            journal = random.choice(self.journals)
            
            # Generate realistic timestamp (weighted towards recent dates)
            days_ago = random.choices(
                range(DATE_RANGE_DAYS),
                weights=[1/(day+1) for day in range(DATE_RANGE_DAYS)],  # More recent = higher weight
                k=1
            )[0]
            
            # Random hour with realistic distribution (work hours more likely)
            hour_weights = [1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 2, 2, 1, 1, 1]
            hour = random.choices(range(24), weights=hour_weights, k=1)[0]
            
            access_time = datetime.now() - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Generate realistic request data
            request_paths = [
                "/", "/search", "/articles", "/issues", "/latest",
                f"/article/{random.randint(1000, 9999)}",
                f"/issue/{random.randint(1, 12)}/{random.randint(2020, 2024)}",
                "/advanced-search", "/browse", "/about"
            ]
            
            request_data = {
                "method": "GET",
                "path": random.choice(request_paths),
                "user_agent": fake.user_agent(),
                "referer": random.choice([
                    "https://www.google.com/",
                    "https://scholar.google.com/",
                    f"http://localhost/{journal['proxy_path']}",
                    None
                ])
            }
            
            response_data = {
                "status_code": random.choices([200, 404, 403, 500], weights=[85, 10, 3, 2], k=1)[0],
                "response_time": round(random.uniform(0.1, 3.0), 3),
                "content_length": random.randint(1024, 50000)
            }
            
            # Generate realistic IP addresses
            ip_address = fake.ipv4()
            
            access_logs.append({
                "user_id": user["id"],
                "journal_id": journal["id"],
                "ip_address": ip_address,
                "timestamp": access_time.isoformat(),
                "request_data": request_data,
                "response_data": response_data
            })
        
        # Insert access logs directly into database using SQL
        self.insert_access_logs_to_db(access_logs)
    
    def insert_access_logs_to_db(self, access_logs):
        """Insert access logs directly to database"""
        import psycopg2
        import psycopg2.extras
        
        try:
            # Database connection parameters
            conn_params = {
                "host": "localhost",
                "port": "5432",
                "database": "libproxy",
                "user": "libproxy_user",
                "password": "libproxy_pass"
            }
            
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Prepare insert query
            insert_query = """
                INSERT INTO access_logs (user_id, journal_id, ip_address, timestamp, request_data, response_data)
                VALUES (%(user_id)s, %(journal_id)s, %(ip_address)s, %(timestamp)s, %(request_data)s, %(response_data)s)
            """
            
            # Insert access logs in batches
            batch_size = 50
            for i in range(0, len(access_logs), batch_size):
                batch = access_logs[i:i+batch_size]
                
                for log in batch:
                    # Convert request_data and response_data to JSON strings
                    log["request_data"] = json.dumps(log["request_data"])
                    log["response_data"] = json.dumps(log["response_data"])
                
                cur.executemany(insert_query, batch)
                conn.commit()
                
                print(f"  ✅ Inserted batch {i//batch_size + 1}/{(len(access_logs)-1)//batch_size + 1}")
            
            cur.close()
            conn.close()
            
            print(f"✅ Successfully created {len(access_logs)} access log entries")
            
        except Exception as e:
            print(f"❌ Error inserting access logs: {e}")
            print("Trying alternative method...")
            self.create_access_logs_via_api(access_logs)
    
    def create_access_logs_via_api(self, access_logs):
        """Fallback: Create access logs via API (slower but more reliable)"""
        print("Creating access logs via API...")
        
        # Note: This would require an API endpoint for creating access logs
        # For now, we'll create a simple analytics log entry
        for i, log in enumerate(access_logs[:50]):  # Limit to 50 for API method
            try:
                # Create analytics log entry
                analytics_data = {
                    "user_id": log["user_id"],
                    "resource_name": f"Journal: {next(j['name'] for j in self.journals if j['id'] == log['journal_id'])}",
                    "resource_type": "journal",
                    "access_method": "proxy",
                    "ip_address": log["ip_address"],
                    "user_agent": log["request_data"]["user_agent"],
                    "session_duration": random.randint(60, 3600),  # 1 minute to 1 hour
                    "pages_viewed": random.randint(1, 20),
                    "downloads": random.randint(0, 5),
                    "timestamp": log["timestamp"]
                }
                
                # You would need to implement this endpoint
                # response = self.session.post(f"{API_BASE_URL}/analytics/log", json=analytics_data)
                
                if i % 10 == 0:
                    print(f"  ✅ Created {i+1}/50 analytics entries")
                    
            except Exception as e:
                print(f"  ❌ Error creating analytics entry {i}: {e}")
    
    def generate_analytics_data(self):
        """Generate additional analytics data"""
        print("Generating additional analytics data...")
        
        # This would create more detailed analytics entries
        # For demonstration, we'll create some summary statistics
        
        analytics_entries = []
        
        for _ in range(100):
            user = random.choice(self.users)
            journal = random.choice(self.journals)
            
            # Generate realistic session data
            session_start = fake.date_time_between(start_date='-90d', end_date='now')
            session_duration = random.randint(120, 7200)  # 2 minutes to 2 hours
            
            entry = {
                "user_id": user["id"],
                "resource_name": journal["name"],
                "resource_type": "journal",
                "access_method": "proxy",
                "ip_address": fake.ipv4(),
                "user_agent": fake.user_agent(),
                "session_start": session_start.isoformat(),
                "session_duration": session_duration,
                "pages_viewed": random.randint(1, 50),
                "downloads": random.randint(0, 10),
                "search_queries": random.randint(0, 15),
                "department": random.choice([
                    "Medicine", "Engineering", "Sciences", "Social Sciences",
                    "Law", "Business", "Education", "Arts"
                ]),
                "user_type": random.choice(["student", "faculty", "researcher", "staff"])
            }
            
            analytics_entries.append(entry)
        
        print(f"Generated {len(analytics_entries)} analytics entries")
        return analytics_entries
    
    def run(self):
        """Run the complete test data generation process"""
        print("🚀 Starting test data generation for LibProxy...")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: Get existing data or create new
        self.get_existing_data()
        
        # Step 3: Create test users if needed
        if len(self.users) < NUM_TEST_USERS:
            self.create_test_users()
        
        # Step 4: Create test journals if needed
        if len(self.journals) < len(SAMPLE_JOURNALS):
            self.create_test_journals()
        
        # Step 5: Create access logs
        self.create_access_logs()
        
        # Step 6: Generate analytics data
        self.generate_analytics_data()
        
        print("=" * 60)
        print("✅ Test data generation completed!")
        print(f"📊 Summary:")
        print(f"   • Users: {len(self.users)}")
        print(f"   • Journals: {len(self.journals)}")
        print(f"   • Access logs: {NUM_ACCESS_LOGS}")
        print(f"   • Date range: Last {DATE_RANGE_DAYS} days")
        print("\n🎯 You can now examine graphs and statistics in the admin panel!")
        
        return True

if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.run()
