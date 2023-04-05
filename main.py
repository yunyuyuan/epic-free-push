from requests import get
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
import json
import os.path as path

passed_file = path.join(path.dirname(__file__), 'passed.json')

def read_passed_file():
    with open(passed_file, 'r') as fp:
        return json.load(fp)

def write_passed_file(data):
    with open(passed_file, 'w') as fp:
        json.dump(data, fp)

passed = []
if not path.exists(passed_file):
    write_passed_file(passed)
else:
    passed = read_passed_file()

env = Environment(loader=FileSystemLoader(path.dirname(__file__)))
template = env.get_template('content.html')

origin_format = '%Y-%m-%dT%H:%M:%S.%fZ'
target_format = '%Y-%m-%d'


def get_games():
    global passed
    result = get('https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN', headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62'
    }).json()
    origin_games = [x for x in result['data']['Catalog']['searchStore']['elements'] if x['offerType'] == 'BASE_GAME']
    # remove item not in origin_games
    passed =  [x for x in passed if [y for y in origin_games if x['id']==y['id'] and x['upcoming']!=bool(y['promotions']['promotionalOffers'])]]
    games = []
    for game in origin_games:
        title = game['title']
        cover = [x for x in game['keyImages'] if x['type']=='Thumbnail'][0]['url'] + '?h=480&quality=medium&resize=1&w=360'
        upcoming = False
        promotions = game['promotions']
        if not promotions['promotionalOffers']:
            upcoming = True
        discount_time = [x for x in promotions['upcomingPromotionalOffers' if upcoming else 'promotionalOffers'][0]['promotionalOffers'] if x['discountSetting']['discountPercentage']==0][0]
        start_time = datetime.strptime(discount_time['startDate'], origin_format) + timedelta(hours=8)
        end_time = datetime.strptime(discount_time['endDate'], origin_format) + timedelta(hours=8)
        if [x for x in passed if x['id']==game['id'] and x['upcoming']==upcoming]:
            # already exist
            continue
        else:
            item = {
                'id': game['id'],
                'title': title, 
                'cover': cover,
                'upcoming': upcoming,
                'link': f"https://store.epicgames.com/zh-CN/p/{game['catalogNs']['mappings'][0]['pageSlug']}",
                'start': start_time.strftime(target_format),
                'end': end_time.strftime(target_format),
            }
            games.append(item)
            passed.append(item)
    write_passed_file(passed)
    if not games:
        print('no new games')
        exit()
    return template.render(games=sorted(games, key=lambda game: game['upcoming']))

html = get_games()

config = {}

with open(path.join(path.dirname(__file__), '.env'), 'r') as file:
    for line in file.readlines():
        key, value = line.strip().split('=')
        config[key] = value

smtp_server = 'smtp.qq.com'
smtp_port = 587

# Create a message
msg = MIMEMultipart()
msg['From'] = config['ADDRESS']
msg['To'] = config['ADDRESS']
msg['Subject'] = 'Epic Free Games'
msg.attach(MIMEText(html, 'html'))

# Connect to SMTP server
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(config['ADDRESS'], config['CODE'])

# Send the email
server.sendmail(config['ADDRESS'], config['ADDRESS'], msg.as_string())

# Close the SMTP connection
server.quit()

print('Email sent successfully!')
