# -*- coding: utf-8 -*-
from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, safe_int

class CategoryBrowser(object):
    """ Class used for browsing categories
    """

    def find_categories(self, category_id_list):
        """
        """
        if not category_id_list:
            return []

        query = ("SELECT category_name FROM categories WHERE category_id in (%s)" %
                 ",".join(str(safe_int(item)) for item in category_id_list))

        data = []
        with admin_query() as cursor:
            try:
                conf.log.debug(query)
                cursor.execute(query)

                for row in cursor:
                    data.append(row[0])
            except:
                conf.log.exception("CategoryBrowser.find_categories query failed '''%s'''" % query)
                raise

        return data
