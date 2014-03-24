import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import csv
import sys
import matplotlib.pyplot as plt

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def findCorrelation(attribute,changes):
	return np.corrcoef(attribute,changes,rowvar=0)[0,1]


def writeToFile(fname,orderkeys,corr):
	with open(fname,'wb') as csvfile:
		w=csv.writer(csvfile,delimiter=',')
		for i in range(len(orderkeys)):
			w.writerow((orderkeys[i],corr[i]))

def plotGraph(orderkeys,corr,year):
	feature_list=np.arange(0,len(orderkeys))
	plt.plot(feature_list,corr)
	plt.xlabel('Features')
	plt.ylabel('Correlations')
	plt.title(year)
	name=str(year)+'corr.png'
	plt.savefig(name)
	plt.show()

def getPercentageChange(sp500list,year):
	dt_start = dt.datetime(year, 1, 1)
	dt_end = dt.datetime(year, 12, 31)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
	dataobj = da.DataAccess('Yahoo')
    	ls_symbols = dataobj.get_symbols_from_list(sp500list)
	ls_keys = ['close']
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)
    
	na_price = d_data['close'].values
	percentchange=na_price[len(na_price)-1,:]/na_price[0,:]-1 #Percentage change 
	i=0
	pchange=dict()
	for sym in ls_symbols:
		pchange[sym]=percentchange[i]
		i=i+1

	return pchange

def getFeaturesFinalData(fname):
	reader=csv.reader(open(fname,"rb"))
	i=0
	data=[]
	ks=[]
	for row in reader:
		if i==0:
			ks.append(row)
		else:
			data.append(row)
		i=i+1

	fkeys=dict()
	keys=ks[0]
	symbols=[]
	
	for j in range(0,len(data)):
		for i in range(0,len(keys)):
			if i>=0 and i<=8:
				continue
			elif i==9:
				symbols.append(data[j][i])
				fkeys[symbols[j]]=[]
			elif i>=10 and i<=13:
				continue
			else:
				if is_number(data[j][i]):
					fkeys[symbols[j]].append(keys[i])
		print len(fkeys[symbols[j]])			

	finalfeatures=set(fkeys[fkeys.keys()[0]])
	for key in fkeys.keys():
		finalfeatures=set.intersection(set(fkeys[key]),finalfeatures)
	
	finaldata=[]
	
	for j in range(0,len(data)):
		dts=[]
		for i in range(0,len(keys)):
			if keys[i] in finalfeatures:
				dts.append(data[j][i])
			if keys[i]=='tic':
				dts.append(symbols[j])
		finaldata.append(dts)
	return keys,finaldata,finalfeatures    #keys-contain all the fundamental factors,finaldata-data of all the stocks with only relevant available fundamental factor data,finalfeatures-only features which are present for all stocks
	

if __name__ == '__main__':

	sp500list='sp5002012'
	pchange=getPercentageChange(sp500list,2012)
	
	keys,finaldata,finalfeatures=getFeaturesFinalData("Dec2012.csv")
	
	orderkeys=[]
	for i in range(0,len(keys)):
		if keys[i] in finalfeatures:
			orderkeys.append(keys[i])
	
	for l in range(len(finaldata)):
		if finaldata[l][0] in pchange.keys():
			finaldata[l].append(pchange[finaldata[l][0]])

	
	changes=[float(l[-1]) for l in finaldata]                 #Get correlations
	changes=np.array(changes)
	changes=np.reshape(changes,(len(changes),1))
	corr=np.zeros((len(finaldata[0])-2,1))
	for p in range(1,len(finaldata[0])-1):
		attribute=[float(l[p]) for l in finaldata]
		attribute=np.array(attribute)
		attribute=np.reshape(attribute,(len(attribute),1))
		corr[p-1,0]=findCorrelation(attribute,changes)

	writeToFile('correlations_2012.csv',orderkeys,corr)
	plotGraph(orderkeys,corr,year)
	
