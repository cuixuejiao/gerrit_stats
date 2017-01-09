# -*- coding: utf-8 -*-
import pymysql

import params

class Account():
    """ Insert new account into database if account doesn't exist,
        update account email if it has been changed. """
    def __init__(self, conn):
        self.conn = conn
    
    def search_user(self, name):
        """ Search user in MySQL by name (which should be user id).
            Return: account_id. """
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM accounts WHERE full_name=%s"
            cursor.execute(sql, (name))
            results = cursor.fetchall()
            # The results is a tuple object - ((name, email, account_id),)
            if len(results):
                self.email = results[0][1]
                return results[0][2]
            else:
                return 0
        
    def create_user(self, name, email):
        """ Create new user if he or she doesn't exit. """
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO `accounts` (`full_name`, `preferred_email`)\
                       VALUES (%s, %s)"
                cursor.execute(sql, (name, email))
            self.conn.commit()
        except:
            self.conn.rollback()
    
    def check_email(self, name, email):
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
    
    def get_id(self, name, email):
        """ Get account id. """
        account_id = self.search_user(name)
        if account_id:
            self.check_email(name, email)
        else:
            self.create_user(name, email)
            account_id = self.search_user(name)
        return account_id
    
    def check_user(self):
        """ Check change owner, patchset uploader and approvals info. """
        # Get account id.
        owner_id = self.get_id(params.OWNER_NAME, params.OWNER_EMAIL)
        uploader_id = self.get_id(params.UPLOADER_NAME, params.UPLOADER_EMAIL)
        by_0_id = self.get_id(params.BY_0, params.BY_EMAIL_0)
        by_1_id = self.get_id(params.BY_1, params.BY_EMAIL_1)
        by_2_id = self.get_id(params.BY_2, params.BY_EMAIL_2)
        ids = {
            'OWNER_ACCOUNT_ID': str(owner_id),
            'UPLOADER_ACCOUNT_ID': str(uploader_id),
            'BY_0_ID': str(by_0_id),
            'BY_1_ID': str(by_1_id),
            'BY_2_ID': str(by_2_id),
            }
        
        # Write ids into params_file.
        params_file = 'params.py'
        try:
            with open(params_file, 'a') as f_obj:
                for key, value in sorted(ids.items()):
                    f_obj.write(key + " = " + value + "\n")
        except FileNotFuondError:
            print("Sorry, the file " + params_file + " does not exist.")