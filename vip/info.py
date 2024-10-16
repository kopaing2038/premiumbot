import re, os


DATABASE_URI = os.environ.get('DATABASE_URI', "mongodb+srv://premiumbot:premiumbot@cluster0.5siafyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1001254905376'))
START_IMG = os.environ.get('START_IMG', 'https://l.arzfun.com/30hBn')

NEW_USER_TXT = """<b>#New_User 

≈ ɪᴅ:- <code>{}</code>
≈ ɴᴀᴍᴇ:- {}</b>"""
