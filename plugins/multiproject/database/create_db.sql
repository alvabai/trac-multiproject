DROP DATABASE IF EXISTS trac_admin;
CREATE DATABASE trac_admin DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
DROP USER 'tracuser';
CREATE USER 'tracuser' IDENTIFIED BY 'password';
DROP USER tracuser@localhost;
CREATE USER tracuser@localhost IDENTIFIED BY 'password';
GRANT ALL ON *.* TO 'tracuser'@'localhost';
FLUSH PRIVILEGES;
