# Copyright (c) 2013-2015 Intel, Inc.
# Author Igor Stoppa <igor.stoppa@intel.com>
# Author Topi Kuutela <topi.kuutela@intel.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

"""
Tools for remote controlling a device over ssh.
"""

import aft.tools.misc as tools
import os
import logging
import subprocess32

def _get_proxy_settings():
    """
    Fetches proxy settings from the environment.
    """
    proxy_env_variables = ["http_proxy", "https_proxy", "ftp_proxy", "no_proxy"]

    proxy_env_command = ""
    for var in proxy_env_variables:
        val = os.getenv(var)
        if val != None and val != "":
            proxy_env_command += "export " + var + '="' + val + '"; '
    return proxy_env_command

def test_ssh_connectivity(remote_ip, timeout = 10):
    """
    Test whether remote_ip is accessible over ssh.
    """
    try:
        remote_execute(remote_ip, ["echo", "$?"], connect_timeout = timeout)
        return True
    except subprocess32.CalledProcessError as err:
        logging.warning("Could not establish ssh-connection to " + remote_ip +
                        ". SSH return code: " + str(err.returncode) + ".")
        return False

def push(remote_ip, source, destination, timeout = 60, ignore_return_codes = None, user = "root"):
    """
    Transmit a file from local 'source' to remote 'destination' over SCP
    """
    scp_args = ["scp", source,
                user + "@" + str(remote_ip) + ":" + destination]
    return tools.local_execute(scp_args, timeout, ignore_return_codes)

def pull(
    remote_ip,
    source,
    destination,
    timeout = 60,
    ignore_return_codes = None,
    user = "root"):
    """
    Transmit a file from remote 'source' to local 'destination' over SCP

    Args:
        remote_ip (str): Remote device IP
        source (str): path to file on the remote filesystem
        destination (str): path to the file on local filesystem
        timeout (integer): Timeout in seconds for the operation
        ignore_return_codes (list(integer)):
            List of scp return codes that will be ignored
        user (str): User that will be used with scp


    Returns:
        Scp output on success

    Raises:
        subprocess32.TimeoutExpired:
            If timeout expired
        subprocess32.CalledProcessError:
            If process returns non-zero, non-ignored return code
    """
    scp_args = [
        "scp",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
        user + "@" + str(remote_ip) + ":" + source,
        destination]
    return tools.local_execute(scp_args, timeout, ignore_return_codes)

def init_log(logger_name, prefix):
    """
    Initialize ssh logger, if it has not been initialized yet
    """
    if not hasattr(init_log, "initialized"):
        logger = logging.getLogger(logger_name)
        formatter = logging.Formatter("%(asctime)s: %(message)s")
        file_handler = logging.FileHandler("ssh.log", mode='w')
        file_handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.propagate = False # Do not send events to parent loggers
        init_log.initialized = True

        logger.info("All commands have following prefix - not repeated due to its length: " + prefix)


def remote_execute(remote_ip, command, timeout = 60, ignore_return_codes = None,
                   user = "root", connect_timeout = 15):
    """
    Execute a Bash command over ssh on a remote device with IP 'remote_ip'.
    Returns combines stdout and stderr if there are no errors. On error raises
    subprocess32 errors.
    """
    logger_name = "ssh_logger"


    ssh_args = ["ssh",
                "-i", "".join([os.path.expanduser("~"), "/.ssh/id_rsa_testing_harness"]),
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "StrictHostKeyChecking=no",
                "-o", "BatchMode=yes",
                "-o", "LogLevel=ERROR",
                "-o", "ConnectTimeout=" + str(connect_timeout),
                user + "@" + str(remote_ip),
                _get_proxy_settings(),]

    # Todo: Figure out a better way to do this. While init_log does nothing
    # after the first call, it's still a stupid way to do this
    init_log(logger_name, " ".join(ssh_args))
    logger = logging.getLogger(logger_name)

    logger.info("Executing " + " ".join(command))

    ret = ""
    try:
        ret = tools.local_execute(ssh_args + command, timeout, ignore_return_codes)
    except subprocess32.CalledProcessError, err:
        logger.error("Command raised exception: " + str(err))
        logger.error("Output: " + str(err.output))
        raise err

    return ret
