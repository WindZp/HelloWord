"""
Zp_Core系列
本电池主要包含自己需写得一套api电池；
为简化函数构造准备；

作者:笑里追风
日期：2021.7.18
"""



import Grasshopper
from sys import path
#调用IronPython文件夹
path1=[]
path1.append(r'C:\Program Files\Rhino 6\Plug-ins\IronPython\Lib')
path1.append(r'C:\Program Files\Rhino 7\Plug-ins\IronPython\Lib')
for i in path1:
    if i not in path:
        path.append(i)


"""
ghenv.Component.Message = "点线面基类"
ghenv.Component.Name = "Pt,Crv,Srf,Brep"
ghenv.Component.NickName = "Zp_Base"
ghenv.Component.Category = 'Zp'
ghenv.Component.SubCategory = '0 |Core'
"""


#函数库调用
import Rhino.Geometry as rg
import scriptcontext as sc
import ghpythonlib.components as ghc
import ghpythonlib.treehelpers as ght
import math
import clr
import copy
import System
import rhinoscriptsyntax as rs




#AAA索引——基类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++0.基础++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#01物件属性函数值排序
def Zp_Sort(Zp_SortNumber,geos):
    numbers_unsort=[]
    indexs_unsort=[]
    for i in range(len(geos)):
        indexs_unsort.append(i)
        numbers_unsort.append(Zp_SortNumber(geos[i]))
    numbers_sort,indexs_sort,geos_sort=zip(*sorted(zip(numbers_unsort,indexs_unsort,geos)))
    return numbers_sort,indexs_sort,geos_sort
#02跟随排序
def Zp_FollowSort(numbers_unsort,geos):
    numbers_sort,geos_sort=zip(*sorted(zip(numbers_unsort,geos)))
    return geos_sort
def Zp_Item(indexs,geos):
    geos_sort=[geos[i] for i in indexs]
    return geos_sort   

#03最值选择
def Zp_MaxMin(geos_sort,choose):
    if choose=="min":
        return geos_sort[0]
    elif choose=="max":
        return geos_sort[-1]
    else:
        return geos_sort[choose]




#04改写数字容差（打包法则）双层嵌套列表
def Zp_NumberTolenrancePartionSort(numbers,tolenrance):
    #打包
    group_ni=[(numbers[i],i) for i in range(len(numbers))]
    #打包数字排序
    numbers_sort,group_ni_sort=zip(*sorted(zip(numbers,group_ni)))
    #构造分组双层数列：
    group_p=[]
    #简化
    a=group_ni_sort
    #组合列表容差分组
    if len(a)==1:
        group_p.append([a[0]])
    else:
        lst=[]
        lst.append(a[0])
        for i in range(1,len(a)):
           #判定数字间是否间断
            if a[i][0]-a[i-1][0]<=tolenrance:
                lst.append(a[i])
                #末数判定成组
                if i==len(a)-1:
                    group_p.append(lst)
            else:
                group_p.append(lst)
                lst=[]
                lst.append(a[i])
                #末数判定成组
                if i==len(a)-1:
                    group_p.append(lst)
    #双层列表解包
    numbers_p=[]
    indexs_p=[]
    for i in range(len(group_p)):
        numbers_p.append(map(lambda x:x[0],group_p[i]))
        indexs_p.append(map(lambda x:x[1],group_p[i]))
    return numbers_p,indexs_p



#05改写数字容差分组（打包法则）双层嵌套列表改进，路径法则优化
#建立二层列表空集，再向空集扔元素
def Zp_NumberTolenrancePartionSort(numbers,tolenrance):
    #打包
    group_ni=[(numbers[i],i) for i in range(len(numbers))]
    #打包数字排序
    numbers_sort,group_ni_sort=zip(*sorted(zip(numbers,group_ni)))
    #构造分组双层数列：
    group_p=[]
    #简化
    a=group_ni_sort
    #组合列表容差分组
    if len(a)==1:
        group_p.append([a[0]])
    else:
        group_p.append([])
        group_p[-1].append(a[0])
        for i in range(1,len(a)):
           #判定数字间是否间断
            if a[i][0]-a[i-1][0]<=tolenrance:
                group_p[-1].append(a[i])
            else:
                group_p.append([])
                group_p[-1].append(a[i])
    #双层列表解包
    numbers_p=[]
    indexs_p=[]
    for i in range(len(group_p)):
        numbers_p.append(map(lambda x:x[0],group_p[i]))
        indexs_p.append(map(lambda x:x[1],group_p[i]))
    return numbers_p,indexs_p


#06数字容差替换：平均值替换得数值列表
def Zp_NumberTolenranceReplace(numbers,tolenrance):
    a,b=Zp_NumberTolenrancePartionSort(numbers,tolenrance)
    c=map(lambda x:len(x),a)
    d=map(lambda x:ghc.Average(x),a)
    e=[]
    f=[]
    for i in range(len(a)):
        for j in range(len(a[i])):
            e.append(d[i])
            f.append(b[i][j])
    f,e=zip(*sorted(zip(f,e)))
    return e


"""
#知识补充
#双层解包：双层元组列表拆分元素
#已知：p=[[(a1,b1),(a2,b2)],[(a3,b3),(a4,b4)]]
#求解：a=[[a1,a2],[a3,a4]]

#解法1：空集添加法,适用与元组，list组合。通用
def Zp_UnGroup(lst_ij,n):
    lst_ij_n=[]
    for i in range(len(lst_ij)):
        lst_ij_n.append([])
        for j in range(len(lst_ij[i])):
            lst_ij_n[i].append(lst_ij[i][j][n])
    return lst_ij_n
#解法2：深层copy替换法，适合非元组系列
def Zp_UnGroup(lst_ij,n):
    lst_ij_n=copy.deepcopy(lst_ij)
    for i in range(len(lst_ij)):
        for j in range(len(lst_ij[i])):
            lst_ij_n[i][j]=lst_ij[i][j][n]
    return lst_ij_n

#双层打包：双层列表解包打包元组
#已知1：a=[[a1,a2],[a3,a4]]
#已知2：b=[[b1,b2],[b3,b4]]
#求解3：p=[[(a1,b1),(a2,b2)],[(a3,b3),(a4,b4)]]
#解法1：
def Zp_Group(lst_ij_a,lst_ij_b):
    lst_ij=copy.deepcopy(lst_ij_a)
    for i in range(len(lst_ij)):
        for j in range(len(lst_ij[i])):
            lst_ij[i][j]=[lst_ij_a[i][j],lst_ij_b[i][j]]
    return lst_ij
"""

#06群点距离测量格式化数据输出
def DistanceByIndexs(pts,indexlist,decimals,crv_t,scale):
    #默认化：
    def MoRen(str,str_number):
        str=str if str else str_number
        number=float(eval(str))
        return number
    #精度默认化
    decimals=int(MoRen(decimals,"0"))
    crv_t=MoRen(crv_t,"0.5")
    scale=MoRen(scale,"0.8")
    #一句话表达，pts[]中得东西麻烦还重复，如何解决？
    #构造一个字符int转化函数得点；
    def Pts(pts,str,n):
        return pts[int(str.split(",")[n])]
    #简化lambda函数：
    dsts=map(lambda x:round(Pts(pts,x,0).DistanceTo(Pts(pts,x,1)),decimals),indexlist)
    crvs=map(lambda x:rg.Line(Pts(pts,x,0),(Pts(pts,x,1))),indexlist)
    #曲线单元化：
    for i in range(len(crvs)):
        crvs[i]=crvs[i].ToNurbsCurve()
        crvs[i].Domain=rg.Interval(0,1)
    #曲线可视化标注点
    ptt=map(lambda x:ghc.EvaluateCurve(x,crv_t)[0],crvs)
    pts_scale=map(lambda x:ghc.Scale(x,ghc.Average(ptt),scale)[0],ptt)
    return crvs,dsts,pts_scale














#AAA索引——str类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Zp_Str:
    #+++++++++++++++++++0点属性构造+++++++++++++++++++++
    def __init__(self,name):
        self.name=name
        self.type="字符"
    def __call__(self):
        return self
    #+++++++++++++++++++1构造++++++++++++++++++++++++++++
    #01构造偏移数据：原则：判定切割方向，以及偏移数据
    def OffNumber(self):
        strs=str.split(",")
        float(strs[-1])
        numbers=map(lambda x:float(x),strs)
        return numbers
    #+++++++++++++++++++2方法++++++++++++++++++++++++++++
    #2.1定义一个路径筛选属性；
    def PathCount(self,strs,n):
        str=self.name
        return map(lambda x:x[1:n*2],strs).count(str[1:n*2])
        


class Zp_Strs(object):
    #+++++++++++++++++++0点属性构造+++++++++++++++++++++
    def __init__(self,name):
        self.name=name
        self.type="字符列表"
    #+++++++++++++++++++1构造++++++++++++++++++++++++++++
    #+++++++++++++++++++2方法++++++++++++++++++++++++++++
    #2.1数据去重统计
    #注意index是双层list列表，gh输出用得时候树形转换一下
    def Static(self):
        strs=self.name
        #数据统计
        str_amout=len(strs)
        #去重以及排序
        str_set=list(set(strs))
        str_set.sort(key=strs.index)
        #构造去重统计
        str_count=[]
        str_index=[]
        for i in range(len(str_set)):
            a=[]
            for j in range(str_amout):
                if str_set[i]==strs[j]:
                    a.append(j)
            str_count.append(len(a))
            str_index.append(a)
        return str_amout,str_set,str_count,str_index







