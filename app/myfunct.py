import math as mat
import numpy as np
import copy
##########################################################
###  Give root equations one varriables Newton method  ###
##########################################################

def rootN(x0,fName,ntp=0):
    def difF(x0,h):
        return (fName(x0+h)-fName(x0-h))/2/h

    BESTACC=-14
    N=300; hi=1e-12; xi=x0
    xout=[xi]; hout=[hi]
    
    for i in range(N):
        hi=fName(xi)/difF(xi,abs(hi))
        xi=xi-hi
        hout.append(hi)
        xout.append(xi)
        if abs(hi)<1e-13 or mat.isnan(xi):
            break

    hout=[mat.log(abs(itt))/mat.log(10) if itt!=0 else BESTACC for itt in hout]
    if fName(xi)!=0:
        if abs(fName(xi))>1e-12:
            xi=float('nan')
    if ntp==0:    
        return xi
    elif ntp==1:
        return [xi,hout[-1]]
    else:
        return [xi,hout[-1],xout,hout]
#****************************************************#


#################################
#### Integral simpson method  ###
#################################
    
def intSims(lim,nInt,fName):
    ld=lim[0]; lu=lim[1];
    nump=2*nInt+1; 
    h=float(lu-ld)/(nump-1)
    sum2=0; sum4=0
    for i in range(1,nump-1,2):
        sum4+=fName(ld+i*h)
        sum2+=fName(ld+i*h+h)
    return h/3*(fName(ld)-fName(lu)+4*sum4+2*sum2)

def accInt(metName,nPow,fName,lim):
    nInt=2**np.arange(nPow)
    delt=np.zeros(nPow)
    deltt=np.ones(nPow)
    ma=np.ones(nPow)
    inti=np.zeros(nPow)
    for i in range(nPow):
        inti[i]=metName(lim,nInt[i],fName)
        delt[i]=abs(inti[i]-inti[i-1])/(2**ma[i]-1)
        deltt[i]=abs(inti[i]-inti[i-1])
        ma[i]=1/np.log(2)*np.log(deltt[i-1]/deltt[i])
    return nInt,np.log(delt)/np.log(10),ma,inti


def intSimscum(lim,nInt,fName,nOut=100):
    ld=lim[0]; lu=lim[1];
    nump=2*nInt+1; #Число точек интегрирования
    h=float(lu-ld)/(nump-1)
    intC=np.zeros(nInt+1)
    for i in range(1,nump-1,2):
        intC[int((i+1)/2)]=intC[int((i+1)/2)-1]+h/3*(fName(ld+i*h-h)+4*fName(ld+i*h)+fName(ld+i*h+h))
    return intC

def intSimscumR(lim,nInt,f_name,nOut=100):
    diapH=(lim[1]-lim[0])/(nOut-1)
    intC=np.zeros(nOut)
    for i in range(nOut):
        intC[i]=intSims([lim[0],diapH*i],nInt,f_name)
    return intC
#****************************************************#



#################################
####       Gauss method       ###
#################################

class ExGaussNoSquare(Exception):
    pass
class ExGaussBnoA(Exception):
    pass

def lingauss(A,B,ntp=0):
    def changemax(M,S,crcl):
        ind=crcl+abs(M[crcl:,crcl]).argmax()
        tmpM=M[crcl,crcl:].copy()
        tmpS=S[crcl].copy()
        
        S[crcl]=S[ind]
        M[crcl,crcl:]=M[ind,crcl:]
        S[ind]=tmpS
        M[ind,crcl:]=tmpM
        
    try:
        A=np.array(A,'float');B=np.array(B,'float')
        n=len(A[0,:])
        
        if A.ndim!=2 or n!=len(A[:,0]):
            raise ExGaussNoSquare()
        if len(B)!=len(A):
            raise ExGaussBnoA()

        X=np.zeros(n)
        N=0
        
        if ntp==1:        
            A0=A.copy()
            B0=B.copy()
        
        for imcl in range(n):
            changemax(A,B,imcl)
            for irw in range(imcl+1,n):
                if A[irw,imcl]!=0:
                    alph=-A[irw,imcl]/A[imcl,imcl]
                    B[irw]+=B[imcl]*alph
                    for icl in range(imcl,n):
                        A[irw,icl]+=A[imcl,icl]*alph

        for imcl in sorted(range(n),reverse=True): #Обходим с конца в начало
            tmpb=B[imcl]
            for itt in range(imcl,n):
                tmpb-=A[imcl,itt]*X[itt]
            X[imcl]=tmpb/A[imcl,imcl]

        if ntp==1:    
            for imrw in range(n):
                tmpn=-B0[imrw]
                for imcl in range(n):
                    tmpn+=A0[imrw,imcl]*X[imcl]
                N+=abs(tmpn)
            N=N/n
    except ExGaussNoSquare:
        print('Матрица не квадратная')
        if ntp==1:
            return None,None
        else:
            return None 
    except ExGaussBnoA:
        print('Размер матрицы B не соответствует A')
        if ntp==1:
            return None,None
        else:
            return None
    else:
        if ntp==1:
            return X,N
        else:
           return X 
