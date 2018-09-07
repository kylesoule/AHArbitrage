import math
import json
import datetime
import oracle_insert
import oracle_select
import os


# General functions

def measurekeys(path):
    keylist = {}
    files = getfiles(path)

    for file in files:
        filename = path + file + ".json"
        json = readjson(filename)
        auctions = json["auctions"]

        for auction in auctions:
            for key in auction.keys():
                if isinstance(auction[key], list):
                    for i in range(0, len(auction[key])):
                        for k in auction[key][i].keys():
                            tlen = len(str(auction[key][i][k]))

                            if key + "_" + k in keylist:
                                if tlen > keylist[key + "_" + k]:
                                    keylist[key + "_" + k] = tlen
                            else:
                                keylist[key + "_" + k] = tlen
                else:
                    tlen = len(str(auction[key]))

                    if key in keylist:
                        if tlen > keylist[key]:
                            keylist[key] = tlen
                    else:
                        keylist[key] = tlen

    for key in keylist:
        print("{val}\t{key}".format(val=keylist[key], key=key))


# Auction Functions

class Auction():
    def __init__(self, auction, timestamp):
        self.auction = auction

        self.timestamp = int(timestamp)                 # Snapshot timestamp
        self.auctionID = auction["auc"]                 # Auction ID
        self.itemID = auction["item"]                   # Item ID
        self.owner = auction["owner"]                   # Owner
        self.realm = auction["ownerRealm"]              # Realm
        self.bid = auction["bid"]                       # Bid amount
        self.buyout = auction["buyout"]                 # Buyout amount
        self.quantity = auction["quantity"]             # Quantity
        self.time = auction["timeLeft"]                 # Time left
        self.rand = auction["rand"]                     # Item suffix
        self.seed = auction["seed"]                     # Unknown -- Blizzard side?
        self.context = auction["context"]               # How was it obtained (dungeon, crafting, etc.)

        # Check if available
        self.petspecies = self.GetValue("petSpecifiesId")   # Pet species ID
        self.petbreed = self.GetValue("petBreedId")         # Pet breed ID
        self.petlevel = self.GetValue("petLevel")           # Pet level
        self.petquality = self.GetValue("petQualityId")     # Pet quality ID

        # Not yet implemented
        self.modtype = -1       # self.modtype = auction["modifiers"]["type"]            # Modifier Type(s)
        self.modvalue = -1      # self.modvalue = auction["modifiers"]["value"]          # Modifier Value(s)
        self.bonuslist = -1     # self.bonuslists = auction["bonusLists"]["bonusListId"] # Bonus list ID(s)

        # Custom views
        self.bidper = math.floor(self.bid / self.quantity)
        self.buyoutper = math.floor(self.buyout / self.quantity)

    def GetValue(self, key):
        if key in self.auction:
            return self.auction[key]
        else:
            return -1

    def GetGoldValue(self, amount, silver=False):
        if silver:
            return math.floor(amount / 100) / 100
        else:
            return math.floor(amount / 10000)

    def GetBuyoutGold(self, silver=False):
        return self.GetGoldValue(self.buyout, silver)

    def GetTimeLeft(self):
        case = {"SHORT": 0, "MEDIUM": 30, "LONG": 120, "VERY_LONG": 720}
        return case[self.time]


def getfiles(path):
    files = []
    f = {}
    for (dirpath, dirnames, filenames) in os.walk(path):
        files.extend(filenames)
        break

    for file in files:
        # f[timestamp] = (filename, fullpath)
        f[file[:13]] = (file, path + file)
    return f


def readjson(file):
    with open(file, encoding='utf-8') as fh:
        jsondata = json.load(fh)
    return jsondata


def converttimestamp(ts, um="ms"):
    if um == "ms":
        return datetime.datetime.fromtimestamp(ts / 1000.0)  # Millisecond convert
    else:
        return datetime.datetime.fromtimestamp(ts)   # Assume seconds


def sortauctions(data, timestamp):
    auctions = {}
    item = []
    for a in data["auctions"]:
        auction = Auction(a, timestamp)

        if auction.itemID in auctions:
            item = auctions[auction.itemID]
        else:
            del item
            item = []

        item.append(auction)
        auctions[auction.itemID] = item

    return auctions


def processfile(file):
    timestamp = file[0][:13]
    # filename = file[0]
    fullpath = file[1]

    json = readjson(fullpath)
    auctions = sortauctions(json, timestamp)
    sql = preparesql(auctions)
    oracle_insert.insertbulk(sql, GLOBALDB)

    print("\t...processed {lcount} lines in file...".format(lcount=len(sql), flush=True))


def processfiles(files):
    progress = 0
    total = len(files)
    for file in files:
        timestamp = file
        # filename = files[file][0]
        fullpath = files[file][1]

        json = readjson(fullpath)
        auctions = sortauctions(json, timestamp)
        sql = preparesql(auctions)
        oracle_insert.insertbulk(sql, GLOBALDB)

        progress += 1
        print("Processed {c} lines in file {p} of {t}...".format(c=len(sql), p=progress, t=total), flush=True)


def preparesql(auctions):
    sql = []
    for listings in auctions:
        for item in auctions[listings]:
            row = (item.timestamp, item.auctionID, item.itemID, item.owner, item.realm, "A",
                   item.bid, item.buyout, item.quantity, item.time, item.rand, item.seed, item.context,
                   item.bonuslist, item.modtype, item.modvalue,
                   item.petspecies, item.petbreed, item.petlevel, item.petquality)
            sql.append(row)
    return sql


def initiate(path):
    snapshots = oracle_select.snapshotlist(GLOBALDB)
    files = getfiles(path)
    i = 0

    for file in files:
        i += 1
        tstamp = int(file)
        if tstamp not in snapshots:
            # print("Skipping {tstamp}...{c} of {count}".format(tstamp=tstamp, c=i, count=len(files)), flush=True)
            print("Begin processing {tstamp}...{c} of {count}".format(
                tstamp=tstamp, c=i, count=len(files)), flush=True)
            processfile(files[file])


# path = "G:\\Downloads\\python\\AH Arbitrage\\Data\\"
# path = "C:\\Users\\Kyle\\Downloads\\AH Data\\Dumps\\"
# GLOBALDB = "PROUDMOORE_A"
# path = "C:\\Users\\Kyle\\Downloads\\AH Data\\Dumps\\proudmoore\\"

GLOBALDB = "EMERALD_DREAM_H"
path = "C:\\Users\\Kyle\\Downloads\\AH Data\\Dumps\\emerald-dream\\"
initiate(path)


# oracle_connect.countrecords()
# sql = "SELECT AVG(*) FROM ( SELECT COUNT(*) FROM PROUDMOORE_A GROUP BY TSTAMP )"
# sql = "SELECT COUNT(*) FROM PROUDMOORE_A GROUP BY TSTAMP"
# connection, cursor = oracle_connect.executesql(sql)

# row = cursor.fetchone()
# rows = cursor.fetchmany(numRows=3)
# allrows = cursor.fetchall()
# for r in allrows:
#   print(r[0])
# with open("G:\\Downloads\\python\\AH Arbitrage\\data.out", 'w') as file:
#   for d in cursor:
#       #file.write("{d0}\t{d1}\n".format(d0 = d[0], d1 = d[1]))
#       print(type(d))

# cursor.close()
# connection.close()


# buyouts = oracle_connect.priceinformation(119148)
# for buyout in buyouts:
#   print(buyout)

'''
auctions = sortauctions(json, timestamp)

import pprint
for auction in auctions[124113]:
    print(auction.buyout)
'''
