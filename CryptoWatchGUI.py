import pylab
from matplotlib.ticker import FormatStrFormatter 
from matplotlib.dates import MinuteLocator, DateFormatter
import matplotlib.gridspec as gridspec
from datetime import datetime
from termcolor import colored
import Cryptsy
from CryptsyConfig import APIkey, APIsecret
import time
import sys
import os
global Exchange
global watching
global coinbook
global count
Exchange = Cryptsy.Cryptsy(APIkey, APIsecret)   
orders = Exchange.getOrderbookData()                                #variable to store entire orderbook
coinrecord = dict()                                                 #dictionary to store all iterations of all coinpairs
coinbook = dict()                                                   #dictionary to store current iteration of all coinpairs
dates = dict()                                                      #Dictionary to store timestamps for x axis of graphs
x = dict()                                                          #Dictionary to store graph plotting data
count = 1                                                           #set iteration counter to 1
if len(sys.argv) > 1:                                               #if coinpairs of interest via command line arguments
    watching = sys.argv[1:]                                         #variable to store coinpairs of interest via command line arguments
    watching = [i.upper() for i in watching]
else:
    watching = []
    for market in orders['return']:                                 #if no command line arguments, watch all markets
        label = orders['return'][market]['label']
        watching.append(str(market))
for market in orders['return']:
    label = orders['return'][market]['label']                       #coinpair labels
    coinbook[label] = dict()                                        #Dictionary for each coin on each individual iteration
    coinrecord[label] = dict()                                      #dictionary of ALL coinpairs on ALL iterations
    dates[label] = dict()                                           #dates for each coinpair
    x[label] = dict()                                               #graphs for each coinpair

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
        coinbook[label][count] = [str(label), price, datetime.now()]    #store label, price, timestamp for iteration
        coinrecord[label] = coinbook[label]                             #store coinbook for each iteration
    return coinrecord

def printcoins(coinrecord):
    for label in sorted(coinrecord.keys()):
        if label.split("/")[0] in watching:# or label.split("/")[1] in watching:            # if coin in list of coins of interest
            price = float(coinrecord[label][count][1])                                      #current iteration price
            stamp = datetime.strftime(coinrecord[label][count][-1], "%b %d %Y %H:%M:%S")    #timestamp 
            if len(label.split("/")[0]) < 3:
                print  "%s \t \t %.8f \t %s" % (label, price , stamp), "\n"          
            else:
                print  "%s \t %.8f \t %s" % (label, price , stamp), "\n"              
            if count > 1:
                old_price = float(coinrecord[label][count-1][1])    #last iteration's price info
                price_diff = price - old_price                      #gain of loss amount
                if price_diff > 0:                                  # if price increased
                    print colored("\t \t %s \t+ %.8f GAIN" % (label, price_diff), "green") , "\n" 
                elif price_diff < 0:                                # if price decreased
                    print colored("\t \t %s \t- %.8f LOSS" % (label, abs(price_diff)), "red"), "\n"
                else:
                    pass                                            #if price stayed same
            else:
                pass

def plot_rates(coinrecord):                                         #Function to plot coinpair rate / timestamp 
    size1 = float(len(watching))/2                                  #gridsize is dynamic based on coins of interest
    if size1 % 2 > 0:                                               #if non even number, 
        size1 = float((len(watching)//2))+1                             #add one
    size1 = int(size1)                                              #gridsize from float to int
    if count > 1:
        pylab.close()                                               #close figure from last iteration
    fig = pylab.gcf()                                               #create matplotlib figure
    fig.canvas.set_window_title('CryptoWatchGUI')                   #Set title of matplotlib figure window
    yFormatter = FormatStrFormatter('%.8f')                         #format y axis labels
    xFormatter = DateFormatter("%H:%M:%S")                          #format x axis labels
    n = 0                                                           #zero out Grid placement spaces from last iteration
    gs = gridspec.GridSpec(2, size1)
    for label in sorted(coinrecord.keys()):
        if label.split("/")[0] in watching:# or label.split("/")[1] in watching:# if coinpair in coins of interest            
            for i in coinrecord[label]:
                dates[label][count] = coinrecord[label][count][-1]          #convert dates into list for graphing
                graph = (label, dates[label][i], coinrecord[label][i][-2])  #Place label, dates, and prices for each iteration into list
                x[label][count]= graph                                      #store all iterations for plotting into dictionary
        
            xdates = [x[label][i][1] for i in [y for y in x[label]]]        #convert timestamps for coinpair into list for plotting
            yrates = [x[label][i][2] for i in [y for y in x[label]]]        #Convert prices for coinpair into list for plotting

            ax = fig.add_subplot(gs[n], axisbg="#07000D")                   #create subplot and place into next grid space of figure
            ax.grid(True, color="grey", linewidth=1)                        #grid in background of graph
            ax.xaxis_date()                                                 #x axis as dates, datetime objects
            ax.xaxis.set_major_formatter(xFormatter)                        #format x axis with string of hours, minutes, seconds
            ax.xaxis.set_minor_locator(MinuteLocator(interval = 5))         # set ticks in minutes
            ax.yaxis.set_major_formatter(yFormatter)                        #format y axis with %.8f format string
            ax.spines['bottom'].set_color("#FF3300")                        #add red bar on bottom of graph
            ax.spines['top'].set_color("#47D147")                           #add green bar on top of graph
            ax.spines['bottom'].set_linewidth(6)                            #set size of bottom bar/border
            ax.spines['top'].set_linewidth(6)                               #set size of top bar/border
            pylab.xlabel("Time")                                            #label x axis
            pylab.ylabel(label.split("/")[1])                               #label y axis
            pylab.xticks(rotation=90)                                       #rotate x ticks by 90 degrees
            pylab.yticks(rotation=0)
            pylab.autoscale(enable=True, axis='both', tight=None)           #autoscale both axis of graph
            pylab.title(label)                                              #title graph with coinpair                       
            ax.plot_date(xdates, yrates, color='green', linestyle='-', marker='o', markerfacecolor='white', markersize=5, drawstyle='solid', linewidth=3)   #plot graph to prepare for placement into grid on figure
            n = n+1                                                         #update grid space for next graph placement
    if count > 1:
        gs.tight_layout(fig, pad=0.4, w_pad=0.5, h_pad=1.0)                 #layout graphs into grid
        mng = pylab.get_current_fig_manager()                               #get figure to process
        mng.window.wm_geometry("+1281+0")                                   # place figure/canvas on second monitor
        mng.resize(*mng.window.maxsize())                                   #maximize figure
        fig.show()                                                          #show figure of all graphs
    else:
        print "Initializing Graphs"

if __name__ == "__main__":
    while True:                                                             #Mainloop of program
        os.system("clear")                                                  #clear terminal window (os.system('cls') for windows 
        print "CryptoWatch v1.1"
        print "Watching:"
        print watching, "\n"
        try:
            printcoins(gather_data(count))                                  #gather data via API and print rates/differences in terminal
        except: 
            print "Error parsing data"    
        print "\t Run:", count, "\t %s" % datetime.strftime(datetime.now(), "%b %d %Y %H:%M:%S") 
        plot_rates(coinrecord)                                              #plot data onto graphs
        sys.stdout.flush()                               #force stdout to terminal incase buffered (mostly for ipython notebook format)
        count+=1                                        #increase the current count for next iteration        
        time.sleep(15)                                  #wait 15 seconds before next iteration
