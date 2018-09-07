require(RODBC)
ch <- odbcConnect("ORCL", uid="system", pwd="H1LpQ3Rzf")
#costs <- sqlQuery(ch, "SELECT * FROM PROUDMOORE_A_AUCTION_SUMMARY;")
costs <- sqlQuery(ch, "SELECT * FROM EMERALD_DREAM_H_AUCTION_SUMMARY;")
#costs <- sqlQuery(ch, "SELECT * FROM PROUDMOORE_A_AUCTION_SUMMARY WHERE ITEM = 124113;")
#costs <- read.csv("C:/Users/soulek/Downloads/fullitemlist.csv")

options("scipen"=100, "digits"=4) # Print all digits -- no scientific notation
min_tstamp <- min(costs$ADDED)
max_tstamp <- max(costs$REMOVED)

costs <- costs[costs$ADDED > min_tstamp & costs$REMOVED < max_tstamp, ]

# Convert list time to hour and create df of sold items
costs$timetosell <- ifelse(costs$REMOVED < max_tstamp & costs$ADDED > min_tstamp, (costs$REMOVED - costs$ADDED) / 60000 / 60, -1)
costs$sold <- ifelse(costs$timetosell > 0 & costs$timetosell < 40, 1, 0)
costs$BUYOUTPER <- costs$BUYOUT / costs$QUANTITY
costs$BUYOUTPERGOLD <- round(costs$BUYOUTPER / 10000, 2)

# Get sold amount per hour
tempag <- aggregate(sold ~ ITEM + ADDED, data=costs, FUN=sum)
average_sold_per_hour <- aggregate(sold ~ ITEM, data=tempag, FUN=mean)
#write.csv(average_sold_per_hour, file = "G:/Downloads/avgsold.csv")

get_average_sold <- function(itemid) {
  return(round(average_sold_per_hour[average_sold_per_hour$ITEM == itemid, "sold"], 1))
}

# Calculate the 25% quantile of sales by item
quantile25_of_sold <- aggregate(BUYOUTPER ~ ITEM, data=costs[costs$sold == 1,], FUN=function(x) quantile(x, 0.25))
#write.csv(quantile25_of_sold, file = "G:/Downloads/quantiles.csv")

# Get average sell price of items sold
average_sell_price <- aggregate(BUYOUTPER ~ ITEM, data=costs[costs$sold == 1,], FUN=mean)

# Blizzard API call to get item name by item ID
get_item_name <- function(itemid) {
  require(rjson)
  url <- paste("https://us.api.battle.net/wow/item/", itemid, "?locale=en_US&apikey=62smfn278yetwmngu5fs9xxyzygt3k4w", sep="")
  data <- rjson::fromJSON(file=url)
  return(data$name)
}

