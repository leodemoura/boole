# -*- coding: utf-8 -*-

###############################################################################
#
# terms.py
#
# description: an info type describing how to build terms and types at the
# top level.
#
#
# Authors:
# Cody Roux
# Jeremy Avigad
#
###############################################################################

from boole.core.info import *
from boole.core.context import *
from boole.core.expr import Const, Sub, Pair, Fst, Snd, Box, root_app, \
  root_clause, root_pi
from color import *
import boole.core.expr as e
import boole.core.typing as typing
import elab
from elab import app_expr, mvar_infer, open_expr, sub_mvar, subst_expr
import boole.core.tactics as tac
import unif as u
from boole.semantics.value import Value


###############################################################################
#
# Exceptions associated with expressions
#
###############################################################################

class TermError(Exception):
    """Errors for expressions
    """
    def __init__(self, mess):
        Exception.__init__(self, mess)


###############################################################################
#
# String methods for terms
#
###############################################################################

def print_const(expr):
    """Pretty prints constants: if there is a unicode name
    in the info field, return that, otherwise return the ascii name.
    """
    if expr.info.unicode is None:
        return expr.name
    else:
        return expr.info.unicode

# TODO: wouldn't it be clearer to inline most of these in the definitions
# of term_str and typ_str?

# TODO: print_app uses info fields 'print_iterable' and 'print_implies' to
# determine if special print methods are needed for application.
# Is that o.k.?

# TODO: right now the str method uses the name of the constant to print out
# a value. Should the value class instead determine how values are printed out?


def print_app(expr):
    """Takes an application and prints it in the following manner:
    if the application is of the form (..(f a0)... an), print
    f(a0,...,an), or (a0 f a1) if f is infix.
    
    Arguments:
    - `expr`: an expression
    """
    root, args = dest_app_implicit(expr)
    if root.is_const() and root.info.print_iterable_app:
        return print_iterable_app(expr, root)
    elif root.is_const() and root.info.print_implies:
        return print_implies(expr)
    elif root.info.infix and len(args) == 2:
        return "({0!s} {1!s} {2!s})".format(args[0], root, args[1])
    else:
        args_str = map(str, args)
        args_str = ", ".join(args_str)
        return "{0!s}({1!s})".format(root, args_str)


def print_iterable_app(expr, op):
    """Prints an expression of the form
    op(... op(op(e1, e2), e3) ..., en) as 'op(e1, ..., en)', or, if op
    is infix, as 'e1 op e2 op ... op en'
    """
    args = dest_binop_left(expr, op)
    args_str = map(str, args)
    if op.info.infix:
        return '(' + (' ' + str(op) + ' ').join(args_str) + ')'
    else:
        return "{0!s}({1!s})".format(op, ', '.join(args_str))


def print_implies(expr):
    """Prints an implication implies([h1, ..., hn], conc)
    """
    hyps, conc = dest_implies(expr)
    if len(hyps) == 1:
        return "{0!s}({1!s}, {2!s})".format(implies, hyps[0], conc)
    else:
        hyp_str = ", ".join(map(str, hyps))
        return "{0!s}([{1!s}], {2!s})".format(implies, hyp_str, conc)


def print_pair(expr):
    """
    
    Arguments:
    - `expr`: a pair
    """
    return "pair({0!s}, {1!s})".format(expr.fst, expr.snd)


def print_fst(expr):
    """
    
    Arguments:
    - `expr`:
    """
    return color.cyan + "fst" + color.reset + "({0!s})".format(expr.expr)


def print_snd(expr):
    """
    
    Arguments:
    - `expr`:
    """
    return color.cyan + "snd" + color.reset + "({0!s})".format(expr.expr)


def print_box(expr):
    """
    
    Arguments:
    - `expr`:
    """
    return color.purple + "cast" + color.reset +\
           "({0!s}, {1!s})".format(expr.expr, expr.type)


def print_pi(expr):
    """
    
    Arguments:
    - `expr`:
    """
    return "({0!s}) → {1!s}".format(expr.dom, expr.body)


def print_sig(expr):
    """
    
    Arguments:
    - `expr`:
    """
    return "{0!s} × {1!s}".format(expr.dom, expr.body)


def print_sub(expr):
    """
    
    Arguments:
    - `expr`:
    """
    return "{0!s} ≤ {1!s}".format(expr.lhs, expr.rhs)


