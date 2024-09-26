# -*- coding: utf-8 -*-
"""
Script to convert the political bias and factual reporting dataset to ground-truth rewards

Copyright 2024 Idiap Research Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Sergio Burdisso (sergio.burdisso@idiap.ch)
"""
import os
import logging
import argparse
import pandas as pd

logging.basicConfig(format='[%(asctime)s] (%(levelname)s) %(message)s')
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(prog="Convert the political bias and factual reporting dataset to ground-truth rewards")
parser.add_argument("-i", "--input-file", help="Path to mbfc.csv file", default="data/mbfc.csv")
parser.add_argument("-o", "--output-folder", help="Folder to store the ground-truth reward files", default="data/rewards/")
args = parser.parse_args()


BIAS2REWARDS = {
    "left": -1,
    "left-center": -0.5,
    "neutral": 0,
    "right-center": 0.5,
    "right": 1
}

FACT2REWARDS = {
    "low": -1,
    "mixed": 0,
    "high": 1
}


df = pd.read_csv(args.input_file)
df.bias = df.bias.map(BIAS2REWARDS.get)
df.bias.value_counts()

df.factual_reporting = df.factual_reporting.map(FACT2REWARDS.get)
df.factual_reporting.value_counts()

os.makedirs(args.output_folder, exist_ok=True)
for prop in ["bias", "factual_reporting"]:
    SOURCE2LABEL = {}
    for _, row in df.iterrows():
        if row[prop] is None:
            continue
        SOURCE2LABEL[row.source] = row[prop]

    df_true = pd.DataFrame.from_records(list(SOURCE2LABEL.items()), columns=['domain', 'reliability_label'])
    df_true["wiki_citation"] = 0
    df_true.dropna(inplace=True)
    output_path = os.path.join(args.output_folder, f"golden_truth_dataset-{prop}.csv")
    df_true.to_csv(output_path, index=False)
    logger.info(f"Ground truth rewards files for '{prop}' saved in '{output_path}'")
