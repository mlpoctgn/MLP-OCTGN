import re

#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------
Action = ("Action", "ec99fdcb-ffea-4658-8e8f-5dc06e93f6fd") #The GUID from markers.o8g
GameURL = "http://tinyurl.com/ne3sb8t"
FaceoffColor1 = "#ff0000"
FaceoffColor2 = "#0000ff"
#---------------------------------------------------------------------------
# Globals
#---------------------------------------------------------------------------
FaceoffPosition = 0
FaceoffOffset = 0
#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------
	
def flipCoin(group, x = 0, y = 0):
	mute()
	n = rnd(1, 2)
	if n == 1:
		notify("{} flips heads.".format(me))
	else:
		notify("{} flips tails.".format(me))
		
def sixSided(group, x = 0, y = 0):
	mute()
	n = rnd(1,6)
	notify("{} rolls a {} on a 6-sided die.".format(me, n))

def inspired(targetgroup, x = 0, y = 0, count = None):
    mute()
    if len(players) == 1:
    	notify("There must be more than 1 player to use Inspired.")
    	return
    
    group = players[1].Deck
    	
    inspiredCount = sum(1 for card in table if card.controller == me and re.search(r'Inspired', card.Keywords))
    
    if count == None:
        count = askInteger("Look at how many cards?", inspiredCount)
    if count == None or count == 0:
        return
    
    notify("{} uses Inspired to look at the top {} cards of {}'s deck.".format(me, count, players[1]))
    
    topCards = group.top(count)

    buttons = []  ## This list stores all the card objects for manipulations.
    for c in topCards:
        c.peek()  ## Reveal the cards to python
        buttons.append(c)
       
    topList = []  ## This will store the cards selected for the top of the pile
    bottomList = []  ## For cards going to the bottom of the pile
    rnd(1,2)  ## allow the peeked card's properties to load
    loop = 'BOTTOM'  ## Start with choosing cards to put on bottom
           
    while loop != None:
        desc = "Select a card to place on {}:\n\n{}\n///////DECK///////\n{}".format(
                loop,
                '\n'.join([c.Name for c in topList]),
                '\n'.join([c.Name for c in bottomList]))
	if loop == 'TOP':
		num = askChoice(desc, [c.Type + ": " + c.Name + " " + c.Subname for c in buttons], customButtons = ["Select BOTTOM","Leave Rest on BOTTOM","Reset"])
		if num == -1:
			loop = 'BOTTOM'         
		elif num == -2:
			while len(buttons) > 0:
				card = buttons.pop()
				bottomList.append(card)
		elif num == -3:
			topList = []
			bottomList = []
			buttons = []
			for c in group.top(count):
				c.peek()
				buttons.append(c)
		elif num > 0:
			card = buttons.pop(num - 1)
			topList.insert(0, card)
	else:
		num = askChoice(desc, [c.Type + ": " + c.Name + " " + c.Subname for c in buttons], customButtons = ["Select TOP","Leave Rest on TOP","Reset"])
		if num == -1:
			loop = 'TOP'
		elif num == -2:
			while len(buttons) > 0:
				card = buttons.pop()
				topList.insert(0, card)
		elif num == -3:
			topList = []
			bottomList = []
			buttons = []
			for c in group.top(count):
				c.peek()
				buttons.append(c)
		elif num > 0:
			card = buttons.pop(num - 1)
			bottomList.append(card)
	if len(buttons) == 0: ##  End the loop
		loop = None
	if num == None:  ## closing the dialog window will cancel the ability, not moving any cards, but peek status will stay on.
		return
    topList.reverse()  ## Gotta flip topList so the moveTo's go in the right order
    for c in topList:
        c.moveTo(group)
    for c in bottomList:
        c.moveToBottom(group)
    for c in group:  ## This removes the peek status
        c.isFaceUp = True
        c.isFaceUp = False
    notify("{} looked at {} cards and put {} on top and {} on bottom.".format(me, count, len(topList), len(bottomList)))


#def inspiredPeek(card, x = 0, y = 0):
#	if len(players) == 1: return
#	choice = confirm("Do you want to activate Inspired to see the top card of your opponent's deck?")
#	if choice == True:
#		card = players[1].Deck.top()
#		card.peek()
#		whisper("Use Alt+Shift+I if you want to move this card to the bottom of their deck.")
	