# Begin function
plot_item_data <- function(itemid) {
  # Display some plots
  require(ggplot2)
  require(anytime)
  require(gtable)
  require(gridExtra)
  require(scales)
  
  # Functions
  count_listings <- function(timestamp) {
    listings <- sum(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp, "QUANTITY"])
    return(listings)
  }
  
  count_sold_listings <- function(timestamp) {
    soldlistings <- sum(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp & itemlist$sold == 1, "QUANTITY"])
    return(soldlistings)
  }
  
  min_buyout <- function(timestamp) {
    minbuyout <- min(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp, "BUYOUTPER"])
    return(minbuyout)
  }
  
  mean_buyout <- function(timestamp) {
    meanbuyout <- mean(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp, "BUYOUTPER"])
    return(meanbuyout)
  }
  
  min_sell_price <- function(timestamp) {
    minsellprice <- min(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp & itemlist$sold == 1, "BUYOUTPER"])
    return(minsellprice)
  }
  
  mean_sell_price <- function(timestamp) {
    meansellprice <- mean(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp & itemlist$sold == 1, "BUYOUTPER"])
    return(meansellprice)
  }
  
  max_sell_price <- function(timestamp) {
    maxsellprice <- max(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp & itemlist$sold == 1, "BUYOUTPER"])
    return(maxsellprice)
  }
  
  count_listings_near_min <- function(timestamp) {
    minbuyout <- min(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp, "BUYOUTPER"])
    ratio = 1.25
    nearmin <- sum(itemlist[itemlist$ADDED <= timestamp & itemlist$REMOVED > timestamp & itemlist$BUYOUTPER <= (minbuyout * ratio), "QUANTITY"])
    return(nearmin)
  }

  # Create a DF of unique timestamps
  unique_tstamps <- data.frame()
  tcol <- c(sort(unique(c(unique(costs$ADDED), unique(costs$REMOVED)))))
  dtcol <- anytime(tcol / 1000)
  unique_tstamps <- rbind(unique_tstamps, data.frame(c(tcol)))
  unique_tstamps$datetime <- dtcol
  colnames(unique_tstamps) <- c("timestamp", "datetime")

  avgsellprice <- average_sell_price[average_sell_price$ITEM == itemid, "BUYOUTPER"]
  itemlist <- costs[costs$ITEM == itemid & costs$BUYOUT > 0, ]

  #write.csv(itemlist, file = "G:/Downloads/fullitemlist.csv")
  #itemlist <- costs[costs$PETSPECIES == itemid & costs$BUYOUT > 0, ]
  
  # Create some data mappings
  unique_tstamps$listings <- sapply(unique_tstamps$timestamp, count_listings)
  unique_tstamps$soldlistings <- sapply(unique_tstamps$timestamp, count_sold_listings)
  unique_tstamps$minbuyout <- sapply(unique_tstamps$timestamp, min_buyout)
  unique_tstamps$minsellprice <- sapply(unique_tstamps$timestamp, min_sell_price)
  unique_tstamps$meansellprice <- sapply(unique_tstamps$timestamp, mean_sell_price)
  unique_tstamps$nearmin <- sapply(unique_tstamps$timestamp, count_listings_near_min)
  unique_tstamps$avgsellprice <- rep(avgsellprice, nrow(unique_tstamps))
  
  #unique_tstamps$meanbuyout <- sapply(unique_tstamps$timestamp, mean_buyout)
  #unique_tstamps$maxsellprice <- sapply(unique_tstamps$timestamp, max_sell_price)
  item_name <- get_item_name(itemid)
  title = paste("Auction Data for ", item_name, " (ID: ", itemid, ", AVG_SOLD: ", get_average_sold(itemid), ")", sep="")
  
  # Chart data
  g1 <- ggplot(unique_tstamps, aes(x=datetime)) +
        geom_col(aes(y=nearmin), color="grey", size=1, width=0) +
        geom_line(aes(y=listings), color="black", size=1) +
        geom_line(aes(y=soldlistings),  color="darkgreen", size=1) +
        ggtitle(title) + xlab("") + ylab("Auction Listings") +
        scale_x_datetime(breaks = pretty_breaks(10)) +
        theme_classic()
  g2 <- ggplot(unique_tstamps, aes(x=datetime)) +
        geom_line(aes(y=minbuyout / 10000), size=1, color="black") +
        geom_smooth(method = loess, span=0.3, aes(y=meansellprice / 10000), fill="red") +
        geom_line(aes(y=avgsellprice / 10000), size=1, color="orange", linetype = 2) +
        xlab("") + ylab("Selling Characteristics") +
        scale_x_datetime(breaks = pretty_breaks(10)) +
        scale_y_continuous(breaks = pretty_breaks(10)) +
        theme_classic() +
        theme(axis.title.x=element_blank(), axis.text.x=element_blank(), axis.ticks.x=element_blank(), panel.grid.minor.y = element_line(colour="grey", size=0.5))
  g <- rbind(g1, g2, size="first")
  grid.arrange(g1, g2, layout_matrix = rbind(c(1), c(2)))
  item_name
}

plot_item_data(152296)
# Test

# Calculate average sale price
average_sell_price <- function(itemid) {
  itemlist <- costs[costs$ITEM == itemid & costs$sold == 1, "BUYOUT"]
  return(mean(itemlist))
}

items <- aggregate(BUYOUTPER~ITEM, data=costs[costs$sold == 1, ], FUN=function(x) c(mean=mean(x)))


# Sample: Write to a CSV file
#write.csv(itemlist, file = "G:/Downloads/fullitemlist.csv")




# quantities <- c(1,2,3,4,5,10,20,50,100,200)
# loop_sales <- function(dframe, id, quantities) {
#   df <- data.frame()
#   for(i in quantities) {
#     df <- rbind(df, sale_summary(dframe, id, i))
#   }
#   
#   return(df)
# }
# 
# test <- loop_sales(sold, 124113, quantities)
# colnames(test) <- c("ItemID", "Qty", "Mean", "Count")
# test
# hist(test$Mean)
# plot(test$Qty, test$Mean)
# leather <- sold[sold$ITEM == 124113 & sold$QUANTITY == 1 & sold$BUYOUT < 30000, ]
# plot(leather$BUYOUT, leather$timetosell)
# 
# sales_by_tstamp <- function(dframe) {
#   df <- data.frame()
#   dframe$buyoutper <- dframe$BUYOUT / dframe$QUANTITY
#   
#   for(ts in unique(dframe$REMOVED)) {
#     df <- rbind(df, c(ts, mean(dframe[dframe$REMOVED == ts, "buyoutper"])))
#   }
# 
#   return(df)
# }
# 
# ts_sales <- sales_by_tstamp(leather)
# colnames(ts_sales) <- c("TS", "Mean")
# plot(ts_sales$TS, ts_sales$Mean)
# mean(ts_sales$Mean)
# 
# sale_volume <- function(dframe) {
#   df <- data.frame()
#   all_items <- unique(dframe$ITEM)
#   
#   for(i in all_items) {
#     df <- rbind(df, c(i, NROW(dframe[dframe$ITEM == i, "ITEM"])))
#   }
#   
#   return(df)
# }
# 
# sales_volume <- sale_volume(sold)
