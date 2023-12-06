import copy
import tkinter as tk
import tkinter.ttk as ttk

import matplotlib.pylab as plt
from matplotlib import rcParams

rcParams["font.family"] = "Times Уравнение_переноса Roman"
rcParams["font.size"] = "15"
import tkinter.filedialog as fdial

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BG = "#45CEA2"
abg = "#EEFFE0"


class CreateCanvTable(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg=BG)
        self.title = MyTitleTabl(self, parent)
        self.title.pack(side="top", fill="x")
        self.vsb = tk.Scrollbar(self, orient="vertical", bg=BG)
        self.vsb.pack(side="right", fill="y")
        self.title.setwidth(-1, self.vsb.winfo_reqwidth())

        self.canvas = tk.Canvas(
            self, yscrollcommand=self.vsb.set, bd=0, highlightthickness=0, bg=BG
        )
        self.vsb.config(command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg=BG)
        self.frame_id = self.canvas.create_window(0, 0, window=self.frame, anchor="nw")
        self.canvas.pack(side="top", fill="both", expand=1)

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onFrameConfigure)
        parent.bind("<MouseWheel>", self.onMouseWheel)
        self.parent = parent

    def onFrameConfigure(self, event=None):
        self.canvas.itemconfig(self.frame_id, width=event.width)
        self.parent.update()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onMouseWheel(self, ev=None):
        if self.frame.winfo_height() >= self.canvas.winfo_height():
            self.canvas.yview_scroll(-1 * int(ev.delta / 100), "units")


class MyTitleTabl(tk.Frame):
    def __init__(self, parent, appdata):
        tk.Frame.__init__(self, parent, bg=BG)
        self.appdata = appdata
        self.init = appdata.init

        self.titletabl = []
        self.titletabl.append(tk.Frame(self, width=self.init.wid[0] + 2))
        self.titletabl[0].grid(row=0, column=0, sticky="e" + "w" + "n" + "s")

        for itt in range(1, self.init.NUMFIELDS):
            self.titletabl.append(
                self.makelabel(
                    self, h=30, w=self.init.wid[itt], intext=self.init.name[itt]
                )
            )
            self.titletabl[itt].grid(
                row=0, column=itt, sticky="n" + "s" + "e" + "w", padx=1, pady=1
            )
            self.columnconfigure(itt, weight=1)

        self.titletabl.append(tk.Frame(self, width=2))
        self.titletabl[-1].grid(
            row=0, column=self.init.NUMFIELDS + 1, sticky="e" + "w" + "n" + "s"
        )

    def makelabel(self, parent, h, w, intext):
        frame = tk.Frame(parent, height=h, width=w)
        frame.pack_propagate(0)
        label = tk.Label(frame, text=intext, anchor="w")
        label.pack()
        return frame

    def setwidth(self, num, w):
        self.titletabl[num].config(width=w)


class Makecombobox(tk.Frame):
    def __init__(self, parent, dictionary, w=100):
        self.dict = dictionary
        tk.Frame.__init__(self, parent, height=20, width=w, bg="#fff")
        self.pack_propagate(0)
        self.cmbox = ttk.Combobox(self, state="readonly")
        self.cmbox.config(values=list(self.dict.keys()))
        self.cmbox.current(0)
        self.cmbox.pack(expand=1, fill=tk.BOTH)
        self.cmbox.bind("<MouseWheel>", self.onMouseWheel)

    def setstate(self, val):
        if val == 1:
            self.cmbox.config(state="readonly")
        elif val == 0:
            self.cmbox.config(state="disabled")

    def getvalue(self):
        return self.cmbox.get(), self.dict[self.cmbox.get()]

    def refresh(self, inval):
        self.cmbox.set(inval)

    def setcmd(self, incomm):
        self.cmbox.bind("<<ComboboxSelected>>", incomm.execute)

    def onMouseWheel(self, ev=None):
        return "break"

    def setbg(self, bg):
        pass


class Makeflag(tk.Frame):
    def __init__(self, parent, w):
        self.isselected = True
        tk.Frame.__init__(self, parent, height=20, width=w, bg="#fff")
        self.pack_propagate(0)
        self.flag = tk.IntVar()
        self.chbut = tk.Checkbutton(
            self, bg="#fff", variable=self.flag, state=tk.DISABLED
        )
        self.chbut["disabledforeground"] = "#000"
        self.chbut.place(anchor="w", relx=-0.1, rely=0.4)
        self.setmultiselect(0)

    def setmultiselect(self, inval):
        if inval == 1:
            self.isselected = True
            self.chbut.bind("<Button-1>", self.inexecute_select_only)
            self.chbut.bind("<ButtonRelease-1>", "")
        elif inval == 0:
            self.isselected = True
            self.chbut.bind("<Button-1>", self.inexecute)
            self.chbut.bind("<ButtonRelease-1>", self.onCommrelise)
        elif inval == 2:
            self.isselected = False
            self.chbut.bind("<Button-1>", "")
            self.chbut.bind("<ButtonRelease-1>", "")

    def setbg(self, bg):
        self.chbut.config(bg=bg)

    def setcmd(self, incomm):
        self.cmd = incomm.execute
        self.cmd_sel_only = incomm.execute_select_only

    def inexecute(self, ev=None):
        self.cmd()

    def inexecute_select_only(self, ev=None):
        self.cmd_sel_only()

    def onCommrelise(self, ev=None):
        self.flag.set(1)

    def getflag(self):
        return self.flag.get()

    def setflag(self, value):
        if self.isselected:
            self.flag.set(value)