#def inspiredMove(card, x = 0, y = 0):
#	if len(players) == 1: return
#	choice = confirm("Are you sure you want to move the top card to bottom of your opponent's deck?")
#	if choice == True:
#		card = players[1].Deck.top()
#		card.moveToBottom(players[1].Deck)
#		notify("{} has used Inspired to move a card to bottom of {}'s deck.".format(me, players[1]))

def clearFaceoff(group, x = 0, y = 0):
	mute()
	global FaceoffPosition
	global FaceoffOffset
	global FaceoffColor1
	global FaceoffColor2
	
	FaceoffPosition = 0
	FaceoffOffset = 0
	
	FaceoffCards = (card for card in table if card.highlight == FaceoffColor1 or card.highlight == FaceoffColor2)
	
	count = 0
	for card in FaceoffCards:
		card.moveToBottom(card.owner.Deck)
		count += 1
	
	if count > 0:
		notify("Faceoff Cards have been put on the bottoms of their owner's decks.")

def readyAll(group, x = 0, y = 0): 
	mute()
	myCards = (card for card in table
				if card.controller == me
				and card.owner == me)
	for card in myCards:
		if card.isFaceUp:
			card.orientation &= ~Rot90
			card.highlight = None
	notify("{} readies all their cards.".format(me))

def turnStart(group, x = 0, y = 0):
	mute()
	maxPoints = 0
	maxName = ""
	addActions = 0
	
	if me.getGlobalVariable("TurnStarted") == "True":
		whisper("You've already started your turn.")
		return
	
	if me.isActivePlayer:
		notify("*{} begins Turn {}*".format(me, turnNumber()))
		me.setGlobalVariable("TurnStarted", "True")
	else:
		whisper("You can't start the turn when it isn't your turn. If you are just starting a new game, click the green arrow on a player's tab to make him first player.")
		return
	
	checkFirstTurn = getGlobalVariable("FirstTurn")
			
	for person in players:
		if maxPoints < person.counters['Points'].value:
			maxPoints = person.counters['Points'].value
			maxName = person.name
		
	if maxPoints < 2:
		addActions = 2
	elif maxPoints < 6:
		addActions = 3
	elif maxPoints < 11:
		addActions = 4
	else:
		addActions = 5
	
	if maxPoints == 0:
		notify("*Nobody has Points yet. {} adds {} Action Tokens.*".format(me,addActions))
	else:	
		notify("*{} has {} Points. {} adds {} Action Tokens.*".format(maxName,maxPoints,me,addActions))
	
	me.counters['Actions'].value = me.counters['Actions'].value + addActions
	
	if checkFirstTurn == "True":
		notify("{} does not draw on the game's first turn.".format(me))
		setGlobalVariable("FirstTurn", "False")
	else:
		draw(me.deck)

def turnTroublemaker(group, x = 0, y = 0):
	mute()
	if me.isActivePlayer:
		clearFaceoff(group, x, y)
		notify("*{} begins their Troublemaker Phase.*".format(me))
	else:
		whisper("You can't set the phase when it isn't your turn.")	

def turnMain(group, x = 0, y = 0):
	mute()
	if me.isActivePlayer:
		clearFaceoff(group, x, y)
		notify("*{} begins their Main Phase.*".format(me))
	else:
		whisper("You can't set the phase when it isn't your turn.")	

def turnScore(group, x = 0, y = 0):
	mute()
	if me.isActivePlayer:	
		clearFaceoff(group, x, y)
		notify("*{} begins their Score Phase.*".format(me))
	else:
		whisper("You can't set the phase when it isn't your turn.")	

def turnDone(group, x = 0, y = 0):
	mute()
	if me.isActivePlayer:
		me.setGlobalVariable("TurnStarted", "False")
		clearFaceoff(group, x, y)
		if len(players) == 2:
			players[1].setActivePlayer()
			notify("*{} is done. It is now {}'s turn.*".format(me, players[1]))
		else:
			notify("*{} is done.*".format(me))			
	else:
		whisper("You can't pass the turn when it isn't your turn.")

def holdOn(group, x = 0, y = 0):
	mute()
	notify("*{} has an reaction/question.*".format(me))
	
