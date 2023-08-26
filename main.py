import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import os.path as path

subject = 'Epic Free Games'
mail_content = None

try:
    from requests import get
    from jinja2 import Environment, FileSystemLoader

    passed_file = path.join(path.dirname(__file__), 'passed.json')

    def read_passed_file():
        with open(passed_file, 'r', encoding='utf-8') as fp:
            return json.load(fp)

    def write_passed_file(data):
        with open(passed_file, 'w', encoding='utf-8') as fp:
            json.dump(data, fp)

    passed = []
    if not path.exists(passed_file):
        write_passed_file(passed)
    else:
        passed = read_passed_file()

    print('passed: ', passed)
    env = Environment(loader=FileSystemLoader(path.dirname(__file__)))
    template = env.get_template('content.html')

    origin_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    target_format = '%Y-%m-%d'

    result = get('https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN', headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62'
    }).json()
    origin_games = [x for x in result['data']['Catalog']['searchStore']['elements'] if (x['offerType'] == 'BASE_GAME' or x['offerType'] == 'OTHERS') and x['promotions']]
    print('origin_games', origin_games)
    # remove item not in origin_games
    passed =  [x for x in passed if [y for y in origin_games if x['id']==y['id']]]
    games = []
    for game in origin_games:
        title = game['title']
        cover = game['keyImages'][0]['url']
        upcoming = False
        promotions = game['promotions']
        if not promotions:
            continue
        for k in ['promotionalOffers', 'upcomingPromotionalOffers']:
            if promotions[k]:
                promotions[k] = [x for x in promotions[k][0]['promotionalOffers'] if x['discountSetting']['discountPercentage']==0]
        if not promotions['promotionalOffers']:
            upcoming = True
        valid_promotion = promotions['upcomingPromotionalOffers' if upcoming else 'promotionalOffers']
        if not valid_promotion:
            continue
        discount_time = valid_promotion[0]
        start_time = datetime.strptime(discount_time['startDate'], origin_format) + timedelta(hours=8)
        end_time = datetime.strptime(discount_time['endDate'], origin_format) + timedelta(hours=8)
        old_game = [x for x in passed if x['id']==game['id']]
        if old_game and old_game[0]['upcoming'] == upcoming:
            # already exist
            continue
        else:
            if old_game and old_game[0]['upcoming'] != upcoming:
                # upcoming change
                passed.remove(old_game[0])

            item = {
                'id': game['id'],
                'title': title, 
                'cover': cover,
                'upcoming': upcoming,
                'link': f"https://store.epicgames.com/zh-CN/p/{game['catalogNs']['mappings'][0]['pageSlug'] if game['catalogNs']['mappings'] else game['productSlug']}",
                'start': start_time.strftime(target_format),
                'end': end_time.strftime(target_format),
            }
            games.append(item)
            passed.append(item)
    write_passed_file(passed)
    if not games:
        print('no new games')
        exit()
    mail_content = MIMEText(template.render(games=sorted(games, key=lambda game: game['upcoming'])), 'html')
except Exception as e:
    subject = '出错了 - Epic Free Games'
    mail_content = MIMEText('''
    <html>
        <body>
            <h2>An error has occurred. Here is the traceback:</h2>
            <pre style="overflow: auto;">{}</pre>
        </body>
    </html>
'''.format(traceback.format_exc()), 'html')

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
msg['Subject'] = subject
msg.attach(mail_content)

# Connect to SMTP server
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(config['ADDRESS'], config['CODE'])

# Send the email
server.sendmail(config['ADDRESS'], config['ADDRESS'], msg.as_string())

# Close the SMTP connection
server.quit()

print('Email sent successfully!')
