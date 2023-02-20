import pyodbc
server = '172.16.17.149'
database = 'testautomatici'
username = "sa"
password = "B310m3tti"
driver= '{ODBC Driver 18 for SQL Server}'
print ()
with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password + ';Trust Server Certificate=false;Encrypt=no') as conn:
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO test(pc,titolo,pagina,tcaricamento,timeouts) VALUES ('1','1','1','1','1')")
