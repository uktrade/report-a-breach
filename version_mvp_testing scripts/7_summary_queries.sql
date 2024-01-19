/* Summary */


-- Your details for report no 1 shows report unique ref for verification ---
SELECT A.unique_ref,
C.full_name
FROM report A 
INNER JOIN report_reporter B ON B.report_id = A.id
INNER JOIN reporter  C ON C.id = B.reporter_id
WHERE A.id = 1;

-- Company or person suspected  of breaching sanctions -- The address is captured from company house, but not shown here ....
SELECT 
C.unique_ref, 
role, 
company_name, 
company_house_number,
address,
postcode,
city
FROM companies_list A 
INNER JOIN report_company B ON A.company_id = B.company_id
INNER JOIN reports_list C ON C.report_id = B.report_id
INNER JOIN company_role D ON D.id = B.company_role_id
WHERE C.report_id = 1
AND D.id = 1;


-- company or person suspected to receive the services
SELECT 
A.unique_ref, 
A.role, 
B.company_name, 
B.address,
B.postcode,
B.city
FROM report_companies_list A 
INNER JOIN companies_list B ON A.company_id = B.company_id
WHERE A.report_id = 1 
AND A.role_id  = 2;

-- Sanctions breach details
SELECT *
FROM report_details;

