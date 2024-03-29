from django.contrib.auth import get_user_model
from PIL import Image
from PIL.ExifTags import IFD
from math import floor, ceil
import requests

######################
# Internal functions #
######################

def _gps_from_exif(exif):
    try:
        lat_deg = exif.get_ifd(IFD.GPSInfo)[2]
        lat_dec = deg_to_dec(lat_deg)
    except KeyError:
        lat_dec=None
    try:
        lon_deg = exif.get_ifd(IFD.GPSInfo)[4]
        lon_dec = deg_to_dec(lon_deg)
    except KeyError:
        lon_dec=None
    return lat_dec, lon_dec

def _exif_from_image(image):
    with Image.open(image) as img:
        return img.getexif()

def _send_osm_request(lat: float, lon: float, lang="en"):
    return requests.get(
        f"https://nominatim.openstreetmap.org/reverse.php?lat={lat}&lon={lon}&format=json",
        headers={"Accept-Language":f"{lang}", "Referer":"https://hanbaiki.fyi"}
    ).json()

def _parse_osm(osm_info:dict):
    result = dict()
    # try to get country information
    try:
        result['country'] = osm_info['address']['country']
    except KeyError:
        result['country'] = None
    # try to get state information
    try:
        result['state'] = osm_info['address']['state']
    except KeyError:
        try:
            result['state'] = osm_info['address']['county']
        except KeyError:
            result['state'] = None

    # try to get postcode information
    try:
        result['postcode'] = osm_info['address']['postcode']
    except KeyError:
        result['postcode'] = None

    # try to get city information
    try:
        result['city'] = osm_info['address']['city']
    except KeyError:
        result['city'] = None

    # try to get town/village/neighborhood information
    try:
        result['town'] = osm_info['address']['town']
    except KeyError:
        try:
            result['town'] = osm_info['address']['village']
        except KeyError:
            try:
                result['town'] = osm_info['address']['neighborhood']
            except KeyError:
                result['town'] = None
    return result


######################
# External functions #
######################

def dec_to_deg(dec:float):
    deg = int(dec)
    min = int((dec - deg) * 60.)
    sec = round((((dec - deg) * 60.) - min) * 60., 6)
    return (deg, min, sec)

def deg_to_dec(deg_min_sec:tuple):
    deg, min, sec = deg_min_sec
    return round(float(deg + min/60. + sec/3600.), 6)

def get_sentinel_user():
    User = get_user_model()
    return User.objects.get_or_create(username="deleted")[0]

def gps_from_image(image):
    return _gps_from_exif(_exif_from_image(image))

def info_from_gps(lat:float, lon:float):
    return _parse_osm(_send_osm_request(lat, lon))

def slugify_post(fname: str) -> str:
    filename = fname.split("/")[-1]
    return filename.split(".")[0]

def round_up(n, decimals=0):
    multiplier = 10**decimals
    return ceil(n * multiplier) / multiplier

def round_down(n, decimals=0):
    multiplier = 10**decimals
    return floor(n * multiplier) / multiplier