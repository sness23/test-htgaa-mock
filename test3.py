from opentrons import types
import math
import matplotlib.pyplot as plt

import re

plt.rcParams["figure.figsize"] = (10,10)

def mock_print(str):
    #print("...\n" + str)
    pass

class PipetteSim:
  droplets_x = []
  droplets_y = []
  total_volume = 0
  curr_color = 'red'

  def __init__(self):
    self.droplets_x = []
    self.droplets_y = []
    self.colors = []
    self.total_volume = 0
    self.curr_color = 'red'

  def dispense(self, vol, loc):
    self.droplets_x.append(loc.point.x)
    self.droplets_y.append(loc.point.y)
    self.colors.append(self.curr_color)

  def aspirate(self, vol, loc):
    self.total_volume += vol
    self.curr_color = loc.color()

  def pick_up_tip(self):
    pass 

  def drop_tip(self):
    pass 

  def move_to(self, loc):
    pass
    

  def visualize(self):
    print()
    print("### Total Volume used: ", self.total_volume, "uL ###")
    print()
    plt.scatter(0, 0, s=112*50*50, c='#d7ca95') # agar plate
    plt.scatter(self.droplets_x, self.droplets_y, s=100, c=self.colors)

    plt.xlim((-46, 46))
    plt.ylim((-46, 46))
    plt.show()


class WellMock:
    labware = ""
    well_id = ""
    well_color = "purple"

    def __init__(self, well_id, well_color, labware):
        self.well_id = well_id
        self.labware = labware
        self.well_color = well_color if well_color else 'purple'

    def get_row_col(self):
        row = ord(self.well_id[0].upper())
        col = int(self.well_id[1])
        return (row, col)

    def set_row_col(self, row, col):
        self.well_id = chr(row) + str(col)

    def bottom(self, z):
        assert z >= 0
        return self

    def center(self):
        return self

    def color(self):
        return self.well_color

    def top(self, z=0):
        assert(isinstance(z, (int, float)))
        return types.Location(types.Point(x=0, y=0, z=0), 'Well')
        # return self

    def move(self, loc):
        assert(isinstance(loc, PointMock))
        return self

    def __repr__(self):
        return self.well_id



class LabwareMock:
    labware = ""
    slot = ""
    label = ""

    def __init__(self, labware, slot, label, color_by_well):
        self.labware = labware
        self.slot = slot
        self.label = label
        self.color_by_well = color_by_well

    def well(self, well_id):
        return WellMock(well_id, self.color_by_well.get(well_id, ''), self)

    def __getitem__(self, well_id):
        return WellMock(well_id, self.color_by_well.get(well_id, ''), self)

    def __repr__(self):
        return "Deck Slot %s - %s" % (str(self.slot), self.label)


class ModuleMock:
    module = ""
    slot = 0
    color_by_well = {}

    def __init__(self, module, slot, color_by_well):
        self.module = module
        self.slot = slot
        self.color_by_well = color_by_well

    def load_labware(self, labware, label):
        mock_print("Module " + str(self.module) + " loaded " + str(labware))
        return LabwareMock(labware, self.slot, label, color_by_well)

    def set_temperature(self, temp):
        assert(isinstance(temp, int))
        assert(temp >= 4 and temp <= 110)
        mock_print("Setting temperature to " + str(temp) + "C")

    def open_lid(self):
        mock_print("Opening lid")

    def close_lid(self):
        mock_print("Closing lid")

    def set_lid_temperature(self, temp):
        assert(isinstance(temp, int))
        assert(temp >= 4 and temp <= 110)
        mock_print("Setting lid temperature to " + str(temp) + "C")

    def deactivate_lid(self):
        mock_print("Deactivate lid")

    def set_block_temperature(self, temp, hold_time_minutes=0, hold_time_seconds=0, block_max_volume=50):
        assert(isinstance(temp, int))
        assert(temp >= 4 and temp <= 110)
        assert(isinstance(hold_time_minutes, int))
        assert(isinstance(block_max_volume, int))
        mock_print("Setting block temperature to " + str(temp) + "C")
        if (hold_time_minutes > 0):
            mock_print("Holding for " + str(hold_time_minutes) + " minutes...")
        if (hold_time_seconds > 0):
            mock_print("Holding for " + str(hold_time_seconds) + " seconds...")

    def execute_profile(self, steps, repetitions, block_max_volume):
        assert(isinstance(repetitions, int))
        assert(isinstance(block_max_volume, int))

        mock_print("Executing following protocol for " + str(repetitions) + " cycles")

        for step in steps:
            assert(isinstance(step, dict))
            assert(isinstance(step['temperature'], int))
            assert(isinstance(step['hold_time_seconds'], int))

            mock_print("Temperature: " + str(step['temperature']) + "C, Time: " + str(step['hold_time_seconds']) + " seconds")



