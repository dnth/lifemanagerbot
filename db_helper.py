import MySQLdb as mdb
import MySQLdb.cursors
import datetime
from datetime import timedelta
import calendar
import pandas as pd

db_charset='utf8'
db_host='127.0.0.1'
db_user="root"
db_passwd="root"
db_lhc="national_db"

def nc_entry(nc_name, nc_gend, nc_church, nc_ev_date, nc_dept, nc_age, nc_perso_type, nc_comp_uni, nc_niche_course):
    try:


        db = MySQLdb.connect(charset=db_charset, host=db_host, user=db_user, passwd=db_passwd, db=db_lhc,
                             cursorclass=MySQLdb.cursors.DictCursor)
        cur = db.cursor()

        query = """
        INSERT INTO `nc_details` (id, nc_name, nc_gend, nc_age, nc_church, nc_perso_type, nc_dept, nc_comp_uni, nc_niche_course, nc_ev_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (None, nc_name, nc_gend, nc_age, nc_church, nc_perso_type, nc_dept, nc_comp_uni, nc_niche_course, nc_ev_date))


    except Exception as e:
        print e
    finally:
        db.commit()
        db.close()



# nc_entry(nc_name='aniki', nc_gend='Male', nc_church='LLC', nc_ev_date='1978-01-02',
#          nc_dept='Campus', nc_age=None, nc_perso_type=None, nc_comp_uni=None, nc_niche_course=None)


def check_for_existing_user(telegram_id=None):
    try:
        db = mdb.connect(charset=db_charset, host=db_host, user=db_user, passwd=db_passwd, db=db_lhc)
        cur = db.cursor()
        cur.execute("SELECT real_name FROM members_list WHERE telegram_id='{}'".format(telegram_id))
        user_name = cur.fetchall()

        if user_name:
            return True
        else:
            return False
    except Exception as e:
        print "Error in connecting to database", e
        # update.message.reply_text("Error in connecting to database. I cannot seem to record your response. Please try again later")
    finally:
        db.commit()
        db.close()


def get_user_engname(telegram_id):
    try:
        db = MySQLdb.connect(charset=db_charset, host=db_host, user=db_user, passwd=db_passwd, db=db_lhc)
        cur = db.cursor()

    except Exception as e:
        print e

    else:
        cur.execute("SELECT real_name FROM members_list WHERE telegram_id={}".format(telegram_id))
        real_name = cur.fetchall()[0][0]
        return real_name


def get_user_info(telegram_id=None):
    try:
        db = MySQLdb.connect(charset=db_charset, host=db_host, user=db_user, passwd=db_passwd, db=db_lhc, cursorclass=MySQLdb.cursors.DictCursor)
        cur = db.cursor()
        cur.execute("SELECT * FROM members_list WHERE telegram_id='{}'".format(telegram_id))

        user_data_dict = cur.fetchall()[0]
        return user_data_dict

    except Exception as e:
        print "Error in connecting to database", e
        # update.message.reply_text("Error in connecting to database. I cannot seem to record your response. Please try again later")
    finally:
        db.commit()
        db.close()