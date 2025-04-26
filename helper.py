import math

def generate_coordinate_id(latitude, longitude):
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Некорректные координаты")
    
    lat_abs = abs(latitude)
    lon_abs = abs(longitude)
    lat_deg = int(lat_abs)
    lat_min = (lat_abs - lat_deg) * 60
    lon_deg = int(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60
    first_letter = chr(ord('A') + int(lon_deg / 20))
    second_letter = chr(ord('A') + int(lat_deg / 10))
    numeric_part = f"{int(lon_min):02d}{int(lat_min):02d}"
    height = int((math.sin(lat_abs) * 1000) % 500 
    
    ns = 'N' if latitude >= 0 else 'S'
    ew = 'E' if longitude >= 0 else 'W'
    
    coordinate_id = f"{first_letter}{second_letter}{numeric_part}{ns.lower()}{ew.lower()} @{height}m"
    
    return coordinate_id
