# Access arXiv Paperlist 📑

为了更好地持续追踪最新的研究近况，本仓库实现了一个能够按照时间和领域类别爬取arXiv上的计算机领域论文信息并根据关键词筛选的小工具，目前实现的功能如下：

✅ Step 1. 选取细分的领域[类别](https://arxiv.org/archive/cs)和指定时间(以月为单位）来进行爬取原始的html网页。

✅ Step 2. 根据对应的网页生成论文信息列表，包括: arXiv id、标题、作者、所属全部类别。

✅ Step 3. 给定关键词列表，筛选题目包含关键词的论文列表。

- [Access arXiv Paperlist 📑](#access-arxiv-paperlist-)
  - [TODO 😉](#todo-)
  - [使用方法 😎](#使用方法-)
  - [按照月份获取arxiv文章](#按照月份获取arxiv文章)
    - [Step 1: 获取对应的html网页](#step-1-获取对应的html网页)
    - [Step 2: 生成所选月份的完整论文列表](#step-2-生成所选月份的完整论文列表)
    - [Step 3: 根据关键字筛选论文列表](#step-3-根据关键字筛选论文列表)
  - [按照年获取arxiv文章](#按照年获取arxiv文章)
    - [Step 1: 获取对应的html网页](#step-1-获取对应的html网页-1)
    - [Step 2: 生成全年的完整论文列表](#step-2-生成全年的完整论文列表)
    - [Step 3: 根据关键字筛选论文列表](#step-3-根据关键字筛选论文列表-1)
  
## TODO 😉

后续会持续更新，欢迎follow🖱️和star⭐!

⬜ 调用API获取筛选后的题目的中文翻译。

⬜ 爬取摘要，获得中文翻译。

⬜ 摘要/题目的词云。


## 使用方法 😎

1. 克隆本项目：
   `git clone git@github.com:codingClaire/access-arxiv-paperlist.git`

2. 安装相关的库：
   `pip install beautifulsoup4`

3. 根据不同的需求按月/年爬取arxiv文章。
   

## 按照月份获取arxiv文章

### Step 1: 获取对应的html网页

存储在当前目录下新建的月份目录，为了分辨是哪一天的爬取的，月份目录的命名加入了爬取的时间。


例子1： 爬取类别为`cs.AI`、`cs.PL`和`cs.SE`在2022年5至7月的全部文章的原始html页面，存储在当前目录。

`python "arxivMonthly.py" --operation "access" --data_dir "./" --categories cs.AI cs.PL cs.SE  --months "2205" "2206" "2207"`

例子2： 爬取类别为`cs.AI`在2022年4月的全部文章的原始html页面，并存储在paperlist目录下。

 `python -u "arxivMonthly.py" --operation "access" --data_dir "./paperlist" --categories cs.AI  --months "2204" --keywords "code" "graph"`



### Step 2: 生成所选月份的完整论文列表

例子：处理`cs.AI`、`cs.PL`和`cs.SE`在2022年5至7月的全部文章的原始html页面，并存储在同一目录下。

`python "arxivMonthly.py" --operation "generate" --data_dir "./" --categories cs.AI cs.PL cs.SE  --months "2205" "2206" "2207"`

### Step 3: 根据关键字筛选论文列表

例子： 筛选2022年4月的`cs.AI`类别的论文中题目包含关键字`code`或`graph`的论文列表。注意，Step3必须要在进行Step2后才可以完成筛选。

`python "arxivMonthly.py" --operation "filt" --data_dir "./paperlist" --categories cs.AI  --months "2204" --keywords "code" "graph"`

## 按照年获取arxiv文章

和按照月份爬取arxiv文章类似，需要经历获取网页、生成完整列表、根据关键词筛选三步。

> arxiv的反爬机制基本只允许一次爬单个类别完整两年的文章，所以如果要爬取的文章较多，可以过段时间再爬。

### Step 1: 获取对应的html网页

存储在当前目录下新建的月份目录，为了记录是哪一天的爬取的，年份目录的命名加入了爬取日期。


例子1： 爬取类别为`cs.AI`在2018年至2022年的全部文章的原始html页面，存储在`pooling_count`当前目录。

`python "arxivYearly.py" --operation "access" --data_dir "./pooling_count/" --categories cs.AI --years "2018" "2019"`


### Step 2: 生成全年的完整论文列表

`python "arxivYearly.py" --operation "generate" --data_dir "./pooling_count/" --categories cs.AI --years "2018" "2019"`


### Step 3: 根据关键字筛选论文列表

`python "arxivYearly.py" --operation "filt" --data_dir "./pooling_count/" --categories cs.AI --years "2018" "2019" --keywords "graph"`