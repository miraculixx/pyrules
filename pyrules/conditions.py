import operator
from pyparsing import Forward, Word, Literal, Suppress, Optional, Group, nums
from pyparsing import infixNotation, opAssoc, ParseResults


class C(object):
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'
    default = AND
    OPS_MAP = {AND: operator.and_, OR: operator.or_, XOR: operator.xor}

    def __init__(self, _key=None, _value=None, _negate=False, **kwargs):
        if _key:
            self._expr = (_key, _value, _negate)
        else:
            self._expr = ()
        for k, v in kwargs.iteritems():
            self._expr = self.combine(C(k, v))._expr

    def clone(self):
        """
        Create a new C-expression that is a copy of this one.
        """
        new = self.__class__()
        new._expr = self._expr
        return new
            
    def combine(self, other, op=default):
        """
        Combine another C-expression with this using a logical operator.
        """
        assert(isinstance(other, C))
        self._expr = (
            op, self._expr, other._expr, False) if self._expr else other._expr
        return self

    def apply(self, context):
        """
        Apply evaluation context to this C-expression. Context should be a dict
        or dict-like object.
        """
        return self._apply_expr(context, self._expr)

    def _apply_expr(self, context, expr):
        if isinstance(expr[1], tuple):
            return self.OPS_MAP[expr[0]](
                self._apply_expr(context, expr[1]),
                self._apply_expr(context, expr[2]))
        else:
            # expr[2] holds negation flag, that's why we xor with it.
            return ExpressionHandler().evaluate(
                expr[0], context, expr[1]) ^ expr[2]

    def __repr__(self):
        return '<C: {}>'.format(self._to_str(self._expr)).encode('utf-8')

    def _to_str(self, val):
        if not val:
            return u'N/A'
        elif isinstance(val[1], tuple):
            return u'{}({} {} {})'.format(
                'NOT' if val[-1] else '', self._to_str(val[1]), val[0],
                self._to_str(val[2]))
        else:
            return u'{} {}= {}'.format(
                val[0], '!' if val[-1] else '=', val[1])            

    def __and__(self, other):
        return self.clone().combine(other, self.AND)

    def __or__(self, other):
        return self.clone().combine(other, self.OR)

    def __xor__(self, other):
        return self.clone().combine(other, self.XOR)

    def __invert__(self):
        new = self.clone()
        new._expr = tuple(self._expr[:-1]) + (not self._expr[-1],)
        return new

    def __eq__(self, other):
        if not issubclass(other.__class__, C):
            return False
        return self._expr == other._expr


class ExpressionError(Exception):
    pass

        
class ExpressionHandler(object):
    handlers = [
        'gt', 'lt', 'gte', 'lte', 'eq', 'neq', 'contains', 'icontains', 'bool']

    def evaluate(self, expression, context, arg):
        bits = expression.split('__')
        last = len(bits) - 2
        bit = bits[0]
        try:
            cur = context[bit]
        except KeyError:
            raise ExpressionError(
                'Can\'t resolve "{}" bit in expression: "{}"'.format(
                    bit, expression))
        for i, bit in enumerate(bits[1:]):
            try:
                cur = getattr(cur, bit)
                continue
            except AttributeError:
                try:
                    cur = cur[bit]
                    continue
                except (TypeError, KeyError):
                    if i == last and bit in self.handlers:
                        return getattr(self, 'handle_' + bit)(cur, arg)
                    raise ExpressionError(
                        'Can\'t resolve "{}" bit in expression: "{}"'.format(
                            bit, expression))
        else:
            return cur == arg
            
    handle_gt = operator.gt
    handle_lt = operator.lt
    handle_gte = operator.ge
    handle_lte = operator.le
    handle_eq = operator.eq
    handle_neq = operator.ne
    handle_contains = lambda self, val, arg: arg in val
    handle_icontains = lambda self, val, arg: arg.lower() in val.lower()
    handle_bool = lambda self, val, arg: bool(val) == arg

            
#
# BNF grammar for parser:
#
# number    :: '1' .. '9'
# negated   :: '~' condition
# sub_cond  :: '(' condition ')'
# op        :: '&' | '|' | '^'
# op_cond   :: condition op condition
# condition :: number | negated | op_cond | sub_cond

# Trying to convert BNF directly to pyparsing code doesn't work very well -
# I ended up running into infinite recursion. However, it has good support
# for math/logic ops parsing with infixNotation helper.        

    
# parse action maker
def makeLRlike(numterms=None):
    """
    Pyparsing outputs flat lists of token. This helper function converts them
    to LR-like structures (basically, nested lists) that we can process later.

    Borrowed from http://stackoverflow.com/a/4589920
    """
    if numterms is None:
        # None operator can only by binary op
        initlen = 2
        incr = 1
    else:
        initlen = {0:1,1:2,2:3,3:5}[numterms]
        incr = {0:1,1:1,2:2,3:4}[numterms]

    # define parse action for this number of terms,
    # to convert flat list of tokens into nested list
    def pa(s,l,t):
        t = t[0]
        if len(t) > initlen:
            ret = ParseResults(t[:initlen])
            i = initlen
            while i < len(t):
                ret = ParseResults([ret] + t[i:i+incr])
                i += incr
            return ParseResults([ret])
    return pa

boolOperand = Word(nums)

# define expression, based on expression operand and
# list of operations in precedence order
boolExpr = infixNotation(
    boolOperand,
    [
        ("~", 1, opAssoc.RIGHT, makeLRlike()),
        ("&", 2, opAssoc.LEFT, makeLRlike(2)),
        ("|",  2, opAssoc.LEFT, makeLRlike(2)),
        ("^",  2, opAssoc.LEFT, makeLRlike(2))
    ])


class LogicEvaluator(object):
    LOGIC_OPS = {'&': operator.and_, '|': operator.or_, '^': operator.xor}
    _force_conditions = None
    
    def __init__(self, logic, conditions):
        self.logic = self.parse_logic(
            logic or
            ' & '.join(
                map(str, xrange(1, len(conditions) + 1))))
        if isinstance(conditions[0], bool):
            self._force_conditions = conditions[0]
        else :
            self.logic_context = dict(
                ('cond' + str(i + 1),
                 (C(**condition) if isinstance(condition, dict) else
                  C(**{condition: True})))
                for i, condition in enumerate(conditions))

    def parse_logic(self, logic):
        tree = boolExpr.parseString(logic)[0]
        return LogicEvaluator.to_c_expression(tree)

    @classmethod
    def to_c_expression(cls, tree):
        if isinstance(tree, basestring):
            return C('cond' + tree, True)
        elif tree[0] == '~':
            return ~LogicEvaluator.to_c_expression(tree[1])
        elif tree[1] in cls.LOGIC_OPS:
            return cls.LOGIC_OPS[tree[1]](
                cls.to_c_expression(tree[0]), cls.to_c_expression(tree[2]))

    def evaluate(self, context):
        """
        Evaluate logic conditions for given context
        """
        if self._force_conditions is not None:
            return self._force_conditions

        # First, we evaluate logic context conditions in given context. This
        # gives us the logic context.
        logic_context = dict(
            (key, value.apply(context))
            for key, value in self.logic_context.iteritems())
        # Next, we evaluate logic conditions in this logic context.
        return self.logic.apply(logic_context)
