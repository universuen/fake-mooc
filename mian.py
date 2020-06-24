import re
import hashlib
import requests
import json
import time

# 生成enc
def make_enc(time, clazzId, duration, clipTime, objectId, jobid, userid):
    if jobid == None:
        jobid = ''
    raw = '[{0}][{1}][{2}][{3}][{4}][{5}][{6}][{7}]'.format(clazzId, userid, jobid, objectId, time*1000, "d_yHJ!$pdA~5", duration*1000, clipTime)
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

# 生成视频状态序列
def make_sequence(clazzId, duration, clipTime, objectId, jobid, userid):
    playingTime = -60
    result = []
    while playingTime < duration:
        playingTime += 60
        if playingTime > duration:
            playingTime = duration
        enc = make_enc(playingTime, clazzId, duration, clipTime, objectId, jobid, userid)
        result.append((playingTime, enc))
    return result

# 获取请求相关参数
def get_arg(url, cookies):
    chapterId = re.search(r'chapterId=(.*?)&', url).group(1)
    clazzId = re.search(r'clazzid=(.*?)&', url).group(1)
    courseId = re.search(r'courseId=(.*?)&', url).group(1)
    url = "http://mooc1.mooc.whu.edu.cn/knowledge/cards?clazzid=" + clazzId + "&courseid=" + courseId + "&knowledgeid=" + chapterId + "&num=0&ut=s&cpi=64752888&v=20160407-1"
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
    headers = {'User-Agent':ua}

    html = requests.get(url, cookies=cookies, headers=headers).text
    arg_string = re.search("mArg = ({.+?});", html, re.S).group(1)
    arg = json.loads(arg_string)
    for item in arg['attachments']:
        sub_url = item['objectId']
        url = "http://mooc1.mooc.whu.edu.cn/ananas/status/" + sub_url
        html = requests.get(url, cookies=cookies, headers=headers).text
        item['dtoken'] = re.search('"dtoken":"(.*?)"', html).group(1)
    return arg


def play_video(url, cookies):
    # 获取相关参数
    arg = get_arg(url, cookies)
    clazzId = str(arg['defaults']['clazzId'])
    userid = arg['defaults']['userid']

    # 播放页面中所有视频
    for video in arg['attachments']:

        # 相关参数预处理
        duration = str(int(video['headOffset'])/1000)
        clipTime = '0_' + str(duration)
        objectId = video['objectId']
        otherInfo = video['otherInfo']
        jobid = video['jobid']
        dtoken = video['dtoken']
        sequence = make_sequence(clazzId, duration, clipTime, objectId, jobid, userid)
        standard_t = int(round(time.time() * 1000))

        # 将每一个状态序列依次发送到服务端
        for info in sequence:

            # 相关参数预处理
            playingTime = str(info[0])
            _t = str(standard_t + int(playingTime * 1000))
            enc = info[1]

            # 拼接url
            url = "http://mooc1.mooc.whu.edu.cn/multimedia/log/a/64752888/" + dtoken + "?clazzId=" + clazzId + "&playingTime=" + playingTime +"&duration=" + duration + "&clipTime=" + clipTime + "&objectId=" + objectId + "&otherInfo=" + otherInfo + "&jobid=" + jobid + "&userid=" + userid + "&isdrag=0&view=pc&enc=" + enc + "&rt=0.9&dtype=Video&_t=" + _t

            # 发送请求并回执状态码
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
            headers = {'User-Agent': ua}
            print(requests.get(url, cookies=cookies, headers=headers).status_code)


if __name__ == '__main__':
    url = "http://mooc1.mooc.whu.edu.cn/mycourse/studentstudy?chapterId=331570352&courseId=207018950&clazzid=14103123&enc=5085df6bb6f7a2546c8ad0a57d938da3"

    # 读取cookies
    f = open(r'cookies.txt', 'r')
    cookies = {}
    for line in f.read().split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value

    #播放视频
    play_video(url, cookies)