# TODO: check with siva
def majority(array,maj_threshold):
    counter = 1
    #guess = array[]
    for i in range(1,array.amount()):
        if array[i] == guess :
            counter++
        else:
            if counter == 0:
                counter = 1
                guess = array[i]
            else: 
                counter--
    counter = 0
    for i in range(array.amount()):
        if array[i]==guess:
            counter++
    if counter >= maj_threshold :
        return [1,guess]
    else:
        return [0,guess]
