def majority(array,maj_threshold):
    if len(array) == 0 :
    	return (False, None)

    counter = 1
    guess = array[0]
    for i in range(1,len(array)):
        if array[i] == guess :
            counter += 1
        else:
            if counter == 0:
                counter = 1
                guess = array[i]
            else: 
                counter -= 1
    counter = 0
    for i in range(len(array)):
        if array[i]==guess:
            counter +=1
    if counter >= maj_threshold :
        return (True,guess)
    else:
        return (False,guess)
