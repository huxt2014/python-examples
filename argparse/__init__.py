
"""
for command-line input parsing
"""

# get an parser instance ########################################
import argparse

parser = argparse.ArgumentParser()



# configure parser ##############################################

## store the value as default action
##     Only store one value.
##     Required options are generally considered bad form for optional arg.
##     If the nargs keyword argument is not provided, the number of arguments 
## consumed is determined by the action.
parser.add_argument('foo')            # positional arg
parser.add_argument('--bar')          # optional arg
parser.add_argument('-b', '--bar')    # optional arg with short version

## print version
parser.add_argument('--version', action='version', version='%(prog)s 2.0')

## parse and get result
args = parser.parse_args()
args.foo
args.b



# configure sub-commands ########################################

## get an action object for sub-commands
subparsers = parser.add_subparsers()
subparsers = parser.add_subparsers(dest='subcommand')

## add a parser for each sub-command
parser_foo = subparsers.add_parser('foo')
parser_foo.add_argument('-x')

parser_bar = subparsers.add_parser('bar')
parser_bar.add_argument('-y')

## bound function for sub-command by setting default 
parser_foo.set_defaults(func=f_foo)
parser_bar.set_defaults(func=f_bar)

args = parser.parse_args()
args.func(args)

## bound function for sub-command by setting dest
args = parser.parse_args()
if args.subcommand == 'foo':
    f_foo(args)
elif args.subcommand == 'bar':
    f_bar(args)