def print_eq(expr):
    return "{0!s} ≃ {1!s}".format(expr.lhs, expr.rhs)


def print_bool():
    return color.green + "Bool" + color.reset


def print_type():
    return color.green + "Type" + color.reset


def print_ev(expr):
    if len(expr.tele) == 0:
        return color.cyan + "triv()" + color.reset
    else:
        return expr.to_string()


def typ_str(expr):
    if expr.is_const():
        return print_const(expr)
    if expr.is_app():
        return print_app(expr)
    elif expr.is_pi():
        return print_pi(expr)
    elif expr.is_sig():
        return print_sig(expr)
    elif expr.is_sub():
        return print_sub(expr)
    elif expr.is_bool():
        return print_bool()
    elif expr.is_type():
        return print_type()
    else:
        return expr.to_string()


binder_utf_name = {
    'pi': color.purple + 'Π' + color.reset,
    'sig': color.purple + 'Σ' + color.reset,
    'abst': color.purple + 'λ' + color.reset,
    'forall': color.purple + '∀' + color.reset,
    'exists': color.purple + '∃' + color.reset
    }


def print_bound(expr):
    b = expr.binder
    vars, body = elab.open_bound_fresh_consts(expr)
    name = binder_utf_name[b.name]
    if len(vars) == 1:
        return "{0!s}({1!s}, {2!s})".format(name, vars[0], body)
    else:
        vars_str = ', '.join(map(str, vars))
        return "{0!s}([{1!s}], {2!s})".format(name, vars_str, body)


def tm_str(expr):
    if expr.is_const():
        return print_const(expr)
    if expr.is_app():
        return print_app(expr)
    elif expr.is_pair():
        return print_pair(expr)
    elif expr.is_fst():
        return print_fst(expr)
    elif expr.is_snd():
        return print_snd(expr)
    elif expr.is_sub():
        return print_eq(expr)
    elif expr.is_bound():
        return print_bound(expr)
    elif expr.is_ev():
        return print_ev(expr)
    elif expr.is_box():
        return print_box(expr)
    else:
        return expr.to_string()


###############################################################################
#
# Constructors for terms and types
#
###############################################################################

# 'standard' information for terms and types.
# The fields are filled in below.

st_term = ExprInfo('term_info', {})
st_typ = ExprInfo('type_info', {})


# cast Python objects to appropriate expressions
def to_expr(expr):
    if isinstance(expr, int):
        return ii(expr)
    elif isinstance(expr, float):
        return rr(expr)
    else:
        return expr


@with_info(st_term)
def pair(expr1, expr2):
    """Turn a pair of simply typed arguments
    into a Pair.
    
    Arguments:
    - `expr1`: an expression or int or float
    - `expr1`: an expression or int or float
    """
    e1 = to_expr(expr1)
    e2 = to_expr(expr2)
    ty1, _ = typing.infer(e1, ctxt=local_ctxt)
    ty2, _ = typing.infer(e2, ctxt=local_ctxt)
    return Pair(e1, e2, typ_mul(ty1, ty2))


@with_info(st_term)
def tm_call(fun, *args):
    """Return the result of the application of
    fun to the arguments *args, using trivial
    conversion certificates.
    
    Arguments:
    - `fun`: an expression
    - `arg`: a list of expresstions
    """
    fun_typ, _ = typing.infer(fun, ctxt=local_ctxt)
    conv = [triv()] * len(args)
    cast_args = map(to_expr, args)
    return app_expr(fun, fun_typ, conv, cast_args)


@with_info(st_term)
def const(name, type, value = None, **kwargs):
    return Const(name, type, value)

# Special call methods for 'And', 'Or', and 'implies'. Allosw e.g.
# And(e1, e2, e3) and implies([e1, e2, e3], e4), and specifies that the
# resulting expressions should print out this way.
# This also works for add and mul, so we can write e.g.
#   add(e1, e2, ...) and mul(e1, e2, ...)

def iterative_app_call(op, *args):
    e = reduce(lambda e1, e2: tm_call(op, e1, e2), args[1:], args[0])
    return e


# note: to use reduce, the arguments have to go in this order
def mk_implies(conc, hyp):
    e = tm_call(implies, hyp, conc)