#AAA索引——number类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Number(object):
    #+++++++++++++++++++0点属性构造+++++++++++++++++++++
    def __init__(self,name):
        self.name=name
        self.type="数字"
    #+++++++++++++++++++1构造++++++++++++++++++++++++++++
    #+++++++++++++++++++2方法++++++++++++++++++++++++++++
    ##########2.1字符数字化############
    def FormatNmuber(self):
        return eval(str(self.name))
    ##########2.2字符默认化############
    def DefaultNumber(self):
        pass
    ##########2.3数字精度############
    def Precision(self,decimals):
        number=self.FormatNmuber()
        decimals=Zp_Number(decimals).FormatNmuber()
        decimals=int(decimals)
        if decimals==0:
            number=int(number)
        else:
            number=round(number,decimals)
        return number
    ##########2.4逗号间隔多表达式合并############
    def EXpressionJoin(self):
        a=(self.name).split(",")
        for i in range(len(a)):
            if "+" in a[i] or "-" in a[i] or "*" in a[i] or "/" in a[i]:
                a[i]=str(eval(a[i]))
        b=",".join(a)
        return b
    ##########2.5数子模数化############
    def Mod(self,start,mod,pattern):
        #参数格式化
        number=self.FormatNmuber()
        start=Zp_Number(start).FormatNmuber()
        mod=Zp_Number(mod).FormatNmuber()
        pattern=Zp_Number(pattern).FormatNmuber()
        #选择判定方式，pattern（0：near，1：ceil，2：floor）
        if pattern==1:
            zhengshu=math.ceil((number-start)/mod)
        elif pattern==2:
            zhengshu=math.floor((number-start)/mod)
        else:
            zhengshu=round((number-start)/mod)
        number_mod=zhengshu*mod+start
        tolerance=number-number_mod
        return number_mod,tolerance
    ##########2.6单数字整数映射############
    def NumberIntMap(self,numbers):
        #数字排序
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,numbers)
        #数字去重
        str_amout,str_set,str_count,str_index=Zp_Numbers(numbers_sort).Static()
        #排序占位求解
        a=int(len(str_set)/10)
        b=1
        while a>0:
            a=int(a/10)
            b=b+1
        c=int(math.pow(10,b))
        #去重数字替换并加位值
        list_replace=[int(i+c) for i in range(len(str_set))]
        #去重数字位置还原
        numbers_replace=list(copy.deepcopy(numbers_sort))
        for i in range(len(str_index)):
            for j in range(len(str_index[i])):
                numbers_replace[(str_index[i][j])]=list_replace[i]
        #原未去重数字位置还原替换
        numbers_replaceall=list(Zp_FollowSort(indexs_sort,numbers_replace))
        #数字查找并替换
        for i in range(len(numbers)):
            if self.name==numbers[i]:
                number_replace=numbers_replaceall[i]
                break
        return  number_replace,b




#AAA索引——numbers类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Numbers(object):
    #+++++++++++++++++++0点属性构造+++++++++++++++++++++
    def __init__(self,name):
        self.name=name
        self.type="数字列表"
    #+++++++++++++++++++1构造++++++++++++++++++++++++++++
    #+++++++++++++++++++2方法++++++++++++++++++++++++++++
    #2.1数组模数化分析统计
    def NumbersModSet(self,start,mod,pattern):
        numbers=self.name
        number_mod=map(lambda x: Zp_Number(x).Mod(start,mod,pattern)[0],numbers)
        tolerance=map(lambda x: Zp_Number(x).Mod(start,mod,pattern)[1],numbers)
        #数字统计
        number_set=list(set(number_mod))
        number_set.sort(key=number_mod.index)
        count=map(lambda x: number_mod.count(x),number_set)
        return number_mod,tolerance,number_set,count
    #2.2数据去重统计
    #注意index是双层list列表，gh输出用得时候树形转换一下
    def Static(self):
        strs=self.name
        #数据统计
        str_amout=len(strs)
        #去重以及排序
        str_set=list(set(strs))
        str_set.sort(key=strs.index)
        #构造去重统计
        str_count=[]
        str_index=[]
        for i in range(len(str_set)):
            a=[]
            for j in range(str_amout):
                if str_set[i]==strs[j]:
                    a.append(j)
            str_count.append(len(a))
            str_index.append(a)
        return str_amout,str_set,str_count,str_index
    #2.3求一个数据得最简化整数映射得方法
    #返回替换后得整数映射数字以及换位位数
    def NumbersIntMap(self):
        numbers=self.name
        #数字排序
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,numbers)
        #数字去重
        str_amout,str_set,str_count,str_index=Zp_Numbers(numbers_sort).Static()
        #排序占位求解
        a=int(len(str_set)/10)
        b=1
        while a>0:
            a=int(a/10)
            b=b+1
        c=int(math.pow(10,b))
        #去重数字替换并加位值
        list_replace=[int(i+c) for i in range(len(str_set))]
        #去重数字位置还原
        numbers_replace=list(copy.deepcopy(numbers_sort))
        for i in range(len(str_index)):
            for j in range(len(str_index[i])):
                numbers_replace[(str_index[i][j])]=list_replace[i]
        #原未去重数字位置还原替换
        numbers_replaceall=list(Zp_FollowSort(indexs_sort,numbers_replace))
        return  numbers_replaceall
    ##########2.6单数字整数映射############
    def NumbersTPartion(self,t):
        numbers,indexs=Zp_NumberTolenrancePartionSort(self,t)
        numbers_sort=ght.list_to_tree(numbers)
        indexs_sort=ght.list_to_tree(indexs)
        return numbers_sort,indexs_sort








#AAA索引——点类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++点类+++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Zp_Pt(object):
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++0点属性构造++++++++++++++++++++++++++++
    def __init__(self,name):
        self.name=name
        self.type="点"
    #++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++1构造++++++++++++++++++++++++++++
    
    
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++2点常规系列++++++++++++++++++++++++++++
    #2.1相对坐标
    def PlaneCo(self,plane):
        try:
            plane=plane if plane else rg.Plane.WorldXY
        except:
            plane=rg.Plane.WorldXY
        trans=rg.Transform.PlaneToPlane(plane,rg.Plane.WorldXY)
        pt_new=rg.Point3d(self.name)
        pt_new.Transform(trans)
        return pt_new
    #2.2相对坐标单轴值
    def PlaneCoAxis(self,plane,axis):
        pts_new=self.PlaneCo(plane)
        if axis=="x":
            pt_number=pts_new.X
        elif axis=="y":
            pt_number=pts_new.Y
        else:
            pt_number=pts_new.Z
        return pt_number
    #2.3点移动到相对坐标系
    def PlaneTo(self,plane):
        try:
            plane=plane if plane else rg.Plane.WorldXY
        except:
            plane=rg.Plane.WorldXY
        trans=rg.Transform.PlaneToPlane(rg.Plane.WorldXY,plane)
        pt_new=rg.Point3d(self.name)
        pt_new.Transform(trans)
        return pt_new
    #2.4点双向挤出线
    def PtLine(self,vector,length,choose=True):
        pt=self.name
        vector.Unitize()
        vector=vector*length
        if choose:
            #参数变化，起始点跟移动长度均变化；
            pt=pt-vector
            vector=vector*2
        pt2=pt+vector
        line=rg.Line(pt,pt2)
        return line
    #2.5点到其他线的t值,或者
    def LocationOnCrv(self,crv,outindex=-1):
        midpt=self.name
        t=ghc.CurveClosestPoint(midpt,crv)[1]
        if outindex==-1:
            return t
        else:
            output=ghc.EvaluateCurve(crv,t)[outindex]
            return output