class Makeentry(tk.Frame):
    def __init__(self, parent, w=None, indata="", font=None):
        if w == None:
            w = 10
        tk.Frame.__init__(self, parent, height=20, width=w, bg="#fff")
        self.pack_propagate(0)
        self.entry = tk.Entry(self, bg="#fff")
        if font != None:
            self.entry.config(font=font)
        self.entry.pack(expand=1, fill=tk.BOTH)
        self.entry.bind("<Any-KeyRelease>", self.nokeypress)
        self.data = indata

    def setbg(self, bg):
        self.entry.config(bg=bg)

    def nokeypress(self, ev=None):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.data)

    def refresh(self, dataentry):
        self.data = dataentry
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.data)

    def getvalue(self):
        return self.entry.get()

    def panactiv(self):
        self.entry.config(state=tk.NORMAL)

    def panoff(self):
        self.refresh("")
        self.entry.config(state=tk.DISABLED)


class FastPan(tk.Frame):
    def __init__(self, parent):
        wbut = 12
        self.parent = parent
        tk.Frame.__init__(self, parent, width=100, height=20)
        cont = tk.Frame(self)
        self.butcopykz = tk.Button(
            cont, text="Скопировать\nкр. задерж.", width=wbut, activebackground=abg
        )
        self.butcopyfr = tk.Button(
            cont, text="Скопировать\nфункц. распред.", width=wbut, activebackground=abg
        )
        self.butcopytabl = tk.Button(
            cont, text="Скопировать\nтаблицу", width=wbut, activebackground=abg
        )
        self.butcopydat = tk.Button(
            cont,
            text="Скопировать\nаппрокс.",
            width=wbut,
            height=2,
            activebackground=abg,
        )
        self.butcopykz.grid(row=1, column=0, pady=10)
        self.butcopyfr.grid(row=0, column=0)
        self.butcopytabl.grid(row=2, column=0)
        self.butcopydat.grid(row=3, column=0, pady=10)

        cont.columnconfigure(0, weight=1)
        cont.place(anchor="e", relx=0.98, rely=0.5)
        self.setstateall(0)

    def setstateall(self, state):
        if state == 1:
            self.butcopykz.config(state="active")
            self.butcopyfr.config(state="active")
            self.butcopytabl.config(state="active")
            self.butcopydat.config(state="active")
        elif state == 0:
            self.butcopykz.config(state="disabled")
            self.butcopyfr.config(state="disabled")
            self.butcopytabl.config(state="disabled")
            self.butcopydat.config(state="disabled")

    def setcmd(self, incomm):
        self.butcopykz.config(command=incomm["kzfr"].savekz)
        self.butcopyfr.config(command=incomm["kzfr"].savefw)
        self.butcopytabl.config(command=incomm["tabl"].execute)
        self.butcopydat.config(command=incomm["dat"].execute)


class MyPan(tk.Frame):
    def __init__(self, parent):
        wbut = 10
        self.parent = parent
        tk.Frame.__init__(self, parent, width=85, height=20)
        cont = tk.Frame(self)
        self.butadd = tk.Button(cont, text="Добавить", width=wbut, activebackground=abg)
        self.butdel = tk.Button(cont, text="Удалить", width=wbut, activebackground=abg)
        self.butdelall = tk.Button(
            cont, text="Очистить", width=wbut, activebackground=abg
        )
        self.butsavearr = tk.Button(
            cont,
            text="Сохранить \nв архив...",
            width=wbut,
            height=2,
            activebackground=abg,
        )
        self.butsavetxt = tk.Button(
            cont,
            text="Сохранить в \nтекст. файл...",
            width=wbut,
            height=2,
            activebackground=abg,
        )
        self.butload = tk.Button(
            cont, text="Загрузить...", width=wbut, activebackground=abg
        )

        self.butdel.grid(row=1, column=0, pady=10)
        self.butadd.grid(row=0, column=0)
        self.butdelall.grid(row=2, column=0)
        self.butsavearr.grid(row=3, column=0, pady=10)
        self.butsavetxt.grid(row=4, column=0)
        self.butload.grid(row=5, column=0, pady=10)
        cont.columnconfigure(0, weight=1)
        cont.place(anchor="e", relx=0.98, rely=0.5)
        self.setstate(0)
        self.cansave(0)

    def setcmd(self, incomm):
        self.butadd.config(command=incomm["add"].execute)
        self.butdel.config(command=incomm["del"].execute)
        self.butdelall.config(command=incomm["clear"].execute)
        self.butsavearr.config(command=incomm["savearr"].execute)
        self.butload.config(command=incomm["load"].execute)
        self.butsavetxt.config(command=incomm["savetxt"].execute)

    def setstate(self, state):
        if state == 1:
            self.butdel.config(state="active")
            self.butdelall.config(state="active")
            self.butsavearr.config(state="active")
        elif state == 0:
            self.butdel.config(state="disabled")
            self.butdelall.config(state="disabled")
            self.butsavetxt.config(state="disabled")
            self.butsavearr.config(state="disabled")

    def setstateall(self, state):
        if state == 1:
            self.butdel.config(state="active")
            self.butdelall.config(state="active")
            self.butsavearr.config(state="active")
            self.butsavetxt.config(state="active")
            self.butadd.config(state="active")
            self.butload.config(state="active")
        elif state == 0:
            self.butdel.config(state="disabled")
            self.butdelall.config(state="disabled")
            self.butsavetxt.config(state="disabled")
            self.butsavearr.config(state="disabled")
            self.butadd.config(state="disabled")
            self.butload.config(state="disabled")

    def cansave(self, val):
        if val == 0:
            self.butsavetxt.config(state="disabled")
        elif val == 1:
            self.butsavetxt.config(state="normal")


