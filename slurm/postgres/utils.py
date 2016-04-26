from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import exc
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager

Base = declarative_base()

class CustomToolTypeMixin(object):
    ''' Gather timing metrics with input/output uuids '''
    id = Column(Integer, primary_key=True)
    case_id = Column(String)
    datetime_now = Column(String)
    vcf_id = Column(String)
    src_vcf_id = Column(String)
    files = Column(ARRAY(String))
    elapsed = Column(String)
    thread_count = Column(String)
    status = Column(String)

    def __repr__(self):
        return "<CustomToolTypeMixin(case_id='%s', elapsed='%s', status='%s'>" %(self.systime,
                self.case_id, self.elapsed, self.status) 

class ToolTypeMixin(object):
    """ Gather the timing metrics for different datasets """

    id = Column(Integer, primary_key=True)
    case_id = Column(String)
    datetime_now = Column(String)
    vcf_id = Column(String)
    files = Column(ARRAY(String))
    elapsed = Column(String)
    thread_count = Column(String)
    status = Column(String)

    def __repr__(self):
        return "<ToolTypeMixin(systime='%d', usertime='%d', elapsed='%s', cpu='%d', max_resident_time='%d'>" %(self.systime,
                self.usertime, self.elapsed, self.cpu, self.max_resident_time)

class Metrics(ToolTypeMixin, Base):

    __tablename__ = 'metrics_table'

@contextmanager
def session_scope():
    """ Provide a transactional scope around a series of transactions """

    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def db_connect(database):
    """performs database connection"""

    return create_engine(URL(**database))

def create_table(engine, tool):
    """ checks if a table for metrics exists and create one if it doesn't """

    inspector = Inspector.from_engine(engine)
    tables = set(inspector.get_table_names())
    if tool.__tablename__ not in tables:
        Base.metadata.create_all(engine)


def add_metrics(engine, met):
    """ add provided metrics to database """

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    #create table if not present
    create_table(engine, met)

    session.add(met)
    session.commit()
    session.expunge_all()
    session.close()

def update_postgres(exit, cwl_failure, vcf_upload_location, vep_location, logger):
    """ update the status of job on postgres """

    loc = 'UNKNOWN'
    status = 'UNKNOWN'

    if exit == 0:

        loc = vcf_upload_location

        if not(cwl_failure):

            status = 'COMPLETED'
            logger.info("uploaded all files to object store. The path is: %s" %vep_location)

        else:

            status = 'CWL_FAILED'
            logger.info("CWL failed but outputs were generated. The path is: %s" %vep_location)

    else:

        loc = 'Not Applicable'

        if not(cwl_failure):

            status = 'UPLOAD_FAILURE'
            logger.info("Upload of files failed")

        else:
            status = 'FAILED'
            logger.info("CWL and upload both failed")

    return(status, loc)