#AAA索引——群点类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++群点类++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Zp_Pts(object):
    #点属性构造
    def __init__(self,name):
        self.name=name
        self.type="群点"
    #++++++++++++++++++++++++1构造方法++++++++++++++++++++++++++
    #1.1点整列
    def PtsGrip(self,plane,w,h,wi,hi,pt_indexs,cell_indexs):
        #叠加法则：
        def Zp_MasAdd(lst):
            if len(lst)>1:
                for i in range(len(lst)):
                    if i>0:
                        lst[i]=lst[i-1]+lst[i]
            return lst
        #点定位
        def PlaneTo(pt,plane):
            try:
                plane=plane if plane else rg.Plane.WorldXY
            except:
                plane=rg.Plane.WorldXY
            trans=rg.Transform.PlaneToPlane(rg.Plane.WorldXY,plane)
            pt_new=rg.Point3d(pt)
            pt_new.Transform(trans)
            return pt_new
        #01数据格式化
        w=float(w)
        h=float(h)
        wi=map(lambda x:float(x),wi.split(","))
        wi.insert(0,0)
        hi=map(lambda x:float(x),hi.split(","))
        hi.insert(0,0)
        #02数据叠加化
        wi_add=Zp_MasAdd(wi)
        hi_add=Zp_MasAdd(hi)
        #构造树形点
        pt_ij=[]
        for i in range(len(wi_add)):
            pt_i=[]
            for j in range(len(hi_add)):
                pt=rg.Point3d(wi_add[i],hi_add[j],0)
                pt_co=PlaneTo(pt,plane)
                pt_i.append(pt_co)
            pt_ij.append(pt_i)
        pt_ijtree=ght.list_to_tree(pt_ij)
        #03构造细胞
        cell_ij=[]
        for i in range(len(pt_ij)-1):
            cell_i=[]
            for j in range(len(pt_ij[i])-1):
                j_dx=pt_ij[i][j].DistanceTo(pt_ij[i+1][j])
                j_dy=pt_ij[i][j].DistanceTo(pt_ij[i][j+1])
                plane1=rg.Plane(plane)
                plane1.Origin=pt_ij[i][j]
                j_r=ghc.Rectangle(plane1,j_dx,j_dy,0)[0]
                cell_i.append(j_r)
            cell_ij.append(cell_i)
        cell_ijtree=ght.list_to_tree(cell_ij)
        kuang=ghc.Rectangle(plane,w,h,0)[0]
        #04取点
        pt_items=[]
        if pt_indexs:
            for i in range(len(pt_indexs)):
                a,b=pt_indexs[i].split(",")
                a=int(a)
                b=int(b)
                pt_items.append(pt_ij[a][b])
        #05取框
        cell_items=[]
        if cell_indexs:
            for i in range(len(cell_indexs)):
                a,b=cell_indexs[i].split(",")
                a=int(a)
                b=int(b)
                cell_items.append(cell_ij[a][b])
        return kuang,pt_ijtree,cell_ijtree,pt_items,cell_items
    
    #1.1.1 群点indexs值
    def Indexs(self):
        pts=self.name
        indexs=[i for i in range(len(pts))]
        return vector
    
    
    #1.2.1 前2点构造向量
    def PtsVector(self):
        pts=self.name
        vector=ghc.Vector2Pt(pts[0],pts[1],True)[0]
        return vector
    #1.2.2 前三点构造平面
    def Plane(self):
        pts=self.name
        plane=rg.Plane(pts[0],pts[1],pts[2])
        return plane
    
    
    #1.3.1前两点构造线
    def PtsLine(self):
        pts=self.name
        line=rg.Line(pts[0],pts[1])
        return line
    #1.3.2三点构造圆弧
    def PtsArc(self):
        pts=self.name
        arc=rg.Arc(pts[0],pts[1],pts[2])
        return arc
    #1.3.3 多点构造多端线
    def PtsPolyLine(self,pts,bool=False):
        pts=self.name
        polyline=ghc.PolyLine(pts,bool)
        return polyline
    #1.3.4 多点构造3阶内差点线
    def PtsCrv(self,pts,bool=False):
        pts=self.name
        crv=ghc.Interpolate(pts,3,bool,2)
        return crv
    

    #1.4.1 多点构造面（3，4点）
    def Srf(self):
        pts=self.name
        n=len(pts)
        if n==3:
            srf=rg.Brep.CreateFromCornerPoints(pts[0],pts[1],pts[2],0.1)
        else:
            srf=rg.Brep.CreateFromCornerPoints(pts[0],pts[1],pts[2],pts[3],0.1)
        return srf
    #1.4.2 多点构造面(前三点为核心坐标面点)
    def PSrf(self):
        pts=self.name
        plane=rg.Plane(pts[0],pts[1],pts[2])
        pts_pro=map(lambda x:ghc.PlaneClosestPoint(x,plane)[0],pts)
        crv=ghc.PolyLine(pts_pro,True)
        srf=ghc.BoundarySurfaces(crv)
        return srf

    
    
    
    #+++++++++++++++++++2群点常规系列++++++++++++++++++++++++++++
    #2.0构造点数量
    def Count(self):
        return len(self.name)
    #2.1构造平均点
    def Average(self):
        return ghc.Average(self.name)
    #2.2点坐标轴容差替换：t=tolenrance,r=replace
    def PtsTolenranceReplace(self,tx,ty,tz):
        pts=self.name
        pts_x=map(lambda x:x.X,pts)
        pts_y=map(lambda x:x.Y,pts)
        pts_z=map(lambda x:x.Z,pts)
        pts_xr=Zp_NumberTolenranceReplace(pts_x,tx)
        pts_yr=Zp_NumberTolenranceReplace(pts_y,ty)
        pts_zr=Zp_NumberTolenranceReplace(pts_z,tz)
        pts_replace=map(lambda x,y,z: rg.Point3d(x,y,z),pts_xr,pts_yr,pts_zr)
        return pts_replace
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++3群点排序系列++++++++++++++++++++++++++++
    #3.1坐标轴排序
    def SortByPlane(self,plane,axis):
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:Zp_Pt(x).PlaneCoAxis(plane,axis),self.name)
        return geos_sort,indexs_sort
    #3.2坐标优先排序先x,再yz;
    def SortByPlaneXYZ(self,plane):
        pts=self.name
        #构造相对坐标点
        pts_co=map(lambda x:Zp_Pt(x).PlaneCo(plane),pts)
        indexs_sort=ghc.SortPoints(pts_co)[1]
        pts_sort=map(lambda x:pts[x],indexs_sort)
        return pts_sort,indexs_sort
    #3.3坐标环绕排序
    def SortByCircle(self,plane,seam):
        try:
            plane=plane if plane else rg.Plane.WorldXY
        except:
            plane=rg.Plane.WorldXY
        pts_mid=self.Average()
        plane.Origin=pts_mid
        #构造辅助圆
        radius=pts_mid.DistanceTo(self.name[0])*1.2
        crv=rg.Circle(plane,radius).ToNurbsCurve()
        crv.Domain=rg.Interval(0,1)
        crv.ChangeClosedCurveSeam(seam)
        line=rg.Line(pts_mid,crv.PointAtStart)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:ghc.CurveClosestPoint(x,crv)[1],self.name)
        return geos_sort,indexs_sort,line,plane
    #3.4坐标X单轴容差分组排序
    def SortByTolenrancePartionPlaneXAxis(self,plane,tx):
        pts=self.name
        #构造相对坐标点
        pts_co=map(lambda x:Zp_Pt(x).PlaneCo(plane),pts)
        #构造x,y容差点
        pts_r=Zp_Pts(pts_co).PtsTolenranceReplace(tx,0,0)
        #构造x容差分组,yp代表x分组
        pts_ry=map(lambda x:x.X,pts_r)
        indexs_yp=Zp_NumberTolenrancePartionSort(pts_ry,tx)[1]
        #对分组相对坐标点构造x排序
        for i in range(len(indexs_yp)):
            numbers_unsort=map(lambda x:pts_co[x].X,indexs_yp[i])
            indexs_yp[i]= Zp_FollowSort(numbers_unsort,indexs_yp[i])
        pts_sort=[]
        #*列表套列表元素得替换！！！！
        for i in range(len(indexs_yp)):
            pts_sort.append(map(lambda x:ghc.ListItem(pts,x,True),indexs_yp[i]))
        #树形转化
        pts_sort=ght.list_to_tree(pts_sort)
        indexs_sort=ght.list_to_tree(indexs_yp)
        #可视化(后补充)
        return pts_sort,indexs_sort
    #3.5三坐标容差分组排序
    def SortByTolenrancePartionPlane(self,plane,tx,ty):
        pts=self.name
        #构造相对坐标点
        pts_co=map(lambda x:Zp_Pt(x).PlaneCo(plane),pts)
        #构造x,y容差点
        pts_r=Zp_Pts(pts_co).PtsTolenranceReplace(tx,ty,0)
        #构造y容差分组,yp代表y分组
        pts_ry=map(lambda x:x.Y,pts_r)
        indexs_yp=Zp_NumberTolenrancePartionSort(pts_ry,ty)[1]
        #对分组相对坐标点构造x排序
        for i in range(len(indexs_yp)):
            numbers_unsort=map(lambda x:pts_co[x].X,indexs_yp[i])
            indexs_yp[i]= Zp_FollowSort(numbers_unsort,indexs_yp[i])
        pts_sort=[]
        #*列表套列表元素得替换！！！！
        for i in range(len(indexs_yp)):
            pts_sort.append(map(lambda x:ghc.ListItem(pts,x,True),indexs_yp[i]))
        #树形转化
        pts_sort=ght.list_to_tree(pts_sort)
        indexs_sort=ght.list_to_tree(indexs_yp)
        #可视化(后补充)
        return pts_sort,indexs_sort
    #3.6最近点排序
    def SortByNear(self,index_s):
        pts=self.name
        #*构造点index组
        ptandindex=[(pts[i],i) for i in range(len(pts))]
        #构造起始数组
        pt_s=ptandindex[index_s]
        pts_add=[pt_s]
        #构造删除数组
        pts_del=ptandindex
        del pts_del[index_s]
        while len(pts_del)>0:
            d=map(lambda x:pts_add[-1][0].DistanceTo(x[0]),pts_del)
            pts_del=list(Zp_FollowSort(d,pts_del))
            pts_add.append(pts_del[0])
            del pts_del[0]
        #元组解组
        pts_sort=map(lambda x:x[0],pts_add)
        indexs_sort=map(lambda x:x[1],pts_add)
        return pts_sort,indexs_sort
    #3.7单线线t值排序；
    def SortByCrv(self,crv):
        pts=self.name
        ptandindex=[(pts[i],i) for i in range(len(pts))]
        #改造c#得rg函数,注意t值得属性
        def ClosePtT(pt,crv):
            t=clr.StrongBox[float]()
            crv.ClosestPoint(pt,t)
            return t.Value
        t=map(lambda x:ClosePtT(x[0],crv),ptandindex)

        ptandindex=list(Zp_FollowSort(t,ptandindex))
        #元组解组
        pts_sort=map(lambda x:x[0],ptandindex)
        indexs_sort=map(lambda x:x[1],ptandindex)
        return pts_sort,indexs_sort
    #3.8多线t值排序：
    def SortByCrvs(self,crvs):
        pts=self.name
        #打包
        ptandindex=[(pts[i],i) for i in range(len(pts))]
        crvandindex=[(crvs[i],i) for i in range(len(crvs))]
        #构造点选线(pt,pt_index,crv_index)
        choose=[]
        for i in range(len(ptandindex)):
            d=map(lambda x:ghc.CurveClosestPoint( ptandindex[i][0],x[0])[2],crvandindex)
            crv_indexchoose=Zp_FollowSort(d,crvandindex)[0][1]
            choose.append((ptandindex[i][0],ptandindex[i][1],crv_indexchoose))
        #点按线index得容差分组
        crv_indexs=map(lambda x:x[2],choose)
        a,b=Zp_NumberTolenrancePartionSort(crv_indexs,0)

        #双层对打包进行双列表匹配
        choose_p=[]
        for i in range(len(b)):
            choose_p.append(map(lambda x:choose[x],b[i]))

        #双层列表t排序
        for i in range(len(choose_p)):
        #改造c#得rg函数,注意t值得属性
            def ClosePtT(pt,crv):
                t=clr.StrongBox[float]()
                crv.ClosestPoint(pt,t)
                return t.Value
            t=map(lambda x:ClosePtT(x[0],crvs[x[2]]),choose_p[i])
            choose_p[i]=list(Zp_FollowSort(t,choose_p[i]))
        #双层列表解包：
        pts_sort=[]
        index_sort=[]
        for i in range(len(choose_p)):
            pts_sort.append(map(lambda x:x[0],choose_p[i]))
            index_sort.append(map(lambda x:x[1],choose_p[i]))
        #树形转化
        pts_sort=ght.list_to_tree(pts_sort)
        indexs_sort=ght.list_to_tree(index_sort)
        return pts_sort,indexs_sort

    #3.9点距离分组同时按轴线对组中点排序：
    def GroupByDistance(self,distance,plane,axis):
        pts=self.name
        pts_p,indexs_p=ghc.trees.PointGroups(pts,distance)
        #列表转化
        pts_plst=ght.tree_to_list(pts_p)
        indexs_plst=ght.tree_to_list(indexs_p)
        #群组中心点axis排序
        pts_mid=map(lambda x:ghc.Average(x),pts_plst)
        pts_a,indexs_a=Zp_Pts(pts_mid).SortByPlane(plane,axis)
        #群组列表选项排序
        indexs_plst=map(lambda x:indexs_plst[x],indexs_a)
        pts_plst=map(lambda x:pts_plst[x],indexs_a)
        #树形转化
        pts_ptree=ght.list_to_tree(pts_plst)
        indexs_ptree=ght.list_to_tree(indexs_plst)
        return pts_ptree,indexs_ptree
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++4群点其他系列++++++++++++++++++++++++++++
    #3.2坐标面分组线(仅针对多数据)
    #对于树形数据需要改进对树形数据得处理！！不然错误！！！！！
    def PartionByPlane(self,plane):
        pts=self.name
        def Zp_FollowSort1(plane,geos):
            numbers=map(lambda x:abs(ghc.PlaneClosestPoint(x,plane)[2]),geos)
            numbers_sort,geos_sort=zip(*sorted(zip(numbers,geos)))
            numbers_sort=[i-numbers_sort[0] for i in numbers_sort]
            return numbers_sort,geos_sort
        #群点坐标面分组
        pts_up=[]
        pts_down=[]
        for i in pts:
            if ghc.PlaneCoordinates(i,plane)[2]>0:
                pts_up.append(i)
            else:
                pts_down.append(i)
        #群点坐标面分组后距离排序
        #分析点间距离！
        d_up,pts_up=Zp_FollowSort1(plane,pts_up)
        d_down,pts_down=Zp_FollowSort1(plane,pts_down)
        return pts_up,pts_down



