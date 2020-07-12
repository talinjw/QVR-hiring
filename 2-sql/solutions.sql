-- Too Many Tickers: http://sqlfiddle.com/#!18/4ab55/6/0

CREATE TABLE too_many_tickers(
	id int NOT NULL IDENTITY(1,1),
	ticker varchar(10),
	series varchar(10),
	short_ticker varchar(4)
	)

INSERT INTO too_many_tickers(ticker, series, short_ticker)
VALUES ('eq.USO.US', 'eq.USO.US', 'USO'),
	   ('eq.USO1.US', 'eq.USO.US', 'USO1'),
	   ('eq.VXX.US', 'eq.VXX.US', 'VXX'),
	   ('eq.VXXB.US', 'eq.VXX.US', 'VXXB'),
       ('eq.USO3.US', 'eq.USO.US', 'USO3')

DECLARE @specified_ticker varchar(MAX) = 'eq.USO.US'

SELECT
  t1.short_ticker AS short_ticker_sibling,
  t1.series AS shared_series
FROM 
  too_many_tickers t1
 INNER JOIN too_many_tickers t2 ON t1.series = t2.series
 WHERE 
	t2.ticker = @specified_ticker

-- Counting Unread Email: http://sqlfiddle.com/#!18/5d549/10

CREATE TABLE threads(
	thread_id int NOT NULL IDENTITY(1,1),
	subject varchar(100)
	)

CREATE TABLE messages(
	message_id int NOT NULL IDENTITY(1,1),
	thread_id int,
    read_status bit,
    contents varchar(20)
	)

INSERT INTO threads(subject)
VALUES ('Thread 1'),
	   ('Thread 2'),
	   ('Thread 3'),
	   ('Thread 4')
       
INSERT INTO messages(thread_id, read_status, contents)
VALUES (1, 1, 'email 1'),
	   (1, 1, 'email 2'),
       (1, 0, 'email 3'),
       (1, 0, 'email 4'),
       (2, 1, 'email 1'),
       (2, 1, 'email 2'),
       (3, 1, 'email 1'),
       (4, 1, 'email 1'),
       (4, 0, 'email 2')

SELECT 
	t2.thread_id,
	t2.subject,
	COUNT(t1.read_status) As unread_message_count
FROM 
  messages t1
LEFT JOIN threads t2 ON t1.thread_id = t2.thread_id
WHERE t1.read_status = 0
GROUP BY t2.thread_id, t2.subject, t1.read_status

-- Updating Read Status by Thread ID: http://sqlfiddle.com/#!18/5d549/12

DECLARE @specified_thread_id int = 4

UPDATE messages
SET read_status = 1
WHERE thread_id = @specified_thread_id

-- Delete all messages for a given Thread ID: http://sqlfiddle.com/#!18/5d549/13

DECLARE @specified_thread_id int = 4

DELETE FROM messages
WHERE thread_id = @specified_thread_id