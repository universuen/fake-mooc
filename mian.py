import re
import hashlib


def make_enc(time, clazzId, duration, clipTime, objectId, jobid, userid):
    if jobid == None:
        jobid = ''
    raw = '[{0}][{1}][{2}][{3}][{4}][{5}][{6}][{7}]'.format(clazzId, userid, jobid, objectId, time*1000, "d_yHJ!$pdA~5", duration*1000, clipTime)
    return hashlib.md5(raw.encode('utf-8')).hexdigest()



def get_sequence(url):
    clazzId = re.search(r'clazzId=(.*?)&', url).group(1)
    duration = int(re.search(r'duration=(.*?)&', url).group(1))
    clipTime = re.search(r'clipTime=(.*?)&', url).group(1)
    objectId = re.search(r'objectId=(.*?)&', url).group(1)
    jobid = re.search(r'jobid=(.*?)&', url).group(1)
    userid = re.search(r'userid=(.*?)&', url).group(1)
    playingTime = -60
    result = []
    while playingTime < duration:
        playingTime += 60
        if playingTime > duration:
            playingTime = duration
        enc = make_enc(playingTime, clazzId, duration, clipTime, objectId, jobid, userid)
        result.append((playingTime, enc))
    return result

if __name__ == '__main__':
    url = input()
    for i in get_sequence(url):
        print(i)