#AAA索引——线类
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++线类++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Zp_Crv(object):
    #++++++++++++++++++++++++00属性+++++++++++++++++++++++++ 
    def __init__(self,name):
        self.name=name
        self.type="线"
    #++++++++++++++++++++++++01构造方法++++++++++++++++++++++
    #1.1三角形以及四边形多段线边线建面
    def EdgeSrf(self):
        polycrv=self.name
        crvs=ghc.Explode(polycrv,True)[0]
        if len(crvs)==3:
            srf=ghc.EdgeSurface(crvs[0],crvs[1],crvs[2])
            return srf
        else:
            srf=ghc.EdgeSurface(crvs[0],crvs[1],crvs[2],crvs[3])
            return srf
    
    #++++++++++++++++++++++++02相关点方法++++++++++++++++++++++
    #2.1转角点
    def Pts(self):
        return ghc.Discontinuity(self.name,1)[0]
    #2.2转角点数目
    def PtsCount(self):
        return len(self.Pts())
        
    #2.3角点平均点
    def AvePt(self):
        return ghc.Average(self.Pts())
    #2.4中点
    def MidPt(self):
        pt_mid=ghc.CurveMiddle(self.name)
        return pt_mid
    #2.5端点
    def EndPts(self):
        pts=[self.name.PointAtStart,self.name.PointAtEnd]
        return pts
    #2.6线在坐标系轴线坐标得最值角点
    def PtPlaneM(self,plane,axis,choose):
        pts=self.Pts()
        pts_sort,indexs_sort=Zp_Pts(pts).SortByPlane(plane,axis)
        return Zp_MaxMin(pts_sort,choose)
    #2.7线中点在坐标系轴线坐标得最值数据！！！
    def PtNumberPlaneM(self,plane,axis,choose):
        pt_m=self.MidPt()
        number_m=Zp_Pt(pt_m).PlaneCoAxis(plane,axis)
        return number_m
    #2.8线断点前三点坐标面2021.4.7
    def Plane(self):
        pts=self.Pts()
        plane=Zp_Pts(pts).Plane()
        return plane
    #2.9线上点的切方向2021.4.15
    def TVectorAtPt(self,pt):
        crv=self.name
        t=ghc.CurveClosestPoint(pt,crv)[1]
        tvector=ghc.EvaluateCurve(crv,t)[1]
        return tvector
    #2.13线中点到线的位置
    def LocationOnCrv(self,crv,outindex=-1):
        midpt=self.MidPt()
        t=ghc.CurveClosestPoint(midpt,crv)[1]
        if outindex==-1:
            return t
        else:
            output=ghc.EvaluateCurve(crv,t)[outindex]
            return output




    #++++++++++++++++++++++++03单线相关线方法++++++++++++++++++++++
    #++++++++++++++++++++++++3.1单线方向系列++++++++++++++++++++++
    #3.1.1线的方向
    def CrvVector(self):
        vector=rg.Vector3d(self.name.PointAtEnd)-rg.Vector3d(self.name.PointAtStart)
        return vector
    #3.1.2线的方向统一通过坐标轴线
    def CrvUnityByPlane(self,plane,axis):
        crv=copy.copy(self.name)
        endpts=self.EndPts()
        ptsn_co=map(lambda x:Zp_Pt(x).PlaneCoAxis(plane,axis),endpts)
        if ptsn_co[0]>ptsn_co[1]:
            crv.Reverse()
        return crv
    #3.1.2.1线的方向统一通过点
    def CrvUnityByPt(self,pt):
        crv=copy.copy(self.name)
        endpts=self.EndPts()
        ds=map(lambda x:pt.DistanceTo(x),endpts)
        if ds[0]>ds[1]:
            crv.Reverse()
        return crv
    #3.1.3线的方向统一通过向量
    def CrvUnityByVector(self,vector):
        if vector=="x":
            vector=rg.Plane.WorldXY.XAxis
        elif vector=="y":
            vector=rg.Plane.WorldXY.YAxis
        elif vector=="z":
            vector=rg.Plane.WorldXY.ZAxis
        else:
            pass
        crv=copy.copy(self.name)
        vto=self.CrvVector()
        if vto*vector<0:
            crv.Reverse()
        return crv
    #3.1.4线的方向统一通过曲线
    def CrvUnityByCrv(self,crv_guid):
        crv=copy.copy(self.name)
        vto=self.CrvVector()
        midpt=self.MidPt()
        t=ghc.CurveClosestPoint(midpt,crv_guid)[1]
        vector_t=ghc.EvaluateCurve(crv_guid,t)[1]
        if ghc.DotProduct(vto,vector_t,False)<0:
            crv.Reverse()
        return crv
    #3.1.5闭合环绕线方向得统一
    def ClosedCrvUnity(self,plane):
        crv=copy.copy(self.name)
        try:
            plane=plane if plane else rg.Plane.WorldXY
        except:
            plane=rg.Plane.WorldXY
        curveorientation=crv.ClosedCurveOrientation(plane)
        if curveorientation==rg.CurveOrientation.Clockwise:
            crv.Reverse()
        return crv
    #3.1.5.1闭合环绕线方向得统一通过线
    def ClosedCrvUnityByCrv(self,crv):
        t=self.LocationOnCrv(crv)
        plane=ghc.PerpFrame(crv,t)
        crv1=self.ClosedCrvUnity(plane)
        return crv1







    #3.1.6闭合环绕线方向以及起点统一
    def ClosedCrvUnityAll(self,plane,seam):
        crv=self.ClosedCrvUnity(plane)
        pts=Zp_Crv(crv).Pts()
        geos_sort,indexs_sort,line,plane=Zp_Pts(pts).SortByCircle(plane,seam)
        pt_s=geos_sort[0]
        t=ghc.CurveClosestPoint(pt_s,crv)[1]
        crv_seam=ghc.Seam(crv,t)
        return crv_seam,plane,line
    #3.1.6.1闭合环绕线方向以及起点统一通过线最近角点
    def ClosedCrvUnityAllByCrv(self,crv):
        crv1=self.ClosedCrvUnityByCrv(crv)
        pts=ghc.Discontinuity(crv1,1)[0]
        ts=ghc.Discontinuity(crv1,1)[1]
        ds=map(lambda x:ghc.CurveClosestPoint(x,crv)[2],pts)
        t=Zp_FollowSort(ds,ts)[0]
        pt_start=Zp_FollowSort(ds,pts)[0]
        crv_seam=ghc.Seam(crv1,t)
        return crv_seam



    #3.1.7通过端点离曲线远近点统一线方法
    def CrvUnityByCrvNear(self,crv_guid):
        crv=copy.copy(self.name)
        endpts=self.EndPts()
        d=map(lambda x:ghc.CurveClosestPoint(x,crv_guid)[2],endpts)
        if d[0]>d[1]:
            crv.Reverse()
        return crv


    #3.1.8 闭合曲线接缝点调整
    def CloseSeam(self,pt):
        crv=self.name
        if ghc.Closed(crv):
            t=ghc.CurveClosestPoint(pt,crv)[1]
            crv=ghc.Seam(crv,t)
        return crv




    #++++++++++++++++++++++++3.2单线其他++++++++++++++++++++++
    #3.2.1内部边线
    def Crvs(self):
        #bug单线自己炸开为空值
        crvs=list(self.name.DuplicateSegments())
        if crvs:
            return list(self.name.DuplicateSegments())
        else:
            return [self.name]
    #3.2.2内部边线数量
    def CrvsCount(self):
        return len(self.Crvs())
    #3.2.3长度最值线
    def CrvsM(self,choose):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetLength(),crvs)
        return Zp_MaxMin(geos_sort,choose)
    #3.2.4坐标最值线(线中点)
    def CrvsPlaneM(self,plane,axis,choose):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:Zp_Crv(x).PtNumberPlaneM(plane,axis,choose),crvs)
        return Zp_MaxMin(geos_sort,choose)
    #3.2.5曲线三点平面
    def ThreePtsPlane(self):
        pt0,pt1=self.EndPts()
        pt2=self.MidPt()
        plane=rg.Plane(pt0,pt1,pt2)
        return plane
    #3.2.6构造线面最近点函数,踩点数目10,后期方法改进
    #先判定起始点是否满足t容差，然后再排序
    def CrvClosePtOnBrep(self,brep,n=10):
        crv=self.name
        pts=self.Pts()
        if ghc.BrepClosestPoint(pts[0],brep)[2]<1:
            return pts[0]
        elif ghc.BrepClosestPoint(pts[1],brep)[2]<1:
            return pts[1]
        else:
            pts=ghc.DivideCurve(crv,n,False)[0]
            d=ghc.BrepClosestPoint(pts,brep)[2]
            d,pts=zip(*sorted(zip(d,pts)))
            return pts[0]

    #3.2.7曲线在面上得垂平面
    def CrvBrepPlane(self,brep):
        crv=self.name
        vector0=Zp_Crv(crv).CrvVector()
        #构造最值面
        pt=self.CrvClosePtOnBrep(brep)
        faces=map(lambda x:x.DuplicateFace(False),brep.Faces)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetArea(),faces)
        srf=geos_sort[-1]
        #构造面上点方向
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        vector1=ghc.EvaluateSurface(srf,pt_uv)[1]
        #构造坐标面
        plane=rg.Plane(pt,vector0,vector1)
        return plane


    #3.2.8曲线在面上得法向曲面
    def CrvBrepCutter(self,brep,length):
        crv=self.name
        pt=self.MidPt()
        #构造最值面
        faces=map(lambda x:x.DuplicateFace(False),brep.Faces)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetArea(),faces)
        srf=geos_sort[-1]
        #构造面上点方向
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        vector=ghc.EvaluateSurface(srf,pt_uv)[1]*length
        #我这里可以调用srf函数！！！牛啊！！！
        #vector=Zp_Srf(srf).Normal()*length
        #构造法向曲面
        crv.Translate(-vector)
        brep_extrude=rg.Surface.CreateExtrusion(crv,vector*2).ToBrep()
        return brep_extrude
    
    #3.2.9指定三折线折点1为切点于第三边相切得倒角线；
    def TreePolyCrvFillet(self):
        pts=self.Pts()
        pt2=ghc.LineXLine(rg.Line(pts[0],pts[1]),rg.Line(pts[3],pts[2]))[2]
        radius=ghc.Distance(pt2,pts[1])
        pt3=ghc.Move(pt2,ghc.Vector2Pt(pts[2],pts[3],True)[0]*radius)[0]
        pts=[pts[0],pts[1],pt3,pts[3]]
        crv1=rg.Line(pts[0],pts[1])
        crv2=ghc.ArcSED(pts[1],pts[2],pts[1]-pts[0])[0]
        crv3=rg.Line(pts[2],pts[3])
        crv=ghc.JoinCurves([crv1,crv2,crv3],False)
        return crv

    #3.2.10曲线变直线
    def CrvToLine(self):
        pts=self. EndPts()
        return rg.Line(pts[0],pts[1])

    #3.2.11曲线拱高值
    def Arch(self):
        line=self.CrvToLine()
        pt0,pt1=self.EndPts()
        avept=self.AvePt()
        midpt=self.MidPt()
        arch=ghc.Distance(avept,midpt)
        return arch

    #3.2.12曲线容差优化弧形或者直线:
    def IsArc(self,t=10):
        if self.Arch()>t:
            return True
        else:
            return False

    #3.2.13曲线容差优化弧形或者直线:
    def ArcOrLine(self,t=10):
        if self.Arch()>t:
            pt0,pt1=self.EndPts()
            avept=self.AvePt()
            midpt=self.MidPt()
            return ghc.Arc3Pt(pt0,midpt,pt1)[0]
        else:
            return self.CrvToLine()

    #3.2.14拱高最值线
    def CrvsArchM(self,choose=-1):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:Zp_Crv(x).Arch(),crvs)
        return Zp_MaxMin(geos_sort,choose)




