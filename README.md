# :performing_arts: Mapping the Media Landscape: Predicting Factual Reporting and Political Bias Through Web Interactions

> **Paper Abstract:** Bias assessment of news sources is paramount for professionals, organizations, and researchers who rely on truthful evidence for information gathering and reporting. While certain bias indicators are discernible from content analysis, descriptors like political bias and fake news pose greater challenges. In this paper, we propose an extension to a recently presented news media reliability estimation method that focuses on modeling outlets and their longitudinal web interactions. Concretely, we assess the classification performance of four reinforcement learning strategies on a large news media hyperlink graph. Our experiments, targeting two challenging bias descriptors, factual reporting and political bias, showed a significant performance improvement at the source media level. Additionally, we validate our methods on the CLEF 2023 CheckThat! Lab challenge, outperforming the reported results in both, F1-score and the official MAE metric. Furthermore, we contribute by releasing the largest annotated dataset of news source media, categorized with factual reporting and political bias labels. Our findings suggest that profiling news media sources based on their hyperlink interactions over time is feasible, offering a bird's-eye view of evolving media landscapes.
---

This is the repo accompanying the paper [_"Mapping the Media Landscape: Predicting Factual Reporting and Political Bias Through Web Interactions"_](https://link.springer.com/chapter/10.1007/978-3-031-71736-9_7) (PDF version available [here](https://publications.idiap.ch/attachments/papers/2024/Sanchez-Cortes_CLEF2024_2024.pdf)).

## :bookmark_tabs: Datasets

### 1. :bar_chart: Political Bias and Factual Reporting (paper)

The CSV file with the ground truth dataset described in the paper is located in [`data/mbfc.csv`](data/mbfc.csv). The CSV file contains, for each news media url domain, the factual reporting and political bias labels. The CSV structure is as shown in the following example:

|source|bias|factual_reporting|
| --- | --- | --- |
|9news.com|neutral|high|
|nbc11news.com|neutral|high|
|academia.org|right|mixed|
|aim.org|right|mixed|
|acton.org|right|mixed|
|trueactivist.com|left|low|
|bossip.com|left|mixed|
|hannity.com|right|low|
|hawarnews.org|left|low|
|...|||

This CSV file contains annotation for 3920 news sources and the label distribution is as follows:
- Political Bias Label distribution:
    |Label|Count|
    | --- | --- |
    |neutral|1102|
    |right-center|976|
    |left-center|763|
    |right|754|
    |left|325|
- Factual Reporting Label distribution:
    |Label|Count|
    | --- | --- |
    |high|2121|
    |mixed|1391|
    |low|408|

### 2. :newspaper: Raw `mediabiasfactcheck.com` dataset

The dataset introduced in the paper was build from scraping the [mediabiasfactcheck.com](https://mediabiasfactcheck.com) website and then normalizing the annotation. In this repo we also release the raw dataset extracted from scraping [mediabiasfactcheck.com](https://mediabiasfactcheck.com). The CSV file containing the raw annotation is located in [`data/mbfc_raw.csv`](data/mbfc_raw.csv). The file contains the structure shown in the following example:

|source|country|bias|factual_reporting|press_freedom|media_type|popularity|mbfc_credibility_rating|
|---|---|---|---|---|---|---|---|
|9news.com|usa|least biased|high|mostly free|tv station|high traffic|high credibility|
|nbc11news.com|usa|least biased|high|mostly free|tv station|medium traffic|high credibility|
|academia.org|usa|right|mixed|mostly free|organization/foundation|minimal traffic|medium credibility|
|aim.org|usa|right|mixed|mostly free|organization/foundation|minimal traffic|low credibility|
|acton.org|usa|right|mixed|mostly free|organization/foundation|minimal traffic|medium credibility|
|trueactivist.com|germany|extreme left|low|mostly free|website|minimal traffic|low credibility|
|bossip.com|usa|extreme left|mixed|mostly free|magazine|high traffic|low credibility|
|hannity.com|usa|extreme right|low|mostly free|website|medium traffic|low credibility|
|hawarnews.org|syria|far left|low|total oppression|news agency|medium traffic|low credibility|
|...||||||||

In this repo we also release the script we used to scrape [mediabiasfactcheck.com](https://mediabiasfactcheck.com) so that it can be used to generate a more up-to-date version of the datasets when needed, as follows:
1. Make sure you have the required packages first with `pip install -r requirements.txt`, then
1. Run `python scrape_mbfc.py` to scrape again the webpage and generate a more up-to-date version of `data/mbfc_raw.csv` (a timestamp will be added at the end of the name to prevent overwriting the original previous versions).
2. Run `python create_dataset.py -i data/mbfc_raw.csv -o data/news_media_bias_and_factuality-new.csv` to create the new version of the dataset described in the paper (`data/news_media_bias_and_factuality-new.csv`).

## :microscope: Experiments

First, we need to convert our dataset into ground-truth rewards for both, political bias and factual reporting, using the `dataset2rewards.py` script:
```bash
python dataset2rewards.py
```
These script will create the folliwing two files in `data/rewards`:
1. `golden_truth_dataset-bias.csv`
2. `golden_truth_dataset-factual_reporting.csv`

Now we need to clone the [Reliability Estimation of News Media Sources: "Birds of a Feather Flock Together"](https://github.com/idiap/News-Media-Reliability) repo:
```bash
git clone git@github.com:idiap/News-Media-Reliability.git
cd News-Media-Reliability
```
And then we use our ground truth rewards to compute the scores and perform the 5-fold cross validation using the original `ccnews_create_graph_clef.py` script in the repo following the original README file instructions but using our own ground truth rewards files:
1. Political Bias:
    ```bash
    python ccnews_create_graph_clef.py golden_truth.output_file="PATH/TO/golden_truth_dataset-bias.csv"
    ```
2. Factual Reporting:
    ```bash
    python ccnews_create_graph_clef.py golden_truth.output_file="PATH/TO/golden_truth_dataset-factual_reporting.csv"
    ```

---
## :speech_balloon: Citation

```bibtex
@inproceedings{sanchez2024mapping,
  title={Mapping the media landscape: predicting factual reporting and political bias through web interactions},
  author={S{\'a}nchez-Cort{\'e}s, Dairazalia and Burdisso, Sergio and Villatoro-Tello, Esa{\'u} and Motlicek, Petr},
  booktitle={International Conference of the Cross-Language Evaluation Forum for European Languages},
  pages={127--138},
  year={2024},
  organization={Springer}
}

@inproceedings{burdisso-etal-2024-reliability,
    title = "Reliability Estimation of News Media Sources: Birds of a Feather Flock Together",
    author = "Burdisso, Sergio  and
      Sanchez-cortes, Dairazalia  and
      Villatoro-tello, Esa{\'u}  and
      Motlicek, Petr",
    editor = "Duh, Kevin  and
      Gomez, Helena  and
      Bethard, Steven",
    booktitle = "Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)",
    month = jun,
    year = "2024",
    address = "Mexico City, Mexico",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.naacl-long.383",
    pages = "6893--6911",
}
```
