'''
Postgres tables for the VEP CWL Workflow
'''
from postgres.mixins import StatusTypeMixin
import postgres.utils
import postgres.time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table

from sqlalchemy import Column, Integer, String, Float, cast

class VEPStatus(StatusTypeMixin, postgres.utils.Base):

    __tablename__ = 'vep_cwl_status'

def add_status(engine, case_id, vcf_id, src_vcf_id, file_ids, status, output_location, datetime_now, md5, hostname):
    """ add provided status metrics to database """
    met = VEPStatus(case_id = case_id,
              vcf_id        = vcf_id,
              src_vcf_id    = src_vcf_id,
              files         = file_ids,
              status        = status,
              location      = output_location,
              datetime_now  = datetime_now,
              md5           = md5,
              hostname      = hostname)

    postgres.utils.create_table(engine, met)
    postgres.utils.add_metrics(engine, met)

def set_download_error(exit_code, case_id, vcf_id, src_vcf_id, file_ids, object_store, 
                       datetime_now, threads, elapsed, engine, logger, hostname):
    ''' Sets the status for download errors '''
    loc    = 'UNKNOWN'
    md5    = 'UNKNOWN'
    if exit_code != 0:
        logger.info('Input file download error from {0}'.format(object_store))
        status = 'DOWNLOAD_FAILURE'
        add_status(engine, case_id, vcf_id, src_vcf_id, file_ids, status, loc, datetime_now, md5, hostname)
        # Set metrics table
        met = postgres.time.Time(case_id = case_id,
                   datetime_now = datetime_now,
                   vcf_id       = vcf_id,
                   src_vcf_id   = src_vcf_id, 
                   files        = file_ids, 
                   elapsed      = elapsed, 
                   thread_count = threads, 
                   status = status,
                   hostname = hostname)

        postgres.utils.create_table(engine, met)
        postgres.utils.add_metrics(engine, met)
    else:
        logger.info('Input file size 0 from {0}'.format(object_store))
        status = 'INPUT_EMPTY'
        add_status(engine, case_id, vcf_id, src_vcf_id, file_ids, status, loc, datetime_now, md5, hostname)
        # Set metrics table
        met = postgres.time.Time(case_id = case_id,
                   datetime_now = datetime_now,
                   vcf_id       = vcf_id,
                   src_vcf_id   = src_vcf_id, 
                   files        = file_ids, 
                   elapsed      = elapsed, 
                   thread_count = threads, 
                   status = status,
                   hostname = hostname)

        postgres.utils.create_table(engine, met)
        postgres.utils.add_metrics(engine, met)

def set_no_input_variants_error(case_id, vcf_id, src_vcf_id, file_ids,
                   object_store, datetime_now, threads, elapsed, engine, logger, hostname):
    ''' Sets the status for input VCF files with no variants '''
    loc    = 'UNKNOWN'
    md5    = 'UNKNOWN'

    logger.info('Error! Input VCF has no variants!')
    status = 'NO_INPUT_VARIANTS'
    add_status(engine, case_id, vcf_id, src_vcf_id, file_ids, status, loc, datetime_now, md5, hostname)
    # Set metrics table
    met = postgres.time.Time(case_id = case_id,
               datetime_now = datetime_now,
               vcf_id       = vcf_id,
               src_vcf_id   = src_vcf_id,
               files        = file_ids,
               elapsed      = elapsed,
               thread_count = threads,
               status = status,
               hostname = hostname)

    postgres.utils.create_table(engine, met)
    postgres.utils.add_metrics(engine, met)
 
def get_status(exit, cwl_failure, vcf_upload_location, vep_location, logger):
    """ get the status of job based on s3upload and cwl status """

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
