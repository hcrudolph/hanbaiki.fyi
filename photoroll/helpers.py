from django.contrib.auth import get_user_model
from PIL import Image
from PIL.ExifTags import IFD
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
        headers={"Accept-Language":f"{lang}"}
    ).json()

def _parse_osm(osm_info:dict):
    result = dict()
    try:
        result['country'] = osm_info['address']['country']
    except KeyError:
        result['country'] = None
    # try to get state/county information
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

    # try to get postcode information
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
    result = dict()
    result['degree'] = int(dec)
    result['minute'] = int((dec - result['degree']) * 60)
    result['second'] = round((((dec - result['degree']) * 60) - result['minute']) * 60, 4)
    return result

def deg_to_dec(deg_min_sec:list):
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
