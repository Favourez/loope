#!/usr/bin/env python3
"""
Performance and Load tests for Emergency Response App
"""

import pytest
import sys
import os
import time
import threading
import concurrent.futures
import statistics
import json
from unittest.mock import patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import init_database

@pytest.fixture
def performance_client():
    """Create test client for performance testing"""
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_database()
        yield client

@pytest.fixture
def api_headers():
    """API headers with authentication"""
    return {
        'Content-Type': 'application/json',
        'X-API-Key': 'emergency-api-key-2024'
    }

class TestAPIPerformance:
    """Test API endpoint performance"""
    
    def test_health_endpoint_response_time(self, performance_client):
        """Test health endpoint response time"""
        response_times = []
        
        # Warm up
        for _ in range(5):
            performance_client.get('/api/v1/health')
        
        # Measure response times
        for _ in range(20):
            start_time = time.time()
            response = performance_client.get('/api/v1/health')
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Performance assertions
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        print(f"\n📊 Health Endpoint Performance:")
        print(f"   Average: {avg_response_time:.3f}s")
        print(f"   Maximum: {max_response_time:.3f}s")
        print(f"   95th percentile: {p95_response_time:.3f}s")
        
        # Performance requirements
        assert avg_response_time < 0.1, f"Average response time {avg_response_time:.3f}s exceeds 100ms"
        assert max_response_time < 0.5, f"Maximum response time {max_response_time:.3f}s exceeds 500ms"
        assert p95_response_time < 0.2, f"95th percentile {p95_response_time:.3f}s exceeds 200ms"
    
    def test_emergency_api_performance(self, performance_client, api_headers):
        """Test emergency API endpoint performance"""
        response_times = []
        
        # Warm up
        for _ in range(3):
            performance_client.get('/api/v1/emergencies', headers=api_headers)
        
        # Measure response times
        for _ in range(15):
            start_time = time.time()
            response = performance_client.get('/api/v1/emergencies', headers=api_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"\n📊 Emergency API Performance:")
        print(f"   Average: {avg_response_time:.3f}s")
        print(f"   Maximum: {max_response_time:.3f}s")
        
        # Performance requirements
        assert avg_response_time < 0.2, f"Average response time {avg_response_time:.3f}s exceeds 200ms"
        assert max_response_time < 1.0, f"Maximum response time {max_response_time:.3f}s exceeds 1s"
    
    def test_first_aid_api_performance(self, performance_client, api_headers):
        """Test first aid API endpoint performance"""
        response_times = []
        
        # Test getting all first aid practices
        for _ in range(10):
            start_time = time.time()
            response = performance_client.get('/api/v1/first-aid', headers=api_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        
        print(f"\n📊 First Aid API Performance:")
        print(f"   Average: {avg_response_time:.3f}s")
        
        assert avg_response_time < 0.15, f"Average response time {avg_response_time:.3f}s exceeds 150ms"

class TestConcurrentLoad:
    """Test concurrent load handling"""
    
    def test_concurrent_health_checks(self, performance_client):
        """Test concurrent health check requests"""
        num_threads = 10
        requests_per_thread = 5
        results = []
        
        def make_requests():
            thread_results = []
            for _ in range(requests_per_thread):
                start_time = time.time()
                response = performance_client.get('/api/v1/health')
                end_time = time.time()
                
                thread_results.append({
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            return thread_results
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_requests) for _ in range(num_threads)]
            
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        
        # Analyze results
        successful_requests = [r for r in results if r['status_code'] == 200]
        failed_requests = [r for r in results if r['status_code'] != 200]
        
        success_rate = len(successful_requests) / len(results)
        avg_response_time = statistics.mean([r['response_time'] for r in successful_requests])
        
        print(f"\n📊 Concurrent Load Test Results:")
        print(f"   Total requests: {len(results)}")
        print(f"   Successful: {len(successful_requests)}")
        print(f"   Failed: {len(failed_requests)}")
        print(f"   Success rate: {success_rate:.2%}")
        print(f"   Average response time: {avg_response_time:.3f}s")
        
        # Performance requirements
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95%"
        assert avg_response_time < 0.5, f"Average response time {avg_response_time:.3f}s exceeds 500ms"
    
    def test_concurrent_api_requests(self, performance_client, api_headers):
        """Test concurrent API requests"""
        num_threads = 8
        requests_per_thread = 3
        results = []
        
        def make_api_requests():
            thread_results = []
            endpoints = [
                '/api/v1/health',
                '/api/v1/emergencies',
                '/api/v1/first-aid',
                '/api/v1/fire-departments'
            ]
            
            for endpoint in endpoints:
                for _ in range(requests_per_thread):
                    start_time = time.time()
                    if endpoint == '/api/v1/health':
                        response = performance_client.get(endpoint)
                    else:
                        response = performance_client.get(endpoint, headers=api_headers)
                    end_time = time.time()
                    
                    thread_results.append({
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'response_time': end_time - start_time
                    })
            return thread_results
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_api_requests) for _ in range(num_threads)]
            
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        
        # Analyze results by endpoint
        endpoints = set(r['endpoint'] for r in results)
        
        print(f"\n📊 Concurrent API Load Test Results:")
        
        overall_success_rate = len([r for r in results if r['status_code'] == 200]) / len(results)
        
        for endpoint in endpoints:
            endpoint_results = [r for r in results if r['endpoint'] == endpoint]
            successful = [r for r in endpoint_results if r['status_code'] == 200]
            
            if successful:
                success_rate = len(successful) / len(endpoint_results)
                avg_time = statistics.mean([r['response_time'] for r in successful])
                
                print(f"   {endpoint}:")
                print(f"     Success rate: {success_rate:.2%}")
                print(f"     Avg response time: {avg_time:.3f}s")
        
        print(f"   Overall success rate: {overall_success_rate:.2%}")
        
        # Performance requirements
        assert overall_success_rate >= 0.90, f"Overall success rate {overall_success_rate:.2%} below 90%"

