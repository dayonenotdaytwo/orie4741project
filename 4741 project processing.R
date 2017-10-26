#install required pakcages
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



#read json file
review_json <- jsonlite::stream_in(file("review.json"))

#convert json to tibble
review_flat <- flatten(revview_json)
head(review_flat)
review_tbl <- as_data_frame(review_flat)

#data cleaning
review <- review_tbl %>% 
            #keep only useful columns
            select(c("review_id", "user_id", "useful", "funny", "cool")) %>% 
            #filter through reviews received low aggregate votes (could be changed later)
            filter(useful + funny + cool >= 10)  %>% 
            #create new columns max count number and its corresponding category
            mutate(max = pmax(useful, funny, cool)) %>%
            mutate(category = derivedVariable(
              "useful" = max == useful,
              "funny" = max == funny,
              "coll" = max == cool,
              .method = "first"
            ))

write.csv(review, "review.csv")
#####If you want to do a join, the primary key is (review_id, user_id)

##Problems left. 
#     1. Need a more accurate metric other than simply taking max?
#     2. If only take max, what to do with tie?(i.e. useful = funny)
#     3. Is 10 a good enough threshold?
