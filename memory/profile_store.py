import sqlite3, json
from pathlib import Path
from memory.paths import PROFILE_DB
#BASE = Path(__file__).parent

class ProfileStore:
    def __init__(self, db_path=PROFILE_DB):
        self.con = sqlite3.connect(db_path)   # 绝对路径
        self.con.execute("CREATE TABLE IF NOT EXISTS profile (k TEXT PRIMARY KEY, v TEXT)")
        self.con.commit()

    def set_profile(self, k, v):
        self.con.execute("INSERT OR REPLACE INTO profile VALUES(?,?)",(k,json.dumps(v)))

    def get_profile(self,k):
        row=self.con.execute("SELECT v FROM profile WHERE k=?",(k,)).fetchone()
        return json.loads(row[0]) if row else None

    