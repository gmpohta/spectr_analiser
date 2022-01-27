
import tkinter as tk
import tkinter.filedialog as fdial
import tkinter.messagebox as msgbox
import os
import sys
import pickle as pck
import scipy as sp
import io
from PIL import Image
import win32clipboard
import copy

import libwidgets as lwd
import myfunct as myf
import numpy as np

AEM=1.660540e-27 #kg
QE= 1.60217662e-19 #Kl

class ExWrongFormat(Exception):
    pass

class ExNoMetAppr(Exception):
    pass

class Command():
    def execute(self):
        raise NotImplementedError()
    
class TraceCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.arrdata=arrdata
        self.appdata=appdata
        self.pltwind=pltwind
        
    def execute(self,ev=None):
        x=ev.xdata
        y=ev.ydata
        if x!=None and y!=None:
            cdata=self.arrdata[self.appdata.oneselect()]
            self.currpoint=cdata.calctrace(x)
            maxdi=max(cdata.data.data['adi'])
            if maxdi==0:
                maxdi=1
            self.pltwind.settrace([x,self.currpoint[1]/maxdi])
        else:
            self.pltwind.settrace() 

class DelPointCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.arrdata=arrdata
        self.appdata=appdata
        self.pltwind=pltwind
        self.currpoint=[0,0]
        self.top=lwd.DelPointDial(appdata)
        self.top.setcmd(self.okcmd,self.cancelcmd)
        self.pltwind.setclosecmd(self.normalmodePlt)
        self.currselect=0
        self.dialog=False

    def execute(self,ev=None):
        self.currselect=self.appdata.oneselect()
        self.cdata=self.arrdata[self.appdata.oneselect()]
        self.originaldata=self.cdata.get_current_data()
        self.appdata.setstatepanelall(0)
        self.appdata.intpan.panoff()
        self.appdata.genaprxpan.panoff()
        self.setstate('delpoint')
        self.top.setposition()
        self.pltwind.setmouseselectcmd(self.onMouseRelease)
        self.pltwind.setmenustate(0)
        self.dialog=True
        
    def onMouseRelease(self,ev=None):
        x=ev.xdata
        y=ev.ydata
        if x!=None and y!=None:
            k=self.pltwind.ki
            mousepoint=[x,y/k]+self.pltwind.get_range_figure()
            mousepoint[3]=mousepoint[3]/k
            currpoint=self.cdata.detpoint(mousepoint)
            self.pltwind.pltdata(self.cdata,currpoint)
            self.cdata.deletepoint(currpoint)
            self.pltwind.pltdata(self.cdata)
            self.top.setposition()
            self.top.panstate(1)

    def okcmd(self):
        self.appdata.mainaprxcmd.execute()
        self.pltwind.pltdata(self.cdata)
        self.setstate('norm')
        self.appdata.setallflag(0)
        if self.currselect!=None:
            cdata=self.arrdata[self.currselect]
            cdata.setselect(1)
            self.appdata.intpan.setlim(cdata)
            self.appdata.genaprxpan.refreshdata(cdata)
            self.pltwind.pltdata(cdata)
        self.appdata.setstatepanelall(1)
        self.pltwind.setmouseselectcmd(0)
        self.pltwind.setmenustate(1)

    def cancelcmd(self):
        self.cdata.set_current_data(self.originaldata)
        self.pltwind.pltdata(self.cdata)
        self.setstate('norm')
        self.appdata.setallflag(0)
        if self.currselect!=None:
            cdata=self.arrdata[self.currselect]
            cdata.setselect(1)
            self.appdata.intpan.setlim(cdata)
            self.appdata.genaprxpan.refreshdata(cdata)
            self.pltwind.pltdata(cdata)
        self.appdata.setstatepanelall(1)
        self.pltwind.setmouseselectcmd(0)
        self.pltwind.setmenustate(1)
        
    def normalmodePlt(self):
        if self.dialog==True:
            self.setstate('norm')
            self.appdata.setallflag(0)
            if self.currselect!=None:
                cdata=self.arrdata[self.currselect]
                cdata.setselect(1)
                self.appdata.intpan.setlim(cdata)
                self.appdata.genaprxpan.refreshdata(cdata)
            self.appdata.setstatepanelall(1)
            self.pltwind.setmouseselectcmd(0)
            self.pltwind.setmenustate(1)
            self.top.withdraw()
            self.dialog=False
        
    def setstate(self,val):
        for itt in self.arrdata:
            itt.setstate(val)
            
class SetAllCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.arrdata=arrdata
        self.appdata=appdata
        self.pltwind=pltwind
        self.top=lwd.SetAllDialog(self.appdata)
        self.top.setcmd(self.cmdset)
        
    def execute(self,ev=None):
        self.top.setposition()
        
    def cmdset(self,inrowdata,inkeyrowdata):
        for itt in self.arrdata:
            itt.setrowdata(inrowdata,inkeyrowdata)
            itt.iscalculated=False
            itt.lose_result_table()

        num=self.appdata.oneselect()
        self.arrdata[num].autoaprx(self.appdata.genaprxpan.getdata())##
        self.arrdata[num].calcDens()##
        self.arrdata[num].iscalculated=True
        self.pltwind.pltdata(self.arrdata[num])
        self.appdata.intpan.setlim(self.arrdata[num])
        self.appdata.genaprxpan.refreshdata(self.arrdata[num])
        self.appdata.current_method_aprx=self.arrdata[num].getaprxdata()
        self.appdata.cansavetxt()
         
class SaveTxtCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.appdata=appdata
        self.arrdata=arrdata
        self.pltwind=pltwind
        self.top=lwd.SaveTxtDialog(self.appdata)
        cmd={'save':self.cmdsave,'sel':self.selectall,'unsel':self.unselectall,'norm':self.normalmode}
        self.top.setcmd(cmd)
        
    def execute(self,ev=None):
        self.currselect=self.appdata.oneselect()
        self.pltwind.pltdata()
        self.appdata.setstatepanelall(0)
        self.appdata.intpan.panoff()
        self.appdata.genaprxpan.panoff()
        self.setstate('mult')
        for itt in self.arrdata:
            itt.setselect(1)
        self.top.setposition()
        
    def selectall(self,ev=None):
        self.appdata.setallflag(1)
    def unselectall(self,ev=None):
        self.appdata.setallflag(0)

    def cmdsave(self,npcalc,wsave):
        alls=self.appdata.detallselect()
        if alls!=[]:
            pfile=fdial.asksaveasfilename(defaultextension=".txt",initialfile='noname.txt',title='Сохранить в текстовый файл')
            if pfile:
                f = open(pfile, 'w')
                wlist,wrt=self.recalc(npcalc,wsave)
                for itt in wrt:
                    for jj in itt:
                        f.write(str(jj))
                        f.write('\t')
                    f.write('\n')
                if wlist!=[]:
                    tmplen=[]
                    for itt in wlist:
                        tmplen.append(len(itt))
                    maxrowwlist=max(tmplen)
                    for itt in range(maxrowwlist):
                        for jj in wlist:
                            try:
                                f.write(str(jj[itt]))
                                f.write('\t')
                            except IndexError:
                                f.write('')
                                f.write('\t')
                        f.write('\n')
                f.close()
        self.top.withdraw()
        self.normalmode()
                
    def recalc(self,npcalc,wsave):
        alls=self.appdata.detallselect()
        inptval=[]
        name=[];gas=[]
        scol=[];wavr=[]
        dens=[];sco=[]
        nqgas=[];wmax=[]
        for itt in alls:
            tdat=self.arrdata[itt]
            ncoln=-2
            if wsave['a']==1:
                ncoln+=3
                inptval+=tdat.autocalc(npcalc,1)
            if wsave['e'] or wsave['d']:
                ncoln+=1
                inptval+=tdat.getdata()['w']
            if wsave['e']==1:
                ncoln+=1
                inptval+=tdat.getdata()['sco']
            if wsave['d']==1:
                ncoln+=1
                inptval+=tdat.getdata()['i']
            name+=['Кадр:',tdat.rowdata['kname']]+['']*ncoln
            gas+=['Газ:',tdat.keyrowdata['mgas']]+['']*ncoln
            nqgas+=['Кратн. заряда иона:',tdat.rowdata['mgas'][1]]+['']*ncoln
            scol+=['S коллект., м^2:',tdat.rowdata['scol']]+['']*ncoln
            dens+=['Плотность, см^-3:',tdat.rowdata['n']]+['']*ncoln
            wavr+=['Ср. энергия, эВ:',tdat.rowdata['wavr']]+['']*ncoln
            wmax+=['Энергия максимума, эВ:',tdat.rowdata['wmax']]+['']*ncoln
            sco+=['SСО аппроксимации:',tdat.getaprxdata()['sco']]+['']*ncoln
            
        wrt=[name,gas,nqgas,scol,dens,wavr,wmax,sco]
        return inptval,wrt
        
    def setstate(self,val):
        for itt in self.arrdata:
            itt.setstate(val)
            
    def normalmode(self):
        self.setstate('norm')
        self.appdata.setallflag(0)
        if self.currselect!=None:
            cdata=self.arrdata[self.currselect]
            cdata.setselect(1)
            self.appdata.intpan.setlim(cdata)
            self.appdata.genaprxpan.refreshdata(cdata)
        self.appdata.setstatepanelall(1)
        
class SaveArrCommand(Command):
    def __init__(self,appdata,arrdata):
        self.arrdata=arrdata
        self.appdata=appdata
        
    def execute(self,ev=None):
        pfile=fdial.asksaveasfilename(defaultextension=".pkl",initialfile='newarr.pkl',title='Сохранить в архив')
        if pfile:
            try:
                f = open(pfile, 'wb')
                data=[]
                for itt in self.arrdata:
                    data.append(itt.data)
                pck.dump(data, f)
            except IOError:
                msgbox.showerror("Open Source File", "Failed to save file\n'%s'" % pfile)
            except:
                msgbox.showerror("Open Source File", "Wrong type file\n'%s'" % pfile)
                f.close()
            else:
                f.close()

class LoadArrCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.arrdata=arrdata
        self.appdata=appdata
        self.pltwind=pltwind
        self.init=appdata.init
        
    def execute(self):
        pfile=fdial.askopenfilename(filetypes=(('Пакет данных','*.pkl'),("All files", "*.*")))
        if pfile:
            try:
                f=open(pfile,'rb')
                data=pck.load(f)
                parent=self.appdata.canvtabl.frame
                lenarr=len(data)
                for itt in range(lenarr):
                    curline=TableLine(parent,data[itt])
                    cmdS=OneSelectCommand(self.appdata,curline,self.pltwind)
                    cmdC=SelectComboCommand(self.appdata,curline,self.pltwind)
                    curline.setcmd(cmdS,cmdC)
                    self.arrdata.append(curline)
                cmdS.execute()
                self.appdata.repacktabl()
                self.appdata.setstatepanel(1)
                self.appdata.cansavetxt()
                
            except IOError:
                msgbox.showerror("Open Source File", "Failed to load file\n'%s'" % pfile)
            except:
                msgbox.showerror("Open Source File", "Wrong type file\n'%s'" % pfile)
                f.close()
            else:
                f.close()
        
class ClearAllCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.arrdata=arrdata
        self.appdata=appdata
        self.pltwind=pltwind
        self.curdata=None
        
    def execute(self):
        if msgbox.askyesno('Очистить?','Вы уверены?'):
            num=len(self.arrdata)
            if num!=0:
                for itt in range(num-1,-1,-1): #Переменная itt проходит все строки  
                    self.arrdata[itt].destroyGUI()   #с конца в начало, чтобы последующие строки не смещались
                    del(self.arrdata[itt])   
                self.appdata.repacktabl() 

                self.appdata.intpan.panoff()
                self.appdata.genaprxpan.panoff()
                self.pltwind.pltdata()
                self.appdata.setstatepanel(0)
                self.appdata.title('Spectrum')

class AprxCommand(Command):
    def __init__(self,appdata,arrdata,pltwind):
        self.arrdata=arrdata
        self.appdata=appdata
        self.gaprxpan=appdata.genaprxpan
        self.pltwind=pltwind
        
    def execute(self,ev=None):
        num=self.appdata.oneselect()
        if num!=None:
            self.arrdata[num].autoaprx(self.gaprxpan.getdata())
            self.arrdata[num].calcDens()
            self.gaprxpan.refreshdata(self.arrdata[num])
            self.pltwind.pltdata(self.arrdata[num])
                  
class GetLimitsCommand(Command):
    def __init__(self,appdata,arrmdata,pltwind):
        self.arrdata=arrmdata
        self.pltwind=pltwind
        self.appdata=appdata
        
    def execute(self):
        num=self.appdata.oneselect()
        if num != None:
            mdata=self.arrdata[num]
            if mdata.status=='norm':
                self.appdata.intpan.getlim(mdata)
                self.appdata.intpan.setlim(mdata)
                mdata.autocalc()
                mdata.calcDens()
                self.appdata.genaprxpan.refreshdata(mdata)
                self.pltwind.pltdata(mdata)

class CopytableCommand(Command):
    def __init__(self,appdata,arrdata):
        self.arrdata=arrdata
        self.appdata=appdata
        
    def execute(self):
        temp='Кадр\tn, см^-3\tWср, эВ\tWmax, эВ \n'
        for itt in self.arrdata:
            temp+=itt.rowdata['kname']+'\t'+str(round(itt.rowdata['n'],0))+\
                 '\t'+str(round(itt.rowdata['wavr'],3))+'\t'+str(round(itt.rowdata['wmax'],3))+'\n'
        self.appdata.clipboard_clear()
        self.appdata.clipboard_append(temp)
        
class CopydataCommand(Command):
    def __init__(self,appdata,arrdata):
        self.appdata=appdata
        self.arrdata=arrdata
        
    def execute(self):
        num=self.appdata.oneselect()
        if num!=None:
            temp=''
            itt=self.arrdata[num]
            temp+=itt.rowdata['kname']+'\nn= '+str(round(itt.rowdata['n'],0))+' см^-3\nWср= '+\
                 str(round(itt.rowdata['wavr'],3))+' эВ\nWmax= '+str(round(itt.rowdata['wmax'],3))+' эВ\n'
            calc=itt.autocalc(nump=50,inputvar=1)
            temp+=str(calc[0][0])+'\t'+str(calc[2][0])+'\n'
            for itt in range(1,len(calc[0])):
                strw=str(round(calc[0][itt],3))
                for sym in strw:
                    if sym == ".":
                        strw = strw.replace(sym,",")
                strf=str(round(calc[2][itt],3))
                for sym in strf:
                    if sym == ".":
                        strf = strf.replace(sym,",")
                temp+=strw+'\t'+strf+'\n'
            self.appdata.clipboard_clear()
            self.appdata.clipboard_append(temp)  
        
class CopykzfrCommand(Command):
    def __init__(self,pltwind):
        self.pltwind=pltwind
        
    def add_clipboard(self,clip_type, data): 
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data) 
        win32clipboard.CloseClipboard()
    
    def savefw(self):
        tmpp=lwd.__file__.split('\\')
        pfile=tmpp[0]
        for itt in tmpp[1:-1]:
            pfile+='\\'+itt
        pfile+='\\tmp.png'
        size0=self.pltwind.figdi.get_size_inches()
        self.pltwind.figdi.set_size_inches(6, 4)
        self.pltwind.figdi.savefig(pfile,dpi=200)
        img=Image.open(pfile)
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        self.add_clipboard(win32clipboard.CF_DIB,data)
        self.pltwind.figdi.set_size_inches(size0)
        
    def savekz(self):
        tmpp=lwd.__file__.split('\\')
        pfile=tmpp[0]
        for itt in tmpp[1:-1]:
            pfile+='\\'+itt
        pfile+='\\tmp.png'
        size0=self.pltwind.figi.get_size_inches()
        self.pltwind.figi.set_size_inches(6, 4)
        self.pltwind.figi.savefig(pfile,dpi=200)
        img=Image.open(pfile)
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        self.add_clipboard(win32clipboard.CF_DIB,data)
        self.pltwind.figdi.set_size_inches(size0)
        
class DelLineCommand(Command):
    def __init__(self,appdata,arrmdata,pltwind):
        self.arrdata=arrmdata
        self.appdata=appdata
        self.pltwind=pltwind
        
    def execute(self):
        numrow=self.appdata.oneselect()
        if numrow!=None:
            self.arrdata[numrow].destroyGUI()
            del(self.arrdata[numrow])
            self.appdata.repacktabl()
            #Устанавливаем выделение на следующюю строку и рисуем график 
            if len(self.arrdata) > 0:
                self.appdata.setallflag(0)
                if numrow >= len(self.arrdata):
                    numrow=-1
                self.arrdata[numrow].setselect(1)
                self.appdata.intpan.setlim(self.arrdata[numrow])
                self.pltwind.pltdata(self.arrdata[numrow])
                self.appdata.genaprxpan.refreshdata(self.arrdata[numrow])
                self.appdata.cansavetxt()
            else:
                self.appdata.intpan.panoff()
                self.appdata.genaprxpan.panoff()
                self.pltwind.pltdata()
                self.appdata.setstatepanel(0)
                