class TestDatabasePerformance:
    """Test database performance under load"""
    
    def test_database_connection_performance(self, performance_client):
        """Test database connection performance"""
        from database import get_db_connection
        
        connection_times = []
        
        for _ in range(20):
            start_time = time.time()
            conn = get_db_connection()
            end_time = time.time()
            
            if conn:
                conn.close()
                connection_times.append(end_time - start_time)
        
        if connection_times:
            avg_connection_time = statistics.mean(connection_times)
            max_connection_time = max(connection_times)
            
            print(f"\n📊 Database Connection Performance:")
            print(f"   Average: {avg_connection_time:.3f}s")
            print(f"   Maximum: {max_connection_time:.3f}s")
            
            # Performance requirements
            assert avg_connection_time < 0.05, f"Average connection time {avg_connection_time:.3f}s exceeds 50ms"
            assert max_connection_time < 0.1, f"Maximum connection time {max_connection_time:.3f}s exceeds 100ms"
    
    def test_emergency_creation_performance(self, performance_client, api_headers):
        """Test emergency creation performance"""
        creation_times = []
        
        for i in range(10):
            emergency_data = {
                'emergency_type': 'fire',
                'location': f'Test Location {i}',
                'description': f'Performance test emergency {i}',
                'severity': 'medium',
                'latitude': 3.8634,
                'longitude': 11.5167,
                'reporter_name': f'Test User {i}',
                'reporter_phone': '+237123456789'
            }
            
            start_time = time.time()
            response = performance_client.post('/api/v1/emergencies',
                                             json=emergency_data,
                                             headers=api_headers)
            end_time = time.time()
            
            if response.status_code == 201:
                creation_times.append(end_time - start_time)
        
        if creation_times:
            avg_creation_time = statistics.mean(creation_times)
            max_creation_time = max(creation_times)
            
            print(f"\n📊 Emergency Creation Performance:")
            print(f"   Average: {avg_creation_time:.3f}s")
            print(f"   Maximum: {max_creation_time:.3f}s")
            
            # Performance requirements
            assert avg_creation_time < 0.2, f"Average creation time {avg_creation_time:.3f}s exceeds 200ms"
            assert max_creation_time < 0.5, f"Maximum creation time {max_creation_time:.3f}s exceeds 500ms"

class TestMemoryPerformance:
    """Test memory usage and performance"""
    
    def test_memory_usage_under_load(self, performance_client, api_headers):
        """Test memory usage under sustained load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate sustained load
        for _ in range(100):
            performance_client.get('/api/v1/health')
            performance_client.get('/api/v1/emergencies', headers=api_headers)
            performance_client.get('/api/v1/first-aid', headers=api_headers)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\n📊 Memory Usage:")
        print(f"   Initial: {initial_memory:.2f} MB")
        print(f"   Final: {final_memory:.2f} MB")
        print(f"   Increase: {memory_increase:.2f} MB")
        
        # Memory requirements (should not increase by more than 50MB)
        assert memory_increase < 50, f"Memory increase {memory_increase:.2f} MB exceeds 50 MB"

class TestScalabilityLimits:
    """Test scalability limits"""
    
    def test_maximum_concurrent_users(self, performance_client, api_headers):
        """Test maximum concurrent users the system can handle"""
        max_users = 50  # Start with 50 concurrent users
        success_threshold = 0.95  # 95% success rate required
        
        def simulate_user_session():
            """Simulate a user session with multiple requests"""
            session_results = []
            
            # Simulate user workflow
            endpoints = [
                ('/api/v1/health', {}),
                ('/api/v1/emergencies', api_headers),
                ('/api/v1/first-aid', api_headers),
            ]
            
            for endpoint, headers in endpoints:
                try:
                    start_time = time.time()
                    response = performance_client.get(endpoint, headers=headers)
                    end_time = time.time()
                    
                    session_results.append({
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'response_time': end_time - start_time,
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    session_results.append({
                        'endpoint': endpoint,
                        'status_code': 500,
                        'response_time': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            return session_results
        
        # Execute concurrent user sessions
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_users) as executor:
            futures = [executor.submit(simulate_user_session) for _ in range(max_users)]
            
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        # Analyze results
        total_requests = len(all_results)
        successful_requests = len([r for r in all_results if r['success']])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        avg_response_time = statistics.mean([r['response_time'] for r in all_results if r['success']])
        
        print(f"\n📊 Scalability Test Results ({max_users} concurrent users):")
        print(f"   Total requests: {total_requests}")
        print(f"   Successful requests: {successful_requests}")
        print(f"   Success rate: {success_rate:.2%}")
        print(f"   Average response time: {avg_response_time:.3f}s")
        
        # Scalability requirements
        assert success_rate >= success_threshold, f"Success rate {success_rate:.2%} below {success_threshold:.0%}"
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s exceeds 1s"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
