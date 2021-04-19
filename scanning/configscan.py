import abc
import pydaq
import pycdb
import logging
import argparse
import numpy as np


logger = logging.getLogger(__name__)


class SimXtc:
    def __init__(self, src):
        self.src = src
        self.xtcs = {}

    def get(self, cycle):
        if PartitionInfo.get_dev(self.src) in [48, 50]:
            # Epix10ka2M and Epix10kaQuad
            cfg = {
                'elemCfg': [{
                    'asicMask': 0xf,
                    'asicPixelConfigArray': [[0]*384] * 352,
                    'asics': [{'atest': 0, 'test': 0, 'trbit': 0, 'Pulser': 0, 'PulserSync': 0}] * 4,
                }],
                'quads': [{
                    'asicAcqLToPPmatL': 0,
                }],
            }
            return self.xtcs.get(cycle, cfg)
        elif PartitionInfo.get_dev(self.src) == 45:
            # Epix10ka
            cfg = {
                'asicMask': 0xf,
                'asicPixelConfigArray': [[0]*384] * 352,
                'asics': [{'atest': 0, 'test': 0, 'trbit': 0, 'Pulser': 0, 'PulserSync': 0}] * 4,
                'asicAcqLToPPmatL': 0,
            }
            return self.xtcs.get(cycle, cfg)
        else:
            return self.xtcs.get(cycle, {})

    def set(self, xtc, cycle):
        self.xtcs[cycle] = xtc


class ConfigDB:
    def __init__(self, path, alias, sim=False):
        self.__db = None if sim else pycdb.Db(path)
        self.alias = alias
        self.__key = None

    @property
    def key(self):
        if self.__key is None:
            if self.__db is None:
                self.__key = 0
            else:
                self.__key = self.__db.clone(self.alias)
        return self.__key

    def get(self, src, typeid=None):
        if self.__db is not None:
            if typeid is not None:
                return self.__db.get(key=self.key, src=src, typeid=typeid)
            else:
                return self.__db.get(key=self.key, src=src)
        else:
            return [SimXtc(src)]

    def substitute(self, xtc):
        if self.__db is not None:
            self.__db.substitute(self.key, xtc)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__db is not None:
            self.__db.unlock()


class DetectorConfig(abc.ABC):
    def __init__(self, devtype, name, src, spacing, values, typeid=None, namesize=None):
        self.devtype = devtype
        self.name = name
        self.src = src
        self.spacing = spacing
        self.values = values
        self.typeid = typeid
        self.ncycles = 0
        self.xtc = None
        self.config = None
        # maximum length allowed in pvlabels
        self.scan_name_suffix = " scan"
        if namesize is not None:
            self.scan_name_max = namesize - len(self.scan_name_suffix) - 1
        else:
            self.scan_name_max = None

    @abc.abstractmethod
    def cycle_name(self, cycle):
        pass

    def is_calib(self, cycle):
        return False

    @property
    @abc.abstractmethod
    def max_dark(self):
        pass

    @property
    def scan_name(self):
        if self.scan_name_max is None or len(self.name) < self.scan_name_max:
            return self.name + self.scan_name_suffix
        else:
            # try removing the XcsEndStation, MecTargetChamber, etc. part of the name
            splitname = self.name.split('|')[-1]
            if splitname and len(splitname) < self.scan_name_max:
                return splitname + self.scan_name_suffix
            else:
                return self.name[:self.scan_name_max] + self.scan_name_suffix

    @property
    def max_cycle(self):
        return self.max_dark

    @property
    def use_config(self):
        return True

    @abc.abstractmethod
    def _configure(self, cycle):
        pass

    def configure(self, db, cycle):
        if cycle < self.max_cycle:
            if self.xtc is None:
                self.ncycles = 0
                if self.use_config:
                    if self.typeid is not None:
                        self.xtc = db.get(self.src, self.typeid)[0]
                    else:
                        self.xtc = db.get(self.src)[0]
                else:
                    self.xtc = SimXtc(self.src)
                self.config = self.xtc.get(0)
                logger.debug("Retrieved configuration for %s from db: %s",
                             self.name, self.config)
            if self._configure(cycle):
                logger.debug("Modified configuration for %s for cycle %d: %s",
                             self.name, cycle, self.config)
                self.xtc.set(self.config, self.ncycles)
                self.ncycles += 1
            return self.is_calib(cycle)
            
    def complete(self, db):
        if self.ncycles > 0:
            db.substitute(self.xtc)
        self.xtc = None
        self.config = None


