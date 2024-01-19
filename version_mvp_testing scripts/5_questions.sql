/* This script  tests the questions, content, and json_schema.*/

DELETE FROM json_schema;
DELETE FROM content;

DELETE FROM question;

DO $$
DECLARE
schema_json TEXT := '{ "properties": { "text": { "type": ["string"]}}}';
BEGIN
INSERT INTO json_schema(id, label, schema)
VALUES(1, 'textbox', schema_json);
END $$;

DO $$
DECLARE
schema_json TEXT := '{ "properties": {"question": { "type": ["string"]},"description":{"type":["string"]}}}';
BEGIN
INSERT INTO json_schema(id, label, schema)
VALUES (2, 'question with one line', schema_json);
END $$;

DO $$
DECLARE
schema_json TEXT := '{ "properties": {"question": { "type": ["string"]},"options":{"type": "array", "items": {"type": "string"}}}}';
BEGIN
INSERT INTO json_schema(id, label, schema)
VALUES (3, 'question with options', schema_json);
END $$;

----- We create a question and then an answer.
INSERT INTO question (id, json_question, schema_id)
VALUES(1, '{"question": "What is your email address?", "description":"We will need it to verify your email."}', 2);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(1,1,'{"text":"name@email.com"}', 1);
----
INSERT INTO question (id, json_question, schema_id)
VALUES(2, '{"question": "We have sent you an email", "description":"Enter the 6 digit security code."}', 2);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(2,1,'{"text":"123456"}', 1);
----
INSERT INTO question (id, json_question, schema_id)
VALUES(3, '{"text": "What is your fullname?"}', 1);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(3,1,'{"text":"Harry Potter"}', 1);

----

INSERT INTO question (id, json_question, schema_id)
VALUES(4, '{"text": "Where is the address of the company or person who made the suspected breach?","options":"[in the uk, outside the uk]}', 3);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(4,1,'{"text":"In the UK"}', 1);
---

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(1,3,'{"text":"name.surname@email.com"}', 1);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(2,3,'{"text":"394828"}', 1);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(3,3,'{"text":"Hermione Granger"}', 1);

INSERT INTO content (question_id, report_id, json_answer, schema_id)
VALUES(4,3,'{"text":"outside the uk"}', 1);  -- check that number 3 will have a company abroad



SELECT *
FROM report_questions_list;
