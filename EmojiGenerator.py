from PIL import Image
import sys
import math
import operator
import os.path
from collections import OrderedDict


	
# <img src="https://mail.google.com/mail/u/0/e/360" goomoji="360" style="margin: 0px 0.2ex; vertical-align: middle;">
# Div in which the email text is inserted, add emoticon to it. 
# Note: Id seems to change but the class remains the same. Label is "Message Body" 
# <div id=":1dw" class="Am Al editable LW-avf" hidefocus="true" aria-label="Message Body" g_editable="true" role="textbox" contenteditable="true" tabindex="1" style="direction: ltr; min-height: 80px;">
# ddf <img src="https://mail.google.com/mail/u/0/e/360" goomoji="360" style="margin: 0px 0.2ex; vertical-align: middle;">

###########################################################################
# This function inspects the pixels in a tile and returns the most
# prominent color among all pixesl in that tile. 
#
# Note: For the purpose of this implementation a tile is just a region
#		of pixels in the screen.
#
# @param imgPixels - Access object to the pixels in the image.
# @param imgSize - Tuple containing width and height of the image.
# @param tileInfo - Tuple containing (tileX, tileY, tileW, tileH)
#
# @return - Color for the tile.
###########################################################################
def inspectTile(imgPixels, imgSize, tileInfo): 
	
	# Used to handle dirty images
	# usually this image will have a very low frequency 
	# of a given color because the tile is composed 
	# of shades of the color.
	threshold = 50
	
	xPos = tileInfo[0]
	yPos = tileInfo[1]
	tileW = tileInfo[2]
	tileH = tileInfo[3]
	
	colorDict = {}
	#avaliableColors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,182,193)]
	
	totalColor = (0,0,0)
	colorCount = 0
	# Count the occurrence of each pixel color
	# in the tile.
	for x in xrange(xPos, xPos + tileW):
		
		if  x >= imgSize[0]:
			#print "X:" + str(x)
			break
			
		for y in xrange(yPos, yPos + tileH):
			
			if y >= imgSize[1]:
				break
				
			# Get a specific pixel
			pixelColor = imgPixels[x,y]
			# Find the closest color make that the
			# new pixel color instead
			#pixel = findClosestColorForPixel(pixel, avaliableColors)[0]
			
			colorCount = colorCount + 1
			totalColor = (totalColor[0] + pixelColor[0],
					totalColor[1] + pixelColor[1],
					totalColor[2] + pixelColor[2])
			
			
			if pixelColor in colorDict:
				colorDict[pixelColor] = colorDict[pixelColor] + 1
			else:
				colorDict[pixelColor] = 1
	
	
	if colorCount == 0:
		return totalColor
	# Get the most prominent color in this tile
	color = getMostProminentColor(colorDict)
	
	# Find the average color of the tiles.
	totalColor= (totalColor[0] / colorCount,
				totalColor[1] / colorCount,
				totalColor[2] / colorCount)
	
	# if the prominent color doesn't have 
	# much influence then use the average
	if colorDict[color]	> threshold:
		outColor = color
	else:
		outColor = totalColor
		
	return outColor
	
###########################################################################
# Helper function to find the closest closet color to the pixel color
# that is available. Designed in case there was a need to limit the created
# image to just a few colors. 
#
# @param pixelColor - Current color of the pixel in the image.
# @param colorList - List of available colors to choose from.
#
# @return - Tuple containing the closest color and the distance away from
#			the color in question.
###########################################################################
def findClosestColorForPixel(pixelColor, colorList):
	minDistance = sys.maxint;
	closestColor = (0,0,0)
	for color in colorList:
		distance = getDistanceBetweenColors(pixelColor, color)
		if distance < minDistance:
			minDistance = distance
			closestColor = color
			
	return (closestColor, minDistance)
	
