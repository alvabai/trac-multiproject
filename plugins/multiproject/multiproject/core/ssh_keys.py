import base64
import os
import re
import struct

import MySQLdb

from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.multiproj_exceptions import SingletonExistsException
from multiproject.core.db import admin_query, admin_transaction
from multiproject.core.users import get_userstore


class CQDESshKeyStore(object):
    """ DAO for contexts and categories
    """
    __instance = None

    def __init__(self):
        if CQDESshKeyStore.__instance:
            raise SingletonExistsException("Use CQDESshKeyStore.instance()")

    @staticmethod
    def instance():
        if CQDESshKeyStore.__instance is None:
            CQDESshKeyStore.__instance = CQDESshKeyStore()
        return CQDESshKeyStore.__instance

    def get_all_ssh_keys(self):
        """ Returns all ssh keys from database
        """
        keys = []
        query = """
        SELECT key_id, user_id, ssh_key, comment, added
        FROM ssh_keys
        """

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    keys.append(SshKey.from_sql_row(row))
            except:
                conf.log.exception("Exception. get_all_ssh_keys procedure failed: %s" % query)

        return keys

    def get_ssh_keys_by_user_id(self, user_id):
        """ Returns ssh keys for user
        """
        if not user_id:
            return None

        keys = []

        query = """
        SELECT key_id, user_id, ssh_key, comment, added
        FROM ssh_keys
        WHERE user_id = %s
        """

        with admin_query() as cursor:
            try:
                cursor.execute(query, (user_id,))
                for row in cursor:
                    keys.append(SshKey.from_sql_row(row))
            except:
                conf.log.exception("Exception. get_ssh_keys_by_user_id(%s) procedure failed: %s" %
                                   (str(user_id), query))

        return keys

    def add_ssh_key(self, user_id, ssh_key, description):
        """ Add a new ssh key for user
        """
        query = """
        INSERT INTO ssh_keys
        VALUES(NULL, %s, %s, %s, NOW())
        """
        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (user_id, ssh_key, description))
            except:
                conf.log.exception("Failed to add SSH key")
                return False

        if not self.add_ssh_key_update_flag():
            return False

        return True

    def remove_ssh_key(self, user_id, key_id):
        """ Remove a category
        """
        if not user_id or not key_id:
            return False

        query = """
        DELETE FROM ssh_keys
        WHERE
            user_id = %s AND
            key_id = %s
        """
        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (user_id, key_id))
            except:
                conf.log.exception("Failed to delete ssh key")
                return False

        if not self.add_ssh_key_update_flag():
            return False

        return True

    def add_ssh_key_update_flag(self):
        """ Add a new flag for ssh key update request if none exists
        """

        # if update flag has been already raised we don't need another
        list = self.get_ssh_key_update_flags()
        if len(list) > 0:
            return True

        query = "INSERT INTO ssh_key_update VALUES(NULL, NOW())"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Exception. add_ssh_key_update_flag procedure failed: %s" % query)
                return False

        return True

    def clean_ssh_key_update_flags(self):
        """ Cleans ssh key update flags
        """
        query = "DELETE FROM ssh_key_update"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Exception. clean_ssh_key_update_flags procedure failed: %s" % query)
                return False

        return True

    def perform_ssh_key_update(self, target_path):
        """ Performs ssh key generation if needed
        """
        if not target_path or target_path == "":
            return False

        if not target_path[-1] == "/":
            target_path += "/"

        keydir = target_path + "keydir/"

        # keydir must exists and be empty
        if not os.path.exists(keydir) or os.listdir(keydir):
            return False

        update_ids = self.get_ssh_key_update_flags()

        # no flags raised, no updates needed
        if not len(update_ids):
            return True

        if self.clean_ssh_key_update_flags():
            count = self.generate_all_ssh_key_files(keydir)
            conf.log.info("Updated %d gitosis SSH keys" % count)
        else:
            return False

        return True

    def get_ssh_key_update_flags(self):
        """ Fetches update flags from database
        """
        update_ids = []

        query = "SELECT update_id,added FROM ssh_key_update"
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    update_ids.append(row[0])
            except:
                conf.log.exception("Exception. get_ssh_key_update_flags procedure failed: %s" % query)

        return update_ids

    def generate_ssh_key_file(self, user_name, ssh_key, keydir):
        """ Generates a single ssh key file to a location specified
            with gitosis_clone_path in project.ini
        """
        if not keydir or not user_name or user_name == "":
            return False

        if not keydir[-1] == "/":
            keydir += "/"

        if os.path.exists(keydir):
            keyfile = keydir + user_name + ".pub"
            if not os.path.exists(keyfile):
                try:
                    file = open(keyfile, 'w')
                    file.write(ssh_key)
                    file.close()
                except EnvironmentError:
                    conf.log.debug("Gitosis ssh key update: could not write keyfile %s" % keyfile)
            else:
                conf.log.debug("Gitosis ssh key update: key for %s existed" % user_name)
                return False
        else:
            return False

        return True

    def generate_all_ssh_key_files(self, keydir):
        """ Generates all ssh keys found in database to a location
            specified with with gitosis_clone_path in project.ini
        """
        keys = self.get_all_ssh_keys()

        if not keys:
            return 0

        count = 0
        users = get_userstore()

        for key in keys:
            user = users.getUserWhereId(key.user_id)
            if self.generate_ssh_key_file(user.username, key.ssh_key, keydir):
                count += 1

        return count


class SshKey(object):
    """ Class for database ssh key entities
    """

    def __init__(self):
        self.key_id = None
        self.user_id = None
        self.ssh_key = None
        self.description = None
        self.added = None

    @staticmethod
    def from_sql_row(row):
        """ Static factory method
        """
        key = SshKey()
        if len(row) != 5:
            return None

        key.key_id = row[0]
        key.user_id = row[1]
        key.ssh_key = row[2]
        key.description = row[3]
        key.added = row[4]
        return key

    @staticmethod
    def remove_comment_from_key_string(key):
        """
        Remove comment field from the end of the SSH key string::

            # <format> <key> <comment>
            ssh-rsa ae32342cdaefedaceeaefa foo@localhost

        """
        if key:
            list = key.split()
            if len(list) > 2:
                key = "%s %s" % (list[0], list[1])

        return key

    @staticmethod
    def validate_key_string(key):
        """ Attempt to validate an SSH key in string format
        """
        if not key: # no key automatically fails
            return False

        try:
            list = key.split()

            if len(list) < 2: # first two are type and the key
                return False

            if len(list[1]) < 300: # too few characters in the key
                return False

            if len(list[1]) > 750: # too many characters in the key
                return False

            if re.search(r'[^\=\+\/a-zA-Z0-9]', list[1]): # allowed base64 characters
                return False

            data = base64.b64decode(list[1]) # discovers invalid base64 padding

            int_len = 4
            str_len = struct.unpack('>I', data[:int_len])[0] # this should return 7

            if str_len != 7:
                return False

            if not data[int_len:int_len + str_len] == list[0]:
                return False
        except:
            return False

        return True

    def __repr__(self):
        return "<SshKey:" + str(self.key_id) +\
               ":" + str(self.user_id) +\
               ":" + str(self.ssh_key) +\
               ":" + str(self.description) +\
               ":" + str(self.added) + ">"
