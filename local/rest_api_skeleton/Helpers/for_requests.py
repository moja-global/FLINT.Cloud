from flask_restful import reqparse
from  werkzeug.datastructures import FileStorage

def title_query():
    query = reqparse.RequestParser()
    query.add_argument("title", required=True, location="form" )
    return query.parse_args() 

def classifier_query():
    query = reqparse.RequestParser()
    query.add_argument("classifiers",type=FileStorage, required=True, action="append", location="files" )
    query.add_argument("attributes", location= "form")
    return query.parse_args() 

def disturbance_query():
    query = reqparse.RequestParser()
    query.add_argument("disturbances",type=FileStorage, required=True, action="append", location="files" )
    query.add_argument("attributes", location= "form")
    return query.parse_args() 

def miscellaneous_query():
    query = reqparse.RequestParser()
    query.add_argument("miscellaneous",type=FileStorage, required=True, action="append", location="files" )
    query.add_argument("attributes", location= "form")
    return query.parse_args() 

