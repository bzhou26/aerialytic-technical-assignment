import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from aerialytic.pv_modeling.optimal_orientation import get_optimal_orientation


@pytest.fixture
def test_coordinates():
    """Test coordinate fixtures"""
    return {
        'latitude_ny': 40.7128,
        'longitude_ny': -74.0060,
        'latitude_sydney': -33.8688,
        'longitude_sydney': 151.2093
    }


class TestOptimalOrientation:
    
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.location.Location')
    @patch('aerialytic.pv_modeling.optimal_orientation.pd.date_range')
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.irradiance.get_total_irradiance')
    def test_get_optimal_orientation_northern_hemisphere(self, mock_irradiance, mock_date_range, mock_location, test_coordinates):
        mock_loc = MagicMock()
        mock_location.return_value = mock_loc
        
        mock_solar_position = pd.DataFrame({
            'apparent_zenith': [45.0] * 8760,  # 1 year of hourly data
            'azimuth': [180.0] * 8760
        })
        mock_loc.get_solarposition.return_value = mock_solar_position
        
        mock_clearsky = pd.DataFrame({
            'dni': [800.0] * 8760,
            'ghi': [600.0] * 8760,
            'dhi': [100.0] * 8760
        })
        mock_loc.get_clearsky.return_value = mock_clearsky
        
        mock_times = pd.date_range(start='2024-01-01', periods=8760, freq='1H')
        mock_date_range.return_value = mock_times
        
        mock_poa = pd.Series([500.0] * 8760)
        mock_irradiance.return_value = {'poa_global': mock_poa}
        
        result = get_optimal_orientation(test_coordinates['latitude_ny'], test_coordinates['longitude_ny'], 0.0)
        
        assert isinstance(result, dict)
        assert 'optimal_tilt' in result
        assert 'optimal_azimuth' in result
        assert 'effective_tilt' in result
        assert 'ground_slope_offset' in result
        assert 'annual_irradiance_kwh_m2' in result
        
        assert result['optimal_tilt'] >= 0
        assert result['optimal_tilt'] <= 90
        assert result['optimal_azimuth'] >= 90
        assert result['optimal_azimuth'] <= 270
        assert result['annual_irradiance_kwh_m2'] > 0
        
        mock_location.assert_called_once()
        assert mock_date_range.called
        mock_loc.get_solarposition.assert_called_once()
        mock_loc.get_clearsky.assert_called_once()
    
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.location.Location')
    @patch('aerialytic.pv_modeling.optimal_orientation.pd.date_range')
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.irradiance.get_total_irradiance')
    def test_get_optimal_orientation_southern_hemisphere(self, mock_irradiance, mock_date_range, mock_location, test_coordinates):
        """Test optimal orientation calculation for Southern Hemisphere"""
        mock_loc = MagicMock()
        mock_location.return_value = mock_loc
        
        mock_solar_position = pd.DataFrame({
            'apparent_zenith': [45.0] * 8760,
            'azimuth': [0.0] * 8760
        })
        mock_loc.get_solarposition.return_value = mock_solar_position
        
        mock_clearsky = pd.DataFrame({
            'dni': [800.0] * 8760,
            'ghi': [600.0] * 8760,
            'dhi': [100.0] * 8760
        })
        mock_loc.get_clearsky.return_value = mock_clearsky
        
        mock_times = pd.date_range(start='2024-01-01', periods=8760, freq='1H')
        mock_date_range.return_value = mock_times
        
        mock_poa = pd.Series([500.0] * 8760)
        mock_irradiance.return_value = {'poa_global': mock_poa}
        
        result = get_optimal_orientation(test_coordinates['latitude_sydney'], test_coordinates['longitude_sydney'], 0.0)
        
        assert isinstance(result, dict)
        assert 'optimal_tilt' in result
        assert 'optimal_azimuth' in result
        assert 'effective_tilt' in result
        
        assert result['optimal_tilt'] >= 0
        assert result['optimal_tilt'] <= 90
        assert (
            (result['optimal_azimuth'] >= 270 and result['optimal_azimuth'] <= 360) or
            (result['optimal_azimuth'] >= 0 and result['optimal_azimuth'] <= 90)
        )
        
        mock_location.assert_called_once()
        assert mock_date_range.called
        mock_loc.get_solarposition.assert_called_once()
        mock_loc.get_clearsky.assert_called_once()
    
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.location.Location')
    @patch('aerialytic.pv_modeling.optimal_orientation.pd.date_range')
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.irradiance.get_total_irradiance')
    def test_get_optimal_orientation_with_positive_offset(self, mock_irradiance, mock_date_range, mock_location, test_coordinates):
        """Test optimal orientation with positive ground slope offset"""
        mock_loc = MagicMock()
        mock_location.return_value = mock_loc
        
        mock_solar_position = pd.DataFrame({
            'apparent_zenith': [45.0] * 8760,
            'azimuth': [180.0] * 8760
        })
        mock_loc.get_solarposition.return_value = mock_solar_position
        
        mock_clearsky = pd.DataFrame({
            'dni': [800.0] * 8760,
            'ghi': [600.0] * 8760,
            'dhi': [100.0] * 8760
        })
        mock_loc.get_clearsky.return_value = mock_clearsky
        
        mock_times = pd.date_range(start='2024-01-01', periods=8760, freq='1H')
        mock_date_range.return_value = mock_times
        
        mock_poa = pd.Series([500.0] * 8760)
        mock_irradiance.return_value = {'poa_global': mock_poa}
        
        offset = 15.0
        result = get_optimal_orientation(test_coordinates['latitude_ny'], test_coordinates['longitude_ny'], offset)
        
        assert result['ground_slope_offset'] == offset
        assert result['effective_tilt'] == result['optimal_tilt'] + offset
        
        assert result['effective_tilt'] >= 0
        assert result['effective_tilt'] <= 105  # max 90 + 15
        
        mock_location.assert_called_once()
        assert mock_date_range.called
        mock_loc.get_solarposition.assert_called_once()
        mock_loc.get_clearsky.assert_called_once()
    
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.location.Location')
    @patch('aerialytic.pv_modeling.optimal_orientation.pd.date_range')
    @patch('aerialytic.pv_modeling.optimal_orientation.pvlib.irradiance.get_total_irradiance')
    def test_get_optimal_orientation_with_negative_offset(self, mock_irradiance, mock_date_range, mock_location, test_coordinates):
        mock_loc = MagicMock()
        mock_location.return_value = mock_loc
        
        mock_solar_position = pd.DataFrame({
            'apparent_zenith': [45.0] * 8760,
            'azimuth': [180.0] * 8760
        })
        mock_loc.get_solarposition.return_value = mock_solar_position
        
        mock_clearsky = pd.DataFrame({
            'dni': [800.0] * 8760,
            'ghi': [600.0] * 8760,
            'dhi': [100.0] * 8760
        })
        mock_loc.get_clearsky.return_value = mock_clearsky
        
        mock_times = pd.date_range(start='2024-01-01', periods=8760, freq='1H')
        mock_date_range.return_value = mock_times
        
        mock_poa = pd.Series([500.0] * 8760)
        mock_irradiance.return_value = {'poa_global': mock_poa}
        
        offset = -10.0
        result = get_optimal_orientation(test_coordinates['latitude_ny'], test_coordinates['longitude_ny'], offset)
        
        assert result['ground_slope_offset'] == offset
        assert result['effective_tilt'] == result['optimal_tilt'] + offset
        
        assert result['effective_tilt'] >= -10
        assert result['effective_tilt'] <= 80  # max 90 - 10
        
        mock_location.assert_called_once()
        assert mock_date_range.called
        mock_loc.get_solarposition.assert_called_once()
        mock_loc.get_clearsky.assert_called_once()
    
    def test_get_optimal_orientation_type_hints(self, test_coordinates):        
        with patch('aerialytic.pv_modeling.optimal_orientation.pvlib.location.Location') as mock_location, \
             patch('aerialytic.pv_modeling.optimal_orientation.pd.date_range') as mock_date_range, \
             patch('aerialytic.pv_modeling.optimal_orientation.pvlib.irradiance.get_total_irradiance') as mock_irradiance:
            
            mock_loc = MagicMock()
            mock_location.return_value = mock_loc
            
            mock_solar_position = pd.DataFrame({
                'apparent_zenith': [45.0] * 8760,
                'azimuth': [180.0] * 8760
            })
            mock_loc.get_solarposition.return_value = mock_solar_position
            
            mock_clearsky = pd.DataFrame({
                'dni': [800.0] * 8760,
                'ghi': [600.0] * 8760,
                'dhi': [100.0] * 8760
            })
            mock_loc.get_clearsky.return_value = mock_clearsky
            
            mock_times = pd.date_range(start='2024-01-01', periods=8760, freq='1H')
            mock_date_range.return_value = mock_times
            
            mock_poa = pd.Series([500.0] * 8760)
            mock_irradiance.return_value = {'poa_global': mock_poa}
            
            result = get_optimal_orientation(40.7128, -74.0060, 15.0)
            
            assert isinstance(result, dict)
    
    def test_get_optimal_orientation_edge_cases(self, test_coordinates):
        """Test edge cases for optimal orientation calculation"""
        with patch('aerialytic.pv_modeling.optimal_orientation.pvlib.location.Location') as mock_location, \
             patch('aerialytic.pv_modeling.optimal_orientation.pd.date_range') as mock_date_range, \
             patch('aerialytic.pv_modeling.optimal_orientation.pvlib.irradiance.get_total_irradiance') as mock_irradiance:
            
            mock_loc = MagicMock()
            mock_location.return_value = mock_loc
            
            mock_solar_position = pd.DataFrame({
                'apparent_zenith': [45.0] * 8760,
                'azimuth': [180.0] * 8760
            })
            mock_loc.get_solarposition.return_value = mock_solar_position
            
            mock_clearsky = pd.DataFrame({
                'dni': [800.0] * 8760,
                'ghi': [600.0] * 8760,
                'dhi': [100.0] * 8760
            })
            mock_loc.get_clearsky.return_value = mock_clearsky
            
            mock_times = pd.date_range(start='2024-01-01', periods=8760, freq='1H')
            mock_date_range.return_value = mock_times
            
            mock_poa = pd.Series([500.0] * 8760)
            mock_irradiance.return_value = {'poa_global': mock_poa}
            
            result_equator = get_optimal_orientation(0.0, 0.0, 0.0)
            assert isinstance(result_equator, dict)
            
            result_north_pole = get_optimal_orientation(90.0, 0.0, 0.0)
            assert isinstance(result_north_pole, dict)
            
            result_south_pole = get_optimal_orientation(-90.0, 0.0, 0.0)
            assert isinstance(result_south_pole, dict)
            
            result_max_offset = get_optimal_orientation(40.0, -74.0, 90.0)
            assert isinstance(result_max_offset, dict)
            
            result_min_offset = get_optimal_orientation(40.0, -74.0, -90.0)
            assert isinstance(result_min_offset, dict) 