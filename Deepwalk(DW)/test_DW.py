import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import word2vec
import numpy as np
import random

path = '/home/hongqiaochen/Desktop/Date_Link_predict/Power'

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

def Create_Not():
    Num = len(np.unique(E))
    N = [[1] * Num for i in range(Num)]
    N = np.array(N)
    for i in range(0, len(E)):
        N[E[i][0]][E[i][1]] = 0
        N[E[i][1]][E[i][0]] = 0
    for i in range(0, Num):
        N[i][i] = 0

    count = 0
    for i in range(0, Num):
        for j in range(0, Num):
            if N[i][j] == 1:
                count += 1
    number = int(count / 2)

    count = 0
    Not = [[0, 0] for i in range(number)]
    for i in range(Num):
        for j in range(i, Num):
            if N[i][j] == 1:
                Not[count][0] = i
                Not[count][1] = j
                count += 1
    return Not

def rank(list,k=50):
    Rank = list[0]
    for i in range(1,k):
        Rank = Rank+list[i]/(np.log2(i+1))
    return Rank

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
    np.savetxt(path+'/walkpath.txt', walkpath,fmt='%d',delimiter=' ')
    walkpath = word2vec.Text8Corpus(path+'/walkpath.txt')
    model = word2vec.Word2Vec(walkpath,size = 64,hs = 1,min_count = min_count,window = window,sg=1,alpha=alpha)
    model.wv.save_word2vec_format(path+'/DW_vector.txt')
    V = np.loadtxt(path+'/DW_vector.txt', dtype=float,skiprows=1)
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
    DCG = [0.0 for i in range(MAX)]
    IDCG = [0.0 for i in range(MAX)]
    for i in range(MAX):
        if S_Test_Sample[i] > S_Not_Sample[i]:
            DCG[i] = 1
            n1 += 1
        if S_Test_Sample[i] == S_Not_Sample[i]:
            DCG[i] = 0.5
            n2 += 1
    AUC = (n1 + 0.5 * n2) / n
    for i in range(n1 + n2):
        if i < n1:
            IDCG[i] = 1.0
        else:
            IDCG[i] = 0.5
    NDCG = rank(DCG) / rank(IDCG)
    return AUC, NDCG


# 读取Test,E,Train集合
Test = np.loadtxt(path+'/Test.edgelist',dtype=int)
E = np.loadtxt(path+'/standard.txt',dtype=int)
Train = np.loadtxt(path+'/Train.edgelist',dtype=int)
# 构造Not集
Not = Create_Not()

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

AUC,NDGC = Randwalk(p=0, times=15, length=10, window=15,min_count=0, alpha=0.01)

print(AUC,NDGC)

