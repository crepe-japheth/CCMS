Courier and Cargo Management System (CCMS)
1. Project Overview
1.1 Purpose
The Courier and Cargo Management System (CCMS) is a web-based platform designed to manage the transportation of parcels, documents, and cargo between company branches. The system shall enable package registration, shipment tracking, arrival confirmation, branch management, vehicle assignment, reporting, and user access control.
1.2 Objectives
The system aims to:
•	Digitize cargo and parcel management processes.
•	Improve shipment tracking and visibility.
•	Reduce package loss and delivery disputes.
•	Provide accountability for branch staff.
•	Generate operational and financial reports.
•	Improve customer service through shipment tracking.
________________________________________
2. Functional Requirements
2.1 Branch Management
The system shall allow administrators to:
•	Create branches/stations.
•	Update branch information.
•	Activate or deactivate branches.
•	View all registered branches.
Branch Information
•	Branch Name
•	Branch Code
•	Location
•	Contact Number
•	Status (Active/Inactive)
________________________________________
2.2 User Management
The system shall support multiple users with role-based access control.
User Information
•	Full Name
•	Username
•	Email
•	Phone Number
•	Assigned Branch
•	Role
•	Status
Roles
System Administrator / Manager
Privileges:
•	Create, edit, and deactivate users.
•	Create and manage branches.
•	Create and manage vehicles.
•	View all shipments across all branches.
•	View financial reports.
•	View operational reports.
•	Configure system settings.
Branch Officer
Privileges:
•	Register outgoing packages.
•	Receive incoming packages.
•	Scan and confirm package arrivals.
•	View packages created by themselves.
•	View all packages assigned to their branch.
•	View packages received by themselves.
________________________________________
2.3 Vehicle Management
The system shall maintain records of vehicles used for transportation.
Vehicle Information
•	Plate Number
•	Vehicle Type
•	Driver Name
•	Driver Phone Number
•	Status
Functions
•	Register vehicles.
•	Update vehicle details.
•	Assign vehicles to shipments.
•	View transportation history.
________________________________________
2.4 Package Registration
The system shall allow branch officers to register packages.
Sender Information
•	Sender Full Name
•	Sender National ID/Passport Number
•	Sender Phone Number
Receiver Information
•	Receiver Full Name
•	Receiver National ID/Passport Number
•	Receiver Phone Number
Shipment Information
•	Tracking Number
•	Package Type
•	Package Description
•	Quantity
•	Weight
•	Origin Branch
•	Destination Branch
•	Assigned Vehicle
•	Transport Fee
•	Registration Date and Time
•	Registered By
Package Types
•	Documents
•	Parcel
•	Cargo
•	Other
________________________________________
2.5 Tracking Number Generation
The system shall automatically generate a unique tracking number for every package.
Example:
CCMS-20260604-000001
The tracking number shall be unique throughout the system.
________________________________________
2.6 QR Code Generation
After package registration:
•	The system shall generate a QR Code.
•	The QR Code shall contain the shipment tracking number.
•	The QR Code shall be printable.
•	The QR Code shall be attached to the package.
________________________________________
2.7 Shipment Status Management
The system shall maintain shipment statuses.
Statuses
•	Registered
•	Ready for Dispatch
•	In Transit
•	Arrived at Destination
•	Ready for Pickup
•	Delivered
•	Cancelled
The system shall record the date, time, and user responsible for each status change.
________________________________________
2.8 Package Arrival Confirmation
When a package arrives at the destination branch:
•	The receiving officer shall scan the QR Code.
•	The system shall retrieve shipment details.
•	The receiving officer shall confirm arrival.
•	Shipment status shall change to "Arrived at Destination".
The system shall store:
•	Receiving User
•	Receiving Branch
•	Arrival Date and Time
________________________________________
2.9 Package Collection by Receiver
When the receiver comes to collect the package:
The officer shall verify:
•	Receiver ID
•	Receiver Name
•	Receiver Phone Number
After verification:
•	Officer confirms package collection.
•	Shipment status changes to "Delivered".
The system shall record:
•	Collection Date and Time
•	Delivered By
•	Receiver Identification Number
________________________________________
2.10 Shipment Tracking
The system shall provide shipment tracking using:
•	Tracking Number
•	QR Code
Users shall be able to view:
•	Shipment Status
•	Origin Branch
•	Destination Branch
•	Registration Date
•	Arrival Date
•	Delivery Date
________________________________________
2.11 Reports
Operational Reports
•	Packages Sent Per Branch
•	Packages Received Per Branch
•	Packages Delivered
•	Packages In Transit
•	Delayed Packages
•	Vehicle Utilization Report
Financial Reports
•	Revenue by Branch
•	Revenue by Date Range
•	Revenue by Vehicle
•	Revenue by User
User Activity Reports
•	Packages Registered by User
•	Packages Received by User
•	Login Activity
Reports shall support:
•	Export to PDF
•	Export to Excel
________________________________________
3. Non-Functional Requirements
Performance
•	Search results should be returned quickly.
Security
•	Role-based access control.
•	Secure password storage.
•	Audit logs for all critical activities.
Availability
•	System availability of 99%.
Scalability
•	Support future expansion to additional branches.
________________________________________
4. Audit Trail
The system shall maintain logs for:
•	User login/logout.
•	Package registration.
•	Package arrival confirmation.
•	Package delivery confirmation.
•	User creation and modifications.
•	Vehicle assignments.
________________________________________
5. Future Enhancements
•	SMS Notifications to sender and receiver.
•	WhatsApp Notifications.
•	Customer Self-Service Tracking Portal.
•	Mobile Application.
•	GPS Vehicle Tracking Integration.
•	Electronic Signature Capture.
•	Barcode Label Printing.
________________________________________
6. Recommended Technology Stack
Backend:
•	Python Django
Frontend:
•	Django Templates, Tailwind and Js
Database:
•	Sqlite3 for now
Reporting:
•	PDF and Excel Export
•	Dashboard visual (html and Js)

