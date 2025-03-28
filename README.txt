Instalation
-----------

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Grotski/airport-api.git

2. **Navigate to the project directory**:
    ```bash
    cd airport-api

3. **Set up the virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # `venv/Scripts/activate` for windows

4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

5. **Set Up Environment Variables**:
- Create a `.env` file in the project root directory.

6. **Applay migrations**:
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate

7. **Run server**:
    ```bash
    pyhton3 manage.py runserver


Docker
------

To deploy the application using Docker:

1. **Build and start the containers**:
    ```bash
    docker-compose up --build

2. **Access the Application**:
- The application will be running at `http://localhost:8000/`.


Features
--------

- **Flight Tracking**: Monitor real-time flight statuses and schedules.
- **Airport Information**: Access detailed information about airports worldwide.
- **User Management**: Register and manage user profiles for personalized experiences.