class SetAllDialog(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        self.init = parent.init

        tk.Toplevel.__init__(self, parent)
        self.title("Установить значения")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.onclosing)
        wid = 10

        self.cbgas = Makecombobox(self, dictionary=self.init.gas)
        self.cbscol = Makecombobox(self, dictionary=self.init.scoll)
        self.butok = tk.Button(self, text="Ok", width=wid)
        butcancel = tk.Button(self, text="Отмена", width=wid, command=self.onCancel)
        lscol = tk.Label(self, text="Площадь коллектора", anchor="w")
        lgas = tk.Label(self, text="Газ", anchor="e")

        self.butok.grid(row=2, column=0, padx=5, pady=10)
        butcancel.grid(row=2, column=1, padx=5, pady=10)
        lgas.grid(row=0, column=0)
        lscol.grid(row=1, column=0)
        self.cbgas.grid(row=0, column=1, pady=5, padx=5)
        self.cbscol.grid(row=1, column=1, pady=5, padx=5)

        self.withdraw()

    def setcmd(self, incmd):
        self.cmd = incmd
        self.butok.config(command=self.onOk)

    def onOk(self):
        inkeyrowdata = {}
        inrowdata = {}
        inkeyrowdata["mgas"], inrowdata["mgas"] = self.cbgas.getvalue()
        inkeyrowdata["scol"], inrowdata["scol"] = self.cbscol.getvalue()
        self.cmd(inrowdata, inkeyrowdata)
        self.withdraw()

    def onCancel(self):
        self.withdraw()

    def setposition(self):
        self.update_idletasks()
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        wpar = self.parent.winfo_width()
        hpar = self.parent.winfo_height()
        wself = self.winfo_width()
        hself = self.winfo_height()
        self.geometry("+%d+%d" % (x + wpar / 2 - wself / 2, y + hpar / 2 - hself / 2))
        self.deiconify()
        self.focus_set()

    def onclosing(self):
        self.withdraw()


class CheckLabelBut(tk.Frame):
    def __init__(self, parent, text, cmd=None):
        self.cmd = cmd
        tk.Frame.__init__(self, parent)
        self.flag = tk.IntVar()
        self.chframe = tk.Frame(self, height=15, width=15)
        self.chframe.pack_propagate(0)
        self.chb = tk.Checkbutton(self.chframe, variable=self.flag, command=cmd)
        self.chb.place(anchor="w", relx=-0.05, rely=0.45)
        self.chframe.pack(side="left")
        self.lbl = tk.Label(self, text=text, anchor="w")
        self.lbl.pack(side="left")
        self.lbl.bind("<ButtonPress>", self.onClickLabel)
        self.flag.set(1)

    def onClickLabel(self, ev=None):
        if self.flag.get() == 1:
            self.flag.set(0)
        else:
            self.flag.set(1)
        self.cmd()

    def getflag(self):
        return self.flag.get()

    def setflag(self, val):
        self.flag.set(val)

    def setcmd(self, incmd):
        self.chb.config(command=incmd)
        self.lbl.bind("<ButtonPress>", incmd)


class EntrySaveTxt(tk.Frame):
    def __init__(self, parent, title, limits):
        self.limits = limits
        tk.Frame.__init__(self, parent)
        self.entr = tk.Entry(self, width=5, bg="#fff", selectbackground=BG)
        self.entr.pack(side="right")
        tk.Label(self, text=title, anchor="e").pack(side="right")
        self.entr.bind("<Any-KeyRelease>", self.onKeyPress)
        self.entr.delete(0, tk.END)
        self.entr.insert(0, self.limits[2])

    def onKeyPress(self, ev=None):
        data = self.entr.get()
        if not data.isdigit() and data != "":
            self.entr["bg"] = "red"
            result = ""
            for itt in self.entr.get():
                if itt.isdigit():
                    result += itt
            self.entr.delete(0, tk.END)
            self.entr.insert(0, result)
        else:
            self.entr["bg"] = "white"

    def getdata(self):
        try:
            result = int(self.entr.get())
        except ValueError:
            result = self.limits[2]
        if result < self.limits[0]:
            result = self.limits[0]
        elif result > self.limits[1]:
            result = self.limits[1]
        self.entr.delete(0, tk.END)
        self.entr.insert(0, result)
        return result

    def setdata(self):
        pass

    def statepan(self, state):
        if state == 1:
            self.entr.config(state="normal")
        elif state == 0:
            self.entr.config(state="disabled")


