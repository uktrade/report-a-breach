Read.me
==============

ERD: ERD.jpg shows a the entity relationships. It has been created with PGAdmin. So some zooming in is required. Thank you
for your patience.

A MVP database used for testing : you will find a backup of the MVP database -  backup_mvp.sql.  All the data definition
are expressed in SQL DDL. Some views are created.

The sql scripts numbered [1-8] demonstrates how the database has been populated for testing the model against user requirements,
UI, and data consumption. This data can be used to test the implementation in Django. It would be a suitable exercise to review with the
data architect and validate the implementation.  Other testing strategies are suggested below.

Problems to address:

How are we going to capture and store the date of the breach?

Proposed series of test
-----------------------

The backup_mvp.sql constains a lot of contraints define as primary keys and foreign keys mainly. Also, some NOT NULL values are
specified. It would be useful to have a series of test that should pass if each constraint is respected. A successful
outcome should assess (1) the input of data we know should meet the  constraint and  (2) the input of data we know should not
meet the constraint. The latter should be added but an SQL error thrown.
