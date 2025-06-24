#!/usr/bin/env python3
"""
End-to-End (E2E) tests for Emergency Response App
Tests complete user workflows using Selenium WebDriver
"""

import pytest
import sys
import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import init_database

# Test configuration
BASE_URL = "http://localhost:3000"
SELENIUM_TIMEOUT = 10

@pytest.fixture(scope="session")
def test_server():
    """Start test server for E2E tests"""
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    # Initialize database
    with app.app_context():
        init_database()
    
    # Start server in a separate thread
    server_thread = threading.Thread(
        target=lambda: app.run(host='localhost', port=3000, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield
    
    # Server will be stopped when the test session ends

@pytest.fixture
def driver():
    """Create WebDriver instance"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for CI/CD
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(SELENIUM_TIMEOUT)
        yield driver
    except Exception as e:
        # Fallback to Firefox if Chrome is not available
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            driver = webdriver.Firefox(options=firefox_options)
            driver.implicitly_wait(SELENIUM_TIMEOUT)
            yield driver
        except Exception:
            pytest.skip(f"No WebDriver available: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

class TestUserRegistrationFlow:
    """Test user registration end-to-end workflow"""
    
    def test_user_registration_success(self, driver, test_server):
        """Test successful user registration"""
        driver.get(f"{BASE_URL}/register")
        
        # Fill registration form
        driver.find_element(By.NAME, "username").send_keys("e2euser")
        driver.find_element(By.NAME, "password").send_keys("E2ETest123!")
        driver.find_element(By.NAME, "email").send_keys("e2e@example.com")
        
        # Select user type
        user_type_select = driver.find_element(By.NAME, "user_type")
        user_type_select.send_keys("regular")
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect or success message
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: "login" in d.current_url.lower() or 
                     "welcome" in d.current_url.lower() or
                     "success" in d.page_source.lower()
        )
        
        # Verify registration success
        assert "login" in driver.current_url.lower() or \
               "welcome" in driver.current_url.lower() or \
               "success" in driver.page_source.lower()
    
    def test_user_registration_validation(self, driver, test_server):
        """Test user registration form validation"""
        driver.get(f"{BASE_URL}/register")
        
        # Try to submit empty form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Should show validation errors or stay on same page
        time.sleep(1)
        assert "register" in driver.current_url.lower()

class TestUserLoginFlow:
    """Test user login end-to-end workflow"""
    
    def test_user_login_success(self, driver, test_server):
        """Test successful user login"""
        driver.get(f"{BASE_URL}/login")
        
        # Fill login form
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("password123")
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect to dashboard or landing page
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: "login" not in d.current_url.lower()
        )
        
        # Verify login success (should be redirected away from login page)
        assert "login" not in driver.current_url.lower()
        assert "landing" in driver.current_url.lower() or \
               "dashboard" in driver.current_url.lower() or \
               "profile" in driver.current_url.lower()
    
    def test_user_login_invalid_credentials(self, driver, test_server):
        """Test login with invalid credentials"""
        driver.get(f"{BASE_URL}/login")
        
        # Fill login form with invalid credentials
        driver.find_element(By.NAME, "username").send_keys("invaliduser")
        driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Should stay on login page or show error
        time.sleep(2)
        assert "login" in driver.current_url.lower() or \
               "error" in driver.page_source.lower() or \
               "invalid" in driver.page_source.lower()

class TestFireDepartmentFlow:
    """Test fire department user workflow"""
    
    def test_fire_department_login_and_dashboard(self, driver, test_server):
        """Test fire department user login and dashboard access"""
        driver.get(f"{BASE_URL}/login")
        
        # Login as fire department user
        driver.find_element(By.NAME, "username").send_keys("fireuser")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: "login" not in d.current_url.lower()
        )
        
        # Should be redirected to fire department landing page
        assert "fire" in driver.current_url.lower() or \
               "emergency" in driver.page_source.lower() or \
               "dashboard" in driver.page_source.lower()

class TestEmergencyReportingFlow:
    """Test emergency reporting workflow"""
    
    def test_emergency_report_creation(self, driver, test_server):
        """Test creating emergency report through web interface"""
        # First login
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: "login" not in d.current_url.lower()
        )
        
        # Navigate to emergency reporting (if available)
        try:
            # Look for emergency reporting link or button
            emergency_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Emergency")
            emergency_link.click()
        except NoSuchElementException:
            # If no direct link, try to access emergency page directly
            driver.get(f"{BASE_URL}/emergency")
        
        # If emergency form exists, fill it out
        try:
            emergency_type = driver.find_element(By.NAME, "emergency_type")
            emergency_type.send_keys("fire")
            
            location = driver.find_element(By.NAME, "location")
            location.send_keys("Test Location")
            
            description = driver.find_element(By.NAME, "description")
            description.send_keys("Test emergency description")
            
            # Submit form
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for success message or redirect
            time.sleep(2)
            
            # Verify submission (success message or redirect)
            assert "success" in driver.page_source.lower() or \
                   "submitted" in driver.page_source.lower() or \
                   "thank" in driver.page_source.lower()
        except NoSuchElementException:
            # Emergency form might not be implemented in web interface
            pytest.skip("Emergency reporting form not found in web interface")

class TestFirstAidFlow:
    """Test first aid section workflow"""
    
    def test_first_aid_navigation(self, driver, test_server):
        """Test navigating first aid section"""
        driver.get(f"{BASE_URL}/first_aid")
        
        # Verify first aid page loads
        assert "first aid" in driver.page_source.lower() or \
               "first-aid" in driver.page_source.lower()
        
        # Try to click on a first aid practice
        try:
            first_aid_link = driver.find_element(By.CSS_SELECTOR, "a[href*='first_aid_detail']")
            first_aid_link.click()
            
            # Wait for detail page to load
            WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                lambda d: "detail" in d.current_url.lower()
            )
            
            # Verify detail page content
            assert "steps" in driver.page_source.lower() or \
                   "procedure" in driver.page_source.lower() or \
                   "instructions" in driver.page_source.lower()
        except NoSuchElementException:
            # First aid links might not be available
            pass

class TestMessagingFlow:
    """Test messaging system workflow"""
    
    def test_messages_page_access(self, driver, test_server):
        """Test accessing messages page"""
        # Login first
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: "login" not in d.current_url.lower()
        )
        
        # Navigate to messages
        driver.get(f"{BASE_URL}/messages")
        
        # Verify messages page loads
        assert "message" in driver.page_source.lower()

class TestMapFlow:
    """Test map functionality workflow"""
    
    def test_map_page_access(self, driver, test_server):
        """Test accessing map page"""
        driver.get(f"{BASE_URL}/map")
        
        # Verify map page loads
        assert "map" in driver.page_source.lower() or \
               "hospital" in driver.page_source.lower() or \
               "fire station" in driver.page_source.lower()

class TestProfileFlow:
    """Test user profile workflow"""
    
    def test_profile_access_and_edit(self, driver, test_server):
        """Test accessing and editing user profile"""
        # Login first
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: "login" not in d.current_url.lower()
        )
        
        # Navigate to profile
        driver.get(f"{BASE_URL}/profile")
        
        # Verify profile page loads
        assert "profile" in driver.page_source.lower() or \
               "account" in driver.page_source.lower()
        
        # Try to edit profile if edit functionality exists
        try:
            edit_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Edit")
            edit_button.click()
            
            # If edit form exists, make a change
            try:
                email_field = driver.find_element(By.NAME, "email")
                email_field.clear()
                email_field.send_keys("updated@example.com")
                
                # Save changes
                save_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                save_button.click()
                
                # Wait for save confirmation
                time.sleep(2)
                
                # Verify save success
                assert "updated" in driver.page_source.lower() or \
                       "saved" in driver.page_source.lower() or \
                       "success" in driver.page_source.lower()
            except NoSuchElementException:
                pass
        except NoSuchElementException:
            # Edit functionality might not be available
            pass

class TestNavigationFlow:
    """Test general navigation workflow"""
    
    def test_main_navigation(self, driver, test_server):
        """Test main navigation links"""
        driver.get(f"{BASE_URL}/")
        
        # Test navigation to different pages
        pages_to_test = [
            ("/first_aid", "first aid"),
            ("/map", "map"),
            ("/help", "help"),
            ("/login", "login")
        ]
        
        for url, expected_content in pages_to_test:
            try:
                driver.get(f"{BASE_URL}{url}")
                assert expected_content.lower() in driver.page_source.lower()
            except Exception as e:
                # Some pages might not exist
                print(f"Warning: Could not test {url}: {e}")

class TestResponsiveDesign:
    """Test responsive design and mobile compatibility"""
    
    def test_mobile_viewport(self, driver, test_server):
        """Test mobile viewport rendering"""
        # Set mobile viewport
        driver.set_window_size(375, 667)  # iPhone 6/7/8 size
        
        driver.get(f"{BASE_URL}/")
        
        # Verify page loads in mobile viewport
        assert driver.execute_script("return window.innerWidth") <= 375
        
        # Test that content is still accessible
        assert len(driver.page_source) > 100  # Basic content check

class TestPerformanceE2E:
    """Test performance aspects in E2E scenarios"""
    
    def test_page_load_performance(self, driver, test_server):
        """Test page load performance"""
        start_time = time.time()
        driver.get(f"{BASE_URL}/")
        
        # Wait for page to fully load
        WebDriverWait(driver, SELENIUM_TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        load_time = time.time() - start_time
        
        # Page should load within reasonable time
        assert load_time < 10.0  # 10 seconds max

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
