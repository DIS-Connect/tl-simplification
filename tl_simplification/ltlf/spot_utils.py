from tl_simplification.expression.ltl_data_classes import *
from tl_simplification.ltlf.LTLf import LTLf
import spot

@typechecked
def to_spot_syntax(exp : Expression):
        """
        Currently this function removes the U [x,y] oparator
        """
        match exp:
            case BinaryExpression(TempBinOp("U", (a,b)), exp_l, exp_r):
                exp_l = to_spot_syntax(exp_l)
                exp_r = to_spot_syntax(exp_r)
                
                if a == 0 and b == None:
                    return BinaryExpression(TempBinOp("U", (a,b)), exp_l, exp_r)
                
                elif b == None:
                    return LTLf._and(
                        LTLf.always(exp_l, (0,a-1)),
                        LTLf.next(
                            LTLf.until(exp_l, exp_r),
                            a
                        )
                    )
                
                else:
                    disj_exps = []

                    for k in range(a, b+1):
                        if k > 0:
                            disj_exps.append(
                                LTLf._and(
                                    LTLf.always(exp_l, (0,k-1)),
                                    LTLf.next(exp_r,k)
                                    )
                                )
                        else:
                            disj_exps.append(
                                    LTLf.next(exp_r,k)
                                )
                
                    return LTLf.disjunction(disj_exps)
            
            case BinaryExpression(op, exp_l, exp_r):
                exp_l = to_spot_syntax(exp_l)
                exp_r = to_spot_syntax(exp_r)
                return BinaryExpression(op, exp_l, exp_r)
            case UnaryExpression(op, exp_r):
                exp_r = to_spot_syntax(exp_r)
                return UnaryExpression(op, exp_r)
            case MultiExpression(op, expressions):
                new_expressions = [to_spot_syntax(exp) for exp in expressions]
                return MultiExpression(op, new_expressions)

            case other:
                return other

def to_finite_syntax_rec(exp : Expression):
        match exp:
            case BinaryExpression(TempBinOp("U", (a,b)), exp_l, exp_r):
                exp_l = to_finite_syntax_rec(exp_l)
                exp_r = to_finite_syntax_rec(exp_r)

                exp_l = LTLf._and(LTLf.ap("alive"), exp_l)
                exp_r = LTLf._and(LTLf.ap("alive"), exp_r)
                return BinaryExpression(TempBinOp("U", (a,b)), exp_l, exp_r)

            case UnaryExpression(TempUnOp("G", (a,b)), exp_r):
                exp_r = to_finite_syntax_rec(exp_r)
                exp_r = LTLf._or(LTLf._not(LTLf.ap("alive")), exp_r)
                return UnaryExpression(TempUnOp("G", (a,b)), exp_r)
            

            case UnaryExpression(TempUnOp("F", (a,b)), exp_r):
                exp_r = to_finite_syntax_rec(exp_r)
                exp_r = LTLf._and(LTLf.ap("alive"), exp_r)
                return UnaryExpression(TempUnOp("F", (a,b)), exp_r)

            case UnaryExpression(TempUnOp("X", (a,b)), exp_r):
                exp_r = to_finite_syntax_rec(exp_r)
                exp_r = LTLf._and(LTLf.ap("alive"), exp_r)
                return UnaryExpression(TempUnOp("X", (a,b)), exp_r)

            
            case BinaryExpression(op_type, exp_l, exp_r):
                exp_l = to_finite_syntax_rec(exp_l)
                exp_r = to_finite_syntax_rec(exp_r)
                return BinaryExpression(op_type, exp_l, exp_r)

            case UnaryExpression(op_type, exp_r):
                exp_r = to_finite_syntax_rec(exp_r)
                return UnaryExpression(op_type, exp_r)

            case MultiExpression(op_type, expressions):
                new_expressions = [to_finite_syntax_rec(exp) for exp in expressions]
                return MultiExpression(op_type, new_expressions)

            case other:
                return other

def to_finite_syntax(exp : Expression):
    return LTLf.conjunction([
        LTLf.ap("alive"),
        LTLf.until(LTLf.ap("alive"), LTLf.always(LTLf._not(LTLf.ap("alive")))),
        to_finite_syntax_rec(exp)
    ])

@typechecked
def to_buechi(exp : Expression):

        # Convert to spot syntax
        exp = to_spot_syntax(exp)

        # Convert for finite automata translation
        exp = to_finite_syntax(exp)

        #exp_spot = LTLf.translate_for_spot(exp)
        f = spot.formula(str(exp))

        aut = f.translate(xargs='simul=0')
        
        finite_aut = spot.to_finite(aut)

        return finite_aut
