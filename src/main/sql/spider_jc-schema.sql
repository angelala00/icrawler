
# -----------------------------------------------------------------------
# objectattr
# -----------------------------------------------------------------------
drop table if exists objectattr;

CREATE TABLE objectattr
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    website VARCHAR(25),
    attrname VARCHAR(15),
    reg VARCHAR(100),
    index INTEGER,
    createtime TIMESTAMP,
    updatetime TIMESTAMP,
    operator VARCHAR(10),
    PRIMARY KEY(id));


# -----------------------------------------------------------------------
# objectitem
# -----------------------------------------------------------------------
drop table if exists objectitem;

CREATE TABLE objectitem
(
    id INTEGER NOT NULL AUTO_INCREMENT,
    website VARCHAR(50),
    appname VARCHAR(50),
    appsize VARCHAR(10),
    appurl VARCHAR(100),
    imgurl VARCHAR(100),
    appdesc VARCHAR(500),
    createtime TIMESTAMP,
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
    createtime TIMESTAMP,
    updatetime TIMESTAMP,
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

ALTER TABLE objectattr
    ADD CONSTRAINT objectattr_FK_1
    FOREIGN KEY (website)
    REFERENCES site (website)
;

ALTER TABLE unvisitedurl
    ADD CONSTRAINT unvisitedurl_FK_1
    FOREIGN KEY (website)
    REFERENCES site (website)
;

ALTER TABLE visitedurl
    ADD CONSTRAINT visitedurl_FK_1
    FOREIGN KEY (website)
    REFERENCES site (website)
;

