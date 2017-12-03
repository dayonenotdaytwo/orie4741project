import ijson

f = open('data/review.json')
for prefix, the_type, value in ijson.parse(f):
    print(prefix, the_type, value)