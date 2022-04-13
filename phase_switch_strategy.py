import dpw_model as dpwm
from logconfig import logger


def dpw_for_decision(laneInfos, phases):
    '''
    :func:function of calculating the total dpw value of each phase
    :param laneInfos: list,车道状态信息
    :param phases: list,相位状态信息
    :return: dpw_all_decision:list,所有相位的总dpw值
    '''

    dpw_all_decision = []
    if len(laneInfos) < len(phases):
        for phase in phases:
            dpw_all_decision.append({"id": phase["id"], "tdpw": 0})
        logger.info(dpw_all_decision)
        return dpw_all_decision

    for (index, phase) in enumerate(phases):
        phaseNumber2Totaldpw = phase["id"]
        dpw_each_phase = dpwm.dpw_total(laneInfos, phases, phaseNumber2Totaldpw)
        logger.info(f'dpw_each_phase: {dpw_each_phase}')
        try:
            if laneInfos[index]["queue_length"] == 0:
                dpw_all_decision.append(
                    {"id": phaseNumber2Totaldpw, "tdpw": dpw_each_phase})
            else:
                if phase["phaseStates"][1]["timing"]["counting"]["startTime"] == 0:
                    dpw_all_decision.append(
                        {"id": phaseNumber2Totaldpw, "tdpw": dpw_each_phase})
                else:
                    dpw_all_decision.append({"id": phaseNumber2Totaldpw, "tdpw": 0})
        except KeyError:
            logger.error('KeyError')
            continue  # 解决空数据的lane报错
    logger.info(dpw_all_decision)
    return dpw_all_decision


def output_request_phase(dpw_all_decision):
    dpwvalues = []
    for item in dpw_all_decision:
        dpwvalues.append(item["tdpw"])
    try:
        max(dpwvalues)
    except ValueError:
        requestPhase = None
        logger.info(f'requestPhase: {requestPhase}')
        return requestPhase
    else:
        if max(dpwvalues) == 0:
            requestPhase = None
            logger.info(f'requestPhase: {requestPhase}')
            return requestPhase
        else:
            requestPhase = dpw_all_decision[dpwvalues.index(max(dpwvalues))]["id"]
            logger.info(f'requestPhase: {requestPhase}')
            return requestPhase
