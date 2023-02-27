#!/usr/bin/env python3

from opentrons import protocol_api

metadata = {'apiLevel': '2.13'}

def run(protocol: protocol_api.ProtocolContext):
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    nest = protocol.load_labware('nest_12_reservoir_15ml',2)
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack])

    rows = ['A','B','C','D','E','F','G','H']
    cols = range(1,12)

    for row in rows:
        for col in cols:
            dest = row + str(col)
            p300.transfer(100, nest.wells()[col], plate[dest])
