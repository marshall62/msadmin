import os
import shutil
# sudo apt-get install python-mysqldb
import MySQLdb

DIR = '/srv/fastdisk/dev/pythondev/temp/'

def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)

def getConnection (type):
    if not type or type=='localhost':
        db = MySQLdb.connect(host="localhost",  # host name
                             user="WayangServer",       # username
                             passwd="jupiter",     # password
                             db="wayangoutpostdb")   # name of the database
    else:
        db = MySQLdb.connect(host="rose.cs.umass.edu",  # host name
                             user="WayangServer",       # username
                             passwd="m4thspr1ng!",     # password
                             db="wayangoutpostdb")   # name of the database
    return db

def migrateSurvey (db, cur, id):
    id = str(id)
    q = 'select id,name,image from prepostproblem where id=%s;'
    cur.execute(q,(id,))
    res = cur.fetchone()
    name = res[1]
    blob = res[2]
    if blob:
        write_file(blob,DIR+'problem_'+id + '.jpg')
    else:
        print("problem " + id + " has no image blob")


def migrateSurveys (db, cur):
    q = 'select id,name,image from prepostproblem where image is not null'
    cur.execute(q)
    for row in cur.fetchall():
        id = str(row[0])
        name = row[1]
        blob = row[2]
        if blob:
            write_file(blob,DIR+'problem_'+id + '.jpg')
            print("Wrote image for problem " + id)
        else:
            print("problem " + id + " has no image blob")



#id_name_mapping_list = [(int(row[0]), row[1]) for row in cur.fetchall()]
#db.close()


def main():
    db = getConnection('localhost')
    if db:
        migrateSurvey(db,db.cursor(),197)
        # migrateSurveys(db,db.cursor())
        db.close()




if __name__ == '__main__':
    main()