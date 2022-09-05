from bs4 import BeautifulSoup

import re
import datetime
import os
import argparse
import pandas as pd
from tqdm import tqdm
import glob
from utils import get_one_page


def accessYearlyPaper(data_dir, categories, years):
    for category in categories:
        for year in years:
            for i in range(1, 13):
                if i < 10:
                    month = year[2:] + "0" + str(i)
                else:
                    month = year[2:] + str(i)
                url = "https://arxiv.org/list/" + category + "/" + month
                print("accessing " + category + " in " + month)
                html = get_one_page(url)
                soup = BeautifulSoup(html, features="html.parser")
                # get the url that contains all paper in the specific category and month
                allurl = (
                    "https://arxiv.org/"
                    + soup.findAll("a", attrs={"href": re.compile("\?show=")})[0][
                        "href"
                    ]
                )
                html = get_one_page(allurl)
                soup = BeautifulSoup(html, features="html.parser")
                now_time = datetime.datetime.now().strftime("%y%m%d")
                # create access time folders
                page_year_dir = os.path.join(data_dir + year + "_until_" + now_time)
                if not os.path.exists(page_year_dir):
                    os.mkdir(page_year_dir)
                page_month_dir = os.path.join(page_year_dir, month)
                if not os.path.exists(page_month_dir):
                    os.mkdir(page_month_dir)
                page_name = category + ".html"
                with open(
                    os.path.join(page_month_dir, page_name), "w", encoding="utf-8"
                ) as fp:
                    fp.write(soup.prettify())


def generatePaperList(data_dir, categories, years):
    for year in years:
        print("cur year:", year)
        items = []
        page_year_dir = glob.glob(data_dir + year + "*")
        page_year_dir = page_year_dir[0].replace("\\", "/")  # just in case
        for category in categories:
            cur_total = 0
            print("cur category:", category)
            for i in range(1, 13):
                if i < 10:
                    month = year[2:] + "0" + str(i)
                else:
                    month = year[2:] + str(i)
                print(month)
                for dirpath, _, filenames in os.walk(page_year_dir):
                    # find the correct month folders
                    if dirpath[-4:] == month:
                        print(dirpath)
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
                            titles = content.find_all(
                                "div", class_="list-title mathjax"
                            )
                            authors = content.find_all("div", class_="list-authors")
                            subjects = content.find_all("div", class_="list-subjects")

                            print(
                                "total papers for "
                                + category
                                + " in "
                                + month
                                + ":"
                                + str(len(ids))
                            )
                            cur_total += len(ids)
                            print(cur_total)
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
            print(paper.info())
            save_dir = os.path.join(
                page_year_dir, year + "_" + category + ".csv"
            ).replace("\\", "/")
            paper.to_csv(save_dir)
            print("Saved paperlist for " + category + " in " + year)


def filterWithKeyWords(data_dir, categories, years, keywords):
    for year in years:
        for category in categories:
            for dirpath, _, filenames in os.walk(data_dir):
                page_name = year + "_" + category + ".csv"
                if page_name not in filenames:
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
                        year
                        + "_"
                        + category
                        + "_selected_"
                        + "_".join(keywords)
                        + ".csv",
                    )
                )
                print(
                    "Saved paperlist for "
                    + category
                    + " in "
                    + year
                    + " with keywords =",
                    keywords,
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom your own areas and times")
    parser.add_argument("--operation", type=str, default="access", help="months list")
    parser.add_argument(
        "--years", type=str, nargs="+", default=["2021"], help="months list"
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
        accessYearlyPaper(args.data_dir, args.categories, args.years)
    elif args.operation == "generate":
        generatePaperList(args.data_dir, args.categories, args.years)
    elif args.operation == "filt":
        filterWithKeyWords(args.data_dir, args.categories, args.years, args.keywords)
