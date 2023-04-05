from requests import get
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('content.html')

origin_format = '%Y-%m-%dT%H:%M:%S.%fZ'
target_format = '%Y-%m-%d'

def get_games():
    result = get('https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN').json()
    games = []
    for game in [x for x in result['data']['Catalog']['searchStore']['elements'] if x['offerType'] == 'BASE_GAME']:
        title = game['title']
        cover = [x for x in game['keyImages'] if x['type']=='Thumbnail'][0]['url'] + '?h=480&quality=medium&resize=1&w=360'
        upcoming = False
        promotions = game['promotions']
        if not promotions['promotionalOffers']:
            upcoming = True
        discount_time = [x for x in promotions['upcomingPromotionalOffers' if upcoming else 'promotionalOffers'][0]['promotionalOffers'] if x['discountSetting']['discountPercentage']==0][0]
        games.append({
            'title': title, 
            'cover': cover,
            'upcoming': upcoming,
            'link': f"https://store.epicgames.com/zh-CN/p/{game['catalogNs']['mappings'][0]['pageSlug']}",
            'discount_time': {
                'start': (datetime.strptime(discount_time['startDate'], origin_format) + timedelta(hours=8)).strftime(target_format),
                'end': (datetime.strptime(discount_time['endDate'], origin_format) + timedelta(hours=8)).strftime(target_format),
            }
        })
    return template.render(games=sorted(games, key=lambda game: game['upcoming']))

html = get_games()

config = {}

with open('.env', 'r') as file:
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