#****************************************************#

        
#######################################
####           Gauss method         ###
####  Без выбора главного элемента  ###
#######################################
        
def lingaussNCng(A,B,ntp=0):
    try:
        A=np.array(A,'float');B=np.array(B,'float')
        n=len(A[0,:])
        
        if A.ndim!=2 or n!=len(A[:,0]):
            raise ExGaussNoSquare()
        if len(B)!=len(A):
            raise ExGaussBnoA()

        X=np.zeros(n)
        N=0
        
        if ntp==1:        
            A0=A.copy()
            B0=B.copy()
        
        for imcl in range(n):
            for irw in range(imcl+1,n):
                if A[irw,imcl]!=0:
                    alph=-A[irw,imcl]/A[imcl,imcl]
                    B[irw]+=B[imcl]*alph
                    for icl in range(imcl,n):
                        A[irw,icl]+=A[imcl,icl]*alph

        for imcl in sorted(range(n),reverse=True): #Обходим с конца в начало
            tmpb=B[imcl]
            for itt in range(imcl,n):
                tmpb-=A[imcl,itt]*X[itt]
            X[imcl]=tmpb/A[imcl,imcl]

        if ntp==1:    
            for imrw in range(n):
                tmpn=-B0[imrw]
                for imcl in range(n):
                    tmpn+=A0[imrw,imcl]*X[imcl]
                N+=abs(tmpn)
            N=N/n
    except ExGaussNoSquare:
        print('Матрица не квадратная')
        if ntp==1:
            return None,None
        else:
            return None 
    except ExGaussBnoA:
        print('Размер матрицы B не соответствует A')
        if ntp==1:
            return None,None
        else:
            return None
    else:
        if ntp==1:
            return X,N
        else:
           return X 
#****************************************************#
        

##############################################
####    Polinom approximate/interpolate    ###
##############################################

class ExNoOneDim(Exception):
    pass
class ExLenxiNoyi(Exception):
    pass

def polyapr(xi,yi,m):
    try:
        xi=np.array(xi);yi=np.array(yi)
        A=[];  B=[];  c=[]
        npnt=len(xi)
        if xi.size!=yi.size:
            raise ExLenxiNoyi()
        
        if npnt > m:
            for jj in range(m*2):
                summac=0;summab=0
                for itt in range(npnt):
                    summac+=xi[itt]**jj
                    if jj<m:
                        summab+=(xi[itt]**jj)*yi[itt]
                c.append(summac)
                if jj<m:
                    B.append(summab)

            for jj in range(m):
                line=[]
                for itt in range(jj,m+jj):
                    line.append(c[itt])
                A.append(line)
        else:
            m=npnt
            for itt in range(m):
                line=[]
                for jj in range(m):
                    line.append(xi[itt]**jj)
                A.append(line)
            B=yi
            
        A=np.array(A)
        B=np.array(B)
        X=np.linalg.solve(A,B)
        #X=lingauss(A,B)
    except ExLenxiNoyi:
        print('Размер xi и yi не совпадает')
        return None
    except ExGaussBnoA:
        return None
    else:
        return X
#****************************************************#



################################
####    Polinom calculate    ###
################################
    
def polyval(p,x):
    try:
        p=np.array(p)
        if p.ndim!=1:
            raise ExNoOneDim()
        
        n=len(p)
        out=[]
        for itt in x:
            line=0
            for jj in range(n):
                line+=p[jj]*itt**jj
            out.append(line)
    except TypeError:
        line=0
        for jj in range(n):
            line+=p[jj]*x**jj
        return line
    except ExNoOneDim:
        print('Матрица коэффициентов полинома не вектор')
        return None
    else:
        return np.array(out)