#    e.info['__str__'] = print_implies
    return e


# op here should be implies. But this could be abstracted out as in the
# last case to generalize this behavior
def implies_call(op, hyps, conc):
    if isinstance(hyps, list):
        return reduce(mk_implies, reversed(hyps), conc)
    else:
        return tm_call(implies, hyps, conc)


@with_info(st_term)
def get_pair(expr, index):
    """Get the field of an expression using python syntax
    
    Arguments:
    - `expr`: an expression
    - `index`: an integer equal to 0 or 1
    """
    if index == 0:
        return Fst(expr)
    elif index == 1:
        return Snd(expr)
    else:
        raise Exception("Index applied to {0!s} must be 0 or 1"\
                        .format(expr))


# without the decorator, would have term info
@with_info(st_typ)
def type_arrow(type1, type2):
    return pi(Const('_', type1), type2)


# this is used for functions that take a string, consisting either of
# a single name, or a list of names, e.g.
#
#   Int('x')
#   Int('x y z')
#   Int('x,y,z')
#
# It is modeled after Sage's SR.var
def _str_to_list(s):
    if ',' in s:
        return [item.strip() for item in s.split(',')]
    elif ' ' in s:
        return [item.strip() for item in s.split()]
    else:
        return [s]


# a special call method for types - create a constant of that type
def typ_call(type, name_str):
    names = _str_to_list(name_str)
    if len(names) == 1:
        return defconst(names[0], type)
    else:
        consts = ()
        for name in names:
            consts += (defconst(name, type),)
        return consts


@with_info(st_typ)
def typ_mul(type1, type2):
    return sig(Const('_', type1), type2)


@with_info(st_typ)
def typ_le(type1, type2):
    return Sub(type1, type2)


###############################################################################
#
# Set the appropriate syntactic operations for terms and types
#
###############################################################################

# operations for terms
st_term['__str__'] = tm_str
st_term['__call__'] = tm_call
st_term['__getitem__'] = get_pair
st_term['__eq__'] = (lambda expr1, expr2: eq(expr1, expr2))
st_term['__ne__'] = (lambda expr1, expr2: Not(eq(expr1, expr2)))
st_term['__add__'] = (lambda expr1, expr2: add(expr1, expr2))
st_term['__radd__'] = (lambda expr2, expr1: add(expr1, expr2))
st_term['__mul__'] = (lambda expr1, expr2: mul(expr1, expr2))
st_term['__rmul__'] = (lambda expr2, expr1: mul(expr1, expr2))
st_term['__sub__'] = (lambda expr1, expr2: minus(expr1, expr2))
st_term['__rsub__'] = (lambda expr2, expr1: minus(expr1, expr2))
st_term['__div__'] = (lambda expr1, expr2: div(expr1, expr2))
st_term['__rdiv__'] = (lambda expr2, expr1: div(expr1, expr2))
st_term['__mod__'] = (lambda expr1, expr2: mod(expr1, expr2))
st_term['__rmod__'] = (lambda expr2, expr1: mod(expr1, expr2))
st_term['__pow__'] = (lambda expr1, expr2: power(expr1, expr2))
st_term['__rpow__'] = (lambda expr2, expr1: power(expr1, expr2))
st_term['__rshift__'] = type_arrow
st_term['__le__'] = (lambda expr1, expr2: le(expr1, expr2))
st_term['__ge__'] = (lambda expr1, expr2: le(expr2, expr1))
st_term['__lt__'] = (lambda expr1, expr2: lt(expr1, expr2))
st_term['__gt__'] = (lambda expr1, expr2: lt(expr2, expr1))
st_term['__abs__'] = (lambda expr: absf(expr))
st_term['__neg__'] = (lambda expr: uminus(expr))

# operations for types
st_typ['__call__'] = typ_call
st_typ['__mul__'] = typ_mul
st_typ['__rshift__'] = type_arrow
st_typ['__str__'] = typ_str
st_typ['__le__'] = typ_le


###############################################################################
#
# More term and type constructors
#
###############################################################################

def fold_over(base_op, var, tm, **kwargs):
    """
    Apply a base operation to a list of
    objects
    """
    if isinstance(var, list):
        var.reverse()
        res = tm
        for v in var:
            res = base_op(v, res, **kwargs)
        var.reverse()
        return res
    else:
        return base_op(var, tm, **kwargs)