class SaveTxtDialog(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        tk.Toplevel.__init__(self, parent)
        self.title("Сохраниить в текстовый файл")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.onclosing)
        wid = 10

        panwsave = tk.LabelFrame(self)
        self.chaprx = CheckLabelBut(panwsave, "Аппроксимация", cmd=self.onCheck)
        self.cherr = CheckLabelBut(panwsave, "Ошибка", cmd=self.onCheck)
        self.chdat = CheckLabelBut(panwsave, "Данные", cmd=self.onCheck)

        self.butok = tk.Button(self, text="Ok", width=wid)
        butcancel = tk.Button(self, text="Отмена", width=wid, command=self.onclosing)
        self.inpnt = EntrySaveTxt(
            panwsave, "Число точек аппроксимации: ", [2, 1000, 300]
        )
        self.butselectall = tk.Button(panwsave, text="Выбрать все", width=wid)
        self.butunselectall = tk.Button(panwsave, text="Очистить", width=wid)

        panwsave.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w" + "e")
        # self.chaprx.grid(row=0,column=0,padx=5,pady=3,sticky='w')
        # self.cherr.grid(row=1,column=0,padx=5,sticky='w')
        # self.chdat.grid(row=2,column=0,padx=5,pady=3,sticky='w')
        self.butselectall.grid(row=0, column=0, columnspan=2, padx=10, pady=15)
        self.butunselectall.grid(row=0, column=2, columnspan=2, padx=10, pady=15)
        self.inpnt.grid(
            row=1, column=1, columnspan=2, padx=10, pady=15, sticky="s" + "w"
        )

        self.butok.grid(row=1, column=0, padx=5, pady=10)
        butcancel.grid(row=1, column=1, padx=5, pady=10)
        self.withdraw()

    def onCheck(self, ev=None):
        if self.chaprx.getflag() == 0:
            self.inpnt.statepan(0)
        elif self.chaprx.getflag() == 1:
            self.inpnt.statepan(1)

    def setcmd(self, incmd):
        self.cmd = incmd["save"]
        self.butselectall.config(command=incmd["sel"])
        self.butunselectall.config(command=incmd["unsel"])
        self.normcmd = incmd["norm"]
        self.butok.config(command=self.onOk)

    def onOk(self):
        wsave = {"a": 1, "e": 0, "d": 0}
        np = self.inpnt.getdata()
        self.cmd(np, wsave)

    def setposition(self):
        self.update_idletasks()
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        wpar = self.parent.winfo_width()
        hpar = self.parent.winfo_height()
        wself = self.winfo_width()
        hself = self.winfo_height()
        self.geometry("+%d+%d" % (x + wpar, y + hpar / 2 - hself / 2))
        self.deiconify()
        self.focus_set()

    def onclosing(self):
        self.normcmd()
        self.withdraw()


class PanelEntry(tk.Frame):
    def __init__(self, parent, title, limits):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=title)
        label.pack(side=tk.LEFT)
        self.entr = tk.Entry(self, font="15", width=5, selectbackground=BG, bg="#fff")
        self.entr.pack(side=tk.LEFT)
        self.entr.bind("<Any-KeyRelease>", self.nosymbpress)
        self.limits = limits

    def nosymbpress(self, ev=None):
        data = self.entr.get()
        result = data
        if not data.isdigit() and data != "":
            result = ""
            for itt in data:
                if itt.isdigit():
                    result += itt
        self.entr.delete(0, tk.END)
        self.entr.insert(0, result)

        if ev.keysym == "Return":
            if result == "":
                result = self.limits[0]
            elif int(result) > self.limits[1]:
                result = self.limits[1]
            elif int(result) < self.limits[0]:
                result = self.limits[0]
            self.var = result
            self.entr.delete(0, tk.END)
            self.entr.insert(0, result)
            self.incmd()
            self.entr.focus_set()

    def setdata(self, intext):
        self.entr.delete(0, tk.END)
        self.entr.insert(0, intext)
        self.var = intext

    def getdata(self):
        return self.entr.get()

    def setcmd(self, incmd):
        self.incmd = incmd

    def panoff(self):
        self.entr.config(state=tk.DISABLED)

    def panactiv(self):
        self.entr.config(state=tk.NORMAL)

    def hide(self):
        self.pack_forget()


