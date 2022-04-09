DROP DATABASE IF EXISTS db_TED_Talks;

CREATE DATABASE IF NOT EXISTS db_TED_Talks;

USE predicted_outputs();

DROP TABLE IF EXISTS table_outputs;
CREATE TABLE table_outputs
(
	age INT NOT NULL,
    month_value INT NOT NULL,
    probability FLOAT NOT NULL,
    prediction BIT NOT NULL
);
