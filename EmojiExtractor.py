import urllib

# Animals 
#for i in range (250, 597):

#26c4
#for i in range (2600, ):
for i in range (392, 597):
	urllib.urlretrieve("https://mail.google.com/mail/e/1f"+str(i), "extractedEmoji/1f"+str(i)+".png")