class SimpleConfig(DetectorConfig):
    def __init__(self, devtype, name, src, spacing, values, typeid=None, namesize=None):
        super().__init__(devtype, name, src, spacing, values, typeid, namesize)
        self.ndarks = 1

    def cycle_name(self, cycle):
        if cycle < self.ndarks:
            return "pedestal"

    @property
    def max_dark(self):
        return self.ndarks

    @property
    def use_config(self):
        return False

    def _configure(self, cycle):
        return False


class JungfrauConfig(DetectorConfig):
    def __init__(self, devtype, name, src, spacing, values, typeid=None, namesize=None):
        super().__init__(devtype, name, src, spacing, values, typeid, namesize)
        self.dark_info = [
            ('Normal', 0),
            ('ForcedGain1', 3),
            ('ForcedGain2', 4),
        ]
        self.ndarks = len(self.dark_info)

    def cycle_name(self, cycle):
        if cycle < self.ndarks:
            return self.dark_info[cycle][0]

    @property
    def max_dark(self):
        return self.ndarks

    def _configure(self, cycle):
        if cycle < self.ndarks:
            name, value = self.dark_info[cycle]
            logger.debug("Setting 'gainMode' to %s for %s",
                         name, self.name)
            self.config['gainMode'] = value
            return True
        else:
            return False


class EpixConfig(DetectorConfig):
    def __init__(self, devtype, name, src, spacing, values, typeid=None, namesize=None):
        super().__init__(devtype, name, src, spacing, values, typeid, namesize)
        self.dark_info = [
            ('Fixed High Gain', 0xc, 1),
            ('Fixed Medium Gain', 0xc, 0),
            ('Fixed Low Gain', 0x8, 0),
            ('Auto High to Low', 0, 1),
            ('Auto Medium to Low', 0, 0),
        ]
        self.ndarks = len(self.dark_info)
        self.ncalib = spacing ** 2
        self.nrows = 352
        self.ncols = 384
        self.nasics = 4
        self.asicAcqLToPPmatL = 1000
        if self.devtype in ['Epix10kaQuad', 'Epix10ka2M']:
            self.ghostCorrect = True
        else:
            self.ghostCorrect = False

    def _calib_values(self, cycle):
        calib = cycle - self.ndarks
        return calib % self.ncalib, calib // self.ncalib

    def _pixel_mask(self, value0, value1, spacing, position):
        logger.debug("Creating pixel mask with values: %d %d %d %d",
                     value0, value1, spacing, position)
        if position>=spacing**2:
            logger.warning('Charge injection position for %s is out of range: %d',
                           self.name, position)
            position=0
        out = np.zeros((self.nrows, self.ncols), dtype=np.int) + value0
        position_x = position % spacing
        position_y = position // spacing
        out[position_y::spacing,position_x::spacing] = value1
        return out

    def cycle_name(self, cycle):
        if cycle < self.ndarks:
            return f'dark {self.dark_info[cycle][0]}'
        elif cycle < self.max_cycle:
            position, trbit = self._calib_values(cycle)
            return f'position {position} trbit {trbit}'

    def is_calib(self, cycle):
        return cycle >= self.ndarks

    @property
    def max_dark(self):
        return self.ndarks

    @property
    def max_cycle(self):
        return self.ndarks + self.ncalib * 2

    def _pedestal(self, cycle):
        _, darkValue, trbitValue = self.dark_info[cycle]
        if 'elemCfg' in self.config:
            for e in self.config['elemCfg']:
                mask = e['asicMask']
                for rows in range(self.nrows):
                    for cols in range(self.ncols):
                        e['asicPixelConfigArray'][rows][cols] = darkValue
                for asicNum in range(self.nasics):
                    if mask & (1 << asicNum) :
                        e['asics'][asicNum]['trbit'] = trbitValue
        else:
            mask = self.config['AsicMask']
            for rows in range(self.nrows):
                for cols in range(self.ncols):
                    self.config['asicPixelConfigArray'][rows][cols] = darkValue
                for asicNum in range(self.nasics):
                    if mask & (1 << asicNum):
                        self.config['asics'][asicNum]['trbit'] = trbitValue

        return True

    def _charge_injection(self, position, trbit):
        maskedpixels = self._pixel_mask(*self.values, self.spacing, position)
        if 'elemCfg' in self.config:
            for e in self.config['elemCfg']:
                mask = e['asicMask']
                for rows in range(self.nrows):
                    for cols in range(self.ncols):
                        e['asicPixelConfigArray'][rows][cols] = maskedpixels[rows][cols]
                for asicNum in range(self.nasics) :
                    if mask & (1 << asicNum) :
                        e['asics'][asicNum]['atest']=1
                        e['asics'][asicNum]['test']=1
                        e['asics'][asicNum]['trbit']=trbit
                        e['asics'][asicNum]['Pulser']=0
                        if self.ghostCorrect:
                            e['asics'][asicNum]['PulserSync']=1
        else:
            mask = self.config['AsicMask']
            for rows in range(self.nrows):
                for cols in range(self.ncols):
                    self.config['asicPixelConfigArray'][rows][cols] = maskedpixels[rows][cols]
            for asicNum in range(self.nasics):
                if mask & (1 << asicNum):
                    self.config['asics'][asicNum]['atest']=1
                    self.config['asics'][asicNum]['test']=1
                    self.config['asics'][asicNum]['trbit']=trbit
                    self.config['asics'][asicNum]['Pulser']=0
                    if self.ghostCorrect:
                        self.config['asics'][asicNum]['PulserSync']=1
        if self.ghostCorrect:
            if 'quads' in self.config:
                for q in self.config['quads']:
                    q['asicAcqLToPPmatL']=self.asicAcqLToPPmatL
            else:
                self.config['asicAcqLToPPmatL']=self.asicAcqLToPPmatL

        return True

    def _configure(self, cycle):
        if cycle < self.ndarks:
            return self._pedestal(cycle)
        elif cycle < self.ncalib * 2:
            position, trbit = self._calib_values(cycle)
            return self._charge_injection(position, trbit)
        else:
            return False


