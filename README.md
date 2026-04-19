# Grocery Store Management System

> *Note: This repository contains an academic project. The source code, comments, and full PDF documentation are written in Polish to strictly meet the university course requirements.*

A desktop application written in Python with a graphical user interface (GUI), integrated with an Oracle relational database. The project enables comprehensive management of the store's inventory, employees, customers, and orders.

## Technologies

* **Database:** Oracle SQL, PL/SQL (stored procedures, triggers)
* **Application (Backend & GUI):** Python 3, Tkinter, `oracledb`
* **Reporting:** `fpdf` (PDF generation), `matplotlib` (charts)

## Main Features

* **Data Management (CRUD):** Viewing, adding, modifying, and deleting products, customers, suppliers, and warehouses directly from the application.
* **Advanced Oracle Mechanisms:** Utilizing stored procedures (e.g., employee bonus allocation system) and triggers (automatic price validation and promotion tagging).
* **Automated Reports:** Generating price lists, customer cards, and warehouse statistics as PDF documents with charts.

## Project Structure

* `main_gui.py` - Main application script (user interface).
* `db_operations.py` - Module for communicating with the Oracle database.
* `report_manager.py` - Script for generating PDF reports and charts.
* `sklep_DDL_DML_Full.sql` - SQL script to create tables, relationships, and insert sample data.
* `Dokumentacja.pdf` - Full documentation including ERD/UML diagrams and business logic description.

## How to run?

1. Execute the `sklep_DDL_DML_Full.sql` script in your Oracle database.
2. Install the required libraries:
```bash
pip install oracledb fpdf matplotlib
