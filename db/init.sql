CREATE DATABASE covidInsight;
use covidInsight;

CREATE TABLE IF NOT EXISTS users(
    id        INTEGER(5) NOT NULL AUTO_INCREMENT
   , name       VARCHAR(30) NOT NULL
  ,email        VARCHAR(50) NOT NULL
  ,username     VARCHAR(25)  NOT NULL
  ,password     VARCHAR(50)  NOT NULL
  ,PRIMARY KEY (id)
);