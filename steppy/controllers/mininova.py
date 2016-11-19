# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from ..note import Note
from ..rules import RulesChain, Rule
from ..base_controller import BaseController
from ..helpers import msb_lsb_output, msb_lsb_rules_chain
from ..sequencer_events import SequencerEvents


class MiniNova(BaseController):

    def __init__(self, sequencer, port_name='MiniNova'):
        super(MiniNova, self).__init__(sequencer, port_name)

        self.sequencer.on(SequencerEvents.STEP_BEGIN, self, self.on_step_begin)
        self.sequencer.on(SequencerEvents.STEP_END, self, self.on_step_end)
        self.sequencer.on(SequencerEvents.PAUSE, self, self.on_pause)

        self.register('NOTE ON', self.on_note_on, RulesChain(Rule(type_='note_on', velocity='!0')))
        self.register('NOTE OFF #1', self.on_note_off, RulesChain(Rule(type_='note_on', velocity=0)))
        self.register('NOTE OFF #2', self.on_note_off, RulesChain(Rule(type_='note_off')))

        # https://d19ulaff0trnck.cloudfront.net/sites/default/files/novation/downloads/9558/mininova-cc-nprn-chart_0.pdf
        self.register('TEMPO', self.on_tempo_change, msb_lsb_rules_chain(2, '*', 63, '*'))
        for i in range(0, 8):
            self.register('ARPEG #%d on' % i, lambda msgs, i=i, **kw: self.on_arpeg(i, True), msb_lsb_rules_chain(60, msb_value=127, lsb=32+i))
            self.register('ARPEG #%d off' % i, lambda msgs, i=i, **kw: self.on_arpeg(i, False), msb_lsb_rules_chain(60, msb_value=0, lsb=32+i))

        # The problem with 'LATCH' button is that it also modifies the synth's output...
        """
        self.register('RESUME',
                      lambda *args, **kw: self.sequencer.resume(),
                      msb_lsb_rules_chain(0, 50, 122)
                     )

        self.register('PAUSE',
                      lambda *args, **kw: self.sequencer.pause(),
                      msb_lsb_rules_chain(0, 51, 122)
                     )"""

        self.register('FILTER', self.on_cc, RulesChain(Rule(type_='control_change', control='74')))

    def on_step_begin(self, step):
        self.sequencer.output(self, *msb_lsb_output(60, 0, 32 + step.pos))

    def on_step_end(self, step):
        self.sequencer.output(self, *msb_lsb_output(60, 127, 32 + step.pos))

    def on_pause(self, steps):
        for i, step in enumerate(steps.steps):
            self.sequencer.output(self,
                                  *msb_lsb_output(60, 127 if steps.current_step == step else 0, 32 + i))

    def on_note_on(self, msgs, **kw):
        self.sequencer.note_pressed(Note(numeric_note=msgs[0].note,
                                         velocity=msgs[0].velocity))

    def on_note_off(self, msgs, **kw):
        self.sequencer.note_release()

    def on_pad_pressed(self, i):
        print('>>>>>>>>>>> PAD %d PRESSED' % i)

    def on_arpeg(self, i, on):
        print('>>>>>>>>>>> ARPEG %d %s' % (i, 'on' if on else 'off'))
        self.sequencer.toggle_step(i)

    def on_tempo_change(self, msgs, **kw):
        _, _, msb, lsb = [msg.value for msg in msgs]
        bpm = msb * 128 + lsb
        self.sequencer.set_tempo(bpm)

    def on_cc(self, msgs, **kw):
        self.sequencer.set_step_cc(msgs[0].control, msgs[0].value)