@with_info(st_term)
def pi_base(var, codom, **kwargs):
    return elab.pi(var, codom, **kwargs)


def pi(var, codom, **kwargs):
    return fold_over(pi_base, var, codom, **kwargs)


@with_info(st_term)
def abst_base(var, body):
    return elab.abst(var, body)


def abst(var, body):
    return fold_over(abst_base, var, body)


@with_info(st_term)
def forall_base(var, prop):
    return elab.forall(var, prop)


def forall(var, prop):
    return fold_over(forall_base, var, prop)


@with_info(st_term)
def exists_base(var, prop):
    return elab.exists(var, prop)


def exists(var, prop):
    return fold_over(exists_base, var, prop)


@with_info(st_term)
def sig_base(var, codom):
    return elab.sig(var, codom)


def sig(var, codom):
    return fold_over(sig_base, var, codom)


@with_info(st_term)
def nullctxt():
    return elab.nullctxt()


@with_info(st_term)
def triv():
    return elab.trivial


@with_info(st_term)
def cast(expr, ty):
    """cast an expression to ty
    
    Arguments:
    - `expr`: an expression
    - `ty`: a type equal to the type of expr
    """
    return Box(triv(), expr, ty)


###############################################################################
#
# Destructors -- routines to unpack a forall, etc.
#
###############################################################################

def dest_app_implicit(expr):
    """If a term is of the form (..(f a0).. an), return the pair
    (f, [ai,..., ak]) where the ai...ak are the non-implicit arguments of f.
    
    Arguments:
    - `expr`: an expression
    """
    r, args = root_app(expr)
    
    ty, _ = mvar_infer(r, ctxt=local_ctxt)

    non_implicit = []
    i = 0
    while ty.is_pi() and i < len(args):
        if not ty.info.implicit:
            non_implicit.append(args[i])
        i += 1
        ty = ty.body

    return (r, non_implicit)


def instantiate_bound_expr(e1, e2):
    """Takes an expression e1 of the form  'Binder dom, body', and returns
    the result of substituting e2 in body.
    """
    assert(e1.is_bound())
    return subst_expr([e2], e1.body)


def dest_binop_left(expr, op):
    """Assuming 'op' is a binary operation, returns a list of expressions,
    elist, such that
    expr = op(op(...op(elist[0], elist[1]), ... elist[n-1]), elist[n]),
    that is, an iterated application of op associating to the left.
    """
    if not expr.is_app():
        raise TermError('dest_binop_left: DEBUG')
#        raise TermError('dest_binop_left: {0!s} is not {1!s}'.format(expr, op))
    r, args = dest_app_implicit(expr)
    if not r.is_const() or r.name != op.name:
        raise TermError('dest_binop_left: {0!s} is not {1!s}'.format(expr, op))
    elist = [args[1]]
    expr = args[0]
    while r.is_const() and r.name == op.name and expr.is_app():
        r, args = dest_app_implicit(expr)
        if r.is_const() and r.name == op.name:
            elist.append(args[1])
            expr = args[0]
    elist.append(expr)
    elist.reverse()
    return elist

def dest_binop_right(expr, op):   
    """Assuming 'op' is a binary operation, returns a list of expressions, 
    elist, such that 
    expr = op(elist[0], op(elist[1], ... op(elist[n-1], elist[n])))
    that is, an iterated application of op associating to the right.
    """
    if not expr.is_app():
        raise TermError('dest_binop: {0!s} is not an {1!s}'.format(expr, op))
    r, args = dest_app_implicit(expr)
    if not r.is_const() or r.name != op.name:
        raise TermError('dest_binop: {0!s} is not {1!s}'.format(expr, op))
    elist = [args[0]]
    expr = args[1]
    while r.is_const() and r.name == op.name and expr.is_app():
        r, args = dest_app_implicit(expr)
        if r.is_const() and r.name == op.name:
            elist.append(args[0])
            expr = args[1]
    elist.append(expr)
    return elist


# TODO: maybe the next four are not needed
def dest_And(expr):
    """Returns a list elist of expressions such that expr = And(elist)
    """
    return dest_binop_left(expr, And)


def dest_Or(expr):
    """Returns a list elist of expressions such that expr = Or(elist)
    """
    return dest_binop_left(expr, Or)


