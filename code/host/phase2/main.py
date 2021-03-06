import globalvar
import time, threading
import host
import graph
import datahandler
import servogene
import sys
import monitor
from multiprocessing import Process, Manager
import os
import numpy as numpy
import matplotlib.pyplot as plt

comb = []
for i in range(80,145,5):
	for j in range(80,145,5):
		comb.append([i,j])

best = [0 for i in range(169)]


def P2(fo,strategy_q,buffer_q):
	global best
	ns = [ 4, 10, 135,140, 90, 90]
	time.sleep(4)
	step = -5

	strategy_q.put(ns)
	while True:
		
		print "strategy generated ", ns
		while buffer_q.empty():
			time.sleep(0.01)
		while not buffer_q.empty():
			b = buffer_q.get()
		if b!=[]:
			if abs(b[8][-1])>0.001:
				max_index = numpy.argmax(b[2])
				min_index = numpy.argmin(b[2])

				if max_index < min_index:
					print "postive, continue",step
				else:
					step = - step
					print "negative, reverse", step
				ns[3] += step
				ns[2] += step
			else:
				step =- step
				ns[3] += step
				ns[2] += step

			# if abs(b[8][-1])>0.002:
			# 	if b[8][-1] < 0:
			# 		step = -step

			# # print "**************"
			# # print b[-1]
			# # if b[-1]>0:
			# # 	print "postive, continue", step
			# # else:
			# # 	print "negative, previous", step, "reverse"
			# # 	step = -step
			# 	ns[3] += step
			# 	ns[2] += step
			# else:
			# 	step =- step
			# 	ns[3] += step
			# 	ns[2] += step

			if ns[2] >155 or ns[2] < 75:
				ns[2],ns[3]=135,135 
			fo.write(str(b[2])+'\n')

		time.sleep(0.4)
		strategy_q.put(ns)


# def P2(fo,strategy_q,buffer_q):
# 	ns = [ 4, 7, 135,140, 90, 90,0.8,90,90,90,90]
# 	while True:
# 		strategy_q.put(ns)
# 		time.sleep(2)

# def P2(fo,strategy_q,buffer_q):
# 	ns = [ 4, 7, 135,140, 90, 90,0.8,135,140,90,90]
# 	time.sleep(2)
# 	strategy_q.put(ns)

# 	while True:
# 		for k in range(len(comb)):
# 			while buffer_q.empty():
# 				time.sleep(0.01)
# 			while not buffer_q.empty():
# 				b = buffer_q.get()
# 			if b!=[]:
# 				ns[2]=comb[k][0]
# 				ns[3]=comb[k][1]
# 				strategy_q.put(ns)
# 				best[(k+168)%169]=max(best[(k+168)%169],b[8][-1])
# 			time.sleep(1)
# 			print best

def P1(fo,strategy_q,buffer_q):
	# t4 = threading.Thread(target=graph.run, name='graph')
	# t4.daemon = True
	# t4.start()
	# time.sleep(5)

	# plt initilization
	#plt.figure()
	f, axarr = plt.subplots(3, sharex=True)
	li = [axarr[i].plot([],[],'r',[],[],'b',[],[],'g') for i in xrange(3)]
	li.append(axarr)
	plt.setp(li[2][0],label="X-axis")
	plt.setp(li[2][1],label="Y-axis")
	plt.setp(li[2][2],label="Z-axis")
	axarr[0].set_title("Acceleration")
	axarr[1].set_title("Velocity")
	axarr[2].set_title("Displacement")
	box = axarr[2].get_position()
	axarr[2].set_position([box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8])
	axarr[2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), fancybox=True,ncol=3)

	# li = plt.plot([],[],'r',[],[],'b')
	plt.ion()
	plt.show(block=False)
	t1 = threading.Thread(target=host.serv, name='server')
	t1.daemon = True
	t1.start()
	t2 = threading.Thread(target=datahandler.handler, name='datahandler',args=(buffer_q,plt,li,))
	t2.daemon = True
	t2.start()
	print "datahandler start"
	t3 = threading.Thread(target=servogene.servo_gene, name='servo_generation',args=(strategy_q,))
	t3.daemon = True
	t3.start()
	print "servo_generation start"
	t5 = threading.Thread(target=monitor.monitor, name='monitor')
	t5.daemon = True
	t5.start()
	print "monitor start"
	# t6 = threading.Thread(target=ml, name='ml',args=(fo,))
	# t6.daemon = True
	# t6.start()
	graph.run()
	sys.exit()

if __name__=='__main__':
	manager = Manager()
	strategy_q = manager.Queue()
	buffer_q = manager.Queue()

	fo = open('stand.txt', 'w+')

	p1 = Process(target=P1, args=(fo,strategy_q,buffer_q,))
	p1.start()
	p2 = Process(target=P2, args=(fo,strategy_q,buffer_q,))
	p2.start()
	p1.join()
	p2.terminate()
	fo.write(str(best))
	fo.close()
