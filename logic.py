import sqlite3
from config import DATABASE

skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Telegram'])]
statuses = [ (_,) for _ in (['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
    #таблица
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()
        print("База данных успешно создана.")

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
            
    #команды по таблице____________________________________________________________________________________________________________
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_project(self, data):
        sql = 'INSERT OR IGNORE INTO projects (user_id, project_name, url, status_id) values(?, ?, ?, ?)'
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id,skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES (?, ?)'
        self.__executemany(sql, data)

  
    def get_statuses(self):
        sql='SELECT status_name from status'
        return self.__select_data(sql)
        
    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        return self.__select_data(sql='SELECT * FROM projects WHERE user_id = ?', data = (user_id,))

    def get_project_id(self, project_name, user_id):
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ', data = (project_name, user_id,))[0][0]

    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skills')
    
    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
JOIN project_skills ON projects.project_id = project_skills.project_id 
JOIN skills ON skills.skill_id = project_skills.skill_id 
WHERE project_name = ?''', data = (project_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE project_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data = (project_name, user_id))
    

    def update_projects(self, param, data):
        self.__executemany(f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?", [data]) # data ('atr', 'mew', 'name', 'user_id')

    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ? "
        self.__executemany(sql, [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM skills WHERE skill_id = ? AND project_id = ? "
        self.__executemany(sql, [(skill_id, project_id)])

    def insert_status(self, status_name):
        sql = "INSERT INTO status (status_name) VALUES (?)"
        self.__executemany(sql, [(status_name,)])

    def delete_status(self, status_id):
        sql = "DELETE FROM status WHERE status_id = ?"
        self.__executemany(sql, [(status_id,)])

    def update_status(self, status_id, new_status_name):
        sql = "UPDATE status SET status_name = ? WHERE status_id = ?"
        self.__executemany(sql, [(new_status_name, status_id)])

    def insert_new_skill(self, skill_name):
        sql = "INSERT INTO skills (skill_name) VALUES (?)"
        self.__executemany(sql, [(skill_name,)])

    def delete_skill(self, skill_id):
        sql = "DELETE FROM skills WHERE skill_id = ?"
        self.__executemany(sql, [(skill_id,)])

    def update_skill(self, skill_id, new_skill_name):
        sql = "UPDATE skills SET skill_name = ? WHERE skill_id = ?"
        self.__executemany(sql, [(new_skill_name, skill_id)])

    def get_skill_id(self, skill_name):
        sql = "SELECT skill_id FROM skills WHERE skill_name = ?"
        res = self.__select_data(sql, (skill_name,))
        if res: return res[0][0]
        else: return None

    def update_project_status(self, user_id, project_name, new_status_id):
        sql = "UPDATE projects SET status_id = ? WHERE user_id = ? AND project_name = ?"
        self.__executemany(sql, [(new_status_id, user_id, project_name)])

    def update_project_skills(self, user_id, project_name, skills_list):
        project_id = self.get_project_id(project_name, user_id)
        delete_query = "DELETE FROM project_skills WHERE project_id = ?"
        self.__executemany(delete_query, [(project_id,)])
        
        for skill in skills_list:
            skill_id = self.get_skill_id(skill)
            if skill_id:
                insert_query = "INSERT INTO project_skills (project_id, skill_id) VALUES (?, ?)"
                self.__executemany(insert_query, [(project_id, skill_id)])

    def remove_skill_from_project(self, user_id, project_name, skill_name):
        project_id = self.get_project_id(project_name, user_id)
        skill_id = self.get_skill_id(skill_name)
        if skill_id:
            sql = "DELETE FROM project_skills WHERE project_id = ? AND skill_id = ?"
            self.__executemany(sql, [(project_id, skill_id)])

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()