###########################################################################
# Helper function to replace every pixel in a tile with the specified 
# color.
#
# @param color - Color to paint the tile with.
# @param imgDestPixel - Access object to the pixesl in the image.
# @param imgSize - Tuple containing (imgPixelWidth, imgPixelHeight)
# @param tileInfo - Tuple containing (tileX, tileY, tileW, tileH)
###########################################################################
def paintTileWithColor(color, imgDestPixel, imgSize, tileInfo):	
	xPos = tileInfo[0]
	yPos = tileInfo[1]
	tileW = tileInfo[2]
	tileH = tileInfo[3]
	
	for x in xrange(xPos, xPos + tileW):
		if x >= imgSize[0]:
			break
			
		for y in range(yPos, yPos + tileH):
			if y >= imgSize[1]:
				break
				
			imgDestPixel[x,y] = color


###########################################################################
# Function to group all colors that are similar into a common color. 
# It creates a map colors to replacement colors for all colors that are 
# very similar to the most prominent color of that shade in the image.
#
# @param colorDict - Dictionary containing all the colors mapped to their
#					 frequency in the image.
# @param colorMinDistance - Minimum distance two color can be appart to be
#							considered similar.
#
# return - Color map dictionary containing a mapping between colors to 
#		   replacement colors.
###########################################################################
def clusterColors(colorDict, colorMinDistance):
	
	# Minimum distance colors can be appart
	# to be considered the same color.
	#colorMinDistance = 20;
	
	# Sort in descending frequency order
	colorDict = OrderedDict(sorted(colorDict.items(), key=lambda t:t[1], reverse=True))
	
	colorMappingDict = {}
	#tempDict = deepcopy(colorDict)
	for color1 in colorDict:
		for color2 in colorDict:
			if color1 == color2:
				colorMappingDict[color1] = color1
				continue
			
			distance = getDistanceBetweenColors(color1 , color2)
			
			# If colors are similar then map it 
			# to the color1.
			if distance <= colorMinDistance:
				colorMappingDict[color2] = color1
				#colorDict[color1] += colorDict[color2]
				#colorDict[color2] = 0
				
	
	return colorMappingDict
	
###########################################################################
# Helper function to find the most prominent color on a region/tile. 
#
# @param colorDict - Dictionary containing a map of color to frequency 
#					 of all the colors in the given region.
#
# @return - Tuple containing most prominent color.
###########################################################################
def getMostProminentColor(colorDict):
	# Keep track of color count.
	maxColorCount = 0
	# Keep track of Most Prominent Color
	maxColorRGB = (0,0,0)

	for color in colorDict:
		colorCount = colorDict[color]
		if colorCount > maxColorCount:
			maxColorCount = colorCount
			maxColorRGB = color
	

	return maxColorRGB


###########################################################################
# Returns the Euclidean distance between two colors.
#
# @param color1 - First color
# @param color2 - Second color
#
# @return - The euclidean distance between the colors.
###########################################################################
def getDistanceBetweenColors(color1, color2):
	rDiff = color2[0] - color1[0]
	gDiff = color2[1] - color1[1]
	bDiff = color2[2] - color2[2]
	
	return math.sqrt( 
			math.pow(rDiff, 2) + 
			math.pow(gDiff, 2) + 
			math.pow(bDiff, 2))


