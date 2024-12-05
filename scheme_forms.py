from scheme_eval_apply import *
from scheme_utils import *
from scheme_classes import *
from scheme_builtins import *

#################
# Special Forms #
#################

# Each of the following do_xxx_form functions takes the cdr of a special form as
# its first argument---a Scheme list representing a special form without the
# initial identifying symbol (if, lambda, quote, ...). Its second argument is
# the environment in which the form is to be evaluated.

def do_define_form(expressions, env):
    """Evaluate a define form.
    >>> env = create_global_frame()
    >>> do_define_form(read_line("(x 2)"), env) # evaluating (define x 2)
    'x'
    >>> scheme_eval("x", env)
    2
    >>> do_define_form(read_line("(x (+ 2 8))"), env) # evaluating (define x (+ 2 8))
    'x'
    >>> scheme_eval("x", env)
    10
    >>> # problem 10
    >>> env = create_global_frame()
    >>> do_define_form(read_line("((f x) (+ x 2))"), env) # evaluating (define (f x) (+ x 8))
    'f'
    >>> scheme_eval(read_line("(f 3)"), env)
    5
    """
    validate_form(expressions, 2) # Checks that expressions is a list of length at least 2
    signature = expressions.first
    if scheme_symbolp(signature):
        # assigning a name to a value e.g. (define x (+ 1 2))
        validate_form(expressions, 2, 2) # Checks that expressions is a list of length exactly 2
        # BEGIN PROBLEM 4
        value = scheme_eval(expressions.rest.first, env)
        env.define(signature, value) #Bind symbol to value
        return signature #returning the symbol
        # END PROBLEM 4
    elif isinstance(signature, Pair) and scheme_symbolp(signature.first):
        # defining a named procedure e.g. (define (f x y) (+ x y))
        # BEGIN PROBLEM 10
        "*** YOUR CODE HERE ***"
        # END PROBLEM 10
    else:
        bad_signature = signature.first if isinstance(signature, Pair) else signature
        raise SchemeError('non-symbol: {0}'.format(bad_signature))

def do_quote_form(expressions, env):
    """Evaluate a quote form.

    >>> env = create_global_frame()
    >>> do_quote_form(read_line("((+ x 2))"), env) # evaluating (quote (+ x 2))
    Pair('+', Pair('x', Pair(2, nil)))
    """
    validate_form(expressions, 1, 1)
    # BEGIN PROBLEM 5
    return expressions.first #returns the operand
    # END PROBLEM 5

def do_begin_form(expressions, env):
    """Evaluate a begin form.

    >>> env = create_global_frame()
    >>> x = do_begin_form(read_line("((print 2) 3)"), env) # evaluating (begin (print 2) 3)
    2
    >>> x
    3
    """
    validate_form(expressions, 1)
    return eval_all(expressions, env)

def do_lambda_form(expressions, env):
    """Evaluate a lambda form.

    >>> env = create_global_frame()
    >>> do_lambda_form(read_line("((x) (+ x 2))"), env) # evaluating (lambda (x) (+ x 2))
    LambdaProcedure(Pair('x', nil), Pair(Pair('+', Pair('x', Pair(2, nil))), nil), <Global Frame>)
    """
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    # BEGIN PROBLEM 7
    "*** YOUR CODE HERE ***"
    # END PROBLEM 7

def do_if_form(expressions, env):
    """Evaluate an if form.

    >>> env = create_global_frame()
    >>> do_if_form(read_line("(#t (print 2) (print 3))"), env) # evaluating (if #t (print 2) (print 3))
    2
    >>> do_if_form(read_line("(#f (print 2) (print 3))"), env) # evaluating (if #f (print 2) (print 3))
    3
    """
    validate_form(expressions, 2, 3)
    if is_scheme_true(scheme_eval(expressions.first, env)):
        return scheme_eval(expressions.rest.first, env)
    elif len(expressions) == 3:
        return scheme_eval(expressions.rest.rest.first, env)


def do_and_form(expressions, env):
    # base case and
    if expressions is nil:
        return True
    front_sche = scheme_eval(expressions.first, env)
    if is_scheme_true(front_sche):
        if expressions.rest is nil:
            return front_sche
        else:
            return do_and_form(expressions.rest, env)
    else:
        return front_sche

def do_or_form(expressions, env):
    # base case or
    if expressions is nil:
        return False
    front_sche = scheme_eval(expressions.first, env)
    if is_scheme_false(front_sche):
        if expressions.rest is nil:
            return front_sche
        else:
            return do_or_form(expressions.rest, env)
    else:
        return front_sche


def do_cond_form(expressions, env):
    """Evaluate a cond form."""
    while expressions is not nil:
        clause = expressions.first
        validate_form(clause, min=1)
        predicate = clause.first
        if predicate == 'else':
            if clause.rest is nil:
                return True
            return eval_all(clause.rest, env)
        result = scheme_eval(predicate, env)
        if is_scheme_true(result):
            if clause.rest is nil:
                return result
            return eval_all(clause.rest, env)
        expressions = expressions.rest
    return None

def do_let_form(expressions, env):
    """Evaluate a let form.

    >>> env = create_global_frame()
    >>> do_let_form(read_line("(((x 2) (y 3)) (+ x y))"), env)
    5
    """
    validate_form(expressions, 2)
    let_env = make_let_frame(expressions.first, env)
    return eval_all(expressions.rest, let_env)

def make_let_frame(bindings, env):
    """Create a child frame of env that binds symbols to values."""
    symbols = nil
    values = nil
    
    while bindings is not nil:
        binding = bindings.first
        validate_form(binding, 2, 2)
        symbol = binding.first
        expression = binding.rest.first
        symbols = Pair(symbol, symbols)
        values = Pair(scheme_eval(expression, env), values)
        bindings = bindings.rest
    
    validate_formals(symbols)
    return env.make_child_frame(symbols, values)



def do_quasiquote_form(expressions, env):
    """Evaluate a quasiquote form with parameters EXPRESSIONS in
    Frame ENV."""
    def quasiquote_item(val, env, level):
        """Evaluate Scheme expression VAL that is nested at depth LEVEL in
        a quasiquote form in Frame ENV."""
        if not scheme_pairp(val):
            return val
        if val.first == 'unquote':
            level -= 1
            if level == 0:
                expressions = val.rest
                validate_form(expressions, 1, 1)
                return scheme_eval(expressions.first, env)
        elif val.first == 'quasiquote':
            level += 1

        return val.map(lambda elem: quasiquote_item(elem, env, level))

    validate_form(expressions, 1, 1)
    return quasiquote_item(expressions.first, env, 1)

def do_unquote(expressions, env):
    raise SchemeError('unquote outside of quasiquote')


#################
# Dynamic Scope #
#################

def do_mu_form(expressions, env):
    """Evaluate a mu form."""
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    # BEGIN PROBLEM 11
    "*** YOUR CODE HERE ***"
    # END PROBLEM 11



SPECIAL_FORMS = {
    'and': do_and_form,
    'begin': do_begin_form,
    'cond': do_cond_form,
    'define': do_define_form,
    'if': do_if_form,
    'lambda': do_lambda_form,
    'let': do_let_form,
    'or': do_or_form,
    'quote': do_quote_form,
    'quasiquote': do_quasiquote_form,
    'unquote': do_unquote,
    'mu': do_mu_form,
}