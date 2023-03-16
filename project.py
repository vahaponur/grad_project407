import pyomo
from pyomo.environ import *
from pyomo.opt import SolverFactory




M=AbstractModel()

#commodities
M.c=Set()

#locations
M.l=Set()

#Params
M.Cos=Param(M.l,M.l)
M.Dem=Param(M.l,M.c)
M.Cap=Param(M.l)

#Dec Var
M.X=Var(M.c,M.l,M.l,within=NonNegativeReals)

def value_rule(model):
    return sum(model.Cos[i,j]*model.X[k,i,j] for k,i,j in model.c*model.l*model.l) 
#ObjFunc
M.value=Objective(rule=value_rule,sense=minimize)

def demand_rule(model,i,k):
    
    if model.Dem[i,k]<0 and i!=11 and i!=13:
        return sum(model.X[k,j,i] - model.X[k,i,j]  for j in model.l) == -model.Dem[i,k]
    elif model.Dem[i,k]>0 and i!=11 and i!=13: #suppl node check et
        return sum(model.X[k,i,j] for j in model.l) <= model.Dem[i,k]
    elif i==11 or i==13:
        return sum(0.85*model.X[k,j,i]-model.X[k,i,j] for j in model.l) == 0
    else:
        return sum(model.X[k,j,i]-model.X[k,i,j] for j in model.l) ==0
def cap_rule(model,i):
    return sum(model.X[k,j,i] for k,j in model.c*model.l) <= model.Cap[i]

M.demand=Constraint(M.l,M.c,rule=demand_rule)
M.capacity=Constraint(M.l,rule=cap_rule)
data=DataPortal(model=M)
#read locations
data.load(filename="pythondata.xlsx", range="ltable", format='set', set='l')
#read commodities
data.load(filename="pythondata.xlsx", range="ctable", format='set', set='c')
#read demands
data.load(filename="pythondata.xlsx", range="Demtable", param='Dem',format="array")
#read capasities
data.load(filename="pythondata.xlsx", range="Captable",index='l', param='Cap')
#read costs
data.load(filename="pythondata.xlsx", range="Costabler", param='Cos',format="array")
instance = M.create_instance(data)

optimizer=SolverFactory("glpk")
optimizer.solve(instance)
instance.display()