def _get_device_config_handlers():
    special_handlers = {
        'Jungfrau': JungfrauConfig,
        'Epix10ka': EpixConfig,
        'Epix10kaQuad': EpixConfig,
        'Epix10ka2M': EpixConfig,
    }
    excluded_handlers = {
        'NoDevice',
        'Evr',
        'Acqiris',
        'Ipimb',
        'Encoder',
        'AcqTDC',
        'Xamps',
        'Fexamp',
        'Gsc16ai',
        'OceanOptics',
        'USDUSB',
        'Imp',
        'Epix',
        'EpixSampler',
        'Wave8',
        'LeCroy',
        'JungfrauSegment',
        'JungfrauSegmentM2',
        'JungfrauSegmentM3',
        'JungfrauSegmentM4',
        'QuadAdc',
    }
    daq = pydaq.Control(0)

    return {dev: special_handlers.get(dev, SimpleConfig) for dev in daq.devices() if dev not in excluded_handlers}


DEVICE_CONFIG_HANDLERS = _get_device_config_handlers()


class PartitionInfo:
    def __init__(self, daq):
        self.partition = daq.partition()
        self.devices = daq.devices()
        self.detectors = daq.detectors()

    def lookup_dev(self, name):
        try:
            return self.devices.index(name)
        except ValueError:
            return -1

    def lookup_det(self, name):
        try:
            return self.detectors.index(name)
        except ValueError:
            return -1

    @staticmethod
    def get_dev(phy):
        return (phy & 0xff00) >> 8

    @staticmethod
    def get_devid(phy):
        return _phy & 0xff

    @staticmethod
    def get_det(phy):
        return (phy & 0xff000000) >> 24

    @staticmethod
    def get_detid(phy):
        return (phy & 0xff0000) >> 16

    @staticmethod
    def sort_devices(devinfo):
        result = {}
        for devtype, devices in sorted(devinfo.items()):
            result[devtype] = sorted(devices, key=lambda x: x[0])
        return result

    def find_devices(self, devtypes):
        found = { name: [] for name in devtypes }
        for node in self.partition['nodes']:
            for dev in devtypes:
                if (self.get_dev(node['phy']) == self.lookup_dev(dev)):
                    found[dev].append((node['id'], node['phy']))
                    break
        return self.sort_devices(found)


