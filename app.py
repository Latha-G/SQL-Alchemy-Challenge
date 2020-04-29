'''-----------------------------------------------------------------
Dependencies & Python SQL toolkit and Object Relational Mapper
------------------------------------------------------------------'''

import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy import create_engine, func,inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from datetime import datetime, timedelta


'''-----------------------------------------------------------------
Database set_up
------------------------------------------------------------------'''

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model

Base = automap_base()

# Reflect the tables

Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found

Base.classes.keys()

# Save references to measurement table

Measurement = Base.classes.measurement

# Save references to station table

Station = Base.classes.station

# Create a session (link) from Python to the DB

session = Session(engine)


'''-----------------------------------------------------------------
Flask Setup
------------------------------------------------------------------'''

# Import Flask
from flask import Flask, jsonify

# Create an app, being sure to pass __name__
app = Flask(__name__)

'''-----------------------------------------------------------------
Flask route
------------------------------------------------------------------'''

# Define what to do when a user hits the index route

@app.route("/")
def home():
    
    print("Server received request for 'Home' page...")
    
    return(f"<h2>Hello! Welcome to Hawaii Climate Analysis page!</h2><br/>"
           f"/api/v1.0/precipitation<br/><br/>"
           f"/api/v1.0/stations<br/><br/>"
           f"/api/v1.0/tobs<br/><br/>"
           f"/api/v1.0/start<br/><br/>"
           f"/api/v1.0/start/end")

   
'''-----------------------------------------------------------------
year_ago_date
------------------------------------------------------------------'''


def year_ago_date():
    
    date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date of last data point from the query

    latest_date_str = date_query[0]

    # Using strptime() to create a datetime object from the time string

    latest_date = datetime.strptime(latest_date_str,"%Y-%m-%d").date()
    
    # Calculate the date 1 year ago from the last data point in the database

    Year_Ago_Date = latest_date - timedelta(days=365)
    
    return Year_Ago_Date


'''-----------------------------------------------------------------
active_station_query
------------------------------------------------------------------'''


# Design a query to find the most active station

def active_station_id():
    
    active_station_query = session.query(Measurement.station).\
                           group_by(Measurement.station).\
                           order_by(func.count().desc()).\
                           first()

    return active_station_query[0]



'''-----------------------------------------------------------------
Flask precipitation API
------------------------------------------------------------------'''

@app.route("/api/v1.0/precipitation")
def precipitation():

    Year_Ago_Date = year_ago_date()

    # Perform a query to retrieve the date and precipitation scores for the past one year

    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= Year_Ago_Date).all()
    
    # Convert the query results into a dictionary
    
    prcp_dict = {Date : precipitation for Date,precipitation in prcp_query}
    
    # Return the results in Json
    
    return jsonify(prcp_dict)

 
'''-----------------------------------------------------------------
Flask stations API
------------------------------------------------------------------'''

@app.route("/api/v1.0/stations")
def stations():
    
    # Perform a query to retrieve the station names

    station_query = session.query(Measurement.station, Station.name).\
                                  filter(Measurement.station == Station.station).\
                                  group_by(Measurement.station).all()
    
    # Convert the query results into a dictionary
    
    stations_list = {ID : Name for ID, Name in station_query}
    
    # Return the results in Json
    
    return jsonify(stations_list)


'''-----------------------------------------------------------------
Flask tobs API
------------------------------------------------------------------'''

@app.route("/api/v1.0/tobs")
def tobs():
    
    Year_Ago_Date = year_ago_date()
    
    active_station_id = active_station_id()
    
    # Query the last 12 months of TOBS for the most active station
    
    tobs_query = session.query(Measurement.date, Measurement.tobs).\
                 filter(Measurement.station == active_station_id).\
                 filter(Measurement.date >= Year_Ago_Date).\
                 all()   

    # Convert the query results into a dictionary
    
    tobs = {date : tobs for date, tobs in tobs_query}
    
    # Return the results in Json
    
    return jsonify(tobs)
        

'''-----------------------------------------------------------------
Flask stats API given start date
------------------------------------------------------------------'''

@app.route("/api/v1.0/<start>")
def start(start):
    
    stats_query = session.query(Measurement.station,
                                func.min(Measurement.tobs),
                                func.max(Measurement.tobs),
                                func.avg(Measurement.tobs)).\
                  filter(Measurement.date >= start).\
                  group_by(Measurement.station).all()

    return jsonify(stats_query)


'''-----------------------------------------------------------------
Flask stats API given start date and end date
------------------------------------------------------------------'''

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    
    stats_query = session.query(Measurement.station,
                                func.min(Measurement.tobs),
                                func.max(Measurement.tobs),
                                func.avg(Measurement.tobs)).\
                  filter(Measurement.date >= start).\
                  filter(Measurement.date <= end).\
                  group_by(Measurement.station).all()
    
    return jsonify(stats_query)


'''^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''

if __name__ == "__main__":
    app.run(debug = True)
    
'''^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''
