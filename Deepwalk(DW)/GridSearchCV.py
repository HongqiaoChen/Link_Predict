import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import word2vec
import numpy as np
import random

path = '/home/hongqiaochen/Desktop/Date_Link_predict/USAir'

def Start(list_v):
    choice = List[list_v[0]]
    r = random.randint(0,len(choice)-1)
    list_v[1] = choice[r]

def DFS(list_v,k,flag):
    choice = List[list_v[k-1]]
    if choice == None:
        flag += 1
        list_v[k] = list_v[k-1]
    else:
        r = random.randint(0,len(choice)-1)
        list_v[k] = choice[r]

def BFS(list_v,k,flag):
    choice = List[list_v[k-2]]
    if choice == None:
        flag += 1
        list_v[k] = list_v[k - 1]
    else:
        r = random.randint(0,len(choice)-1)
        list_v[k] = choice[r]

def get_sample(Test, Not):
    l_test = len(Test)
    l_Not = len(Not)
    MAX = 672400
    Test_sample = np.random.choice(l_test, size=MAX, replace=True)
    Not_sample = np.random.choice(l_Not, size=MAX, replace=True)
    return Test_sample, Not_sample

def DW_Similarity(V1,V2):
    temp = np.sqrt(np.sum(np.square(V1 - V2)))
    S = float(1/(1+temp))
    return S

def Randwalk(p,times,length,window,min_count,alpha):
    MAX = 672400
    flag = 0
    walkpath = [[]for i in range(len(List)*times)]
    for m in range(times):
        for i in range(len(List)):
            list_v = [0 for i in range(length)]
            list_v[0]= i
            Start(list_v)
            for k in range(2,length):
                if flag == 0 :
                    a = random.random()
                    if a > p :
                        DFS(list_v,k,flag)
                    else:
                        BFS(list_v,k,flag)
                else:
                    list_v[k] = list_v[k-1]
            walkpath[i+m*len(List)] = list_v
    walkpath = np.array(walkpath)
    np.savetxt(path+'walkpath.txt', walkpath,fmt='%d',delimiter=' ')
    walkpath = word2vec.Text8Corpus(path+'/walkpath.txt')
    model = word2vec.Word2Vec(walkpath,size = 64,hs = 1,min_count = min_count,window = window,sg=1,alpha=alpha)
    model.wv.save_word2vec_format(path+'DW_vector.txt')
    V = np.loadtxt(path+'DW_vector.txt', dtype=float,skiprows=1)
    V = V[np.lexsort(V[:, ::-1].T)]
    V = np.delete(V, 0, axis=1)
    Test_sample, Not_sample = get_sample(Test, Not)
    S_Test_Sample = [0 for i in range(MAX)]
    S_Not_Sample = [0 for i in range(MAX)]
    for i in range(MAX):
        S_Test_Sample[i] = DW_Similarity(V[Test[Test_sample[i]][0]], V[Test[Test_sample[i]][1]])
    for j in range(MAX):
        S_Not_Sample[j] = DW_Similarity(V[Not[Not_sample[j]][0]], V[Not[Not_sample[j]][1]])
    n = MAX
    n1 = 0
    n2 = 0
    for i in range(MAX):
        if S_Test_Sample[i] > S_Not_Sample[i]:
            n1 += 1
        if S_Test_Sample[i] == S_Not_Sample[i]:
            n2 += 1
    auc = (n1+0.5*n2)/n
    return auc


# 读取Test,E,Train集合
Test = np.loadtxt('/home/hongqiaochen/Desktop/Link_predict/Power/Test.edgelist',dtype=int)
E = np.loadtxt('/home/hongqiaochen/Desktop/Link_predict/Power/Power_standard.txt',dtype=int)
Train = np.loadtxt('/home/hongqiaochen/Desktop/Link_predict/Power/Train.edgelist',dtype=int)
# 构造Not集
P_E = 0
for i in range(len(E)):
    if E[i][0] > P_E:
        P_E = E[i][0]
    elif E[i][1] > P_E:
        P_E = E[i][1]
P_E += 1
N = [[1]*P_E for i in range(P_E)]
N = np.array(N)
for i in range(0,len(E)):
    a = E[i][0]
    b = E[i][1]
    N[a][b] = 0
for i in range(0,P_E):
    N[i][i] = 0
count2 =0
for i in range(0,P_E):
    for j in range(0,P_E):
        if N[i][j] == 1:
            count2 += 1
number = count2
i = 0
j = 0
count3 = 0
NotA = [0 for i in range(number)]
NotA = np.array(NotA)
NotB = [0 for i in range(number)]
NotB = np.array(NotB)
for i in range(0,P_E):
    for j in range(0,P_E):
        if N[i][j] == 1:
            NotA[count3] = i
            NotB[count3] = j
            count3 += 1
Not = np.vstack([NotA,NotB])
Not=np.transpose(Not)

#创建List集 第i行表示 节点i的邻居节点的序号
Train = np.transpose(Train)
list1 = Train[0]
list1 = list1.tolist()
list2 = Train[1]
list2 = list2.tolist()
Train = np.transpose(Train)
list3 = list1+list2
list3 = np.unique(list3)
list3 = np.array(list3)
list3 = list3.reshape(-1,1)
list4 = [[0] for i in range(len(list3))]
list4 = np.array(list4)
list_degree = np.hstack([list3,list4])
for i in range(len(Train)):
    list_degree[Train[i][0]][1] += 1
    list_degree[Train[i][1]][1] += 1
List = [[] for i in range(len(list_degree))]
for i in range(len(Train)):
    List[Train[i][0]].append(Train[i][1])
    List[Train[i][1]].append(Train[i][0])
for i in range(len(list_degree)):
    List[i] = list(set(List[i]))
    List[i] = list(set(List[i]))



# auc = Randwalk(p=1, times=10, length=30, window=10,
#                    min_count=0, alpha=0.01)
#
# print(auc)


param_p = np.arange(0,1.1,0.5)
print(len(param_p))
param_times = np.arange(10,35,10)
print(len(param_times))
param_length = np.arange(10,50,10)
print(len(param_length))
param_window = np.arange(5,50,5)
print(len(param_window))
param_min_count = np.array([0])
print(len(param_min_count))
param_alpha = np.array([0.001,0.01,0.025,0.05,0.1,0.25,0.5,1])
print(len(param_alpha))
# 测试数据
# param_p = np.array([0,1])
# param_times = np.array([10])
# param_length = np.array([30])
# param_window = np.array([15])
# param_min_count = np.array([0])
# param_alpha = np.array([0.01,0.025,0.1,0.25,0.5,1])
n = len(param_p)*len(param_times)*len(param_length)*len(param_window)*len(param_min_count)*len(param_alpha)
print(n)
AUC = [0 for i in range(n)]
count = 0
for i in range(len(param_p)):
    for j in range(len(param_times)):
        for k in range(len(param_length)):
            for m in range(len(param_window)):
                for n in range(len(param_min_count)):
                    for p in range(len(param_alpha)):
                        auc = Randwalk(p=param_p[i],times=param_times[j],length=param_length[k],window=param_window[m],min_count=param_min_count[n],alpha=param_alpha[p])
                        AUC[count]=auc
                        count += 1
                        print(count)
                        print(auc)
best_auc_index = AUC.index(max(AUC))
best_auc = AUC[best_auc_index]
print(best_auc)
np.savetxt('/home/hongqiaochen/Desktop/Link_predict/Power/bestDW.edgelist',AUC)