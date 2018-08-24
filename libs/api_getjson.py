import urllib.request
import json
import api_key


def download_ah_data(realm):
    """Download AH API link and timestamp.

    Args:
        realm (str): Realm name (eg. proudmoore)

    Returns:
        TYPE: Description
    """
    url = "https://us.api.battle.net/wow/auction/data/" + realm + "?locale=en_US&apikey=" + api_key.KEY
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())

    return data


def download_item_data(itemid):
    """Download item data.

    Args:
        itemid (str or int): Item ID

    Returns:
        dict: JSON dictionary.
    """
    url = "https://us.api.battle.net/wow/item/" + str(itemid) + "?locale=en_US&apikey=" + api_key.KEY
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
    print(type(data))
    return data


def download_item_class_data():
    """Download item class/sublcass data.

    Returns:
        dict: JSON dictionary.
    """
    url = "https://us.api.battle.net/wow/data/item/classes?locale=en_US&apikey=" + api_key.KEY
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())

    return data


download_item_data(124113)
