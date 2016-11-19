# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from steppy.steps import Steps
from steppy.sequencer import Sequencer
from steppy.tempo import Tempo
from steppy.controllers.launchcontrol import LaunchControl


def get_launchcontrol():
    steps = Steps()
    tempo = Tempo()
    seq = Sequencer(steps, tempo)
    lc = LaunchControl(seq)
    return lc


def test_rotaries():
    lc = get_launchcontrol()
    rotary_8_rules_chain = lc.get_rules_chain_by_name('ROTARIES: FIRST ROW #8')

    last_msg = Message('control_change', channel=8, control=28, value=65)
    lc.handle_message(last_msg)
    print(rotary_8_rules_chain.rules)
    assert rotary_8_rules_chain.full_match
    assert last_msg in rotary_8_rules_chain.matched_messages

    print('------')

    last_msg = Message('control_change', channel=8, control=28, value=66)
    lc.handle_message(last_msg)
    print(rotary_8_rules_chain.rules)
    assert rotary_8_rules_chain.full_match
    assert last_msg in rotary_8_rules_chain.matched_messages