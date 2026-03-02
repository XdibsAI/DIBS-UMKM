#!/bin/bash
echo "==================================="
echo "🔍 CEK DATABASE DIBS"
echo "==================================="

sqlite3 data/dibs.db << 'END_SQL'
.tables
SELECT '---' as '';
SELECT '📊 CHAT SESSIONS:' as '';
SELECT * FROM chat_sessions;
SELECT '---' as '';
SELECT '📝 CHAT MESSAGES:' as '';
SELECT * FROM chat_messages;
SELECT '---' as '';
SELECT '👤 SESSIONS PER USER:' as '';
SELECT user_id, COUNT(*) as total_sessions FROM chat_sessions GROUP BY user_id;
END_SQL