def setup(group, x = 0, y = 0):
	ManeCheck = 0
	
	if not confirm("Setup your side of the table?"): return

	for card in me.hand:
		if card.Type == 'Problem': 
			card.moveTo(me.piles['Problem Deck'])
		elif card.Type != 'Mane Character' and card.Type != 'Mane Character Boosted': 
			card.moveTo(me.Deck)
	

	for card in me.piles['Discard Pile']:
		if card.Type == 'Mane Character': 
			card.moveTo(me.hand)
		elif card.Type == 'Mane Character Boosted': 
			card.moveTo(me.hand)
		elif card.Type == 'Problem': 
			card.moveTo(me.piles['Problem Deck'])
		else: 
			card.moveTo(me.Deck)
	
	for card in me.piles['Banished Pile']: 
		if card.Type == 'Mane Character': 
			card.moveTo(me.hand)
		elif card.Type == 'Mane Character Boosted': 
			card.moveTo(me.hand)
		elif card.Type == 'Problem': 
			card.moveTo(me.piles['Problem Deck'])
		else: 
			card.moveTo(me.Deck)

	myCards = (card for card in table
        	if card.owner == me)

	for card in myCards:
		if card.Type == 'Mane Character': 
			card.moveTo(me.hand)
		elif card.Type == 'Mane Character Boosted': 
			card.moveTo(me.hand)
		elif card.Type == 'Problem': 
			card.moveTo(me.piles['Problem Deck'])
		else: 
			card.moveTo(me.Deck)
	
	for card in me.hand: 
		if card.Type == 'Mane Character':
			if me.hasInvertedTable():
				card.moveToTable(0,-220)
			else:				
				card.moveToTable(0,130)
			ManeCheck = ManeCheck + 1
		elif card.Type == 'Mane Character Boosted':
			if me.hasInvertedTable():
				card.moveToTable(0,-220)
			else:				
				card.moveToTable(0,130)
			card.switchTo()
			ManeCheck = ManeCheck + 1
		else:
			notify("{}: Invalid Setup! Must not have any other cards in hand but your Mane Character".format(me))
			return

	if ManeCheck != 1:
		notify("{}: Invalid Setup! Must have exactly one copy of a Mane Character in your deck!".format(me))
		return

	mute()

	shuffle(me.Deck)
	
	if len(me.Deck) == 0: return
	if len(me.Deck) < 6:
		drawAmount = len(group)
	
	for card in me.Deck.top(6):
		card.moveTo(me.hand)
	notify("{} draws their opening hand of {} cards.".format(me, 6))	

	notify("{} has set up their side of the table.".format(me))

	setGlobalVariable("FirstTurn", "True")
		
	me.counters['Points'].value = 0
	me.counters['Actions'].value = 0
	

def scoop(group, x = 0, y = 0):
	mute()
	
	if not confirm("Scoop your side of the table?"): return
	
	for c in me.hand: 
		if not c.Type == "Mane Character":
			c.moveTo(me.Deck)			
	for c in me.piles['Discard Pile']: c.moveTo(me.Deck)
	for c in me.piles['Banished Pile']: c.moveTo(me.Deck)

	myCards = (card for card in table
        	if card.owner == me)

	for card in myCards:
		if card.Type == "Mane Character": 
			card.moveTo(me.hand)
		elif card.Type == "Problem": 
			card.moveTo(me.piles['Problem Deck'])
		else: 
			card.moveTo(me.Deck)
	
	notify("{} scoops their side of the table.".format(me))

def gainPoint(group, x = 0, y = 0):
	me.counters['Points'].value = me.counters['Points'].value + 1

def losePoint(group, x = 0, y = 0):
	me.counters['Points'].value = max(0, me.counters['Points'].value - 1)
	
def gainAction(group, x = 0, y = 0):
	me.counters['Actions'].value = me.counters['Actions'].value + 1
	
def loseAction(group, x = 0, y = 0):
	me.counters['Actions'].value = max(0, me.counters['Actions'].value - 1)

#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------		
def exhaust(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} exhausts {}.'.format(me, card))
    else:
        notify('{} readies {}.'.format(me, card))

def flipcard(card, x = 0, y = 0):
    mute()
    
    if card.Type == 'Mane Character':
	card.switchTo('Mane Character Boosted')
    	notify("{} flips {}.".format(me, card))
    	return 
    
    if card.Type == 'Mane Character Boosted':
    	card.switchTo()
        notify("{} flips {}.".format(me, card))
        return 

    if card.isFaceUp:
        notify("{} turns {} face down.".format(me, card))
        card.isFaceUp = False
    else:
        card.isFaceUp = True
        notify("{} turns {} face up.".format(me, card))

def addAction(card, x = 0, y = 0):
	mute()
	notify("{} adds an Action Marker to {}.".format(me, card))
	card.markers[Action] += 1
        
