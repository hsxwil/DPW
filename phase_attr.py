import configparser
import globe_value as gv

def phaseAttrParser():
    cf = configparser.ConfigParser()
    cf.read("controller_config.conf")
    s = cf.sections()
    phaseConf = gv.get_value('phaseConf')

    phaseTiming = {}
    for config_P in phaseConf:
         phaseDict = {'laneIDs': list(map(int,(cf.get(config_P,cf.options(config_P)[0]).split(",")))),
                      'gMax': int(cf.get(config_P,cf.options(config_P)[1])),
                      'gMin': int(cf.get(config_P,cf.options(config_P)[2])),
                      'red': int(cf.get(config_P,cf.options(config_P)[3])),
                      'yellow': int(cf.get(config_P,cf.options(config_P)[4]))}
         phaseTiming[config_P] = phaseDict
    cycle = phaseTiming["1"]['gMax'] + phaseTiming["1"]['red'] + phaseTiming["1"]['yellow']
    # print(phaseTiming["2"]['gMax'])
    return {'cycle': cycle, 'phaseTiming': phaseTiming}

# print(phaseAttrParser())