class AddLineCommand(Command):
    def __init__(self,appdata,arrmdata,pltwind):
        self.appdata=appdata
        self.mdata=arrmdata
        self.pltwind=pltwind
        self.init=appdata.init
        
    def execute(self):
        fpath=fdial.askdirectory()
        if fpath:
            flist=os.listdir(path=fpath)
            for itt in flist:
                expan=itt.split('.')
                if expan[-1]=='txt':
                    self.getdatafile(fpath+'/'+itt)
            fp_split=fpath.split('/')
            self.appdata.title('Spectrum - '+fp_split[-1])
                                    
    def getdatafile(self,fpath):
        try:
            filesize = os.path.getsize(fpath)
            choicework=''
            fp=fpath.split('/')
            fp=fp[-1].split('.')
            kname='.'.join(fp[:-1])
            if fp[-1]!='txt':
                raise ExWrongFormat()
            f=open(fpath,'r')
            if kname[0]=='A':
                choicework='A'
            elif kname[0].isdigit():
                choicework='D'
            else:
                raise ExWrongFormat()
            curdata=f.read()
            self.workdata(curdata,choicework)
            self.addline(kname)
        except IOError:
            msgbox.showerror("Open Source File", "Failed to read file\n'%s'" % fpath)
        except ExWrongFormat:
            #msgbox.showerror("Open Source File", "Wrong type file\n'%s'" % fpath)
            pass
        except:
            #msgbox.showerror("Open Source File", "Wrong data\n'%s'" % fpath)
            pass
        else:
            f.close()
            
    def workdata(self,curdata, choicework):
        curdata=curdata.split('\n')
        self.w=[];self.i=[];self.sco=[]
        if choicework=='A':
            for itt in curdata:
                itt=itt.rstrip()
                itt=itt.replace(self.init.sepnum,'.')
                nitt=[]
                itt=itt.split(' ')
                for jj in itt:
                    if jj!='':
                        nitt.append(jj)
                if len(nitt)==3 and nitt[1][-1].isdigit():
                    self.w.append(float(nitt[1]))
                    self.i.append(float(nitt[2]))#mkA
                    self.sco.append(0)#mkA
        elif choicework=='D':
            ncolumn=len(curdata[-1].split('\t'))
            for itt in curdata:
                itt=itt.replace(self.init.sepnum,'.')
                itt=itt.split('\t')
                itt[0]=itt[0].rstrip()
                if len(itt)==4 and itt[0][-1].isdigit():
                    self.w.append(float(itt[0]))
                    self.i.append(float(itt[1]))#mkA
                    self.sco.append(0)#mkA
                elif len(itt)==5 and itt[0][-1].isdigit():
                    self.w.append(float(itt[0]))
                    self.i.append(float(itt[1]))
                    self.sco.append(float(itt[2]))

    def addline(self,kname):
        parent=self.appdata.canvtabl.frame 
        curdata=MainData([self.w,self.i,self.sco],kname)
        curline=TableLine(parent,curdata)
        cmdS=OneSelectCommand(self.appdata,curline,self.pltwind)
        cmdC=SelectComboCommand(self.appdata,curline,self.pltwind)
        curline.setcmd(cmdS,cmdC)

        self.mdata.append(curline)
        self.appdata.repacktabl()
        #Оставляем выделение на текущей строке, 
        selrow=self.appdata.oneselect()
        self.appdata.setallflag(0)
        if selrow==None:
            selrow=0
        self.mdata[selrow].setselect(1)
        #Отображаем пределы
        self.appdata.genaprxpan.refreshdata(self.mdata[selrow])
        self.appdata.intpan.setlim(self.mdata[selrow])
        self.appdata.setstatepanel(1)
        
class SelectComboCommand(Command):
    def __init__(self,appdata,mdata,pltwind):
        self.mdata=mdata
        self.appdata=appdata
        self.pltwind=pltwind
        
    def execute(self,ev=None):
        self.appdata.setallflag(0)
        self.mdata.setselect(1)
        self.appdata.intpan.setlim(self.mdata)
        if not self.mdata.accept():
            self.appdata.genaprxpan.panoff()
            self.mdata.lose_result_table()
        else:
            if self.mdata.iscalculated==False:
                self.mdata.autoaprx(self.appdata.current_method_aprx)  ##
                self.mdata.calcDens()  ##
                self.appdata.genaprxpan.refreshdata(self.mdata)
            else:
                self.appdata.genaprxpan.refreshdata(self.mdata)
                self.appdata.mainaprxcmd.execute()
        self.appdata.cansavetxt()
        self.pltwind.pltdata(self.mdata)

class OneSelectCommand(Command):
    def __init__(self,appdata,mdata,pltwind):
        self.appdata=appdata
        self.mdata=mdata
        self.pltwind=pltwind
        
    def execute(self,ev=None):
        self.appdata.setallflag(0)
        self.mdata.setselect(1)
        if self.mdata.iscalculated==False:
            self.mdata.autoaprx(self.appdata.current_method_aprx)  ##
            self.mdata.calcDens() ##

        self.pltwind.pltdata(self.mdata)
        self.appdata.intpan.setlim(self.mdata)
        self.appdata.genaprxpan.refreshdata(self.mdata)

    def execute_select_only(self,ev=None):
        if self.mdata.getselect()==0:
            self.mdata.setselect(1)
        elif self.mdata.getselect()==1:
            self.mdata.setselect(0)
        
