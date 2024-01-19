/****
this script tests and validate the reporters and relationship to the breach.
****/

DELETE FROM report_reporter;
DELETE FROM relationship;
DELETE FROM verification_code;
DELETE FROM reporter;


-- Those entries matches the prototypes late 2023-12
--- relationship entries.
INSERT INTO relationship(id, short_name, full_name, shown_gui_flag)
VALUES(0 , 'unknown', 'email not verified', FALSE);

INSERT INTO relationship(id, short_name, full_name)
VALUES(1, 'employee/owner', ' I am an owner, officer or employee of the company, or I am the person');

INSERT INTO relationship(id, short_name, full_name)
VALUES(2, 'voluntary_dec', 'I do not work for the company or person, but I am acting on their behalf to make a voluntary declation.');

INSERT INTO relationship(id, short_name, full_name)
VALUES(3, 'third_party', 'I work for a third party with a legal responsibility to make a mandatory declaration');

INSERT INTO relationship(id, short_name, full_name)
VALUES(4, 'no_relationship', 'I do not have a professional relationship with the company or person, or I no longer have a professional relationship with them.');

INSERT INTO relationship(id, short_name, full_name, start_date, end_date, shown_gui_flag)
VALUES(5, 'test_only', 'testing only ignore me', '2000-1-1','2000-1-2', False);

-- this should fails
--INSERT INTO relationship(id, short_name, full_name, start_date, end_date, shown_gui_flag)
--VALUES(5, 'test_only', 'testing only ignore me', '2000-1-1','2000-1-2', False);

---INSERT INTO relationship(id)
---VALUES(999);

-- This process aims at simulating the order of input from the UI
---- everything goes well
INSERT INTO reporter (id, full_name)
VALUES(1, 'Mickey Mouse');

UPDATE reporter
SET
email = 'mickey.mouse@disney.com'
WHERE id = 1;

INSERT INTO verification_code(reporter_id, code)
VALUES(1, 'AB4617');

UPDATE verification_code
SET
succesful_verification_date = CURRENT_TIMESTAMP
WHERE
reporter_id = 1;

UPDATE reporter
SET
email_verified  = TRUE
WHERE id = 1;


------- not verified the email
INSERT INTO reporter (id, full_name)
VALUES(2, 'Donald Duck');

UPDATE reporter
SET
email = 'donald.duck@disney.com'
WHERE id = 2;

INSERT INTO verification_code(reporter_id, code)
VALUES(2, 'CT8308');



---- everything goes well
INSERT INTO reporter (id, full_name)
VALUES(3, 'Pocahontas');

UPDATE reporter
SET
email = 'pocahontas@disney.com'
WHERE id = 3;

INSERT INTO verification_code(reporter_id, code)
VALUES(3, 'GR1234');

UPDATE verification_code
SET
succesful_verification_date = CURRENT_TIMESTAMP
WHERE
reporter_id = 3;

UPDATE reporter
SET
email_verified  = TRUE
WHERE id = 3;



---- everything goes well
INSERT INTO reporter (id, full_name)
VALUES(4, 'Cruella Devil');

UPDATE reporter
SET
email = 'cruella.devil@disney.com'
WHERE id = 4;

INSERT INTO verification_code(reporter_id, code)
VALUES(4, 'WE8917');

UPDATE verification_code
SET
succesful_verification_date = CURRENT_TIMESTAMP
WHERE
reporter_id = 4;

UPDATE reporter
SET
email_verified  = TRUE
WHERE id = 4;

----

INSERT INTO reporter (id, full_name)
VALUES(5, 'Jack Sparrow');

UPDATE reporter
SET
email = 'jack.sparrow@disney.com'
WHERE id = 5;

INSERT INTO verification_code(reporter_id, code, creation_date_time)
VALUES(5, 'YS3951', CURRENT_TIMESTAMP - INTERVAL '1 day');

INSERT INTO verification_code(reporter_id, code)
VALUES(5, 'IM0214');

UPDATE verification_code
SET
succesful_verification_date = CURRENT_TIMESTAMP
WHERE
reporter_id = 5;

UPDATE reporter
SET
email_verified  = TRUE
WHERE id = 5;

----

INSERT INTO reporter (id, full_name)
VALUES(6, 'Rex');

UPDATE reporter
SET
email = 'rex@disney.com'
WHERE id = 6;

INSERT INTO verification_code(reporter_id, code)
VALUES(6, 'LU7654');

UPDATE verification_code
SET
succesful_verification_date = CURRENT_TIMESTAMP
WHERE
reporter_id = 6;

UPDATE reporter
SET
email_verified  = TRUE
WHERE id = 6;


SELECT *
FROM reporters_list;

/*
SELECT relationship, count(*)
FROM reporters
GROUP BY relationship

*/
