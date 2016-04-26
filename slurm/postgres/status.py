'''
Postgres tables for the VEP CWL Workflow
'''
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, Integer, String, Float, cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import exc
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager
from sqlalchemy.sql import select

Base = declarative_base()

class ToolTypeMixin(object):
    """ Gather information about processing status """
    id           = Column(Integer, primary_key=True)
    case_id      = Column(String)
    vcf_id       = Column(String)
    src_vcf_id   = Column(String)
    files        = Column(ARRAY(String))
    status       = Column(String)
    location     = Column(String)
    datetime_now = Column(String)

    def __repr__(self):
        return "<ToolTypeMixin(case_id='%s', status='%s' , location='%s'>" %(self.case_id,
                self.status, self.location)

class VEP(ToolTypeMixin, Base):

    __tablename__ = 'vep_cwl_status'

def db_connect(database):
    """performs database connection"""

    return create_engine(URL(**database))

def create_table(engine, tool):
    """ checks if a table  exists and create one if it doesn't """

    inspector = Inspector.from_engine(engine)
    tables = set(inspector.get_table_names())
    if tool.__tablename__ not in tables:
        Base.metadata.create_all(engine)

def add_status(engine, case_id, vcf_id, src_vcf_id, file_ids, status, output_location, datetime_now):
    """ add provided metrics to database """
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    met = VEP(case_id      = case_id,
              vcf_id       = vcf_id,
              src_vcf_id   = src_vcf_id,
              files        = file_ids,
              status       = status,
              location     = output_location,
              datetime_now = datetime_now)

    create_table(engine, met)
    session.add(met)
    session.commit()
    session.close()

class State(object):
    pass

class Files(object):
    pass

def get_all_vep_inputs(engine, inputs_table='vep_input'):
    '''
    Gets all the input files when the status table is not present.
    '''

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    meta = MetaData(engine)

    #read the status table
    files = Table(inputs_table, meta, 
                  Column("src_vcf_id", String, primary_key=True),
                  autoload=True)

    mapper(Files, files)

    count = 0
    s = dict()

    cases = session.query(Files).all()

    for row in cases:
        s[count] = row 
        count += 1

    return s

def get_vep_inputs_from_status(engine, status_table):
    '''
    Gets the incompleted input files when the status table is present.
    '''
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    meta = MetaData(engine)

    #read the status table
    state = Table(status_table, meta, autoload=True)

    mapper(State, state)

    data = Table('vep_input', meta,
                 Column("src_vcf_id", String, primary_key=True),
                 autoload=True)

    mapper(Files, data)
    count = 0
    s = dict()

    cases = session.query(Files).all()

    for row in cases:

        completion = session.query(State).filter(State.src_vcf_id == row.src_vcf_id).all()

        rexecute = True

        for comp_case in completion:
            if not comp_case == None:
                if comp_case.status == 'COMPLETED':
                    rexecute = False

        if rexecute:
            s[count] = row 
            count += 1
    
    return s
