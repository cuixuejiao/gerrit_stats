# -*- coding: utf-8 -*-
import pymysql

import params

class Change():
    """ Write change dict into database. """
    def __init__(self, conn):
        self.conn = conn
        self.change_id = 0
    
    def get_change_id(self, change_key):
        """ Get change id in MySQL by change_key. """
        with self.conn.cursor() as cursor:
            sql = "SELECT `change_id` FROM `changes` WHERE change_key=%s"
            cursor.execute(sql, (change_key))
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
                                              `last_updated_on`, \
                                              `owner_account_id`, \
                                              `dest_project_name`, \
                                              `dest_branch_name`, \
                                              `status`, \
                                              `current_patch_set_id` ) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (params.CHANGE_KEY,
                                     params.CREATED_ON,
                                     params.LAST_UPDATED_ON,
                                     params.OWNER_ACCOUNT_ID,
                                     params.DEST_PROJECT_NAME,
                                     params.DEST_BRANCH_NAME,
                                     'M',
                                     params.CURRENT_PATCH_SET_ID))
            self.conn.commit()
        except:
            self.conn.rollback()
        # Write change_id into params_file.
        self.get_change_id(params.CHANGE_KEY)
    
    def create_patch_set(self):
        """ Insert new gerrit change patchset into database. """
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO `patch_sets` (`revision`, \
                                                 `uploader_account_id`, \
                                                 `size_insertions`, \
                                                 `size_deletions`, \
                                                 `change_id`, \
                                                 `patch_set_id` ) \
                       VALUES ( %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (params.REVISION,
                                     params.UPLOADER_ACCOUNT_ID,
                                     params.SIZE_INSERTIONS,
                                     params.SIZE_DELETIONS,
                                     self.change_id,
                                     params.CURRENT_PATCH_SET_ID))
            self.conn.commit()
        except:
            self.conn.rollback()
    
    def create_patch_set_approvals(self):
        """ Insert new gerrit change patchset approvals into database. """
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO `patch_set_approvals` (`value`, \
                                                          `granted`, \
                                                          `change_id`, \
                                                          `patch_set_id`, \
                                                          `account_id`, \
                                                          `category_id`) \
                       VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (params.VALUE_0,
                                     params.GRANTED_0,
                                     self.change_id,
                                     params.CURRENT_PATCH_SET_ID,
                                     params.BY_0_ID,
                                     params.CATEGORY_ID_0))
                cursor.execute(sql, (params.VALUE_1,
                                     params.GRANTED_1,
                                     self.change_id,
                                     params.CURRENT_PATCH_SET_ID,
                                     params.BY_1_ID,
                                     params.CATEGORY_ID_1))
                cursor.execute(sql, (params.VALUE_2,
                                     params.GRANTED_2,
                                     self.change_id,
                                     params.CURRENT_PATCH_SET_ID,
                                     params.BY_2_ID,
                                     params.CATEGORY_ID_2))
            self.conn.commit()
        except:
            self.conn.rollback()
    
    def check_change(self):
        """ Create new change into database if it doesn't exist. """
        self.get_change_id(params.CHANGE_KEY)
        if self.change_id == 0:
            self.create_change()
            self.create_patch_set()
            self.create_patch_set_approvals()