class TableLine():
    def __init__(self,parent,indata):
        self.rowdata=indata.rowdata
        self.keyrowdata=indata.keyrowdata
        self.data=indata
        self.NUMFIELDS=self.data.NUMFIELDS
        self.table=[0]*self.NUMFIELDS
        self.NODATAROW=self.data.NODATAROW
        self.iscalculated=False
        self.status='norm'

        self.table[0]=lwd.Makeflag(parent,self.data.wid[0])
        self.table[1]=lwd.Makeentry(parent,self.data.wid[1])
        self.table[2]=lwd.Makecombobox(parent,self.data.scoll,self.data.wid[2])
        self.table[3]=lwd.Makecombobox(parent,self.data.gas,self.data.wid[3])
        self.table[4]=lwd.Makeentry(parent,self.data.wid[4])
        self.table[5]=lwd.Makeentry(parent,self.data.wid[5])
        self.table[6]=lwd.Makeentry(parent,self.data.wid[6])
        
        self.settabledata()

    def get_current_data(self):
        return copy.deepcopy(self.data.data)

    def set_current_data(self,indata):
        self.data.data=copy.deepcopy(indata)

    def calctrace(self,x):
        return self.data.calcpoint(x)
        
    def deletepoint(self,point):
        self.data.deletepoint(point)
        
    def detpoint(self,point):
        return self.data.detpoint(point)
    
    def getdata(self):
        return self.data.getdata()

    def setstate(self,val):
        self.status=val
        if val=="mult":
            if self.accept():
                self.table[0].setmultiselect(1)
            else:
                self.table[0].setmultiselect(2)
            self.table[2].setstate(0)
            self.table[3].setstate(0)
        elif val=="norm":
            self.table[0].setmultiselect(0)
            self.table[2].setstate(1)
            self.table[3].setstate(1)
        elif val=="delpoint":
            self.table[0].setmultiselect(2)
            self.table[2].setstate(0)
            self.table[3].setstate(0)
            
    def setcmd(self,incmdS,incmdC):
        self.table[0].setcmd(incmdS)
        self.table[2].setcmd(incmdC)
        self.table[3].setcmd(incmdC)       
        
    def setrowdata(self,inrowdata,inkeyrowdata):
        self.rowdata.update(inrowdata)
        self.keyrowdata.update(inkeyrowdata)
        self.settabledata()
        
    def settabledata(self):
        self.table[1].refresh(self.rowdata['kname'])
        self.table[2].refresh(self.keyrowdata['scol'])
        self.table[3].refresh(self.keyrowdata['mgas'])
        if self.rowdata['n'] != self.NODATAROW:
            self.table[4].refresh('%E'%round(self.rowdata['n'],0))
        else:
            self.table[4].refresh(self.NODATAROW)
        if self.rowdata['wavr'] != self.NODATAROW:
            self.table[5].refresh(round(self.rowdata['wavr'],2))
            self.table[6].refresh(round(self.rowdata['wmax'],2))
        else:
            self.table[5].refresh(self.NODATAROW)
            self.table[6].refresh(self.NODATAROW)
            
    def destroyGUI(self):
        for itt in self.table:     
            itt.destroy()

    def repack(self,numrow):
        self.table[0].grid(row=numrow,column=0,sticky='w'+'e'+'n'+'s',padx=1,pady=1)
        for itt in range(1,len(self.table)):
            self.table[itt].grid(row=numrow,column=itt,sticky='w'+'e'+'n'+'s',padx=1,pady=1)

    def updaterowdata(self):
        self.rowdata['kname']=self.table[1].getvalue()
        self.keyrowdata['scol'],self.rowdata['scol']=self.table[2].getvalue()
        self.keyrowdata['mgas'],self.rowdata['mgas']=self.table[3].getvalue()
            
    def accept(self):
        self.updaterowdata()
        if self.rowdata['mgas'] != self.NODATAROW  and self.rowdata['scol'] != self.NODATAROW:
            return True
        else:
            return False

    def getselect(self):
        return self.table[0].getflag()

    def setselect(self,flag):
        self.table[0].setflag(flag)
        if flag==1:
            for itt in self.table:
                itt.setbg(bg='#FFD700')
        elif flag==0:
            for itt in self.table:
                itt.setbg(bg='#fff')

    def  lose_result_table(self):
        self.table[4].refresh(self.NODATAROW)
        self.table[5].refresh(self.NODATAROW)
        self.table[6].refresh(self.NODATAROW)

    def calcDens(self):
        if self.accept():
            self.data.calcDens()
            self.iscalculated=True
            self.data.setrowdata(self.rowdata)
            self.table[1].refresh(self.rowdata['kname'])
            if self.rowdata['n'] != self.data.NODATAROW:
                self.table[4].refresh('%E'%round(self.rowdata['n'],0))
            else:
                self.table[4].refresh(self.NODATAROW)
            if self.rowdata['wavr']!= self.NODATAROW and self.rowdata['wmax']!= self.NODATAROW:
                self.table[5].refresh(round(self.rowdata['wavr'],2))
                self.table[6].refresh(round(self.rowdata['wmax'],2))
            else:
                self.table[5].refresh(self.NODATAROW)
                self.table[6].refresh(self.NODATAROW)
        else:
            self.table[4].refresh(self.NODATAROW)
            self.table[5].refresh(self.NODATAROW)
            self.table[6].refresh(self.NODATAROW)

    def autoaprx(self,aprxdata):
        if self.accept():
            self.data.autoaprx(aprxdata)

    def autocalc(self,nump=None,inputvar=None):
        if self.accept():
            return self.data.autocalc(nump,inputvar)
            
    def getaprxdata(self):
        return self.data.getaprxdata()
    
