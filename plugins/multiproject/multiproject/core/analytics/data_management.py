from multiproject.core.analytics.dimension import DateDimension
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
from multiproject.core.db import analytical_query, analytical_transaction


class AnalyticalDataManagement(object):
    def __init__(self):
        self.data_management_plans = []

    def _read_data_management_plans(self):
        """ Reads current data management plan table
        """
        self.data_management_plans = []
        query = ("SELECT `table`, buffer_partitions, partition_size, partition_count, archive_table, "
                 "VALID_FROM, VALID_TO FROM data_management")

        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor.fetchall():
                    self.data_management_plans.append(TableDataManagementPlan(row))
            except:
                conf.log.exception("Failed reading data management plans")

    def rotate_partitions(self):
        # Create new partitions if necessary
        self._read_data_management_plans()
        for plan in self.data_management_plans:
            if plan.needs_new_partitions:
                self.add_new_partitions(plan)

        # Drop old partitions if necessary
        self._read_data_management_plans()
        for plan in self.data_management_plans:
            if plan.needs_to_drop_partitions:
                self.drop_aged_partitions(plan)

    def add_new_partitions(self, table_plan):
        date = DateDimension()
        now = date.date_sk_utcnow()

        # Calculate partition limits
        latest = table_plan.partitions[-1]
        step = table_plan.partition_size
        first = latest + step
        limit = now + (table_plan.partition_size * (table_plan.buffer_partitions + 1))

        if limit <= first:
            return

        # Create sql statement
        partitions = []
        for partition in range(first, limit, step):
            partitions.append("PARTITION p_%d VALUES LESS THAN (%d)" % (partition, partition))
        sql = "ALTER TABLE %s ADD PARTITION (%s)" % (table_plan.table, ','.join(partitions))

        # Run partitioning command
        with analytical_transaction() as cursor:
            try:
                cursor.execute(sql)
            except:
                conf.log.exception("Adding partitions FAILED! %s" % sql)

        conf.log.info("Added partitions for %s" % table_plan.table)

    def drop_aged_partitions(self, table_plan):
        """
        Drop aged partitions from the end so that max_partitions rule holds
        """
        partitions_to_drop = len(table_plan.partitions) - table_plan.max_partitions

        # Sanity check calculation and then run
        if 0 < partitions_to_drop < table_plan.partitions:
            with analytical_transaction() as cursor:
                for partition in table_plan.partitions[:partitions_to_drop]:
                    partition_name = 'p_%s' % partition
                    drop_clause = "ALTER TABLE %s DROP PARTITION %s" % (table_plan.table, partition_name)
                    try:
                        cursor.execute(drop_clause)
                    except:
                        conf.log.exception("Unable to drop partition from table. %s" % drop_clause)
                    conf.log.info("Dropped partitions for %s" % table_plan.table)


class TableDataManagementPlan(object):
    def __init__(self, row):
        self.table = row[0]
        self.buffer_partitions = row[1]
        self.partition_size = row[2]
        self.partition_count = row[3]
        self.archive_table = row[4]
        self.VALID_FROM = row[5]
        self.VALID_TO = row[6]

        self.max_partitions = self.buffer_partitions + self.partition_count
        self.partitions = self._partitions()

    def needs_new_partitions(self):
        date = DateDimension()
        now = date.date_sk_utcnow()
        return self.partitions[-1] < now + (self.partition_size * self.buffer_partitions + 1)

    def needs_to_drop_partitions(self):
        return len(self.partitions) > self.max_partitions

    def _partitions(self):
        query = "EXPLAIN PARTITIONS SELECT * FROM %s" % self.table

        row = []

        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Failed reading partitions from the database")

        partition_names = []
        if len(row) > 3:
            partition_names = row[3].split(',')

        partitions = []
        for partition_name in partition_names:
            partitions.append(int(partition_name.split('_')[1]))
        return partitions
