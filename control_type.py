import dpw_model as dpwm
import time
import globe_value as gv


def control_type(laneInfos, phases, requestPhase):
    controlType = {
        "opt_type": "7F010001",
        "device_id": gv.get_value("device_id"),
        "time_stamp": round(time.time()*1000),
        "data": {
            "intersection_id": gv.get_value("intersection_id"),
            "phase_id": None,
            "time_stamp": round(time.time()*1000),
            "strategy": None,
            "hold_interval": 0
        },
    }

    if requestPhase is None:
        return controlType
    currentPhases = dpwm.currentPhaseState(phases)
    for phase in currentPhases:
        if phase["id"] == requestPhase:
            controlType["data"]["strategy"] = "相位保持"
            controlType["data"]["phase_id"] = phase["id"]
            hold_interval = dpwm.delta_g(laneInfos, phases, requestPhase)
            controlType["data"]["hold_interval"] = hold_interval
            return controlType
    for (index, phase) in enumerate(phases):
        if phase["id"] == requestPhase:
            if 1 <= index:
                if phases[index - 1]["phaseStates"][1]["timing"]["counting"]["startTime"] == 0:
                    controlType["data"]["strategy"] = "相位切换"
                    controlType["data"]["phase_id"] = phase["id"]
                else:
                    controlType["data"]["strategy"] = "相位跳跃"
                    controlType["data"]["phase_id"] = phase["id"]
            elif index == 0:
                if phases[-1]["phaseStates"][1]["timing"]["counting"]["startTime"] == 0:
                    controlType["data"]["strategy"] = "相位切换"
                    controlType["data"]["phase_id"] = phase["id"]
                else:
                    controlType["data"]["strategy"] = "相位跳跃"
                    controlType["data"]["phase_id"] = phase["id"]
            return controlType
