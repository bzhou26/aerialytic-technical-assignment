import json
import pytest
from django.test import Client
from unittest.mock import patch


@pytest.fixture
def client():
    """Django test client fixture"""
    return Client()


@pytest.fixture
def solar_geometry_url():
    """URL for solar geometry API"""
    return '/api/solar-geometry'


@pytest.fixture
def test_api_url():
    """URL for test API"""
    return '/api/test'


class TestSolarGeometryAPIView:
    """Tests for the solar geometry API view"""
    
    def test_valid_coordinates_no_offset(self, client, solar_geometry_url):
        """Test API with valid coordinates and no offset"""
        data = {
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        
        with patch('aerialytic.views.get_optimal_orientation') as mock_func:
            mock_result = {
                'optimal_tilt': 35.0,
                'optimal_azimuth': 180.0,
                'effective_tilt': 35.0,
                'annual_irradiance_kwh_m2': 1500.5
            }
            mock_func.return_value = mock_result
            
            response = client.post(
                solar_geometry_url,
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.content)
            
            # Use approximate comparison for floating point values
            assert abs(result['latitude'] - 40.7128) < 0.001
            assert abs(result['longitude'] - (-74.0060)) < 0.001
            assert result['offset'] == 0.0
            assert result['optimal_tilt'] == 35.0
            assert result['optimal_azimuth'] == 180.0
            assert result['effective_tilt'] == 35.0
            assert result['annual_irradiance_kwh_m2'] == 1500.5
            
            # Check that the function was called with the correct arguments
            mock_func.assert_called_once()
            call_args = mock_func.call_args[0]
            assert abs(call_args[0] - 40.7128) < 0.001  # latitude
            assert abs(call_args[1] - (-74.0060)) < 0.001  # longitude
            assert call_args[2] == 0.0  # offset
    
    def test_valid_coordinates_with_offset(self, client, solar_geometry_url):
        """Test API with valid coordinates and positive offset"""
        data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'offset': 15.0
        }
        
        with patch('aerialytic.views.get_optimal_orientation') as mock_func:
            mock_result = {
                'optimal_tilt': 20.0,
                'optimal_azimuth': 180.0,
                'effective_tilt': 35.0,
                'annual_irradiance_kwh_m2': 1450.2
            }
            mock_func.return_value = mock_result
            
            response = client.post(
                solar_geometry_url,
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.content)
            
            assert result['offset'] == 15.0
            assert result['optimal_tilt'] == 20.0
            assert result['effective_tilt'] == 35.0
            
            # Check that the function was called with the correct arguments
            mock_func.assert_called_once()
            call_args = mock_func.call_args[0]
            assert abs(call_args[0] - 40.7128) < 0.001  # latitude
            assert abs(call_args[1] - (-74.0060)) < 0.001  # longitude
            assert call_args[2] == 15.0  # offset
    
    def test_null_offset(self, client, solar_geometry_url):
        """Test API with null offset value"""
        data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'offset': None
        }
        
        with patch('aerialytic.views.get_optimal_orientation') as mock_func:
            mock_result = {
                'optimal_tilt': 35.0,
                'optimal_azimuth': 180.0,
                'effective_tilt': 35.0,
                'annual_irradiance_kwh_m2': 1500.5
            }
            mock_func.return_value = mock_result
            
            response = client.post(
                solar_geometry_url,
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.content)
            assert result['offset'] == 0.0
            
            # Check that the function was called with the correct arguments
            mock_func.assert_called_once()
            call_args = mock_func.call_args[0]
            assert abs(call_args[0] - 40.7128) < 0.001  # latitude
            assert abs(call_args[1] - (-74.0060)) < 0.001  # longitude
            assert call_args[2] == 0.0  # offset
    
    def test_coordinate_normalization(self, client, solar_geometry_url):
        """Test coordinate normalization for out-of-range values"""
        data = {
            'latitude': 95.0,  # Should normalize to 85.0
            'longitude': 185.0,  # Should normalize to -175.0
            'offset': 0.0
        }
        
        with patch('aerialytic.views.get_optimal_orientation') as mock_func:
            mock_result = {
                'optimal_tilt': 35.0,
                'optimal_azimuth': 180.0,
                'effective_tilt': 35.0,
                'annual_irradiance_kwh_m2': 1500.5
            }
            mock_func.return_value = mock_result
            
            response = client.post(
                solar_geometry_url,
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.content)
            
            # Check that coordinates were normalized correctly
            # For latitude 95°, normalization should give 85° (not -85°)
            assert abs(result['latitude'] - 85.0) < 0.001
            assert abs(result['longitude'] - (-175.0)) < 0.001
            
            # Check that the function was called with the normalized coordinates
            mock_func.assert_called_once()
            call_args = mock_func.call_args[0]
            assert abs(call_args[0] - 85.0) < 0.001  # normalized latitude
            assert abs(call_args[1] - (-175.0)) < 0.001  # normalized longitude
            assert call_args[2] == 0.0  # offset
    
    def test_invalid_latitude_range(self, client, solar_geometry_url):
        """Test API with latitude outside valid range"""
        data = {
            'latitude': 500.0,  # Outside -360 to 360 range
            'longitude': -74.0060,
            'offset': 0.0
        }
        
        response = client.post(
            solar_geometry_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'Latitude must be between -360 and 360' in result['error']
    
    def test_invalid_longitude_range(self, client, solar_geometry_url):
        """Test API with longitude outside valid range"""
        data = {
            'latitude': 40.7128,
            'longitude': 500.0,  # Outside -360 to 360 range
            'offset': 0.0
        }
        
        response = client.post(
            solar_geometry_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'Longitude must be between -360 and 360' in result['error']
    
    def test_invalid_offset_range(self, client, solar_geometry_url):
        """Test API with offset outside valid range"""
        data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'offset': 95.0  # Outside -90 to 90 range
        }
        
        response = client.post(
            solar_geometry_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'Offset (ground slope) must be between -90 and 90 degrees' in result['error']
    
    def test_missing_latitude(self, client, solar_geometry_url):
        """Test API with missing latitude"""
        data = {
            'longitude': -74.0060,
            'offset': 0.0
        }
        
        response = client.post(
            solar_geometry_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'Missing required parameter: latitude' in result['error']
    
    def test_missing_longitude(self, client, solar_geometry_url):
        """Test API with missing longitude"""
        data = {
            'latitude': 40.7128,
            'offset': 0.0
        }
        
        response = client.post(
            solar_geometry_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'Missing required parameter: longitude' in result['error']
    
    def test_invalid_json(self, client, solar_geometry_url):
        """Test API with invalid JSON"""
        response = client.post(
            solar_geometry_url,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'error' in result
    
    def test_get_method_not_allowed(self, client, solar_geometry_url):
        """Test that GET method is not allowed"""
        response = client.get(solar_geometry_url)
        assert response.status_code == 405  # Method Not Allowed


class TestTestAPIView:
    """Tests for the test API view"""
    
    def test_valid_date(self, client, test_api_url):
        """Test test API with valid date"""
        data = {'date': '2024-01-15'}
        
        response = client.post(
            test_api_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['result'] == 'received: 2024-01-15'
    
    def test_invalid_json(self, client, test_api_url):
        """Test test API with invalid JSON"""
        response = client.post(
            test_api_url,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert 'error' in result 