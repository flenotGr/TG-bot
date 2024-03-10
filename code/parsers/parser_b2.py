import requests 
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
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

    url = 'https://word-by-word.ru/ratings/cefr-b2?page='
    for i in range(22):
        response = requests.get(url+str(i), headers=headers).text
        soup = BeautifulSoup(response, 'html.parser')
        eng_words = soup.find_all(class_='spelling')
        ru_words = soup.find_all(class_='translations')

        for j, o in zip(eng_words, ru_words):
            with connection.cursor() as cursor:
                ru = str(o.text).replace('/', ' ')
                expression = f'insert into eng_b2(eng_word, ru_word) values("{j.text}", "{ru}");'
                cursor.execute(expression)
                connection.commit()

    with connection.cursor() as cursor:
        cursor.execute('select * from eng_b2')
        for i in cursor.fetchall():
            print(f'{i}\n')

    connection.close()

    
if __name__ == "__main__":
    main()