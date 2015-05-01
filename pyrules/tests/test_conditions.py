from unittest import TestCase
from ..conditions import LogicEvaluator, C, boolExpr, ExpressionHandler
from ..conditions import ExpressionError


class SampleObj(object):
    a_dict = {'foo': 'bar'}
    a_num = 10
    a_string = 'foobar'


class ExpressionHandlerTestCase(TestCase):
    def test_evaluate(self):
        sample = SampleObj()
        sample.sub = SampleObj()
        sample.sub.a_num = 20
        e = ExpressionHandler()
        with self.assertRaises(ExpressionError):
            e.evaluate('sample', {}, True)
        # Test math
        self.assertTrue(
            e.evaluate('sample__a_num', {'sample': sample}, 10))
        self.assertFalse(
            e.evaluate('sample__a_num', {'sample': sample}, 9))
        self.assertTrue(
            e.evaluate('sample__a_num__gt', {'sample': sample}, 9))
        self.assertFalse(
            e.evaluate('sample__a_num__gt', {'sample': sample}, 10))
        self.assertTrue(
            e.evaluate('sample__a_num__gte', {'sample': sample}, 10))
        self.assertTrue(
            e.evaluate('sample__a_num__lte', {'sample': sample}, 10))
        self.assertTrue(
            e.evaluate('sample__a_num__lt', {'sample': sample}, 11))
        self.assertTrue(
            e.evaluate('sample__a_num__eq', {'sample': sample}, 10))
        self.assertFalse(
            e.evaluate('sample__a_num__eq', {'sample': sample}, 11))
        self.assertTrue(
            e.evaluate('sample__a_num__neq', {'sample': sample}, 11))
        self.assertFalse(
            e.evaluate('sample__a_num__neq', {'sample': sample}, 10))
        # Test string ops
        self.assertTrue(
            e.evaluate('sample__a_string__eq', {'sample': sample}, 'foobar'))
        self.assertTrue(
            e.evaluate('sample__a_string__contains', {'sample': sample}, 'ba'))
        self.assertFalse(
            e.evaluate('sample__a_string__contains', {'sample': sample}, 'ab'))
        self.assertFalse(
            e.evaluate('sample__a_string__contains', {'sample': sample}, 'BA'))
        self.assertTrue(
            e.evaluate('sample__a_string__icontains', {'sample': sample}, 'BA'))
        self.assertFalse(
            e.evaluate('sample__a_string__icontains', {'sample': sample}, 'xx'))
        # Dict access
        self.assertTrue(
            e.evaluate('sample__a_dict__foo', {'sample': sample}, 'bar'))
        self.assertTrue(
            e.evaluate(
                'sample__a_dict__foo__contains', {'sample': sample}, 'ba'))
        # Access nested objects
        self.assertTrue(
            e.evaluate('sample__sub__a_num', {'sample': sample}, 20))
        self.assertTrue(
            e.evaluate(
                'sample__sub__a_dict__foo__icontains', {'sample': sample}, 'a'))

    
class CTestCase(TestCase):
    def test_clone(self):
        c1 = C('foo', 'bar')
        c2 = c1.clone()
        self.assertNotEqual(hash(c1), hash(c2))
        self.assertEqual(c1, c2)
        self.assertEqual(c1._expr, c2._expr)

    def test_combine(self):
        c1 = C('foo', 'bar')
        h1 = hash(c1)
        c1.combine(C('x', True), C.OR)
        self.assertEqual(hash(c1), h1)
        self.assertEqual(
            c1._expr,
            (C.OR, ('foo', 'bar', False), ('x', True, False), False))

    def test_apply(self):
        self.assertEqual(C(foo=True).apply({'foo': True}), True)
        self.assertEqual(C(foo=True).apply({'foo': False}), False)
        self.assertEqual((~C(foo=True)).apply({'foo': True}), False)
        self.assertEqual((~C(foo=True)).apply({'foo': False}), True)
        self.assertEqual(
            (C(foo=True) & C(bar=True)).apply({'foo': True, 'bar': True}),
            True)
        self.assertEqual(
            (C(foo=True) & C(bar=True)).apply({'foo': False, 'bar': True}),
            False)
        self.assertEqual(
            (C(foo=True) & C(bar=True)).apply({'foo': True, 'bar': False}),
            False)
        self.assertEqual(
            (C(foo=True) & C(bar=True)).apply({'foo': False, 'bar': False}),
            False)
        for c1 in (True, False):
            for c2 in (True, False):
                for c3 in (True, False):
                    self.assertEqual(
                        (~C(c1=True) ^ (C(c2=True) | C(c3=True))).apply(
                            {'c1': c1, 'c2': c2, 'c3': c3}),
                        (not c1) ^ (c2 | c3))

    def test_negation(self):
        self.assertNotEqual(~C('foo', 'bar'), C('foo', 'bar'))
        self.assertEqual(~(~C('foo', 'bar')), C('foo', 'bar'))
        
    def test_simple_cond(self):
        self.assertEqual(C('foo', 'bar')._expr, ('foo', 'bar', False))
        self.assertEqual(C(foo=True)._expr, ('foo', True, False))
        self.assertEqual(C(foo=False)._expr, ('foo', False, False))

    def test_simple_cond_negate(self):
        self.assertEqual(C('foo', 'bar', True)._expr, ('foo', 'bar', True))
        self.assertEqual((~C(foo=True))._expr, ('foo', True, True))

    def test_cond_ops(self):
        self.assertEqual(
            (C(foo=True) & C(bar=False))._expr,
            (C.AND, ('foo', True, False), ('bar', False, False), False))
        self.assertEqual(
            (C(foo=True) | C(bar=False))._expr,
            (C.OR, ('foo', True, False), ('bar', False, False), False))
        self.assertEqual(
            (C(foo=True) ^ C(bar=False))._expr,
            (C.XOR, ('foo', True, False), ('bar', False, False), False))

    def test_cond_ops_negate(self):
        self.assertEqual(
            (~C(foo=True) & C(bar=False))._expr,
            (C.AND, ('foo', True, True), ('bar', False, False), False))
        self.assertEqual(
            (~(C(foo=True) & C(bar=False)))._expr,
            (C.AND, ('foo', True, False), ('bar', False, False), True))

    def test_multi_cond(self):
        self.assertEqual(
            C(foo__gt=4, foo__ne=10)._expr,
            (C.AND, ('foo__gt', 4, False), ('foo__ne', 10, False), False))

    def test_repr(self):
        self.assertEqual(repr(C(foo='bar')), '<C: foo == bar>')
        self.assertEqual(repr(~C(foo='bar')), '<C: foo != bar>')
        self.assertEqual(
            repr(C(foo='bar') & C(x=100)),
            '<C: (foo == bar AND x == 100)>')
        self.assertEqual(
            repr(C(foo='bar') | C(x=100)),
            '<C: (foo == bar OR x == 100)>')
        self.assertEqual(
            repr(C(foo='bar') ^ C(x=100)),
            '<C: (foo == bar XOR x == 100)>')
        self.assertEqual(
            repr(~C(foo='bar') & C(x=100)),
            '<C: (foo != bar AND x == 100)>')
        self.assertEqual(
            repr(~(C(foo='bar') & C(x=100))),
            '<C: NOT(foo == bar AND x == 100)>')
        self.assertEqual(
            repr(C(foo__gt=4, foo__ne=10)),
            '<C: (foo__gt == 4 AND foo__ne == 10)>')


