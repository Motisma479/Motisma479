import xml.etree.ElementTree as ET
from datetime import date, timedelta
import sys
import json

monthToText = {
    1 : "Jan",
    2 : "Feb",
    3 : "Mar",
    4 : "Apr",
    5 : "May",
    6 : "Jun",
    7 : "Jul",
    8 : "Aug",
    9 : "Sep",
    10 : "Oct",
    11 : "Nov",
    12 : "Dec"
}

contributionToColor = {
    "NONE" : "#151b23",
    "FIRST_QUARTILE" : "#033a16",
    "SECOND_QUARTILE" : "#196c2e",
    "THIRD_QUARTILE" : "#2ea043",
    "FOURTH_QUARTILE" : "#56d364"
}


char_width = {
    "0": 1.2,
    "1": 1.2,
    "2": 1.2,
    "3": 1.2,
    "4": 1.2,
    "5": 1.2,
    "6": 1.2,
    "7": 1.2,
    "8": 1.2,
    "9": 1.2,
}

def estimate_width(text, base=8):
    width = 0
    for c in text:
        width += char_width.get(c, 1.0)
    return width * base

json_file = sys.argv[1]
with open(json_file, "r") as f:
    contribution = json.load(f)


tree = ET.parse("Resources/MonthlyGraphTemplate.svg")
root = tree.getroot()

ET.register_namespace("", "http://www.w3.org/2000/svg")
grid = root.find(".//*[@id='month']")

padding = 9.6

cellSize = 15
gap = 3.5

root.set("height",str(cellSize*7 + gap*6 + padding*2 + 30))
border = root.find(".//*[@id='border']")
border.set("height", str(cellSize*7 + gap*6 + padding*2 + 30-2))

mon = root.find(".//*[@id='mon']")
mon.set("y", str(cellSize*2+gap +padding + 30))
mon.set("x", str(padding))

wed = root.find(".//*[@id='wed']")
wed.set("y", str(cellSize*4+gap*3 +padding + 30))
wed.set("x", str(padding))

fri = root.find(".//*[@id='fri']")
fri.set("y", str(cellSize*6+gap*5 +padding + 30))
fri.set("x", str(padding))

step = cellSize + gap

def add_cell(x,y, level):
    rect = ET.SubElement(
        grid,
        "{http://www.w3.org/2000/svg}rect"
    )
    
    rect.set("x", str(x))
    rect.set("y", str(y))
    rect.set("width", str(cellSize))
    rect.set("height", str(cellSize))
    rect.set("rx", "2")
    
    rect.set("fill", level)
    
today = date.today()
year = today.year
month = today.month

days = days = (date(year, month % 12 + 1, 1) - timedelta(days=1)).day