def _init_logger(level, logfile=None):
    log_handlers = [logging.StreamHandler()]
    if logfile is not None:
        file_format = logging.Formatter('[ %(asctime)s | %(levelname)-8s] %(message)s')
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(file_format)
        log_handlers.append(file_handler)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(format='%(message)s', level=log_level, handlers=log_handlers)


def cli_scan_calibration(devtypes=None):
    parser = argparse.ArgumentParser(description='Detector pedestal/calibration script')
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
            "-A",
            "--dbalias",
            dest="dbalias",
            help="data base key in use"
    )
    parser.add_argument(
            "-s",
            "--space",
            dest="space",
            type=int,
            default=7,
            help="space is the spacing in the array"
    )
    parser.add_argument(
            "-e",
            "--events",
            dest="events",
            type=int,
            default=4608,
            help="record N events/cycle"
    )
    parser.add_argument(
            "-v",
            "--value0",
            dest="Value0",
            type=int,
            default=0,
            help="Value0 for most of the pixel array, default=0 "
    )
    parser.add_argument(
            "-V",
            "--value1",
            dest="Value1",
            type=int,
            default=1,
            help="Value1 for pixels under test in the pixel array, default=1"
    )
    parser.add_argument(
            "-d",
            "--darkEvents",
            dest="darkEvents",
            type=int,
            default=1200,
            help="Number of events in each Dark, default=1200"
    )
    parser.add_argument(
            "-u",
            "--user",
            dest="userFlag",
            action="store_false",
            help="Disable user prompts"
    )
    parser.add_argument(
            "-o",
            "--cycleStart",
            dest="cycleStart",
            type=int,
            default=0,
            help="Starting at cycle number, default=0"
    )
    parser.add_argument(
            "-O",
            "--cycleStop",
            dest="cycleStop",
            type=int,
            default=105,
            help="Stopping at cycle number, default=105"
    )
    parser.add_argument(
            '-r',
            '--enableRecord',
            dest='record',
            action="store_true",
            help='force the daq to record overriding the choice in the control GUI'
    )
    parser.add_argument(
            '-R',
            '--disableRecord',
            dest='record',
            action="store_false",
            help='force the daq to record overriding the choice in the control GUI'
    )
    parser.set_defaults(record=None)
    parser.add_argument(
            '-f',
            '--fullCalib',
            action="store_true",
            help='enable full calibrations - e.g. charge injection of epix10ka'
    )
    parser.add_argument(
            '-S',
            '--sim',
            action="store_true",
            help='simulate pedestal/calibration run - database is not touched'
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

    options = parser.parse_args()

    # set up the logger
    _init_logger(options.log_level, options.log_file)

    if devtypes is None:
        devtypes = list(DEVICE_CONFIG_HANDLERS)
    scan_calibration(devtypes, options)


def scan_calibration(devtypes, options):

    # if only a single device type was passed change to a list
    if isinstance(devtypes, str):
        devtypes = [devtypes]

    if logger.isEnabledFor(logging.INFO):
        logger.info('Detector pedestal/calibration script settings to use:')
        logger.info('  host: %s', options.host)
        logger.info('  platform: %s', options.platform)
        logger.info('  dbalias: %s',options.dbalias)
        logger.info('  devtypes: %s', devtypes)
        if options.space > 7 :
            logger.warning('Space is too large, truncated to 7')
            options.space = 7
        logger.info('  space: %s', options.space)
        logger.info('  Values: %s, %s', options.Value0, options.Value1)
        logger.info('  darkEvents: %s', options.darkEvents)
        logger.info('  events: %s', options.events)
        logger.info('  userFlag: %s', options.userFlag)
        logger.info('  cycleStart: %s', options.cycleStart)
        logger.info('  cycleStop: %s', options.cycleStop)
        logger.info('  fullCalib: %s', options.fullCalib)
        logger.info('  record: %s', options.record)
        logger.info('  simMode: %s', options.sim)

    # configuration handlers for each detector
    configs = {}
    ncycles = 0
    # Connect to the daq system
    logger.debug('Connecting to the DAQ at %s with platform %d',
                 options.host, options.platform)
    daq = pydaq.Control(options.host, options.platform)
    daq.connect()
    info = PartitionInfo(daq)
    logger.debug('Current DAQ partition: %s', info.partition)
    devices = info.find_devices(devtypes)
    logger.info('Selected the following detectors to scan in the partition:')
    max_label_size = daq.sizes().get('LabelNameSize')
    logger.debug('Maximum allowed length of label names: %d', max_label_size)
    for devtype, devs in sorted(devices.items()):
        # only print devtype if there are devices of that type
        if devs:
            logger.info('  %s:', devtype)
        for name, src  in devs:
            logger.info('    %s', name)
            if devtype in DEVICE_CONFIG_HANDLERS:
                handler = DEVICE_CONFIG_HANDLERS[devtype]
                logger.debug('Creating configuration handler of type %s for %s',
                             handler.__name__, name)
                configs[name] = handler(
                    devtype,
                    name,
                    src,
                    options.space,
                    (options.Value0, options.Value1),
                    namesize=max_label_size
                )
                # check which detector has the highest max_cycles/max_dark
                if options.fullCalib:
                    if configs[name].max_cycle > ncycles:
                        ncycles = configs[name].max_cycle
                else:
                    if configs[name].max_dark > ncycles:
                        ncycles = configs[name].max_dark
            else:
                logger.warning('Unsupported detector type: %s', devtype)

    # select the default number of events for each cycle
    nevents = [options.darkEvents] * ncycles
    # prepare the database
    key = daq.dbkey()
    alias = daq.dbalias()
    newkey = None
    logger.info('Retrieved key %x with alias %s from the DAQ', key, alias)
    # override the alias to use if one is passed to the script
    if options.dbalias is not None:
        logger.debug('Switching to user specified alias %s', options.dbalias)
        alias = options.dbalias

    with ConfigDB(daq.dbpath(), alias, sim=options.sim) as cdb:
        logger.info('Cloned the alias %s to new key %x', cdb.alias, cdb.key)
        logger.info('Composing the sequence of configurations ...')
        for cycle in range(ncycles) :
            if cycle >= options.cycleStart and cycle < options.cycleStop:
                for name, config in configs.items():
                    logger.debug("Creating cycle %d for %s", cycle, name)
                    if config.configure(cdb, cycle):
                        nevents[cycle] = options.events
        # complete the database update
        for name, config in configs.items():
            logger.debug("Completing configuration for %s", name)
            config.complete(cdb)
        logger.info(' Done')
        # save the value of the keyy before closing db
        newkey = key if options.sim else cdb.key

    try:
        # Configure the DAQ and add pvlabels with scan metadata
        cycle_labels = [(configs[name].scan_name, '') for devs in devices.values() for name, _ in devs]
        logger.debug("Configuring with key=%x, events=%d, labels=%s, record=%s",
                     newkey, options.events, cycle_labels, options.record)
        if options.record is None:
            daq.configure(key=newkey, events=options.events, labels=cycle_labels)
        else:
            daq.configure(key=newkey, events=options.events, labels=cycle_labels, record=options.record)

        logger.info("Configured.")

        #
        #  Wait for the user to declare 'ready'
        #    Setting up monitoring displays for example
        #
        if options.userFlag > 0 :
            ready = input('--Hit Enter when Ready-->')
    
        for cycle in range(ncycles) :
            if cycle >= options.cycleStart and cycle < options.cycleStop:
                cycle_labels = []
                logger.info('Scan info for calib cycle %d:', cycle)
                logger.debug('  Number of events: %d', nevents[cycle])
                for devs in devices.values():
                    for name, _ in devs:
                        scan_name = str(configs[name].scan_name)
                        cycle_name = str(configs[name].cycle_name(cycle))
                        cycle_labels.append((scan_name, cycle_name))
                        logger.info('  %s: %s', scan_name, cycle_name)
                if not options.sim:
                    logger.debug('Starting calib cycle %d with events=%d, labels=%s',
                                 cycle, nevents[cycle], cycle_labels)
                    daq.begin(events=nevents[cycle], labels=cycle_labels)
                    daq.wait()
                    logger.debug('Finished calib cycle %d', cycle)

        #
        #  Wait for the user to declare 'done'
        #    Saving monitoring displays for example
        #
        if options.userFlag > 0 :
            ready = input('-- Finished, hit Enter to exit -->')
    finally:
        logger.info('Restoring key: %x', key)
        daq.configure(key=key, events=1)
        logger.debug('Disconnecting from the DAQ')
        daq.disconnect()
