class prngen: 
    SV = {
    1: [2, 6],
    2: [3, 7],
    3: [4, 8],
    4: [5, 9],
    5: [1, 9],
    6: [2, 10],
    7: [1, 8],
    8: [2, 9],
    9: [3, 10],
    10: [2, 3],
    11: [3, 4],
    12: [5, 6],
    13: [6, 7],
    14: [7, 8],
    15: [8, 9],
    16: [9, 10],
    17: [1, 4],
    18: [2, 5],
    19: [3, 6],
    20: [4, 7],
    21: [5, 8],
    22: [6, 9],
    23: [1, 3],
    24: [4, 6],
    25: [5, 7],
    26: [6, 8],
    27: [7, 9],
    28: [8, 10],
    29: [1, 6],
    30: [2, 7],
    31: [3, 8],
    32: [4, 9],
}

    @staticmethod
    def shift_register1(array):
        sum_val = array[2] + array[9]
        if sum_val % 2 == 0:
            return 0
        else:
            return 1

    @staticmethod
    def shift_register2(array):
        sum_val = array[1] + array[2] + array[5] + array[7] + array[8] + array[9]
        if sum_val % 2 == 0:
            return 0
        else:
            return 1

    @staticmethod
    def prnmain(svcode):
        g1 = [1] * 10
        g2 = [1] * 10
        prncode = [0] * 1023
        
        for j in range(1023):
            val1 = shift_register1(g1)
            val2 = shift_register2(g2)
            add2 = g2[svcode[0] - 1] + g2[svcode[1] - 1]
            output1 = 0
            
            for k in range(9, -1, -1):
                if k == 9:
                    output1 = g1[k]
                if k == 0:
                    g1[k] = val1
                    g2[k] = val2
                    break
                g1[k] = g1[k - 1]
                g2[k] = g2[k - 1]
            
            if (output1 + add2) % 2 == 0:
                prncode[j] = 0
            else:
                prncode[j] = 1
        
        return prncode

class subframe1gen:
    tlmword = [1, 0, 0, 0, 1, 0, 1, 1]
    for i in range(8, 29):
        tlmword.append(0)

    how = []
    



