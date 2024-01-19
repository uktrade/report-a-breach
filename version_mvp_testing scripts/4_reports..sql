/*** this scripts test the documents and the creation of a report ***/
DELETE FROM other_regime;
DELETE FROM document;
DELETE FROM report;
DELETE FROM report_type;




--- report types  at that moment in time we have only one. Several types for breaches should appear ---

INSERT INTO report_type (id, short_label, start_date)
VALUES (1, 'self-report','2024-1-1');

----  creation of reports --- 
/*
Please note the data range of the breach is captured in the questions and content. It should be added at a later stage 
during the investigation. It will be useful for analytical purposes. 

We simulate the user interaction flow of data. 
*/

--- report 1 ---
INSERT INTO report (id, unique_ref)
VALUES(1, 'ZY2345');

UPDATE report 
SET 
regime_id = 1
WHERE id = 1;

INSERT INTO other_regime(regime_id, description, report_id)
VALUES(1,'Another regime typed by the reporter',1);

INSERT INTO document (path, report_id, ref)
VALUES ('\\worm\ZY2345\evidence.docx', 1, 1);


--- report 2 ---

INSERT INTO report (id, unique_ref)
VALUES(2, 'ZY2346');



--- report 3 ---
INSERT INTO report (id, unique_ref)
VALUES(3, 'ZY2326');

UPDATE report 
SET 
regime_id = 3
WHERE id = 3;

INSERT INTO document (path, report_id, ref)
VALUES ('\\worm\ZY2326\evidence.docx', 3, 1);

INSERT INTO document (path, report_id, ref)
VALUES ('https://www.commandprompt.com/education/how-to-declare-a-variable-in-postgresql/', 3, 2);


--- report 4 ---

INSERT INTO report (id, unique_ref)
VALUES(4, 'ZX2346');

UPDATE report 
SET 
regime_id = 4
WHERE id = 4;

--- report 5 ---
INSERT INTO report (id, unique_ref)
VALUES(5, 'AB9999');

UPDATE report 
SET 
regime_id = 4
WHERE id = 5;
---

INSERT INTO report (id, unique_ref)
VALUES(6, 'AB9939');

UPDATE report 
SET 
regime_id = 4
WHERE id = 6;

---

INSERT INTO report (id, unique_ref)
VALUES(7, 'AC9999');

UPDATE report 
SET 
regime_id = 1
WHERE id = 7;

INSERT INTO other_regime(regime_id, description, report_id)
VALUES(1,'Somewhere in Russia',7);
----

INSERT INTO report (id, unique_ref)
VALUES(8, 'AB9990');

UPDATE report 
SET 
regime_id = 3
WHERE id = 8;


INSERT INTO document (path, report_id, ref)
VALUES ('\\worm\invoices.xls', 8, 1);

---

SELECT 
B.unique_ref as unique_ref,
A.ref        as document_ref,
A.creation_date as document_creation_date,
A.path  as path,
B.id AS report_id
FROM document A
INNER JOIN report B on A.report_id = B.id
		








