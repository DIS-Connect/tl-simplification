from typing import List, Callable
from typeguard import typechecked
from typing import List, Tuple
from tl_simplification.expression.ltl_data_classes import Constant
from tl_simplification.inference.int_set import IntegerSet


class PredicateChecker():

    def __init__(self):
        self.cache = {}

        """
        It is important to keep the structure of the cache

        cache = {
            example_predicate1 = {
                eval: func (list[str]) -> IntegerSet,IntegerSet
                check: IntegerSet,IntegerSet                   // Checks if predicate is always true/false for any input
                input_len: int
                V8: {
                    check: true, false
                    }
            }

            example_predicate2 = {
                eval: func (List[Constant]) -> IntegerSet,IntegerSet
                check:IntegerSet,IntegerSet                   // Checks if predicate is always true/false for any input
                V8: {
                    V12: {
                        check: true, false
                        }
                    }
            }
        }
        """
    
    @typechecked
    def check_predicate(self, pred_name:str, input : List[Constant]) -> Tuple[IntegerSet, IntegerSet]:
        """
        This function checks the predicate with given input. The input can only be constants
        For example: 
        pred_name: OnAccessRamp, input: [Constant("V8")] -> would be accepted
        pred_name: OnAccessRamp, input: [Variable("X_{other}")] -> would NOT be accepted
        """
        if not pred_name in self.cache:
            return IntegerSet.empty(), IntegerSet.empty()
        
        pred_cache = self.cache[pred_name]

        if len(input) == 0:
            if "check" in pred_cache:
                return pred_cache["check"]
            else:
                pred_cache["check"] = pred_cache["eval"]([])
                return pred_cache["check"]
        
        assert pred_cache["input_len"] == len(input)

        if "check" in pred_cache:
            I_true, I_false = pred_cache["check"]
            if I_true.is_N0() or I_false.is_N0():
                return I_true, I_false
        
        # At this point "check" does not exist or all values or it could hold more information

        constants = [const.name for const in input]

        # check if predicate has been evaluated for the same constants before
        temp = pred_cache
        in_cache = True
        for const in constants:
            if const in temp:
                temp = temp[const]
            else:
                in_cache = False
                break
        
        
        if in_cache:
            return temp["check"]
        
        I_true, I_false = pred_cache["eval"](constants)

        
        for const in constants:
            if not const in pred_cache:
                pred_cache[const] = {}
            pred_cache = pred_cache[const]
        
        pred_cache["check"] = (I_true, I_false)
        return I_true, I_false

    @typechecked
    def add_predicate(self, pred_name, eval_func : Callable[[List[str]], Tuple[IntegerSet, IntegerSet]], input_len):
        self.cache[pred_name] = {
            "input_len": input_len,
            "eval": eval_func
        }