class InitData():
    NODATAROW='##'
    gas={'##':NODATAROW} #единицы: а.е.м., кратность заряда
    scoll={'##':NODATAROW}  #единицы: м^2
    filename='config.txt'
    try:
        f=open('config.txt','r')
        curdata=f.read()
        currdata=curdata.split('\n')
        flg=0
        for itt in currdata:
            if itt=='':
                continue
            elif itt[0]=='#':
                continue
            elif itt=='*Gas*' or itt=='*Scol*':
                flg=itt
                continue
            itt=itt.split(';')
            if flg=='*Gas*':
                gas[str(itt[0])]=[float(itt[1]),int(itt[2])]
            elif '*Scol*':
                scoll[str(itt[0])]=float(itt[1])
    except IOError:
        rt=tk.Tk()
        rt.withdraw()
        msgbox.showerror("Open Config File", "Failed to read config file")
        rt.destroy()
    except:
        rt=tk.Tk()
        rt.withdraw()
        msgbox.showerror("Open Config File", "Failed format config file")
        rt.destroy()
    else:
        f.close()

    def __init__(self):
        self.NUMFIELDS=7# #Количество колонок таблицы(включая колонку флага выделения строки)
        self.name=['','Кадр','Площадь \n коллектора','Газ',
                   'Плотность,\n см-3','Средняя \n энергия, эВ','Энергия \n максимума, эВ']
        self.NOROWDATA={'kname':InitData.NODATAROW,'scol':InitData.NODATAROW,'mgas':InitData.NODATAROW,
                      'n':InitData.NODATAROW,'wavr':InitData.NODATAROW,'wmax':InitData.NODATAROW}      
        self.wid=[20,60,30,3,22,13,13]
        self.sepnum=','       
        
class MainData(InitData):
    def __init__(self,data,kname):
        InitData.__init__(self)
        self.rowdata=self.NOROWDATA # Данные строки табл
        self.keyrowdata=self.NOROWDATA.copy() # Ключи данных строки табл
        self.datares={'w':[['w_э, эВ']+data[0].copy()],'i':[['icol_э, мкА']+data[1].copy()],'sco':[['sco, мкА']+data[2].copy()]}
        self.rowdata['kname']=kname
        self.approx=AppoxProc(self.rowdata)

        self.data={'w':data[0],'i':data[1],'sco':data[2]} #Данные + аппроксимированные данные+ ошибки данных
        self.limits={'max':self.data['w'][-1],'min':self.data['w'][0],'lup':self.data['w'][-1],'ldw':self.data['w'][0]}#Пределы интегрирования (и сохр. данных)

    def calcpoint(self,x):
        return self.approx.calcpoint(x)
        
    def deletepoint(self,point):
        w=self.data['w']
        i=self.data['i']
        sco=self.data['sco']
        if len(w)>1:
            del w[point[2]]
            del i[point[2]]
            del sco[point[2]]
        
    def detpoint(self,point):
        w=self.data['w']
        i=self.data['i']
        im=point[3]
        wm=point[2]
        rmin=((w[0]/wm-point[0]/wm)**2+(i[0]/im-point[1]/im)**2)**0.5
        ind=0
        for itt in range(1,len(w)):
            rcurr=((w[itt]/wm-point[0]/wm)**2+(i[itt]/im-point[1]/im)**2)**0.5
            if rmin>=rcurr:
                rmin=rcurr
                ind=itt
        return w[ind],i[ind],ind
    
    def getdata(self):
        return self.datares

    def setrowdata(self,rowdata):
        self.rowdata=rowdata
    
    def calcDens(self):
        self.approx.calcDens(self.limits)

    def autoaprx(self,aprxdata):
        self.approx.autoaprx(self,aprxdata)
    def autocalc(self,nump=None,inputvar=None):
        return self.approx.autocalc(self,nump,inputvar)
    def getaprxdata(self):
        return self.approx.getaprxdata()

