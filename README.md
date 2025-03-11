## Team 11 - Analytics Pipeline

To run the program follow the steps mentioned below:

1. Open a command prompt
2. Run the command ```pip install -r requirements.txt```
3. Run PostgreSQL locally on the port 5432 using the credentials ```user: postgres  -  password: admin```
4. Created a database named ```biteback_analytics```
5. Add the firebase credentials file ```biteback-89c7a-firebase-adminsdk-fbsvc-5ce126e950``` to the projects root
6. Run the main application using the command  ```python -m uvicorn main:app --reload```