###########################################################################
# This function to convert an image into GMAIL emoticons. 
# All this function does is replace every color in the 
# image by one of the emoticons in the emoticonID list.
# The function will try to assign a unique emoticon to each
# color and assign the same emoticon to the same color.
#
# Note: During the replacement process the first emoticonID is mapped to
#		the color of the first tile, the second emoticonID is mapped to 
#		the color of the second tile and so on. (No single emoticonID will
#		be mapped to two different colors unless the image has more colors
#		than the emoticon list has emoticonIDs. If that happens emoticons
#		will be reused. 
#		A way to change the look of the generated image is to change the 
#		order of the emoticonIDList. 
#
# @param image - Image to process
# @param emoticonIDList - List of ids for emoticons in GMAIL
# @param pixelatedInfo - Tuple containing the number of tiles on the image
# @param tileInfo - Tuple containing (0,0, tileWidth, tileHeight)
#
# @return - HTML code for the entire emoticon art (list).
############################################################################
def generateGMailEmoticonArt(image, emoticonIDList, pixelatedInfo, tileInfo):
	
	imagePixels = image.load()
	imageSize = image.size
	
	countHorizontalTiles = pixelatedInfo[0]
	countVerticalTiles = pixelatedInfo[1]
	
	tileWidth = tileInfo[2]
	tileHeight = tileInfo[3]
	
	# Position of the last emoticon used
	lastEmoticonUsed = -1
	
	# Emoticon to color map
	# keeps track of which emoticon was used for what color.
	emoticonMap = {}
	
	# Out HTML Code for the Emoticon Art
	lstHtml = [];
	
	# Generate the HTML for GMAIL
	for tileY in xrange(0, countVerticalTiles):
		lstHtml.append("<div>\n")
		for tileX in xrange(0, countHorizontalTiles):
			# Find common color in the tile
			color = inspectTile(imagePixels, imageSize, (tileX * tileWidth, tileY * tileHeight, tileWidth, tileHeight))
			# If no emoticon has been used for this color yet 
			# assign one.
			if color not in emoticonMap:
				lastEmoticonUsed = (lastEmoticonUsed + 1) % len(emoticonIDList)
				emoticonMap[color] = lastEmoticonUsed
			
			lstHtml.append("\t"+generateGMAILEmoticonHTMLFromID(emoticonIDList[emoticonMap[color]])+"\n")
		lstHtml.append("<br>\n")
		lstHtml.append("</div>\n")
	
	return lstHtml

###########################################################################
# This function maps each pixel color to a colorID. This mapping 
# holds information on what color to user for each tile. 
#
# @param pixelatedImage - Image to generate the map from.
# @param pixelatedInfo - Tuple containing the number of horizontal and 
#						 vertical tiles in the image.
# @param tileInfo - Tuple containing tile information (x, y, width, height)
#
# @return - 2D Array contaning an ID for each color in the image. 
###########################################################################
def generateColorMapForEmoticonArt(pixelatedImage, pixelatedInfo, tileInfo):
	
	imagePixels = pixelatedImage.load()
	imageSize = pixelatedImage.size
	
	countHorizontalTiles = pixelatedInfo[0]
	countVerticalTiles = pixelatedInfo[1]
	
	tileWidth = tileInfo[2]
	tileHeight = tileInfo[3]
	
	# Position of the last emoticon used
	lastEmoticonUsed = -1
	
	# Emoticon to color map
	# keeps track of which emoticon was used for what color.
	emoticonMap = {}
	
	# Out Color Code for the Emoticon Art
	colorMapOutLst = [];
	
	decSpacer = "0"
	
	# Generate the HTML for GMAIL
	for tileY in xrange(0, countVerticalTiles):
		lstRow = []
		for tileX in xrange(0, countHorizontalTiles):
			# Find common color in the tile
			color = inspectTile(imagePixels, imageSize, (tileX * tileWidth, tileY * tileHeight, tileWidth, tileHeight))
			# If no emoticon has been used for this color yet 
			# assign one.
			if color not in emoticonMap:
				lastEmoticonUsed = lastEmoticonUsed + 1
				emoticonMap[color] = lastEmoticonUsed
			
			# If the color mapped is a single digit 
			# add a 0 infront so the final image map
			# looks a bit more recognizable.
			#if emoticonMap[color] < 10:
			#	colorMapOutLst.append(decSpacer)
			
			lstRow.append(emoticonMap[color])
			#colorMapOutLst.append(str(emoticonMap[color])+" ")
		
		colorMapOutLst.append(lstRow)
		#colorMapOutLst.append("\n")
	
	return colorMapOutLst

