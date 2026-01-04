import sys
import re
from geopy.geocoders import Nominatim

print("for my reference, paste then use ctrl + z")

html = sys.stdin.read()
pattern = r'(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)'
matches = re.findall(pattern, html)

valid_coords = [(float(lat), float(long)) for lat, long in matches if -90<=float(lat)<=90 and -180<=float(long)<=180]
if not valid_coords:
    print("coords lowk trippin")
    sys.exit(1)

lat, long = valid_coords[0]
print(f"Latitude: {lat}")
print(f"Longitude: {long}")
geolocator = Nominatim(user_agent="html_location_lookup")
location = geolocator.reverse((lat, long), exactly_one=True, timeout=10)
if not location:
    print("couldnt find it buddy")
    sys.exit(1)
addr = location.raw.get("address", {})

print("City:", addr.get("city") or addr.get("town") or addr.get("village"))
print("State:", addr.get("state"))
print("Country:", addr.get("country"))