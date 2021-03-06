import math
import os
from params import get_params
import matplotlib.pyplot as plt 
import numpy as np
from scipy import signal, special
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker 
from matplotlib.font_manager import FontProperties
font = FontProperties(fname="/home/wcj/anaconda2/envs/pytorch/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf/simhei.ttf")
plt.rcParams['font.sans-serif']=['simhei']#设置作图中文显示


# 生成前导码 10233112133200212121230200211331033030003331112003103211232003002330310031030202

def gen_presemble():

    T = 1               #基带信号宽度，也就是频率
    nb = 100            #定义传输的比特数
    delta_T = T/200     #采样间隔
    fs = 1/delta_T      #采样频率
    fc = 10/T           #载波频率
    SNR = 0             #信噪比

    t = np.arange(0, nb*T, delta_T)
    N = len(t)

    # 产生基带信号
    data = [1 if x > 0.5 else 0 for x in np.random.randn(1, nb)[0]]  #调用随机函数产生任意在0到1的1*nb的矩阵，大于0.5显示为1，小于0.5显示为0
    data0 = []                             #创建一个1*nb/delta_T的零矩阵
    for q in range(nb):
        data0 += [data[q]]*int(1/delta_T)  #将基带信号变换成对应波形信号 每1/delta_T个0/1表示一个符号

   

    # 调制信号的产生
    data1 = []                              #创建一个1*nb/delta_T的零矩阵
    datanrz = np.array(data)*2-1            #将基带信号转换成极性码,映射;二相正交调制 *2 
   

    for q in range(nb):
        data1 += [datanrz[q]]*int(1/delta_T)#将极性码变成对应的波形信号
    

   

    idata = datanrz[0:(nb-1):2]             #串并转换，将奇偶位分开，间隔为2，i是奇位 q是偶位
    qdata = datanrz[1:nb:2]         
    ich = []                                #创建一个1*nb/delta_T/2的零矩阵，以便后面存放奇偶位数据
    qch = []         
    for i in range(int(nb/2)):
        ich += [idata[i]]*int(1/delta_T)    #奇位码元转换为对应的波形信号
        qch += [qdata[i]]*int(1/delta_T)    #偶位码元转换为对应的波形信号

    a = []     #余弦函数载波
    b = []     #正弦函数载波
    for j in range(int(N/2)):
        a.append(np.math.sqrt(2/T)*np.math.cos(2*np.math.pi*fc*t[j]))    #余弦函数载波
        b.append(np.math.sqrt(2/T)*np.math.sin(2*np.math.pi*fc*t[j]))    #正弦函数载波
    idata1 = np.array(ich)*np.array(a)          #奇数位数据与余弦函数相乘，得到一路的调制信号
    qdata1 = np.array(qch)*np.array(b)          #偶数位数据与余弦函数相乘，得到另一路的调制信号
    s = idata1 + qdata1                         #将奇偶位数据合并，s即为QPSK调制信号

    plt.figure(figsize=(14,12))
    plt.subplot(3,1,1)
    plt.plot(idata1)
    plt.title('同相支路I',fontproperties=font, fontsize=20)
    plt.axis([0,500,-3,3])
    plt.subplot(3,1,2)
    plt.plot(qdata1)
    plt.title('正交支路Q',fontproperties=font, fontsize=20)
    plt.axis([0,500,-3,3])
    plt.subplot(3,1,3)
    plt.plot(s)
    plt.title('调制信号',fontproperties=font, fontsize=20)
    plt.axis([0,500,-3,3])
    plt.show()

def detect_signal(input_signal,threshold):

    print(input_signal.shape)
    i_index=np.arange(0,input_signal.shape[0],2)
    q_index=np.arange(1,input_signal.shape[0],2)
    print(i_index.shape[0])
    print(q_index.shape[0])
    
    i_data=input_signal[i_index]
    q_data=input_signal[q_index]
     
    print("i {}".format(i_data))
    print("q {}".format(q_data))

  

    signal=i_data+1j*q_data #合成两路信号
    abs_signal=abs(signal)  #求模

   
    print(abs_signal)

    # plot_and_save_fig(abs_signal,"abs signal","plots/")
    

    new_power=[threshold if sample<threshold else sample for sample in abs_signal]

    plot_and_save_fig(new_power[0:50000],"power cut by threshold","plots/")
   

    

    total_start=[]
    total_end=[]

    start=None
    end=None
    threshold_num=0
    for i in range(1,len(new_power)-1):

        if new_power[i]>threshold:
            # 平滑点(最低点)个数有个阈值
            if not start and threshold_num>1000:
                threshold_num=0
                start=i 
                total_start.append(start)
                
        elif new_power[i]==threshold:
            if new_power[i-1]==new_power[i] and new_power[i]==new_power[i+1]:
                threshold_num+=1
                smoothness=True
                if start:
                    # 后续1000个数全为平滑值
                    for j in range(i,i+1000):
                        if j<len(new_power)-1:
                            if new_power[j-1]==new_power[j] and new_power[j]==new_power[j+1]:
                                smoothness=True
                            else:
                                smoothness=False
                                break
                    # 单个切割信号长度有个阈值
                    if i-start>10000 and smoothness:
                        start=None
                        end=i
                        total_end.append(end)
            

    print('total_start {}'.format(len(total_start)))
    print('total_end {}'.format(len(total_end)))

    



    print(total_start[0:10])
    print(total_end[0:10])

    plot_and_save_fig(new_power[total_start[0]:total_end[0]],"single signal segment","plots/")
    total_start=np.array(total_start)*2
    total_end=np.array(total_end)*2-1
    

    # plt.show()

    return total_start,total_end


    # plot_and_save_fig(abs_signal[start:end],"raw signal after select","plots/")
   
    # new_power_=[5000 if sample<5000 else sample for sample in new_power[start:end]]

    # plot_and_save_fig(new_power_,"raw signal after select by threshold cut","plots/")
  
    

    # # print(new_power_[start+12],new_power_[start+13])
    # # 4800 前导码长度
    # pulse_start,pulse_end=pulse_detection(new_power_[start+4800:end],5000)


    # print('pulse start {}'.format(len(pulse_start)))
    # print('pulse end {}'.format(len(pulse_end)))
    # pulse_start=np.array(pulse_start)
    # pulse_end=np.array(pulse_end)
    # pulse_start=pulse_start+start+4800
    # pulse_end=pulse_end+start+4800

    # for i in range(len(pulse_start)):
    #     # plot_and_save_fig(new_power_[pulse_start[i]+start+4800:pulse_end[i]+start+4800],"pluse "+str(i),"plots/")
    #     plot_and_save_fig(new_power_[pulse_start[i]:pulse_end[i]],"pluse "+str(i),"plots/")
    #     break

    
    # pulse_length=pulse_end-pulse_start


    
    # # plot_save_his_fig(pulse_length,"statistics pulse length","plots/")
    # hist=count_elements(pulse_length)
    # print(hist)


    # plt.show()


    # return start+4800,end

