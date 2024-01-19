/* this script tests the companies reported within a report of breach */

DELETE FROM company_uk_ch;
DELETE FROM company_uk_non_ch;
DELETE FROM company_non_uk;
DELETE FROM company;
DELETE FROM company_type;
DELETE FROM company_role;
DELETE FROM report_company;
--DROP VIEW report_companies;

INSERT INTO company_type(id, short_label, long_label)
VALUES (0, 'no_type_yet', 'no type has been set yet.');

-- Are you reporting a limited company which is registered with Companies House? Yes --
INSERT INTO company_role(id, role)
VALUES(1, 'suspected supplier');

INSERT INTO company_type(id, short_label, long_label)
VALUES (1, 'uk_companies_house', 'UK limited companies registered with companies house');

INSERT INTO company(id, company_type_id)
VALUES (1, 1);

INSERT INTO company_uk_ch(company_id, registered_number)
VALUES (1,'00000000');

-- name of the company is capture from companies house
UPDATE company
SET
name = 'Company XYZ'
WHERE
id = 1;


---
INSERT INTO company_type(id, short_label, long_label)
VALUES (2, 'uk_not_ch', 'A UK company not in comapanies house');

INSERT INTO company(id, company_type_id)
VALUES (2, 2);

INSERT INTO company_uk_non_ch(company_id,website,postcode,city)
VALUES(2, 'https://www.awebsite.com', 'AA99 8Y8', 'a_city');

-- name of the company is capture front end
UPDATE company
SET
name = 'Company ABC'
WHERE
id = 2;


----- non-uk company suspected company ----
INSERT INTO company_type(id, short_label, long_label)
VALUES (3, 'non_uk', 'company with a non-uk address');

INSERT INTO company(id, company_type_id)
VALUES (3, 3);

INSERT INTO company_non_uk(company_id,website,address_1, postcode, city, country)
VALUES(3, 'https://www.halwebsite.com', 'Leopold Robert, 200', '2300',  'a_non_uk_city', 'CH');

-- name of the company is capture front end
UPDATE company
SET
name = 'Company HAL'
WHERE
id = 3;


--- recipient

INSERT INTO company_role(id, role)
VALUES(2, 'suspected recipient');

INSERT INTO company(id, company_type_id)
VALUES (4, 3);

INSERT INTO company_non_uk(company_id,website,address_1, postcode, city, country)
VALUES(4, 'https://www.websitexxx.com', 'a street ', '101',  'Moscow', 'RU');



-- name of the company is capture front end
UPDATE company
SET
name = 'A russian company'
WHERE
id = 4;


--- another recipient
INSERT INTO company(id, company_type_id)
VALUES (5, 3);

INSERT INTO company_non_uk(company_id,website,address_1, postcode, city, country)
VALUES(5, 'https://www.websiteyyy.com', 'a street ', '102',  'Moscow', 'RU');

-- name of the company is capture front end
UPDATE company
SET
name = 'Another russian company'
WHERE
id = 5;



--- another recipient
INSERT INTO company(id, company_type_id)
VALUES (6, 3);

INSERT INTO company_non_uk(company_id,website,address_1, postcode, city, country)
VALUES(6, 'https://www.websitezzz.com', 'a street ', '103',  'Moscow', 'RU');

-- name of the company is capture front end
UPDATE company
SET
name = 'Another russian company'
WHERE
id = 6;




SELECT
E.short_label AS company_type,
C.name AS company_name,
F.registered_number AS company_house_number,
'CH address 1' || ',' || 'CH address 2 ' AS address,
'CH postcode' AS postcode,
'CH city'     AS city,
'CH country'  AS country,
C.id          AS company_id
FROM company C
INNER JOIN company_type E ON E.id = C.company_type_id
INNER JOIN company_uk_ch F ON F.company_id = C.id
UNION
SELECT
E.short_label AS company_type,
C.name AS company_name,
'NO COMPANIES HOUSE NUMBER' AS company_house_number,
F.address_1 || ',' || F.address_2 AS address,
F.postcode AS postcode,
F.city      AS city,
F.country   AS country,
C.id        AS company_id
FROM company C
INNER JOIN company_type E ON E.id = C.company_type_id
INNER JOIN company_uk_non_ch F ON F.company_id = C.id
UNION
SELECT
E.short_label AS company_type,
C.name AS company_name,
'NO COMPANIES HOUSE NUMBER' AS company_house_number,
F.address_1 || ',' || F.address_2 || ',' || F.address_3 || ',' || F.address_4 AS address,
F.postcode AS postcode,
F.city      AS city,
F.country   AS country,
C.id        AS company_id
FROM company C
INNER JOIN company_type E ON E.id = C.company_type_id
INNER JOIN company_non_uk F ON F.company_id = C.id;
