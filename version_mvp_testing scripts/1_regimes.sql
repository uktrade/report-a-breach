/******
This script test the table regime and its constraints.
*****/

-- for testing only
DELETE FROM content;
DELETE FROM document;
DELETE FROM report_company;
DELETE FROM report_reporter;
DELETE FROM other_regime;
DELETE FROM report;
DELETE FROM regime;

-- INSERT VALUES
-- default to report foreign key
INSERT INTO regime(id, short_name, full_name, start_date)
VALUES(0, 'NOT KNOWN', 'I do not know', '1/1/2000');

-- default value for other_regime
INSERT INTO regime(id, short_name, full_name, start_date)
VALUES(1, 'OTHER REGIME', 'Other regime', '1/1/2000');

-- those other rows should be managed as an admin tools within the system.
INSERT INTO regime(id, short_name, full_name, start_date)
VALUES (3, 'AFGHANISTAN_2020', 'The Afghanistan (Sanctions) (EU Exit) Regulations 2020', '1/1/2020');

INSERT INTO regime(id, short_name, full_name, start_date)
VALUES (4, 'BELARUS_2020', 'The Republic of Belarus (Sanctions) (EU Exit) Regulations 2019', '1/1/2019');



-- should fail -- for testing purposes
--INSERT INTO other_regime(description)
--VALUES('Another regime that is not listed');


-- This insert is just for testing purposes.
INSERT INTO regime(id, short_name, full_name, start_date, shown_gui_flag)
VALUES(666, 'NOT SHOWN', 'Not Shown for testing purposes', '1/1/2000', False);

--=- A view referred as regimes_list has been created for consumption purposes

SELECT *
FROM regimes_list;
