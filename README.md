Group 21

Valmonte Janelle Darcy Juban (Group Leader), A0300338R, e1354704@u.nus.edu, 85710900
Li Zhirui, A0322266J, e1525173@u.nus.edu, 97736278

-- HOW TO RUN TUTORLINK WITH DEMO DATA --
1. Create and activate a virtual environment, then install the requirements:
     python -m venv .venv
     Mac: source .venv/bin/activate
     Windows: .venv\Scripts\activate
     pip install -r requirements.txt
3. Go into the project folder and set up the database:
     cd tutorlink
     python manage.py migrate
4. Start the server:
     python manage.py runserver
5. Open http://127.0.0.1:8000/ and click "Load demo data" on the landing page.
6. Log in with any demo account below (password for all: demo1234),
   or sign up for a new account.

     Staff:   staff@demo.com
     Tutor:   tutor1@demo.com, tutor2@demo.com
     Parent:  parent1@demo.com

The trained price model (ml/price_model.joblib) is included, so no training is needed.
To retrain it: python manage.py train_price_model

-- DEMO VIDEO --
https://youtu.be/MOBKJrWXyJ8
