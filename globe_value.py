def _init():
    global _global_dict
    _global_dict = {}

def set_value(name, value):
    _global_dict[name] = value

def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


import configparser
cf = configparser.ConfigParser()
cf.read("./controller_config.conf")

device_id = cf.get("globe_value", "device_id")
fai = cf.getint("globe_value", "fai")
phaseConf = cf.get("globe_value", "phaseConf")  # 1,2,3,4,5,6,7,8
phaseConf = phaseConf.split(",")  # ['1', '2', '3', '4', '5', '6', '7', '8']

trans = cf.get("phase_trans", "trans")
intersection_id = cf.get("globe_value", "intersection_id")
trans_rule = {}
for k, v in cf.items("phase_trans"):
    if k != "trans":
        trans_rule[k] = list(map(int,v.split(",")))    # trans_rule = {'1': [0, 5], '2': [1, 6], '3': [2], '4': [3]}

_init()
set_value("fai", fai)
set_value("phaseConf", phaseConf)
set_value("intersection_id", intersection_id)
set_value("device_id", device_id)
set_value("trans", trans)
set_value("trans_rule",trans_rule)
