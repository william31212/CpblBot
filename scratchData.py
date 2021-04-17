import re
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime

BaseballTeam = {
    'http://cpbl-elta.cdn.hinet.net/phone/images/team/AJL011_logo_01.png': '樂天桃猿',
    'http://cpbl-elta.cdn.hinet.net/phone/images/team/E02_logo_01.png': '中信兄弟',
    'http://cpbl-elta.cdn.hinet.net/phone/images/team/B04_logo_01.png': '富邦悍將',
    'http://cpbl-elta.cdn.hinet.net/phone/images/team/D01_logo_01.png': '味全龍',
    'http://cpbl-elta.cdn.hinet.net/phone/images/team/L01_logo_01.png': '統一7-ELEVEn獅'
}

BaseballState = {
    'http://cpbl-elta.cdn.hinet.net/web/images/schedule_icon_final.png' : '比賽結束'
}

class CompetitionInfo:
    def __init__(self):
        # 例行賽編號
        self.number = ''
        # 比賽地點
        self.location = ''
        # A 隊伍
        self.teamA = ''
        # B 隊伍
        self.teamB = ''
        # A 的得分
        self.teamAScore = ''
        # B 的得分
        self.teamBScore = ''
        # 比賽開打時間
        self.playBallTime = ''
        # 現在比賽局數
        self.now = ''
        # 取消比賽敘述
        self.cancelDescription = ''


class DayInfo:
    def __init__(self):
        # 今天日期
        self.date = '{year}-{month}-{day}({week})'.format(
            year=date.today().strftime("%Y"),
            month=str(date.today().strftime("%m")).lstrip('0'),
            day=date.today().strftime("%d"),
            week=date.today().strftime("%a"))
        # 今日比賽數量
        self.competitionCount = 0
        #
        self.competition = []

def parseDayInfoData(todayInfo, content):

    # 將今日表格轉成文字，撈出今日比賽內容
    todaycontent = BeautifulSoup(str(content), 'html.parser')

    # 今日比賽 ( 比賽內容有4個表格 )
    todayCompetition = todaycontent.select('table', {'class': 'schedule_team'})

    if len(todayCompetition) // 4 == 0:
        todayInfo.competitionCount = 0
    else:
        todayInfo.competitionCount = len(todayCompetition) // 4

    for i in range(len(todayCompetition) // 4):
        competitionInfo = CompetitionInfo()
        competitionInfo.number = int(
            todayCompetition[4*i + 1].find('th', {'align': 'center'}).get_text())
        competitionInfo.location = todayCompetition[4*i + 0].select('td')[1].get_text()
        competitionInfo.teamA = BaseballTeam[todayCompetition[4*i + 0].select('img')[0]['src']]
        competitionInfo.teamB = BaseballTeam[todayCompetition[4*i + 0].select('img')[1]['src']]

        # TODO: 現在局數
        if todayCompetition[4*i + 2].select('img', {'align' : 'absmiddle'}):
            competitionInfo.now = BaseballState[todayCompetition[4*i + 2].select('img', {'align': 'absmiddle'})[0]['src']]

        if todayCompetition[4*i + 2].select('span', {'class': 'schedule_score'}):
            competitionInfo.teamAScore = todayCompetition[4*i + 2].select(
                'span', {'class': 'schedule_score'})[0].get_text()
            competitionInfo.teamBScore = todayCompetition[4*i + 2].select(
                'span', {'class': 'schedule_score'})[1].get_text()

        if re.search("\w+:\w+", str(todayCompetition[4*i + 3].select('td', {'align': 'center'}))):
            competitionInfo.playBallTime = todayCompetition[4*i + 3].select(
                'td', {'align': 'center'})[1].get_text()

        if todayCompetition[4*i + 3].select('span', {'class': 'schedule_sp_txt'}):
            competitionInfo.cancelDescription = todayCompetition[4*i + 3].select(
                'span', {'class': 'schedule_sp_txt'})[0].get_text()

        todayInfo.competition.append(competitionInfo)
    
    return todayInfo

def getTodayInformation():
    # new Object 
    todayInfo = DayInfo()
    res = requests.get(
        'http://www.cpbl.com.tw/schedule/index/{year}-{month}-{day}.html?&date={year}-{month}-{day}&gameno=01&sfieldsub=&sgameno=01'.format(
            year=date.today().strftime("%Y"),
            month=str(date.today().strftime("%m")).lstrip('0'),
            day=date.today().strftime("%d")))

    soup = BeautifulSoup(res.text, 'html.parser')

    # 中職賽程表
    table = soup.find('table', {'class': 'schedule gap_t20 gap_b20'})

    # 今日 tr header
    headers = table.find('th', {'class': 'today'}).parent.find_all('th')
    header = table.find('th', {'class': 'today'})

    # 找出今日的表格Index，扣掉tr開頭
    todayIndex = headers.index(header)

    # 撈出今日表格，轉成文字
    content = table.find('th', {'class': 'today'}).parent.findNext(
        'tr').find_all('td', {'valign': 'top'})[todayIndex]

    # 將今日表格轉成文字，撈出今日比賽內容
    todaycontent = BeautifulSoup(str(content), 'html.parser')

    # 今日比賽 ( 比賽內容有4個表格 )
    todayCompetition = todaycontent.select('table', {'class': 'schedule_team'})

    if len(todayCompetition) // 4 == 0:
        todayInfo.competitionCount = 0
    else:
        todayInfo.competitionCount = len(todayCompetition) // 4

    # 交給函式處理當天比賽資料
    todayInfo = parseDayInfoData(todayInfo, content)
    return todayInfo

# Format 20xx-1-2
def getDayOfCpblSchedule(_year, _month, _day):
    # init Data
    dayInfo = DayInfo()
    dayIndex = 0
    header = ''
    
    res = requests.get(
        'http://www.cpbl.com.tw/schedule/index/{year}-{month}-{day}.html?&date={year}-{month}-{day}&gameno=01&sfieldsub=&sgameno=01'.format(
            year=_year,
            month=int(_month),
            day="%02d" % _day))

    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {'class': 'schedule gap_t20 gap_b20'})
    
    try:
        # 檢查日期是否符合格式
        newDate = datetime(_year, _month, _day)

        # 15號以前，都取前面找到的那個，後面那個一定是下個月的
        if _day < 15:
            headers = table.find_all('th', text="%02d" % _day)[0].parent.find_all('th')
            header = table.find_all('th', text="%02d" % _day)[0]
            dayIndex = headers.index(header)
        # 15號以後，若有兩個相同取後面，如果只有一個就取前面
        elif 15 <= _day and _day <= 31:
            # 該個月只有一個 31 天
            if len(table.find_all('th', text=_day)) <= 1:
                headers = table.find_all('th', text=_day)[0].parent.find_all('th')
                header = table.find_all('th', text=_day)[0]
                dayIndex = headers.index(header)
            # 該個月有兩個 31 天以上，取後面那一個
            else:
                headers = table.find_all('th', text=_day)[1].parent.find_all('th')
                header = table.find_all('th', text=_day)[1]
                dayIndex = headers.index(header)

        # 取資料
        content = header.parent.findNext('tr').find_all('td', {'valign': 'top'})[dayIndex]
        # 更新查詢日期
        dayInfo.date = '{year}-{month}-{day}({week})'.format(
            year=_year, month=int(_month), day="%02d" % _day, week=newDate.strftime("%a"))
        # 交給函式處理當天比賽資料  
        tmp = parseDayInfoData(dayInfo, content)
        dayinfo = tmp
        return dayInfo

    except ValueError:
        return '日期格式錯誤'
    