###########################################################################
# This function uses a color map to create an image composed of emoticons.
# Each unique color ID will be replaced by a unique emoticon in the 
# emoticon list. 
# 
# @param colorID2Arr - 2D array connect 
# @param emoticonIDList - List of emoticon IDs to replace colors for. 
# @param pixalatedInfo - Tuple (horizontal tiles, vertical tiles) 
# @parem tileInfo - Tuple (tileX, tileY, tileW, tileH)
# @param emoticonInfo - Tuple (emoticonW, emoticonH, emoticonID)
#
# @return - Returns image built out of emoticons in the emoticon list.
#############################################################################
def generateEmoticonArtImage(colorID2DArr, emoticonIDList, pixelatedInfo, tileInfo, emoticonInfo):
		
	countHorizontalTiles = pixelatedInfo[0]
	countVerticalTiles = pixelatedInfo[1]
	
	tileWidth = tileInfo[2]
	tileHeight = tileInfo[3]
	
	emoticonWidth = emoticonInfo[0]
	emoticonHeight = emoticonInfo[1]
	emoticonID = emoticonInfo[2]
	
	# Create a new image for the emoticon art
	emoticonImgSize = ( emoticonWidth * countHorizontalTiles, emoticonHeight * countVerticalTiles)
	emoticonImg = Image.new("RGB", emoticonImgSize, "white")
	emoticonImgPixels = emoticonImg.load()
	
	# Replace each unique colorID with an emoticon from the
	# emoticon list. 
	for tileY in xrange(0, countVerticalTiles):
		lstRow = colorID2DArr[tileY]
		for tileX in xrange(0, countHorizontalTiles):
			colorID = lstRow[tileX]
			emoticonID = emoticonIDList[colorID]
			# Draw Emoticon into Image
			drawEmoticonOnImage(emoticonImgPixels, 
								(tileX, tileY, tileWidth, tileHeight), 
								(emoticonWidth,emoticonHeight, emoticonID ))
		
	return emoticonImg
	
###########################################################################
# Helper function to draw an emoticon on an image. It will place the 
# emoticon in the in the specified tile of the image.
#
# @param imageOutPixels - Access object to the pixels on the output image
# @param tileInfo - Tuple with information on the tile (tileX, tileY,w,h)
# @param emoticonInfo - Tuple (emoticonW, emoticonH, emoticonID)
###########################################################################
def drawEmoticonOnImage(imageOutPixels, tileInfo, emoticonInfo):

	tileX = tileInfo[0]
	tileY = tileInfo[1]
	
	emoticonWidth = emoticonInfo[0]
	emoticonHeight = emoticonInfo[1]
	emoticonID = emoticonInfo[2]
	
	# Open Emoticon Image
	emoticonImg = Image.open("./emoticonsGmail/"+emoticonID+".gif")
	emoticonImg = emoticonImg.convert("RGB")
	emoticonImgPixels = emoticonImg.load()
	emoticonSizeActual = emoticonImg.size
	
	startX = tileX * emoticonWidth
	startY = tileY * emoticonHeight
	endX = startX + emoticonWidth
	endY = startY + emoticonHeight
	
	# Copy the emoticon to that tile on the screen.
	for y in xrange(startY, endY):
		if y - startY >= emoticonSizeActual[1]:
			break
			
		for x in xrange(startX, endX):
			if x - startX >= emoticonSizeActual[0]:
				break
			
			imageOutPixels[x, y] = emoticonImgPixels[x - startX, y - startY]

