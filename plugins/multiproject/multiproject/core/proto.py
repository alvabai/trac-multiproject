import base64

from multiproject.core.db import admin_query, admin_transaction
from multiproject.core.configuration import Configuration
conf = Configuration.instance()


class ProtocolCache(object):
    def __init__(self):
        # Cache protocols for 15min
        self.CACHE_TIME = 15 * 60

    def set_project_protocols(self, project_id, type, protocols):
        mc = conf.getMemcachedInstance()
        mc.set(self.__key(project_id, type), protocols, self.CACHE_TIME)

    def get_project_protocols(self, project_id, type):
        mc = conf.getMemcachedInstance()
        return mc.get(self.__key(project_id, type))

    def clear_project_protocols(self, project_id, type):
        mc = conf.getMemcachedInstance()
        mc.delete(self.__key(project_id, type))

    def __key(self, project_id, type):
        project_id = str(project_id)
        key = "prjprtos:%s:%s" % (project_id, base64.b64encode(type))
        return key.encode('utf-8')


class ProtocolManager(object):
    protocols = None
    schemes = None

    def __init__(self, project_id):
        self.project_id = project_id
        self.__init_protos()
        self.__init_schemes()
        self.cache = ProtocolCache()

    @staticmethod
    def available_schemes(storage_type):
        """ Returns a list of schemes which are available for
            a given storage type
            
            storage type can be on of the following
            dav, git, svn, hg
            
            If illegal system parameter is given, returns an empty array
        """
        try:
            return ProtocolManager.schemes[storage_type]
        except:
            conf.log.error("Illegal system parameter '%s' for ProtocolManager.available_schemes" % str(storage_type))
            return []

    def allowed_protocols(self, storage_type):
        """ Returns a set of allowed schemes
        """
        available = self.available_schemes(storage_type)
        denied = self.denied_protocols(storage_type)
        return set(available) - denied

    def denied_protocols(self, storage_type):
        """ Returns a set of denied schemes
        """
        # Try from cache
        denied = self.cache.get_project_protocols(self.project_id, storage_type)
        if denied:
            return denied

        denied = []
        table = self._table_by_type(storage_type)

        query = """
        SELECT prt.scheme FROM `%s` AS dsp 
        INNER JOIN protocol AS prt 
           ON prt.protocol_id = dsp.protocol_key
        """ % table
        query += "WHERE dsp.project_key = %s"
        with admin_query() as cursor:
            try:
                cursor.execute(query, self.project_id)
                for row in cursor:
                    denied.append(row[0])
            except:
                conf.log.exception("Error occurred while reading project protocol list")
                raise

        self.cache.set_project_protocols(self.project_id, storage_type, set(denied))
        return set(denied)

    # Methods for changing project protocol settings
    def allow_protocols(self, names, storage_type):
        """ Allow protocol for a project
        """
        if not names:
            return

        table = self._table_by_type(storage_type)

        # Go through protocol keys, change them to string and join to be used SQL IN clause
        proto_keys = ','.join([str(key) for key in self._protocol_keys(names)])

        query = "DELETE FROM `%s`" % table
        query += "WHERE project_key = %s AND protocol_key IN (%s)" % (self.project_id, proto_keys)

        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Failed allowing protocol.")
                raise

        self.cache.clear_project_protocols(self.project_id, storage_type)

    def disallow_protocols(self, names, storage_type):
        """ DisAllow protocol for a project
        """
        if not names:
            return

        table = self._table_by_type(storage_type)

        values = []
        for name in names:
            values.append("(%d, %d)" % (self.project_id, ProtocolManager.protocols[name]))

        query = "REPLACE INTO `%s` " % table
        query += "VALUES %s" % ",".join(values)

        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Failed allowing protocol.")
                raise

        self.cache.clear_project_protocols(self.project_id, storage_type)

    def is_protocol_allowed(self, protocol, storage_type):
        protocol = protocol.lower()
        return protocol in self.allowed_protocols(storage_type)

    def _protocol_keys(self, names):
        return [ProtocolManager.protocols[name] for name in names]

    def _table_by_type(self, storage_type):
        table = 'deny_scm_protocol'
        if storage_type == 'dav':
            table = 'deny_dav_protocol'
        return table

    def __init_schemes(self):
        """ Scheme lists are initialized in priority
        order based on security
        """
        if ProtocolManager.schemes:
            return

        http_schemes = []
        if 'https' in ProtocolManager.protocols:
            http_schemes.append('https')
        if 'http' in ProtocolManager.protocols:
            http_schemes.append('http')

        schemes = {}
        schemes['svn'] = http_schemes
        schemes['hg'] = http_schemes
        schemes['dav'] = http_schemes

        if 'ssh' in ProtocolManager.protocols:
            schemes['git'] = ['ssh'] + http_schemes
        else:
            schemes['git'] = http_schemes

        ProtocolManager.schemes = schemes

    def __init_protos(self):
        if ProtocolManager.protocols:
            return

        ProtocolManager.protocols = self.__read_protos()

    def __read_protos(self):
        protos = {}
        query = "SELECT protocol_id, scheme FROM protocol"
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    protos[row[1]] = row[0]
            except:
                conf.log.exception("Failed reading a list of protocols")
                raise

        return protos
