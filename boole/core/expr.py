# -*- coding: utf-8 -*-

#############################################################################
#
# expr.py
#
# description: types and expressions in Boole, all constructors inherit from
# the Expr class, except Tele, which inherits from BaseExpr
#
#
# Authors:
# Jeremy Avigad
# Cody Roux
#
#
##############################################################################


from expr_base import *

import vargen

##############################################################################
#
# Expressions and types: these implement the term language of a dependent,
# extensional, impredicative and classical type theory, With subtyping.
#
#
# The datatype is represented by:
#
# Expr := Type | Kind | Bool   | Const(string,Expr)  | DB(int) |
#         Pi(name,Expr,Expr)   | App(Expr,Expr,Expr) |
#         Abst(name,Expr,Expr) | Sig(name,Expr,Expr) |
#         Pair(Expr,Expr,Type) | Fst(Expr) | Snd(Expr) |
#         Ev(Tele) |
#         Forall(name,Expr,Expr)           | Exists(name,Expr,Expr) |
#         Sub(Expr,Expr)       | Box(Expr,Expr,Expr)
#
# Tele := Tele([name,...,name],[Expr,...,Expr])
#
###############################################################################


class Const(Expr):
    """A constant declaration. Variables
    and constants are identified.
    """

    def __init__(self, name, type, value=None, **kwargs):
        """
        
        Arguments:
        - `name`: A name representing the constant
        - `type`: an expression representing its type
        - `value`: possibly a semantic value, making this an interpreted
        constant
        """
        Expr.__init__(self)
        self.name = name
        self.type = type
        self.value = value
        for k in kwargs:
            self.info[k] = kwargs[k]
        self._hash = hash(('Const', self.name, self.type))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_const(self, *args, **kwargs)

    def to_string(self):
        return self.name

    def is_const(self):
        return True

    def eq(self, expr):
        """Structural equality. Simply compares names.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_const():
            return self.name == expr.name
        else:
            return False


class DB(Expr):
    """A bound index represented by a De Bruijn variable.
    a De Bruijn variable generally does not to be initialized
    as it is incremented while moving through a term
    """
    
    def __init__(self, index):
        """
        """
        Expr.__init__(self)
        self.index = index
        self._hash = hash(("DB", self.index))

    def incr(self, inc):
        """Increment the index
        
        Arguments:
        - `inc`: integer specifying the increment.
        """
        self.index += inc

    def decr(self):
        """Decrement the index by 1
        """
        if self.index == 0:
            raise ExprError("Cannot decrement a DB\
            variable with index 0", self)
        else:
            self.index -= 1

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_db(self, *args, **kwargs)

    def to_string(self):
        return "DB({0!s})".format(self.index)

    def is_db(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_db():
            return self.index == expr.index
        else:
            return False


class Type(Expr):
    """The type of all small types
    """
    
    def __init__(self):
        """
        """
        Expr.__init__(self)
        self.name = 'Type'
        self._hash = hash('Type')

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_type(self, *args, **kwargs)

    def to_string(self):
        return "Type()"

    def is_type(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        return expr.is_type()


class Kind(Expr):
    """The type of all large types
    """
    
    def __init__(self):
        """
        """
        Expr.__init__(self)
        self._hash = hash('Kind')

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_kind(self, *args, **kwargs)

    def to_string(self):
        return "Kind()"
    
    def is_kind(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        return expr.is_kind()


class Bool(Expr):
    """The type of all propositions.
    """
    
    def __init__(self):
        """
        """
        Expr.__init__(self)
        self.name = 'Bool'
        self._hash = hash('Bool')

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_bool(self, *args, **kwargs)

    def to_string(self):
        return "Bool()"

    def is_bool(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        return expr.is_bool()


class Bound(Expr):
    """An expression consisting of a binder,
    a domain, and a term which binds a variable of
    that domain.
    """
    
    def __init__(self, binder, dom, body):
        """
        
        Arguments:
        - `binder`: an element of the Binder class
        - `dom`: an expression denoting the domain of the variable
        - `body`: an expression with a bound variable.
        """
        Expr.__init__(self)
        self.binder = binder
        self.dom = dom
        self.body = body
        self._hash = hash(("Bound", self.binder, self.dom, self.body))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_bound(self, *args, **kwargs)

    def to_string(self):
        # Printing a bound expression involves
        # substituting the DB index by a constant
        # with the appropriate name.
        var = self.binder.var
        open_self = open_expr(var, self.dom, self.body, None)
        return "{0!s}({1!s}, {2!s})".format(\
            self.binder.name, self.binder.var, open_self)

    def to_string_raw(self):
        return "{0!s}({1!s}, {2!s}, {3!s})".format(\
            self.binder.name, self.binder.var, self.dom, self.body)

    def is_bound(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_bound() and (self.binder.name == expr.binder.name):
            return self.dom.equals(expr.dom) and self.body.equals(expr.body)
        else:
            return False


class App(Expr):
    """Applications. Carries the proof of well-formedness
    """
    
    def __init__(self, conv, fun, arg):
        """
        
        Arguments:
        - `conv`: A term representing evidence that the application
        is well-typed.
        - `fun`: The functional part of the application.
        - `arg`: The argument part of the application.
        """
        Expr.__init__(self)
        self.conv = conv
        self.fun = fun
        self.arg = arg
        self._hash = hash(("App", self.fun, self.arg))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_app(self, *args, **kwargs)

    def to_string(self):
        """
        
        Arguments:
        - `self`:
        """
        return "App({0!s},{1!s},{2!s})".format(self.conv, self.fun, self.arg)

    def is_app(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_app():
            return self.fun.equals(expr.fun) and self.arg.equals(expr.arg)
        else:
            return False


class Pair(Expr):
    """Elements of Sigma types. They need to carry around their type,
    for type-checking to be decidable.
    """
    
    def __init__(self, fst, snd, type):
        """
        
        Arguments:
        - `fst`: an expression denoting the first component
        - `snd`: an expression denoting the second component
        - `type`: an expression
        """
        Expr.__init__(self)
        self.fst = fst
        self.snd = snd
        self.type = type
        self._hash = hash(("Pair", self.type, self.fst, self.snd))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_pair(self, *args, **kwargs)

    def to_string(self):
        return "Pair({0!s},{1!s},{2!s})".\
               format(self.fst, self.snd, self.type)
        
    def is_pair(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_pair():
            return self.fst.equals(expr.fst) and \
                   self.snd.equals(expr.snd) and \
                   self.type.equals(expr.type)
        else:
            return False


class Fst(Expr):
    """First projection for Sigma types
    """
    
    def __init__(self, expr):
        """
        
        Arguments:
        - `expr`: the expression to which is applied the projection.
        """
        Expr.__init__(self)
        self.expr = expr
        self._hash = hash(("Fst", self.expr))
    
    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_fst(self, *args, **kwargs)

    def to_string(self):
        """
        
        Arguments:
        - `self`:
        """
        return "Fst({0!s})".format(self.expr)

    def is_fst(self):
        return True

    def equals(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_fst():
            return self.expr.equals(expr.expr)
        else:
            return False


class Snd(Expr):
    """Second projection for Sigma types
    """
    
    def __init__(self, expr):
        """
        
        Arguments:
        - `expr`: the expression to which is applied the projection.
        """
        Expr.__init__(self)
        self.expr = expr
        self._hash = hash(("Snd", self.expr))
    
    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_snd(self, *args, **kwargs)

    def to_string(self):
        """
        
        Arguments:
        - `self`:
        """
        return "Snd({0!s})".format(self.expr)

    def is_snd(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_snd():
            return self.expr.equals(expr.expr)
        else:
            return False


class Ev(Expr):
    """Evidence type: provides evidence for a
    proposition (of type Bool)
    """
    
    def __init__(self, tele):
        """
        
        Arguments:
        - `tele`: a telescope of evidence for a proposition
        - `goals`: None, or a pointer to a set of goals,
        which may be solved by tactic applications.
        """
        Expr.__init__(self)
        self.tele = tele
        self.goals = None
        self._hash = hash("Ev")

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_ev(self, *args, **kwargs)

    def to_string(self):
        return "Ev({0!s})".format(self.tele)

    def is_ev(self):
        return True

    def eq(self, expr):
        """Structural equality. Does not compare telescopes!
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_ev():
            return True
        else:
            return False

    def show_proof(self):
        """Show the proof of the goal set containing
        the goal generated by self, if there is one.
        """
        if self.goals is None:
            print "No proof!"
            print
        prf = map(lambda x: str(x[1]), self.goals.history)
        print ", ".join(prf)
        print
        

