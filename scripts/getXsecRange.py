def getXsecRange(neutralinopoint,gluinopoint):

	if neutralinopoint > 50:
		if gluinopoint <= 150 :
			return [0.1, 1.0, 10.0, 100.0]
		elif gluinopoint == 175:
			return [0.1, 1.0, 10.0, 50.0]
		elif gluinopoint == 200:
			return [0.1, 1.0, 10.0, 30.0]
		elif gluinopoint <= 325:
			return [0.05, 0.1, 1.0, 10.0]
		elif gluinopoint <= 400:
			return [0.01, 0.05, 0.5, 5.0]
		elif gluinopoint <= 450:
			return [0.005, 0.01, 0.1, 3.0]
		elif gluinopoint <= 500:
			return [0.005, 0.01, 0.1, 1.0]
		elif gluinopoint <= 575:
			return [0.001, 0.005, 0.1, 0.5]
		elif gluinopoint <= 625:
			return [0.001, 0.003, 0.05, 0.1, 0.5] # added for leptons
		elif gluinopoint <= 775:
			return [0.001, 0.003, 0.02, 0.08, 0.1] # added for leptons
		elif gluinopoint == 800:
			return [0.0005, 0.001, 0.008, 0.08, 0.1] # added for leptons

	else:
	    if gluinopoint <= 150 :
	        return [0.01, 0.05, 0.07, 1.0, 2.0]
	    elif gluinopoint ==175 :
	        return [0.01, 0.05, 0.07, 1.0, 1.5]
	    elif gluinopoint == 200 :
	        return [0.01, 0.05, 0.07, 0.5, 0.7, 1.0, 1.5]
	    elif gluinopoint == 225 :
	        return [ 0.05, 0.1, 0.2, 0.5, 0.7, 1.0, 1.5]
	    elif gluinopoint == 250 :
	        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 275 :
	        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 300 :
	        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 325 :
	        return [  0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 350 :
	        return [  0.05, 0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 375 :
	        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 400 :
	        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
	    elif gluinopoint == 425 :
	        return [ 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
	    elif gluinopoint == 450 :
	        return [ 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
	    elif gluinopoint == 475 :
	        return [ 0.01, 0.1, 0.2, 0.3, 0.5]
	    elif gluinopoint == 500 :
	        return [ 0.01, 0.05, 0.1, 0.2, 0.3]
	    elif gluinopoint == 525 :
	        return [0.01, 0.05, 0.1, 0.2]
	    elif gluinopoint == 550 :
	        return [ 0.01, 0.05, 0.1, 0.2, 0.3]
	    elif gluinopoint == 575 :
	        return [ 0.01, 0.05, 0.1, 0.2, 0.3]
	    elif gluinopoint == 600 :
	        return [ 0.005, 0.01, 0.05, 0.1, 0.2]
	    elif gluinopoint == 625 :
	        return [ 0.005, 0.01, 0.05, 0.1, 0.2]
	    elif gluinopoint == 650 :
	        return [ 0.005, 0.01, 0.05, 0.1]
	    elif gluinopoint == 675 :
	        return [ 0.005, 0.01, 0.05, 0.1]
	    elif gluinopoint == 700 :
	        return [ 0.005, 0.01, 0.03, 0.05, 0.1] 
	    elif gluinopoint == 725 :
	        return [ 0.005, 0.01, 0.03, 0.05, 0.1]
	    elif gluinopoint == 750 :
	        return [ 0.005, 0.01, 0.03, 0.05, 0.1]
	    elif gluinopoint == 775 :
	        return [ 0.005, 0.01, 0.03, 0.05, 0.1]
	    elif gluinopoint == 800 :
	        return [ 0.005, 0.01, 0.03, 0.05, 0.1]