class AppoxProc():
    def __init__(self,rowdata):
        self.NUMPINT=500 #Количество точек интегрироввания
        self.NUMPLT=300
        self.met='P'
        self.aprxdataP=10
        self.aprxdataS={'npintr':5,'pspl':3}
        
        self.rowdata=rowdata# Данные строки табл
        self.scoP='none' #Полное SCO метода
        self.scoS='none' #Полное SCO метода
    #Аппроксимация полиномом
        self.aprxP=[] #Вектор коэффициентов аппрокс. полинома
        self.aprxdP=[]
    #Аппроксимация сплайном
        self.aprxS=None
  
    ##Общие методы##
    def calcDens(self,limits):
        if self.met=='P':
            self.integrP(limits)
        elif self.met=='S':
            self.integrS(limits)
        else:
            raise ExNoMetAppr()
        
    def autoaprx(self,mdata,aprxdata):
        self.met=aprxdata['meth']
        if self.met=='P':
            if aprxdata['data']!=None:   
                self.aprxdataP=aprxdata['data']
            self.doaprxP(mdata)
        elif self.met=='S':
            if aprxdata['data']!=None:  
                self.aprxdataS=aprxdata['data']
            self.doaprxS(mdata)
            
    def autocalc(self,mdata,nump=None,inputvar=None):
        if nump==None:
            nump=self.NUMPLT
        if self.met=='P':
            return self.calcxP(mdata,nump,inputvar)
        elif self.met=='S':
            return self.calcxS(mdata,nump,inputvar)
        
    def calcpoint(self,x):
        if self.met=='P':
            return [self.aprxP(x),self.functFRP(x)]
        elif self.met=='S':
            return [self.aprxS.calcspl(x),self.functFRS(x)]
        
    def getaprxdata(self):
        if self.met=='P':
            aprxdata=self.aprxdataP
            sco=self.scoP
        elif self.met=='S':
            aprxdata=self.aprxdataS
            sco=self.scoS
        return {'meth':self.met,'data':aprxdata,'sco':sco}
        
    ##Методы полиномов##
    def doaprxP(self,mdata):
        xi=mdata.data['w'];yi=mdata.data['i']
        scoi=mdata.data['sco']
        fp = sp.polyfit(xi, yi, self.aprxdataP)
        self.aprxP = sp.poly1d(fp)
        self.aprxdP=sp.polyder(self.aprxP)
        self.calcxP(mdata,self.NUMPLT)
        
    def calcxP(self,mdata,nump,inputvar=None):   
        sco=0;xi=[];yi=[];scoi=[]
        xcur=mdata.data['w'];ycur=mdata.data['i']
        scocur=mdata.data['sco']
        lup=mdata.limits['lup']
        ldw=mdata.limits['ldw']
        for itt in range(len(xcur)):
            if xcur[itt]<=lup and xcur[itt]>=ldw:
                xi.append(xcur[itt])
                yi.append(ycur[itt])
                scoi.append(scocur[itt])
        for itt in range(len(xi)):
            if scoi[itt]!=0:
                sco+=((yi[itt]-self.aprxP(xi[itt]))/scoi[itt])**2
            elif scoi[itt]==0:
                sco+=((yi[itt]-self.aprxP(xi[itt])))**2
        self.scoP=sco**0.5
        
        linew=np.linspace(mdata.limits['ldw'],mdata.limits['lup'],nump)
        linei=self.aprxP(linew)
        linedi=self.functFRP(linew)
        if inputvar!=None:
            return [['w_a, эВ']+linew.tolist(),['icol_a, мкА']+linei.tolist(),['f(w)_a, отн.ед']+linedi]
        else:
            mdata.data.update({'aw':linew,'ai': linei,'adi': linedi})
            #Вычисление интервалов полиномов 
            mdata.data['intsw']=[mdata.limits['min'],mdata.limits['max']]
            mdata.data['intsi']=self.aprxP(mdata.data['intsw'])
            mdata.data['intsdi']=self.functFRP(mdata.data['intsw'])
        indmax=max(enumerate(linedi), key= lambda x: x[1])
        self.rowdata['wmax']=linew[indmax[0]]
        
    def functFRP(self,x):
        mgas=self.rowdata['mgas'][0]*AEM
        scol=self.rowdata['scol']
        nq=self.rowdata['mgas'][1]*QE
        try:
            fr=[]
            for itt in x:
                fr.append(-self.aprxdP(itt)*(mgas*nq/2/itt)**0.5/nq/nq/scol*1e-12)
            for itt in range(len(x)):
                if fr[itt]<=0:
                    fr[itt]=0
        except TypeError:
            fr=-self.aprxdP(x)*(mgas*nq/2/x)**0.5/nq/nq/scol*1e-12
            if fr<=0:
                fr=0
        return fr
    
    def integrP(self,limits):
        def functwavr(x):
            return x*self.functFRP(x)
        
        self.rowdata['n']=myf.intSims([limits['ldw'],
                                    limits['lup']],self.NUMPINT,self.functFRP)
        if self.rowdata['n']==0:
            wavr=limits['ldw']
        else:
            wavr=myf.intSims([limits['ldw'],
                                    limits['lup']],self.NUMPINT,functwavr)/self.rowdata['n']
        self.rowdata['wavr']=wavr
        
    ##Методы B-сплайов##
    def doaprxS(self,mdata,weigt=None):
        xi=mdata.data['w']
        yi=mdata.data['i']
        scoi=mdata.data['sco']
        self.aprxS=myf.B_Spline(xi,yi,npintr=self.aprxdataS['npintr'],pspl=self.aprxdataS['pspl'],w=weigt)
        self.calcxS(mdata,self.NUMPLT)
        
    def calcxS(self,mdata,nump,inputvar=None):
        sco=0;xi=[];yi=[];scoi=[]
        xcur=mdata.data['w'];ycur=mdata.data['i']
        scocur=mdata.data['sco']
        lup=mdata.limits['lup']
        ldw=mdata.limits['ldw']
        for itt in range(len(xcur)):
            if xcur[itt]<=lup and xcur[itt]>=ldw:
                xi.append(xcur[itt])
                yi.append(ycur[itt])
                scoi.append(scocur[itt])
        for itt in range(len(xi)):
            if scoi[itt]!=0:
                sco+=((yi[itt]-self.aprxS.calcspl(xi[itt]))/scoi[itt])**2
            elif scoi[itt]==0:
                sco+=((yi[itt]-self.aprxS.calcspl(xi[itt])))**2
        self.scoS=sco**0.5
        linew=np.linspace(mdata.limits['ldw'],mdata.limits['lup'],nump)
        linei=self.aprxS.calcspl(linew)
        linedi=self.functFRS(linew)
        if inputvar!=None:
            return [['w_a, эВ']+linew.tolist(),['icol_a, мкА']+linei.tolist(),['f(w)_a, отн.ед']+linedi]
        else:
            mdata.data.update({'aw':linew,'ai': linei,'adi': linedi})
            mdata.data['intsw']=self.aprxS.getintervals()
            mdata.data['intsi']=self.aprxS.calcspl(mdata.data['intsw'])
            mdata.data['intsdi']=self.functFRS(mdata.data['intsw'])
        indmax=max(enumerate(linedi), key= lambda x: x[1])
        self.rowdata['wmax']=linew[indmax[0]]
        
    def functFRS(self,x):
        mgas=self.rowdata['mgas'][0]*AEM
        scol=self.rowdata['scol']
        nq=self.rowdata['mgas'][1]*QE
        try:
            fr=[]
            for itt in x:
                fr.append(-self.aprxS.calcderspl(itt)*(mgas*nq/2/itt)**0.5/nq/nq/scol*1e-12)
            for itt in range(len(x)):
                if fr[itt]<=0:
                    fr[itt]=0
        except TypeError:
            fr=-self.aprxS.calcderspl(x)*(mgas*nq/2/x)**0.5/nq/nq/scol*1e-12
            if fr<=0:
                fr=0
        return fr
    
    def integrS(self,limits):
        n0=1
        mgas=self.rowdata['mgas']
        scol=self.rowdata['scol']
        def functavrg(x):
            return x*self.functFRS(x)
        
        self.rowdata['n']=myf.intSims([limits['ldw'],
                                    limits['lup']],self.NUMPINT,self.functFRS)
        if self.rowdata['n']>1:
            n0=self.rowdata['n']
        wavr=myf.intSims([limits['ldw'],
                                    limits['lup']],self.NUMPINT,functavrg)/n0
        if np.isnan(wavr):
            wavr=limits['ldw']
        self.rowdata['wavr']=wavr

