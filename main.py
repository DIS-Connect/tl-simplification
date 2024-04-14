from typing import Tuple
from tl_simplification.inference.int_set import IntegerSet
from tl_simplification.inference.predicate import PredicateChecker
from tl_simplification.ltlf.LTLf import LTLf
from tl_simplification.expression.ltl_data_classes import *
from tl_simplification.ltlf.spot_utils import *

# from commonroad_reach_semantic.data_structure.model_checking.finite_automaton import FiniteAutomaton d
#exp = LTLf.until(LTLf.pred("A", []), LTLf.pred("B", []), (5,8))





class TestInterval(PredicateChecker):

    def __init__(self):
        super().__init__()
        self.add_predicate("A", TestInterval.interval_v1, 0)
        self.add_predicate("B", TestInterval.interval_v2, 0)

    def interval_v1(input) -> Tuple[IntegerSet, IntegerSet]:
        
        I_true = IntegerSet.from_interval([0,10])
        I_false = IntegerSet.empty()

        return I_true, I_false

    def interval_v2(input) -> Tuple[IntegerSet, IntegerSet]:
        I_true = IntegerSet.from_interval([5,15])
        I_false = IntegerSet.empty()
        return I_true, I_false


#exp = LTLf.always(LTLf._and(LTLf.eventually(LTLf.pred("A", []), (5,10)), LTLf.pred("B", [])))
#exp = LTLf.eventually(LTLf._or(LTLf.pred("A", []), LTLf.pred("B", [])))
#exp = LTLf.next(LTLf.previously(LTLf.pred("A", []), 30), 30)
#exp = LTLf.always(LTLf.eventually(LTLf._and(LTLf.pred("A", []), LTLf.pred("B", []))))

#exp = LTLf.implies(LTLf._not(LTLf.pred("A", [])), LTLf.pred("B", []))
exp = LTLf.always(LTLf.implies(
    LTLf.ap("a"),
    LTLf.next(LTLf._or(
        LTLf.ap("b"),
        LTLf.ap("c")
    ))
    ))

print(exp)

test_interval = TestInterval()

I = IntegerSet([0], False)

S = LTLf.interval_simplification(exp, I, test_interval)
print(S.get_at_timestep(0))