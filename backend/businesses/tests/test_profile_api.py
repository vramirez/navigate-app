"""
Tests for user profile API endpoint
Task-18.4: Create User Profile API Endpoint
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from businesses.models import Business, BusinessType


@pytest.fixture
def api_client():
    """Create API client for testing"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def business_type(db):
    """Get or create a test business type"""
    business_type, _ = BusinessType.objects.get_or_create(
        code='pub',
        defaults={
            'display_name': 'Pub',
            'display_name_es': 'Bar',
            'icon': '🍺'
        }
    )
    return business_type


@pytest.fixture
def test_business(db, test_user, business_type):
    """Create a test business for the user"""
    return Business.objects.create(
        owner=test_user,
        name='Test Pub',
        business_type=business_type,
        city='Madrid',
        address='Test Street 123',
        neighborhood='Centro',
        latitude=40.4168,
        longitude=-3.7038,
        description='A test pub',
        target_audience='Young professionals',
        is_active=True
    )


@pytest.mark.django_db
class TestUserProfileEndpoint:
    """Test user profile API endpoint"""

    def test_authenticated_user_with_business(self, api_client, test_user, test_business):
        """
        Test profile endpoint returns correct data for authenticated user with business
        """
        # Authenticate the client
        api_client.force_authenticate(user=test_user)

        # Call the endpoint
        response = api_client.get('/api/businesses/auth/profile/')

        # Assert response
        assert response.status_code == status.HTTP_200_OK

        # Check user data
        assert response.data['user']['id'] == test_user.id
        assert response.data['user']['username'] == 'testuser'
        assert response.data['user']['email'] == 'test@example.com'
        assert response.data['user']['first_name'] == 'Test'
        assert response.data['user']['last_name'] == 'User'

        # Check business data
        assert response.data['business'] is not None
        assert response.data['business']['id'] == test_business.id
        assert response.data['business']['name'] == 'Test Pub'
        assert response.data['business']['business_type'] == test_business.business_type.id

        # Check business_type_details nested data
        assert response.data['business']['business_type_details'] is not None
        assert response.data['business']['business_type_details']['code'] == 'pub'
        # Note: display_name might vary based on database seed data
        assert 'display_name' in response.data['business']['business_type_details']
        assert 'icon' in response.data['business']['business_type_details']

        # Check business_type_code quick access
        assert response.data['business_type_code'] == 'pub'

    def test_authenticated_user_without_business(self, api_client, test_user):
        """
        Test profile endpoint handles users without businesses gracefully
        """
        # Authenticate the client
        api_client.force_authenticate(user=test_user)

        # Call the endpoint
        response = api_client.get('/api/businesses/auth/profile/')

        # Assert response
        assert response.status_code == status.HTTP_200_OK

        # Check user data is present
        assert response.data['user']['id'] == test_user.id
        assert response.data['user']['username'] == 'testuser'

        # Check business data is None
        assert response.data['business'] is None
        assert response.data['business_type_code'] is None

    def test_unauthenticated_request(self, api_client):
        """
        Test profile endpoint returns 403 for unauthenticated requests
        """
        # Call endpoint without authentication
        response = api_client.get('/api/businesses/auth/profile/')

        # Assert 403 Forbidden (IsAuthenticated permission)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_inactive_business_not_returned(self, api_client, test_user, test_business):
        """
        Test that inactive businesses are not returned
        """
        # Mark business as inactive
        test_business.is_active = False
        test_business.save()

        # Authenticate and call endpoint
        api_client.force_authenticate(user=test_user)
        response = api_client.get('/api/businesses/auth/profile/')

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['business'] is None
        assert response.data['business_type_code'] is None

    def test_multiple_businesses_returns_active_one(self, api_client, test_user, business_type):
        """
        Test that only active business is returned when user has multiple businesses
        """
        # Create an inactive business
        Business.objects.create(
            owner=test_user,
            name='Inactive Pub',
            business_type=business_type,
            city='Madrid',
            is_active=False
        )

        # Create an active business
        active_business = Business.objects.create(
            owner=test_user,
            name='Active Pub',
            business_type=business_type,
            city='Madrid',
            is_active=True
        )

        # Authenticate and call endpoint
        api_client.force_authenticate(user=test_user)
        response = api_client.get('/api/businesses/auth/profile/')

        # Assert active business is returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['business']['id'] == active_business.id
        assert response.data['business']['name'] == 'Active Pub'
        assert response.data['business_type_code'] == 'pub'

    def test_response_structure(self, api_client, test_user, test_business):
        """
        Test that response has all expected fields in correct structure
        """
        api_client.force_authenticate(user=test_user)
        response = api_client.get('/api/businesses/auth/profile/')

        assert response.status_code == status.HTTP_200_OK

        # Check top-level keys
        assert 'user' in response.data
        assert 'business' in response.data
        assert 'business_type_code' in response.data

        # Check user keys
        user_data = response.data['user']
        assert 'id' in user_data
        assert 'username' in user_data
        assert 'email' in user_data
        assert 'first_name' in user_data
        assert 'last_name' in user_data

        # Check business has business_type_details
        business_data = response.data['business']
        assert 'business_type_details' in business_data
        assert 'code' in business_data['business_type_details']
        assert 'display_name' in business_data['business_type_details']
        assert 'icon' in business_data['business_type_details']
