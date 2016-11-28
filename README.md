# ezdb: MySQL and PostgreSQL Database Tool
The ezdb application combines MySQL and PostgreSQL database management into one easy-to-use Linux command-line interface tool. It utilizes the Python ncurses library framework, npyscreen, and provides a form-based user interface for easily building powerful SQL queries; creating databases and tables; adding and deleting data; managing users and permissions; and providing complete query results with pagination. 

<h2> Architecture </h2>
The ezdb database tool is a Linux-based program written in Python. The backend implements two adapter frameworks for communicating with MySQL and postgreSQL database systems (MySQL Connector and pyscopg2). This lightweight command-line interface combines a facade and template architecture design. It also includes an ncurses-based frontend framework called npyscreen for the command-line user interface.

The general program flow is as follows:
<ul>
<li>	A user launches the ezdb tool implementing the npyscreen ncurses-based frontend</li>
<li>	Per user specification, the tool connects to a specified local or remote host</li>
<li>	The program uses one of two adapters to interface with the selected database management system (DBMS): psycopg2 for PostgreSQL or MySQL Connector for MySQL</li>
<li>	All database interactions specific to the DBMS are handled by ezdb’s frontend and backend files</li>
<li>	The user can switch between PostgreSQL and MySQL at any time without have to exit the program</li>
</ul>

<h2>Use Cases</h2>
<ul>
<li>	Easily switch between PostgreSQL and MySQL database systems</li>
<li>	View, open, delete and create databases</li>
<li>	View existing tables in DBMS</li>
<li>	View browse table data and table field structure</li>
<li>	View table field structure</li>
<li>	Create a table using a table builder form</li>
<li>	Delete a table</li>
<li>	Create and execute a SELECT query using a query builder form using up to 3 tables, 3 fields, 9 criteria values and 2 condition operators; view complete query results</li>
<li>	Create and execute an INSERT query using a query builder form using 1 table, 1 or more of its associated fields and supplied field values</li>
<li>	Create and execute an UPDATE query using a query builder form using 1 table; 1 or more fields to update and supplied field values; up to 3 criteria fields and up to 9 criteria values</li>
<li>	Create and execute a DELETE query using 1 table, up to 3 criteria fields and up to 9 criteria values
<li>	Create and execute a custom (and potentially complex) query, and view complete query results</li>
<li>	Import table data from a csv file</li>
<li>	Export table data to a csv file</li>
<li>	Create a new user with all permissions</li>
<li>	Create a new user with permission to create and delete databases and tables</li>
<li>	Create a new user with permission to create and delete other users</li>
<li>	Delete selected user</li>  
</ul>
