import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List available api routes:"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation"""
    # Retrieve the last 12 months of precipitation data
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') - relativedelta(years = 1)
    year_prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert result to dictionary using date as the key and prcp as the value
    all_precipitation = []
    for date, prcp in year_prcp_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return stations"""
    # Retrieve the list of stations
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Convert the station list to a dictionary
    all_stations = []
    for id, station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tobs"""
    # Retrieve the dates and temperature observations of the most-active station for the previous year
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') - relativedelta(years = 1)
    top_station = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()
    year_temp_data = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).filter(Measurement.station == top_station[0]).all()

    session.close()

    # Convert the tobs list to a dictionary
    all_tobs = []
    for station, date, tobs in year_temp_data:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>", defaults={"end": None})
def temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temps"""
    # Return the minimum, average, and maximum temperatures for a specified start or start-end date range

    # If end is not in URL use most_recent_date as end
    if end is None:
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        end = most_recent_date

    temp_query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Convert the tobs list to a dictionary
    all_temps = []
    for min, max, avg in temp_query:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        all_temps.append(temp_dict)

    return jsonify(all_temps)


if __name__ == '__main__':
    app.run(debug=True)