def polyder(p,nder=1):
    try:
        p=np.array(p)
        if p.ndim!=1:
            raise ExNoOneDim()
        
        for itt in range(p.size):
            p[itt]*=itt

    except ExNoOneDim:
        print('Матрица коэффициентов полинома не вектор')
        return None
    else:
        return p[1:]


##################################
####    Spline interpolate    ####
####      (class Spline)      ####
##################################

class Spline():
    def __init__(self,xi,yi,y2sh=[0,0]):
        self.spline=[]
        self.nder=0
        self.n=len(xi)
        try:
            if self.n!=len(yi):
                raise ExLenxiNoyi()

            for itt in range(self.n):
               self.spline.append({'a':yi[itt],'x':xi[itt]})
            self.spline[0]['c']=y2sh[0]/2
            self.spline[-1]['c']=y2sh[-1]/2
        
            A=np.zeros(self.n-1)
            B=np.zeros(self.n-1)
            B[0]=self.spline[0]['c']
            for itt in range(1,self.n-1):
                hi=xi[itt]-xi[itt-1] 
                hi1=xi[itt+1]-xi[itt]
                a=hi; b=2.*(hi+hi1); c=hi1
                d=3.*((yi[itt+1]-yi[itt])/hi1-(yi[itt]-yi[itt-1])/hi)
                z=b+a*A[itt-1]
                A[itt]=-a/z
                B[itt]=(d-a*B[itt-1])/z

            for itt in sorted(range(1,self.n-1),reverse=True):
                self.spline[itt]['c']=B[itt]+A[itt]*self.spline[itt+1]['c']

            for itt in range(self.n-1):
                hi1=xi[itt+1]-xi[itt]
                self.spline[itt]['d']=(self.spline[itt+1]['c']-self.spline[itt]['c'])/hi1/3
                self.spline[itt]['b']=(yi[itt+1]-yi[itt])/hi1-hi1/3*(2*self.spline[itt]['c']+self.spline[itt+1]['c'])
            
        except ExLenxiNoyi:
            print('Размер xi и yi не совпадает')
    
    def calcspln(self,xin):
        arr=[]
        for xi in xin:
            if xi<=self.spline[0]['x']:
                s=self.spline[0]
            elif xi>=self.spline[-1]['x']:
                s=self.spline[-2]
            else:
                lbnd = 0
                ubnd = self.n
                while ubnd-lbnd>1:
                    cmpval = (ubnd+lbnd)//2
                    if xi <= self.spline[cmpval]['x']:
                        ubnd=cmpval
                    else:
                        lbnd=cmpval
                s = self.spline[lbnd]
            arr.append(s['a']+s['b']*(xi-s['x'])+(s['c']+s['d']*(xi-s['x']))*(xi-s['x'])*(xi-s['x']))
        return arr

    def splder(self,nder=1):
        if nder+self.nder>3 or nder < 1:
            ds=None
        else:
            ds=copy.deepcopy(self)
            for jj in range(nder):
                ds.nder+=1
                for itt in range(ds.n-1):
                    ds.spline[itt]['a']=ds.spline[itt]['b']
                    ds.spline[itt]['b']=2*ds.spline[itt]['c']
                    ds.spline[itt]['c']=3*ds.spline[itt]['d']
                    ds.spline[itt]['d']=0
        return ds

##################################
####    B - Spline form        ###
####      (class B_Spline)     ###
##################################

