import pandas as pd
import pvlib
import numpy as np

# The pvlib-python library is a well-validated and community-supported tool for
# modeling photovoltaic systems. It implements a wide range of models for solar
# geometry, irradiance, and PV system performance, many of which were originally
# developed at the National Renewable Energy Laboratory (NREL).
#
# Citations:
# - Holmgren, W. F., Hansen, C. W., and Mikofski, M. A. (2018). "pvlib python:
#   a python package for modeling solar energy systems." Journal of Open
#   Source Software, 3(29), 884. doi:10.21105/joss.00884.
# - The Liu and Jordan model (and its derivatives like the Perez model used here)
#   is a foundational model for estimating solar radiation on tilted surfaces from
#   horizontal data. Duffie, J.A., and Beckman, W.A. (2013). "Solar Engineering
#   of Thermal Processes". 4th Edition. Wiley.


def get_optimal_orientation(latitude, longitude, ground_slope_offset=0):
    """
    Calculates the optimal tilt and azimuth for a given location, accounting for ground slope.

    This function performs a search over a range of tilt and azimuth angles
    to find the orientation that maximizes the total annual plane-of-array (POA)
    irradiance, considering the ground slope offset.

    Mathematical Models Used:
    1. Solar Position Calculations (declination, hour angle, zenith angle, azimuth)
    2. Liu and Jordan Model for irradiance on tilted surfaces
    3. Clear Sky Model (Ineichen-Perez) for atmospheric effects
    4. Ground slope compensation formulas

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        ground_slope_offset (float): Angle between ground surface and horizontal line in degrees.
                                   Positive values indicate upward slope, negative downward.

    Returns:
        dict: A dictionary with 'optimal_tilt', 'optimal_azimuth', 'effective_tilt', and 'annual_irradiance_kwh_m2'.
    """
    # Formula 7: Time Zone Calculation
    # tz_offset = longitude / 15 (15° per hour)
    tz_offset = int(longitude / 15)
    if tz_offset >= 0:
        tz = f'Etc/GMT-{tz_offset}'
    else:
        tz = f'Etc/GMT+{-tz_offset}'

    location = pvlib.location.Location(latitude, longitude, tz=tz)
    
    # Generate time series for one year analysis
    from datetime import datetime, timedelta
    
    today = datetime.now()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=365)
    
    times = pd.date_range(start=start_date, end=end_date, freq='1h', tz=tz)
    
    # Formula 1: Solar Position Calculations
    # pvlib calculates: declination (δ), hour angle (ω), zenith angle (θz), azimuth (γs)
    solar_position = location.get_solarposition(times)
    
    # Formula 5: Clear Sky Model (Ineichen-Perez)
    # Calculates DNI, GHI, DHI using atmospheric models
    clearsky = location.get_clearsky(times, solar_position=solar_position)
    
    # Formula 4: Ground Slope Compensation
    # β_optimal = max(0, min(90, β_ideal - β_ground))
    base_tilts = range(0, 91, 5)
    tilts = [max(0, min(90, tilt - ground_slope_offset)) for tilt in base_tilts]
    tilts = list(set(tilts))  # Remove duplicates
    tilts.sort()
    
    # Formula 8: Hemisphere-Specific Azimuth Ranges
    if latitude >= 0:  # Northern Hemisphere
        azimuths = range(120, 241, 5)  # Search around South (180 deg)
    else:  # Southern Hemisphere
        azimuths = list(range(0, 61, 5)) + list(range(300, 361, 5))

    max_irradiance = 0
    optimal_tilt = 0
    optimal_azimuth = 0

    # Formula 6: Annual Energy Optimization
    # E_annual = Σ(Gt(t) × η × A × Δt)
    for tilt in tilts:
        for azimuth in azimuths:
            # Formula 2: Liu and Jordan Model
            # Gt = Gb + Gd + Gr
            # Where:
            # Gb = Gbn × cos(θ)  (Formula 3: Angle of Incidence)
            # Gd = Gdh × (1 + cos(β)) / 2
            # Gr = (Gbh + Gdh) × ρ × (1 - cos(β)) / 2
            poa_irradiance = pvlib.irradiance.get_total_irradiance(
                surface_tilt=tilt,
                surface_azimuth=azimuth,
                solar_zenith=solar_position['apparent_zenith'],
                solar_azimuth=solar_position['azimuth'],
                dni=clearsky['dni'],
                ghi=clearsky['ghi'],
                dhi=clearsky['dhi']
            )['poa_global']
            
            annual_irradiance = poa_irradiance.sum()
            
            if annual_irradiance > max_irradiance:
                max_irradiance = annual_irradiance
                optimal_tilt = tilt
                optimal_azimuth = azimuth

    # Formula 4: Effective Tilt Calculation
    # β_effective = β_panel + β_ground
    effective_tilt = optimal_tilt + ground_slope_offset

    return {
        'optimal_tilt': optimal_tilt,
        'optimal_azimuth': optimal_azimuth,
        'effective_tilt': effective_tilt,
        'ground_slope_offset': ground_slope_offset,
        'annual_irradiance_kwh_m2': max_irradiance / 1000  # Convert to kWh/m²
    }


