import requests 
from fake_useragent import UserAgent
import json
import pymysql

ua = UserAgent()

headers = {
    'User-Agent' : ua.random,
}

def main():
    global headers
    connection = pymysql.Connect(
        host = '127.0.0.1',
        port = 3306,
        user = 'root',
        password = 'gobenot11!30SMa',
        database = 'eng_words',
        cursorclass = pymysql.cursors.DictCursor
    )

    url = '	https://puzzle-english.com/api2/sets/getInfoBySlug?slug=b1_level_cefr'
    response = requests.get(url, headers=headers).text

    data = json.loads(response)
    del response 

    for i in data['response']['info']['words']:
        eng_word = i['word']
        ru_word = i['translations']
        print(eng_word)
        with connection.cursor() as cursor:
            expression = f'insert into eng_b1(eng_word, ru_word) values("{str(eng_word)}", "{str(ru_word)}");'
            cursor.execute(expression)
            connection.commit()

    with connection.cursor() as cursor:
        cursor.execute('select * from eng_b1')
        for i in cursor.fetchall():
            print(f'{i}\n')

    connection.close()

if __name__ == "__main__":
    main()