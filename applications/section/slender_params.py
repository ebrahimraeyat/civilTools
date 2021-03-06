slenderParameters = {'notPlate': {'B': {'M': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                              'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                                        'H': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('2*0.55*tf/.6', ''), 'D': 'd',
                                              'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}},
                                  'C': {'M': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                              'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                                        'H': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                              'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}}},
                     'TBPlate': {'B': {'M': {'BF': 'c+2*xm', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                                             'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                             'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                                       'H': {'BF': 'c+2*xm', 'tfCriteria': 't1<(.6*B1*tf)/(0.55*bf)',
                                             'TF': ('(0.55*BF*t1)/(.60*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                             'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}},
                                 'C': {'M': {'BF': 'c+2*xm', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                                             'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                             'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                                       'H': {'BF': 'c+2*xm', 'tfCriteria': 't1<(B1*tf)/(bf)',
                                             'TF': ('(BF*t1)/(B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                             'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}}},
                     'TBLRPLATE': {'B': {'M': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                                               'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                               'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                                         'H': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(.6*B1*tf)/(0.55*bf)',
                                               'TF': ('(0.55*BF*t1)/(.60*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                               'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}},
                                   'C': {'M': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                                               'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                               'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                                         'H': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(B1*tf)/(bf)',
                                               'TF': ('(BF*t1)/(B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                               'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}}},
                     'LRPLATE': {'B': {'M': {'BF': 'c+2*xm+2*t2',
                                             'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd', 'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}, 'H': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 'True', 'TF': ('2*0.55*tf/.6', ''), 'D': 'd',
                                                                                                                                                                                                         'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}},
                                 'C': {'M': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                             'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                                       'H': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                             'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}}}}
