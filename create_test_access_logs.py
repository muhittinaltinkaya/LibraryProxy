#!/usr/bin/env python3
import sys
import os
sys.path.append('/app')

import random
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.journal import Journal
from app.models.access_log import AccessLog

def create_test_data():
    app = create_app()
    
    with app.app_context():
        print('🚀 Creating test access log data...')
        
        # Get existing users and journals
        users = User.query.filter_by(is_active=True).all()
        journals = Journal.query.filter_by(is_active=True).all()
        
        print(f'Found {len(users)} users and {len(journals)} journals')
        
        if not users or not journals:
            print('❌ Need users and journals to create access logs')
            return False
        
        # Create 300 access log entries with realistic patterns
        num_logs = 300
        
        for i in range(num_logs):
            user = random.choice(users)
            journal = random.choice(journals)
            
            # Random date in last 60 days with realistic distribution
            # More recent dates have higher probability
            days_ago = random.choices(range(60), weights=[1/(day+1) for day in range(60)])[0]
            
            # Realistic hour distribution (work hours more likely)
            hour_weights = [1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 2, 2, 1, 1, 1]
            hour = random.choices(range(24), weights=hour_weights)[0]
            
            access_time = datetime.utcnow() - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Realistic IP addresses (simulate different subnets)
            ip_prefixes = ['192.168.1.', '192.168.2.', '10.0.0.', '172.16.0.', '172.16.1.']
            ip_address = random.choice(ip_prefixes) + str(random.randint(1, 254))
            
            # Create realistic request data
            paths = [
                '/', '/search', '/articles', '/latest', '/browse', '/about',
                f'/article/{random.randint(1000, 9999)}',
                f'/issue/{random.randint(1, 12)}/{random.randint(2020, 2024)}',
                '/advanced-search', '/download'
            ]
            
            request_data = {
                'method': 'GET',
                'path': random.choice(paths),
                'user_agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ]),
                'referer': random.choice([
                    'https://www.google.com/',
                    'https://scholar.google.com/',
                    f'http://localhost/{journal.proxy_path}',
                    None
                ])
            }
            
            # Create realistic response data
            response_data = {
                'status_code': random.choices([200, 404, 403, 500], weights=[85, 8, 5, 2])[0],
                'response_time': round(random.uniform(0.1, 3.0), 3),
                'content_length': random.randint(1024, 100000)
            }
            
            # Create access log
            access_log = AccessLog(
                user_id=user.id,
                journal_id=journal.id,
                ip_address=ip_address,
                timestamp=access_time,
                request_data=request_data,
                response_data=response_data
            )
            
            db.session.add(access_log)
            
            if (i + 1) % 50 == 0:
                db.session.commit()
                print(f'✅ Created {i + 1}/{num_logs} access logs')
        
        db.session.commit()
        print(f'🎉 Successfully created {num_logs} access log entries!')
        
        # Create some analytics logs as well
        print('📈 Creating analytics log entries...')
        
        from app.models.analytics_log import AnalyticsLog
        
        for i in range(100):
            user = random.choice(users)
            journal = random.choice(journals)
            
            # Random date in last 30 days
            access_time = datetime.utcnow() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            analytics_log = AnalyticsLog(
                user_id=user.id,
                resource_name=journal.name,
                resource_type='journal',
                access_method='proxy',
                ip_address=ip_address,
                user_agent=request_data['user_agent'],
                session_duration=random.randint(60, 3600),  # 1 minute to 1 hour
                pages_viewed=random.randint(1, 20),
                downloads=random.randint(0, 5),
                timestamp=access_time
            )
            
            db.session.add(analytics_log)
        
        db.session.commit()
        print('✅ Created 100 analytics log entries!')
        
        print('📊 Test data creation completed! You can now check:')
        print('   • Admin Panel → Analytics')
        print('   • Admin Panel → Access Logs')
        print('   • Admin Panel → Statistics')
        
        return True

if __name__ == '__main__':
    create_test_data()
