/* This script brings all the data of a report together. */

DELETE FROM report_reporter;
DELETE FROM report_company;

-- report and reporters - we bring the relationship together.
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(1,1,1);
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(2,3,2);
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(3,3,3);
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(4,4,4);
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(5,4,1);
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(6,6,1);
INSERT INTO report_reporter(report_id, reporter_id, relationship_id)
VALUES(7,2,0);



-- report and companies. We add the role of the company against the breach

-- company report and role into breach 2,3,5, 6 recipients 2 

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(1,1,1);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(3,4,1);


INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(4,2,1);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(5,5,1);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(6,6,1);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(7,1,1);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(8,5,1);


INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(1,6,2);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(3,3,2);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(4,6,2);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(5,2,2);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(7,5,2);

INSERT INTO report_company(report_id, company_id, company_role_id)
VALUES(8,6,2);

select *
FROM report_companies_list;