#AAA索引——群线类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++1.群线类++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Crvs(object):
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #++++++++++++++++++++++++00属性+++++++++++++++++++++++++ 
    def __init__(self,name):
        self.name=name
        self.type="群线"
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++01群线通用方法++++++++++++++++++++++
    def Srf(self):
        crvs=self.name
        if len(crvs)==2:
            surface=ghc.EdgeSurface(crvs[0],crvs[1])
        elif len(crvs)==3:
            surface=ghc.EdgeSurface(crvs[0],crvs[1],crvs[2])
        elif len(crvs)==4:
            surface=ghc.EdgeSurface(crvs[0],crvs[1],crvs[2],crvs[3])
        else:
            pass
        return surface







    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++2群线排序系列+++++++++++++++++++++++++++
    #2.0构造数量
    def Count(self):
        return len(self.name)
    #2.1群线长度排序
    def SortByLength(self):
        crvs=self.name
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetLength(),crvs)
        return geos_sort,indexs_sort
    #2.2群线按中点坐标轴排序
    def SortByPlane(self,plane,axis):
        crvs=self.name
        pts=map(lambda x: Zp_Crv(x).MidPt(),crvs)
        geos_sort,indexs_sort=Zp_Pts(pts).SortByPlane(plane,axis)
        crvs_sort=map(lambda x:crvs[x],indexs_sort)
        return crvs_sort,indexs_sort
    #2.3向量排序
    def SortByVector(self,vector):
        crvs=self.name
        vtos=map(lambda x:Zp_Crv(x).CrvVector(),crvs)
        numbers=map(lambda x:ghc.DotProduct(x,vector,True),vtos)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,numbers)
        crvs_sort=map(lambda x:crvs[x],indexs_sort)
        return crvs_sort,indexs_sort
    #2.4辅助线最近t值排序
    def SortByCurve(self,crv_guide):
        crvs=self.name
        pts=map(lambda x:ghc.CurveProximity(crv_guide,x)[0],crvs)
        ts=map(lambda x:ghc.CurveClosestPoint(x,crv_guide)[1],pts)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,ts)
        crvs_sort=map(lambda x:crvs[x],indexs_sort)
        return crvs_sort,indexs_sort
    #2.5最近线排序
    def SortByNear(self,index_s):
        crvs=self.name
        #*构造index组
        group_ci=[(crvs[i],i) for i in range(len(crvs))]
        #构造起始数组
        crv_s=group_ci[index_s]
        crvs_add=[crv_s]
        #构造删除数组
        crvs_del=group_ci
        del crvs_del[index_s]
        #此处可扩写一个通用函数参数函数！
        while len(crvs_del)>0:
            d=map(lambda x:ghc.CurveProximity(crvs_add[-1][0],x[0])[2],crvs_del)
            crvs_del=list(Zp_FollowSort(d,crvs_del))
            crvs_add.append(crvs_del[0])
            del crvs_del[0]
        #元组解组
        crvs_sort=map(lambda x:x[0],crvs_add)
        indexs_sort=map(lambda x:x[1],crvs_add)
        return crvs_sort,indexs_sort
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++3群线其他系列+++++++++++++++++++++++++++
    #3.1顺序线延伸角点连线
    def CrvsConerPts(self,bool):
        crvs=self.name
        if bool:
            #中心引导线调整曲线方向！
            midpts=map(lambda x: Zp_Crv(x).MidPt(),crvs)
            crv_guide=ghc.NurbsCurve(midpts,3,False)[0]
            crvs=map(lambda x:Zp_Crv(x).CrvUnityByCrv(crv_guide),crvs)
            #线近似闭合判定可采用起始点给与bool判定，此处手工给于bool判定
            pts=[]
            for i in range(len(crvs)-1):
                line1=rg.Line(crvs[i].PointAtStart,crvs[i].PointAtEnd)
                line2=rg.Line(crvs[i+1].PointAtStart,crvs[i+1].PointAtEnd)
                pts.append(ghc.LineXLine(line1,line2)[2])
            pts.append(ghc.Line_Line(crvs[-1],crvs[0])[2])
            crv_p=ghc.PolyLine(pts,True)
        else:
            midpts=map(lambda x: Zp_Crv(x).MidPt(),crvs)
            crv_guide=ghc.NurbsCurve(midpts,3,False)[0]
            crvs=map(lambda x:Zp_Crv(x).CrvUnityByCrv(crv_guide),crvs)
            pts=[]
            pts.append(Zp_Crv(crvs[0]).pt0)
            for i in range(len(crvs)-1):
                line1=Zp_Crv(crvs[i]).CrvToLine()
                line2=Zp_Crv(crvs[i+1]).CrvToLine()
                pts.append(ghc.LineXLine(line1,line2)[2])
            pts.append(Zp_Crv(crvs[-1]).pt1)
            crv_p=ghc.PolyLine(pts,False)
        return pts,crv_p
    #3.2坐标面分组线(仅针对多数据)
    #对于树形数据需要改进对树形数据得处理！！不然错误！！！！！
    def PartionByPlane(self,plane):
        crvs=self.name
        #筛选相交线
        crvs_inter=[]
        crvs_up=[]
        crvs_down=[]
        indexs_inter=[]
        indexs_up=[]
        indexs_down=[]
        for i in range(len(crvs)):
            if rg.Intersect.Intersection.CurvePlane(crvs[i],plane,0.1):
                crvs_inter.append(crvs[i])
                indexs_inter.append(i)
            else:
                if Zp_Pt(Zp_Crv(crvs[i]).MidPt()).PlaneCoAxis(plane,"z")>0:
                    crvs_up.append(crvs[i])
                    indexs_up.append(i)
                else:
                    crvs_down.append(crvs[i])
                    indexs_down.append(i)
        crvs_ij=[crvs_inter,crvs_up,crvs_down]
        indexs_ij=[indexs_inter,indexs_up,indexs_down]
        
        crvs_ij=ght.list_to_tree(crvs_ij)
        indexs_ij=ght.list_to_tree(indexs_ij)
        return crvs_ij,indexs_ij



