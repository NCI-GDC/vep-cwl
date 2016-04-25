import os
import sys
import subprocess

import utils.pipeline

def aws_s3_get(logger, remote_input, local_output, profile, endpoint_url):
    '''
    Uses aws cli to get files from s3.

    remote_input s3bin for files
    local_output path to location of output files
    profile aws s3 credential profile
    endpoint_url endpoint url for s3 store
    '''
    if (remote_input != ""):
        cmd = ['/home/ubuntu/.virtualenvs/p2/bin/aws', '--profile', profile,
               '--endpoint-url', endpoint_url, 's3', 'cp', remote_input,
               local_output, '--recursive']
        print cmd
        exit_code = utils.pipeline.run_command(cmd, logger)

    else:
        raise Exception("invalid input %s" % remote_input)

    return exit_code