def count_elements(seq) -> dict:
 """Tally elements from `seq`."""
 hist = {}
 for i in seq:
    hist[i] = hist.get(i, 0) + 1
 return hist
 


def plot_save_his_fig(data,title,path):
    plt.figure()
    plt.hist(data)
    plt.title(title)
    title=title.replace(" ","_")
    fig_name=path+'/'+title+'.png'
    plt.savefig(fig_name)


def plot_and_save_fig(data,title,path):
    plt.figure()
    plt.plot(data)
    plt.title(title)
    title=title.replace(" ","_")
    fig_name=path+'/'+title+'.png'
    plt.savefig(fig_name)
    

def pulse_detection(data,threshold):
    """
    @data:
    @threshold:
    @return:two list,element resprents the index indicating the pulse start and end
    """

    start=[]
    end=[]
    up=False
    for i in range(0,len(data)-1):
        if data[i]==threshold and data[i+1]>threshold:
            print('start i {}'.format(i))
            start_up=i
            up=True
        if data[i]>threshold and data[i+1]==threshold and up:
            print('end i {}'.format(i))
            up=False
            end_down=i
            if end_down>start_up:
                start.append(start_up)
                end.append(end_down)
        if data[i]>threshold and up:
            # print('continue')
            continue
        
        
    return start,end


    



def read_train_data(opt):
    files=os.listdir(opt.train_data_path)
    for i,file in enumerate(files):
        emitter_num=file.split('-')[0]
        file_path=os.path.join(opt.train_data_path,file)
        file_data=np.memmap(file_path,dtype='int16',mode='r')
        print('file_data {}'.format(file_data.shape))


        total_start,total_end=detect_signal(file_data[0:50000],1000)
        plot_and_save_fig(file_data[total_start[0]:total_end[0]],"signal segmentation after detect","plots/")
        plt.show()
        # plt.figure() 
        # fig_name='plots/'+str(emitter_num)+'_1.png'
        # plt.plot(file_data[0:10000])
        # plt.savefig(fig_name)
        # plt.figure()
        # fig_name='plots/'+str(emitter_num)+'_2.png'
        # plt.plot(file_data[10000:20000])
        # plt.savefig(fig_name)
        # plt.figure()
        # fig_name='plots/'+str(emitter_num)+'_3.png'
        # plt.plot(file_data[20000:30000])
        # plt.savefig(fig_name)
        # plt.figure()
        # plt.plot(file_data[30000:40000])
        # plt.figure()
        # plt.plot(file_data[40000:50000])

        # plt.figure()
        # plt.plot(file_data[50000:60000])
        # plt.figure()
        # plt.plot(file_data[60000:70000])
        # plt.figure()
        # plt.plot(file_data[70000:80000])
        # plt.figure()
        # plt.plot(file_data[80000:90000])

        break
    # plt.show()
    

def read_test_data(opt):
    files=os.listdir(opt.test_data_path)
    for file in files:
        file_path=os.path.join(opt.test_data_path,file)
        file_data=np.fromfile(file_path,dtype='int16')

        plt.figure() 
        plt.plot(file_data[0:10000])
        plt.figure() 
        plt.plot(file_data[1000:2000])
        plt.figure() 
        plt.plot(file_data[2000:3000])



        print('file data {}'.format(file_data.shape))
    plt.show()

if __name__=='__main__':
    opt=get_params()
    read_train_data(opt)
    # read_test_data(opt)
    # gen_presemble()

    # data=[]
    # for i in range(10):
    #     data+=[i]*2

    # print(data)

    # a=np.array([1,-12,3])
    # print(type(a))
    # print(a.shape)
    # b=np.power(a,2)
    # print(b.shape)
    # print(b)

    # a=-14387
    # b=a**2
    # print(b)

    # a=1-1j
    # # a=a**2
    # print(abs(a))



