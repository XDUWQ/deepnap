# coding: utf-8

###################################
# Index log files for phiNN agents
# Author: Jingchu Liu
# Date: Feb 2017
###################################

from sys import argv
import os
import regex as re
import pandas as pd
from multiprocessing import Pool

re_epoch_msg = re.compile(
    # epoch: uint
    # time stamp: YYYY-MM-DD HH:MM:SS
    'Epoch (?P<epoch>\d+), (?P<start_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (?P<end_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\n'
    # last reward: float or None
    'Emulation.step\(\): last reward: ((?P<last_reward>[-]*[\d\.]+)|(None))\n'
    # Sessions: uint
    '    TrafficEmulator.generate_traffic\(\): located (?P<session_in>\d+), droped (?P<session_out>\d+), left (?P<session_net>\d+) sessions.\n'
    # Requests: uint
    '        TrafficEmulator.generate_requests_\(\): generated (?P<req_generated>\d+) requests.\n'
    # Observation (uint, uint, uint)
    'Emulation.step\(\): observation: \((?P<ob_last_q>\d+), (?P<ob_last_t>\d+), (?P<ob_new_q>\d+)\)\n'
    # agent update msg: 4 strings or loss (float or string) + rs (float or string)
    '((    QAgentNN.reinforce_\(\): (?P<agent_update_msg>'
            '(last_state is None.)|'
            '(last_reward is None.)|'
            '(state is None.)|'
            '(unfull memory.)'
    ')\n)|('
    '(    QAgentNN.reinforce_\(\): update counter (?P<counter_update>\d+), freeze counter (?P<counter_freeze>\d+), rs counter (?P<counter_rs>\d+).\n)'
    '('
        '(    QAgentNN.reinforce_\(\): update loss is (?P<loss>[a-zA-Z\d\.-]+), reward_scaling is (?P<reward_scaling>[a-zA-Z\d\.-]+)\n)'
    # mini-batch distribution: wake and sleep (float or string)
        '(?:'
            '(?:        QAgentNN.reinforce_\(\): batch action distribution: (?P<batch_dist>\{'
                            '\(False, \'serve_all\'\): (?P<batch_dist_wake>[\w\.-]+), '
                            '\(True, None\): (?P<batch_dist_sleep>[\w\.-]+)'
            '\})\n)|'
            '(?:        QAgentNN.reinforce_\(\): batch action distribution: (?P<batch_dist>\{'
                            '\(True, None\): (?P<batch_dist_sleep>[\w\.-]+), '
                            '\(False, \'serve_all\'\): (?P<batch_dist_wake>[\w\.-]+)'

            '\})\n)|'
            '(?:        QAgentNN.reinforce_\(\): batch action distribution: (?P<batch_dist>\{'
                            '\(True, None\): (?P<batch_dist_sleep>[\w\.-]+)'

            '\})\n)|'
                '(?:        QAgentNN.reinforce_\(\): batch action distribution: (?P<batch_dist>\{'
                            '\(False, \'serve_all\'\): (?P<batch_dist_wake>[\w\.-]+)'

            '\})\n)'
        ')'
    ')?'
    '))'

    # action msg: random or policy
    #   q_values if epsilon greedy
    # policy msg
    '    QAgent.act_\(\): '
        '(?P<agent_act_msg>('
            '(?:randomly choose action)|'
            '(?:choose best q among '
                '(?P<q_vals>\{\(False, \'serve_all\'\): (?P<q_wake>[\w\.-]+), \(True, None\): (?P<q_sleep>[\w\.-]+)\}))|'
            '(?:choose best q among '
                '(?P<q_vals>\{\(True, None\): (?P<q_sleep>[\w\.-]+), \(False, \'serve_all\'\): (?P<q_wake>[\w\.-]+)\}))|'
        ')'
        ' \((?P<agent_act_basis>[a-zA-Z ]+)\)'
        ').\n'
    # agent action: (True, None) or (False, 'serve_all')
    # agent update: [ignore]
    'Emulation.step\(\): control: (?P<agent_action>\([a-zA-Z,_ \']+\)), agent update: [a-zA-Z\d\.-]+\n'
    # Service: 
    #   req: served, queued, rejected (retried+canceled), unattended [uint]
    #   reward: service, wait, fail [int]
    #   buffer: pending, waiting, served, failed
    '        TrafficEmulator.evaluate_service_\(\): '
                'served (?P<req_served>\d+), queued (?P<req_queued>\d+), '
                'rejected (?P<req_rejected>\d+) \((?P<req_retried>\d+), (?P<req_canceled>\d+)\), unattended (?P<req_unattended>\d+), '
                'reward ([-]?[\d\.]+) \((?P<tr_reward_serve>[-]?[\d\.]+), (?P<tr_reward_wait>[-]?[\d\.]+), (?P<tr_reward_fail>[-]?[\d\.]+)\)\n'
    '        TrafficEmulator.evaluate_service_\(\): '
                'pending (?P<req_pending_all>\d+), waiting (?P<req_waiting_all>\d+), '
                'served (?P<req_served_all>\d+), failed (?P<req_failed_all>\d+)\n'
    # # operation cost: float
    # # traffic reward: float
    'Emulation.step\(\): cost: (?P<op_cost>[-]*[\d\.]+), reward: (?P<tr_reward>[-]*[\d\.]+)'
    # # last line
    '\n{0,1}'
)


if len(argv)>2:
    log_file = argv[1]
    print "    Processing {}".format(log_file)
    
    def index_file(file):
        index_fname = "./log/index_"+file+".csv"
        if os.path.isfile(index_fname):
            print '    file {} already exist!'.format(index_fname)
        else:
            with open('./log/'+file, "r") as f_log:
                all_log = "".join(f_log.readlines()).split('\n\n')
                extract = [re_epoch_msg.search(piece) for piece in all_log]
                df = pd.DataFrame.from_dict([piece.groupdict() for piece in extract if piece is not None])
                df.set_index('epoch')
                df.index.name = 'epoch'
            with open(index_fname, "w") as f_ind:
                df.to_csv(f_ind, sep=';', index=True, header=True)
            print "        ",
            print (file, df.shape)
        return
    
    index_file(log_file)
else:
    print "Please specify the name of log file."