gridMinX = 30 + cellSize + padding
gridMaxX = gridMinX
idRelativeToWeekStart = 0
preWeek = -1
for day in range(1, days + 1):
    d = date(year, month, day)

    # Monday = 0
    # weekday = d.weekday()
    # Sunday = 0
    weekday = (d.weekday() + 1) % 7

    first = date(year, month, 1)
    firstWeekDay = (first.weekday() + 1) % 7
    
    week = (d.day + firstWeekDay - 1) // 7

    x = week * step + gridMinX
    if(x>gridMaxX):
        gridMaxX = x+cellSize
    
    if(preWeek != week):
            preWeek = week
            xxx = -1
    xxx += 1
 
    add_cell(
        x,
        weekday * step+padding+ 30,
        contributionToColor[contribution["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]["weeks"][week]["contributionDays"][((weekday - firstWeekDay * (week == 0))%7)]["contributionLevel"]]
    )

monthText = root.find(".//*[@id='monthText']")
monthText.set("x",str((gridMinX + gridMaxX) / 2))
monthText.set("y",str(padding))

monthText.text = monthToText[month]

separator = root.find(".//*[@id='separator']")
separator.set("x1",str(gridMaxX + cellSize + gap))
separator.set("x2",str(gridMaxX + cellSize + gap))
separator.set("y1",str(padding))
separator.set("y2",str(cellSize*7 + gap*6 + padding*2 + 30 - padding))


statTitle = root.find(".//*[@id='statTitle']")

statTitle.set("y",str(padding))

commit = contribution["data"]["viewer"]["contributionsCollection"]["totalCommitContributions"]
issue = contribution["data"]["viewer"]["contributionsCollection"]["totalIssueContributions"]
pullRequestOppend = contribution["data"]["viewer"]["contributionsCollection"]["totalPullRequestContributions"]
pullRequestReview = contribution["data"]["viewer"]["contributionsCollection"]["totalPullRequestReviewContributions"]
newRepo = contribution["data"]["viewer"]["contributionsCollection"]["totalRepositoryContributions"]

EntryCount = (commit > 0) + (issue > 0) + (pullRequestOppend > 0) + (pullRequestReview > 0) + (newRepo > 0)

if(EntryCount > 1 ):
    statTitle.text = 'Stats'
else:
    statTitle.text = 'Stat'

lastY = 30
longestString = 0
if(commit > 0):
    commitTxt = ET.Element("text")
    commitTxt.set("x",str(gridMaxX + cellSize + gap +10))
    lastY += 25
    commitTxt.set("y",str(lastY))
    commitTxt.set("class","descriptor")
    commitTxt.text = f"• {str(commit)} new {'commit' if commit == 1 else 'commits'}"
    if(estimate_width(commitTxt.text) > longestString): longestString = estimate_width(commitTxt.text)
    root.append(commitTxt)

if(issue > 0):
    issueTxt = ET.Element("text")
    issueTxt.set("x",str(gridMaxX + cellSize + gap +10))
    lastY += 25
    issueTxt.set("y",str(lastY))
    issueTxt.set("class","descriptor")
    issueTxt.text = f"• {str(issue)} new {'issue' if issue == 1 else 'issues'}"
    if(estimate_width(issueTxt.text) > longestString): longestString = estimate_width(issueTxt.text)
    root.append(issueTxt)
 
if(pullRequestOppend > 0):
    pullTxt = ET.Element("text")
    pullTxt.set("x",str(gridMaxX + cellSize + gap +10))
    lastY += 25
    pullTxt.set("y",str(lastY))
    pullTxt.set("class","descriptor")
    pullTxt.text = f"• {str(pullRequestOppend)} new pull {'request' if pullRequestOppend == 1 else 'requests'}"
    if(estimate_width(pullTxt.text) > longestString): longestString= estimate_width(pullTxt.text)
    root.append(pullTxt)
    
if(pullRequestReview > 0):
    reviewTxt = ET.Element("text")
    reviewTxt.set("x",str(gridMaxX + cellSize + gap +10))
    lastY += 25
    reviewTxt.set("y",str(lastY))
    reviewTxt.set("class","descriptor")
    reviewTxt.text = f"• {str(pullRequestReview)} pull request {'review' if pullRequestReview == 1 else 'reviews'}"
    if(estimate_width(reviewTxt.text) > longestString): longestString = estimate_width(reviewTxt.text)
    root.append(reviewTxt)
    
if(newRepo > 0):
    repoTxt = ET.Element("text")
    repoTxt.set("x",str(gridMaxX + cellSize + gap +10))
    lastY += 25
    repoTxt.set("y",str(lastY))
    repoTxt.set("class","descriptor")
    repoTxt.text = f"• {str(newRepo)} new {'repository' if newRepo == 1 else 'repositories'}"
    if(estimate_width(repoTxt.text) > longestString): longestString = estimate_width(repoTxt.text)
    root.append(repoTxt)

border.set("width",str(gridMaxX + cellSize + gap + 10 + longestString))
root.set("width",str(float(border.get("width"))+2))
statTitle.set("x",str(((gridMaxX + cellSize + gap) + float(border.get("width"))) / 2))

tree.write("Generated/MonthlyGraphOutput.svg")