def dest_add(expr):
    """Returns a list elist of expressions such that expr =
    elist[0] + ... + elist[n]
    """
    return dest_binop_left(expr, add)


def dest_mul(expr):
    """Returns a list elist of expressions such that expr =
    elist[0] + ... + elist[n]
    """
    return dest_binop_left(expr, mul)


def dest_implies(expr):
    """Returns a tuple hlist, conc of expressions such that
    expr = implies(hlist, conc)
    """
    elist = dest_binop_right(expr, implies)
    return elist[:-1], elist[-1]


###############################################################################
#
# A global variable to determine whether to use verbose output when
#   checking and elaborating terms, and defining objects
#
###############################################################################

verbose = False


def set_verbose(setting=True):
    global verbose

    verbose = setting


###############################################################################
#
# Term checking and elaboration.
#
# TODO: right now these just use the default local context. 
#
###############################################################################

elab_tac = tac.par(u.unify) >> tac.trytac(u.instances)
type_tac = tac.auto >> tac.trytac(u.instances)


def elaborate(expr, type, elabtac, tactic):
    """Elaborate an expression and (optionally) its type.
    Returns the elaborated expression and its type, and any
    remaining obligations.
    It also marks the expression and its type as elaborated.
    
    Arguments:
    - `expr`: the expression to be elaborated
    - `type`: it's putative type
    - `elabtac`: a tactic to use in the elaboration
    - `tactic`: a tactic to use in the type-checking
    """
    if expr.info.elaborated and type is None:
        ty, obl = typing.infer(expr, ctxt=local_ctxt)
        if tactic is None:
            obl.solve_with(type_tac)
        else:
            obl.solve_with(tactic)
        return (expr, ty, obl)

    _, obl = mvar_infer(expr, ctxt=local_ctxt)

    u.mvar_stack.clear()
    u.mvar_stack.new()

    if elabtac is None:
        obl.solve_with(elab_tac)
    else:
        obl.solve_with(elabtac)

    val = sub_mvar(expr, undef=True)

    if not (type is None):
        _, obl = mvar_infer(type, ctxt=local_ctxt)

        u.mvar_stack.clear()
        u.mvar_stack.new()
        
        if elabtac is None:
            obl.solve_with(elab_tac)
        else:
            obl.solve_with(elabtac)

        ty = sub_mvar(type, undef=True)

    if type is None:
        ty, obl = typing.infer(val, ctxt=local_ctxt)
    else:
        ty, obl = typing.infer(val, type=ty, ctxt=local_ctxt)

    if tactic is None:
        obl.solve_with(type_tac)
    else:
        obl.solve_with(tactic)

    val.info['elaborated'] = True

    return (val, ty, obl)


def check(expr, type=None, tactic=None):
    """Elaborates the expression if necessary, and shows the type. Returns
    the elaborated expression
    
    Arguments:
    - `expr`: the expression to be checked
    - `type`: it's putative type
    - `tactic`: a tactic to use in the elaboration
    """

    val, ty, obl = elaborate(expr, type, None, tactic)
    if obl.is_solved():
        if verbose:
            print "{0!s} : {1!s}.\n".format(val, ty)
    else:
        local_ctxt.add_to_field(obl.name, obl, 'goals')
        print "In checking the expression\n"\
        "{0!s} : {1!s}".format(val, ty)
        print "remaining type-checking constraints!"
        print obl
    return val


###############################################################################
#
# Routines to create objects and put them in a context.
#
# TODO: right now these just use the default local context. Abstract over
#   local_ctxt.
#
#
###############################################################################

def deftype(name):
    """Define a type constant, and add it
    to local_ctxt.
    
    Arguments:
    - `name`:
    """
    c = mktype(name)
    local_ctxt.add_const(c)
    if verbose:
        print "{0!s} : {1!s} is assumed.\n".format(c, c.type)
    return c


