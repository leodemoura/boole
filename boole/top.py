#############################################################################
#
# top.py
#
# description: The top-level environment in which to play around
#
#
# Authors:
# Cody Roux
# Jeremy Avigad
#
##############################################################################

from boole.elab.terms import *
from boole.core.expr import Mvar
import boole.elab.unif as unif


if __name__ == '__main__':

    set_verbose()


    x = Real('x')

    i = Int('i')

    defexpr('_', i + x)
    defexpr('_', x + i)
    defexpr('_', i + i)
    
    Nat = deftype('Nat')
    defsub('nat_sub_int', Nat <= Int)

    n = Nat('n')

    add_nat = defconst('add_nat', Nat >> (Nat >> Nat))

    definstance('Add_nat', Add(Nat, add_nat), triv())

    defexpr('_', n + n)

    defexpr('_', n + i)

    defexpr('_', x + (i + n))

    defexpr('_', (i + n) + x)

    defexpr('_', (x + n) + i)

    Rat = deftype('Rat')
    
    defsub('int_sub_rat', Int <= Rat)
    defsub('rat_sub_real', Rat <= Real)

    add_rat = defconst('add_rat', Rat >> (Rat >> Rat))

    definstance('Add_rat', Add(Rat, add_rat), triv())

    q = Rat('q')

    defexpr('_', (q + n) + x)

    defexpr('_', (i + q) + x)

    defexpr('_', x + (n + q))

    m1 = Mvar('m1', Type)
    m2 = Mvar('m2', Type)
    m3 = Mvar('m3', Type)
    m4 = Mvar('m4', Type)
    A = deftype('A')
    B = deftype('B')
    f = defconst('f', pi(A, A >> Bool))

    a = const('a', m1)
    
    print a.type._value
    print
    t, ty, g = elaborate(abst([A, B, a], f(B, a)), None, None)
    print t, ":", ty
    print
    print g
    
    print a.type._value
    print
    print ", ".join(map(str, a.type.pending))

    a = const('a', m2)

    print
    print a.type._value
    print
    t, ty, g = elaborate(abst([A, a, B], f(B, a)), None, None)
    print t, ":", ty
    print
    print g
    
    print a.type._value
    print
    print ", ".join(map(str, a.type.pending))

    a = const('a', m3)

    b = B('b')
    print
    tm = abst([A, a], a) == abst([B, b], b)
    ty, g = mvar_infer(tm, ctxt=local_ctxt)
    print 'ty =', ty
    print
    print g
    g.interact(unif.solve_mvar)
    g.interact(unif.sub_mvar)
    g.interact(unif.destruct >> unif.par(unif.trivial))
    g.interact(unif.destruct)
    g.interact(unif.solve_mvar >> unif.par(unif.sub_mvar) >> unif.par(unif.trivial))

    tm = sub_mvar(tm, undef=True)

    print tm.arg.body.to_string_raw()
    print tm.fun.arg.body.to_string_raw()
    print tm.arg.body.equals(tm.fun.arg.body)
    print tm.fun.fun.arg.to_string()

    typing.infer(tm, ctxt=local_ctxt)

    
