"""
Script to convert MySQL dump 10.13 into 10.11 version with some modifications.

Prints out the result into stdout.

Since in production, we have db dump version 10.13, and the existing
empty database dump is 10.11, we cannot diff them straight away, but
need to modify the db dump from production.

Usage: python db_dump_filter.py db_dump_from_production.sql

.. TODO::

- Allow adding (empty) data parts into generated file if they are not
  provided by the imported dump. This means that the primary key is
  parsed from the table structure.
- Turn this into proper parsing with states, etc.

"""

__author__ = 'alhannin'
import sys
import re

def main():

    end_of_table_with_autoincrement_re = None
    is_analytical = False

    if len(sys.argv) < 2:
        print "Provide mysqldump file as first argument"
        exit()
    if sys.argv[1].find('analytical') != -1:
        is_analytical = True
    file = open(sys.argv[1],'r')
    line_number = 0
    line = ''

    end_of_file = False

    while not end_of_file:
        line_number += 1
        line = file.next()

        if line.startswith("DELIMITER ;;"):
            break
        if line == "SET @saved_cs_client     = @@character_set_client;\n":
            line_number += 1
            line = file.next()
            if line == "SET character_set_client = utf8;\n":
                sys.stdout.write("""/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
""")
            else:
                sys.stderr.write("Error at line %d, did not receive expected line: SET character_set_client = utf8;\n" % line_number)
        else:
            if not end_of_table_with_autoincrement_re:
                if not is_analytical:
                    end_of_table_with_autoincrement_re = re.compile(r"^\) ENGINE=([a-zA-Z]+)( AUTO_INCREMENT=\d*)? DEFAULT CHARSET=utf8( COLLATE=utf8_bin)?( COMMENT='[^']*')?;$")
                else:
                    end_of_table_with_autoincrement_re = re.compile(r"^\) ENGINE=([a-zA-Z]+)( AUTO_INCREMENT=\d*)? DEFAULT CHARSET=utf8( COLLATE=utf8_bin)?( COMMENT='[^']*')?")
            end_of_line_match = end_of_table_with_autoincrement_re.match(line)
            if end_of_line_match:
                engine = end_of_line_match.group(1)

                auto_increment = end_of_line_match.group(2)
                auto_increment_start = ' AUTO_INCREMENT='

                collate = end_of_line_match.group(3)
                collate_start = " COLLATE="

                comment = end_of_line_match.group(4)
                comment_start = ' COMMENT='

                if collate and not collate.startswith(collate_start):
                    if collate.startswith(comment_start):
                        collate, comment = comment, collate
                        collate = ''
                    else:
                        sys.stderr.write("Error at line %d, collate_start invalid: '%s' %s\n" % (line_number, collate, line))
                if not collate:
                    collate = ''
                if comment and not comment.startswith(comment_start):
                    sys.stderr.write("Error at line %d, comment_start invalid: '%s'\n" % (line_number, comment))
                if not comment:
                    comment = ''
                if auto_increment and not auto_increment.startswith(auto_increment_start):
                    sys.stderr.write("Error at line %d, auto_increment invalid: '%s'\n" % (line_number, auto_increment))
                if not auto_increment:
                    auto_increment = ''
                else:
                    auto_increment = ''
                line_number += 1
                next_line = file.next()
                if next_line != "SET character_set_client = @saved_cs_client;\n":
                    if not is_analytical:
                        sys.stderr.write("Error at line %d, did not receive expected line: SET character_set_client = @saved_cs_client;\n'%s'\n" % (line_number, next_line))
                    else:
                        sys.stdout.write(""") ENGINE=%(engine)s%(auto_increment)s DEFAULT CHARSET=utf8%(collate)s%(comment)s\n""" %
                                         {'engine' : engine, 'auto_increment': auto_increment, 'collate': collate, 'comment': comment})
                        while True:
                            sys.stdout.write(next_line)
                            line_number += 1
                            next_line = file.next()
                            if next_line.find('PARTITION') != 1:
                                if next_line != "SET character_set_client = @saved_cs_client;\n":
                                    sys.stderr.write("Error at line %d, did not receive expected line in analytical: SET character_set_client = @saved_cs_client;\n'%s'\n" % (line_number, next_line))
                                else:
                                    print "/*!40101 SET character_set_client = @saved_cs_client */;\n"
                                    break
                else:
                    sys.stdout.write(""") ENGINE=%(engine)s%(auto_increment)s DEFAULT CHARSET=utf8%(collate)s%(comment)s;
/*!40101 SET character_set_client = @saved_cs_client */;
""" % {'engine' : engine, 'auto_increment': auto_increment, 'collate': collate, 'comment': comment})
            elif line.startswith(') ENGINE'):
                sys.stderr.write("Error at line %d, line started with ') ENGINE' but did not continue correctly: \n%s\n" % (line_number, line))
            else:
                sys.stdout.write(line)

    # first drop procedure needs special handling

    line_number += 1
    line = file.next()
    # "DELIMITER ;;" was already read

    drop_procedure_re = re.compile(r"^\/\*!50003 DROP PROCEDURE IF EXISTS `(\w+)` \*\/;;")
    drop_procedure_match = drop_procedure_re.match(line)
    drop_procedure_name = ''
    create_procedure_name = ''
    params = ''
    if drop_procedure_match:
        drop_procedure_name = drop_procedure_match.group(1)

        line_number += 1
        line = file.next()
        expected = """/*!50003 SET SESSION SQL_MODE=""*/;;\n"""
        if line == expected:
            sys.stdout.write("""/*!50003 DROP PROCEDURE IF EXISTS `%s` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
""" % drop_procedure_name)
        else:
            sys.stderr.write("""Error at line %d, did not receive expected line: \n'%s'\n'%s'\n""" % (line_number, expected, line))
    else:
        sys.stderr.write("""Error at line %d, did not receive expected line: '/*!50003 DROP PROCEDURE IF EXISTS `([^`])` */;;'\n'%s'\n""" % (line_number, line))

    create_procedure_re = re.compile(r"/\*!50003 CREATE\*/ /\*!50020 DEFINER=`(?:root|tracuser)`@`(?:localhost|10\.0\.0\.3|%)`\*\/ /\*!50003 PROCEDURE `(\w*)`(.*)$")

    # LOOP:
    while True:
        try:
            line = file.next()
            line_number += 1
        except StopIteration:
            break
        create_procedure_match = create_procedure_re.match(line)
        drop_procedure_match = drop_procedure_re.match(line)
        if create_procedure_match:
            create_procedure_name = create_procedure_match.group(1)
            params = create_procedure_match.group(2)
            sys.stdout.write("/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`%%`*/ /*!50003 PROCEDURE `%s`%s\n" % (create_procedure_name, params))
        elif line.startswith("""/*!50003 CREATE*/ /*!50020"""):
            sys.stderr.write("""Error at line %d, did not receive expected line: '/*!50003 CREATE*/ /*!50020'\n'%s'\n""" % (line_number, line))
        elif line == "/*!50003 SET SESSION SQL_MODE=@OLD_SQL_MODE*/;;\n":
            sys.stdout.write( """DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
""")
        elif drop_procedure_match:
            drop_procedure_name = drop_procedure_match.group(1)
            sys.stdout.write( "/*!50003 DROP PROCEDURE IF EXISTS `%s` */;\n" % drop_procedure_name)
        elif line.startswith("""/*!50003 CREATE*/ /*!50020 DEFINER"""):
            sys.stderr.write("""Error at line %d, did not receive expected line: '/*!50003 CREATE*/ /*!50020 DEFINER'\n'%s'\n""" % (line_number, line))
        elif line == '/*!50003 SET SESSION SQL_MODE=""*/;;\n':
            sys.stdout.write("""/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
""")
        else:
            sys.stdout.write(line)

if __name__== '__main__':
    main()
