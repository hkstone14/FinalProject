CREATE DATABASE covidInsight;
use covidInsight;

CREATE TABLE IF NOT EXISTS users(
    id        INTEGER(5) NOT NULL AUTO_INCREMENT
  ,email        VARCHAR(50) NOT NULL
  ,username     VARCHAR (20) NOT NULL
  ,password     VARCHAR(50)  NOT NULL
  ,PRIMARY KEY (id)
);
INSERT INTO users(email,username,password) VALUES ('admin@gmail.com','admin123','admin@1234');
INSERT INTO users(email,username,password) VALUES ('hari14@gmail.com','hk1234','hk@1234');