# Form-Easy: Temporary Employment Record System
#### Video Demo: https://youtu.be/oFC_GILm928
#### Description: Lightweight record management system

**Form-Easy** was created out of necessity. I had to manage groups of temporary workers, and for every job event, I had to manually fill out three separate documents per person: a contract, a wage claim, and a payment acknowledgment form. Not only was this repetitive and error-prone, but I also had to calculate totals by hand, track participation across different dates, and store it all in an organized way which, frankly, it wasn’t.

I made several attempts using SQL, but realized that the amount of data used does not justify a full fledged database and that ordinary CSV files will suffice and will be easier to interact with while maintaining the flexibility I needed. So I built Form-Easy to streamline the entire process.

Now I can create events, assign employees, and automatically generate all the required paperwork in one go with cleanly formatted PDF documents that include all the necessary information. I can also view monthly data grouped by date, employee, or event, complete with totals and export options for archiving digital records. Behind the scenes, the app reads from CSV files and uses a Flask-based back end to keep the app lightweight, modular, and easy to maintain.

The layout is fully responsive, too. I have made sure it works smoothly on smaller screens, and kept in mind if I wanted for future upgrades, like facial recognition or biometric confirmation to automate the process even further.

This was not just an academic exercise, it’s a tool I genuinely needed, refined through trial, error and iteration, and now it’s something that others in similar situations could benefit from too.

---

## 🛠️ Features

Here are the key features I focused on for creating Form-Easy. 

### 👥 Employee Management
- Add, edit, and remove employees via an intuitive interface
- Form inputs validated on both client and server sides
- All data backed by structured CSV files for easy inspection

### 📆 Event Creation
- Assign employees to specific events with defined dates and task descriptions
- Common event tasks available via dropdown lists to avoid inconsistent labeling
- Clean and consistent layout using Bootstrap and custom styling

### 📄 Form Generation
- Select a month ➝ event ➝ employee to instantly generate a multi-page PDF:
  - **Employment Agreement**
  - **Wage Claim**
  - **Payment Acknowledgment**
- All PDFs include branding, dynamic data, and proper layout formatting via HTML templates and WeasyPrint

### 📊 Report Views
- Three interactive report modes:
  - By Date
  - By Employee
  - By Event
- Each view auto-loads data from the correct CSV and displays it with:
  - Sorted, structured tables
  - Calculated totals for payment sums
  - Export-to-PDF functionality for print-friendly summaries formatted to A4

---

## 🗃️ Project Structure Overview
```
├── README.md
├── app.py
├── config.py
├── data
│   ├── employees
│   │   └── employee_data.csv
│   └── events
│       ├── 202505.csv
│       └── 202506.csv
├── routes
├── static
│   ├── favicon.ico
│   └── styles.css
├── templates
│   ├── base.html
│   ├── employees
│   │   ├── add_employee.html
│   │   ├── edit_employee.html
│   │   └── remove_employee.html
│   ├── employees.html
│   ├── events.html
│   ├── forms
│   │   ├── employment_agreement.html
│   │   ├── payment_acknowledgment.html
│   │   └── wage_claim.html
│   ├── forms.html
│   ├── home.html
│   ├── reports
│   │   ├── by_date.html
│   │   ├── by_employee.html
│   │   └── by_event.html
│   └── reports.html
└── utils.py
```

---

## 🔍 Design Decisions

- **Flask as the web framework**
I chose Flask because it was covered in CS50, and its minimal structure gave me full control over the design and flow of the app. Its simplicity made it easy to get up and running (and to test throughout the build process), while also encouraging clear routing, modularity, and readable code, ideal for a single-developer project like this.

- **Jinja templates for dynamic rendering**
Jinja made it easy to inject data into my HTML pages and reuse layout components. I kept logic minimal in the templates themselves. The decisions, validations, and calculations are handled in Python so the front end stayed clean and maintainable.

- **CSV files instead of SQL**
I experimented with using a database but ultimately realized that, for this context, where the data is limited, structured, and manually managed CSV files are more than enough to store the data. They are easy to read, back up, and debug. Choosing CSV file formats also kept the app portable and reduced complexity.

