
"""
CREATE TABLE locations (
name_id varchar(50) primary key,
name varchar(50) not null,
type varchar(50),
description varchar(255),
price real,
walk_time_min real,
location varchar(100)
);
"""

"""
CREATE TABLE aliases (
alias varchar(50) primary key,
name_id varchar(50) REFERENCES locations (name_id)
);
"""

"""
CREATE TABLE lunch_reviews (
entry_id serial PRIMARY KEY,
timestamp timestamptz,
suggested_lunch varchar(100),
weather varchar(100),
temp_f smallint,
user varchar(25) NOT NULL,
actual_lunch varchar(100) NOT NULL,
rating smallint check (rating BETWEEN 1 AND 10),
comment varchar(250)
);
"""
