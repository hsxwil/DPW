from logconfig import logger
import globe_value as gv
from phase_attr import phaseAttrParser as papar

ARRIVAL_RATE = 10.0
S = 12.0
FAI = gv.get_value('fai')
phaseConf = gv.get_value('phaseConf')


def effective_green(phaseNumber):
    phaseNumber = str(phaseNumber)
    phaseTiming = papar().get('phaseTiming','None')
    effectiveGreen = phaseTiming[phaseNumber]['gMin'] + phaseTiming[phaseNumber]['yellow']
    return effectiveGreen

def dirac_delta(currentPhaseID, currentPhaseTTC):
    phaseTiming = papar().get('phaseTiming','None')
    effective_green = phaseTiming[str(currentPhaseID)]['gMin'] + phaseTiming[str(currentPhaseID)]['yellow']
    if(currentPhaseTTC >= effective_green):
        return 1
    else:
        return 0

# output phases of green("id"+"phaseStates")
def currentPhaseState(phases):
    currentPhaseStates = []
    logger.info(f'phases: {phases}')
    for item in phases:
        for item2 in item["phaseStates"]:
            if (item2["light"] in ('protected_green', 'permissive_green')
                    and item2["timing"]["counting"]["startTime"] == 0):
                currentPhaseStates.append(item)
            else:
                continue
    logger.info(f'currentPhaseStates: {currentPhaseStates}')
    return currentPhaseStates

def queue_bus(phaseNumber,laneInfos):
    phaseTiming = papar().get('phaseTiming','None')
    for configP in phaseConf:
        if int(configP) == phaseNumber:
            laneIDs = phaseTiming[str(phaseNumber)]["laneIDs"]
    busQueues = []
    for laneID in laneIDs:
        for laneInfo in laneInfos:
            if laneID == laneInfo["lane_id"]:
                try:
                    busQueues.append(float(laneInfo["bus_through_put_flow"])*float(laneInfo["headway"]))
                except KeyError:
                    continue  # 解决空数据的lane报错
    logger.info(f'busQueues: {busQueues}')
    return busQueues

def queue_social(phaseNumber,laneInfos):
    phaseTiming = papar().get('phaseTiming','None')
    for configP in phaseConf:
        if int(configP) == phaseNumber:
            laneIDs = phaseTiming[str(phaseNumber)]["laneIDs"]
    carQueues = []
    for laneID in laneIDs:
        for laneInfo in laneInfos:
            if laneID == laneInfo["lane_id"]:
                try:
                    carQueues.append(float(laneInfo["car_through_put_flow"])*float(laneInfo["headway"]))
                except KeyError:
                    continue  # 解决空数据的lane报错
    logger.info(f'carQueues: {carQueues}')
    return carQueues

def delta_g(laneInfos,phases,phaseNumber):
    busQueues = queue_bus(phaseNumber,laneInfos)
    try:
        distLR = max(busQueues)
        logger.info(f'distLR: {distLR}')
    except (IndexError, ValueError):
        return 0
    currentPhases = currentPhaseState(phases)
    if currentPhases == []:
        logger.error('None type of currente phase')
        return 0
    for currentPhase in currentPhases:
        if currentPhase["id"] != phaseNumber:
            continue
        else:
            for item in currentPhase["phaseStates"]:
                if item['light'] in ('protected_green', 'permissive_green'):
                    deltaG = distLR/(S-ARRIVAL_RATE) - item["timing"]["counting"]["likelyEndTime"]
                    if deltaG < 0:
                        deltaG = 0
                    logger.info(f'deltaG: {deltaG}')
                    return deltaG

