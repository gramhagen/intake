import functools
import itertools
from jinja2 import Environment, meta, Template
import sys


def flatten(iterable):
    """Flatten an arbitrarily deep list"""
    iterable = iter(iterable)
    while True:
        try:
            item = next(iterable)
        except StopIteration:
            break

        if isinstance(item, (str, bytes)):
            yield item
            continue

        try:
            data = iter(item)
            iterable = itertools.chain(data, iterable)
        except:
            yield item


def reload_on_change(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.changed:
            self.reload()
        return f(self, *args, **kwargs)

    return wrapper


def clamp(value, lower=0, upper=sys.maxsize):
    """Clamp float between given range"""
    return max(lower, min(upper, value))


def make_prefix_tree(flat_dict):
    """Convert a dictionary with keys of dotted strings into nested dicts with common prefixes.

    Ex: { 'abc.xyz': 1, 'abc.def': 2, 'www': 3} is converted to:
        { 'abc': {'xyz': 1, 'def': 2}, 'www': 3 }
    """
    tree = {}
    for key, value in flat_dict.items():
        subtree = tree
        parts = key.split('.')
        for part in parts[:-1]:
            if part not in subtree:
                subtree[part] = {}
            subtree = subtree[part]
        subtree[parts[-1]] = value

    return tree


def expand_templates(pars, context, return_left=False):
    """
    Render variables in context into the set of parameters with jinja2

    Parameters
    ----------
    pars: dict
        values are strings containing some jinja2 controls
    context: dict
        values to use while rendering
    return_left: bool
        whether to return the set of variables in context that were not used
        in rendering parameters

    Returns
    -------
    dict with the same keys as ``pars``, but updated values; optionally also
    return set of unused parameter names.
    """
    all_vars = set(context)
    out = {}
    for k, v in pars.items():
        ast = Environment().parse(v)
        all_vars -= meta.find_undeclared_variables(ast)
        out[k] = Template(v).render(context)
    if return_left:
        return out, all_vars
    return out