class AprxPanS(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.snpint = PanelEntry(self, "Число точек в интервале: ", [2, 10])
        self.snspl = PanelEntry(self, "Порядок сплайна:              ", [3, 5])
        self.snpint.pack(expand=1)
        self.snspl.pack(expand=1)

    def setcmd(self, incmd):
        self.snpint.setcmd(incmd)
        self.snspl.setcmd(incmd)

    def panoff(self):
        self.snpint.panoff()
        self.snspl.panoff()

    def panactiv(self):
        self.snpint.panactiv()
        self.snspl.panactiv()

    def hide(self):
        self.pack_forget()

    def show(self):
        self.pack(fill=tk.BOTH, expand=1)

    def getdata(self):
        try:
            return {
                "pspl": int(self.snspl.getdata()),
                "npintr": int(self.snpint.getdata()),
            }
        except:
            return None

    def setdata(self, data):
        self.snspl.setdata(data["pspl"])
        self.snpint.setdata(data["npintr"])


class AprxPanP(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.sp = PanelEntry(self, "Степень полинома: ", [1, 25])
        self.sp.pack(expand=1)

    def show(self):
        self.pack(fill=tk.BOTH, expand=1)

    def getdata(self):
        try:
            return int(self.sp.getdata())
        except:
            return None

    def hide(self):
        self.pack_forget()

    def panoff(self):
        self.sp.panoff()

    def setcmd(self, incmd):
        self.sp.setcmd(incmd)

    def panactiv(self):
        self.sp.panactiv()

    def setdata(self, data):
        self.sp.setdata(data)


# Класс общей панели аппроксимации
# Может включать несколько методов аппр.
class GeneralAprxPan(tk.Frame):
    def __init__(self, parent):
        self.appdata = parent
        tk.Frame.__init__(self, parent)
        frAp = tk.LabelFrame(self, text="Панель аппроксимации", height=70)
        frAp.pack_propagate(0)
        frSel = tk.Frame(self)
        frSel.grid(column=1, row=0, padx=10, sticky="w" + "e" + "n" + "s")
        frAp.grid(column=0, row=0, sticky="w" + "e" + "n" + "s")

        self.columnconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.panP = AprxPanP(frAp)
        self.panS = AprxPanS(frAp)

        self.dict = {"Полином": "P", "B-cплайн": "S"}
        self.dictrev = {"P": "Полином", "S": "B-cплайн"}
        self.cmbselectaprx = ttk.Combobox(
            frSel, width=10, state="readonly", values=list(self.dict.keys())
        )
        self.cmbselectaprx.bind("<<ComboboxSelected>>", self.do_aprx_cmd)
        self.panP.setcmd(self.do_aprx_cmd)
        self.panS.setcmd(self.do_aprx_cmd)
        self.entrsco = Makeentry(frSel, w=10)
        tk.Label(frSel, text="СКО аппроксимации КЗ:").grid(
            column=0, row=0, sticky="w" + "e"
        )
        self.entrsco.grid(column=0, row=1, sticky="w" + "e")
        tk.Label(frSel, text="Тип аппроксимации:").grid(
            column=0, row=2, sticky="w" + "e"
        )
        self.cmbselectaprx.grid(column=0, row=3, columnspan=2, sticky="w" + "e")
        self.panoff()

    def getdata(self):
        aprxtype = self.dict[self.cmbselectaprx.get()]
        if aprxtype == "S":
            return {"meth": aprxtype, "data": self.panS.getdata()}
        elif aprxtype == "P":
            return {"meth": aprxtype, "data": self.panP.getdata()}

    def setcmd(self, incmd):
        self.in_do_aprx_cmd = incmd

    def do_aprx_cmd(self, ev=None):
        self.appdata.current_method_aprx = self.getdata()
        self.in_do_aprx_cmd.execute()

    def refreshdata(self, aprxdata):
        self.allpanelshide()
        self.panactive()
        aprxdata = mdata.getaprxdata()
        self.entrsco.refresh(aprxdata["sco"])
        if aprxdata["meth"] == "S":
            self.panS.show()
            self.panS.setdata(aprxdata["data"])
        elif aprxdata["meth"] == "P":
            self.panP.show()
            self.panP.setdata(aprxdata["data"])
        self.cmbselectaprx.set(self.dictrev[aprxdata["meth"]])
        if not (mdata.accept()):
            self.panoff()

    def refreshdata(self, mdata):
        self.allpanelshide()
        self.panactive()
        aprxdata = mdata.getaprxdata()
        self.entrsco.refresh(aprxdata["sco"])
        if aprxdata["meth"] == "S":
            self.panS.show()
            self.panS.setdata(aprxdata["data"])
        elif aprxdata["meth"] == "P":
            self.panP.show()
            self.panP.setdata(aprxdata["data"])
        self.cmbselectaprx.set(self.dictrev[aprxdata["meth"]])
        if not (mdata.accept()):
            self.panoff()

    def allpanelshide(self):
        self.panS.hide()
        self.panP.hide()

    def panoff(self):
        self.cmbselectaprx.config(state=tk.DISABLED)
        self.panP.panoff()
        self.panS.panoff()

    def panactive(self):
        self.panS.panactiv()
        self.panP.panactiv()
        self.cmbselectaprx.config(state="readonly")


class IntegrScale(tk.Frame):
    def __init__(self, parent, sctype, intext):
        self.TYPEDW = "dw"
        self.sctype = sctype
        tk.Frame.__init__(self, parent)
        self.labl = tk.Label(self, text=intext)
        self.labl.grid(row=0, column=0, columnspan=2, sticky="w" + "e" + "s" + "n")

        self.entr = tk.Entry(self, width=8, font="15", selectbackground=BG, bg="#fff")
        self.entr.grid(row=1, column=0, sticky="w" + "e" + "s" + "n")

        self.scale = tk.Scale(
            self,
            orient=tk.HORIZONTAL,
            length=200,
            sliderlength=20,
            showvalue=0,
            resolution=0.5,
            command=self.onscale,
            bg=BG,
        )
        self.scale.grid(row=1, column=1, sticky="w" + "e" + "s" + "n")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.entr.bind("<Any-KeyRelease>", self.nosymbpress)
        self.scale.bind("<ButtonRelease-1>", self.onreleasescale)
        self.curpos = 0

        self.inlim = 0
        self.max = 0
        self.outlim = 0
        self.min = 0

    def setcmd(self, incmd):
        self.incmd = incmd

    def panoff(self):
        self.entr.delete(0, tk.END)
        self.entr.config(state=tk.DISABLED)
        self.scale.set(-1)
        self.scale.config(state=tk.DISABLED)

    def panon(self):
        self.entr.config(state=tk.NORMAL)
        self.scale.config(state=tk.NORMAL)
        self.entr.delete(0, tk.END)
        self.entr.insert(0, self.inlim)

        self.scale.config(from_=self.min, to=self.max)
        self.scale.set(self.inlim)
        self.entr.icursor(self.curpos)

    def setlim(self, lims):
        if self.sctype == self.TYPEDW:
            self.outlim = round(lims["lup"], 2)
            self.inlim = round(lims["ldw"], 2)
        else:
            self.inlim = round(lims["lup"], 2)
            self.outlim = round(lims["ldw"], 2)
        self.max = round(lims["max"], 2)
        self.min = round(lims["min"], 2)

    def getlim(self):
        return self.inlim

    def nosymbpress(self, ev=None):
        data = self.entr.get()
        result = ""
        if ev.keysym != "Return":
            if data != "":
                result = ""
                nchar = 0
                for itt in data:
                    if itt.isdigit() or itt == ".":
                        result += itt
                    else:
                        nchar += 1
                self.curpos = self.entr.index("insert") - nchar
                self.entr.delete(0, tk.END)
                self.entr.insert(0, result)
                self.entr.icursor(self.curpos)
        else:
            flg = 0
            for itt in data:
                if itt != ".":
                    result += itt
                if itt == "." and flg == 0:
                    result += itt
                    flg = 1
            if result == "":
                result = self.min
            self.inlim = float(result)

            if self.inlim >= self.outlim and self.sctype == self.TYPEDW:
                self.inlim = self.outlim
            if self.inlim <= self.outlim and self.sctype != self.TYPEDW:
                self.inlim = self.outlim
            if self.inlim > self.max:
                self.inlim = self.max
            if self.inlim < self.min:
                self.inlim = self.min

            self.incmd.execute()

    def onscale(self, ev=None):
        self.inlim = self.scale.get()
        if self.inlim >= self.outlim and self.sctype == self.TYPEDW:
            self.inlim = self.outlim
        if self.inlim <= self.outlim and self.sctype != self.TYPEDW:
            self.inlim = self.outlim
        self.scale.set(self.inlim)
        self.entr.delete(0, tk.END)
        self.entr.insert(0, self.inlim)
        self.entr.icursor(self.curpos)

    def onreleasescale(self, ev=None):
        self.inlim = self.scale.get()
        if self.inlim >= self.outlim and self.sctype == self.TYPEDW:
            self.inlim = self.outlim
        if self.inlim <= self.outlim and self.sctype != self.TYPEDW:
            self.inlim = self.outlim
        self.incmd.execute()


class MyIntgrPan(tk.LabelFrame):
    def __init__(self, parent):
        tk.LabelFrame.__init__(self, parent, text="Панель интегрирования")

        self.scalup = IntegrScale(self, "up", "Верхний предел, эВ:")
        self.scaldw = IntegrScale(self, "dw", "Нижний предел, эВ:")
        self.scalup.grid(column=0, row=0, sticky="w" + "e", padx=10)
        self.scaldw.grid(column=0, row=1, sticky="w" + "e", padx=10, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.panoff()

    def setcmd(self, incmd):
        self.scalup.setcmd(incmd)
        self.scaldw.setcmd(incmd)

    def panoff(self):
        self.scalup.panoff()
        self.scaldw.panoff()

    def setlim(self, mdata):
        if mdata.accept() and mdata.status == "norm":
            lims = mdata.data.limits
            self.scalup.setlim(lims)
            self.scaldw.setlim(lims)
            self.scalup.panon()
            self.scaldw.panon()
        else:
            self.panoff()

    def getlim(self, mdata):
        if mdata.accept():
            limup = self.scalup.getlim()
            limdw = self.scaldw.getlim()
            mdata.data.limits.update({"lup": limup, "ldw": limdw})


class DelPointDial(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        tk.Toplevel.__init__(self, parent)
        self.title("Удаление точек")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.onclosing)
        wid = 10

        self.butok = tk.Button(
            self,
            text="Ok",
            width=wid,
            state="disabled",
            command=self.okcmd,
            activebackground=abg,
        )
        self.butcancel = tk.Button(
            self, text="Отмена", width=wid, command=self.onclosing, activebackground=abg
        )

        self.butok.grid(row=0, column=0, padx=20, pady=20)
        self.butcancel.grid(row=0, column=1, padx=20, pady=20)
        self.withdraw()

    def panstate(self, state):
        if state == 1:
            self.butok.config(state="active")
        elif state == 0:
            self.butok.config(state="disabled")

    def setcmd(self, okcmd, cancelcmd):
        self.inokcmd = okcmd
        self.incancelcmd = cancelcmd

    def setposition(self):
        self.update_idletasks()
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        wpar = self.parent.winfo_width()
        hpar = self.parent.winfo_height()
        wself = self.winfo_width()
        hself = self.winfo_height()
        self.geometry("+%d+%d" % (x + wpar / 2 - wself / 2, y + hpar / 2 - hself / 2))
        self.deiconify()
        self.focus_set()

    def okcmd(self):
        self.withdraw()
        self.panstate(0)
        self.inokcmd()

    def onclosing(self):
        self.withdraw()
        self.panstate(0)
        self.incancelcmd()


class PlotWindow(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        self.mdata = None
        self.button_release_event_id = None
        self.mouse_move_event_id = None
        tk.Toplevel.__init__(self, parent)
        self.bind("<FocusIn>", self.onTopFocusIn)
        self.bind("<FocusOut>", self.onTopFocusOut)
        self.protocol("WM_DELETE_WINDOW", self.onclosing)
        self.geometry("600x700")
        self.withdraw()

        self.enttrace = Makeentry(self, font="15")
        self.figi = plt.figure(1)
        self.figi.add_axes([0.15, 0.18, 0.82, 0.78])

        self.figdi = plt.figure(2)
        self.figdi.add_axes([0.15, 0.18, 0.82, 0.78])

        self.canvi = FigureCanvasTkAgg(self.figi, self)

        self.canvi._tkcanvas.grid(row=0, column=0, sticky="w" + "e" + "n" + "s")
        self.canvdi = FigureCanvasTkAgg(self.figdi, self)
        self.canvdi._tkcanvas.grid(row=1, column=0, sticky="w" + "e" + "n" + "s")
        self.enttrace.grid(row=2, column=0, columnspan=2, sticky="w" + "e" + "n" + "s")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.ki = 1e3  # масштаб по оси Y на кривой задержки

        # Меню
        self.gmenu = tk.Menu(self)
        self.config(menu=self.gmenu)
        self.filemenu = tk.Menu(self.gmenu, tearoff=False)
        self.showmenu = tk.Menu(self.gmenu, tearoff=False)
        self.gmenu.add_cascade(label="График", menu=self.showmenu)
        self.editmenu = tk.Menu(self.gmenu, tearoff=False)
        self.gmenu.add_cascade(label="Редактировать", menu=self.editmenu)

        self.logshow = [
            tk.BooleanVar(),
            tk.BooleanVar(),
            tk.BooleanVar(),
            tk.BooleanVar(),
        ]
        self.showmenu.add_checkbutton(
            label="Аппроксимация", command=self.privatepltdata, variable=self.logshow[0]
        )
        self.showmenu.add_checkbutton(
            label="Данные", command=self.privatepltdata, variable=self.logshow[1]
        )
        self.showmenu.add_checkbutton(
            label="Ошибка", command=self.privatepltdata, variable=self.logshow[3]
        )
        self.showmenu.add_checkbutton(
            label="Границы полиномов",
            command=self.privatepltdata,
            variable=self.logshow[2],
        )
        self.logshow[2].set(0)
        self.logshow[1].set(1)
        self.logshow[0].set(1)
        self.logshow[3].set(0)

    def get_range_figure(self):
        return [self.wm, self.im]

    def settrace(self, point=None):
        if point != None:
            numW = point[0]
            numF = point[1]
            if point[1] > 1:
                numF = 1
            else:
                numF = point[1]
            trace = "Энергия {0} эВ; ФР {1} отн. ед.".format(
                "%.3f" % numW, "%.3f" % numF
            )
            self.enttrace.refresh(trace)
        else:
            self.enttrace.refresh("")

    def setmenustate(self, val):
        if val == 1:
            self.editmenu.entryconfig("Удаление точек", state="normal")
        elif val == 0:
            self.editmenu.entryconfig("Удаление точек", state="disabled")

    def settracecmd(self, incmd):
        self.tracecmd = incmd.execute

    def setdelpcmd(self, incmd):
        self.editmenu.add_command(label="Удаление точек", command=incmd.execute)

    def setclosecmd(self, incmd):
        self.inclosecmd = incmd

    def setmouseselectcmd(self, incmd):
        if incmd == 0:
            self.canvi.mpl_disconnect(self.button_release_event_id)
        else:
            self.button_release_event_id = self.canvi.mpl_connect(
                "button_release_event", incmd
            )

    def onTopFocusIn(self, ev=None):
        self.bind("<Configure>", self.onTopConfigure)

    def onTopFocusOut(self, ev=None):
        self.unbind("<Configure>")

    def onTopConfigure(self, ev=None):
        x = self.winfo_x()
        y = self.winfo_y()

        xpar = self.parent.winfo_x()
        w_req = self.parent.winfo_width()
        w_form = self.parent.winfo_rootx() - xpar
        w = w_req + w_form * 2
        self.parent.wm_geometry("+%s+%s" % (x - w, y))

    def onclosing(self):
        self.inclosecmd()
        self.withdraw()

    def delfigure(self):
        plt.close(self.figi)
        plt.close(self.figdi)

    def setposition(self):
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        w_req = self.parent.winfo_width()
        w_form = self.parent.winfo_rootx() - x
        w = w_req + w_form * 2
        self.wm_geometry("+%s+%s" % (x + w, y))

    def privatepltdata(self):
        self.setposition()
        self.config(width=300, height=100)
        self.pack_propagate(0)
        self.ploti(self.mdata)
        self.plotdi(self.mdata)
        self.deiconify()

    def pltdata(self, mdata=None, point=None, trace=None):
        if mdata == None:
            self.withdraw()
        elif mdata.accept():
            self.mouse_move_event_id = self.canvi.mpl_connect(
                "motion_notify_event", self.tracecmd
            )
            self.mouse_move_event_id = self.canvdi.mpl_connect(
                "motion_notify_event", self.tracecmd
            )
            self.mdata = mdata.data
            self.setposition()
            self.config(width=300, height=100)
            self.pack_propagate(0)
            self.ploti(self.mdata, point, trace)
            self.plotdi(self.mdata, trace)
            self.deiconify()
        else:
            self.withdraw()

    def ploti(self, mdata, point=None, trace=None):
        plt.figure(1)
        plt.cla()
        plt.grid()
        plt.xlim([mdata.limits["ldw"], mdata.limits["lup"]])
        plt.xlabel("Задерживающий потенциал U$_a$, В")
        plt.ylabel("Ток, нА")
        iplt = [itt * self.ki for itt in mdata.data["i"]]
        if self.logshow[1].get() == 1:
            plt.plot(mdata.data["w"], iplt, "wo", mew=2, ms=5, mec="r")
        if self.logshow[0].get() == 1:
            aiplt = [itt * self.ki for itt in mdata.data["ai"]]
            plt.plot(mdata.data["aw"], aiplt, "k")
        if trace != None:
            plt.plot(trace[0], trace[1], "xk")
        try:
            if self.logshow[2].get() == 1:
                intsiplt = [itt * self.ki for itt in mdata.data["intsi"]]
                plt.plot(mdata.data["intsw"], intsiplt, "bs")
        except KeyError:
            pass
        if self.logshow[3].get() == 1:
            scoplt = [itt * self.ki for itt in mdata.data["sco"]]
            plt.errorbar(
                mdata.data["w"], iplt, scoplt, fmt="o", color="m", ms=0, capsize=4
            )
        if point != None:
            plt.plot(point[0], point[1] * self.ki, "*c", mew=1, ms=10, mec="k")
        self.canvi.draw()
        axes = plt.gca()
        xlim = axes.get_xlim()
        ylim = axes.get_ylim()
        self.wm = abs(xlim[0] - xlim[1])
        self.im = abs(ylim[0] - ylim[1])

    def plotdi(self, mdata, trace=None):
        plt.figure(2)
        plt.cla()
        plt.grid()
        maxdi = max(mdata.data["adi"])
        plt.xlim([mdata.limits["ldw"], mdata.limits["lup"]])
        plt.ylim([0, 1])
        plt.xlabel("Энергия W, эВ")
        plt.ylabel("f(W), отн.ед.")
        if maxdi == 0:
            maxdi = 1
        ai = []
        for itt in mdata.data["adi"]:
            ai.append(itt / maxdi)
        if self.logshow[0].get() == 1:
            plt.plot(mdata.data["aw"], ai, "k")
        if trace != None:
            plt.plot(trace[0], trace[2] / maxdi, "xk")
        try:
            if self.logshow[2].get() == 1:
                plt.plot(mdata.data["intsw"], mdata.data["intsdi"] / maxdi, "bs")
        except KeyError:
            pass
        else:
            self.canvdi.draw()


class AppMenu(tk.Menu):
    def __init__(self, parent):
        self.gmenu = tk.Menu(parent)
        self.setmenu = tk.Menu(self.gmenu, tearoff=False)
        self.filemenu = tk.Menu(self.gmenu, tearoff=False)
        parent.config(menu=self.gmenu)
        self.gmenu.add_cascade(label="Файл", menu=self.filemenu)
        self.gmenu.add_cascade(label="Настройки", menu=self.setmenu)

    def setsetcmd(self, incmd):
        self.setmenu.add_command(label="Настройки", command=incmd.execute)

    def setfilecmd(self, incmd):
        self.filemenu.add_command(label="Добавить...", command=incmd["add"].execute)
        self.filemenu.add_command(
            label="Открыть архив...", command=incmd["load"].execute
        )
        self.filemenu.add_command(label="Очистить", command=incmd["clear"].execute)
        self.filemenu.add_separator()
        self.filemenu.add_command(
            label="Сохранить в массив...", command=incmd["savearr"].execute
        )
        self.filemenu.add_command(
            label="Сохранить в текстовый файл...", command=incmd["savetxt"].execute
        )
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Выход", command=incmd["quit"])
        self.setmenu.add_command(
            label="Установить всем...", command=incmd["setall"].execute
        )
        self.setstate(0)
        self.cansave(0)

    def setstate(self, state):
        if state == 1:
            self.filemenu.entryconfig("Очистить", state="normal")
            self.filemenu.entryconfig("Сохранить в массив...", state="normal")
            self.setmenu.entryconfig("Установить всем...", state="normal")
        elif state == 0:
            self.filemenu.entryconfig("Очистить", state="disabled")
            self.filemenu.entryconfig("Сохранить в массив...", state="disabled")
            self.filemenu.entryconfig("Сохранить в текстовый файл...", state="disabled")
            self.setmenu.entryconfig("Установить всем...", state="disabled")

    def cansave(self, state):
        if state == 0:
            self.filemenu.entryconfig("Сохранить в текстовый файл...", state="disabled")
        elif state == 1:
            self.filemenu.entryconfig("Сохранить в текстовый файл...", state="normal")

    def setstateall(self, state):
        if state == 1:
            self.filemenu.entryconfig("Сохранить в текстовый файл...", state="normal")
            self.filemenu.entryconfig("Очистить", state="normal")
            self.filemenu.entryconfig("Сохранить в массив...", state="normal")
            self.setmenu.entryconfig("Установить всем...", state="normal")
            self.filemenu.entryconfig("Открыть архив...", state="normal")
            self.filemenu.entryconfig("Добавить...", state="normal")
        elif state == 0:
            self.filemenu.entryconfig("Очистить", state="disabled")
            self.filemenu.entryconfig("Сохранить в массив...", state="disabled")
            self.filemenu.entryconfig("Сохранить в текстовый файл...", state="disabled")
            self.setmenu.entryconfig("Установить всем...", state="disabled")
            self.filemenu.entryconfig("Открыть архив...", state="disabled")
            self.filemenu.entryconfig("Добавить...", state="disabled")
