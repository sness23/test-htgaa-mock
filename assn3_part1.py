from opentrons import types
import math
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd

metadata = {
    'protocolName': 'Image printer',
    'author': 'Steven Ness',
    'source': 'HTGAA 2023',
    'apiLevel': '2.9'
}

def run(protocol):
  tips_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', 3, 'Opentrons 20uL Tips')
  temperature_module = protocol.load_module('temperature module gen2', 9)
  source_plate = temperature_module.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', label='Cold Plate')
  agar_plate = protocol.load_labware('htgaa_agar_plate', 1, 'Agar Plate')  ## TA MUST CALIBRATE EACH PLATE!
  pipette_20ul = protocol.load_instrument("p20_single_gen2", "right", tip_racks=[tips_20ul])

  pipette_20ul.starting_tip = tips_20ul.well('A1')
  center_location = agar_plate['A1'].top()

  #url = 'https://raw.githubusercontent.com/Minikaw/Microbial_Earth_Coordinates/main/ResultsMicrobialWorld_final.csv'
  url = "marilyn.csv"
  world_coord = pd.read_csv(url)
  data = world_coord
  data.columns = ["x", "y"]
  y_inverted = np.amax(data['y'])-data['y']
  raw_x_min = np.amin(data['x'])
  raw_x_max = np.amax(data['x'])
  raw_y_min = np.amin(y_inverted)
  raw_y_max = np.amax(y_inverted)
  world_coord_x_shifted = data['x']-((raw_x_min + raw_x_max)/2)
  world_coord_y_shifted = y_inverted-((raw_y_min + raw_y_max)/2)
  all_distances_to_center = np.sqrt(np.square(world_coord_x_shifted) + np.square(world_coord_y_shifted));
  world_coord_x_85mm_shifted = 30/np.amax(all_distances_to_center)*world_coord_x_shifted;
  world_coord_y_85mm_shifted = 30/np.amax(all_distances_to_center)*world_coord_y_shifted;
  center_location = agar_plate['A1'].top()
  cell_well = source_plate['A1']

  pipette_20ul.pick_up_tip()

  for i in range(len(world_coord_x_85mm_shifted)):
    if i%20 == 0:
      pipette_20ul.aspirate(20, cell_well)

    adjusted_location = center_location.move(types.Point(world_coord_x_85mm_shifted[i], world_coord_y_85mm_shifted[i]))
    pipette_20ul.dispense(1, adjusted_location)
    hover_location = adjusted_location.move(types.Point(z = 2))
    pipette_20ul.move_to(hover_location)

  pipette_20ul.drop_tip()