class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.tk_setPalette(background='#EEFFE0')
        self.title('Spectrum')
        self.protocol("WM_DELETE_WINDOW", self.onclosing)
        self.bind("<FocusIn>", self.onAppFocusIn)
        self.bind("<FocusOut>", self.onAppFocusOut)
        self.geometry('600x600')
        # Списки данных...
        self.current_method_aprx={'meth':'P','data':10}
        self.init=InitData()
        self.mdata=[]
        #Создание панели, таблицы, заголовка...
        self.canvtabl=lwd.CreateCanvTable(self)
        self.pan=lwd.MyPan(self) #Указатель на панель кнопок
        self.fastpan=lwd.FastPan(self)
        self.genaprxpan=lwd.GeneralAprxPan(self)#Указатель на панель апр.
        self.intpan=lwd.MyIntgrPan(self)#Указатель на панель интегрирования
        self.appmenu= lwd.AppMenu(self)
        self.pltwind=lwd.PlotWindow(self)#Создаем окно графика

        #Размещение панели, таблицы, заголовка...
        self.canvtabl.grid(row=0,column=1,columnspan=3,sticky='w'+'e'+'s'+'n',pady=5)
        self.pan.grid(row=0,column=0,sticky='s'+'n')
        self.genaprxpan.grid(row=1,column=1,columnspan=4,sticky='w'+'e'+'s'+'n',pady=0,padx=10)
        self.fastpan.grid(row=1,column=0,rowspan=2,sticky='s'+'n',pady=5)
        self.intpan.grid(row=2,column=1,columnspan=4,sticky='w'+'e'+'s'+'n',pady=10,padx=10)

        self.columnconfigure(0,weight=0)
        self.columnconfigure(1,weight=8)
        self.columnconfigure(2,weight=8)
        self.columnconfigure(3,weight=8)
        self.rowconfigure(0,weight=8)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
       
        #Создание объектов комманд
        addlinecmd=AddLineCommand(self,self.mdata,self.pltwind)
        dellinecmd=DelLineCommand(self,self.mdata,self.pltwind)
        clearallcmd=ClearAllCommand(self,self.mdata,self.pltwind)
        savearrcmd=SaveArrCommand(self,self.mdata)
        self.mainaprxcmd=AprxCommand(self,self.mdata,self.pltwind)
        getlimcmd=GetLimitsCommand(self,self.mdata,self.pltwind)
        savetxtcmd=SaveTxtCommand(self,self.mdata,self.pltwind)
        loadarrcmd=LoadArrCommand(self,self.mdata,self.pltwind)
        setallcmd=SetAllCommand(self,self.mdata,self.pltwind)
        delpointcmd=DelPointCommand(self,self.mdata,self.pltwind)
        tracepointcmd=TraceCommand(self,self.mdata,self.pltwind)
        copykzfrcmd=CopykzfrCommand(self.pltwind)
        copytablcmd=CopytableCommand(self,self.mdata)
        copydatcmd=CopydataCommand(self,self.mdata)
        #Устанавливаем события
        pancmd={'del':dellinecmd,'add':addlinecmd,'clear':clearallcmd,'savearr':savearrcmd,
                    'load':loadarrcmd,'savetxt':savetxtcmd,
                    'quit':self.onclosing,'setall':setallcmd}
        fastpancmd={'kzfr':copykzfrcmd,'tabl':copytablcmd,'dat':copydatcmd}
        self.fastpan.setcmd(fastpancmd) 
        self.pan.setcmd(pancmd)  
        self.intpan.setcmd(getlimcmd)
        self.genaprxpan.setcmd(self.mainaprxcmd)
        self.appmenu.setfilecmd(pancmd)
        self.pltwind.setdelpcmd(delpointcmd)
        self.pltwind.settracecmd(tracepointcmd)
        
    def onAppConfigure(self,ev=None):
        self.pltwind.setposition()
            
    def onAppFocusIn(self,ev=None):
        self.bind("<Configure>", self.onAppConfigure)
        
    def onAppFocusOut(self,ev=None):
        self.unbind("<Configure>")
        
    def onclosing(self):
        self.pltwind.delfigure()
        self.destroy()

    def repacktabl(self):
        for jj in range(len(self.mdata)):    
            self.mdata[jj].repack(jj)
        for itt in range(1,self.init.NUMFIELDS):
            self.canvtabl.frame.columnconfigure(itt,weight=1)
    
    def detallselect(self):
        numrow=[]       
        for itt in range(len(self.mdata)):
            if self.mdata[itt].getselect() == 1:
                numrow.append(itt)
        return numrow
    
    def cansavetxt(self):
        flg=False
        for itt in self.mdata:
            if itt.accept():
                flg=True
                break
        if flg:
            self.pan.cansave(1)
            self.appmenu.cansave(1)
            self.fastpan.setstateall(1)
        else:
            self.pan.cansave(0)
            self.appmenu.cansave(0)
            self.fastpan.setstateall(0)

    def setstatepanel(self,val):
        self.pan.setstate(val)
        self.appmenu.setstate(val)
        
    def setstatepanelall(self,val):
        self.pan.setstateall(val)
        self.appmenu.setstateall(val)
        
    def oneselect(self):
        selr=self.detallselect()
        if len(selr)==1:
            return selr[0]
        else:
            return None
    
    def setallflag(self,flag):
        for itt in self.mdata:
            itt.setselect(flag)
       
if __name__ == "__main__":
    appl = MyApp()
    appl.mainloop()

