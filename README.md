# Library Management System (LBMS)

A custom Library Management System built on ERPNext/Frappe Framework with integrated fine management and accounting features.

## Features

### Library Settings

* Configurable Loan Period
* Configurable Fine Per Day
* Fine Receivable Account Configuration
* Fine Income Account Configuration

### Books Management

* Book Registry
* Book Title
* ISBN
* Author
* Category
* Rack Location
* Total Copies
* Available Copies
* Availability Status
* Automatic Stock Tracking

### Member Management

* Member Registration
* Member Type (Student / Staff / Public)
* Membership Start Date
* Membership End Date
* Outstanding Fine Tracking

### Book Issue & Return

* Book Issue Management
* Automatic Due Date Calculation
* Membership Validation
* Book Availability Validation
* Book Return Processing
* Automatic Available Copy Updates

### Overdue Management

* Automatic Overdue Detection
* Daily Scheduler for Overdue Books
* Status Tracking (Issued / Returned / Overdue)

### Fine Management

* Automatic Fine Calculation
* Overdue Day Calculation
* Fine Records
* Waiver Management
* Partial Payment Support
* Outstanding Amount Calculation
* Payment Status Tracking

  * Unpaid
  * Partially Paid
  * Paid

### Accounting Integration

* Automatic Journal Entry Creation
* Fine Receivable Tracking
* Fine Income Tracking
* ERPNext Accounting Integration

## Technology Stack

* Frappe Framework v15
* ERPNext v15
* Python
* MariaDB
* JavaScript

## Installation

```bash
bench get-app <repository-url>
bench --site <site-name> install-app lbms
bench --site <site-name> migrate
```

## Scheduler

The application includes a daily scheduler that automatically marks overdue book issues.

## Module Structure

* Library Settings
* Books
* Library Member
* Book Issue
* Library Fine

## Business Flow

### Book Issue

Book → Issue → Due Date Generated → Status = Issued

### Book Return

Book Return → Fine Calculation → Fine Record Creation

### Fine Collection

Fine → Payment Entry → Journal Entry Creation → Outstanding Balance Updated

## Author

Tushar

## License

MIT