def dpw_single_green(laneInfos,phases,phaseNumber):
    currentPhases = currentPhaseState(phases)
    if currentPhases == []:
        logger.error(currentPhases)
        return 0
    currentPhase = None
    for currentPhase in currentPhases:
        if currentPhase["id"] != phaseNumber:
            continue
        else:
            break
    light = currentPhase["phaseStates"][1]['light']
    likelyEndTime = currentPhase["phaseStates"][1]["timing"]["counting"]["likelyEndTime"]
    deltaG = delta_g(laneInfos,phases,phaseNumber)
    effectiveGreen = effective_green(phaseNumber)
    phaseTiming = papar().get('phaseTiming','None')
    greenDiff = deltaG + phaseTiming[str(phaseNumber)]['gMax'] - phaseTiming[str(phaseNumber)]['gMin']
    logger.error(greenDiff)
    if light in ('protected_green', 'permissive_green'):
        effectiveTTC = likelyEndTime + phaseTiming[str(phaseNumber)]['yellow']
        slop = -(deltaG + effectiveTTC - effectiveGreen)/ greenDiff
        singledpw = 1+slop * dirac_delta(phaseNumber, likelyEndTime)
    else:
        slop = -(deltaG + likelyEndTime - effectiveGreen)/greenDiff
        singledpw = 1+slop * dirac_delta(phaseNumber, likelyEndTime)
    logger.info(f'singledpw: {singledpw}')
    return singledpw

def dpw_single_red(phases,phaseNumber):
    currentPhases = currentPhaseState(phases)
    if currentPhases == []:
        singledpw = 0
        logger.error(singledpw)
        return singledpw

    for currentPhase in currentPhases:
        if currentPhase["id"] == phaseNumber:
            continue
        else:
            phaseTiming = papar().get('phaseTiming','None')
            priorityPhaseMaxGreen = phaseTiming[str(currentPhase['id'])]['gMax']
            priorityPhaseMinGreen = phaseTiming[str(currentPhase['id'])]['gMin']
            priorityPhaseYellow = phaseTiming[str(currentPhase['id'])]['yellow']
            if (((priorityPhaseMaxGreen - priorityPhaseMinGreen) <
                    currentPhase["phaseStates"][1]["timing"]["counting"]["likelyEndTime"])
                    and
               (currentPhase["phaseStates"][1]["timing"]["counting"]["likelyEndTime"] <=
                priorityPhaseMaxGreen)):
                numerator = (priorityPhaseMinGreen
                             - (priorityPhaseMaxGreen - currentPhase["phaseStates"][1]["timing"]["counting"]["likelyEndTime"])
                             + priorityPhaseYellow)
                demoninator = phaseTiming[str(phaseNumber)]['red']\
                              - currentPhase["phaseStates"][0]["timing"]["counting"]["likelyEndTime"]\
                              + priorityPhaseMinGreen - \
                              (priorityPhaseMaxGreen - currentPhase["phaseStates"][1]["timing"]["counting"]["likelyEndTime"])\
                              + priorityPhaseYellow
                logger.info(f"demoninator: {demoninator}")
                singledpw = 1 - numerator / demoninator
                logger.info(f"singledpw: {singledpw}")
                return singledpw
            elif (currentPhase["phaseStates"][1]["timing"]["counting"]["likelyEndTime"]
                    <= (priorityPhaseMaxGreen - priorityPhaseMinGreen)):
                try:
                    singledpw = 1 - 1 / (phaseTiming[str(phaseNumber)]['red']
                                         - currentPhase["phaseStates"][0]["timing"]["counting"]["likelyEndTime"])
                except ZeroDivisionError:
                    logger.error("ZeroDivisionError: float division by zero")
                    singledpw = 0
                logger.info(f"singledpw: {singledpw}")
                return singledpw


