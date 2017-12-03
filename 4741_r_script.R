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
library(jsonlite)
library(tibble)
library(dplyr)
library(mosaic)
library(glmnet)
library(lazyeval)
library(devtools)
library(ggplot2)
install.packages("plot3D")
library(plot3D)
########################################install word2vec packages###############################
if(!require(text2vec))
  install.packages("text2vec")
library(text2vec)

if (!require(wordVectors)) {
  if (!(require(devtools))) {
    install.packages("devtools")
  }
  devtools::install_github("bmschmidt/wordVectors")
}

library(wordVectors)

#read json file
review_json <- jsonlite::stream_in(file("review.json"))
#convert json to tibble
review_flat <- flatten(review_json)
head(review_flat)
review_tbl <- as_data_frame(review_flat)



#business_json <- jsonlite::stream_in(file("business.json"))
#business_flat <- flatten(business_json)
#head(business_flat)
#business_tbl <- as_data_frame(business_flat)

#data cleaning
review <- review_tbl %>% 
  mutate(total_vote = useful + funny + cool) %>% 
  #filter through reviews received low aggregate votes (could be changed later)
  filter(total_vote >= 10)  %>% 
  #create new columns max count number and its corresponding category
  mutate(max_vote = pmax(useful, funny, cool)) %>%
  filter(max_vote > total_vote*0.5) %>% 
  mutate(category = derivedVariable(
    "useful" = max_vote == useful,
    "funny" = max_vote == funny,
    "cool" = max_vote == cool,
    .method = "first"
  )) %>% 
  mutate(num_of_words = sapply(strsplit(text, "\\s+"), length)) %>% 
  mutate(num_of_sent = sapply(gregexpr('[[:alnum:] ][.!?;]', text), length))


#count the number of reviews on each day
review_date <- review %>% 
  select("date") %>% 
  group_by(date) %>% 
  mutate(num_date = n()) %>% 
  arrange(date) %>% 
  distinct()

attach(review)

#########################    Initial visualizations   ##################################
review$stars <- as.factor(review$stars)
review$max_vote <- as.numeric(as.character(review$max_vote))
review$num_of_words <- as.numeric(as.character(review$num_of_words))

table(category)

#histogram of max reviews
max_hist <- ggplot(review, aes(max_vote)) + geom_histogram(breaks=seq(0, 80, by = 1))
max_hist

#boxplot of max vote(grouped by category and colored by stars)
stars_max_boxplot <- ggplot(review, aes(category, max_vote, colour = stars)) + geom_boxplot() 
+
  labs(size = "Nitrogen",
       #x = "Category",
       y = "number of words",
       title = "boxplot of number of words")
stars_max_boxplot

stars_length_boxplot <- ggplot(review, aes(category, num_of_words, colour = stars)) + geom_boxplot()
stars_length_boxplot

#scatterplot of numer of words and max vote
words_max_Scatterplot <- ggplot(review, aes(num_of_words, max_vote, colour = category)) + geom_point()
words_max_Scatterplot

#correlation
cor(review["useful"], review["num_of_sent"])
cor(review["funny"], review["num_of_sent"])
cor(review["cool"], review["num_of_sent"])



write.csv(review, "review.csv")

#####If you want to do a join, the primary key is (review_id, user_id)

##Problems left. 
#     1. Need a more accurate metric other than simply taking max?
#     2. If only take max, what to do with tie?(i.e. useful = funny)
#     3. Is 10 a good enough threshold?





########################################### word2vec ####################################
#data cleaning
review_w2v <- review_tbl %>% 
  mutate(total_vote = useful + funny + cool) %>% 
  #filter through reviews received low aggregate votes (could be changed later)
  filter(total_vote >= 10)  %>% 
  #create new columns max count number and its corresponding category
  mutate(useful_ratio = useful/total_vote, funny_ratio = funny/total_vote, cool_ratio = cool/total_vote) %>% 
  #mutate(max_ratio = pmax(useful_ratio, funny_ratio, cool_ratio))
  mutate(max_vote = pmax(useful, funny, cool)) %>%
  filter(max_vote > total_vote*0.5) %>% 
  mutate(category = derivedVariable(
    "useful" = max_vote == useful,
    "funny" = max_vote == funny,
    "cool" = max_vote == cool,
    .method = "first"
  )) 

###################################### text2vec implementation #############################
prep_fun = tolower
tok_fun = word_tokenizer

#tokenize
train_tokens = review_w2v$text %>% 
  prep_fun %>% 
  tok_fun

it_train = itoken(train_tokens, 
                  ids = review_w2v$user_id,
                  # turn off progressbar because it won't look nice in rmd
                  progressbar = FALSE)

vocab_review <- create_vocabulary(it_train)

vectorizer_review <- it_train %>% 
  create_vocabulary() %>% 
  vocab_vectorizer()

#creat dtm $ tcm
review_dtm <- create_dtm(it_train, vectorizer)
dim(review_dtm)
identical(rownames(review_dtm), review_w2v$user_id)
tcm <- create_tcm(it_train, vectorizer_review, skip_grams_window = 5L)

# fit logistic regression
NFOLDS = 10
t1 = Sys.time()
##change y to max_vote
glmnet_classifier = cv.glmnet(x = review_dtm, y = train[['sentiment']], 
                              family = 'binomial', 
                              # L1 penalty
                              alpha = 1,
                              # interested in the area under ROC curve
                              type.measure = "auc",
                              # 5-fold cross-validation
                              nfolds = NFOLDS,
                              # high value is less accurate, but has faster training
                              thresh = 1e-3,
                              # again lower number of iterations for faster training
                              maxit = 1e3)
print(difftime(Sys.time(), t1, units = 'sec'))


#################################### viz #####################################
max_ratio_hist <- ggplot(review_w2v, aes(max_ratio)) + geom_histogram(breaks=seq(0, 1, by = 0.05)) + 
  labs(x = "Max Ratio", y = "Counts", title = "Histogram of Max Ratio of each Review")


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
