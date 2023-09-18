# -*- coding: utf-8 -*-
"""
toylang value define
"""
from toytoken import *

class Value:
    def __str__(self):
        pass

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self})'

    def type(self):
        return f'{self.__class__.__name__[:-5]}'


class NullValue(Value):
    def __str__(self):
        return 'null'


class BoolValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return 'true' if self._val else 'false'


class NumValue(Value):
    def __init__(self, _val, is_int):
        self._val = _val
        self.is_int = is_int

    def __str__(self):
        return str(self._val)

    def type(self):
        return 'Int' if self.is_int else 'Float'

class StringValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return self._val


class ListValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return '[' + ', '.join(f'v' for v in self._val) + ']'


class MapValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return '{' + ', '.join(f'{k}: {v}' for k, v in self._val.items()) + '}'


class ObjectValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return '<object>'


class TypeValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return self._val


def builtin_typevalues_init(table):
    table['null'] = TypeValue('null')
    table['bool'] = TypeValue('bool')
    table['int'] = TypeValue('int')
    table['float'] = TypeValue('float')
    table['string'] = TypeValue('string')
    table['list'] = TypeValue('list')
    table['map'] = TypeValue('map')
    table['function'] = TypeValue('function')
    table['object'] = TypeValue('object')
    # table['type'] = TypeValue('type')
    # table['variable'] = TypeValue('variable')


class OpImpl:
    @staticmethod
    def eq(l, r):
        return BoolValue(l._val == r._val)

    @staticmethod
    def lt(l, r):
        if type(l) == NumValue and type(r) == NumValue:
            return BoolValue(l._val < r._val)
        else:
            raise TypeError

    @staticmethod
    def le(l, r):
        if type(l) == NumValue and type(r) == NumValue:
            return BoolValue(l._val <= r._val)
        else:
            raise TypeError

    @staticmethod
    def add(l, r):
        if type(l) == NumValue and type(r) == NumValue:
            return NumValue(l._val + r._val, is_int=True if l.is_int and r.is_int else False)
        elif type(l) == StringValue and type(r) in (StringValue, NumValue):
            return StringValue(l._val + str(r._val))
        else:
            raise TypeError

    @staticmethod
    def sub(l, r):
        if type(l) == NumValue and type(r) == NumValue:
            return NumValue(l._val - r._val, is_int=True if l.is_int and r.is_int else False)
        else:
            raise TypeError

    @staticmethod
    def mul(l, r):
        if type(l) == NumValue and type(r) == NumValue:
            return NumValue(l._val * r._val, is_int=True if l.is_int and r.is_int else False)
        else:
            raise TypeError

    @staticmethod
    def div(l, r):
        if type(l) == NumValue and type(r) == NumValue:
            if l.is_int and r.is_int:
                return NumValue(l._val // r._val, is_int=True)
            else:
                return NumValue(l._val / r._val, is_int=False)
        else:
            raise TypeError

    # @staticmethod
    # def pow_

    # @staticmethod
    # def mod

    # @staticmethod
    # def bshl

    # @staticmethod
    # def bshr

    # @staticmethod
    # def band

    # @staticmethod
    # def bxor

    # @staticmethod
    # def bor

    # @staticmethod
    # def and_

    # @staticmethod
    # def or_

    # @staticmethod
    # def is_

    # @staticmethod
    # def in_

    # @staticmethod
    def add_(v):
        if type(v) == NumValue:
            return v
        else:
            raise TypeError

    # @staticmethod
    def sub_(v):
        if type(v) == NumValue:
            return NumValue(-v._val, is_int=v.is_int)
        else:
            raise TypeError

    @staticmethod
    def not_(v):
        bvalue = OpImpl.value_to_bool(v)
        return BoolValue(not bvalue._val)

    # @staticmethod
    # def len_

    # @staticmethod
    # def bnot

    @staticmethod
    def value_to_bool(val):
        '''convert other value to bool
        '''
        if type(val) == NullValue:
            return BoolValue(False)
        elif type(val) == BoolValue:
            return val
        elif type(val) == NumValue:
            return BoolValue(val._val != 0)
        elif type(val) in (StringValue, ListValue, MapValue):
            return BoolValue(len(val._val) != 0)
        else:
            return BoolValue(True)


BINOP_IMPL_TABLE = {
    TokenType.EQ        : OpImpl.eq,        # TokenType.NE
    TokenType.LT        : OpImpl.lt,        # TokenType.GE
    TokenType.LE        : OpImpl.le,        # TokenType.GT
    TokenType.ADD       : OpImpl.add,
    TokenType.SUB       : OpImpl.sub,
    TokenType.MUL       : OpImpl.mul,
    TokenType.DIV       : OpImpl.div,
    # TokenType.POW       :
    # TokenType.MOD       :
    # TokenType.BSHL      :
    # TokenType.BSHR      :
    # TokenType.BAND      :
    # TokenType.BXOR      :
    # TokenType.BOR       :
    TokenType.SELF_ADD  : OpImpl.add,       # self_add is implemented by add
    TokenType.SELF_SUB  : OpImpl.sub,
    # TokenType.SELF_MUL  :
    # TokenType.SELF_DIV  :
    # TokenType.SELF_POW  :
    # TokenType.SELF_MOD  :
    # TokenType.SELF_BSHL :
    # TokenType.SELF_BSHR :
    # TokenType.SELF_BAND :
    # TokenType.SELF_BXOR :
    # TokenType.SELF_BOR  :
    # TokenType.AND       :
    # TokenType.OR        :
    # TokenType.IS        :
    # TokenType.IN        :
}

UNIOP_IMPL_TABLE = {
    TokenType.ADD       : OpImpl.add_,
    TokenType.SUB       : OpImpl.sub_,
    TokenType.NOT       : OpImpl.not_,
    # TokenType.LEN       :
    # TokenType.BNOT      :
}
