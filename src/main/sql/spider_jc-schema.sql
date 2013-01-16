
# -----------------------------------------------------------------------
# city_dianping
# -----------------------------------------------------------------------
drop table if exists city_dianping;

CREATE TABLE city_dianping
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(20),
    url VARCHAR(100),
    url1 VARCHAR(100),
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# parser
# -----------------------------------------------------------------------
drop table if exists parser;

CREATE TABLE parser
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    id_task INTEGER,
    attr VARCHAR(30),
    pattern VARCHAR(100),
    methodtype VARCHAR(30),
    attr_name VARCHAR(30),
    nodatype VARCHAR(100),
    pid INTEGER,
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# parser_copy
# -----------------------------------------------------------------------
drop table if exists parser_copy;

CREATE TABLE parser_copy
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    id_task INTEGER,
    attr VARCHAR(30),
    pattern VARCHAR(100),
    methodtype VARCHAR(30),
    attr_name VARCHAR(30),
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# shangquan_dianping
# -----------------------------------------------------------------------
drop table if exists shangquan_dianping;

CREATE TABLE shangquan_dianping
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    city VARCHAR(30),
    distrist VARCHAR(30) NOT NULL,
    shangquan VARCHAR(30) NOT NULL,
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# site
# -----------------------------------------------------------------------
drop table if exists site;

CREATE TABLE site
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    website VARCHAR(25) NOT NULL,
    websitesuperurl VARCHAR(200),
    middlepageurlreg VARCHAR(100),
    targetpageurlreg VARCHAR(100),
    frequency VARCHAR(10),
    createtime TIMESTAMP NOT NULL,
    updatetime TIMESTAMP NOT NULL,
    operator VARCHAR(10),
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# storer
# -----------------------------------------------------------------------
drop table if exists storer;

CREATE TABLE storer
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    id_task INTEGER,
    fieldname VARCHAR(30),
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# task
# -----------------------------------------------------------------------
drop table if exists task;

CREATE TABLE task
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(30),
    id_prior INTEGER,
    id_next INTEGER,
    timetime INTEGER default 0,
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# unvisitedurl
# -----------------------------------------------------------------------
drop table if exists unvisitedurl;

CREATE TABLE unvisitedurl
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    id_task INTEGER,
    website VARCHAR(25),
    url VARCHAR(200) NOT NULL,
    timetime INTEGER default 0,
    fuzhubiaoshiid VARCHAR(300),
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# visitedurl
# -----------------------------------------------------------------------
drop table if exists visitedurl;

CREATE TABLE visitedurl
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    website VARCHAR(25),
    url VARCHAR(200) NOT NULL,
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# xiaohua
# -----------------------------------------------------------------------
drop table if exists xiaohua;

CREATE TABLE xiaohua
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    title VARCHAR(100),
    content VARCHAR(500),
    upcount VARCHAR(10),
    downcount VARCHAR(10),
    comentcount VARCHAR(10),
    tags VARCHAR(10),
    url VARCHAR(100),
    PRIMARY KEY(id));

