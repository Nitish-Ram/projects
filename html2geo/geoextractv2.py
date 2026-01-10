import sys
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="html_location_lookup")
while True:
    try:
        coords = input("Enter coord (lat,lon): ").strip()
        coords = coords.replace("，", ",")
        lat_str, lon_str = coords.split(",", 1)
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        print(f"Latitude: {lat}")
        print(f"Longitude: {lon}")
        location = geolocator.reverse(
            (lat, lon),
            exactly_one=True,
            timeout=10,
            language="en"
        )
        if not location:
            print("couldn't find it buddy.")
            continue
        addr = location.raw.get("address", {})
        city = (
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
        )
        print("City:", city)
        print("State:", addr.get("state"))
        print("Country:", addr.get("country"))
    except ValueError:
        print("Invalid format. Use: latitude, longitude")
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)