class InstrumentMock:
    instrument = ""
    mount = ""
    label = ""
    starting_tip = None
    vol_range = (0, 1000)

    def __init__(self, instrument, mount, tip_racks):
        self.instrument = instrument
        self.mount = mount

        if "p20" in instrument:
            self.label = "P20"
            self.vol_range = (1, 20)
        elif "p300" in instrument:
            self.label = "P300"
            self.vol_range = (20, 300)
        elif "p1000" in instrument:
            self.label = "P1000"
            self.vol_range = (100, 1000)
        else:
            mock_print("WARNING: UNSUPPORTED PIPETTE")
            assert false

    def advance_tip(self):
        row, col = self.starting_tip.get_row_col()

        row += 1
        if row > ord('H'):
            row = ord('A')
            col += 1

        if col > 12:
            mock_print("WARNING: OUT OF TIPS!!!")
            assert false

        self.starting_tip.set_row_col(row, col)

    def pick_up_tip(self):
        row, col = self.starting_tip.get_row_col()
        assert(row >= ord('A') and row <= ord('H'))
        assert(col >= 1 and col <= 12)
        mock_print(self.label + " is picking up a tip from " + str(self.starting_tip))
        self.advance_tip()

    def drop_tip(self):
        mock_print(self.label + " is dropping a tip");

    def aspirate(self, volume, well):
        assert(isinstance(volume, (int, float)))
        assert(isinstance(well, WellMock))
        assert volume >= self.vol_range[0] and volume <= self.vol_range[1]
        mock_print("##### " + str(well.labware) + " [" + str(well.well_id) + "] ---> (" + str(volume) + "uL)")

    def dispense(self, volume, well):
        assert(isinstance(volume, (int, float)))
        assert(isinstance(well, WellMock))
        assert volume >= self.vol_range[0] and volume <= self.vol_range[1]
        mock_print("##### " + str(well.labware) + " [" + str(well.well_id) + "] <--- (" + str(volume) + "uL)")

    def blow_out(self):
        mock_print(self.label + " blow out")

    def mix(self, repetitions, volume, well):
        assert(isinstance(repetitions, int))
        assert(isinstance(volume, (int, float)))
        assert(isinstance(well, WellMock))
        assert volume >= self.vol_range[0] and volume <= self.vol_range[1]
        mock_print("##### " + str(well.labware) + " [" + str(well.well_id) + "] - Mixing - " + str(repetitions) + " times, volume " + str(volume) + "uL")

    def move_to(self, loc, force_direct=False):
        assert(isinstance(force_direct, bool))
        assert(isinstance(loc, WellMock))
        mock_print(self.label + " is moving");


class OpenTronsMock:
    pipette = None
    color_by_well = {}

    def __init__(self, color_by_well):
        self.color_by_well = color_by_well

    def home(self):
        mock_print("Going home!")

    def load_labware(self, labware, slot, label):
        mock_print("Loaded " + str(labware) + " in deck slot " + str(slot))
        return LabwareMock(labware, slot, label, self.color_by_well)

    def load_module(self, module, slot=0):
        mock_print("Loaded module " + str(module) + " in deck slot " + str(slot))
        return ModuleMock(module, slot, self.color_by_well)

    def load_instrument(self, instrument, mount, tip_racks):
        self.pipette = PipetteSim()
        return self.pipette

    def pause(self):
        mock_print("Robot pause")

    def visualize(self):
        self.pipette.visualize()


import numpy as np
import pandas as pd

from opentrons import types

metadata = {
    'protocolName': 'HTGAA Robotic Patterning',
    'author': 'HTGAA',
    'source': 'HTGAA 2022',
    'apiLevel': '2.9'
}


def run(protocol):
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1, "Corning")
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2, "Opentrons")
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_1])
    p300.transfer(100, plate['A1'], plate['B1'])

color_by_well = {
    'A1' : 'purple'
}

protocol = OpenTronsMock(color_by_well)

run(protocol)

protocol.visualize()
