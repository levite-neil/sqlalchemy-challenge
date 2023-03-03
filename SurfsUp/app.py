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
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
#Base.classes.keys()
Measurement = Base.classes.measurement
Station  = Base.classes.station

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
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end_date>"
    )
@app.route("/api/v1.0/percipitation")
def percipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    measure_last_twelve = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.date <= '2017-08-23')
    result = [{result[0] : result[1]} for result in measure_last_twelve]

    session.close()

    return jsonify(result)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station data"""
    # Query all station names data
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Getting the latest date from the most active to have a reference point on obtaining the last 12 months
    date_recent = session.query(Measurement.date).\
                filter(Measurement.station == "USC00519281").\
                order_by(Measurement.date.desc()).first()

    # Perform a query to retrieve the most active station for the previous year.
    active_station_past_year = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date <= date_recent[0]).\
        filter(Measurement.date >= (dt.date(int(date_recent[0][0:4]),int(date_recent[0][6]),int(date_recent[0][8:10])) - dt.timedelta(days=365))).\
        all()

    session.close()

    # Convert list of tuples into normal list
    active_station = list(np.ravel(active_station_past_year))

    return jsonify(active_station)

@app.route("/api/v1.0/<start>")
def start_date(start):
    #Splitting the start date to get it into a date type
    year_start, month_start, day_start = start.split('-') 
    start_date = dt.date(int(year_start),int(month_start),int(day_start))

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Minimum Temperature, average temperature, and maxium temperature
    range_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()
    
    results = [{"Min": range_result[0], "Max":range_result[1], "Avg" : range_result[2]} for range_result in range_results]

    session.close()

    # Convert list of tuples into normal list
    stats_nums = list(np.ravel(results))

    return jsonify(stats_nums)

@app.route("/api/v1.0/<start>/<end>")
def start_end_dates(start, end):
    #Splitting the start date to get it into a date type
    year_start, month_start, day_start = start.split('-') 
    start_date = dt.date(int(year_start),int(month_start),int(day_start))

    #Splitting the end date to get it into a date type
    year_end, month_end, day_end = end.split('-') 
    end_date = dt.date(int(year_end),int(month_end),int(day_end))
  
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Minimum Temperature, average temperature, and maxium temperature
    range_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all()
    
    results = [{"Min": range_result[0], "Max":range_result[1], "Avg" : range_result[2]} for range_result in range_results]

    session.close()

    # Convert list of tuples into normal list
    stats_nums = list(np.ravel(results))

    return jsonify(stats_nums)

if __name__ == '__main__':
    app.run(debug=True)

