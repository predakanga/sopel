# coding=utf-8
"""
calc.py - Sopel Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2019, dgw, technobabbl.es
Licensed under the Eiffel Forum License 2.

https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import sys

from requests import get

from sopel.config.types import StaticSection, ValidatedAttribute
from sopel.module import commands, example
from sopel.tools.calculation import eval_equation

if sys.version_info.major < 3:
    from urllib import quote as _quote

    def quote(s):
        return _quote(s.encode('utf-8')).decode('utf-8')
else:
    from urllib.parse import quote

if sys.version_info.major >= 3:
    unichr = chr


class CalcSection(StaticSection):
    oblique_url = ValidatedAttribute('oblique_url',
        default='https://tumbolia-sopel.appspot.com/')
    """Full URL of the Oblique service instance to use for Python evaluation"""


def setup(bot):
    bot.config.define_section('calc', CalcSection)


@commands('c', 'calc')
@example('.c 5 + 3', '8')
@example('.c 0.9*10', '9')
@example('.c 10*0.9', '9')
@example('.c 2*(1+2)*3', '18')
@example('.c 2**10', '1024')
@example('.c 5 // 2', '2')
@example('.c 5 / 2', '2.5')
def c(bot, trigger):
    """Evaluate some calculation."""
    if not trigger.group(2):
        return bot.reply("Nothing to calculate.")
    # Account for the silly non-Anglophones and their silly radix point.
    eqn = trigger.group(2).replace(',', '.')
    try:
        result = eval_equation(eqn)
        result = "{:.10g}".format(result)
    except ZeroDivisionError:
        result = "Division by zero is not supported in this universe."
    except Exception as e:
        result = "{error}: {msg}".format(error=type(e), msg=e)
    bot.reply(result)


@commands('py')
@example('.py len([1,2,3])', '3')
def py(bot, trigger):
    """Evaluate a Python expression."""
    if not trigger.group(2):
        return bot.say("Need an expression to evaluate")

    query = trigger.group(2)
    uri = bot.config.calc.oblique_url + 'py/'
    answer = get(uri + quote(query)).content.decode('utf-8')
    if answer:
        # bot.say can potentially lead to 3rd party commands triggering.
        bot.reply(answer)
    else:
        bot.reply('Sorry, no result.')


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)
