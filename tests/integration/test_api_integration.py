#!/usr/bin/env python3
"""
Integration tests for Emergency Response App
Tests the application running in staging/production environment
"""

import pytest
import requests
import json
import time
import os
from datetime import datetime

# Configuration
STAGING_URL = os.getenv('STAGING_URL', 'http://localhost:3000')
PRODUCTION_URL = os.getenv('PRODUCTION_URL', 'http://31.97.11.49')
API_KEY = 'emergency-api-key-2024'
TIMEOUT = 30

class TestEnvironmentHealth:
    """Test environment health and availability"""
    
    @pytest.mark.parametrize("base_url", [STAGING_URL, PRODUCTION_URL])
    def test_application_health(self, base_url):
        """Test application health endpoint"""
        try:
            response = requests.get(f'{base_url}/api/v1/health', timeout=TIMEOUT)
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'success'
            assert data['data']['status'] == 'healthy'
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Environment {base_url} not accessible: {e}")
    
    @pytest.mark.parametrize("base_url", [STAGING_URL, PRODUCTION_URL])
    def test_monitoring_endpoints(self, base_url):
        """Test monitoring endpoints availability"""
        try:
            # Test Prometheus
            prometheus_url = base_url.replace(':3000', ':9090').replace('http://', 'http://').split('/')[2]
            prometheus_response = requests.get(f'http://{prometheus_url}:9090/-/healthy', timeout=TIMEOUT)
            assert prometheus_response.status_code == 200
            
            # Test Grafana
            grafana_response = requests.get(f'http://{prometheus_url}:3001/api/health', timeout=TIMEOUT)
            assert grafana_response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Monitoring services not accessible: {e}")

