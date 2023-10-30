# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text, inspect
from flask import Flask, jsonify
from datetime import datetime
#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///sql_alchemy_challenge/Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
# reflect the tables
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/><br/>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of percipitation data for the last 12 months<br/><br/>"
        f"/api/v1.0/stations<br/>Returns JSON list of stations with station and name<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns the dates and temperature observations of the most-active station for the previous year of data<br/><br/>"  
        f"/api/v1.0/<start><br/>Returns a JSON list of the min, average and max temperature for the dates between the given start date and latest date<br/><br/>"  
        f"/api/v1.0/<start>/<end><br/>Returns a JSON list of the min, average and max temperature for the dates between the given start date and given end date<br/><br/>"        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
   session = Session(engine)
   most_recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
   split_date = datetime.strptime(most_recent_date[0], "%Y-%m-%d")
   query_date = dt.date(split_date.year,split_date.month,split_date.day) - dt.timedelta(days=365)

   """Return a list of Measurement data including the prcp and date for last 12 months"""
   prcp_scores=session.query(Measurement.prcp,Measurement.date).\
                filter(Measurement.date>=query_date).all()
   session.close()

   # Create a dictionary from the row data and append to a list of all_prcp_scores
   all_prcp_scores = []
   for prcp,date in prcp_scores:
        prcp_dict = {}
        prcp_dict["prcp"] = prcp
        prcp_dict["date"] = date
        all_prcp_scores.append(prcp_dict)  
   return jsonify(all_prcp_scores)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    all_stations = session.query(Station.name).all()
    # Convert list of tuples into normal list
    all_station_names = list(np.ravel(all_stations))
    session.close()
    return jsonify(all_station_names)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
   session = Session(engine)
   stations=session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
   most_active_station=stations[0]['station']
# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
   recent_date=session.query(Measurement.date).\
            filter(Measurement.station==most_active_station).order_by(Measurement.date.desc()).first()

   split_date = datetime.strptime(recent_date[0], "%Y-%m-%d")
   query_date = dt.date(split_date.year,split_date.month,split_date.day) - dt.timedelta(days=365)

   """Return a list of tobs data of most active station for last 12 months"""
   temperature=session.query(Measurement.tobs,Measurement.date).\
                filter(Measurement.date>=query_date).\
                filter(Measurement.station == most_active_station).all()
   session.close()

   # Create a dictionary from the row data and append to a list of tobs_scores
   tobs_scores = []
   for tobs,date in temperature:
        tobs_dict = {}
        tobs_dict["tobs"] = tobs
        tobs_dict["date"] = date
        tobs_scores.append(tobs_dict)  
   return jsonify(tobs_scores)



@app.route("/api/v1.0/<start>")
def startDateOnly(start):
    temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    # Convert list of tuples into normal list
    temp_results_start = list(np.ravel(temp_results))
    return jsonify(temp_results_start)

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    temp_results_betweven_dates = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_results_start_end = list(np.ravel(temp_results_betweven_dates))
    return jsonify(temp_results_start_end)

if __name__ == '__main__':
    app.run(debug=True)
