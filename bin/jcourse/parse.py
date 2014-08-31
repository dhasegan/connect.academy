import json

reviews = json.load( open('reviews.json') )
ratings = json.load( open('ratings.json') )

users = {}

def addone(username):
    if username in users:
        users[ username ] += 1
    else:
        users[ username ] = 1

for review in reviews:
    if 'posted_by' in review:
        addone(review['posted_by'])
        for up in review['upvotes']:
            addone(up)
        for down in review['downvotes']:
            addone(down)

for rating in ratings:
    addone( rating['posted_by'] )

contr = open('contributions.json', 'w')
dictlist = []
for key, value in users.iteritems():
    dictlist.append((key,value))
contr.write( json.dumps(sorted(users.iteritems(), key=lambda x:x[1], reverse=True)) )
contr.close()


students = json.load(open('jacobs_user_details.json'))
for st in users:
    if st not in students:
        print st

users_file = open('contr_users.json', 'w')
users_file.write( json.dumps([x[0] for x in dictlist]) )
users_file.close()