class Sub(Expr):
    """The subtype relation. Makes sense regardless
    of the type of the expressions.
    """
    
    def __init__(self, lhs, rhs):
        """
        
        Arguments:
        - `lhs`: an expression
        - `rhs`: an expression
        """
        Expr.__init__(self)
        self.lhs = lhs
        self.rhs = rhs
        self._hash = hash(("Sub", self.lhs, self.rhs))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_sub(self, *args, **kwargs)

    def to_string(self):
        """
        
        Arguments:
        - `self`:
        """
        return "Sub({0!s}, {1!s})".format(self.lhs, self.rhs)

    def is_sub(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_sub():
            return (self.lhs.equals(expr.lhs)) and (self.rhs.equals(expr.rhs))
        else:
            return False


class Box(Expr):
    """Boxed epressions: a boxed expression
    carries a an expression, a type and a witness that the type of
    the expression is a subtype of the given type.
    """
    
    def __init__(self, conv, expr, type):
        """
        
        Arguments:
        - `conv`: A witness to the equality between the type
        of expr and type
        - `expr`: The expression denoted by the box
        - `type`: The type assigned to expr
        """
        Expr.__init__(self)
        self.conv = conv
        self.expr = expr
        self.type = type
        self._hash = hash(("Box", self.expr))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_box(self, *args, **kwargs)

    def to_string(self):
        return "Box({0!s},{1!s},{2!s})".format(self.conv, self.expr, self.type)

    def is_box(self):
        return True

    def eq(self, expr):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if expr.is_box():
            return self.expr.equals(expr.expr)
        else:
            return False

##############################################################################
#
# The class of variable binders: this includes Pi, Abst, forall/exists
# and Sig
#
###############################################################################


class Binder(object):
    """The class of Expression binders.
    """
    
    def __init__(self, var):
        """
        
        Arguments:
        - `var`: a variable name
        """
        self.var = var
        self._hash = None

    def is_pi(self):
        return False

    def is_abst(self):
        return False

    def is_forall(self):
        return False

    def is_exists(self):
        return False

    def is_sig(self):
        return False

    def __hash__(self, ):
        return self._hash


class Pi(Binder):
    """Dependent product
    """
    
    def __init__(self, var):
        Binder.__init__(self, var)
        self.name = "pi"
        self._hash = hash("Pi")

    def is_pi(self):
        return True


class Sig(Binder):
    """Dependent sum
    """
    
    def __init__(self, var):
        Binder.__init__(self, var)
        self.name = "sig"
        self._hash = hash("Sig")
       
    def is_sig(self):
        return True


class Abst(Binder):
    """Abstraction
    """
    
    def __init__(self, var):
        Binder.__init__(self, var)
        self.name = "abst"
        self._hash = hash("Abst")
        
    def is_abst(self):
        return True

 
class Forall(Binder):
    """Universal quantification
    """
    
    def __init__(self, var):
        Binder.__init__(self, var)
        self.name = "forall"
        self._hash = hash("Forall")

    def is_forall(self):
        return True


class Exists(Binder):
    """Existential quantification
    """
    
    def __init__(self, var):
        Binder.__init__(self, var)
        self.name = "exists"
        self._hash = hash("Exists")

    def is_exists(self):
        return True


###############################################################################
#
# The Tele class represents a telescope.
#
###############################################################################

class Tele(Expr):
    """A telescope is a (possible) list of names
    and expressions, each expression may depend on the
    previous ones.
    """
    
    def __init__(self, vars, types):
        """
        
        Arguments:
        - `vars`: the names of the variable associated to each expression.
        - `exprs`: a list of types. Each type binds a variable of
        the previous type.
        """
        Expr.__init__(self)
        self.info = info.DefaultInfo()
        self.vars = vars
        self.types = types
        self.len = len(self.types)
        assert(len(self.vars) == self.len)
        self._hash = hash(("Tuple", tuple(self.types)))

    def accept(self, visitor, *args, **kwargs):
        """The accept method allows the definition of
        recursive functions over objects of type expr.
        
        Arguments:
        - `visitor`: an object of class ExprVisitor
        - `*args`: arguments to the visitor instance
        - `**kwargs`: named arguments to the visitor instance
        """
        return visitor.visit_tele(self, *args, **kwargs)

    def to_string(self):
        """
        
        Arguments:
        - `self`:
        """
        var_str = ', '.join(self.vars)
        ty_str = ', '.join(map(str, self.types))
        return "Tele([{0!s}], [{1!s}])".format(var_str, ty_str)

    def eq(self, tele):
        """Structural equality.
        
        Arguments:
        - `expr`: an expression
        """
        if self.len == tele.len:
            eq_info = [t1.equals(t2)\
                       for (t1, t2) in zip(self.types, tele.types)]
            return reduce(lambda x, y: x and y, eq_info, True)
        else:
            return False

    def __str__(self):
        """Call the printer implemented in info
        """
        try:
            return self.info['__str__'](self)
        except KeyError:
            raise AttributeError('__str__')

    def __len__(self):
        return self.len

    def append(self, var, ty):
        """Add a variable and a type to the
        telescope. Side-effect free:
        returns a telescope
        
        Arguments:
        - `var`: a variable
        - `ty`: an expression
        """
        return Tele(self.vars + [var], self.types + [ty])

    def concat(self, tele):
        """Same as above, but for concatenation
        
        Arguments:
        - `tele`:
        """
        return Tele(self.vars + tele.vars, self.types + tele.types)

    def pop(self, i=None):
        """Pop the i-th (last by default)
        argument of a telescope
        return the pair (name, type)
        
        Arguments:
        - `i`: an integer
        """
        if i is None:
            return (self.vars.pop(), self.types.pop())
        else:
            return (self.vars.pop(i), self.types.pop(i))


def open_tele(tele, vars, checked=False):
    """Takes a telescope and returns a list of pairs
    (constant, type) where the subsequent types may depend
    on the constant.
    
    Arguments:
    - `tele`: a telescope
    """
    opened_ty = tele.types
    consts = []
    for i in range(0, tele.len):
        opened_ty[i] = subst_expr(consts, opened_ty[i], is_open=True)
        x = Const(vars[i], opened_ty[i], checked=checked)
        consts.append(x)
    return (consts, opened_ty)


def open_tele_default(tele):
    """Open a telescope with the default variables provided by
    the telescope definition.
    
    Arguments:
    - `tele`: a telescope
    """
    return open_tele(tele, tele.vars)


def open_tele_fresh(tele, checked=False):
    """Open a telescope with fresh variables
    
    Arguments:
    - `tele`: a telescope
    """
    fr_vars = [fresh_name.get_name(v) for v in tele.vars]
    return open_tele(tele, fr_vars, checked=checked)


##############################################################################
#
# We add a new constructor to the Expr class: it represents meta-variables
# which can be given a value when determined to be equal to an expression
# by unification.
#
##############################################################################


class Mvar(Expr):
    """Unification variables for implicit arguments
    """
    
    def __init__(self, name, type):
        """
        Same definition as for Const, without info fields
        and the additional information for:
        - potential value,
        - the conext in which it was created (to be used when finding
        a value)
        - the pending abstractions to be applied to the final value when found.
        """
        Expr.__init__(self)
        self.name = name
        self.type = type
        self._value = None
        self.tele = nullctxt()
        self.pending = []
        self._hash = hash(("Mvar", self.name, self.type))

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_mvar(self, *args, **kwargs)

    def set_val(self, val):
        """Give a value to the meta-variable
        
        Arguments:
        - `val`: an expression
        """
        #update the info field to correspond to that
        #of the value: this makes mvar substitution
        #behave correctly with respect to info
        self.info = val.info
        self._value = val

    def to_string(self):
        return "?{0!s}".format(self.name)

    def is_mvar(self):
        """Tests whether the expression is an instance of
        Mvar
        """
        return True

    def eq(self, expr):
        #There should only be one instance of
        #each meta-variable, so we use pointer equality
        return self is expr

    def has_value(self):
        """Returns True if the expression has a value
        """
        return not (self._value is None)

    def clear(self):
        """Clear the value and the information of the
        meta-variable.
        """
        self.info = info.DefaultInfo()
        self._value = None


##############################################################################
#
# The type of Pending substitution and abstraction operations.
# These are performed as the meta-variable is instantiated to a value
#
##############################################################################


class Pending(object):
    pass


class PendAbs(Pending):
    """A pending abstraction
    """
    
    def __init__(self, names, depth):
        """
        
        Arguments:
        - `names`:
        """
        Pending.__init__(self)
        self.names = names
        self.depth = depth
        
    def now(self, expr):
        """Evaluate the abstraction
        
        Arguments:
        - `expr`:
        """
        return AbstractExpr(self.names).visit(expr, self.depth)

    def __str__(self):
        return "PendAbs({0!s}, {1!s})".format(self.names, self.depth)


class PendSub(Pending):
    """A pending Substitution
    """
    
    def __init__(self, exprs, depth):
        """
        
        Arguments:
        - `names`:
        """
        Pending.__init__(self)
        self.exprs = exprs
        self.depth = depth

    def now(self, expr):
        """Evaluate the substitution
        
        Arguments:
        - `expr`:
        """
        return SubstExpr(self.exprs).visit(expr, self.depth)

    def __str__(self):
        return "PendSub({0!s}, {1!s})".format(self.exprs, self.depth)

###############################################################################
#
# The visitor class for Expr and Tele
#
###############################################################################


class ExprVisitor(object):
    """The visitor class for Expr and Tele
    """
    
    def __init__(self):
        """Do nothing by default.
        """
        pass

    def visit_const(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_db(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_type(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_kind(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_bool(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_bound(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_app(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_pair(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_fst(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_snd(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_ev(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_sub(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_box(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_tele(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit_mvar(self, expr, *args, **kwargs):
        raise NotImplementedError()

    def visit(self, expr, *args, **kwargs):
        """Call the appropriate method of self
        on expr depending on its form.
        
        Arguments:
        - `expr`: an expression
        """
        return expr.accept(self, *args, **kwargs)


###############################################################################
#
# Locally nameless representation utility functions:
# binding and freeing variables.
#
###############################################################################


class AbstractExpr(ExprVisitor):
    """Abstract an expression over a list
    of names, in the locally nameless approach. Return
    the updated expression. The names should be distinct.
    """
    
    def __init__(self, names):
        """

        Arguments:
        - `names`: a list of strings
        """
        ExprVisitor.__init__(self)
        self.names = names

    def visit_const(self, expr, depth):
        """
        
        Arguments:
        - `expr`: an expression.
        - `depth`: the number of binders crossed.
        """
        if expr.name in self.names:
            index = depth + self.names.index(expr.name)
            return DB(index)
        else:
            return expr

    def visit_db(self, expr, *args, **kwargs):
        return DB(expr.index)

    def visit_type(self, expr, *args, **kwargs):
        return Type()

    def visit_kind(self, expr, *args, **kwargs):
        return Kind()

    def visit_bool(self, expr, *args, **kwargs):
        return Bool()

    def visit_bound(self, expr, depth):
        """
        
        Arguments:
        - `expr`: an expression.
        - `depth`: the number of binders crossed.
        """
        dom = self.visit(expr.dom, depth)
        b_body = self.visit(expr.body, depth + 1)
        return Bound(expr.binder, dom, b_body)
        
    def visit_app(self, expr, *args, **kwargs):
        conv = self.visit(expr.conv, *args, **kwargs)
        fun = self.visit(expr.fun, *args, **kwargs)
        arg = self.visit(expr.arg, *args, **kwargs)
        return App(conv, fun, arg)

    def visit_pair(self, expr, *args, **kwargs):
        type = self.visit(expr.type, *args, **kwargs)
        fst = self.visit(expr.fst, *args, **kwargs)
        snd = self.visit(expr.snd, *args, **kwargs)
        return Pair(fst, snd, type)

    def visit_fst(self, expr, *args, **kwargs):
        sub_expr = self.visit(expr.expr, *args, **kwargs)
        return Fst(sub_expr)

    def visit_snd(self, expr, *args, **kwargs):
        sub_expr = self.visit(expr.expr, *args, **kwargs)
        return Snd(sub_expr)

    def visit_ev(self, expr, *args, **kwargs):
        tele = self.visit(expr.tele, *args, **kwargs)
        return Ev(tele)

    def visit_sub(self, expr, *args, **kwargs):
        lhs = self.visit(expr.lhs, *args, **kwargs)
        rhs = self.visit(expr.rhs, *args, **kwargs)
        return Sub(lhs, rhs)

    def visit_box(self, expr, *args, **kwargs):
        conv = self.visit(expr.conv, *args, **kwargs)
        expr_cast = self.visit(expr.expr, *args, **kwargs)
        type = self.visit(expr.type, *args, **kwargs)
        return Box(conv, expr_cast, type)

    def visit_mvar(self, expr, depth):
        expr.tele = self.visit(expr.tele, depth)

        #This code should not be needed
        # print "Abstracting over", self.names[0]
        # expr.pending.append(e.PendAbs(self.names, depth))

        # return the actual object here, as we want the value to
        # be propagated at each instance of the meta-variable
        return expr

    def visit_tele(self, expr, depth):
        types = []
        for i, e in enumerate(expr.types):
            abs_e = self.visit(e, depth + i)
            types.append(abs_e)

        return Tele(expr.vars, types)

    @info.same_info
    def visit(self, expr, *args, **kwargs):
        return expr.accept(self, *args, **kwargs)


def abstract_expr(vars, expr):
    """Abstract a list of variables in an
    expression.
    
    Arguments:
    - `var_list`: a list of variable names
    - `expr`: an expression
    """
    abstractor = AbstractExpr(vars)
    return abstractor.visit(expr, 0)


class SubstExpr(ExprVisitor):
    """Given a list of expressions e0,...,en
    instantiate the DB indices 0,...,n with those
    terms.
    """
    
    def __init__(self, exprs, is_open=None):
        """
        
        Arguments:
        - `exprs`: the expressions to instantiate.
        """
        ExprVisitor.__init__(self)
        self.exprs = exprs
        self.len = len(self.exprs)
        self.is_open = is_open
        
    def visit_const(self, expr, *args, **kwargs):
        if self.is_open:
            return expr
        else:
            ty = self.visit(expr.type, *args, **kwargs)
            return Const(expr.name, ty)

    def visit_db(self, expr, depth):
        if expr.index < depth:
            return DB(expr.index)
        elif expr.index < depth + self.len:
            return self.exprs[expr.index - depth]
        else:
            return DB(expr.index)
            # raise ExprError("Unbound DB variable", expr)
        
    def visit_type(self, expr, *args, **kwargs):
        return Type()

    def visit_kind(self, expr, *args, **kwargs):
        return Kind()

    def visit_bool(self, expr, *args, **kwargs):
        return Bool()

    def visit_bound(self, expr, depth):
        dom = self.visit(expr.dom, depth)
        b_expr = self.visit(expr.body, depth + 1)
        return Bound(expr.binder, dom, b_expr)

    def visit_app(self, expr, *args, **kwargs):
        conv = self.visit(expr.conv, *args, **kwargs)
        fun = self.visit(expr.fun, *args, **kwargs)
        arg = self.visit(expr.arg, *args, **kwargs)
        return App(conv, fun, arg)

    def visit_pair(self, expr, *args, **kwargs):
        type = self.visit(expr.type, *args, **kwargs)
        fst = self.visit(expr.fst, *args, **kwargs)
        snd = self.visit(expr.snd, *args, **kwargs)
        return Pair(fst, snd, type)

    def visit_fst(self, expr, *args, **kwargs):
        sub_expr = self.visit(expr.expr, *args, **kwargs)
        return Fst(sub_expr)

    def visit_snd(self, expr, *args, **kwargs):
        sub_expr = self.visit(expr.expr, *args, **kwargs)
        return Snd(sub_expr)

    def visit_ev(self, expr, *args, **kwargs):
        tele = self.visit(expr.tele, *args, **kwargs)
        return Ev(tele)

    def visit_sub(self, expr, *args, **kwargs):
        lhs = self.visit(expr.lhs, *args, **kwargs)
        rhs = self.visit(expr.rhs, *args, **kwargs)
        return Sub(lhs, rhs)

    def visit_box(self, expr, *args, **kwargs):
        conv = self.visit(expr.conv, *args, **kwargs)
        expr_cast = self.visit(expr.expr, *args, **kwargs)
        type = self.visit(expr.type, *args, **kwargs)
        return Box(conv, expr_cast, type)

    def visit_mvar(self, expr, depth):
        expr.tele = self.visit(expr.tele, depth)
        #We record the opens performed on an Mvar, and apply
        #them in reverse as it is substituted by its value
        if self.is_open:
            names = [exp.name for exp in self.exprs]
            expr.pending.append(PendAbs(names, depth))
        # expr.pending.append(PendSub(self.exprs, depth))
        return expr

    def visit_tele(self, expr, depth):
        types = []
        for i, e in enumerate(expr.types):
            abs_e = self.visit(e, depth + i)
            types.append(abs_e)

        return Tele(expr.vars, types)

    @info.same_info
    def visit(self, expr, *args, **kwargs):
        return expr.accept(self, *args, **kwargs)


def subst_expr(exprs, expr, is_open=None):
    """Instantiate DB indices in expr according
    to expr_list
    
    Arguments:
    - `expr_list`: a list of expressions
    - `expr`: an expression
    """
    if is_open != None:
        subster = SubstExpr(exprs, is_open=is_open)
    else:
        subster = SubstExpr(exprs)
    return subster.visit(expr, 0)


def sub_in(exprs, vars, expr):
    """Replace constants with names given by vars
    by exprs in expr.
    
    Arguments:
    - `exprs`: a list of expressions
    - `vars`: a list of variable names
    - `expr`: an expression
    """
    return subst_expr(exprs, abstract_expr(vars, expr))


def open_expr(var, typ, expr, checked):
    """Return the opened version of an expression
    with a bound variable, by substituting
    the bound name with a constant of type
    typ.
    
    Arguments:
    - `var`: a variable name
    - `typ`: a type
    - `expr`: an expression with a bound
    variable
    - `checked`: marks weather typ has been
    checked for well-typedness
    """
    if checked == None:
        const = Const(var, typ, checked=True)
    else:
        const = Const(var, typ, checked=checked)
    return subst_expr([const], expr, is_open=True)


def open_bound_fresh(expr, checked=None):
    """Return the opened body of a bound expression
    using the variable from the binder to generate a fresh
    name, along with the variable name. The constant is marked as
    type-checked by default.
    
    Arguments:
    - `expr`: an instance of Bound
    """
    assert(expr.is_bound())
    var = fresh_name.get_name(expr.binder.var, free_vars(expr.body))
    return (var, open_expr(var, expr.dom, expr.body, checked))


def open_bound_fresh_const(expr):
    """Returns the pair (v, b) where v is a variable, b is an expression,
    and expr is the result of binding v in b expr.binder.
    """
    assert(expr.is_bound())
    var = fresh_name.get_name(expr.binder.var, free_vars(expr.body))
    return (Const(var, expr.dom), open_expr(var, expr.dom, expr.body, None))


def open_bound_fresh_consts(expr):
    """Returns the pair (vlist, b) where vlist is a list of variables,
    b is an expression, and expr is the result of iteratively binding
    the variables in vlist in b, using the same binder.
    """
    assert(expr.is_bound())
    b = expr
    vlist = []
    while b.is_bound() and b.binder.name == expr.binder.name\
              and str(b.info) == str(expr.info):
        v, b = open_bound_fresh_const(b)
        vlist.append(v)
    return (vlist, b)


###############################################################################
#
# Various utility functions.
#
###############################################################################

def nullctxt():
    """The empty telescope
    """
    return Tele([], [])


def root_app(expr):
    """Returns the pair (r, args)
    such that expr = r(*args)
    
    Arguments:
    - `expr`: an expression
    """
    root = expr
    args = []
    while root.is_app():
        args.append(root.arg)
        root = root.fun
        #The arguments were collected in reverse order
    args.reverse()
    return (root, args)


def root_pi(expr):
    """Returns the pair (r, [an,..,a0])
    such that expr = Pi(a0, Pi(.. Pi(an, r)..)
    
    Arguments:
    - `expr`: an expression
    """
    root = expr
    args = []
    while root.is_pi():
        args.append(root.dom)
        _, root = open_bound_fresh(root)
    return (root, args)


def arg_i(expr, i):
    """Takes an expresion of the form f(a0,..., an)
    and returns ai, fails if the argument is not of the
    correct form.
    
    Arguments:
    - `expr`: an expression
    - `i`: an integer
    """
    _, args = root_app(expr)
    return args[i]


def is_eq(expr):
    """Returns True if the expression
    is of the form eq(e1, e2), False otherwise.
    
    Arguments:
    - `expr`:
    """
    root, args = root_app(expr)
    #There is an implicit type argument
    return root.is_const() and (root.name == '==') and (len(args) == 3)


def is_impl(expr):
    """Returns True if the expression
    is of the form implies(e1, e2), False otherwise.
    
    Arguments:
    - `expr`:
    """
    root, args = root_app(expr)
    # TODO: hardcoding the name of implication here is inelegant
    return root.is_const() and root.name == 'implies' and \
           len(args) == 2


def root_clause(expr):
    """Returns r such that expr is of the form
    forall(x1,...,forall(xn, p1 >= (p2 >= ... (pm >= r))))
    replacing xi with fresh variables
    
    Arguments:
    - `expr`: an expression
    """
    root = expr
    while root.is_forall():
        _, root = open_bound_fresh(root)
    while is_impl(root):
        root = arg_i(root, 1)
    return root


def sig_to_tele(expr, open_bound):
    """Takes a sigma type S = Sig(x1:A1,Sig(x2:A2,...,An+1)..)
    and returns the telescope:
    [x1:A1,...,xn:An,h:An+1]
    
    Arguments:
    - `expr`: an expression
    - `open_bound`: a function which opens binders
    """
    sig_ty = expr
    tele = Tele([], [])
    while sig_ty.is_sig():
        v, new_ty = open_bound(sig_ty)
        tele = tele.append(v, sig_ty.dom)
        sig_ty = new_ty
    hyp = fresh_name.get_name('hyp')
    return tele.append(hyp, sig_ty)


def unpack_sig(expr, names):
    """Takes a sigma type S = Sig(x1:A1,Sig(x2:A2,...,An)..)
    and returns the dependent tuple
    (x1, (x2,(...,h)..) with xi : Ai and h : An
    
    Arguments:
    - `expr`: an expression
    -`names`: either None, or a list of names to give to the projections.
    """
    sig_ty = expr
    tup = []
    if names is None:
        proj_names = []
    else:
        proj_names = names[:]
    proj_names.reverse()
    while sig_ty.is_sig():
        v, new_ty = open_bound_fresh(sig_ty)
        try:
            #FIXME: possible name capture
            n = proj_names.pop()
        except IndexError:
            n = v
        c = Const(n, sig_ty.dom)
        tup.append((c, sig_ty))
        sig_ty = new_ty
    try:
        n = proj_names.pop()
    except IndexError:
        n = fresh_name.get_name('h')
    c = Const(n, sig_ty)
    if len(tup) == 0:
        return c
    else:
        ret = c
        while len(tup) != 0:
            fst, ty = tup.pop()
            ret = Pair(fst, ret, ty)
        return ret


class FreeVars(ExprVisitor):
    """Returns the list of free variables of
    an expression.
    """
    
    def __init__(self):
        ExprVisitor.__init__(self)

    def visit_const(self, expr, *args, **kwargs):
        return self.visit(expr.type, *args, **kwargs) + \
               [expr]

    def visit_db(self, expr, *args, **kwargs):
        return []

    def visit_type(self, expr, *args, **kwargs):
        return []

    def visit_kind(self, expr, *args, **kwargs):
        return []

    def visit_bool(self, expr, *args, **kwargs):
        return []

    def visit_bound(self, expr, *args, **kwargs):
        return self.visit(expr.dom, *args, **kwargs) + \
               self.visit(expr.body, *args, **kwargs)

    def visit_app(self, expr, *args, **kwargs):
        return self.visit(expr.conv, *args, **kwargs) + \
               self.visit(expr.fun, *args, **kwargs) + \
               self.visit(expr.arg, *args, **kwargs)

    def visit_pair(self, expr, *args, **kwargs):
        return self.visit(expr.fst, *args, **kwargs) + \
               self.visit(expr.snd, *args, **kwargs) + \
               self.visit(expr.type, *args, **kwargs)

    def visit_fst(self, expr, *args, **kwargs):
        return self.visit(expr.expr, *args, **kwargs)

    def visit_snd(self, expr, *args, **kwargs):
        return self.visit(expr.expr, *args, **kwargs)

    def visit_ev(self, expr, *args, **kwargs):
        return self.visit(expr.tele, *args, **kwargs)

    def visit_sub(self, expr, *args, **kwargs):
        return self.visit(expr.lhs, *args, **kwargs) + \
               self.visit(expr.rhs, *args, **kwargs)

    def visit_box(self, expr, *args, **kwargs):
        return self.visit(expr.conv, *args, **kwargs) + \
               self.visit(expr.expr, *args, **kwargs) + \
               self.visit(expr.type, *args, **kwargs)

    def visit_mvar(self, expr, *args, **kwargs):
        return self.visit(expr.tele, *args, **kwargs)

    def visit_tele(self, expr, *args, **kwargs):
        tele_vars = [v for ty in expr.types\
                     for v in self.visit(ty, *args, **kwargs)]
        return tele_vars


def free_vars(expr):
    """returns the list of free variables of an expression
    
    Arguments:
    - `expr`:
    """
    l = FreeVars().visit(expr)
    return [e.name for e in l]


##############################################################################
#
# Global fresh variable generator for expressions
#
##############################################################################

fresh_name = vargen.VarGen()