def subAction(card, x = 0, y = 0):
    mute()
    notify("{} subtracts an Action Marker from {}.".format(me, card))
    card.markers[Action] -= 1
        
#------------------------------------------------------------------------------
# Hand Actions
#------------------------------------------------------------------------------

def randomDiscard(group):
	mute()
	card = group.random()
	if card == None: return
	card.moveTo(me.piles['Discard pile'])
	notify("{} randomly discards {}.".format(me, card))
 
def discardMany(group):
	count = 0
	discAmount = None
	
	mute()
	if len(group) == 0: return
	if discAmount == None: discAmount = askInteger("Randomly discard how many cards?", 2)
	if discAmount == None: return
	
	for index in range(0,discAmount):
		card = group.random()
		if card == None: break
		card.moveTo(me.piles['Discard pile'])
		count += 1
		notify("{} randomly discards {}.".format(me,card))
	notify("{} randomly discards {} cards.".format(me, count))

def mulligan(group):
	count = None
	draw = None
	mute()
	
	if not confirm("Are you sure you want to Mulligan?"): return
	if draw == None: draw = askInteger("How many cards would you like to draw for your Mulligan?", len(me.hand))
	if draw == None: return
	
	for card in group:
		card.moveToBottom(me.deck)
			
	me.deck.shuffle()
		
	for card in me.deck.top(draw):
		card.moveTo(me.hand)
	notify("{} mulligans and draws {} new cards.".format(me, draw))

#------------------------------------------------------------------------------
# Pile Actions
#------------------------------------------------------------------------------

def shuffle(group):
	group.shuffle()

def draw(group):
	mute()
	if len(group) == 0: return
	group[0].moveTo(me.hand)
	notify("{} draws a card.".format(me))
	
def drawRandom(group):
	mute()
	
	card = group.random()
	if card == None: return
	card.moveTo(me.hand)
	notify("{} randomly draws a Problem card.".format(me))

def drawMany(group):
	drawAmount = None
	
	mute()
	if len(group) == 0: return
	if drawAmount == None: drawAmount = askInteger("Draw how many cards?", 6)
	if drawAmount == None: return
	
	if len(group) < drawAmount:
		drawAmount = len(group)
	
	for card in group.top(drawAmount):
		card.moveTo(me.hand)
	notify("{} draws {} cards.".format(me, drawAmount))
 
def discardManyFromTop(group):
	count = 0
	discAmount = None
	
	mute()
	if len(group) == 0: return
	if discAmount == None: discAmount = askInteger("Discard how many from top?", 4)
	if discAmount == None: return
	
	for index in range(0,discAmount):
		card = group.top()
		card.moveTo(me.piles['Discard pile'])
		count += 1
		if len(group) == 0: break
	notify("{} discards {} cards from the top of their Deck.".format(me, count))
 	
def reshuffle(group):
	count = None
	
	mute()
	if len(group) == 0: return
	if not confirm("Are you sure you want to reshuffle the {} back into your deck?".format(group.name)): return
	
	myDeck = me.deck
	for card in group:
		card.moveTo(myDeck)
	myDeck.shuffle()
	notify("{} shuffles their {} back into their deck.".format(me, group.name))
	
def moveOneRandom(group):
	mute()
	if len(group) == 0: return
	if not confirm("Are you sure you want to move one random card from your {} to your Hand?".format(group.name)): return
	
	card = group.random()
	if card == None: return
	card.moveTo(me.hand)
	notify("{} randomly moves {} from their {} to their hand.".format(me, card.name, group.name))	
	
def faceoffFlip(group):
	mute()
	global FaceoffColor1
	global FaceoffColor2
	global FaceoffPosition
	global FaceoffOffset

	if len(group) == 0: return


	if me.hasInvertedTable():
		if FaceoffPosition == 0:
			FaceoffPosition = -110
		else:
			FaceoffOffset += 1
		newYPos = FaceoffPosition + (-15 * FaceoffOffset)
		newXPos = 15 * FaceoffOffset
		color = FaceoffColor1
	else:
		if FaceoffPosition == 0:
			FaceoffPosition = 10
		else:
			FaceoffOffset += 1
		newYPos = FaceoffPosition + (15 * FaceoffOffset)
		newXPos = -15 * FaceoffOffset
		color = FaceoffColor2
	
	card = group.top()
	
	card.moveToTable(newXPos, newYPos)
	
	card.highlight = color
	
	notify("{} flips {} for the faceoff with printed power {}.".format(me, card, card.Power))