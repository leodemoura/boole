# -*- coding: utf-8 -*-

#############################################################################
#
# groups.py
#
# description: A possible implementation of the Group module
#
#
# Authors:
# Cody Roux
#
# WARNING: execution of this file is very slow!
#
##############################################################################

import boole.core.tactics as tac
from boole import *


if __name__ == '__main__':

    set_verbose()

    X = deftype('X')
    
    el = defconst('el', X)

    op = defconst('op', X >> (X >> X))

    x, y, z = X('x y z')

    One = defclass('One', [X, el], true)

    definstance('One_int', One(Int, 1), triv())

    one_inst = defconst('one_inst', One(X, el))

    one = defexpr('one', abst([X, el, one_inst], el), \
                  pi([X, el, one_inst], X, impl=True))

    op_mul = defconst('op_mul', Mul(X, op))

    el_one = defconst('el_one', One(X, el))

    Unit_left = defclass('Unit_left', [X, op, el, op_mul, el_one], \
                         forall(x, one() * x == x))

    Unit_right = defclass('Unit_right', [X, op, el, op_mul, el_one], \
                         forall(x, x * one() == x))

    Assoc = defclass('Assoc', [X, op, op_mul], \
                     forall([x, y, z], (x * y) * z == x * (y * z)))

    G = deftype('G')

    G_mul = defconst('G_mul', G >> (G >> G))

    G_one = defconst('G_one', G)

    g = G('g')

    G_unit_l = defconst('G_unit_l', forall(g, G_mul(G_one, g) == g))

    G_unit_r = defconst('G_unit_r', forall(g, G_mul(g, G_one) == g))

    g1, g2, g3 = G('g1 g2 g3')

    G_assoc = defconst('G_assoc',
                       forall([g1, g2, g3], G_mul(G_mul(g1, g2), g3) == G_mul(g1, G_mul(g2, g3))))

    grp_def = sig([G, G_mul, G_one, G_unit_l, G_unit_r, G_assoc], true)

    Grp = defexpr('Grp', grp_def)

    grp = defconst('grp', Grp)

    grp_carr = defexpr('grp_carr', abst(grp, cast(grp, grp_def)[0]), pi(grp, Type), unfold=['Grp'])

    op_cast = cast(cast(grp, grp_def)[1][0], grp_carr(grp) >> (grp_carr(grp) >> grp_carr(grp)))

    grp_op = defexpr('grp_op', abst(grp, op_cast), unfold=['Grp', 'grp_carr'])


    definstance('Mul_grp', forall(grp, Mul(grp_carr(grp), grp_op(grp))), triv())

    one_cast = cast(cast(grp, grp_def)[1][1][0], grp_carr(grp))

    grp_one = defexpr('grp_one', abst(grp, one_cast), unfold=['Grp', 'grp_carr'])

    definstance('One_grp', forall(grp, One(grp_carr(grp), grp_one(grp))), triv())

    definstance('Unit_left_grp',
                forall(grp, Unit_left(grp_carr(grp),
                                  grp_op(grp),
                                  grp_one(grp),
                                  triv(),
                                  triv())),
                triv())


    goal = current_ctxt().next_goal()

    goal.interact(tac.par(tac.trytac(unif.instances)))

    goal.interact(tac.unfold('Grp'))

    goal.interact(tac.unpack('grp'))

    #grp_carr is invisible!
    #it appears in an implicit argument.
    goal.interact(tac.unfold('*', 'one', 'grp_carr', 'grp_op', 'grp_one') >> tac.simpl(conv.beta_norm))

    goal.interact(unif.fast_apply(goal[0]['G_unit_l']))

    # goal.interact(unif.unify >> tac.par(tac.trivial))

    definstance('Unit_right_grp',
                forall(grp, Unit_right(grp_carr(grp),
                                  grp_op(grp),
                                  grp_one(grp),
                                  triv(),
                                  triv())),
                triv())


    goal = current_ctxt().next_goal()

    goal.interact(tac.par(tac.trytac(unif.instances)))

    goal.interact(tac.unfold('Grp'))

    goal.interact(tac.unpack('grp'))

    #grp_carr is invisible!
    #it appears in an implicit argument.
    goal.interact(tac.unfold('*', 'one', 'grp_carr', 'grp_op', 'grp_one') >> tac.simpl(conv.beta_norm))

    goal.interact(unif.fast_apply(goal[0]['G_unit_r']))

    # goal.interact(unif.unify >> tac.par(tac.trivial))

    definstance('Assoc_grp',
                forall(grp, Assoc(grp_carr(grp),
                             grp_op(grp),
                             triv())),
                triv())
    
    goal = current_ctxt().next_goal()

    goal.interact(tac.par(tac.trytac(unif.instances)))

    goal.interact(tac.unfold('Grp'))

    goal.interact(tac.unpack('grp'))

    goal.interact(tac.unfold('*', 'one', 'grp_carr', 'grp_op', 'grp_one')
                  >> tac.simpl(conv.beta_norm))

    goal.interact(unif.fast_apply(goal[0]['G_assoc']))

    # goal.interact(unif.unify >> tac.par(tac.trivial))

    g = defconst('g', grp_carr(grp))
    h = defconst('h', grp_carr(grp))

    defhyp('toto', g * h == (one() * g) * h)