def dpw_bus(laneInfos,phases,phaseNumber):
    '''
    功能：求解某一相位（phaseNumber）的公交车辆（bus）的dpw值
    参数：
        1.laneInfos:list
        2.phases:list,相位状态信息
        3.phaseNumber:需要计算dpw_bus的某一相位
    '''
    busQueues = queue_bus(phaseNumber,laneInfos)
    totalBusQueue = 0
    for item in busQueues:
        totalBusQueue += item
    phaseTiming = papar().get('phaseTiming','None')
    cycle = papar()['cycle']
    LAMDA = phaseTiming[str(phaseNumber)]['gMax']/cycle
    for i in range(len(phases)):
        if ((phases[i]["id"] == phaseNumber) and
                ((phases[i]["phaseStates"][1]["timing"]["counting"]["startTime"]) == 0
            or (phases[i]["phaseStates"][2]["timing"]["counting"]["startTime"]) == 0)):
            singledpwG = dpw_single_green(laneInfos,phases,phaseNumber)
            singledpwG_homo = singledpwG * LAMDA
            singledpwG_homo = singledpwG
            totalBusdpw = totalBusQueue * singledpwG_homo
            logger.info(f"totalBusdpw: {totalBusdpw}")
            return totalBusdpw
        elif ((phases[i]["id"] == phaseNumber) and
            (phases[i]["phaseStates"][0]["timing"]["counting"]["startTime"]) == 0):
            singledpwR = dpw_single_red(phases,phaseNumber)
            # print('singledpwR',singledpwR)
            # singledpwR_homo = singledpwR * (1-LAMDA[phaseNumber])
            singledpwR_homo = singledpwR
            # print('totalBusQueue',totalBusQueue)
            # print('singledpwR_homo',singledpwR_homo)
            try:
                totalBusdpw = totalBusQueue * singledpwR_homo
            except TypeError:
                singledpwR_homo = 0
                totalBusdpw = totalBusQueue * singledpwR_homo
            logger.info(f"totalBusdpw: {totalBusdpw}")
            return totalBusdpw
        elif (phases[i]["id"] != phaseNumber):
            continue

def dpw_social(laneInfos,phases,phaseNumber):
    '''
    功能：求解某一相位（phaseNumber）的社会车辆(social)的dpw值
    参数：
        1.laneInfos:list
        2.phases:list,相位状态信息
        3.phaseNumber:需要计算dpw_bus的某一相位
    '''
    socialQueues = queue_social(phaseNumber,laneInfos)
    totalSocialQueue = 0
    for item in socialQueues:
        totalSocialQueue += item
    # print('queueSocial', queueSocial)
    cycle = papar()['cycle']
    phaseTiming = papar().get('phaseTiming','None')
    LAMDA = phaseTiming[str(phaseNumber)]['gMax']/cycle
    for i in range(len(phases)):
        if ((phases[i]["id"] == phaseNumber) and
                    ((phases[i]["phaseStates"][1]["timing"]["counting"]["startTime"]) == 0
                or (phases[i]["phaseStates"][2]["timing"]["counting"]["startTime"]) == 0)):
            singledpwG = dpw_single_green(laneInfos,phases,phaseNumber)
            # singledpwG_homo = singledpwG * LAMDA[phaseNumber]
            singledpwG_homo = singledpwG
            totalSocialdpw = totalSocialQueue * singledpwG_homo
            logger.info(f'totalSocialdpw: {totalSocialdpw}')
            return totalSocialdpw
        elif ((phases[i]["id"] == phaseNumber) and
            (phases[i]["phaseStates"][0]["timing"]["counting"]["startTime"]) == 0):
            singledpwR = dpw_single_red(phases,phaseNumber)
            singledpwR_homo = singledpwR
            try:
                totalSocialdpw = totalSocialQueue * singledpwR_homo
            except TypeError:
                singledpwR_homo = 0
                totalSocialdpw = totalSocialQueue * singledpwR_homo
            logger.info(f'totalSocialdpw: {totalSocialdpw}')
            return totalSocialdpw
        elif (phases[i]["id"] != phaseNumber):
            continue

def dpw_total(laneInfos,phases,phaseNumber):
    totalBusdpw = dpw_bus(laneInfos,phases,phaseNumber)
    totalSocialdpw = dpw_social(laneInfos,phases,phaseNumber)
    totaldpw = FAI * totalBusdpw + totalSocialdpw
    logger.info(f'totaldpw: {totaldpw}')
    return totaldpw

