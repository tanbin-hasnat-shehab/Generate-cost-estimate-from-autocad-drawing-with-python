import pypyodbc
from datetime import date
import re


class RSEPS:
    
    def __init__(self,*args,**kwargs):
        self.version=kwargs.get('version','2022')
        if self.version=='2022':
            self.con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'\
                          r'DBQ=C:\RSEPS_2022\RSEPS_Back.mdb;PWD=dartalika'

            self.conn = pypyodbc.connect(self.con_string)
         
            self.cursor = self.conn.cursor()
        else:
            self.con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'\
                          r'DBQ=C:\RSEPS\RSEPS_Back.mdb;PWD=dartalika'

            self.conn = pypyodbc.connect(self.con_string)
         
            self.cursor = self.conn.cursor()

        

        #self.location=kwargs.get('location','TONGIBARI')
        self.location=self.existing_upazila()
        self.cursor.execute('SELECT * FROM GeoCode')
        G_code=self.cursor.fetchall()
        for row in G_code:
            if row[4]==self.location:
                first_cd=row[0]
                #print(row)
                break
        self.cursor.execute('SELECT * FROM Estimate')
        ss=self.cursor.fetchall()
        mid_list=[]
        last_list=[]
        for row in ss:
            tr1=row[0].split('-')
            mid_list.append(int(tr1[1]))
            last_list.append(int(tr1[2]))
        self.scheme_code=kwargs.get('scheme_code','O')
        ifnew=False
        if self.scheme_code=='O':
            self.scheme_code=str(first_cd)+'-'+str(max(mid_list))+'-'+str(max(last_list)+1)
            ifnew=True
        #self.scheme_code=kwargs.get('scheme_code','40391-24-10017')
        self.scheme_name=kwargs.get('scheme_name','etimate blank')
        self.today1 = str(date.today())
        self.today2=self.today1.split('-')
        self.date_txt=self.today2[1]+'/'+self.today2[2]+'/'+self.today2[0]
        #print(self.scheme_code)
        self.sc_list=self.scheme_code.split('-')
        self.road_id=self.sc_list[0]

        

        self.cursor.execute('SELECT * FROM Estimate')
        Existing_Dist_codes=self.cursor.fetchall()
        existing_dist_code=Existing_Dist_codes[-1][7]

        
        #self.Estimate_input=kwargs.get('Estimate_input',[''])
        #detail [scheme_code,scheme_name,date,1,1,40391,0,497,40391,0,1,24,15,0,0,0,-1]
        if ifnew==True:
            self.Estimate_input =[[f'{self.scheme_code}',f'{self.scheme_name}',f'{self.date_txt}',1,1,first_cd,0,existing_dist_code,first_cd,0,1,24,16,0,0,0,-1]]
 
        

    def input_data(self,*args,**kwargs):
        try:
            self.cursor.executemany('INSERT INTO Estimate VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', self.Estimate_input)
            self.conn.commit()
        except:
            pass
        estimate_input=kwargs.get('estimate_input',[''])
        brk_string_to_put=kwargs.get('break_up_string','')
        


        #######################################detail [item_code,serial,Deduction for 1,Description,L,B,H,Result,No_item]

        #############to be [sc code,item code,'O',serial,deduction 0,description,L,B,H,Result,No of item,0,'No remark']
        try:
            Item_inp =[
                    [f'{self.scheme_code}',f'{estimate_input[0]}','O',estimate_input[1]]
                    ]
         
            self.cursor.executemany('INSERT INTO EstItem VALUES (?,?,?,?)', Item_inp)
            self.conn.commit()
            #print('Data Inserted')
        except:
            pass

        if estimate_input[3]==None:
            estimate_input[3]='  '


        

        detail_input=[[
            self.scheme_code,estimate_input[0],'O',estimate_input[1],estimate_input[2],estimate_input[3],
                estimate_input[4],estimate_input[5],estimate_input[6],estimate_input[7],estimate_input[8],1,'No Remarks'
                ]]
        self.cursor.executemany('INSERT INTO EstimateDetail VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', detail_input)
        self.conn.commit()
        #print('Data Inserted')


    def get_data(self,*args,**kwargs):
        scheme_code_to_fetch=kwargs.get('scheme_code','')
        self.cursor.execute('SELECT * FROM Estimate')
        name_list=self.cursor.fetchall()
        for row in name_list:
            if row[0]==scheme_code_to_fetch:
                self.estimate_name=row[1]
                break


        self.cursor.execute('SELECT * FROM EstimateDetail')
        detail_data=self.cursor.fetchall()

        
        it_list=[]
        for row in detail_data:
            if scheme_code_to_fetch==row[0]:
                string1=''
                string1=str(row[1])+'|'+str(row[3])+'|'+str(0)+'|'+str(row[5])+'|'+str(row[6])+'|'+str(row[7])+'|'+str(row[8])+'|'+str(row[9])+'|'+str(row[10])
                it_list.append(string1)
        
        return self.estimate_name,it_list

    def existing_upazila(self):
        self.cursor.execute('SELECT * FROM Estimate')
        ext_name_list=self.cursor.fetchall()
        ext_upz=ext_name_list[-1]
        ext_upz_sc_code=ext_upz[0]
        l1=ext_upz_sc_code.split('-')
        up_code_ex=l1[0]
        #print(up_code_ex)
        self.cursor.execute('SELECT * FROM GeoCode')
        G_code1=self.cursor.fetchall()
        for row in G_code1:
            #print(type(row[0]))
            if row[0]==int(up_code_ex):
                name_of_ex_upz=row[4]
                #print(name_of_ex_upz)
                break
        return name_of_ex_upz






    def input_salvage(self,*args,**kwargs):
        self.salvage_input=kwargs.get('salvage_input',[])
        #[    item code      ,1 for 1st class brick,        No of bricks in 1 sqm or cum   ]
        try:
            Item_inp =[
                    [f'{self.scheme_code}',f'{self.salvage_input[0]}','O']
                    ]
         
            self.cursor.executemany('INSERT INTO SalvageItem VALUES (?,?,?)', Item_inp)
            self.conn.commit()
            #print('Data Inserted')
        except:
            pass

        self.cursor.execute('SELECT * FROM EstimateDetail')
        all_data_list=self.cursor.fetchall()
        pos_sum=0
        neg_sum=0
        
        for row in all_data_list:
            if row[0]==self.scheme_code and row[1]==self.salvage_input[0] and row[4]==0 and row[9]!=None:
                pos_sum+=(row[9]*row[10])
            if row[0]==self.scheme_code and row[1]==self.salvage_input[0] and row[4]==1 and row[9]!=None:
                neg_sum+=(row[9]*row[10])
        total_amount_sal=(pos_sum-neg_sum)*self.salvage_input[2]

        sal_detail=[[
            self.scheme_code,self.salvage_input[0],'O',self.salvage_input[1],self.salvage_input[2],1,total_amount_sal
                ]]
        self.cursor.executemany('INSERT INTO SalvageItemDetail VALUES (?,?,?,?,?,?,?)', sal_detail)
        self.conn.commit()
        #print('Data Inserted')

    def get_block_names_in_src_txt(self):
        name_arr=[]
        with open('src.txt', 'r') as f:
            lines = f.readlines()
        for line in lines:
            if 'def' in line:
                tr1=line.split(' ', 1)
                tr2=tr1[1].split('(')
                name_arr.append(tr2[0])
        return name_arr







