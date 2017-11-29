##############################################install required pakcages#######################################
if(!require(jsonlite))
  install.packages("jsonlite")
if(!require(tibble))
  install.packages("tibble")
if(!require(dplyr))
  install.packages("dplyr")
if(!require(mosaic))
  install.packages("mosaic")
if(!require(lazyeval))
  install.packages("lazyeval")
if(!require(devtools))
  install.packages("devtools")
if(!require(plot3D))
  install.packages("plot3D")
library(jsonlite)
library(tibble)
library(dplyr)
library(mosaic)
library(lazyeval)
library(devtools)
library(ggplot2)
library(plot3D)



################################# filtering check #############################
review <- review_tbl %>% 
  #create new columns max count number and its corresponding category
  mutate(total_vote = useful + funny + cool) %>% 
  #filter out all of the review with total vote less than 10
  filter(total_vote > 10) %>% 
  #calculate the max vote rate
  mutate(max_vote_rate = pmax(useful, funny, cool)/total_vote) %>% 
  #keep only useful columns
  select(review_id, user_id, total_vote, max_vote_rate) %>% 
  #arrange in descending order on total vote
  arrange(desc(total_vote))

#2d scatter plot of total vote and max vote rate
ggplot(review, aes(total_vote, max_vote_rate)) + geom_point()

#calculate the number of reviews in total in the raw dataset
n_total <- nrow(review_tbl) 


review_temp <- review_tbl %>% 
  #create new columns max count number and its corresponding category
  mutate(total_vote = useful + funny + cool) %>% 
  mutate(max_vote_rate = pmax(useful, funny, cool)/total_vote) %>% 
  #filter out reviews with no vote
  filter(!is.na(max_vote_rate)) %>% 
  select(review_id, user_id, total_vote, max_vote_rate)

x_seq <- seq(0, 1, 0.05) #max_vote_rate sequance range from 0 - 1 with interval 0.05
y_seq <- seq(0, 250,5)   #total_vote sequance range from 0 - 250 with interval 5,
                         #since most reviews have total vote < 250 (check 2d plot), 
                         #it does not affect the result greatly
x_len <- length(x_seq)
y_len <- length(y_seq)
height <- c()
rate <- c()
total <-c()

for(x in x_seq){
  for (y in y_seq){
    df_temp <- review_temp %>% 
      filter(max_vote_rate > x) %>% 
      filter(total_vote > y)
    height <- c(height, nrow(df_temp)/n_total)
    rate <- c(rate, x)
    total <- c(total, y)
  }
}

data_3d <- data.frame(rate, total, height)
data_3d <- data_3d %>% filter(height > 0)
data_3d$log_height <- -log(data_3d$height)
attach(data_3d)
scatter3D(data_3d$rate, data_3d$total, data_3d$log_height, theta = 15, phi = 20)


write.csv(data_3d, "3d_data.csv")