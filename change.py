# -*- coding: utf-8 -*-
import pymysql
import time

from account import Account

class Change():
    """ Insert new change and new accounts into database,
        update account email if it has been changed. """
    def __init__(self, conn, dict):
        self.conn = conn
        # Change info
        self.change_id = 0
        self.change_key = dict['id']
        self.project = dict['project']
        self.branch = dict['branch']
        # Struct time format (default is timestamp)
        self.created_on = time.strftime("%Y-%m-%d %H:%M:%S",
                               time.localtime(dict['createdOn']))
        # Patchset info
        self.revision = dict['currentPatchSet']['revision']
        self.size_insertions = dict['currentPatchSet']['sizeInsertions']
        self.size_deletions = dict['currentPatchSet']['sizeDeletions']
        self.approvals = dict['currentPatchSet']['approvals']
        self.patchset_id = dict['currentPatchSet']['number']
        # Accounts
        self.owner_id = 0
        self.owner_name = dict['owner']['name']
        self.owner_email = dict['owner']['email']
        self.uploader_id = 0
        self.uploader_name = dict['currentPatchSet']['uploader']['name']
        self.uploader_email = dict['currentPatchSet']['uploader']['email']
    
    def search_change(self):
        """ Get change id in database. """
        with self.conn.cursor() as cursor:
            sql = "SELECT `change_id` FROM `changes` WHERE change_key=%s"
            cursor.execute(sql, (self.change_key))
            results = cursor.fetchall()
            # The results is a tuple object - ((change_id),)
            if len(results):
                self.change_id = results[0][0]
    
        
    def create_change(self):
        """ Insert new gerrit change into database. """
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO `changes` (`change_key`, \
                                              `created_on`, \
                                              `owner_account_id`, \
                                              `dest_project_name`, \
                                              `dest_branch_name`, \
                                              `status`, \
                                              `current_patch_set_id` ) \
                       VALUES (%s, %s, %s, %s, %s, 'M', %s)"
                cursor.execute(sql, (self.change_key,
                                     self.created_on,
                                     self.owner_id,
                                     self.project,
                                     self.branch,
                                     self.patchset_id))
            self.conn.commit()
        except:
            self.conn.rollback()
        else:
            # Set change id.
            self.search_change()
    
    def create_patch_set(self):
        """ Insert new gerrit change patchset into database. """
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO `patch_sets` (\
                                    `revision`,\
                                    `uploader_account_id`,\
                                    `size_insertions`,\
                                    `size_deletions`,\
                                    `change_id`,\
                                    `patch_set_id` )\
                       VALUES ( %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (self.revision,
                                     self.uploader_id,
                                     self.size_insertions,
                                     self.size_deletions,
                                     self.change_id,
                                     self.patchset_id))
            self.conn.commit()
        except:
            self.conn.rollback()
    
    def create_patch_set_approvals(self):
        """ Insert new gerrit change patchset approvals into database. """                
        for approval in self.approvals:
            # There could be multi-reivewers.
            if approval['type'] == 'Code-Review':
                r_value = approval['value']
                r_granted = time.strftime("%Y-%m-%d %H:%M:%S",
                                 time.localtime(approval['grantedOn']))
                r_name = approval['by']['name']
                r_email = approval['by']['email']
                r = Account(self.conn, r_name, r_email)
                r_id = r.get_account_id()
                try:
                    with self.conn.cursor() as cursor:
                        sql = "INSERT INTO `patch_set_approvals` (\
                                            `value`,\
                                            `granted`,\
                                            `change_id`,\
                                            `patch_set_id`,\
                                            `account_id`,\
                                            `category_id`)\
                               VALUES (%s, %s, %s, %s, %s, 'Code-Review')"
                        cursor.execute(sql, (r_value,
                                             r_granted,
                                             self.change_id,
                                             self.patchset_id,
                                             r_id))
                    self.conn.commit()
                except:
                    self.conn.rollback()
    
    def check_change(self):
        """ Create new change into database. """
        # Get change owner, patchset uploader and approvals account id.
        owner = Account(self.conn, self.owner_name, self.owner_email)
        self.owner_id = owner.get_account_id()
        uploader = Account(self.conn, self.uploader_name, self.uploader_email)
        self.uploader_id = uploader.get_account_id()
        
        # Set change info
        self.search_change()
        if self.change_id == 0:
            self.create_change()
            self.create_patch_set()
            self.create_patch_set_approvals()
            print("[Info] insert new change into statisdb: %s" % self.change_key)
        else:
            print("The change: %s has already exist." % self.change_key)