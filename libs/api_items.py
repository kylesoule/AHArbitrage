import wget
import urllib.request
import json
import time
import threading
import csv
import api_key
import file_common
import lib_common
import api_manager
from os import listdir
from os.path import isfile, join


def download_item_data(itemid):
    """Download item data using Blizzard API.

    Args:
        itemid (int or str): Item ID

    Returns:
        dict: JSON dictionary
    """
    # url = "https://us.api.battle.net/wow/item/" + itemid + "?locale=en_US&apikey=" + getAPIKey()
    try:
        url = "https://us.api.battle.net/wow/item/" + str(itemid) + "?locale=en_US&apikey=" + api_key.KEY
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
    except Exception as e:
        return None

    return data


def download_item_class_data():
    """Download item class and subclass data using Blizzard API.

    Returns:
        dict: JSON dictionary
    """
    # url = "https://us.api.battle.net/wow/data/item/classes?locale=en_US&apikey=" + getAPIKey()
    url = "https://us.api.battle.net/wow/data/item/classes?locale=en_US&apikey=" + api_key.KEY
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())

    return data


def savedata(data):
    """Download (via wget) auction house data dump from JSON result.

    Args:
        data (dict): JSON data containing auction house data URL
    """
    global lastModified
    global path
    file = data["files"][0]["url"]
    modified = data["files"][0]["lastModified"]
    savename = "{path}{filename}.json".format(path=path, filename=modified)

    if modified > lastModified:
        wget.download(file, savename)
        print("\n{time}: {modified}.json".format(time=lib_common.prettytime(modified), modified=modified), flush=True)
        lastModified = modified

    # TODO: Can safely sleep for 60 minutes after successful execution
    time.sleep(60 * 15)  # 15 minute delay


def getlastmodified():
    """Returns the timestamp of last AH snapshot.

    Returns:
        int: Timestamp of last AH snapshot retrieved
    """
    global path
    lastmodified = 0
    for f in [f for f in listdir(path) if isfile(join(path, f))]:
        if f.split(".")[1] == "json":
            modified = int(f.split(".")[0])
            if modified > lastmodified:
                lastmodified = modified

    return lastmodified


