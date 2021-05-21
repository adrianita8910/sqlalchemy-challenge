import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"

    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
# Calculate the date one year from the last date in data set.
    previous = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= previous).all()
    # Dictionary with the date as the key and the precipitation as the value
    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precip"] = prcp
        precip.append(precip_dict)

    return jsonify(precip)
    session.close()
    

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to show all of the stations available in this dataset
    station_count = session.query(Station.station, Station.name).all()

    # unravel the results into list
    stations = []
    for station, name in station_count:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        stations.append(station_dict)

    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    previous = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    pre_previous = previous - dt.timedelta(days=365)
    # Design a query the dates and temperature observations of the most active station for the last year of data.
    temp_station = session.query(Measurement.station, func.count(Measurement.tobs)).\
                    filter(Measurement.date >= previous).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.tobs).desc()).first()

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_data = session.query(Measurement.tobs).\
                        filter(Measurement.station == temp_station[0]).\
                        filter(Measurement.date >= pre_previous).\
                        filter(Measurement.date < previous).all()



    session.close()
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def start(start):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    start_1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()

    start_data = []
    for min, avg, max in start_1:
        start_dict = {}
        start_dict["min"] = min
        start_dict["avg"] = avg
        start_dict["max"] = max
        start_data.append(start_dict)
    
    session.close()
    return jsonify(start_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    start_2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()

    
    start_data_end = []
    for min, avg, max in start_2:
        start_dict_end = {}
        start_dict_end["min"] = min
        start_dict_end["avg"] = avg
        start_dict_end["max"] = max
        start_data_end.append(start_dict_end)
    
    session.close()
    return jsonify(start_data_end)

if __name__ == '__main__':
    app.run(debug=True)