- **Modular routing and utility functions**
Tasks like employer info retrieval, PDF generation, and error handling were separated into utility functions. This helped keep routes focused and made the project easier to maintain and extend later.

- **Responsive, mobile-first layout using Bootstrap**
All pages were styled using Bootstrap. The layout adjusts seamlessly across screen sizes, improving usability and laying the groundwork for future enhancements—such as mobile-based biometric check-ins or facial recognition.

- **Client-side sorting and filtering with JavaScript**
Report views are loaded via `fetch()` and sorted using lightweight, client-side logic. This keeps the experience fast and responsive without needing additional server round trips once the data is loaded.

---

## 🧩 Development Challenges & Solutions

Here are some of the more challenging issues I had to overcome.

- **String Matching and Data Consistency**
Matching CSV data to user selections (like event names and dates) required careful string formatting and cleanup. Even small discrepancies—like trailing whitespace, inconsistent capitalization, or hidden characters, could prevent records from linking correctly. I implemented trimming, case normalization, and pattern enforcement throughout the data workflow to keep matching reliable.
(https://www.geeksforgeeks.org/python/normalizing-textual-data-with-python/)

- **PDF Generation Across Multiple Templates**
Combining multiple HTML templates into a single, polished PDF wasn’t as straightforward as expected. I initially tried rendering all forms together, but layout conflicts and overlapping styles made the output unpredictable. The solution was to generate each form separately using WeasyPrint and then merge them on the fly. This on-demand, temp-directory-based approach gave me more control and made the output far more consistent.
(https://weasyprint.org/)
(https://dantebytes.com/generating-pdfs-from-html-with-weasyprint-and-jinja2-python/)
(https://dev.to/bowmanjd/python-pdf-generation-from-html-with-weasyprint-538h)

- **Cross-Device Styling and Button Layout**
Getting the layout to behave across screen sizes—especially for action buttons and form spacing—required more iteration than anticipated. Bootstrap’s utilities were a great help, but fine-tuning spacing, alignment, and stacking behavior took extra care to ensure a consistent look on both desktops and smaller mobile screens.
(https://getbootstrap.com/docs/5.0/layout/utilities/)

- **Developing Outside CS50.dev in Visual Studio Code**  
While CS50.dev was a great starting point, I eventually transitioned the project to Visual Studio Code on my desktop for a more complete development experience. Working locally gave me access to extensions, IntelliSense, and better file navigation, all of which helped me debug faster and organize my code more effectively.

To make this work, I had to install Ubuntu and enable WSL (Windows Subsystem for Linux) to run Bash commands. This setup required adjusting BIOS settings and system configurations, an unexpected challenge in itself. Throughout that process, Microsoft Copilot was a huge help: explaining the steps, troubleshooting the errors, and guiding me through the transition with just-in-time support.

Getting the project running locally wasn’t just about convenience, it helped me better understand the "behind the scenes" and made me more confident in managing real-world development environments.


---

## 📦 Final Thoughts

Form-Easy is more than just a class project, it is the culmination of a long journey, and a tool built from real-world frustration, practical need, and personal growth. It took me, a happily 43-year-old husband and father of two, nearly a year to complete this 10-week course. And it took me two months of late nights, early mornings, and determined weekends to build this app.

Starting with a humble `printf("hello, world")`, I slowly worked my way through concepts I never imagined I’d be able to apply: Python, Flask, HTML, CSS, JavaScript—all working together in a full-stack web application. Every milestone was a breakthrough, every bug a lesson. And yes, sitting through three-hour lectures after work, only to find out there were more videos queued up, tested my patience and grit.

Developing Form-Easy wasn't easy. But it was possible, thanks to the remarkable effort poured into this course by Professor David Malan, the CS50 team, and everyone involved with OpenCourseWare, edX, and Harvard’s commitment to accessible education. I am genuinely grateful to all of them for making this available to learners like me.

This project has changed how I view development, education, and problem-solving. I now have a far deeper understanding and appreciation for what it takes to create meaningful software—both in terms of code and the people behind it.

---



