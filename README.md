# Grocery Store Management System

> *Note: This repository contains an academic project. The source code, comments, and full PDF documentation are written in Polish to strictly meet the university course requirements.*

System for grocery store that integrates a relational database with a custom-built desktop application. The application allows users to manage store data such as products, employees, and orders, while also providing tools for generating reports.

## Project Preview

### Database Architecture

The diagram below presents the initial conceptual relational model. During the physical database implementation in Oracle SQL, the schema was further normalized. To adhere to the First Normal Form (1NF), the multi-valued alergeny attribute was extracted from the `PRODUKTY` table into a dedicated associative table `PRODUKTY_ALERGENY`. This allows for a clean One-to-Many relationship and ensures better data integrity.

![Relational Database Model](images/erd_diagram.png)

### Database Contents

The database is fully populated with sample data to simulate a real-world store environment. Below is a raw view of the `PRODUKTY` table directly from the Oracle database.

![PRODUKTY table content](images/products.png)

### App Interface

Here is how the application interface looks in practice. The uncomplicated GUI provides an intuitive way to interact with the underlying Oracle database without writing SQL. 

![Application (suppliers tab)](images/app_suppliers.png)

The application also provides report generation. Below you can see a view of the raports tab.

![Application (raports tab)](images/app_raports.png)

## Main Features

This project shows how to connect an Oracle database with a Python application. The most important features are:

* **Database Design:** A well-structured relational database with 13 tables to store information about products, employees, and customers.
* **Data Management (CRUD):** You can easily add, view, edit, and delete records using the application interface, without writing any SQL code.
* **PDF Reports & Charts:** The application can generate PDF documents (like customer cards or supplier lists) and draw warehouse statistics charts using the `matplotlib` library.
* **Safe Data Saving:** The Python code uses database transactions (`commit` and `rollback`) to make sure all data is saved safely and without errors.

## Technologies

* **Database:** Oracle SQL
* **Programming Language:** Python 3
* **Desktop GUI:** Tkinter
* **Database Connection:** `oracledb`
* **PDF Reports:** `fpdf`
* **Data Visualization:** `matplotlib`
