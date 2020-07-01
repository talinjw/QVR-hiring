# QVR

## Welcome!

We don't particularly like the hazing that accompanies most technical job interviews, and thought it would be less stressful for everyone involved if we instead gave you an opportunity to show off your abilities by working on a set of problems that are fairly representative of what we deal with on a daily basis.

## The Rules

Please send PRs for each problem set attempted within 96 hours of receiving a link to the repository.

We will schedule an hour to discuss your answers after that.

## The Problem Sets

* [Table Stakes](./1-table-stakes): This problem helps us confirm that you will be comfortable in an environment that makes heavy use of Python and Pandas.
* [SQL](./2-sql): These problems are dialect agnostic and show us that you are comfortable using relational databases.
* [Debugging](./3-debugging) (optional): Bad things happen to good programmers all the time. In this section, you will be airdropped into some questionable code that does something *extremely* wrong, and asked to diagnose and fix it.
* [Distributed Systems](./4-distributed-systems) (optional): Here we will look at some of the challenges inherent in consistently managing more than one server.

## Working with this repository

We like ```make```, specifically the GNU version. If you are on BSD (go you!), you will need to install ```gmake``` using your package manager.

You can run all tests associated with any given problem by issuing:

```
make test-[1-4]
```

You will need python>=2.7 and pandas>=0.19.2 installed.