class LogicEvaluatorTestCase(TestCase):
    def test_parse_tree(self):
        self.assertEqual(boolExpr.parseString('1').asList(), ['1'])
        self.assertEqual(
            boolExpr.parseString('~1').asList(), [['~', '1']])
        self.assertEqual(boolExpr.parseString('(1)').asList(), ['1'])
        self.assertEqual(
            boolExpr.parseString('1 ^ 2').asList(),
            [['1', '^', '2']])
        self.assertEqual(
            boolExpr.parseString('1 & 2 & 3').asList(),
            [[['1', '&', '2'], '&', '3']])
        self.assertEqual(
            boolExpr.parseString('1 & (2)').asList(),
            [['1', '&', '2']])
        self.assertEqual(
            boolExpr.parseString('~1 & 2').asList(),
            [[['~', '1'], '&', '2']])
        self.assertEqual(
            boolExpr.parseString('1 & (2 | 3)').asList(),
            [['1', '&', ['2', '|', '3']]])
        self.assertEqual(
            boolExpr.parseString('~(1)').asList(), [['~', '1']])
        self.assertEqual(
            boolExpr.parseString('(~1)').asList(), [['~', '1']])
        self.assertEqual(
            boolExpr.parseString('1 & ~(2 | 3)').asList(),
            [['1', '&', ['~', ['2', '|', '3']]]])

    def test_to_c_expressions(self):
        self.assertEqual(LogicEvaluator.to_c_expression('1'), C(cond1=True))
        self.assertEqual(
            LogicEvaluator.to_c_expression(['~', '1']), ~C(cond1=True))
        self.assertEqual(
            LogicEvaluator.to_c_expression(['1', '^', '2']),
            C(cond1=True) ^ C(cond2=True))
        self.assertEqual(
            LogicEvaluator.to_c_expression(['1', '&', ['~', '2']]),
            C(cond1=True) & ~C(cond2=True))
        self.assertEqual(
            LogicEvaluator.to_c_expression(['1', '&', ['~', ['2', '|', '3']]]),
            C(cond1=True) & ~(C(cond2=True) | C(cond3=True)))
        
    def test_logic_parsing(self):
        self.assertEqual(LogicEvaluator('1', ['foo']).logic, C(cond1=True))
        self.assertEqual(
            LogicEvaluator('1 | 2', ['foo', 'bar']).logic,
            C(cond1=True) | C(cond2=True))
        self.assertEqual(LogicEvaluator('~1', ['foo']).logic, ~C(cond1=True))
        self.assertEqual(
            LogicEvaluator('~(1 ^ 2)', ['foo', 'bar']).logic,
            ~(C(cond1=True) ^ C(cond2=True)))
        self.assertEqual(
            LogicEvaluator('~(~1 | 2)', ['foo', 'bar']).logic,
            ~(~C(cond1=True) | C(cond2=True)))

    def test_evalutaion(self):
        e = LogicEvaluator('1', [{'foo': True}])
        self.assertEqual(e.evaluate({'foo': True}), True)
        self.assertEqual(e.evaluate({'foo': False}), False)
        e = LogicEvaluator('~1', ['foo'])
        self.assertEqual(e.evaluate({'foo': True}), False)
        self.assertEqual(e.evaluate({'foo': False}), True)
        e = LogicEvaluator('1 & 2', ['foo', 'bar'])
        self.assertEqual(
            e.evaluate({'foo': True, 'bar': True}), True)
        self.assertEqual(
            e.evaluate({'foo': True, 'bar': False}), False)
        self.assertEqual(
            e.evaluate({'foo': False, 'bar': False}), False)
        self.assertEqual(
            e.evaluate({'foo': False, 'bar': False}), False)


'''
class ConditionsTestCase(TestCase):
    def test_and(self):
        data = [
            (['True', 'True'], True),
            (['True', 'False'], False),
            (['False', 'True'], False),
            (['False', 'False'], False)]
        e = LogicEvaluator('1 & 2')
        for condition, result in data:
            self.assertEqual(e.evaluate(condition, RuleContext()), result)
'''        