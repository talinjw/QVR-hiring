# SQL

## So many tickers

In the following table, ```ticker``` is a variant of ```series```.

| ticker      | series     | short_ticker
|---          |---         |---
| eq.USO.US   | eq.USO.US  | USO
| eq.USO1.US  | eq.USO.US  | USO1
| eq.VXX.US   | eq.VXX.US  | VXX
| eq.VXXB.US  | eq.VXX.US  | VXXB

Given a ```ticker```, return a list of ```short_tickers``` with identical ```series```.

Bonus points if you can do it without a nested query.


## Update read status on an email thread

In the following tables, ```thread_id``` is a foreign key in ```messages```


```threads```:

| thread_id   | subject    |
|---          |---         |
| 1           | Thread 1   |
| 2           | Thread 2   |
| 3           | Thread 3   |
| 4           | Thread 4   |

```messages```:

| message_id  | thread_id  | read_status | contents |
|---          |---         |---          |---       |
| 1           | 1          | true        | email 1  |
| 2           | 1          | true        | email 2  |
| 3           | 1          | false       | email 3  |
| 4           | 1          | false       | email 4  |
| 5           | 2          | true        | email 1  |
| 6           | 2          | true        | email 2  |
| 7           | 3          | true        | email 1  |
| 8           | 4          | true        | email 1  |
| 9           | 4          | false       | email 2  |

* Construct a query returning a list of threads ordered by number of unread messages and excluding those with no unread messages, e.g.

| thread_id   | subject    | unread_count
|---          |---         |---
| 1           | Thread 1   | 2
| 4           | Thread 4   | 1

* Construct a query to update the status of all unread messages for a given ```thread_id``` to ```read=true```.

* Construct a query to delete all messages in a thread given a ```thread_id```.