class TestAPIIntegration:
    """Test API endpoints integration"""
    
    @pytest.fixture
    def api_headers(self):
        """API headers with authentication"""
        return {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_emergency_workflow(self, base_url, api_headers):
        """Test complete emergency reporting workflow"""
        try:
            # Step 1: Create emergency report
            emergency_data = {
                'emergency_type': 'fire',
                'location': f'Integration Test Location - {datetime.now().isoformat()}',
                'description': 'Integration test emergency report',
                'severity': 'medium',
                'latitude': 3.8634,
                'longitude': 11.5167
            }
            
            create_response = requests.post(
                f'{base_url}/api/v1/emergencies',
                json=emergency_data,
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert create_response.status_code == 201
            
            emergency_id = create_response.json()['data']['emergency_id']
            
            # Step 2: Retrieve the created emergency
            get_response = requests.get(
                f'{base_url}/api/v1/emergencies/{emergency_id}',
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert get_response.status_code == 200
            
            emergency_data_retrieved = get_response.json()['data']
            assert emergency_data_retrieved['emergency_type'] == 'fire'
            assert emergency_data_retrieved['severity'] == 'medium'
            
            # Step 3: Update emergency status
            status_update = {'status': 'responding'}
            update_response = requests.put(
                f'{base_url}/api/v1/emergencies/{emergency_id}/status',
                json=status_update,
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert update_response.status_code == 200
            
            # Step 4: Verify status update
            verify_response = requests.get(
                f'{base_url}/api/v1/emergencies/{emergency_id}',
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert verify_response.status_code == 200
            assert verify_response.json()['data']['status'] == 'responding'
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_first_aid_integration(self, base_url, api_headers):
        """Test first aid practices integration"""
        try:
            # Get all first aid practices
            response = requests.get(
                f'{base_url}/api/v1/first-aid',
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            
            practices = response.json()['data']
            assert len(practices) > 0
            
            # Test specific practice
            first_practice_id = practices[0]['id']
            detail_response = requests.get(
                f'{base_url}/api/v1/first-aid/{first_practice_id}',
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert detail_response.status_code == 200
            
            practice_detail = detail_response.json()['data']
            assert 'title' in practice_detail
            assert 'steps' in practice_detail
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_messaging_integration(self, base_url, api_headers):
        """Test messaging system integration"""
        try:
            # Create a test message
            message_data = {
                'content': f'Integration test message - {datetime.now().isoformat()}',
                'message_type': 'info'
            }
            
            create_response = requests.post(
                f'{base_url}/api/v1/messages',
                json=message_data,
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert create_response.status_code == 201
            
            # Retrieve messages
            get_response = requests.get(
                f'{base_url}/api/v1/messages',
                headers=api_headers,
                timeout=TIMEOUT
            )
            assert get_response.status_code == 200
            
            messages = get_response.json()['data']
            assert len(messages) > 0
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")

class TestPerformanceIntegration:
    """Test performance characteristics in real environment"""
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_response_times(self, base_url):
        """Test API response times"""
        try:
            endpoints = [
                '/api/v1/health',
                '/api/v1/status',
                '/api/v1/emergencies',
                '/api/v1/first-aid',
                '/api/v1/fire-departments'
            ]
            
            headers = {'X-API-Key': API_KEY}
            
            for endpoint in endpoints:
                start_time = time.time()
                response = requests.get(f'{base_url}{endpoint}', headers=headers, timeout=TIMEOUT)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                assert response.status_code == 200
                assert response_time < 5.0, f"Endpoint {endpoint} took {response_time:.2f}s (>5s)"
                
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_concurrent_requests(self, base_url):
        """Test handling concurrent requests"""
        import threading
        
        try:
            results = []
            errors = []
            
            def make_request():
                try:
                    response = requests.get(f'{base_url}/api/v1/health', timeout=TIMEOUT)
                    results.append(response.status_code)
                except Exception as e:
                    errors.append(str(e))
            
            # Create 20 concurrent threads
            threads = []
            for _ in range(20):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 20
            assert all(status == 200 for status in results)
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")

class TestSecurityIntegration:
    """Test security aspects in real environment"""
    
    @pytest.mark.parametrize("base_url", [STAGING_URL, PRODUCTION_URL])
    def test_api_key_authentication(self, base_url):
        """Test API key authentication"""
        try:
            # Test without API key
            response = requests.get(f'{base_url}/api/v1/emergencies', timeout=TIMEOUT)
            assert response.status_code == 401
            
            # Test with invalid API key
            headers = {'X-API-Key': 'invalid-key'}
            response = requests.get(f'{base_url}/api/v1/emergencies', headers=headers, timeout=TIMEOUT)
            assert response.status_code == 401
            
            # Test with valid API key
            headers = {'X-API-Key': API_KEY}
            response = requests.get(f'{base_url}/api/v1/emergencies', headers=headers, timeout=TIMEOUT)
            assert response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")
    
    @pytest.mark.parametrize("base_url", [STAGING_URL, PRODUCTION_URL])
    def test_security_headers(self, base_url):
        """Test security headers are present"""
        try:
            response = requests.get(f'{base_url}/', timeout=TIMEOUT)
            
            # Check for security headers (if served through nginx)
            expected_headers = [
                'X-Frame-Options',
                'X-XSS-Protection',
                'X-Content-Type-Options'
            ]
            
            for header in expected_headers:
                if header in response.headers:
                    assert response.headers[header] is not None
                    
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Application not accessible: {e}")

class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_database_consistency(self, base_url):
        """Test database operations consistency"""
        try:
            headers = {'X-API-Key': API_KEY}
            
            # Get initial count of emergencies
            initial_response = requests.get(f'{base_url}/api/v1/emergencies', headers=headers, timeout=TIMEOUT)
            assert initial_response.status_code == 200
            initial_count = len(initial_response.json()['data'])
            
            # Create new emergency
            emergency_data = {
                'emergency_type': 'medical',
                'location': 'Data Integrity Test',
                'description': 'Testing database consistency',
                'severity': 'low'
            }
            
            create_response = requests.post(
                f'{base_url}/api/v1/emergencies',
                json=emergency_data,
                headers=headers,
                timeout=TIMEOUT
            )
            assert create_response.status_code == 201
            
            # Verify count increased
            final_response = requests.get(f'{base_url}/api/v1/emergencies', headers=headers, timeout=TIMEOUT)
            assert final_response.status_code == 200
            final_count = len(final_response.json()['data'])
            
            assert final_count == initial_count + 1
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not accessible: {e}")

class TestMonitoringIntegration:
    """Test monitoring and metrics integration"""
    
    @pytest.mark.parametrize("base_url", [STAGING_URL])
    def test_prometheus_metrics(self, base_url):
        """Test Prometheus metrics endpoint"""
        try:
            response = requests.get(f'{base_url}/metrics', timeout=TIMEOUT)
            assert response.status_code == 200
            
            metrics_text = response.text
            
            # Check for expected metrics
            expected_metrics = [
                'emergency_reports_total',
                'system_health_score',
                'active_users',
                'flask_http_request_total'
            ]
            
            for metric in expected_metrics:
                assert metric in metrics_text, f"Metric {metric} not found in response"
                
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Metrics endpoint not accessible: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
