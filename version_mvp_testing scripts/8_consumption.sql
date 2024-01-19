/* data consumption */



-- count the number of report per regimes
SELECT B.full_name, 
COUNT(*)
FROM report A 
INNER JOIN regimes_list B ON B.id = A.regime_id
GROUP BY B.full_name;

-- count the number of reporters per relationship
SELECT relationship, COUNT(*)
FROM reports_and_reporters_list
GROUP BY relationship;

-- count the number of reporters not validating 
SELECT status, 
count(*)
FROM reporters_list
GROUP BY status;