def defconst(name, type, tactic=None, **kwargs):
    """Define a constant, add it to
    local_ctxt and return it.
    
    Arguments:
    - `name`: the name of the constant
    - `type`: the type of the constant
    - `infix`: if the constant being defined is a function,
    infix specifies that it needs to be printed in infix style
    - `tactic`: specifies an optional tactic to solve the proof
    obligations
    """
    c = const(name, type, **kwargs)

    c, _, obl = elaborate(c, None, None, tactic)

    c.info['checked'] = True
    local_ctxt.add_const(c)
    if obl.is_solved():
        if verbose:
            print "{0!s} : {1!s} is assumed.\n".format(c, c.type)
    else:
        local_ctxt.add_to_field(obl.name, obl, 'goals')
        print "In the declaration:\n{0!s} : {1!s}".format(name, c.type)
        print "remaining type-checking constraints!"
        print obl
    return c


def defexpr(name, value, type=None, tactic=None, **kwargs):
    """Define an expression with a given type and value.
    Checks that the type of value is correct, and adds the defining
    equation to the context.
    
    Arguments:
    - `name`: a string
    - `type`: an expression
    - `value`: an expression
    """
    val, ty, obl = elaborate(value, type, None, tactic)

    c = const(name, ty, **kwargs)
    c.info['defined'] = True
    c.info['checked'] = True
    local_ctxt.add_const(c)

    eq_c = equals(c, val)
    def_name = "{0!s}_def".format(name)
    c_def = const(def_name, eq_c)
    local_ctxt.add_const(c_def)
    local_ctxt.add_to_field(name, val, 'defs')

    if obl.is_solved():
        if verbose:
            print "{0!s} : {1!s} := {2!s} is defined.\n".format(c, ty, val)
    else:
        local_ctxt.add_to_field(obl.name, obl, 'goals')
        print "In the definition\n"\
        " {0!s} = {1!s} : {2!s}".format(name, val, ty)
        print "remaining type-checking constraints!"
        print obl
    return c


def defhyp(name, prop):
    """Declare a constant of type bool, add it to the
    list of hypotheses.
    
    Arguments:
    - `name`: the name of the hypothesis
    - `prop`: the proposition
    """
    c = defconst(name, prop)
    typing.infer(c.type, type=e.Bool(), ctxt=local_ctxt)
    local_ctxt.add_to_field(name, c.type, 'hyps')
    return c


def defthm(name, prop, tactic=None):
    """Declare a theorem and call a tactic to attempt to solve it.
    add it as a hypothesis regardless.
    
    """
    if tactic:
        c = defexpr(name, triv(), prop, tactic=tactic)
    else:
        c = defexpr(name, triv(), prop)
    local_ctxt.add_to_field(name, c.type, 'hyps')
    return c


def defsub(name, prop):
    """Declare a hypothesis of type A <= B
    
    Arguments:
    - `name`: the name of the hypothesis
    - `prop`: a proposition of the form A <= B
    """
    if prop.is_sub():
        c = defhyp(name, prop)
        local_ctxt.add_to_field(name, c.type, 'sub')
        return c
    else:
        raise Exception("Error in definition {0!s}:"\
                        "expected a proposition of the form A <= B"\
                        .format(name))


def defclass(name, params, defn):
    """Define a type class with the given name and type
    
    Arguments:
    - `name`: a string
    - `params`: a list of parameters
    - `def`: the definition of the class, which may depend on the parameters
    """
    class_ty = pi(params, Bool)
    class_def = abst(params, defn)
    
    c = defexpr(name, class_def, type=class_ty)
    c.info['is_class'] = True
    local_ctxt.add_to_field(name, c.type, 'classes')
    c_def = local_ctxt.defs[name]
    local_ctxt.add_to_field(name, c_def, 'class_def')
    return c


def definstance(name, ty, value):
    """
    
    Arguments:
    - `name`: a string
    - `ty`: a type of the form ClassName(t1,...,tn)
    """
    root, _ = root_app(root_clause(ty))
    if root.info.is_class:
        class_name = root.name
        class_tac = tac.par(tac.unfold(class_name)) >> tac.auto
        c = defexpr(name, value, type=ty, tactic=class_tac)
        local_ctxt.add_to_field(name, c.type, 'class_instances')
        local_ctxt.add_to_field(name, c.type, 'hyps')
        return c
    else:
        raise Exception("Error in definition of {0!s}:"\
                        "expected {1!s} to be a class name"\
                        .format(name, root))


###############################################################################
#
# Create a context for the basic definitions.
#
###############################################################################

local_ctxt = Context("local_ctxt")


###############################################################################
#
# Equality and basic sorts
#
###############################################################################

