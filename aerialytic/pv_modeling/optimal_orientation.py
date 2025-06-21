import pandas as pd
import pvlib
from datetime import datetime, timedelta


# Citations:
# - Holmgren, W. F., Hansen, C. W., and Mikofski, M. A. (2018). "pvlib python:
#   a python package for modeling solar energy systems." Journal of Open
#   Source Software, 3(29), 884. doi:10.21105/joss.00884.
# - The Liu and Jordan model (and its derivatives like the Perez model used here)
#   is a foundational model for estimating solar radiation on tilted surfaces from
#   horizontal data. Duffie, J.A., and Beckman, W.A. (2013). "Solar Engineering
#   of Thermal Processes". 4th Edition. Wiley.


def get_optimal_orientation(latitude: float, longitude: float, ground_slope_offset: float = 0.0) -> dict:
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
    tilts = list(set(tilts))
    tilts.sort()
    
    # Formula 8: Hemisphere-Specific Azimuth Ranges
    if latitude >= 0:  # Northern Hemisphere
        azimuths = range(90, 271, 5)  # 180-degree range centered on South (180 deg)
    else:  # Southern Hemisphere
        azimuths = range(270, 451, 5)  # 180-degree range centered on North (0/360 deg)
        # Wrap around 360 degrees
        azimuths = [az % 360 for az in azimuths]

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



if __name__ == '__main__':
    # Example usage with ground slope offset:
    latitude_ny = 40.7128
    longitude_ny = -74.0060
    
    print("=== Solar Geometry Analysis ===")
    print(f"Location: New York (Lat: {latitude_ny}, Lon: {longitude_ny})")
    print()
    
    optimal_ny = get_optimal_orientation(latitude_ny, longitude_ny, 15)
    print(f"Ground Slope: 15° Upward")
    print(f"  Optimal Panel Tilt: {optimal_ny['optimal_tilt']}°")
    print(f"  Optimal Azimuth: {optimal_ny['optimal_azimuth']}°")
    print(f"  Effective Tilt: {optimal_ny['effective_tilt']}°")
    print(f"  Annual Energy: {optimal_ny['annual_irradiance_kwh_m2']:.1f} kWh/m²")
    print()

    optimal_ny_down = get_optimal_orientation(latitude_ny, longitude_ny, -10)
    print(f"Ground Slope: 10° Downward")
    print(f"  Optimal Panel Tilt: {optimal_ny_down['optimal_tilt']}°")
    print(f"  Optimal Azimuth: {optimal_ny_down['optimal_azimuth']}°")
    print(f"  Effective Tilt: {optimal_ny_down['effective_tilt']}°")
    print(f"  Annual Energy: {optimal_ny_down['annual_irradiance_kwh_m2']:.1f} kWh/m²")
    print()
    
