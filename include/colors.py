import colorful as cf

cf.use_true_colors()


def print_yellow(*args, **kwargs):
    print(cf.yellow(*args, **kwargs))


def print_orange(*args, **kwargs):
    print(cf.orange(*args, **kwargs))


def print_green(*args, **kwargs):
    print(cf.green(*args, **kwargs))


def print_red(*args, **kwargs):
    print(cf.red(*args, **kwargs))


def print_cyan(*args, **kwargs):
    print(cf.cyan(*args, **kwargs))


def input_yellow(*args, **kwargs):
    return input(cf.yellow(*args, **kwargs))


def input_orange(*args, **kwargs):
    return input(cf.orange(*args, **kwargs))


def input_green(*args, **kwargs):
    return input(cf.green(*args, **kwargs))


def input_red(*args, **kwargs):
    return input(cf.red(*args, **kwargs))