def equals(e1, e2):
    return And(Sub(e1, e2), Sub(e2, e1))

#create a single instance of Bool() and Type().
Bool = e.Bool()
Bool.info.update(st_typ)

Type = e.Type()
Type.info.update(st_typ)


@with_info(st_typ)
def mktype(name):
    """
    
    Arguments:
    - `name`:
    """
    return Const(name, Type)


###############################################################################
#
# Create some basic kinds of values.
#
# Terms of type value_description can be used
#
###############################################################################

value_description = deftype('value_description')
int_val = defconst('int_val', value_description)
float_val = defconst('float_val', value_description)


def ii(n):
    val = Value(n, desc=int_val, is_num=True)
    return const(str(n), Int, val, \
                 unicode=color.orange + str(n) + color.reset)


def rr(n):
    val = Value(n, desc=float_val, is_num=True)
    return const(str(n), Real, val, \
                 unicode=color.orange + str(n) + color.reset)

enumtype_val = defconst('enumtype_val', value_description)
enumelt_val = defconst('enum_val', value_description)


def defenumtype(name, elts):
    """ Takes a name and list of strings, and builds an enumerated type
    
    For example: Beatles, (John, Paul, George, Ringo) =
      defenumtype('Beatles', ['John', 'Paul', 'George', 'Ringo'])
    """
    enumtype = deftype(name)
    enumtype.value = Value(elts, enumtype_val)
    consts = ()
    for e in elts:
        c = defconst(e, enumtype)
        c.value = Value(e, enumelt_val)
        consts += (c,)
    return enumtype, consts


###############################################################################
#
# Logical operations
#
###############################################################################

# allow input and output syntax And(e1, e2, ..., en)
And = defconst('And', Bool >> (Bool >> Bool), \
               unicode=color.purple + 'And' + color.reset)
And.info['__call__'] = iterative_app_call
And.info['print_iterable_app'] = True

# allow input and output syntax Or(e1, e2, ..., en)
Or = defconst('Or', Bool >> (Bool >> Bool), \
              unicode=color.purple + 'Or' + color.reset)
Or.info['__call__'] = iterative_app_call
Or.info['print_iterable_app'] = True

Not = defconst('Not', Bool >> Bool, unicode='¬')

p = Bool('p')
q = Bool('q')
# allow input and output syntax implies([h1, ..., hn], conc)
implies = defexpr('implies', abst(p, abst(q, Sub(p, q))), \
               Bool >> (Bool >> Bool), \
                  unicode=color.purple + 'implies' + color.reset)
implies.info['__call__'] = implies_call
implies.info['print_implies'] = True

#This is equivalent to the constant given as type to terms
# of the form Ev(tele), as constants are only compared
# by name. As a result, it is proven using the auto tactic
true = defconst('true', Bool, \
                unicode=color.cyan + 'true' + color.reset)

false = defconst('false', Bool, \
                unicode=color.cyan + 'false' + color.reset)


###############################################################################
#
# Basic operations on the integers and reals
#
###############################################################################

# reals

Real = deftype('Real')

# binary operations on the reals

add_real = defconst('add_real', Real >> (Real >> Real))
mul_real = defconst('mul_real', Real >> (Real >> Real))
minus_real = defconst('minus_real', Real >> (Real >> Real))
divide_real = defconst('divide_real', Real >> (Real >> Real))
power = defconst('**', Real >> (Real >> Real), infix=True)
# TODO: not overloaded for now

# unary operations on the reals

uminus_real = defconst('uminus_real', Real >> Real)
abs_real = defconst('abs_real', Real >> Real)

# binary predicates on the reals

lt_real = defconst('lt_real', Real >> (Real >> Bool))
le_real = defconst('le_real', Real >> (Real >> Bool))

# integers

Int = deftype('Int')
int_sub_real = defsub('int_sub_real', Int <= Real)

# binary operations on the integers

add_int = defconst('add_int', Int >> (Int >> Int))
mul_int = defconst('mul_int', Int >> (Int >> Int))
minus_int = defconst('minus_int', Int >> (Int >> Int))
divide_int = defconst('divide_int', Int >> (Int >> Int))
mod = defconst('%', Int >> (Int >> Int), infix=True)

# unary operations on the integers

uminus_int = defconst('uminus_int', Int >> Int)
abs_int = defconst('abs_int', Int >> Int)