def getitemlist(filename, skip=False, limit=None):
    """Return item IDs from item list already retrieved.

    Skip can be True to skip over items already retrieved.
    Skip can be an integer to skip to index.
    Skip can be None or omitted to not skip anything.

    Args:
        skip (bool or int, optional): Defines skip behavior
        limit (None, optional): Return this many item IDs

    Returns:
        list: Return list of item IDs.
    """
    # global filename
    queue = []
    result = []
    with open("G:\\Downloads\\cleanitemlist.csv", newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            queue.append(row[0])

    if skip is True:
        # Skip items already downloaded
        existing = file_common.getretrieveditemlist(filename, delimiter='\t')
        for itemid in queue:
            if itemid not in existing:
                if limit is None:
                    result.append(itemid)
                elif len(result) < limit:
                    result.append(itemid)
        return result
    else:
        # Determine how many IDs to return
        if limit is None and skip is None:
            return queue
        if limit is None and skip is not None:
            return queue[skip:]
        if limit is not None and skip is None:
            return queue[:limit]
        else:
            return queue[skip:skip + limit]


def getnextitem():
    """Populates global itemdata with next item ID data from queue
    """
    global queue
    global itemdata

    data = download_item_data(queue.pop(0))
    if data is not None:
        itemLevel = -1
        requiredLevel = -1
        if "itemLevel" in data:
            itemLevel = data["itemLevel"]

        if "requiredLevel" in data:
            requiredLevel = data["requiredLevel"]

        itemdata[data["id"]] = [data["inventoryType"],
                                data["isAuctionable"],
                                data["itemClass"],
                                data["itemSubClass"],
                                data["stackable"],
                                data["sellPrice"],
                                data["buyPrice"],
                                data["name"],
                                itemLevel,
                                requiredLevel]


def getitemdata(data):
    """Populates global itemdata with next item ID data from queue
    """
    itemdata = {}
    if data is not None:
        itemLevel = -1
        requiredLevel = -1
        if "itemLevel" in data:
            itemLevel = data["itemLevel"]

        if "requiredLevel" in data:
            requiredLevel = data["requiredLevel"]

        itemdata[data["id"]] = [data["inventoryType"],
                                data["isAuctionable"],
                                data["itemClass"],
                                data["itemSubClass"],
                                data["stackable"],
                                data["sellPrice"],
                                data["buyPrice"],
                                data["name"],
                                itemLevel,
                                requiredLevel]

    return itemdata


def queuedownload():
    """Control timing of data retrieval to prevent requests exceeding API limit.

    Returns:
        None: Returns None when the queue has been exhausted
    """
    global queue
    global finished

    # Limits: (1) 10 simultaneous threads (2) new thread every 10 milliseconds
    # openthreads = threading.active_count()

    if len(queue) == 0:
        return None
    else:
        while threading.active_count() > 10:
            pass

        threading.Timer(0.1, queuedownload).start()
        if len(queue) % 25 == 0:
            print("Remaining items: {r}".format(r=len(queue)), flush=True)
        getnextitem()


def getitemclassdata():
    """Returns a parsed item class/subclass dictionary.

    Results are returned in form: data[class][subclass] = (classname, subclassname)

    Returns:
        dict: List of class/subclass names
    """
    data = download_item_class_data()
    return parseitemclassdata(data)


def parseitemclassdata(data):
    """Turns a JSON dictionary of class/subclass item data into:

    data[class][subclass] = (classname, subclassname)

    Args:
        data (dict): JSON dictionary containing class/subclass data

    Returns:
        dict: Multidimensional dictionary containing class/subclass data
    """
    classes = {}
    data = data["classes"]

    for c in data:
        sc = c["subclasses"]
        for s in sc:
            if not c["class"] in classes:
                classes[c["class"]] = {}

            classes[c["class"]][s["subclass"]] = (c["name"], s["name"])

    return classes


def preparedownloadqueue(itemids):
    downloadqueue = []
    for itemid in itemids:
        url = "https://us.api.battle.net/wow/item/" + str(itemid) + "?locale=en_US&apikey=" + api_key.KEY
        downloadqueue.append((url, "item"))
    return downloadqueue


# data = download_item_data("9940")
# lib_common.prettyprint(data)
# print(data["inventoryType"])
# print(data)
# print(data["name"])

<<<<<<< HEAD
# filename = "G:\\Downloads\\python\\AH Arbitrage\\Temp\\itemdata.csv"
filename = "G:\\Downloads\\python\\tlist.txt"
=======
# RESTART HERE
'''
filename = "G:\\Downloads\\python\\AH Arbitrage\\Temp\\itemdata.csv"
>>>>>>> a9948f1d6ebcbb0ed94c3fa12fb2a784fde51b38
finished = False
itemdata = {}
queue = getitemlist(filename, skip=True, limit=None)
downloadqueue = preparedownloadqueue(queue)

man = api_manager.ApiManager()
man.loadqueue(downloadqueue)

while man.started is False or man.isinputqueueempty() is False or man.getactivethreads() > 1:
    man.initiatecall()
    man.nap()

itemlist = man.returnoutputqueue("item")
for item in itemlist:
    rawdata = getitemdata(item)
    data = list(rawdata.values())[0]
    itemdata.update(rawdata)

# filename = "G:\\Downloads\\python\\tlist.txt"
# headers = ["ItemID", "Type", "Auctionable", "Class", "Subclass", "Stackable", "Sell Price", "Buy Price", "Name", "iLevel", "rLevel"]
# file_common.writetofile('\t'.join(headers), filename)

for item in itemdata:
    line = "{item}\t".format(item=str(item))
    line = line + '\t'.join((str(x) for x in itemdata[item]))
    file_common.appendtofile(line, filename)

# queue = getitemlist(skip=True)
'''

'''
queuedownload()

while True:
    if len(queue) == 0 and threading.active_count() == 1:
        break

for data in itemdata:
    line = "{id}\t{data}".format(id=data, data=lib_common.joinmixedtypes(itemdata[data], "\t"))
    file_common.appendtofile(line, filename)
'''
