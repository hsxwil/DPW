import _thread
import time
import copy, json
import phase_switch_strategy as phasess
from mq_client import MQC, MQP
import control_type as ct
import globe_value as gv
from phase_trans import psases_id_trans, filter_duplicate
from mq_config import mq_exchange
from logconfig import logger


def getMQMsg(mqc, msgPre):
    msgCur = mqc.getMQ()
    if msgCur == None:
        return msgPre
    msgPre = copy.deepcopy(msgCur)
    return msgPre


def provideMQmsg(mqp, mqbody):
    msgPre = None
    msgCur = mqp.provideMQ(mqbody)
    if msgPre == msgCur:
        msgCur = None
    msgPre = copy.deepcopy(msgCur)
    return msgPre


def main():
    logger.info("this message is from main function")
    mqcSPAT = MQC("mqcSPAT")
    mqcSPAT.queue_bind(mq_exchange, "TOPIC.10001002.*")

    mqcMMW = MQC("mqcMMW")
    mqcMMW.queue_bind(mq_exchange, "TOPIC.20000005.*")

    strategy = MQP("strategy_provider")

    try:
        threadSPAT = _thread.start_new_thread(mqcSPAT.consuming, ())
        logger.debug(f"threadSPAT: {threadSPAT}")
        SPATmsgPre = getMQMsg(mqcSPAT, None)
        time.sleep(1)

        threadMMW = _thread.start_new_thread(mqcMMW.consuming, ())
        logger.debug(f"threadMMW: {threadMMW}")
        MMWmsgPre = getMQMsg(mqcMMW, None)
        time.sleep(1)
    except Exception as e:
        logger.error(e)

    while True:
        time.sleep(3)
        logger.debug(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} {round(time.time() * 1000)} {"=" * 30}')
        try:
            if gv.get_value("trans") == "true":  # 判断是否转换相位ID
                trans_rule = gv.get_value("trans_rule")
                SPATmsgcur = getMQMsg(mqcSPAT, SPATmsgPre)
                SPATmsg = psases_id_trans(trans_rule, SPATmsgcur)  # 转换相位ID的SPATmsg
            else:
                SPATmsg = getMQMsg(mqcSPAT, SPATmsgPre)  # 不转换直接取MQ中的SPATmsg
            logger.debug(f"SPATmsg: {SPATmsg}")
            # time.sleep(0.1)

            MMWmsg = getMQMsg(mqcMMW, MMWmsgPre)
            logger.debug(f"MMWmsg: {MMWmsg}")
            # time.sleep(0.1)

            if SPATmsg is None or MMWmsg is None or list(MMWmsg["data"].keys())[0] != "lane_info":
                continue

            phases = SPATmsg["data"]["intersections"][0]["phases"]
            phases = filter_duplicate(phases)  # 去除重复项
            logger.info(f"SPATphases: {phases}")

            laneInfos = MMWmsg["data"]["lane_info"]
            logger.info(f'laneInfos: {laneInfos}')

            dpwforDecision = phasess.dpw_for_decision(laneInfos, phases)
            REQUEST_PHASE = phasess.output_request_phase(dpwforDecision)
            logger.info(REQUEST_PHASE)

            controlStrategy = json.dumps(ct.control_type(laneInfos, phases, REQUEST_PHASE), ensure_ascii=False)
            Smsg = provideMQmsg(strategy, controlStrategy)
            logger.info(f"Strategy: {Smsg}")
        except Exception as e:
            logger.error(f"Error main: {e}")
            continue


if __name__ == "__main__":
    main()
