代码简介：
dpw算法代码用于路口MEC自适应信号控制。
基于SPAT数据和毫米波雷达数据，输出自适应信号控制策略。

数据相关事项：
1. 毫米波雷达数据中车道编号和信号机相位对应车道编号一致
2. 毫米波雷达数据中 laneInfo["bus_through_put_flow"]  和  laneInfo["headway"]必须有数据，否则计算的dpw结果就是
“dpw_each_phase 0.0”

代码组成：
(1)_main.py主函数文件
代码运行其实函数，执行可输出信号控制策略
	MQ队列名：
		mqcSPAT = MQC('mqcSPAT')   #‘mqcSPAT’为SPAT消息集队列名，MQ需根据该名字创建消息队列提供消息
		mqcMMW = MQC('mqcMMW')     #‘mqcMMW’为毫米波雷达消息队列名，MQ需根据该名字创建消息队列提供消息
		strategy = MQP('strategy_provider')  ##‘strategy_provider’为策略消息输出队列名，MQ需创建该名字消息队列获取消息

(2)controller_config.conf
算法全局变量：
	(a)fai #公交载客率，衡量优先权车辆优先权重，空载时fai=1
	(b)phaseConf = 1,2,3,4,5,6,7,8   路口信号机相位配置，根据路口信号机实际信号配时方案配置

相位转换：phase_trans
	1. 将 trans = true 表示开启相位转换，将SPAT消息中的相位ID转换为标准相位ID
	2. 配置转换规则 ：标准相位ID = SPAT消息中的相位ID
	举例：
	1 = 0,2,3,16,18,19,32,34,35,48,50,51
	2 = 8,10,11,24,26,27,40,42,43,56,58,59
	3 = 1,17,33,49
	4 = 9,25,41,57

相位属性信息配置文件，当所有代码文件部署于路口MEC时，需根据每个路口实际情况修改该配置文件
举例说明：
	[2]  #表示相位编号
	lane_id = 11,12   #表示该相位对应车道编号
	gMax_P2 = 45      #表示该相位最大绿灯时长
	gMin_P2 = 10      #表示该相位最小绿灯时长，即绿灯保护时长
	red_P2 = 85       #表示该相位红灯时长
	yellow_P2 = 0     #表示该相位黄灯时长
其它类似

(3)mq_consumer.py
MQ队列消息获取文件。
	需配置：
        auth = pika.PlainCredentials('huali', 'huali')   #账户名、密码
        connection = pika.BlockingConnection(pika.ConnectionParameters('172.16.1.171', 5672, '/mec', auth))   #IP地址、端口、虚拟主机名

(4)mq_provider.py
MQ队列消息输出文件。
	需配置：
		user_pwd = pika.PlainCredentials('huali', 'huali') #用户名 密码
        connectparam = pika.ConnectionParameters('172.16.1.171',5672,'/mec',credentials=user_pwd)#IP,端口、虚拟主机名

(5)其它文件：算法实现核心代码