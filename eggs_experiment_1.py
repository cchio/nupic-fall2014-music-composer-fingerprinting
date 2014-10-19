#!/usr/bin/python

# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
import csv
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic_output import NuPICFileOutput, NuPICPlotOutput
from nupic.swarming import permutations_runner


def swarm_over_data(input_file):
  SWARM_DEF = "search_def.json"
  SWARM_CONFIG = {
  "includedFields": [
    {
      "fieldName": "pitch",
      "fieldType": "float",
      "maxValue": 12.0,
      "minValue": 0.0
    }
  ],
  "streamDef": {
    "info": "eggs",
    "version": 1,
    "streams": [
      {
        "info": input_file,
        "source": "file://"+input_file,
        "columns": [
          "*"
        ]
      }
    ]
  },
  "inferenceType": "TemporalAnomaly",
  "inferenceArgs": {
    "predictionSteps": [
      1
    ],
    "predictedField": "pitch"
  },
  "swarmSize": "medium"
  }
  return permutations_runner.runWithConfig(SWARM_CONFIG,
    {'maxWorkers': 8, 'overwrite': True})


def generate_data(input_file):
  import generate_data
  generate_data.run(input_file)

def build_model(input_file):
  model_params = swarm_over_data(input_file)
  model = ModelFactory.create(model_params)
  model.enableInference({"predictedField": "pitch"})
  return model

def run_model(input_file, output_file, model, train=False, plot=True):
  if plot:
    output = NuPICPlotOutput(output_file, show_anomaly_score=True)
  else:
    output = NuPICFileOutput(output_file, show_anomaly_score=True)

  if train:
    print "Enable learning."
    model.enableLearning()
  else:
    print "Not for training. Disabling learning."
    model.disableLearning()

  with open(input_file, "rb") as eggs_input:
    csv_reader = csv.reader(eggs_input)

    # skip header rows
    csv_reader.next()
    csv_reader.next()
    csv_reader.next()

    # the real data
    for row in csv_reader:
      twelvth_beat = float(row[0])
      pitch_value = float(row[1])
      result = model.run({"pitch": pitch_value})
      output.write(twelvth_beat, pitch_value, result, prediction_step=1)

  output.close()



if __name__ == "__main__":
  run_sine_experiment()