class B_Spline():
    def __init__(self,xi,yi,w=None,npintr=2,pspl=2):
        
        self.ndat=len(xi)  # Число точек аппрокс.
        try:
            if self.ndat!=len(yi):
                raise ExLenxiNoyi()
            if npintr <= 1:  # Число точек на один сплайн
                npintr=2
            
            self.pspl=pspl #Порядок сплайна
            self.nder=0  # Число дифференцирований сплайна
            self.c=[]   # Коэффициенты аппроксимации
            self.x=[]    # Узлы стыковки сплайнов
            self.xi=xi  # Узлы аппроксимации
            self.yi=yi  # Узлы аппроксимации
            if w==None:   # Вес узлов
                self.w=np.ones(self.ndat)
            self.nspl=self.ndat//npintr # Число сплайнов

            for itt in range(self.pspl,-1,-1):
                self.x.append(xi[0]-itt)

            dn=(self.ndat-self.nspl*npintr)//2

            for itt in range(1,self.nspl):
                self.x.append((xi[dn+itt*npintr]+xi[dn+itt*npintr-1])/2.)
            
            for itt in range(self.pspl+1):
                self.x.append(xi[-1]+itt)

            A=np.zeros([self.nspl+self.pspl,self.nspl+self.pspl])
            B=np.zeros(self.nspl+self.pspl)

            for itt in range(self.nspl+self.pspl):# Здесь
                B[itt]=self.scalmultY(itt)         # itt - индекс узла стыковки
                for jj in range(self.nspl+self.pspl):
                    A[itt,jj]=self.scalmultB(itt,jj)
            self.c=np.linalg.solve(A,B)
            #self.c=lingauss(A,B)

        except ExLenxiNoyi:
            print('Размер xi и yi не совпадает')
            
    def scalmultB(self,ispl,jspl):
        out=0
        for itt in range(self.ndat):
            out+=self.calcB(ispl,self.xi[itt])*self.calcB(jspl,self.xi[itt])*self.w[itt]**2
        return out
    
    def scalmultY(self,ispl):
        out=0
        for itt in range(self.ndat):
            out+=self.calcB(ispl,self.xi[itt])*self.yi[itt]*self.w[itt]**2
        return out
    
    def calcB(self,ispl,x):
        p=self.pspl
        if x <= self.x[ispl] or x > self.x[ispl+p+1]:
            return 0
        
        B=np.zeros(p+1)
        for itt in range(p+1):
            if x>self.x[ispl+itt] and x<=self.x[ispl+itt+1]:
                B[itt]=1
        for pi in range(p):
            for itt in range(p-pi):        
                xn=self.x[ispl+itt]
                xn1=self.x[ispl+itt+1]
                xnp1=self.x[ispl+pi+itt+1]
                xnp2=self.x[ispl+pi+itt+2]
                B[itt]=(x-xn)*B[itt]/(xnp1-xn)+(xnp2-x)*B[itt+1]/(xnp2-xn1)   
        return B[0]
    
    def calcdB(self,ispl,x):
        p=self.pspl
        if x <= self.x[ispl] or x > self.x[ispl+p+1] or p==0:
            return 0
        
        dB=np.zeros(p+1)
        B=np.zeros(p+1)
        for itt in range(p+1):
            if x>self.x[ispl+itt] and x<=self.x[ispl+itt+1]:
                B[itt]=1
        for pi in range(p):
            for itt in range(p-pi):        
                xn=self.x[ispl+itt]
                xn1=self.x[ispl+itt+1]
                xnp1=self.x[ispl+pi+itt+1]
                xnp2=self.x[ispl+pi+itt+2]
                
                dB[itt]=((x-xn)*dB[itt]+B[itt])/(xnp1-xn)+((xnp2-x)*dB[itt+1]-B[itt+1])/(xnp2-xn1)
                B[itt]=(x-xn)*B[itt]/(xnp1-xn)+(xnp2-x)*B[itt+1]/(xnp2-xn1)
        return dB[0]
    
    def calcspl(self,xin):
        try:
            arr=[]
            for itt in xin:
                line=0
                for jj in range(self.nspl+self.pspl):
                    line+=self.c[jj]*self.calcB(jj,itt)
                arr.append(line)
            return np.array(arr)
        except TypeError:
            arr=0
            for jj in range(self.nspl+self.pspl):
                arr+=self.c[jj]*self.calcB(jj,xin)
            return arr
        
    def calcderspl(self,xin):
        try:
            arr=[]
            for itt in xin:
                line=0
                for jj in range(self.nspl+self.pspl):
                    line+=self.c[jj]*self.calcdB(jj,itt)
                arr.append(line)
            return np.array(arr)
        except TypeError:
            arr=0
            for jj in range(self.nspl+self.pspl):
                    arr+=self.c[jj]*self.calcdB(jj,xin)
            return arr 

    def getintervals(self):
        ints=self.x[self.pspl:-self.pspl]
        return ints
    

    def getbasis(self):
        x=np.linspace(self.xi[0],self.xi[-1],1000)
        line=[]
        for itt in range(self.nspl+self.pspl):
            lst=[]
            for jj in x:
                lst.append(self.calcB(itt,jj))
            line.append(lst)
        return line,x
    

    


    
        
