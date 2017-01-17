# -*- coding: utf-8 -*-
import pymysql

class Account():
    """ Insert new account into database if account doesn't exist,
        #update account email if it has been changed. """
    def __init__(self, conn, name, email):
        self.conn = conn
        self.name = name
        self.email = email
        self.id = 0
    
    def search_user(self):
        """ Search user in MySQL by name (which should be user id). """
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM accounts WHERE full_name=%s"
            cursor.execute(sql, (self.name))
            results = cursor.fetchall()
            # The results is a tuple object - ((name, email, account_id),)
            if len(results):
                #self.email = results[0][1]
                self.id = results[0][2]
        
    def create_user(self):
        """ Create new user if he or she doesn't exit. """
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO `accounts` (`full_name`, `preferred_email`)\
                       VALUES (%s, %s)"
                cursor.execute(sql, (self.name, self.email))
            self.conn.commit()
        except:
            self.conn.rollback()
        else:
            self.search_user()
    def check_email(self, email):
        """ Update email if it has changed. """
        if self.email != email:
            try:
                with self.conn.cursor() as cursor:
                    sql = "UPDATE `accounts` SET `preferred_email`=%s \
                           WHERE `full_name`=%s"
                    cursor.execute(sql, (email, name))
                self.conn.commit()
            except:
                self.conn.rollback()
    
    def get_account_id(self):
        """ Return account id. """
        self.search_user()
        if self.id == 0:
            self.create_user()
        #else:
        #    self.check_email(email)
        
        return self.id