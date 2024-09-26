# -*- coding: utf-8 -*-
"""
Script to scrape all news media annotation available at mediabiasfactcheck.com

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
import re
import time
import logging
import requests
import unicodedata
import pandas as pd

from tqdm import tqdm
from tldextract import extract
from bs4 import BeautifulSoup, SoupStrainer

logging.basicConfig(format='[%(asctime)s] (%(levelname)s) %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://mediabiasfactcheck.com"
OUTPUT_FILE_NAME = f"data/mbfc_raw-{int(time.time())}" # CSV file name
MBFC_BIAS_CATEGORY = ["center", "left", "leftcenter", "right-center",
                      "right", "conspiracy", "fake-news", "pro-science", "satire"]
CORR_COLUMNS = ["factual_reporting", "mbfc_credibility_rating", "nela_gt_label", "bias", "press_freedom", "popularity"]


def check_response_ok(r):
    if r.status_code != 200:
        logger.warning(f"{target_url} -> response status: {r.status_code} (skipping)")
        return False
    if "html" not in r.headers['content-type']:
        logger.warning(f"{target_url} -> non-html content-type found: {r.headers['content-type']} (skipping)")
        return False
    return True


def get_url_domain(url:str):
    ext = extract(url) # subdomain, domain, suffix
    return ext.registered_domain if ext else None


def get_matched_text(match):
    return unicodedata.normalize('NFKC', match.group(1).lower()).strip() if match else ''


if __name__ == "__main__":
    mbfc_sources = {"source": [], "country": [], "bias": [], "factual_reporting": [],
                    "press_freedom": [], "media_type": [], "popularity": [], "mbfc_credibility_rating": []}
    for bias in tqdm(MBFC_BIAS_CATEGORY, desc="Bias type"):
        target_url = f"{BASE_URL}/{bias}/"
        r = requests.get(target_url)
        if not check_response_ok(r):
            continue

        dom = BeautifulSoup(r.text, "html.parser", parse_only=SoupStrainer("table"))

        table_sources = dom.find("table", {"id": "mbfc-table"})
        if not table_sources:
            table_sources = BeautifulSoup(r.text, "html.parser", parse_only=SoupStrainer("article")).find("div", {"class": "entry-content"})

        links = table_sources.find_all("a")
        if not links:
            logger.warning(f"{target_url} -> no links found (skipping)")
            continue

        for link_to_source in tqdm(links, desc="News sources"):
            target_url = link_to_source['href']

            try:
                success = False
                while not success:
                    r = requests.get(target_url)
                    if r.status_code == 429:  # Too many requests
                        logger.info(f"{target_url} -> too many requests (waiting for 10 seconds and trying again)")
                        time.sleep(5)
                    else:
                        success = True
                        time.sleep(.5)
            except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema) as e:
                logger.warning(f"{target_url} -> parsing error: invalid schema (skipping)")
                continue

            if not check_response_ok(r):
                continue

            dom = BeautifulSoup(r.text, "html.parser", parse_only=SoupStrainer("article"))

            pp = dom.find_all("p")
            if not pp:
                logger.warning(f"{target_url} -> no paragraph tags <p> found (skipping)")
                continue

            source_info = {key:'' for key in mbfc_sources.keys()}
            for p in dom.find_all("p"):
                m = re.search(r"Sources?:\s*(.+)", p.text, flags=re.IGNORECASE)
                if not m:
                    m = re.search(r"Sources?:?\s*(http.+)", p.text, flags=re.IGNORECASE)
                if m and not source_info["source"]:
                    source_info["source"] = get_url_domain(m.group(1).strip().lower())

                m = re.search(r"Country:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["country"] = get_matched_text(m)

                m = re.search(r"Bias Rating:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["bias"] = get_matched_text(m)

                m = re.search(r"Factual Reporting:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["factual_reporting"] = get_matched_text(m)

                m = re.search(r"Press Freedom \w+:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["press_freedom"] = get_matched_text(m)

                m = re.search(r"Media Type:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["media_type"] = get_matched_text(m)

                m = re.search(r"Traffic/Popularity:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["popularity"] = get_matched_text(m)

                m = re.search(r"MBFC Credibility Rating:\s*(.+)", p.text, flags=re.IGNORECASE)
                if m:
                    source_info["mbfc_credibility_rating"] = get_matched_text(m)

            if source_info["source"]:
                for key, value in source_info.items():
                    mbfc_sources[key].append(value)
            else:
                logger.warning(f"{target_url} -> no source URL found (skipping)")

    df = pd.DataFrame.from_dict(mbfc_sources)
    df = df[["source", "country", "bias", "factual_reporting",
             "press_freedom", "media_type", "popularity",
             "mbfc_credibility_rating"]]
    df.fillna('', inplace=True)
    df.drop_duplicates(inplace=True)

    print(df.head())
    print()

    print("Total entries:", len(df))
    print("Entries with Fact Reporting:", len(df[df.factual_reporting != '']))
    print("Entries with MBFC Credibility Rating:", len(df[df.mbfc_credibility_rating != '']))
    print()
    print("Fact Reporting unique values:", df.factual_reporting.unique().tolist())
    print("MBFC Credibility Rating unique values:", df.mbfc_credibility_rating.unique().tolist())

    df.factual_reporting = df.factual_reporting.map(lambda v: v.replace('-', ' '))
    print("Fixing Fact Reporting unique values:", df.factual_reporting.unique().tolist())
    print()
    print("Fact Reporting value distribution:")
    print(df[df.factual_reporting != ''].factual_reporting.value_counts())
    print()
    print("MBFC Credibility Rating value distribution:")
    print(df[df.mbfc_credibility_rating != ''].mbfc_credibility_rating.value_counts())

    # There's only 1 instance with "mixed credibility" for MBFC Credibility Rating.
    # We'll replace it's value by 'low credibility'
    df.loc[df.mbfc_credibility_rating == 'mixed credibility', 'mbfc_credibility_rating'] = 'low credibility'
    print()
    print("MBFC Credibility Rating value FINAL distribution:")
    print(df[df.mbfc_credibility_rating != ''].mbfc_credibility_rating.value_counts())

    # Replace non-standard Fact Reportirng `mostly factual` value with `mixed` since they both have the same
    # MBFC Credibility Rating distribution
    df.loc[df.factual_reporting == 'mostly factual', 'factual_reporting'] = 'mixed'
    print()
    print("Fact Reporting value FINAL distribution:")
    print(df[df.factual_reporting != ''].factual_reporting.value_counts())

    df.to_csv(f"{OUTPUT_FILE_NAME}.csv", index=False)