def analyze_solar_geometry(latitude, longitude, ground_slope_offset=0):
    """
    Detailed analysis of solar geometry for a given location.
    
    Provides comprehensive solar position data and irradiance analysis
    using the mathematical models described in solar_formulas.md
    
    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        ground_slope_offset (float): Ground slope angle in degrees.
    
    Returns:
        dict: Comprehensive solar analysis including seasonal variations.
    """
    # Use a default timezone based on longitude
    tz_offset = int(longitude / 15)
    if tz_offset >= 0:
        tz = f'Etc/GMT-{tz_offset}'
    else:
        tz = f'Etc/GMT+{-tz_offset}'

    location = pvlib.location.Location(latitude, longitude, tz=tz)
    
    # Analyze key dates: winter solstice, summer solstice, equinoxes from last year
    # In case the topography changes, we can use the last year's key dates to get a baseline.
    from datetime import datetime
    
    current_year = datetime.now().year
    last_year = current_year - 1
    
    key_dates = [
        f'{last_year}-12-21',  # Winter solstice
        f'{last_year}-03-20',  # Spring equinox  
        f'{last_year}-06-21',  # Summer solstice
        f'{last_year}-09-23'   # Fall equinox
    ]
    
    analysis = {}
    
    for date in key_dates:
        times = pd.date_range(start=date, periods=24, freq='1h', tz=tz)
        solar_position = location.get_solarposition(times)
        clearsky = location.get_clearsky(times, solar_position=solar_position)
        
        # Calculate daily energy for optimal orientation
        optimal = get_optimal_orientation(latitude, longitude, ground_slope_offset)
        
        poa_irradiance = pvlib.irradiance.get_total_irradiance(
            surface_tilt=optimal['optimal_tilt'],
            surface_azimuth=optimal['optimal_azimuth'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth'],
            dni=clearsky['dni'],
            ghi=clearsky['ghi'],
            dhi=clearsky['dhi']
        )['poa_global']
        
        # Calculate sunrise and sunset hours
        above_horizon = solar_position['apparent_zenith'] < 90
        if above_horizon.any():
            sunrise_idx = np.where(above_horizon)[0][0]
            sunset_idx = np.where(above_horizon)[0][-1]
            sunrise_hour = pd.to_datetime(times[sunrise_idx]).hour
            sunset_hour = pd.to_datetime(times[sunset_idx]).hour
        else:
            sunrise_hour = None
            sunset_hour = None
        
        analysis[date] = {
            'daily_energy_kwh_m2': poa_irradiance.sum() / 1000,
            'max_zenith_angle': solar_position['apparent_zenith'].max(),
            'min_zenith_angle': solar_position['apparent_zenith'].min(),
            'sunrise_hour': sunrise_hour,
            'sunset_hour': sunset_hour
        }
    
    return analysis


if __name__ == '__main__':
    # Example usage with ground slope offset:
    latitude_ny = 40.7128
    longitude_ny = -74.0060
    
    print("=== Solar Geometry Analysis ===")
    print(f"Location: New York (Lat: {latitude_ny}, Lon: {longitude_ny})")
    print()
    
    # Analysis with 15-degree upward slope
    optimal_ny = get_optimal_orientation(latitude_ny, longitude_ny, 15)
    print(f"Ground Slope: 15° Upward")
    print(f"  Optimal Panel Tilt: {optimal_ny['optimal_tilt']}°")
    print(f"  Optimal Azimuth: {optimal_ny['optimal_azimuth']}°")
    print(f"  Effective Tilt: {optimal_ny['effective_tilt']}°")
    print(f"  Annual Energy: {optimal_ny['annual_irradiance_kwh_m2']:.1f} kWh/m²")
    print()
    
    # Analysis with 10-degree downward slope
    optimal_ny_down = get_optimal_orientation(latitude_ny, longitude_ny, -10)
    print(f"Ground Slope: 10° Downward")
    print(f"  Optimal Panel Tilt: {optimal_ny_down['optimal_tilt']}°")
    print(f"  Optimal Azimuth: {optimal_ny_down['optimal_azimuth']}°")
    print(f"  Effective Tilt: {optimal_ny_down['effective_tilt']}°")
    print(f"  Annual Energy: {optimal_ny_down['annual_irradiance_kwh_m2']:.1f} kWh/m²")
    print()
    
    # Seasonal analysis with ground slope
    seasonal = analyze_solar_geometry(latitude_ny, longitude_ny, 15)
    print("Seasonal Analysis (15° Upward Slope):")
    for date, data in seasonal.items():
        print(f"  {date}: {data['daily_energy_kwh_m2']:.1f} kWh/m²/day")