###########################################################################
# Given the emoticon ID this helper function will create the HTML code
# for displaying the emoticon on GMAIL
#
# @param emoticonID - id in GMAIL for the emoticon.
#
# @return - HTML code for the emoticon.
###########################################################################
def generateGMAILEmoticonHTMLFromID(emoticonID):
	#return '<img src="https://mail.google.com/mail/u/0/e/'+emoticonID+'" goomoji="'+emoticonID+'" style="margin: 0px 0.2ex; vertical-align: middle;">'
	# Produce a more compact image
	return '<img src="https://mail.google.com/mail/u/0/e/'+emoticonID+'" goomoji="'+emoticonID+'">'
	
	# Nice try but, it doesn't send as it shows. 
	#return '<img src="https://mail.google.com/mail/u/0/e/'+emoticonID+'" goomoji="'+emoticonID+'" style="width: 15px; height: 15px vertical-align: middle;">'

	
###########################################################################
# This function generates a pixelated image from the source image
# with the number of horizontal and vertical tiles.
#
# @param imgSrc - Source image to pixelate.
# @param countHorizontalTiles - Number of horizontal tiles.
# @param countVerticalTiles - Number of vertical tiles.
#
# @return - Pixelated image.
###########################################################################
def pixelateImage(imgSrc, countHorizontalTiles, countVerticalTiles, colorMinDistance):
	
	imagePixels = imgSrc.load()
	
	imgSize = imgSrc.size
	# Find the width for each tile given the desired number of horizontal tiles
	tileWidth = imgSize[0] / countHorizontalTiles
	# Find the height of each tile given the desired number of vertical tiles.
	tileHeight = imgSize[1] / countVerticalTiles
	
	# Copy image to dest image to overwrite later.
	imgDest = imgSrc.copy()
	# Get the pixels on the destination image so we re-write them
	outImgPixels = imgDest.load()
	
	for tileY in xrange(0, imgSize[1], tileHeight):
		for tileX in xrange(0, imgSize[0], tileWidth):
			tileInfo = (tileX, tileY, tileWidth, tileHeight)
			# Find common color in the tile
			color = inspectTile(imagePixels, imgSize, tileInfo)
			# Replace entire tile on the out image
			paintTileWithColor(color, outImgPixels, imgSize, tileInfo)

	
	# Perform Second Pass to merge all similar color tiles into one
	colorDict = {}
	for tileY in xrange(0, imgSize[1], tileHeight):
		for tileX in xrange(0, imgSize[0], tileWidth):
			# Get the color of the pixel in the pixelated image data
			tileColor = outImgPixels[tileX, tileY]
			if tileColor in colorDict:
				colorDict[tileColor] += (tileWidth * tileHeight)
			else:
				colorDict[tileColor] = (tileWidth * tileHeight)
	
	colorMappingDict = clusterColors(colorDict, colorMinDistance)
	
	# Replace the colors with the closest color available
	for tileY in xrange(0, imgSize[1], tileHeight):
		for tileX in xrange(0, imgSize[0], tileWidth):
			currColor = outImgPixels[tileX,tileY]
			colorToUse = colorMappingDict[currColor]
			tileInfo = (tileX, tileY, tileWidth, tileHeight)
			paintTileWithColor(colorToUse, outImgPixels, imgSize, tileInfo)
	
	
	return imgDest;
###########################################################################
# This function loads all the emoticon IDs available from a file. 
# 
# @param emoticonInitPath - path to the emoticon file.
#
# @return - List of emoticon IDs.
###########################################################################
def initializeEmoticons(emoticonInitPath):

	if not os.path.isfile(emoticonInitPath):
		return 
	
	emoticonFile = open(emoticonInitPath, 'r')
	
	emoticonIDList = []
	
	for line in emoticonFile:
		line = line.strip()
		# Ignore empty lines.
		if not line:
			continue
		# Ignore comments
		indexStartComment = line.index('#') 
		if indexStartComment == 0:
			continue
		
		# Separate the comment from the emoticon ID
		if indexStartComment > 0:
			line = line.partition("#")[0]
			
		emoticonIDList.append(line.strip())
		
	emoticonFile.close()
	
	return emoticonIDList

