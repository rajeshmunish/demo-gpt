import pyodbc as odbc

# DF Prod database details
#SERVER = 'ubti-p-df-ssvr.database.windows.net'
#DATABASE = 'DiligenceFabric'
#USERNAME = 'adminsql'
#PASSWORD = 'P@$$w0rd'

# DF Dev Test database details
#SERVER = 'ubti-d-ssvr-03.database.windows.net'
#DATABASE = 'DFDevTest'
#USERNAME = 'sqladmin'
#PASSWORD = 'welcome123#'

# FinIN Prod database details
#SERVER = 'UBTI-S-DEVSQL16'
#DATABASE = 'FinMetaPro'
#USERNAME = 'FsDevUser'
#PASSWORD = 'P@$$w0rd'
#DRIVER_NAME = 'SQL SERVER'
DRIVER_NAME = 'FreeTDS'
def handle_sql_variant_as_string(value):
    return value.decode('utf-16le')

def create_connection():
    """ Create or connect to an SQL server database """
    conn = None;
    # try:
    
    connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    conn = odbc.connect(connectionString)
    # conn = pyodbc.connect('Driver={FreeTDS};'
    #                     'Server={SERVER};'
    #                     'Port = 1433;'
    #                     'Database={DATABASE};'
    #                     'UID={USERNAME};'
    #                     'PWD={PASSWORD}'
    #                     ;TDS_Version=8.0;)
    #conn = odbc.connect('DRIVER=FreeTDS;SERVER={SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};CHARSET=UTF8;TDS_Version=7.4;')
    #conn = pyodbc.connect(connectionString)
    #conn = pyodbc.connect(sql_connection_str) 
    # except Error as e:
    #     print(e)

    #connectionString = f"""
    #     DRIVER={{{DRIVER_NAME}}};
    #     SERVER={SERVER};
    #     PORT=1433;
    #     DATABASE={DATABASE};
    #     UID={USERNAME};
    #     PWD={PASSWORD};
    #     TDS_Version=8.0;
    # """
    # conn = odbc.connect(connectionString)
    return conn

def get_schema_representation(sql_include_relationship):
    """ Get the database schema in a JSON-like format """
    conn = create_connection()
    conn.add_output_converter(-150, handle_sql_variant_as_string)
    cursor = conn.cursor()

    # Query to get all table names
    cursor.execute("SELECT t.name TableName, s.name SchemaName, s.name + '.'+ t.name as TableWithSchma FROM sys.tables t join sys.schemas s on s.schema_id = t.schema_id where t.type = 'u';")
    tables = cursor.fetchall()
    
    db_schema = {}
    db_help = {}
    
    for table in tables:
        table_name = table[0]
        table_with_schema_name = table[2]
        
        # Query to get column details for each table
        cursor.execute(f"select c.name as ColumnName, ty.name as TypeName from sys.columns c join sys.tables t on t.object_id = c.object_id join sys.types ty on ty.user_type_id = c.user_type_id where t.name ='{table_name}'")
        columns = cursor.fetchall()
        column_details = {}

        table_definition = {}

        for column in columns:
            column_name = column[0]
            column_type = column[1]
            column_details[column_name] = column_type
        table_definition["fields"] = column_details
        
        table_help = ""
        
        query = f"select p.value from sys.tables t join sys.extended_properties p on p.major_id=t.object_id AND p.class=1 Where p.name = 'About' and t.name ='{table_name}'"
        ##cursor_help.execute(f"select p.value from sys.tables t join sys.extended_properties p on p.major_id=t.object_id AND p.class=1 Where p.name = 'About' and t.name ='{table_name}'")
        cursor.execute(query)
        about = cursor.fetchall()
        
        for about_item in about:
            table_help = about_item[0]
        table_definition["Notes"] = table_help

        if sql_include_relationship == "YES":
            #cursor.execute(f"SELECT  f.name AS foreign_key_name, Object_Schema_name(object_id) as s_name,OBJECT_NAME(f.parent_object_id) AS table_name, COL_NAME(fc.parent_object_id, fc.parent_column_id) AS constraint_column_name, Object_Schema_name (f.referenced_object_id) AS referenced_s_name, OBJECT_NAME (f.referenced_object_id) AS referenced_table_name    ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column_name FROM sys.foreign_keys AS f INNER JOIN sys.foreign_key_columns AS fc    ON f.object_id = fc.constraint_object_id WHERE f.parent_object_id = OBJECT_ID('{table_with_schema_name}') and is_disabled = 0 ")
            cursor.execute(f"SELECT  f.name AS foreign_key_name, Object_Schema_name(object_id) as s_name,OBJECT_NAME(f.parent_object_id) AS table_name, COL_NAME(fc.parent_object_id, fc.parent_column_id) AS constraint_column_name, Object_Schema_name (f.referenced_object_id) AS referenced_s_name, OBJECT_NAME (f.referenced_object_id) AS referenced_table_name    ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column_name FROM sys.foreign_keys AS f INNER JOIN sys.foreign_key_columns AS fc    ON f.object_id = fc.constraint_object_id WHERE f.parent_object_id = OBJECT_ID('{table_with_schema_name}') and is_disabled = 0  UNION SELECT  f.name AS foreign_key_name, Object_Schema_name (f.referenced_object_id) AS s_name, OBJECT_NAME (f.referenced_object_id) AS    table_name ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS  constraint_column_name, Object_Schema_name(object_id) as referenced_s_name ,OBJECT_NAME(f.parent_object_id) AS referenced_table_name , COL_NAME(fc.parent_object_id, fc.parent_column_id) AS referenced_column_name FROM sys.foreign_keys AS f INNER JOIN sys.foreign_key_columns AS fc  ON f.object_id = fc.constraint_object_id WHERE f.referenced_object_id = OBJECT_ID('{table_with_schema_name}') and is_disabled = 0 ")
            relationships = cursor.fetchall()

            foreignkey = {}
            for r_item in relationships:
                constraint_column = r_item[3]
                ref_details = r_item[6] + " field from " + r_item[4] + "." + r_item[5]
                foreignkey[constraint_column] = ref_details
            table_definition["relationship"] = foreignkey
        
        db_schema[table_with_schema_name] = table_definition

    conn.close()
    return db_schema

# This will create the table and insert 100 rows when you run sql_db.py
if __name__ == "__main__":

    #Create Connection
    #print(create_connection())

    # Querying the database
    # print(query_database("SELECT * FROM df.app"))

    # Getting the schema representation
    sql_connection_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=ubti-p-df-ssvr.database.windows.net;DATABASE=DiligenceFabric;UID=sqladmin;PWD=welcome123#'
    print(get_schema_representation(true))
    
