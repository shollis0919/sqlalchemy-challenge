# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import os
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
curr_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(curr_dir, 'hawaii.sqlite')
engine = create_engine(f"sqlite:///{db_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station 
Measurement = Base.classes.measurement

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For following routes enter date in YYYY, YYYY-MM, or YYYY-MM-DD format:<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns precipitation data for the last year"""
    # Query for last year of data
    precip_results = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').\
            order_by(Measurement.date.desc()).all()
    
    #Use a dictionary to pass results through
    precip_d= dict(precip_results)

    #Close sesssion and return results
    session.close() 
    return jsonify(precip_d)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station info"""
    # Query all stations
    results = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    #Close sesssion
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for id, station, name, latitude, longitude,elevation in results:
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        all_stations.append(stations_dict)

    #Return results

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns last year of data for most active station"""
    # Query all stations
    tobs_results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date > '2016-08-23', Measurement.station =='USC00519281' ).\
            order_by(Measurement.date.desc()).all()

    #Use a dictionary to pass through results list
    tobs_dict=dict(tobs_results)

    #Close session and return results
    session.close()
    return(tobs_dict)
    

@app.route("/api/v1.0/<start>")
def temp_start_route(start):
    """Return the min,max, and avg temps calculated from specifed start date to end of data"""
    
    start_results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                                filter(Measurement.date >= start).all()
    #package results into a list for passing
    start_results = [tuple(row) for row in start_results]

    #Close session and return results
    session.close()
    return jsonify(start_results)




@app.route("/api/v1.0/<start>/<end>")
def temp_start_end_route(start,end):
    """Return the min,max, and avg temps calculated from specifed start date to specified end of data"""
    
    start_end_results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                                filter(Measurement.date >= start,Measurement.date <= end).all()
    
    #package results into a list for passing

    start_end_results = [tuple(row) for row in start_end_results]

    #Close session and return results
    session.close()
    return jsonify(start_end_results)




if __name__ == '__main__':
    app.run(debug=True)