#索引03——面类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++面类++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Srf(object):
    #++++++++++++++++++++++++00属性+++++++++++++++++++++++++ 
    def __init__(self,name):
        self.name=name
        self.type="面"
    #++++++++++++++++++++++++01构造方法++++++++++++++++++++++

    #++++++++++++++++++++++++02相关点方法++++++++++++++++++++++
    #2.1角点
    def Pts(self):
        return self.name.DuplicateVertices()
    #2.2角点平均点
    def PtsCount(self):
        return len(self.Pts())
    #2.3角点平均点
    def AvePt(self):
        return ghc.Average(self.Pts())
    #2.4近似面上中点
    def MidPt(self):
        pt=self.AvePt()
        srf=self.name
        pt_mid=ghc.SurfaceClosestPoint(pt,srf)[0]
        return pt_mid
    #2.5面在坐标系轴线坐标得最值角点
    def PtPlaneM(self,plane,axis,choose):
        pts=self.Pts()
        pts_sort,indexs_sort=Zp_Pts(pts).SortByPlane(plane,axis)
        return Zp_MaxMin(pts_sort,choose)
    #2.6面在坐标系轴线坐标得最值数据
    def PtNumberPlaneM(self,plane,axis,choose):
        pt_m=self.PtPlaneM(plane,axis,choose)
        number_m=Zp_Pt(pt_m).PlaneCoAxis(plane,axis)
        return number_m
    #2.7近似面中点法方向
    def Normal(self):
        pt=self.AvePt()
        srf=self.name
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        vector=ghc.EvaluateSurface(srf,pt_uv)[1]
        return vector
    #2.7.1近似面中点法方向
    def PtNormal(self,pt):
        srf=self.name
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        vector=ghc.EvaluateSurface(srf,pt_uv)[1]
        return vector
    #2.8近似面中点对齐坐标面
    def Plane(self,vector,angle):
        if vector=="x":
            vector=rg.Plane.WorldXY.XAxis
        elif vector=="y":
            vector=rg.Plane.WorldXY.YAxis
        elif vector=="z":
            vector=rg.Plane.WorldXY.ZAxis
        else:
            pass
        pt=self.AvePt()
        srf=self.name
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        plane=ghc.EvaluateSurface(srf,pt_uv)[4]
        plane=ghc.AlignPlane(plane,vector)[0]
        plane=ghc.Rotate(plane,math.radians(angle),plane)[0]
        return plane
    #2.8.1近似面中点根据线对齐坐标面
    def PlaneByCrv(self,crv,angle):
        pt=self.AvePt()
        vector=Zp_Crv(crv).TVectorAtPt(pt)
        plane=self.Plane(vector,angle)
        return plane
    #2.9面缩回
    def Shink(self):
        srf=(self.name).Faces.ShrinkFaces()
        return srf
    #2.10排序点
    def CircleSortPts(self,vector,angle):
        pts=self.Pts()
        if vector=="x":
            vector=rg.Plane.WorldXY.XAxis
        elif vector=="y":
            vector=rg.Plane.WorldXY.YAxis
        elif vector=="z":
            vector=rg.Plane.WorldXY.ZAxis
        else:
            pass
        plane=self.Plane(vector,angle)
        pts_sort=(Zp_Pts(pts).SortByCircle(plane,0.5))[0]
        return pts_sort
    #2.11面中点到其他面得距离
    def DistanceToSrf(self,brep):
        midpt=self.MidPt()
        d=ghc.BrepClosestPoint(midpt,brep)[2]
        return d
    #2.12平板单双曲板类型判定群点
    def TypeBoolPts(self):
        pts=list(self.Pts())
        crvs=self.Crvs()
        crvs_midpt=map(lambda x:ghc.CurveMiddle(x),crvs)
        midpt=[self.MidPt()]
        typepts=pts+crvs_midpt+midpt
        return typepts
    #2.13面中点到线的位置
    def LocationOnCrv(self,crv,outindex=-1):
        midpt=self.MidPt()
        t=ghc.CurveClosestPoint(midpt,crv)[1]
        if outindex==-1:
            return t
        else:
            output=ghc.EvaluateCurve(crv,t)[outindex]
            return output
    
    
    
    #++++++++++++++++++++++++3单线其他++++++++++++++++++++++
    #3.1内部边线
    def Crvs(self):
        crvs=(self.name).DuplicateEdgeCurves()
        return crvs
    #3.2内部边线数量
    def CrvsCount(self):
        crvs=self.Crvs()
        n=len(crvs)
        return n
    #3.3长度最值线
    def CrvsM(self,choose):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetLength(),crvs)
        return Zp_MaxMin(geos_sort,choose)
    #3.4坐标最值线
    def CrvsPlaneM(self,plane,axis,choose):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:Zp_Crv(x).PtNumberPlaneM(plane,axis,choose),crvs)
        return Zp_MaxMin(geos_sort,choose)
    #3.5梯形判定
    def UpDivisionDown(self,plane,axis):
        crv_up=self.CrvsPlaneM(plane,axis,"max").GetLength()
        crv_down=self.CrvsPlaneM(plane,axis,"min").GetLength()
        return crv_up/crv_down
    #3.7判定一个brep得每个面得边线是否等于n
    def IsBrepFaceCrvsNumber(self,n=4):
        brep=self.name
        faces=Zp_Brep(brep).Faces()
        bool=True
        for face in faces:
            crvscount=Zp_Brep(face).CrvsCount()
            if crvscount<>n:
                bool=False
                break
        return bool
    #3.8获得不满足边线数量规则得碎面：
    def FacesOfIsBrepFaceCrvsNumber(self,n=4):
        brep=self.name
        faces=Zp_Brep(brep).Faces()
        errorfaces=[]
        for face in faces:
            crvscount=Zp_Brep(face).CrvsCount()
            if crvscount<>n:
                errorfaces.append(face)
        return errorfaces




    #++++++++++++++++++++++++4面属性++++++++++++++++++++++
    #4.1内部面
    def Faces(self):
        brep=self.name
        faces=map(lambda x:x.DuplicateFace(False),brep.Faces)
        return faces
    #4.2内部面数量
    def FacesCount(self):
        faces=self.Faces()
        n=len(faces)
        return n
    #4.3内部最值面#错误等待修正
    def FacesM(self,choose):
        faces=self.Faces()
        geos_sort,indexs_sort=Zp_Srfs(faces).SortByArea()
        return Zp_MaxMin(geos_sort,choose)
    #4.4坐标轴最值面#错误等待修正
    def FacesPlaneM(self,plane,axis,choose):
        faces=self.Faces()
        geos_sort,indexs_sort=Zp_Srfs(faces).SortByPlane(plane,axis)
        return Zp_MaxMin(geos_sort,choose)









