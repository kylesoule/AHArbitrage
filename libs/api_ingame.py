import file_common


def isvaliddata(data):
    if data[5] == "true":
        return True
    else:
        return False


def getdata():
    filename = "G:\\Downloads\\python\\Emerald Dream\\AuctionHouseDownload.lua"
    with open(filename, mode='r', encoding="utf-8") as f:
        data = [line.rstrip() for line in f]

    # Pop off blank line and variable name
    data.pop(0)
    data.pop(0)

    ''' auctions legend:
    0   name                1   texture
    2   count               3   quality
    4   canUse              5   level
    6   levelColHeader      7   minBid
    8   minIncrement        9   buyoutPrice
    10  bidAmount           11  highBidder
    12  highBidderFullName  13  owner
    14  ownerFullName       15  saleStatus
    16  itemID              17  hasAllInfo
    '''

    ''' Reduced to...
    0   itemID      1   count
    2   level       3   buyoutPrice
    4   saleStatus  5   hasAllInfo
    '''
    auctions = []
    auction = []
    linenum = 1
    auctioncount = 0

    # Loop over data and sort it into a list
    for i in range(0, len(data)):
        if "{" in data[i] and "= {" not in data[i]:
            auction = []
            linenum = 1
            auctioncount += 1
        elif "}, -- [" in data[i]:
            if isvaliddata(auction):
                auctions.append(auction)
        else:
            stripsize = (len(str(linenum)) + 7) * -1
            line = data[i].replace('"', '').strip()[:stripsize]
            auction.append(line)

            linenum += 1

    return auctions

filename = "G:\\Downloads\\itemlist.csv"
auctions = getdata()
for auction in auctions:
    count = int(auction[1])
    buyout = int(auction[3])
    level = int(auction[2])
    item = int(auction[0])
    status = auction[4]

    #if level > 110 and buyout > 0 and buyout < 1500000:
    line = "{i},{b},{c},{l},{s}".format(i=item, b=buyout, c=count, l=level, s=status)
    file_common.appendtofile(line, filename)