def main():
	
	argv = sys.argv
	
	fileSrcPath = argv[1]
	fileDestDir = "./outFiles/"
	colorMinDistance = 20
	
	# Catch incorrect usage.
	if len(argv) < 4:
		print "\n"
		print "***************************************************************************"
		print "Tool: GMAIL Emoji Generator v0.01" 
		print "Author: Frank Hernandez"
		print "\nHope you enjoy using this tool, feel free to tweet me any of your" 
		print "creations to @SourceMinion #GEGCreate\n"
			   
		print "Usage: python " + argv[0] +" ImagePath NumOfColumns NumOfRows Threshold(optional) \n"
		print "***************************************************************************"
		print "\n"
		return
		
	# Number of Horizontal Tiles
	countHorizontalTiles = 1
	# Number of Vertical Tiles
	countVerticalTiles = 1
	
	if len(argv) > 2:
		countHorizontalTiles = int(argv[2])
	
	if len(argv) > 3:
		countVerticalTiles = int(argv[3])
		
	if len(argv) > 4 :
		colorMinDistance = int(argv[4])
		#fileDestDir = argv[4]
	
	
	
	# Open Source Image
	im = Image.open(fileSrcPath)
	
	# Make output copy.
	outImg = im.copy();

	# Get our image pixels
	outImgPixels = outImg.load()

	# Get the pixels in the image as a 2D array
	imagePixels = im.load()

	# List of IDs matching the ids of emoticons in GMAIL
	emoticonListID = [
						"B60", #Small Stars
						"B68", #Big Star 
						"ezweb_ne_jp.B10", #Heart Pink 
						"ezweb_ne_jp.B17", # Heart With Bow
						"ezweb_ne_jp.03C", # Four Leaf Clover
						"softbank_ne_jp.B11", # Beating Heart
						"softbank_ne_jp.B12", # Arrow Pierced Heart
						"softbank_ne_jp.B14", # Green Heart
						"softbank_ne_jp.B15", # Yellow Heart
						"softbank_ne_jp.B16", # Purple Heart
						"softbank_ne_jp.B17", # Ribbon Shinning Heart
						"softbank_ne_jp.B18", # Two Hearts
						
						]
	
	emoticonListID = initializeEmoticons("./emoticonsGmail/_EmoticonIDsOrder.txt")
	
	imgSize = im.size
	# Calculate the width and height for the pixelated image
	tileSize = (
				imgSize[0] / countHorizontalTiles,
				imgSize[1] / countVerticalTiles
				)
	
	pixelatedInfo = (countHorizontalTiles, countVerticalTiles)
	tileInfo = (0,0, tileSize[0], tileSize[1] )
	
	outImg = pixelateImage(im, countHorizontalTiles, countVerticalTiles, colorMinDistance)
	outHTML = generateGMailEmoticonArt(outImg, emoticonListID, pixelatedInfo, tileInfo)
	# Generate an emoticon color map, this will make it easier when assigning the order of the emoticon list order to 
	# obtain the look we want.
	#outColorMap = generateColorMapForEmoticonArt(outImg, (countHorizontalTiles, countVerticalTiles), (0,0, tileSize[0], tileSize[1] ))
	# Generate 2D array containing color ID for this image.
	outColor2DArr = generateColorMapForEmoticonArt(outImg, pixelatedInfo, tileInfo)
	emoticonImgFinal = generateEmoticonArtImage(outColor2DArr, emoticonListID, pixelatedInfo, tileInfo, (15,15, ""))
	
	
	# Save HTML Code For Emoticon Art
	outFile = open(fileDestDir+"outfileHTML.txt", 'w')
	outFile.write(''.join(outHTML));
	outFile.close()
	
	# Safe the New Generated Pixel Image 
	outImg.save(fileDestDir +"outPixelFile.png")
	
	# Save the Emoticon Image For Preview.
	emoticonImgFinal.save(fileDestDir +"outEmoticonFile.png")

if __name__ == "__main__":
	main()
	