# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables

Base.prepare(engine,reflect=True)
# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup

app = Flask(__name__)

#################################################
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
  
       # Calculate the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    
    # Calculate the date one year from the most recent date
    one_year_ago = most_recent_date - timedelta(days=365)
    
    # Design a query to retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary with date as key and prcp as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Design a query to retrieve the list of stations
    stations_list = session.query(Station.station).all()
    stations_flat = [station[0] for station in stations_list]
    
    return jsonify(stations_flat)

@app.route("/api/v1.0/tobs")
def tobs():
    # Get the most active station ID
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
       # Calculate the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    
    # Calculate the date one year from the most recent date
    one_year_ago = most_recent_date - timedelta(days=365)
    
    # Design a query to retrieve temperature data for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    # Design a query to calculate temperature statistics for a specified start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    # Design a query to calculate temperature statistics for a specified start and end date
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)