#AAA索引——群面类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++1.群面类++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Srfs(object):
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #++++++++++++++++++++++++00属性+++++++++++++++++++++++++ 
    def __init__(self,name):
        self.name=name
        self.type="群面"
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++01群面通用方法++++++++++++++++++++++
    def Join(self,t=5):
        srfs=self.name
        brep=rg.Brep.JoinBreps(breps,t)
        return brep
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++01群线通用方法++++++++++++++++++++++
 
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++2群面排序系列+++++++++++++++++++++++++++
    #2.0构造数量
    def Count(self):
        return len(self.name)
    #2.1群面按面积排序
    def SortByArea(self):
        srfs=self.name
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetArea(),srfs)
        return geos_sort,indexs_sort
    #2.2坐标轴排序
    def SortByPlane(self,plane,axis):
        srfs=self.name
        pts=map(lambda x:Zp_Srf(x).AvePt(),srfs)
        geos_sort,indexs_sort=Zp_Pts(pts).SortByPlane(plane,axis)
        srfs_sort=map(lambda x:srfs[x],indexs_sort)
        return srfs_sort,indexs_sort
    #2.3向量排序
    def SortByVector(self,vector):
        srfs=self.name
        vtos=map(lambda x:Zp_Srf(x).Normal(),srfs)
        numbers=map(lambda x:ghc.DotProduct(x,vector,True),vtos)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,numbers)
        srfs_sort=map(lambda x:srfs[x],indexs_sort)
        return srfs_sort,indexs_sort
    #2.4辅助线最近t值排序
    def SortByCurve(self,crv_guide):
        srfs=self.name
        pts=map(lambda x:Zp_Srf(x).AvePt(),srfs)
        ts=map(lambda x:ghc.CurveClosestPoint(x,crv_guide)[1],pts)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,ts)
        srfs_sort=map(lambda x:srfs[x],indexs_sort)
        return srfs_sort,indexs_sort
    #2.5最近物件排序(可改写为泛类，函数系列，方便调用修改)
    def SortByNear(self,index_s):
        #*构造index组
        srfs=self.name
        group_ci=[(srfs[i],i) for i in range(len(srfs))]
        #构造起始数组
        srf_s=group_ci[index_s]
        srfs_add=[srf_s]
        #构造删除数组
        srfs_del=group_ci
        del srfs_del[index_s]
        #此处可扩写一个通用函数参数函数！
        while len(srfs_del)>0:
            d=map(lambda x:(Zp_Srf(srfs_add[-1][0]).AvePt()).DistanceTo(Zp_Srf(x[0]).AvePt()),srfs_del)
            srfs_del=list(Zp_FollowSort(d,srfs_del))
            srfs_add.append(srfs_del[0])
            del srfs_del[0]
        #元组解组
        srfs_sort=map(lambda x:x[0],srfs_add)
        indexs_sort=map(lambda x:x[1],srfs_add)
        return srfs_sort,indexs_sort
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++3群面其他系列+++++++++++++++++++++++++++
    #3.1坐标面分组面(仅针对多数据)
    #对于树形数据需要改进对树形数据得处理！！不然错误！！！！！
    def PartionByPlane(self,plane):
        srfs=self.name
        #筛选相交线
        srfs_inter=[]
        srfs_up=[]
        srfs_down=[]
        indexs_inter=[]
        indexs_up=[]
        indexs_down=[]
        for i in range(len(srfs)):
            if rg.Intersect.Intersection.BrepPlane(srfs[i],plane,0.1)[0]:
                srfs_inter.append(srfs[i])
                indexs_inter.append(i)
            else:
                if Zp_Pt(Zp_Srf(srfs[i]).MidPt()).PlaneCoAxis(plane,"z")>0:
                    srfs_up.append(srfs[i])
                    indexs_up.append(i)
                else:
                    srfs_down.append(srfs[i])
                    indexs_down.append(i)
        srfs_ij=[srfs_inter,srfs_up,srfs_down]
        indexs_ij=[indexs_inter,indexs_up,indexs_down]
        
        srfs_ij=ght.list_to_tree(srfs_ij)
        indexs_ij=ght.list_to_tree(indexs_ij)
        return srfs_ij,indexs_ij
    #3.2对群breps进行碎面边线数目判定，并通过bool值返回错位得碎面；
    def IsBrepsFaceCrvsNumber(self,n=4,displayerror=True):
        breps=self.name
        bool=True
        errorfaces=[]
        for brep in breps:
            bool=bool and Zp_Brep(brep).IsBrepFaceCrvsNumber(n)
            if displayerror:
                errorfaces=errorfaces+Zp_Brep(brep).FacesOfIsBrepFaceCrvsNumber(n)
        return bool,errorfaces



#AAA索引——多重面类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++面类+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Brep(object):
    #++++++++++++++++++++++++00属性+++++++++++++++++++++++++ 
    def __init__(self,name):
        self.name=name
        self.type="多重面"
    #++++++++++++++++++++++++01构造方法++++++++++++++++++++++
    #1.1 
    #++++++++++++++++++++++++02相关点方法++++++++++++++++++++++
    #2.1角点
    def Pts(self):
        return self.name.DuplicateVertices()
    #2.2角点平均点
    def PtsCount(self):
        return len(self.Pts())
    #2.3角点平均点
    def AvePt(self):
        return ghc.Average(self.Pts())
    #2.4近似面上中点
    def MidPt(self):
        pt=self.AvePt()
        brep=self.name
        #最大面
        srfs=map(lambda x:x.DuplicateFace(False),brep.Faces)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x: x.GetArea(),srfs)
        srf=geos_sort[-1]
        pt_mid=ghc.SurfaceClosestPoint(pt,srf)[0]
        return pt_mid
    #2.5面在坐标系轴线坐标得最值角点
    def PtPlaneM(self,plane,axis,choose):
        pts=self.Pts()
        pts_sort,indexs_sort=Zp_Pts(pts).SortByPlane(plane,axis)
        return Zp_MaxMin(pts_sort,choose)
    #2.6面在坐标系轴线坐标得最值数据
    def PtNumberPlaneM(self,plane,axis,choose):
        pt_m=self.PtPlaneM(plane,axis,choose)
        number_m=Zp_Pt(pt_m).PlaneCoAxis(plane,axis)
        return number_m
    #2.7近似面中点法方向
    def Normal(self):
        pt=self.AvePt()
        brep=self.name
        #最大面
        srfs=map(lambda x:x.DuplicateFace(False),brep.Faces)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x: x.GetArea(),srfs)
        srf=geos_sort[-1]
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        vector=ghc.EvaluateSurface(srf,pt_uv)[1]
        return vector
    #2.8近似面中点对齐坐标面
    def Plane(self,vector,angle):
        pt=self.AvePt()
        brep=self.name
        #最大面
        srfs=map(lambda x:x.DuplicateFace(False),brep.Faces)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x: x.GetArea(),srfs)
        srf=geos_sort[-1]
        pt_uv=ghc.SurfaceClosestPoint(pt,srf)[1]
        plane=ghc.EvaluateSurface(srf,pt_uv)[4]
        plane=ghc.AlignPlane(plane,vector)[0]
        plane=ghc.Rotate(plane,math.radians(angle),plane)[0]
        return plane
    #2.8.1近似面中点根据线对齐坐标面
    def PlaneByCrv(self,crv,angle):
        pt=self.AvePt()
        vector=Zp_Crv(crv).TVectorAtPt(pt)
        plane=self.Plane(vector,angle)
        return plane
    
    #2.10排序点
    def CircleSortPts(self,vector,angle):
        pts=self.Pts()
        if vector=="x":
            vector=rg.Plane.WorldXY.XAxis
        elif vector=="y":
            vector=rg.Plane.WorldXY.YAxis
        elif vector=="z":
            vector=rg.Plane.WorldXY.ZAxis
        else:
            pass
        plane=self.Plane(vector,angle)
        pts_sort=(Zp_Pts(pts).SortByCircle(plane,0.5))[0]
        return pts_sort
    #2.11面中点到其他面得距离
    def DistanceToSrf(self,brep):
        midpt=self.MidPt()
        d=ghc.BrepClosestPoint(midpt,brep)[2]
        return d
    #2.12面中点到其他线得t值
    def LocationOnCrv(self,crv,outindex=-1):
        midpt=self.MidPt()
        t=ghc.CurveClosestPoint(midpt,crv)[1]
        if outindex==-1:
            return t
        else:
            output=ghc.EvaluateCurve(crv,t)[outindex]
            return output
    #++++++++++++++++++++++++3线属性++++++++++++++++++++++
    #3.1内部边线
    def Crvs(self):
        crvs=(self.name).DuplicateEdgeCurves()
        return crvs
    #3.2内部边线数量
    def CrvsCount(self):
        crvs=self.Crvs()
        n=len(crvs)
        return n
    #3.3长度最值线
    def CrvsM(self,choose):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetLength(),crvs)
        return Zp_MaxMin(geos_sort,choose)
    #3.4坐标最值线
    def CrvsPlaneM(self,plane,axis,choose):
        crvs=self.Crvs()
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:Zp_Crv(x).PtNumberPlaneM(plane,axis,choose),crvs)
        return Zp_MaxMin(geos_sort,choose)
    #3.7判定一个brep得每个面得边线是否等于n
    def IsBrepFaceCrvsNumber(self,n=4):
        brep=self.name
        faces=Zp_Brep(brep).Faces()
        bool=True
        for face in faces:
            crvscount=Zp_Brep(face).CrvsCount()
            if crvscount<>n:
                bool=False
                break
        return bool
    #3.8获得不满足边线数量规则得碎面：
    def FacesOfIsBrepFaceCrvsNumber(self,n=4):
        brep=self.name
        faces=Zp_Brep(brep).Faces()
        errorfaces=[]
        for face in faces:
            crvscount=Zp_Brep(face).CrvsCount()
            if crvscount<>n:
                errorfaces.append(face)
        return errorfaces
    #++++++++++++++++++++++++4面属性++++++++++++++++++++++
    #4.1内部面
    def Faces(self):
        brep=self.name
        faces=map(lambda x:x.DuplicateFace(False),brep.Faces)
        return faces
    #4.2内部面数量
    def FacesCount(self):
        faces=self.Faces()
        n=len(faces)
        return n
    #4.3内部最值面
    def FacesM(self,choose):
        faces=self.Faces()
        geos_sort,indexs_sort=Zp_Srfs(faces).SortByArea()
        return Zp_MaxMin(geos_sort,choose)
    #4.4坐标轴最值面
    def FacesPlaneM(self,plane,axis,choose):
        faces=self.Faces()
        geos_sort,indexs_sort=Zp_Srfs(faces).SortByPlane(plane,axis)
        return Zp_MaxMin(geos_sort,choose)
    #4.5向量排序最值面
    def FacesVectorM(self,vector,choose):
        faces=self.Faces()
        if vector=="x":
            vector=rg.Plane.WorldXY.XAxis
        elif vector=="y":
            vector=rg.Plane.WorldXY.YAxis
        elif vector=="z":
            vector=rg.Plane.WorldXY.ZAxis
        else:
            pass
        geos_sort,indexs_sort=Zp_Srfs(faces).SortByVector(vector)
        return Zp_MaxMin(geos_sort,choose)
    #4.6多重面长边垂面截面线
    def SectionCrvs(self):
        crv=self.CrvsM("max")
        crv.Domain=rg.Interval(0,1)
        plane=ghc.PerpFrame(crv,0.5)
        section_crvs=ghc.BrepXPlane(self.name,plane)[0]
        return section_crvs









