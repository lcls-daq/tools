import math
import pydaq
import logging
import argparse


logger = logging.getLogger(__name__)


def _init_logger(level, logfile=None):
    log_handlers = [logging.StreamHandler()]
    if logfile is not None:
        file_format = logging.Formatter('[ %(asctime)s | %(levelname)-8s] %(message)s')
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(file_format)
        log_handlers.append(file_handler)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(format='%(message)s', level=log_level, handlers=log_handlers)


def _parse_duration(duration):
    nsec, sec = math.modf(duration)
    return [int(sec), int(nsec*1e9)]


def main(host, platform, nruns, duration, ncalib):
    logger.info('Running with configuration: nruns %d, duration %.1f s, ncalib %d', nruns, duration, ncalib)
    logger.info('Connecting to daq control running on %s with platform %d', host, platform)
    try:
        daq = pydaq.Control(host, platform)
        for n in range(nruns):
            logger.info("Started run %d", n)
            logger.debug("Calling daq configure with events=0")
            daq.configure(events=0)
            for c in range(ncalib):
                logger.info("Started calibcycle %d", c)
                duration_s, duration_ns = _parse_duration(duration)
                logger.debug("Calling daq begin with duration=[%d,%d]", duration_s, duration_ns)
                daq.begin(duration=[duration_s, duration_ns])
                logger.debug("Waiting for daq to finish running")
                daq.wait()
                logger.info("Ended calibcycle %d", c)
            logger.debug("Calling daq endrun")
            daq.endrun()
            logger.info("Ended run %d", n)        
    finally:
        logger.info('Disconnecting from the daq')
        daq.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple script for exercising the daq")

    parser.add_argument(
            "-a",
            "--address",
            dest="host",
            default='localhost',
            help="connect to DAQ at HOST"
    )

    parser.add_argument(
            "-p",
            "--platform",
            dest="platform",
            type=int,
            default=0,
            help="connect to DAQ at PLATFORM"
    )

    parser.add_argument(
            '--log-level',
            default='INFO',
            help='the logging level of the application (default INFO)'
    )

    parser.add_argument(
            '--log-file',
            help='an optional file to write the log output to'
    )

    parser.add_argument(
            'nruns',
            type=int,
            metavar="NRUNS",
            help="the number of runs"
    )

    parser.add_argument(
            'duration',
            type=float,
            metavar="DURATION",
            default=30.0,
            nargs='?',
            help="the duration (in secs) of each calib cycle (default: 30 s)"
    )

    parser.add_argument(
            'ncalib',
            type=int,
            metavar="NCALIB",
            default=1,
            nargs='?',
            help="the number of calib cycles to use (default: 1)"
    )

    args = parser.parse_args()

    # set up the logger
    _init_logger(args.log_level, args.log_file)

    try:
        main(args.host, args.platform, args.nruns, args.duration, args.ncalib)
    except KeyboardInterrupt:
        pass
