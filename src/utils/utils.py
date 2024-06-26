from datetime import datetime
from google.auth.exceptions import RefreshError
from flask import redirect, request, session, url_for
from src.googleauth import refresh_token
from src.database import add_user_db, get_user_credentials_db


def get_user_credentials(function):
    def wrapper(*args, **kwargs):
        user_id = kwargs["user_id"]
        try: 
            credentials = get_user_credentials_db(user_id)
            if not credentials.valid:
                try:
                    credentials = refresh_token(credentials)
                    add_user_db(user_id, credentials)
                except RefreshError:
                    print(f"Error occured: {error}")
                    return redirect(url_for("login"))
                
        except Exception as error:
            print(f"Error occured: {error}")
            return redirect(url_for("login"))
        return function(credentials=credentials, *args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper


def user_id_is_required(function):
    def wrapper(*args, **kwargs):
        user_id =  request.form.get('user_id')
        if user_id == None or user_id == "":
            if "user_id" in session:
                user_id = session["user_id"]
            else:
                return redirect(url_for("login"))
        return function(user_id=user_id,*args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper

def validate_dates(function):
    def wrapper(*args, **kwargs):
        try:
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")
        except:
            raise Exception("Enter both dates")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                raise ValueError("Start date should be before end date.")
            dates = (start_date, end_date)
        except ValueError as ve:
            return f"ValueError: {str(ve)}"
        except TypeError as te:
            return f"TypeError: {str(te)}"
        except Exception as e:
            return f"Exception occurred: {str(e)}"

        return function(dates=dates, *args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper

