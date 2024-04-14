import sys
sys.path.append('/Users/henryhenryson/Documents/TUM/Bachelor-Thesis-Info/01_Software/tl_simplification')

from expression.ltl_data_classes import *
from inference.int_set import IntegerSet
from ltlf.ltlf_interval_functions import *
import random


def check_G(I_true_r, I_false_r, I, I_true, I_false):
    true_r_inf = I_true_r.is_inf()
    false_r_inf = I_false_r.is_inf()
    I_true_r = I_true_r.get_deterministic()
    I_false_r = I_false_r.get_deterministic()
    I_true = I_true.get_deterministic()
    I_false = I_false.get_deterministic()
    
    a = I[0]
    b = I[1]

    if b == None:
        b = 199

    res_I_true = []

    for i in range(0,200):
        is_true = True
        for n in range(a, b+1):
            if not (i+n>199 and true_r_inf) and not i+n in I_true_r:
                is_true = False
                break
        
        if is_true:
            res_I_true.append(i)

    res_I_false = []
    for i in range(0,200):
        is_false = False
        
        for n in range(a,b+1):
            if i+n in I_false_r:
                is_false = True
                break

            if i+n > 199 and false_r_inf:
                is_false = True
                break


        if is_false:
            res_I_false.append(i)
    
    res_I_true = set(res_I_true)
    res_I_false = set(res_I_false)
    
    if res_I_false != I_false:
        print("failed G for I_false:")
        print(res_I_false)
    
    if res_I_true != I_true:
        print("failed G for I_true:")
        print(res_I_true)
        
    return res_I_false == I_false and res_I_true == I_true

    



def check_X(I_true_r, I_false_r, I, I_true, I_false):
    true_r_inf = I_true_r.is_inf()
    false_r_inf = I_false_r.is_inf()
    I_true_r = I_true_r.get_deterministic()
    I_false_r = I_false_r.get_deterministic()
    I_true = I_true.get_deterministic()
    I_false = I_false.get_deterministic()
    
    a = I[0]
    b = I[1]

    if b == None:
        b = 199

    res_I_true = []

    for i in range(0,200):
        if i+a in I_true_r or (i+a>199 and true_r_inf):
            res_I_true.append(i)
            

    res_I_false = []
    for i in range(0,200):
        if i+a in I_false_r or (i+a>199 and false_r_inf):
            res_I_false.append(i)
    
    res_I_true = set(res_I_true)
    res_I_false = set(res_I_false)
    
    if res_I_false != I_false:
        print("failed X for I_false:")
        print(res_I_false)
    
    if res_I_true != I_true:
        print("failed X for I_true:")
        print(res_I_true)
        
    return res_I_false == I_false and res_I_true == I_true
    


def check_F(I_true_r, I_false_r, I, I_true, I_false):
    true_r_inf = I_true_r.is_inf()
    false_r_inf = I_false_r.is_inf()
    I_true_r = I_true_r.get_deterministic()
    I_false_r = I_false_r.get_deterministic()
    I_true = I_true.get_deterministic()
    I_false = I_false.get_deterministic()
    
    a = I[0]
    b = I[1]

    if b == None:
        b = 199

    res_I_true = []
    for i in range(0,200):
        for n in range(a, b+1):
            if i+n in I_true_r or (i+n>199 and true_r_inf):
                res_I_true.append(i)
                break

    res_I_false = []
    for i in range(0,200):
        is_false = True
        for n in range(a, b+1):
            if not (i+n in I_false_r or (i+n>199 and false_r_inf)):
                is_false = False
                break

        if is_false:
            res_I_false.append(i)
    
    res_I_true = set(res_I_true)
    res_I_false = set(res_I_false)
    
    if res_I_false != I_false:
        print("failed F for I_false:")
        print(res_I_false)
    
    if res_I_true != I_true:
        print("failed F for I_true:")
        print(res_I_true)
        
    return res_I_false == I_false and res_I_true == I_true

    
def check_U_true(I_true_l,I_true_r, I, I_true):
    true_r_inf = I_true_r.is_inf()
    
    true_l_inf = I_true_l.is_inf()
    
    
    I_true_r = I_true_r.get_deterministic()
    I_true_l = I_true_l.get_deterministic()
    I_true = I_true.get_deterministic()


    a = I[0]
    b = I[1]

    if b == None:
        b = 199

    # True Set
    res_I_true = []
    for t in range(0,200):
        for n in range(0,b+1):
            if n>=a:
                if t+n in I_true_r or (true_r_inf and t+n>199):
                    res_I_true.append(t)
                    break
            if t+n in I_true_l or (true_l_inf and t+n>199):
                continue
            else:
                break
    
    res_I_true = set(res_I_true)
    
    
    
    if res_I_true != I_true:
        print("failed U for I_true:")
        print(res_I_true)
        
    return res_I_true == I_true

