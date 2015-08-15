__author__ = 'Ahab'

import cardutils
import time

if __name__ == "__main__":
    print("No flop")
    print(time.ctime())
    result = cardutils.GenerateProbabilities(8,cardutils.Card(14,1), cardutils.Card(13,1)
                                    ,None,None,None,None,None,1000)
    print(result)
    print(time.ctime())

    print("Flop")
    print(time.ctime())
    result = cardutils.GenerateProbabilities(8,cardutils.Card(14,1), cardutils.Card(13,1)
                                    ,cardutils.Card(10,2),cardutils.Card(9,3),cardutils.Card(3,4),None,None,1000)
    print(result)
    print(time.ctime())

    print("Turn")
    print(time.ctime())
    result = cardutils.GenerateProbabilities(8,cardutils.Card(14,1), cardutils.Card(13,1)
                                    ,cardutils.Card(10,2),cardutils.Card(9,3),cardutils.Card(3,4),cardutils.Card(5,2),None,1000)
    print(result)
    print(time.ctime())

    print("River")
    print(time.ctime())
    result = cardutils.GenerateProbabilities(8,cardutils.Card(14,1), cardutils.Card(13,1)
                                    ,cardutils.Card(10,2),cardutils.Card(9,3),cardutils.Card(3,4),cardutils.Card(5,2),cardutils.Card(7,3),1000)
    print(result)
    print(time.ctime())