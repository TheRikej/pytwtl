from abc import ABC, abstractmethod

class TransitionRule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def is_fullfilled(self, props: set[str]) -> bool:
        pass
    
    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def get_str_repr(self):
        pass

    
    def __str__(self):
        return self.evaluate().get_str_repr()
    



class AtomicPropositionRule(TransitionRule):
    def __init__(self, proposition: str):
        super().__init__()
        self.proposition = proposition

    def is_fullfilled(self, props: set[str]) -> bool:
        return self.proposition in props
    

    def evaluate(self) -> 'AtomicPropositionRule':
        return self


    def get_str_repr(self):
        return self.proposition
    



class NegationRule(TransitionRule):
    def __init__(self, rule: TransitionRule):
        super().__init__()
        self.__rule = rule

    def is_fullfilled(self, props: set[str]) -> bool:
        return not self.__rule.is_fullfilled(props)
    
    def evaluate(self) -> 'NegationRule':
        evaluated_rule = self.__rule.evaluate()
        if isinstance(evaluated_rule, NegationRule):
            return evaluated_rule.__rule
        # elif isinstance(self.__rule, OrRule):
        #     return AndRule(NegationRule(self.__rule.left).evaluate(), NegationRule(self.__rule.right).evaluate())
        # elif isinstance(self.__rule, AndRule):
        #     return OrRule(NegationRule(self.__rule.left).evaluate(), NegationRule(self.__rule.right).evaluate())
        elif isinstance(evaluated_rule, TrueRule):
            return FalseRule()
        elif isinstance(evaluated_rule, FalseRule):
            return TrueRule()
        else:
            return NegationRule(evaluated_rule)
    
    def get_str_repr(self):
        return '!' + str(self.__rule)


class TrueRule(TransitionRule):
    def __init__(self):
        super().__init__()

    def is_fullfilled(self, props: set[str]) -> bool:
        return True
    
    def evaluate(self) -> 'TrueRule':
        return self
    
    def get_str_repr(self):
        return 'True'
    

class FalseRule(TransitionRule):
    def __init__(self):
        super().__init__()

    def is_fullfilled(self, props: set[str]) -> bool:
        return False
    
    def evaluate(self) -> 'FalseRule':
        return self
    
    def get_str_repr(self):
        return 'False'


class OrRule(TransitionRule):
    def __init__(self, left: TransitionRule, right: TransitionRule):
        super().__init__()
        self.left = left
        self.right = right

    def evaluate(self) -> 'OrRule':
        evaluated_left = self.left.evaluate()
        evaluated_right = self.right.evaluate()

        if isinstance(evaluated_left, TrueRule) or isinstance(evaluated_right, TrueRule):
            return TrueRule()
        elif isinstance(evaluated_left, FalseRule):
            return evaluated_right
        elif isinstance(evaluated_right, FalseRule):
            return evaluated_left
        else:
            return OrRule(evaluated_left, evaluated_right)

    def is_fullfilled(self, props: set[str]) -> bool:
        return self.left.is_fullfilled(props) or self.right.is_fullfilled(props)

    def get_str_repr(self):
        return '(' + str(self.left) + ' OR ' + str(self.right) + ')'


class AndRule(TransitionRule):
    def __init__(self, left: TransitionRule, right: TransitionRule):
        super().__init__()
        self.left = left
        self.right = right

    def evaluate(self) -> 'TransitionRule':
        evaluated_left = self.left.evaluate()
        evaluated_right = self.right.evaluate()

        if isinstance(evaluated_left, FalseRule) or isinstance(evaluated_right, FalseRule):
            return FalseRule()
        elif isinstance(evaluated_left, TrueRule):
            return evaluated_right
        elif isinstance(evaluated_right, TrueRule):
            return evaluated_left
        else:
            return AndRule(evaluated_left, evaluated_right)

    def is_fullfilled(self, props: set[str]) -> bool:
        return self.left.is_fullfilled(props) and self.right.is_fullfilled(props)
    
    def get_str_repr(self):
        return '(' + str(self.left) + ' AND ' + str(self.right) + ')'
    
class EmptyRule(TransitionRule):
    def __init__(self):
        super().__init__()

    def evaluate(self) -> 'TransitionRule':
        return self

    def is_fullfilled(self, props: set[str]) -> bool:
        return not props
    
    def get_str_repr(self):
        return 'Empty'

class ElseRule(TransitionRule):
    def __init__(self):
        super().__init__()
    
    def evaluate(self) -> 'ElseRule':
        return self

    def is_fullfilled(self, props: set[str]) -> bool:
        return True

    def get_str_repr(self):
        return 'Else'