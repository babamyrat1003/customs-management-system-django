# Customs Registry & Case Management System

A robust, enterprise-level Django application designed to digitize and automate customs violations, case tracking, and administrative reporting. This project replaces manual data entry with an optimized digital workflow.

## 🌟 Key Technical Highlights
* **Customized Admin Interface:** Leveraged `django-nested-admin` and `searchable-dropdowns` to manage complex hierarchical data (Offices -> Points -> Officers).
* **Dynamic Reporting:** Automated Excel report generation using `openpyxl` with custom styling and formatting.
* **Multi-language Support:** Full implementation of Django's `i18n` (Internationalization) for cross-border operations.
* **Complex Data Modeling:** Managed intricate relationships between Customs Offices, Violations, Products, and Legal Entities.
* **Advanced Form Handling:** Implemented dynamic formsets for witness tracking and incident reporting.

## 🛠 Tech Stack
* **Framework:** Django (Python)
* **Tools:** Openpyxl (Excel automation), Nested Admin, Searchable Dropdowns
* **Database:** PostgreSQL / SQLite
* **Frontend:** Django Templates with JavaScript for dynamic field filtering

## 📂 Project Structure (Simplified)
* `customs_registry/`: Core logic for managing customs offices, points, and staff.
* `reports/`: Module for generating legal documents and Excel summaries.
* `forms.py`: Custom validation for complex violation reports.

## 🚀 How it Works
1.  **Violation Logging:** Officers can log violations, attaching products, vehicles, and witnesses in a single unified form.
2.  **Automated Export:** Generate official reports in Excel format with one click, formatted for government standards.
3.  **Data Filtering:** Advanced search and filtering capabilities to track specific types of violations or regional performance.

---
*Note: This repository is a showcase of backend architecture and business logic implementation.*
