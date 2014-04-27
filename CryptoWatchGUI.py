from IPython.core.display import clear_output
import pylab

from matplotlib.ticker import FormatStrFormatter 
from matplotlib.dates import MinuteLocator, DateFormatter

import pytz

from datetime import datetime
from termcolor import colored

import Cryptsy
from CryptsyConfig import APIkey, APIsecret

import time
import sys
import os
import math

global Exchange
global orders
global watching
global coinbook
global count

Exchange = Cryptsy.Cryptsy(APIkey, APIsecret)
orders = Exchange.getOrderbookData()

coinrecord = dict()
coinbook = dict()
dates = dict()
x = dict()

count = 1
if len(sys.argv) > 1:    
    watching = sys.argv[1:]
    watching = [i.upper() for i in watching]
else:
    if not watching:
    
        watching = []
    
        for market in orders['return']:
        
            label = orders['return'][market]['label']
            watching.append(str(market))
        
for market in orders['return']:
    
    label = orders['return'][market]['label']
    coinbook[label] = dict()  
    coinrecord[label] = dict()
    dates[label] = dict()
    x[label] = dict()

def gather_data(count):
    
    orders = Exchange.getOrderbookData()
    
    for market in sorted(orders['return']):
        
        label = str(orders['return'][market]['label'])
        
        try:            
            buyorders = orders['return'][market]['buyorders'][0:3]
        except:
            buyorders = "No Buy Orders"
        
        try:
            price = str(buyorders[0]['price'])
            price = float(price)
        except:
            price = 0.00000000
            
        coinbook[label][count] = [str(label), price, datetime.now()]
        coinrecord[label] = coinbook[label]
        
    return coinrecord

def printcoins(coinrecord):
    
    for label in sorted(coinrecord.keys()):
        
        if label.split("/")[0] in watching:
            
            price = float(coinrecord[label][count][1])
            stamp = datetime.strftime(coinrecord[label][count][-1], "%b %d %Y %H:%M:%S")
            
            if len(label.split("/")[0]) < 3:
                print  "%s \t \t %.8f \t %s" % (label, price , stamp), "\n"          
            else:
                print  "%s \t %.8f \t %s" % (label, price , stamp), "\n" 
                
            if count > 1:
                old_price = float(coinrecord[label][count-1][1])
                price_diff = price - old_price
                
                if price_diff > 0:
                    print colored("\t \t %s \t+ %.8f GAIN" % (label, price_diff), "green") , "\n" 
                elif price_diff < 0:
                    print colored("\t \t %s \t- %.8f LOSS" % (label, abs(price_diff)), "red"), "\n"
                else:
                    pass
                
            else:
                pass

def plot_rates(coinrecord):
    size1 = float(len(watching))/2
    if size1 % 2 > 0:
        size1 = float((len(watching)//2))+1
    print size1
    size1 = int(size1)
    if count > 1:
        pylab.close()
    import matplotlib.gridspec as gridspec
    fig = pylab.gcf() 
    fig.canvas.set_window_title('CryptoWatchGUI')
    graphs = []
    axes = dict()
    est=pytz.timezone('US/Eastern')
    yFormatter = FormatStrFormatter('%.8f')    
    xFormatter = DateFormatter("%H:%M:%S")
    n = 0
    gs = gridspec.GridSpec(size1, 2)
    for label in sorted(coinrecord.keys()):
        
        if label.split("/")[0] in watching:
            
            for i in coinrecord[label]:
                dates[label][count] = coinrecord[label][count][-1]
                graph = (label, dates[label][i], coinrecord[label][i][-2])
                x[label][count]= graph
        
            xdates = [x[label][i][1] for i in [y for y in x[label]]]
            yrates = [x[label][i][2] for i in [y for y in x[label]]]                             

            ax = fig.add_subplot(gs[n], axisbg="#07000D") 
            
            pylab.xlabel("Time")
            pylab.ylabel(label.split("/")[1])
            
            ax.grid(True, color="w", linewidth=2)
            
            ax.xaxis_date()
            
            ax.xaxis.set_major_formatter(xFormatter)
            ax.xaxis.set_minor_locator(MinuteLocator(interval = 1))
            
            ax.yaxis.set_major_formatter(yFormatter)
                     
            ax.spines['bottom'].set_color("#FF3300")
            ax.spines['top'].set_color("#47D147")
             
            ax.spines['bottom'].set_linewidth(10)
            ax.spines['top'].set_linewidth(10)

            pylab.xticks(rotation=45)
            pylab.yticks(rotation=0)
            
            pylab.autoscale(enable=True, axis='both', tight=None)
            pylab.title(label)
            
            ax.plot_date(xdates, yrates, color='blue', linestyle='-', marker='o', markerfacecolor='orange', markersize=10, drawstyle='solid', linewidth=5)
            graphs.append(ax)
            axes[label] = ax
            n = n+1


    if count > 1:
        gs.tight_layout(fig)
        mng = pylab.get_current_fig_manager()
        mng.window.wm_geometry("+1281+0")   
        mng.resize(*mng.window.maxsize())
        fig.show()
    else:
        print "Initializing Graphs"

if __name__ == "__main__":
    while True:
        os.system("clear")
        clear_output()
        
        print "CryptoWatch v1.1"
        print "Watching:"
        print watching, "\n"
        try:
            printcoins(gather_data(count))
        except: 
            print "Error parsing data"    
        print "\t Run:", count, "\t %s" % datetime.strftime(datetime.now(), "%b %d %Y %H:%M:%S") 
        plot_rates(coinrecord)
        sys.stdout.flush()
        
        count+=1
        
        time.sleep(15)