# binary predicates on the integers

lt_int = defconst('lt_int', Int >> (Int >> Bool))
le_int = defconst('le_int', Int >> (Int >> Bool))


###############################################################################
#
# Type classes and polymorphic constrants for numeric operations
#
###############################################################################

X = deftype('X')

x = X('x')
y = X('y')

eq = defexpr('==', abst([X, x, y], And(Sub(x, y), Sub(y, x))), \
             pi(X, X >> (X >> Bool), impl=True), infix=True, unicode='≃')

op = defconst('op', X >> (X >> X))
uop = defconst('uop', X >> X)

# allow input syntax mul(e1, e2, ..., en)
Mul = defclass('Mul', [X, op], true)
mul_ev = Const('mul_ev', Mul(X, op))
mul = defexpr('*', abst([X, op, mul_ev], op), \
              pi([X, op, mul_ev], X >> (X >> X), impl=True), \
              infix=True, unicode='×')
mul.info['__call__'] = iterative_app_call
mul.info['print_iterable_app'] = True
definstance('Mul_real', Mul(Real, mul_real), triv())
definstance('Mul_int', Mul(Int, mul_int), triv())

# allow input synatx add(e1, e2, ..., en)
Add = defclass('Add', [X, op], true)
add_ev = Const('add_ev', Add(X, op))
add = defexpr('+', abst([X, op, add_ev], op), \
              pi([X, op, add_ev], X >> (X >> X), impl=True), \
              infix=True)
add.info['__call__'] = iterative_app_call
add.info['print_iterable_app'] = True
definstance('Add_real', Add(Real, add_real), triv())
definstance('Add_int', Add(Int, add_int), triv())

Minus = defclass('Minus', [X, op], true)
minus_ev = Const('minus_ev', Minus(X, op))
minus = defexpr('-', abst([X, op, minus_ev], op), \
              pi([X, op, minus_ev], X >> (X >> X), impl=True), \
              infix=True)
definstance('Minus_real', Minus(Real, minus_real), triv())
definstance('Minus_int', Minus(Int, minus_int), triv())

Div = defclass('Div', [X, op], true)
div_ev = Const('div_ev', Div(X, op))
div = defexpr('/', abst([X, op, div_ev], op), \
              pi([X, op, div_ev], X >> (X >> X), impl=True), \
              infix=True)
definstance('Div_real', Div(Real, divide_real), triv())
definstance('Div_int', Div(Int, divide_int), triv())

Uminus = defclass('Uminus', [X, uop], true)
uminus_ev = Const('uminus_ev', Uminus(X, uop))
#TODO: can we use '-' for this as well?
uminus = defexpr('uminus', abst([X, uop, uminus_ev], uop), \
              pi([X, uop, uminus_ev], X >> X, impl=True))
definstance('Uminus_real', Uminus(Real, uminus_real), triv())
definstance('Uminus_int', Uminus(Int, uminus_int), triv())

Abs = defclass('Abs', [X, uop], true)
abs_ev = Const('abs_ev', Abs(X, uop))
# note: 'abs' is a built-in reserved symbol
absf = defexpr('abs', abst([X, uop, abs_ev], uop), \
              pi([X, uop, abs_ev], X >> X, impl=True), \
              infix=True)
definstance('Abs_real', Abs(Real, abs_real), triv())
definstance('Abs_int', Abs(Int, abs_int), triv())

pred = defconst('pred', X >> (X >> Bool))

Lt = defclass('Lt', [X, pred], true)
lt_ev = Const('lt_ev', Lt(X, pred))
lt = defexpr('<', abst([X, pred, lt_ev], pred), \
             pi([X, pred, lt_ev], X >> (X >> Bool), impl=True), \
             infix=True)
definstance('Lt_real', Lt(Real, lt_real), triv())
definstance('Lt_int', Lt(Int, lt_int), triv())

Le = defclass('Le', [X, pred], true)
le_ev = Const('le_ev', Le(X, pred))
le = defexpr('<=', abst([X, pred, le_ev], pred), \
             pi([X, pred, le_ev], X >> (X >> Bool), impl=True), \
             infix=True, unicode='≤')
definstance('Le_real', Le(Real, lt_real), triv())
definstance('Le_int', Le(Int, le_int), triv())
