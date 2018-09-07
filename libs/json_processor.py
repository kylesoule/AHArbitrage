import math
import json
import datetime
import oracle_connect
import os
import file_common


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
        jsonData = json.load(fh)
    return jsonData


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
    oracle_connect.insertbulk(sql)

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
        oracle_connect.insertbulk(sql)

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
    snapshots = oracle_connect.snapshotlist()
    files = getfiles(path)
    i = 0

    for file in files:
        i += 1
        tstamp = int(file)
        if tstamp in snapshots:
            print("Skipping {tstamp}...{c} of {count}".format(tstamp=tstamp, c=i, count=len(files)), flush=True)
        else:
            print("Begin processing {tstamp}...{c} of {count}".format(
                tstamp=tstamp, c=i, count=len(files)), flush=True)
            processfile(files[file])


def readquantiles():
    """Returns quantiles data from prepared file.

    Returns:
        dict: Item ID keys and 25% quantile of buyoutper on sold items value
    """
    quantiles = {}
    filename = "G:\\Downloads\\quantiles.csv"
    data = file_common.readcsv(filename)
    for line in data:
        if line[1] != "ITEM":
            quantiles[line[1]] = float(line[2])
    return quantiles


def readavgsold():
    """Returns average sold data from prepared file.

    Returns:
        dict: Item ID keys and average sold per hour value
    """
    avgsold = {}
    filename = "G:\\Downloads\\avgsold.csv"
    data = file_common.readcsv(filename)
    for line in data:
        if line[1] != "ITEM":
            avgsold[line[1]] = float(line[2])
    return avgsold


# path = "G:\\Downloads\\python\\AH Arbitrage\\Data\\"
# initiate(path)


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

timestamp = 1536210189000
# filename = "G:\\Downloads\\python\\AHArbitrage\\Data\\1534021316000.json"
filename = "L:\\Dumps\\emerald-dream\\" + str(timestamp) + ".json"
# filename = "G:\\Downloads\\python\\Emerald Dream\\" + str(timestamp) + ".json"
jsn = readjson(filename)
auctions = jsn["auctions"]
quantiles = readquantiles()
avgsolds = readavgsold()
listed = []

print("%\tItemID\tQuantile\tBuyout\tQty\tBuyoutPer\tAvgSold\tOwner")
print("-\t------\t--------\t------\t---\t---------\t-------\t-----")

for auction in auctions:
    itemid = str(auction["item"])
    buyout = auction["buyout"]
    quantity = auction["quantity"]

    if buyout > 0 and itemid != "82800":
        buyoutper = buyout / quantity
        if itemid in quantiles:
            quantile = quantiles[itemid]
            if buyoutper <= quantile:
                if itemid in avgsolds:
                    avgsold = avgsolds[itemid]
                else:
                    avgsold = 0

                if itemid in listed:
                    continue
                else:
                    if quantile - buyoutper > 1000000 and buyout < 50000000:
                        listed.append(itemid)
                        print("{i}\t{q}\t{b}\t{qty}\t{bp}\t{a}\t{o}".format(q=quantile,
                                                                            i=itemid,
                                                                            b=buyout,
                                                                            bp=buyoutper,
                                                                            qty=quantity,
                                                                            a=avgsold,
                                                                            o=auction["owner"]))
                    # p=round(buyoutper / quantile * 100, 2),

''' OBSOLETE DEAL FINGER BEGIN
deals = []
itemids = {}

for auction in auctions:
    if auction["buyout"] <= 1500000 and auction["buyout"] > 0 and auction["quantity"] == 1:
        deals.append(auction)
        if auction['item'] in itemids:
            if itemids[auction['item']] > auction["buyout"]:
                itemids[auction['item']] = auction["buyout"]
        else:
            itemids[auction['item']] = auction["buyout"]

#print(len(deals))
#print(len(itemids))
for key in itemids.keys():
    print("{key},{minprice}".format(key=key, minprice=itemids[key]))

for auction in auctions:
    if auction['item'] == 12035:
        print(auction)
    if auction['buyout'] < 1500000 and auction['buyout'] > 0:
        if "modifiers" in auction:
            if "value" in auction["modifiers"][0]:
                if auction["modifiers"][0]["value"] > 110:
                    if auction['item'] in itemids:
                        cost, level = itemids[auction['item']]
                        if cost > auction["buyout"]:
                            # itemids[auction['item']] = auction["buyout"]
                            itemids[auction["item"]] = (auction["buyout"], auction["modifiers"][0]["value"])
                    else:
                        itemids[auction["item"]] = (auction["buyout"], auction["modifiers"][0]["value"])

for key in itemids.keys():
    cost, level = itemids[key]
    print("{key},{minprice},{lvl}".format(key=key, minprice=cost, lvl=level))
OBSOLETE DEAL FINDER END '''

'''
auctions = sortauctions(json, timestamp)

import pprint
for auction in auctions[124113]:
    print(auction.buyout)
'''
