SELECT  c.Type, p.pid, p.pdate, p.title, p.body, p.poster, COALESCE(A.Num_of_Answers,0) AS Num_of_Answers, COALESCE(B.Total_Votes,0) AS Total_Votes
FROM posts p
LEFT OUTER JOIN
(SELECT  'Answer' AS Type, a.pid
FROM answers a 
UNION
SELECT  'Question' AS Type, q.pid
FROM questions q) as C on C.pid = p.pid
LEFT OUTER JOIN
(SELECT  p1.pid, COALESCE(COUNT(a1.qid),0) AS Num_of_Answers
FROM posts p1, answers a1
WHERE p1.pid = a1.qid
GROUP BY (p1.pid)
) as A on A.pid = p.pid
LEFT OUTER JOIN
(SELECT  p2.pid,COUNT(v2.pid) AS Total_Votes
FROM posts p2, votes v2
WHERE p2.pid = v2.pid
GROUP BY (p2.pid)
) as B on B.pid = p.pid
LEFT OUTER JOIN
(SELECT p3.pid AS test
FROM posts p3, tags t
WHERE p3.pid = t.pid
AND lower(t.tag)  like'%whatup%' as C on C.test = p.pid
WHERE 
(lower(p.title)  IN ('%whatup%','%dog%') or lower(p.body) like '%whatup%' )
GROUP BY p.pid
ORDER BY COUNT(p.pid) DESC;