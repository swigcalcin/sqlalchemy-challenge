# Import the dependencies.

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func 
import datetime as dt
from flask import Flask, jsonify 
from dateutil.relativedelta import relativedelta



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()


# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



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
    return(
        f"Avaiable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )
    
    
    #Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    one_year_ago = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = dt.datetime.strptime(one_year_ago[0], "%Y-%m-%d").date()  # Corrected the order
    date_year_ago = latest_date - relativedelta(years=1)
    
    date_from_last_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_year_ago).all()
    
    session.close()

    prcp_data = []
    for date, prcp in date_from_last_year: 
        if prcp is not None:
            precip_dict = {}
            precip_dict = {'date': date, "prcp": prcp}
            prcp_data.append(precip_dict)
            
    return jsonify(prcp_data)

    #Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    stations_info = session.query(Station.station).all()
    
    session.close()
    
    all_stations = list(np.ravel(stations_info))
    
    return jsonify(all_stations)

    
    
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    # Return a JSON list of temperature observations for the previous year. 
@app.route("/api/v1.0/tobs")       
def tobs():
    session = Session(engine)
    
    one_year_ago = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = dt.datetime.strptime(one_year_ago[0], "%Y-%m-%d")
    date_year_ago = latest_date - relativedelta(years=1)
    
    most_active = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()
    
    most_active_id = most_active[0]
    
    data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_id).filter(Measurement.date >= date_year_ago).all()

    session.close()
    
    tobs_data = []
    for date, tobs in data:
        tobs_dict = {"date": date, "tobs": tobs}
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)
    
    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")    
def stats(start=None, end=None):
        session = Session(engine)
        

        select_statement = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
       
        if not end: 
           
           start = dt.datetime.strptime(start, "%Y-%m-%d")
           results = session.query(*select_statement).filter(Measurement.date >= start).all()
           
           session.close()
           
           temps = list(np.ravel(results))
           return jsonify(temps)
           
        session = Session(engine)
        
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        end = dt.datetime.strptime(end, "%Y-%m-%d")
        
        results = session.query(*select_statement).filter(Measurement.date >=start).filter(Measurement.date <= end).all()
        
        session.close()
        
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
       
if __name__=='__main__':
    app.run()
    
      
    
   
    