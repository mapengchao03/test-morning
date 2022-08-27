import math
import random
import config
import requests
from zhdate import ZhDate
from wechatpy import WeChatClient
from datetime import date, datetime
from wechatpy.client.api import WeChatMessage
from apscheduler.schedulers.blocking import BlockingScheduler


# 获取天气
def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    result = requests.get(url)
    if result.status_code == 200:
        weather_data = result.json()['data']['list'][0]
        weather = weather_data['weather']
        current_temp = str(math.floor(weather_data['temp']))
        wind = weather_data['wind']
        low = str(math.floor(weather_data['low']))
        high = str(math.floor(weather_data['high']))
        pm25 = str(math.floor(weather_data['pm25']))
        air_quality = weather_data['airQuality']
        return [weather, current_temp, wind, low, high, pm25, air_quality]
    return ['无'] * 7


# 获取相识天数
def get_days():
    delta = today - datetime.strptime(config.start_date, "%Y-%m-%d")
    return delta.days


# 获取执行时间
def get_send_time():
    send_time = config.send_time
    send_time_list = send_time.split(':')
    send_hour = send_time_list[0]
    send_minute = send_time_list[1]
    return [send_time, send_hour, send_minute]


# 当天转为字符串
def get_today():
    return today.strftime("%Y{}%m{}%d{}").format('年','月','日')


# 农历转换为阳历
def get_transfer_date():
    int_year = date.today().year
    int_month = int(birthday.split('-')[0])
    int_day = int(birthday.split("-")[1])
    # 初始化农历日期
    lunar_date = ZhDate(int_year,int_month,int_day)
    # 农历转阳历
    birthday_date = lunar_date.to_datetime()
    return birthday_date


# 距离生日天数
def get_birthday():
    birthday_date = get_transfer_date()
    if birthday_date < datetime.now():
        birthday_date = birthday_date.replace(year=birthday_date.year + 1)
    return (birthday_date - today).days


# 获取彩虹屁
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code == 200:
        return words.json()['data']['text']
    return '每天都要开心啊臭宝！'


# 获取随机颜色
def get_random_color():
    return "#%06x" % random.randint(0x000000, 0xFFFF00)


#  获取发送结果
def get_send_info():
    send_status = ''
    for user_id in user_ids:
        res = wm.send_template(user_id, template_id, data)
        if res['errmsg'] == 'ok':
            send_status = '发送成功'
        else:
            send_status = '发送失败'
    end_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H_%M_%S")
    print('结束时间: ' + end_date + ',' + send_status + "!")


# 获取任务
def get_task():
    send_time = get_send_time()[0]
    send_hour = get_send_time()[1]
    send_minute = get_send_time()[2]
    start_date = datetime.strftime(today, "%Y-%m-%d %H_%M_%S")
    print('当前时间: ' + start_date + ",距离 " + send_time + " 还有一段时间，稍安勿躁.")
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(get_send_info, 'cron', hour=send_hour, minute=send_minute)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


# 定义基本数据
today = datetime.now()
city = config.city
birthday = config.birthday
app_id = config.app_id
app_secret = config.app_secret
user_ids = config.user_ids
template_id = config.template_id
# 初始化公众号发送信息接口
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
data = {
    "date": {"value": get_today(), "color": get_random_color()},
    "city": {"value": city},
    "weather": {"value": get_weather()[0]},
    "current_temperature": {"value": get_weather()[1], "color": get_random_color()},
    "wind": {"value": get_weather()[2]},
    "min_temperature": {"value": get_weather()[3], "color": get_random_color()},
    "max_temperature": {"value": get_weather()[4], "color": get_random_color()},
    "love_days": {"value": get_days(), "color": get_random_color()},
    "birthday": {"value": get_birthday(), "color": get_random_color()},
    "rainbow": {"value": get_words(), "color": get_random_color()},
}

if __name__ == "__main__":
    get_task()
