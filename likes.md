Step 1 - Build table schema using Db.Model
db.relationship between users - likes &  likes - message

g.user.likes - brings up user liked messages
message.likes - bring up all users who liked it


Within the html templates, logic to add star button (logic to render filled star if liked, empty star if unliked)
1. when like button is pressed, make a post request
2. create POST route to receive request, (csrf validation, check join table to see if its already liked, if not then join)



