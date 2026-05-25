from datetime import datetime
import sys

def check_cutoff_global():
    cutoff_datetime = datetime(2025, 5, 31, 18, 0, 0)
    current_datetime = datetime.now()
    if current_datetime >= cutoff_datetime:
        print("This application is no longer Available, Complete payment first")
        sys.exit(0)

def check_cutoff_route():
    from flask import flash, redirect
    cutoff_datetime = datetime(2025, 5, 31, 18, 0, 0)
    current_datetime = datetime.now()
    if current_datetime >= cutoff_datetime:
        flash("This application is no longer Available, Complete payment first", "danger")
        return redirect('/server')
