from bs4 import BeautifulSoup
import requests
import time
import random
import re
import datetime
import os
import argparse
import pandas as pd
from tqdm import tqdm

# from translate import Translator


def get_one_page(url):
    response = requests.get(url)
    while response.status_code == 403:
        time.sleep(500 + random.uniform(0, 500))
        response = requests.get(url)
        print(response.status_code)
    if response.status_code == 200:
        print("Successfully access " + url + "!")
        return response.text
    return None


def accessMonthlyPaper(data_dir, categories, months):
    for category in categories:
        for month in months:
            url = "https://arxiv.org/list/" + category + "/" + month
            print("accessing " + category + " in " + month)
            html = get_one_page(url)
            soup = BeautifulSoup(html, features="html.parser")
            # get the url that contains all paper in the specific category and month
            allurl = (
                "https://arxiv.org/"
                + soup.findAll("a", attrs={"href": re.compile("\?show=")})[0]["href"]
            )
            html = get_one_page(allurl)
            soup = BeautifulSoup(html, features="html.parser")
            now_time = datetime.datetime.now().strftime("%y%m%d")
            # create month folders
            page_dir = os.path.join(data_dir + "/" + month + "_until_" + now_time + "/")
            if not os.path.exists(page_dir):
                os.mkdir(page_dir)
            page_name = category + ".html"
            with open(os.path.join(page_dir + page_name), "w", encoding="utf-8") as fp:
                fp.write(soup.prettify())


def generatePaperList(data_dir, categories, months):
    # translator= Translator(to_lang="chinese")
    for month in months:
        for dirpath, _, filenames in os.walk(data_dir):
            # find the month folders
            if dirpath.find(month) != -1:
                for category in categories:
                    page_name = category + ".html"
                    # not exist html file for the category in this month
                    if page_name not in filenames:
                        print("No " + category + " in " + month)
                        continue
                    with open(
                        os.path.join(dirpath, page_name), "r", encoding="utf-8"
                    ) as f:
                        page = f.read()
                        soup = BeautifulSoup(page, features="lxml")
                        content = soup.dl
                        ids = content.find_all("a", title="Abstract")
                        titles = content.find_all("div", class_="list-title mathjax")
                        authors = content.find_all("div", class_="list-authors")
                        subjects = content.find_all("div", class_="list-subjects")
                        items = []
                        print(
                            "total papers for "
                            + category
                            + " in "
                            + month
                            + ":"
                            + str(len(ids))
                        )
                        for _, paper in tqdm(
                            enumerate(zip(ids, titles, authors, subjects))
                        ):
                            items.append(
                                [
                                    paper[0]
                                    .text.replace("arXiv:", "")
                                    .replace("\n", " ")
                                    .strip(),
                                    paper[1]
                                    .text.replace("Title:", "")
                                    .replace("\n", " ")
                                    .strip(),
                                    "No Translation",
                                    paper[2]
                                    .text.replace("Authors:", "")
                                    .replace("\n        ", "")
                                    .replace("\n", "")
                                    .strip(),
                                    paper[3]
                                    .text.replace("Subjects:", "")
                                    .replace("\n         ", "")
                                    .replace("\n        ", "")
                                    .replace("\n", ""),
                                ]
                            )
                        # all paper
                        name = ["id", "title", "translation", "author", "subject"]
                        paper = pd.DataFrame(columns=name, data=items)
                        paper.to_csv(os.path.join(dirpath, category + ".csv"))
                        print("Saved paperlist for " + category + " in " + month)


def filterWithKeyWords(data_dir, categories, months, keywords):
    # translator= Translator(to_lang="chinese")
    for month in months:
        for dirpath, _, filenames in os.walk(data_dir):
            # find the month folders
            if dirpath.find(month) != -1:
                for category in categories:
                    page_name = category + ".csv"
                    # not exist csv file for the category in this month
                    if page_name not in filenames:
                        print("No " + category + " in " + month)
                        continue
                    papers = pd.read_csv(os.path.join(dirpath, page_name))
                    # or selection and save
                    query_dir = os.path.join(dirpath, "query")
                    if not os.path.exists(query_dir):
                        os.mkdir(query_dir)
                    selected_papers = papers[
                        papers["title"].str.contains(keywords[0], case=False)
                    ]
                    for key_word in keywords[1:]:
                        tmp = papers[papers["title"].str.contains(key_word, case=False)]
                        selected_papers = pd.concat([selected_papers, tmp], axis=0)
                    selected_papers.to_csv(
                        os.path.join(
                            query_dir,
                            category + "_selected_" + "_".join(keywords) + ".csv",
                        )
                    )
                    print(
                        "Saved paperlist for "
                        + category
                        + " in "
                        + month
                        + " with keywords =",
                        keywords,
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom your own areas and times")
    parser.add_argument("--operation", type=str, default="access", help="months list")
    parser.add_argument(
        "--months", type=str, nargs="+", default=["2207"], help="months list"
    )
    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        default=["cs.AI", "cs.PL", "cs.SE"],
        help="categories list,you can choose from https://arxiv.org/archive/cs",
    )
    parser.add_argument(
        "--keywords", type=str, nargs="+", help="keywords for filter operation"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./",
        help="data path for saving all the output files",
    )
    args = parser.parse_args()
    print(args)
    if not os.path.exists(args.data_dir):
        os.mkdir(args.data_dir)
    if args.operation == "access":
        accessMonthlyPaper(args.data_dir, args.categories, args.months)
    elif args.operation == "generate":
        generatePaperList(args.data_dir, args.categories, args.months)
    elif args.operation == "filt":
        filterWithKeyWords(args.data_dir, args.categories, args.months, args.keywords)
