import pyorc
import pandas as pd 
data = open("ce5fc7da-2893-4d22-841b-31436c7a3728.orc",'rb')
reader = pyorc.Reader(data)
columns = reader.schema.fields
columns =[col_name for col_idx,col_name in sorted(
[
    (reader.schema.find_column_id(c), c) for c in columns   
]
)]
df=pd.DataFrame(reader,columns=columns)

total = 0
for i in range(df.shape[0]):
    if "raw" in df.loc[i, "key"]:
        print(df.loc[i, "key"])
        total += 1
        
print("Clean folders amount", total) 