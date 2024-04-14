from typeguard import typechecked
from tl_simplification.inference.predicate import PredicateChecker
from tl_simplification.expression.ltl_data_classes import *
from tl_simplification.inference.int_set import IntegerSet, BiDict
from tl_simplification.ltlf.ltlf_interval_functions import *


    

class LTLf():

    """ Algorithms: """

    @typechecked
    def interval_simplification(exp : Expression, I : IntegerSet, pred_check : PredicateChecker):
        match exp:
            case AtomicProposition(ap):
                S = BiDict()
                S.add_exp_in(exp, I)
                return S

            case Predicate(name, terms):
                # Predicate Check (called Proposition Check in Thesis)
                I_true, I_false = pred_check.check_predicate(name, terms)
                S = BiDict()
                S.add_exp_in(Wahr(), I_true.intersection(I))
                S.add_exp_in(Falsch() ,I_false.intersection(I))
                S.add_exp_in(exp, I.without(I_false.union(I_true)))
                return S

            case Wahr():
                S = BiDict()
                S.add_exp_in(Wahr(),IntegerSet.n0().intersection(I))
                return S
                
            case Falsch():
                S = BiDict()
                S.add_exp_in(Falsch(),IntegerSet.n0().intersection(I))
                return S
            
            case UnaryExpression(op_type, exp):
                # PropagateInterval
                I_r = propagate_interval(I, op_type)

                # IntervalSimplification
                S_r = LTLf.interval_simplification(exp, I_r, pred_check)

                # Simplify
                S = LTLf.simplify(op_type, I, S_r)
                
                return S

            case BinaryExpression(op_type, exp_l, exp_r):

                I_l, I_r = propagate_interval(I, op_type)

                S_l = LTLf.interval_simplification(exp_l, I_l, pred_check)
                S_r = LTLf.interval_simplification(exp_r, I_r, pred_check)

                S = LTLf.simplify(op_type, I, S_r, S_l)
                return S

            case MultiExpression(op_type, expressions):
                
                I_sub = propagate_interval(I, op_type)

                S_sub = [LTLf.interval_simplification(exp_sub, I_sub, pred_check) for exp_sub in expressions]

                S = LTLf.simplify_multi(op_type, I_sub, S_sub)

                return S
        raise ValueError("ahsdla")


    """ Simplification: """

    @typechecked
    def simplify(op_type, I : IntegerSet, S_r : BiDict, S_l = None):
        
        match op_type:
            case TempBinOp(op, (a,b)):
                match op:
                    case "U": return LTLf.simplify_U(I, S_l, S_r,a,b)
                    case "S": return 
                        
            case TempUnOp(op, (a,b)):
                match op:
                    case "G": return LTLf.simplify_G(I, S_r, a,b)
                    case "F": return LTLf.simplify_F(I, S_r, a,b)
                    case "X": return LTLf.simplify_X(I, S_r, a)
                    case "P": return LTLf.simplify_P(I, S_r, a)
                    case "O": return LTLf.simplify_O(I, S_r, a,b)
                                             
            case LogicBinOp(op):
                match op:
                    case "and": return LTLf.simplify_AND(I, S_l, S_r)
                    case "or": return LTLf.simplify_OR(I, S_l, S_r)
                    case "imp": return LTLf.simplify_IMP(I, S_l, S_r)


            case LogicUnOp(op):
                match op:
                    case "not": return LTLf.simplify_NOT(I, S_r)


    @typechecked
    def simplify_multi(op_type, I : IntegerSet, S_sub : List[BiDict]):
        match op_type:
            case LogicMultiOp(op):
                match(op):
                
                    case "conjunction":
                        S = S_sub[0]
                        for i in range(1, len(S_sub)):
                            S = LTLf.simplify_AND(I, S, S_sub[i])
                        return S

                    case "disjunction":
                        S = S_sub[0]
                        for i in range(1, len(S_sub)):
                            S = LTLf.simplify_OR(I, S, S_sub[i])
                        return S


    def simplify_U(I : IntegerSet, S_l : BiDict, S_r : BiDict, a, b):
        I_true, I_false = interval_U(S_r.get_I(Wahr()), S_r.get_I(Falsch()), S_l.get_I(Wahr()), S_l.get_I(Falsch()), (a,b))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        I = I.without(I_true.union(I_false))

        J_l = S_l.get_J()
        J_r = S_r.get_J()

        no_change_start_r = S_r.no_change_start()
        no_change_start_l = S_l.no_change_start()
        no_change_start = max(no_change_start_l, no_change_start_r)

        for t in I:
            
            #split(J_l, J_r, [a+t, b+t])
            ivl = [a+t, None]
            
            if ivl[1] != None:
                ivl[1] = b+t
            omega = IntegerSet.from_interval(ivl)
            splits = IntegerSet.split(J_l, J_r, omega)

            # V
            disjunction = []
            print(splits)
            for split in splits:        # split = [x,y]
                x = split[0]
                y = split[1]
                S_G = LTLf.simplify_G(IntegerSet([t],False), S_l,0, x-t-1)
                simp_exp1 = S_G.get_at_timestep(t)

                exp_l = S_l.get_at_timestep(x)
                exp_r = S_r.get_at_timestep(x)

                
                
                
                if exp_l == Wahr():
                    left_bound = None if y == None else y-t
                    simp_exp2 = LTLf.eventually(exp_r, (x-t, left_bound))
                else:
                    left_bound = None if y == None else (y-x)-t 
                    simp_exp2 = LTLf.next(LTLf.until(exp_l, exp_r, (0,left_bound)),x-t)
                
                if simp_exp1 == Wahr():
                    disjunction.append(simp_exp2)
                else:
                    disjunction.append(LTLf._and(simp_exp1, simp_exp2))
                

            
            simp_exp = LTLf.disjunction(disjunction)

            if t >= no_change_start:                               # At this point simplified formulas do not change anymore
                rest = IntegerSet([t], True).intersection(I)
                S.add_exp_in(simp_exp, rest)    
                return S                    
            else:
                S.add_exp_at(simp_exp, t)
        
        return S

    def simplify_G(I : IntegerSet, S_r : BiDict, a, b):
        #if a < b:
         #   S = BiDict()
          #  S.add_exp_in(Wahr(), I)
           # return S
        
        I_true, I_false = interval_G(S_r.get_I(Wahr()), S_r.get_I(Falsch()), (a,b))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        
        I = I.without(I_true.union(I_false))

        no_change_start_r = S_r.no_change_start()
        for t in I:
            outer_conjunctions = []
            F = S_r.get_F()
                                
            for phi in F:
                inner_conjunctions = []
                if b == None:
                    timestep_interval = (a+t, None)     # timestep_interval = [a+t,b+t]
                else:
                    timestep_interval = (a+t, b+t)
                                    
                partitions = IntegerSet.partition(S_r.get_I(phi).intersection(IntegerSet.from_interval(timestep_interval)))

                for ivl in partitions:      # ivl = [x,y]
                    new_ivl = ivl.copy()
                    new_ivl[0] -= t
                    if new_ivl[1] != None:
                        new_ivl[1] -= t         # new_ivl = [x-t, b-t]

                    inner_conjunctions.append(LTLf.always(phi,new_ivl))         # G_[x-t, b-t] phi

                outer_conjunctions.append(LTLf.conjunction(inner_conjunctions))


            simp_exp = LTLf.conjunction(outer_conjunctions)

            if t >= no_change_start_r:                               # At this point simplified formulas do not change anymore
                rest = IntegerSet([t], True).intersection(I)
                S.add_exp_in(simp_exp, rest)    
                return S                    
            else:
                S.add_exp_at(simp_exp, t)
                            
        return S

    def simplify_F(I : IntegerSet, S_r : BiDict, a, b):

        I_true, I_false = interval_F(S_r.get_I(Wahr()), S_r.get_I(Falsch()), (a,b))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        
        I = I.without(I_true.union(I_false))

        no_change_start_r = S_r.no_change_start()
        for t in I:
            outer_disjunctions = []
            F = S_r.get_F()
                                
            for phi in F:
                inner_disjunctions = []
                if b == None:
                    timestep_interval = (a+t, None)     # timestep_interval = [a+t,b+t]
                else:
                    timestep_interval = (a+t, b+t)
                                    
                partitions = IntegerSet.partition(S_r.get_I(phi).intersection(IntegerSet.from_interval(timestep_interval)))

                for ivl in partitions:      # ivl = [x,y]
                    new_ivl = ivl.copy()
                    new_ivl[0] -= t
                    if new_ivl[1] != None:
                        new_ivl[1] -= t         # new_ivl = [x-t, b-t]

                    inner_disjunctions.append(LTLf.eventually(phi,new_ivl))         # F_[x-t, b-t] phi

                if len(inner_disjunctions) == 0:
                    continue
                outer_disjunctions.append(LTLf.disjunction(inner_disjunctions))

            if len(outer_disjunctions) == 0:
                continue
            
            simp_exp = LTLf.disjunction(outer_disjunctions)

            if t >= no_change_start_r:                               # At this point simplified formulas do not change anymore
                rest = IntegerSet([t], True).intersection(I)
                S.add_exp_in(simp_exp, rest)    
                return S                        
            else:
                S.add_exp_at(simp_exp, t)
                            
        return S

    def simplify_X(I : IntegerSet, S_r : BiDict, a):
        I_true, I_false = interval_X(S_r.get_I(Wahr()), S_r.get_I(Falsch()), (a,None))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        
        I = I.without(I_true.union(I_false))
        
        no_change_start_r = S_r.no_change_start()
        for t in I:
            
            simp_exp = LTLf.next(S_r.get_at_timestep(t+a), a)

            if t >= no_change_start_r:                               # At this point simplified formulas do not change anymore
                rest = IntegerSet([t], True).intersection(I)
                S.add_exp_in(simp_exp, rest)    
                return S                        
            else:
                S.add_exp_at(simp_exp, t)
                            
        return S

    def simplify_O(I : IntegerSet, S_r : BiDict, a, b):
        raise ValueError("O is not implemented yet")

    def simplify_P(I : IntegerSet, S_r : BiDict, a):
        I_true, I_false = interval_P(S_r.get_I(Wahr()), S_r.get_I(Falsch()), (a,None))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        
        I = I.without(I_true.union(I_false))
        
        no_change_start_r = S_r.no_change_start() - a
        for t in I:
            if t - a >= 0:
                simp_exp = LTLf.previously(S_r.get_at_timestep(t-a), a)

                if t >= no_change_start_r:                               # At this point simplified formulas do not change anymore
                    rest = IntegerSet([t], True).intersection(I)
                    S.add_exp_in(simp_exp, rest)    
                    return S                        
                else:
                    S.add_exp_at(simp_exp, t)
        return S

    def simplify_AND(I : IntegerSet, S_l : BiDict, S_r : BiDict):
        I_true, I_false = interval_And(S_r.get_I(Wahr()), S_r.get_I(Falsch()), S_l.get_I(Wahr()), S_l.get_I(Falsch()))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        I = I.without(I_true.union(I_false))

        no_change_start_r = S_r.no_change_start()
        no_change_start_l = S_l.no_change_start()
        no_change_start = max(no_change_start_l, no_change_start_r)
        for t in I:
            exp_l = S_l.get_at_timestep(t)
            exp_r = S_r.get_at_timestep(t)

            simp_exp = LTLf._and(exp_l, exp_r)
            if exp_l == Wahr():
                simp_exp = exp_r
            elif exp_r == Wahr():
                simp_exp = exp_l


            if t >= no_change_start:                               # At this point simplified formulas do not change anymore
                rest = IntegerSet([t], True).intersection(I)
                S.add_exp_in(simp_exp, rest)    
                break                  
            else:
                S.add_exp_at(simp_exp, t)
                        
        return S

    def simplify_OR(I : IntegerSet, S_l : BiDict, S_r : BiDict):
        I_true, I_false = interval_Or(S_r.get_I(Wahr()), S_r.get_I(Falsch()), S_l.get_I(Wahr()), S_l.get_I(Falsch()))
        S = BiDict()
        S.add_exp_in(Wahr(), I_true)
        S.add_exp_in(Falsch(), I_false)
        I = I.without(I_true.union(I_false))

        no_change_start_r = S_r.no_change_start()
        no_change_start_l = S_l.no_change_start()
        no_change_start = max(no_change_start_l, no_change_start_r)
        for t in I:
            exp_l = S_l.get_at_timestep(t)
            exp_r = S_r.get_at_timestep(t)

            simp_exp = LTLf._or(exp_l, exp_r)
            if exp_l == Falsch():
                simp_exp = exp_r
            elif exp_r == Falsch():
                simp_exp = exp_l


            if t >= no_change_start:                               # At this point simplified formulas do not change anymore
                rest = IntegerSet([t], True).intersection(I)
                S.add_exp_in(simp_exp, rest)    
                break                  
            else:
                S.add_exp_at(simp_exp, t)
                        
        return S

    def simplify_IMP(I : IntegerSet, S_l : BiDict, S_r : BiDict):
        S_not_l = LTLf.simplify_NOT(I, S_l)
        return LTLf.simplify_OR(I, S_not_l,S_r)

    def simplify_NOT(I : IntegerSet, S_r : BiDict):
        S = BiDict()
        for exp in S_r.expressions():
            interval = S_r.get_I(exp)
            if exp == Wahr():
                S.add_exp_in(Falsch(), interval)
            elif exp == Falsch():
                S.add_exp_in(Wahr(), interval)
            else:
                S.add_exp_in(UnaryExpression(LogicUnOp("not"), exp), interval)
        return S



    """ Formula Building: """

    @staticmethod
    def _and(exp1 : Expression, exp2 : Expression):
        return BinaryExpression(LogicBinOp("and"), exp1, exp2)

    @staticmethod
    def _or(exp1 : Expression, exp2 : Expression):
        return BinaryExpression(LogicBinOp('or'), exp1, exp2)

    @staticmethod
    def _not(exp : Expression):
        return UnaryExpression(LogicUnOp('not'), exp)

    @staticmethod
    def implies(exp1 : Expression, exp2 : Expression):
        return BinaryExpression(LogicBinOp('imp'), exp1, exp2)

    @staticmethod
    def iff(exp1 : Expression, exp2 : Expression):
        return BinaryExpression(LogicBinOp('iff'), exp1, exp2)

    @staticmethod
    def eventually(exp : Expression, I=None):
        if I == None:
            return UnaryExpression(TempUnOp('F', (0,None)), exp)
        else:
            if I[1] == "inf":
                I[1] = None
            return UnaryExpression(TempUnOp('F', I), exp)

    
    @staticmethod
    def always(exp : Expression, I=None):
        if I == None:
            return UnaryExpression(TempUnOp('G', (0,None)), exp)
        else:
            if I[1] == "inf":
                I[1] = None
            return UnaryExpression(TempUnOp('G', I), exp)

    
    @staticmethod
    def next(exp : Expression, a=None):
        if a == None:
            return UnaryExpression(TempUnOp('X', (1, None)), exp)
        else:
            return UnaryExpression(TempUnOp('X', (a, None)), exp)

    @staticmethod
    def previously(exp : Expression, a=None):
        if a == None:
            return UnaryExpression(TempUnOp('P', (1, None)), exp)
        else:
            return UnaryExpression(TempUnOp('P', (a,None)), exp)


    @staticmethod
    def once(exp : Expression, interval=None):
        return UnaryExpression(TempUnOp('O', interval), exp)

    @staticmethod
    def conjunction(expressions : List[Expression]):
        if len(expressions) == 1:
            return expressions[0]
        else:
            return MultiExpression(LogicMultiOp('conjunction'), expressions)
        
    @staticmethod
    def disjunction(expressions : List[Expression]):
        if len(expressions) == 1:
            return expressions[0]
        else:
            return MultiExpression(LogicMultiOp('disjunction'), expressions)

    @staticmethod
    def until(exp1 : Expression, exp2 : Expression, interval=None):
        return BinaryExpression(TempBinOp("U", interval), exp1, exp2)

    @staticmethod
    def const(name : str) -> Constant:
        return Constant(name)

    @staticmethod
    def pred(name : str, terms : List[Term]):
        return Predicate(name, terms)

    @staticmethod
    def var(name : str):
        return Variable(name)

    @staticmethod
    def ap(name : str):
        return AtomicProposition(name)