def check_U_false(I_false_l, I_false_r, I, I_false):
    
    false_r_inf = I_false_r.is_inf()
    
    false_l_inf = I_false_l.is_inf()
    
    I_false_r = I_false_r.get_deterministic()
    I_false_l = I_false_l.get_deterministic()
    I_false = I_false.get_deterministic()

    a = I[0]
    b = I[1]

    if b == None:
        b = 199


    res_I_false = []
    for t in range(0,200):
        is_false = True
        for n in range(a,b+1):
            if not (t+n in I_false_r or (t+n>199 and false_r_inf)):
                is_false = False

        if is_false:
            res_I_false.append(t)
            continue

        
        for n in range(0,a):
            if (t+n in I_false_l or (t+n>199 and false_l_inf)):
                is_false = True
                break
        
        if is_false:
            res_I_false.append(t)
            continue

        for n in range(a,b+1):
            if t+n in I_false_r or (t+n>199 and false_r_inf):
                if t+n in I_false_l or (t+n>199 and false_l_inf):
                    res_I_false.append(t)
                    break
                else:
                    continue
            else:
                break
        
            
    res_I_false = set(res_I_false)
    
    if res_I_false != I_false:
        print("failed U for I_false:")
        print(f"I_false_res: {IntegerSet(res_I_false, False)}")
        
    

        
    return res_I_false == I_false






def test_random(iterations):

    for i in range(iterations):
        l1 = random.randint(0,60)
        s1 = []
        for i in range(l1):
            if random.randint(0,1) == 1:
                s1.append(i)
        set1 = set(s1)

        l2 = random.randint(0,60)
        s2 = []
        for i in range(l2):
            if random.randint(0,1) == 1:
                s2.append(i)
        set2 = set(s2)

        if random.randint(0,1) == 1:
            I_true_r = IntegerSet(set1, True)
        else:
            I_true_r = IntegerSet(set1, False)

        if random.randint(0,1) == 1:
            I_false_r = IntegerSet(set2, True)
        else:
            I_false_r = IntegerSet(set2, False)

        
        a = random.randint(0,20)
        if random.randint(0,1) != 1:
            b = a+random.randint(0,20)
        else:
            b = None

        
        I_true, I_false = interval_G(I_true_r, I_false_r, (a,b))
        
        if not check_G(I_true_r, I_false_r, (a,b), I_true, I_false):

            print(f"I_true_r  : {I_true_r}")
            print(f"I_false_r : {I_false_r}")
            print(f"a: {a}, b: {b}")
            print(f"I_true    : {I_true}")
            print(f"I_false   : {I_false}")
            print("------------")
        
        I_true, I_false = interval_X(I_true_r, I_false_r, (a,b))

        if not check_X(I_true_r, I_false_r, (a,b), I_true, I_false):
            print(f"I_true_r  : {I_true_r}")
            print(f"I_false_r : {I_false_r}")
            print(f"a: {a}, b: {b}")
            print(f"I_true    : {I_true}")
            print(f"I_false   : {I_false}")
            print("------------")

        I_true, I_false = interval_F(I_true_r, I_false_r, (a,b))
        
        if not check_F(I_true_r, I_false_r, (a,b), I_true, I_false):
            print(f"I_true_r  : {I_true_r}")
            print(f"I_false_r : {I_false_r}")
            print(f"a: {a}, b: {b}")
            print(f"I_true    : {I_true}")
            print(f"I_false   : {I_false}")
            print("------------")


        I_true_l = I_false_r
        I_false_l = I_true_r

        I_true, I_false = interval_U(I_true_l, I_false_l, I_true_r, I_false_r, (a,b))

        if not check_U_true(I_true_l, I_true_r, (a,b), I_true):
            print(f"I_true_l  : {I_true_l}")
            print(f"I_true_r  : {I_true_r}")
            
            print(f"a: {a}, b: {b}")
            print(f"I_true    : {I_true}")
            print("------------")
            I_true, I_false = interval_U(I_true_l, I_false_l, I_true_r, I_false_r, (a,b))
            return


        
        if not check_U_false(I_false_l, I_false_r, (a,b), I_false):
            print(f"I_false_l  : {I_false_l}")
            print(f"I_false_r  : {I_false_r}")

            print(f"a: {a}, b: {b}")
            print(f"I_false    : {I_false}")            
            print("------------")
            I_true, I_false = interval_U(I_true_l, I_false_l, I_true_r, I_false_r, (a,b))
            return
        
        
            



if "__main__" == __name__:
    test_random(999999)
    