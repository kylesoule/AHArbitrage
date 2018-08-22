require(RODBC)
ch <- odbcConnect("ORCL", uid="system", pwd="H1LpQ3Rzf")
costs <- sqlQuery(ch, "SELECT * FROM PROUDMOORE_A_AUCTION_SUMMARY;")

options("scipen"=100, "digits"=4) # Print all digits -- no scientific notation
min_tstamp <- min(costs$ADDED)
max_tstamp <- max(costs$REMOVED)

# Convert list time to hour and create df of sold items
costs$timetosell <- ifelse(costs$REMOVED < max_tstamp & costs$ADDED > min_tstamp, (costs$REMOVED - costs$ADDED) / 60000 / 60, -1)
sold <- costs[costs$timetosell > 0, ]

quantities <- c(1,2,3,4,5,10,20,50,100,200)
loop_sales <- function(dframe, id, quantities) {
  df <- data.frame()
  for(i in quantities) {
    df <- rbind(df, sale_summary(dframe, id, i))
  }
  
  return(df)
}

test <- loop_sales(sold, 124113, quantities)
colnames(test) <- c("ItemID", "Qty", "Mean", "Count")
test
hist(test$Mean)
plot(test$Qty, test$Mean)
leather <- sold[sold$ITEM == 124113 & sold$QUANTITY == 1 & sold$BUYOUT < 30000, ]
plot(leather$BUYOUT, leather$timetosell)

sales_by_tstamp <- function(dframe) {
  df <- data.frame()
  dframe$buyoutper <- dframe$BUYOUT / dframe$QUANTITY
  
  for(ts in unique(dframe$REMOVED)) {
    df <- rbind(df, c(ts, mean(dframe[dframe$REMOVED == ts, "buyoutper"])))
  }

  return(df)
}

ts_sales <- sales_by_tstamp(leather)
colnames(ts_sales) <- c("TS", "Mean")
plot(ts_sales$TS, ts_sales$Mean)
mean(ts_sales$Mean)

sale_volume <- function(dframe) {
  df <- data.frame()
  all_items <- unique(dframe$ITEM)
  
  for(i in all_items) {
    df <- rbind(df, c(i, NROW(dframe[dframe$ITEM == i, "ITEM"])))
  }
  
  return(df)
}

sales_volume <- sale_volume(sold)
