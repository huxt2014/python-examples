

import argparse

################################################################################
#                                 basic usage
################################################################################

# get an parser instance
parser = argparse.ArgumentParser()

# configure parser
parser.add_argument('foo')            # positional arg
parser.add_argument('--bar')          # optional arg
parser.add_argument('-b', '--bar')    # optional arg with short version

# parse and get result
args = parser.parse_args()
print args.foo
print args.b

# print version
parser.add_argument('--version', action='version', version='%(prog)s 2.0')


################################################################################
#                                 sub-commands
################################################################################
# get an hub for sub-commands
subparsers = parser.add_subparsers()

# add a parser for each sub-command
parser_foo = subparsers.add_parser('foo')
parser_foo.add_argument('-x')

parser_bar = argparse.ArgumentParser()
subparsers._name_parser_map['bar'] = parser_bar


# bound function for sub-command by setting default
def f_foo(*args):
    print args


def f_bar(*args):
    print args

parser_foo.set_defaults(func=f_foo)
parser_bar.set_defaults(func=f_bar)

args = parser.parse_args()
args.func(args)

# bound function for sub-command by setting dest
subparsers2 = parser.add_subparsers(dest='subcommand')
args = parser.parse_args()
if args.subcommand == 'foo':
    f_foo(args)
elif args.subcommand == 'bar':
    f_bar(args)
