import pymysql

class DataBaseChanger():

    connection = pymysql.Connect(
            host = '127.0.0.1',
            port = 3306,
            user = 'root',
            password = 'gobenot11!30SMa',
            database = 'eng_words',
            cursorclass = pymysql.cursors.DictCursor
        )
        

    def get_data(self, num, index, table_name):
        with self.connection.cursor() as cursor:
            expression = f'select * from {table_name} where id > {index} and id <= {index + num}'
            cursor.execute(expression)
            return [i for i in cursor.fetchall()]


    def add_counter(self, chat_id, counter, level):
        with self.connection.cursor() as cursor:
            expression = f'SELECT * FROM users WHERE chat_id = "{chat_id}" and level = "{level}";'
            cursor.execute(expression)
            k = [i for i in cursor.fetchall()]
            print(k)
            if k == []:
                expression = f'INSERT users(chat_id, counter, level) VALUES ("{chat_id}", "{counter}", "{level}");'
                cursor.execute(expression)
                return [i for i in cursor.fetchall()]
            else:
                expression = f'DELETE FROM users WHERE chat_id = "{chat_id}" and level = "{level}" LIMIT 1;'
                cursor.execute(expression)
                expression = f'INSERT users(chat_id, counter, level) VALUES ("{chat_id}", "{counter}", "{level}");'
                cursor.execute(expression)
                self.connection.commit()
                return [i for i in cursor.fetchall()]


            #expression = f'DELETE FROM users WHERE chat_id = {chat_id} and level = {level} LIMIT 1;'



    def get_counter(self, chat_id, level):
        with self.connection.cursor() as cursor:
            expression = f'SELECT counter FROM users WHERE chat_id = "{chat_id}" and level = "{level}";'
            cursor.execute(expression)
            data = [i for i in cursor.fetchall()]

            if data != []:
                return [i for i in data][-1]['counter']
            else:
                return None