#AAA索引——群多重面类
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++1.群多重面类++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Zp_Breps(object):
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #++++++++++++++++++++++++00属性+++++++++++++++++++++++++ 
    def __init__(self,name):
        self.name=name
        self.type="群多重面"
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++01群面通用方法++++++++++++++++++++++
    def Join(self,t=5):
        srfs=self.name
        brep=rg.Brep.JoinBreps(breps,t)
        return brep
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++01群线通用方法++++++++++++++++++++++

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++2群面排序系列+++++++++++++++++++++++++++
    #2.0构造数量
    def Count(self):
        return len(self.name)
    #2.1群面按面积排序
    def SortByArea(self):
        breps=self.name
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x.GetArea(),breps)
        return geos_sort,indexs_sort
    #2.2坐标轴排序
    def SortByPlane(self,plane,axis):
        breps=self.name
        pts=map(lambda x:Zp_Brep(x).AvePt(),breps)
        geos_sort,indexs_sort=Zp_Pts(pts).SortByPlane(plane,axis)
        breps_sort=map(lambda x:breps[x],indexs_sort)
        return breps_sort,indexs_sort
    #2.3向量排序
    def SortByVector(self,vector):
        breps=self.name
        vtos=map(lambda x:Zp_Brep(x).Normal(),breps)
        numbers=map(lambda x:ghc.DotProduct(x,vector,True),vtos)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,numbers)
        breps_sort=map(lambda x:breps[x],indexs_sort)
        return breps_sort,indexs_sort
    #2.4辅助线最近t值排序
    def SortByCurve(self,crv_guide):
        breps=self.name
        pts=map(lambda x:Zp_Brep(x).AvePt(),breps)
        ts=map(lambda x:ghc.CurveClosestPoint(x,crv_guide)[1],pts)
        numbers_sort,indexs_sort,geos_sort=Zp_Sort(lambda x:x,ts)
        breps_sort=map(lambda x:breps[x],indexs_sort)
        return breps_sort,indexs_sort
    #2.5最近物件排序(可改写为泛类，函数系列，方便调用修改)
    def SortByNear(self,index_s):
        #*构造index组
        breps=self.name
        group_ci=[(breps[i],i) for i in range(len(breps))]
        #构造起始数组
        brep_s=group_ci[index_s]
        breps_add=[brep_s]
        #构造删除数组
        breps_del=group_ci
        del breps_del[index_s]
        #此处可扩写一个通用函数参数函数！
        while len(breps_del)>0:
            d=map(lambda x:(Zp_Srf(breps_add[-1][0]).AvePt()).DistanceTo(Zp_Srf(x[0]).AvePt()),breps_del)
            breps_del=list(Zp_FollowSort(d,breps_del))
            breps_add.append(breps_del[0])
            del breps_del[0]
        #元组解组
        breps_sort=map(lambda x:x[0],breps_add)
        indexs_sort=map(lambda x:x[1],breps_add)
        return breps_sort,indexs_sort
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++3群面其他系列+++++++++++++++++++++++++++
    #3.1对群breps进行碎面边线数目判定，并通过bool值返回错位得碎面；
    def IsBrepsFaceCrvsNumber(self,n=4,displayerror=True):
        breps=self.name
        bool=True
        errorfaces=[]
        for brep in breps:
            bool=bool and Zp_Brep(brep).IsBrepFaceCrvsNumber(n)
            if displayerror:
                errorfaces=errorfaces+Zp_Brep(brep).FacesOfIsBrepFaceCrvsNumber(n)
        return bool,errorfaces



#等待添加扩展












#说明，eval,不含geo方式参数，可以直接调用函数，方便整体修正。关键有geo方式参数函数，调用失败！此代码写到具体电池里了。
#AAA索引-单物件属性输出
#++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++
#类型判定系列！
#单一物件
#+++++++++++++++++++++++++++++方法选择++++++++++++++++++++++++++++++++++
#类型判定，输出特定属性
#类型判别电池：     pt,crv,srf,brep,str,number
#list类型判别电池： pts,crvs,srfs,breps,strs,numbers

#物件类型代码字符化代码
def Zp_GeoTypeAndCode(geo,str):
    if type(geo)==System.Guid:
        geo=rs.coercegeometry(geo)
        #判定点
        if isinstance(geo, rg.Point):
            geo=geo.Location
            str_unit="Zp_Pt(geo)."+str
        elif isinstance(geo, rg.Point3d):
            str_unit="Zp_Pt(geo)."+str
        #判定线
        elif isinstance(geo, rg.Curve):
            str_unit="Zp_Crv(geo)."+str
        #判定面/brep
        elif isinstance(geo, rg.Brep):
            if len(list(geo.Faces))==1:
                str_unit="Zp_Srf(geo)."+str
            else:
                str_unit="Zp_Brep(geo)."+str
        else:
            pass
    #判定文字还是数字
    elif type(geo)==System.String or type(geo)==type(0.2) or type(geo)==type(5):
        #数字判定
        try:
            number=float(geo)
            bool=True
            geo=number
        except:
            bool=False
        if bool:
            str_unit="Zp_Number(geo)."+str
        else:
            str_unit="Zp_Str(geo)."+str
    #判定是否为gh物件
    else:
        #判定点
        if isinstance(geo, rg.Point):
            geo=geo.Location
            str_unit="Zp_Pt(geo)."+str
        elif isinstance(geo, rg.Point3d):
            str_unit="Zp_Pt(geo)."+str
        #判定线
        elif isinstance(geo, rg.Curve):
            str_unit="Zp_Crv(geo)."+str
        #判定面/brep
        elif isinstance(geo, rg.Brep):
            if len(list(geo.Faces))==1:
                str_unit="Zp_Srf(geo)."+str
            else:
                str_unit="Zp_Brep(geo)."+str
        else:
            pass
    return geo,str_unit


#AAA索引-群物件属性输出
#++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++
#类型判定系列！
#群物件
#+++++++++++++++++++++++++++++方法选择++++++++++++++++++++++++++++++++++
#类型判定，输出特定属性
def Zp_GeosTypeAndCode(geos,str):
    if type(geos[0])==System.Guid:
        
        geos=map(lambda x:rs.coercegeometry(x),geos)
        #判定点
        if isinstance(geos[0], rg.Point):
            geos_pts=map(lambda x:x.Location,geos)
            geos=geos_pts
            str_unit="Zp_Pts(geos)."+str
        elif isinstance(geos[0], rg.Point3d):
            str_unit="Zp_Pts(geos)."+str
        #判定线
        elif isinstance(geos[0], rg.Curve):
            str_unit="Zp_Crvs(geos)."+str
        #判定面/brep
        elif isinstance(geos[0], rg.Brep):
            if len(list(geos[0].Faces))==1:
                str_unit="Zp_Srfs(geos)."+str
            else:
                str_unit="Zp_Breps(geos)."+str
        else:
            pass
    #判定文字还是数字
    else:
        #数字判定
        try:
            numbers=map(lambda x:float(x),geos)
            bool=True
            geos=numbers
        except:
            bool=False
        if bool:
            str_unit="Zp_Number(geos)."+str
        else:
            str_unit="Zp_Str(geos)."+str
    return geos,str_unit

"""
#AAA索引-群物件条件筛选
#++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++
#类型判定系列！
#+++++++++++++++++++++++++++++方法选择++++++++++++++++++++++++++++++++++
#单类型判定，输出特定属性
def Zp_GeoTypePropertyBool(geo,str):
    #判定点
    if isinstance(geo, rg.Point):
        geo=geo.Location
        str_unit="Zp_Pt(geo)."+str
    elif isinstance(geo, rg.Point3d):
        str_unit="Zp_Pt(geo)."+str
    #判定线
    elif isinstance(geo, rg.Curve):
        str_unit="Zp_Crv(geo)."+str
    #判定面/brep
    elif isinstance(geo, rg.Brep):
        if len(list(geo.Faces))==1:
            str_unit="Zp_Srf(geo)."+str
        else:
            str_unit="Zp_Brep(geo)."+str
    property=eval(str_unit)
    return property
#+++++++++++++++++++++++++++++多条件判定函数++++++++++++++++++++++++++++++++++
#定义一个多条件选择函数,geo仅为单参数
def Zp_Conditions(conditions,geo):
    n=len(conditions)
    if n==0:
        print "0"
        bool=True
        
    elif n==1:
        if conditions[0]=="":
            print "1 and None"
            bool=True
        else:
            print "1 and True"
            bool=Zp_GeoTypePropertyBool(geo,conditions[0])
    elif n>1 and reduce(lambda x,y:x==""+y=="",conditions):
        print "n and None"
        bool=True
    else:
        print "n and True"
        bool=Zp_GeoTypePropertyBool(geo,conditions[0])
        print bool
        why=str(bool)
        for i in range(n-1):
            why=why+str(Zp_GeoTypePropertyBool(geo,conditions[i+1]))
            bool=bool+Zp_GeoTypePropertyBool(geo,conditions[i+1])
        bool=(bool==n)
    return bool,why

#筛选条件函数；
def Zp_Filter(conditions,geos):
    geos_filter=[]
    geos_filterout=[]
    why=[]
    index=[]#等待添加！
    for i in range(len(geos)):
        if Zp_Conditions(conditions,geos[i])[0]:
            geos_filter.append(geos[i])
        else:
            geos_filterout.append(geos[i])
        why.append(Zp_Conditions(conditions,geos[i])[1])
    return geos_filter,geos_filterout,why
"""




#函数测试

#a=Zp_Crv(x).TreePolyCrvFillet()