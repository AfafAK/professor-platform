\# Professor Platform



A web-based educational management platform developed with Django. The project aims to provide professors with a centralized environment to manage educational activities, courses, students, learning resources, and academic content.



\## Project Overview



Professor Platform is a Django-based web application designed to support academic and educational management through dedicated interfaces for professors and students.



\## Main Modules



\- \*\*Dashboard:\*\* Academic activity overview and management interface.

\- \*\*Student Management:\*\* Student information and student-related pages.

\- \*\*Course Management:\*\* Create and manage courses and educational modules.

\- \*\*E-Learning:\*\* Online training, learning modules, quizzes, and results.

\- \*\*Research:\*\* Research-related content and publications.

\- \*\*Resource Management:\*\* Educational resources and materials.

\- \*\*Appointment Management:\*\* Appointment-related interfaces.

\- \*\*Notifications:\*\* Notification management.

\- \*\*Contact Management:\*\* Contact messages and communication pages.



\*Note: These modules describe the project interfaces and implemented components; individual features may require further functional testing.\*



\## Technologies Used



\- Python

\- Django 6.0.5

\- SQLite

\- HTML5

\- CSS3

\- JavaScript

\- Matplotlib

\- python-dotenv



\## Project Structure



```text

professor-platform/

│

├── analytics/

├── core/

├── courses/

├── elearning/

├── platform\_prof/

├── research/

├── scheduler/

├── static/

│   └── css/

├── templates/

├── manage.py

├── requirements.txt

└── .gitignore

```



\## Installation



\### 1. Clone the repository



```bash

git clone https://github.com/AfafAK/professor-platform.git

cd professor-platform

```



\### 2. Create a virtual environment



```bash

python -m venv .venv

```



Activate it on Windows:



```bash

.venv\\Scripts\\activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file in the project root directory:



```env

SECRET\_KEY=replace-with-your-secret-key

DEBUG=True

ALLOWED\_HOSTS=localhost,127.0.0.1

SECURE\_SSL\_REDIRECT=False

```



Never publish your actual secret key or other credentials.



\### 5. Apply database migrations



```bash

python manage.py migrate

```



\### 6. Run the development server



```bash

python manage.py runserver

```



Open your browser at:



http://127.0.0.1:8000/



\## Security



\- Environment-based configuration using python-dotenv.

\- Secret key stored outside the source code.

\- Debug mode configurable through environment variables.

\- Sensitive files excluded using `.gitignore`.

\- Django security middleware and password validators.



\## Project Status



The project is under development and subject to continued testing, improvements, and documentation.



\## Author



\*\*Afaf Ait Khouya\*\*



GitHub: https://github.com/AfafAK

