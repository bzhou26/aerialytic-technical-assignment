# Solar Calculation Formulas and Models

This document explains the mathematical formulas and models used in the solar calculation system.

## 1. Solar Position Calculations

### Solar Declination (δ)
The angle between the sun's rays and the equatorial plane:
```
δ = 23.45° × sin(360° × (284 + n) / 365)
```
Where `n` is the day of the year (1-365).

### Solar Hour Angle (ω)
The angular displacement of the sun east or west of the local meridian:
```
ω = 15° × (t - 12)
```
Where `t` is the solar time in hours.

### Solar Zenith Angle (θz)
The angle between the sun's rays and the vertical:
```
cos(θz) = sin(φ) × sin(δ) + cos(φ) × cos(δ) × cos(ω)
```
Where `φ` is the latitude.

### Solar Azimuth Angle (γs)
The angle between the sun's projection on the horizontal plane and the south direction:
```
cos(γs) = (sin(δ) × cos(φ) - cos(δ) × sin(φ) × cos(ω)) / sin(θz)
```

## 2. Liu and Jordan Model (Isotropic Sky Model)

The Liu and Jordan model is used to calculate the total irradiance on a tilted surface from horizontal irradiance data.

### Beam Component (Gb)
Direct normal irradiance on tilted surface:
```
Gb = Gbn × cos(θ)
```
Where:
- `Gbn` = Direct Normal Irradiance (DNI)
- `θ` = Angle of incidence between sun's rays and surface normal

### Diffuse Component (Gd)
Isotropic diffuse irradiance on tilted surface:
```
Gd = Gdh × (1 + cos(β)) / 2
```
Where:
- `Gdh` = Horizontal Diffuse Irradiance
- `β` = Surface tilt angle

### Reflected Component (Gr)
Ground-reflected irradiance:
```
Gr = (Gbh + Gdh) × ρ × (1 - cos(β)) / 2
```
Where:
- `Gbh` = Horizontal Beam Irradiance
- `ρ` = Ground albedo (typically 0.2 for grass, 0.8 for snow)

### Total Irradiance on Tilted Surface (Gt)
```
Gt = Gb + Gd + Gr
```

## 3. Angle of Incidence (θ)

The angle between the sun's rays and the surface normal:
```
cos(θ) = cos(θz) × cos(β) + sin(θz) × sin(β) × cos(γs - γ)
```
Where:
- `θz` = Solar zenith angle
- `β` = Surface tilt angle
- `γs` = Solar azimuth angle
- `γ` = Surface azimuth angle

## 4. Ground Slope Compensation

When accounting for ground slope, the effective tilt angle becomes:
```
β_effective = β_panel + β_ground
```
Where:
- `β_panel` = Panel tilt angle relative to ground
- `β_ground` = Ground slope angle (positive for upward slope)

The optimal panel tilt is adjusted to compensate for ground slope:
```
β_optimal = max(0, min(90, β_ideal - β_ground))
```

## 5. Clear Sky Model (Ineichen-Perez)

The clear sky model estimates irradiance under clear sky conditions:

### Direct Normal Irradiance (DNI)
```
DNI = A × exp(-B / cos(θz))
```
Where:
- `A` = Apparent extraterrestrial irradiance
- `B` = Rayleigh optical depth at air mass 2

### Global Horizontal Irradiance (GHI)
```
GHI = DNI × cos(θz) + DHI
```

### Diffuse Horizontal Irradiance (DHI)
```
DHI = DNI × (C1 + C2 × cos(θz) + C3 × cos²(θz))
```
Where C1, C2, C3 are empirical coefficients.

## 6. Annual Energy Optimization

The optimization algorithm maximizes the total annual energy:
```
E_annual = Σ(Gt(t) × η × A × Δt)
```
Where:
- `Gt(t)` = Total irradiance at time t
- `η` = System efficiency
- `A` = Panel area
- `Δt` = Time interval (1 hour)

## 7. Time Zone Calculation

Approximate timezone from longitude:
```
tz_offset = longitude / 15
```
Where 15° represents one hour of time difference.

## 8. Hemisphere-Specific Azimuth Ranges

### Northern Hemisphere
Optimal azimuth range: 120° to 240° (around South at 180°)

### Southern Hemisphere
Optimal azimuth range: 0° to 60° and 300° to 360° (around North at 0°/360°)

## References

1. Duffie, J.A., and Beckman, W.A. (2013). "Solar Engineering of Thermal Processes". 4th Edition. Wiley.
2. Liu, B.Y.H. and Jordan, R.C. (1963). "A rational procedure for predicting the long-term average performance of flat-plate solar-energy collectors". Solar Energy, 7(2), 53-74.
3. Holmgren, W. F., Hansen, C. W., and Mikofski, M. A. (2018). "pvlib python: a python package for modeling solar energy systems." Journal of Open Source Software, 3(29), 884.
4. Ineichen, P. and Perez, R. (2002). "A new airmass independent formulation for the Linke turbidity coefficient". Solar Energy, 73(3), 151-157. 