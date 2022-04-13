import copy


def psases_id_trans(trans_rule, spatmsg):
    """
    转换spat中的 pasae_id 为标准psase_id
    :param trans_rule: 转换规则
    :param spatmsg: spat消息
    :return: 转换后的spat消息
    """
    if spatmsg is None:
        return None

    spat_trans = copy.deepcopy(spatmsg)
    rule_values = list(trans_rule.values())
    spat_psases = spatmsg["data"]["intersections"][0]["phases"]

    for (index, spat_phase) in enumerate(spat_psases):
        for values in rule_values:
            if values.count(spat_phase["id"]) != 0:
                id_trans = list(trans_rule.keys())[(rule_values.index(values))]
                # print("psase_id_trans: {}--->{}".format(spat_phase["id"], id_trans))
                spat_trans["data"]["intersections"][0]["phases"][index]["id"] = int(id_trans)

    return spat_trans


def filter_duplicate(o_list):
    """
    去除列表中重复值
    :param o_list: list
    :return: list
    """
    new_list = []
    for i in o_list:
        if i not in new_list:
            new_list.append(i)
    return new_list
