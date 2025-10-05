SELECT n.id, n.user_id, n.subject, u.email
FROM newsletters n
JOIN users u ON n.user_id = u.id
LIMIT 5;
