
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import demo_gpt_db
from prompts.prompts import SQL_SYSTEM_MESSAGE
from prompts.prompts import TEXT_SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from smtplib import SMTP
import json
import smtplib 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import time
import re  

load_dotenv()

# output_type = "TEXT_ONLY"
# sql_include_relationship = "YES"
# system_message_text_only = "YES"

output_type = os.getenv('PROMPT_RESPONSE_TYPE')
sql_include_relationship = os.getenv('SQL_INCLUDE_RELATIONSHIP')
sql_connection_str = os.getenv('SQL_CONNECTION_STRING')
system_message_text_only = os.getenv('PROMPT_NON_SQL_SYSTEM')

def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

# Define the function that would do the replacement  
def replacer(match):  
    return '[{}].[{}]'.format(match.group(1), match.group(2))  

# Validate the json
def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

def _draw_as_table(df, pagesize, title):
    alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
    alternating_colors = alternating_colors[:len(df)]
    fig, ax = plt.subplots(figsize=pagesize)
    #ax.axis('tight')
    ax.set_title(title)
    ax.axis('off')
    the_table = ax.table(cellText=df.values,
                        rowLabels=df.index,
                        colLabels=df.columns,
                        rowColours=['lightblue']*len(df),
                        colColours=['lightblue']*len(df.columns),
                        cellColours=alternating_colors,
                        loc='center')
    return fig
  

def dataframe_to_pdf(df, filename, title, numpages=(1, 1), pagesize=(11, 8.5)):
  with PdfPages(filename) as pdf:
    nh, nv = numpages
    rows_per_page = len(df) // nh
    cols_per_page = len(df.columns) // nv
    for i in range(0, nh):
        for j in range(0, nv):
            page = df.iloc[(i*rows_per_page):min((i+1)*rows_per_page, len(df)),
                           (j*cols_per_page):min((j+1)*cols_per_page, len(df.columns))]
            fig = _draw_as_table(page, pagesize, title)
            if nh > 1 or nv > 1:
                # Add a part/page number at bottom-center of page
                fig.text(0.5, 0.5/pagesize[0],
                         "Part-{}x{}: Page-{}".format(i+1, j+1, i*nv + j + 1),
                         ha='center', fontsize=8)
            pdf.savefig(fig, bbox_inches='tight')
            
            plt.close()

def send_email(sql_results, body, subject, to):
    # recipients = ['{to}'] 
    # emaillist = [elem.strip().split(',') for elem in recipients]
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = 'dfgpt@domain.com'
    df_result = pd.DataFrame(sql_results)
    htmlbody = """\
    <html>
    <head></head>
    <body>
        {0}\n\n
        \n{1}
    </body>
    </html>
    """.format(body, df_result.to_html())
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fileNameWithPath = "C:\\Official\\UBTI\\GIT\\Azure-OpenAI-SQL-master\\prompts\\Attachments\\report_"+timestr+".pdf"
    dataframe_to_pdf(df_result, fileNameWithPath, subject)
    print( fileNameWithPath.split("\\")[-1])
    msgbody = MIMEText(htmlbody, 'html')
    msg.attach(msgbody)
    # try:
    #     with open(fileNameWithPath, "rb") as attachment:
    #         p = MIMEApplication(attachment.read(),_subtype="pdf")	
    #         p.add_header('Content-Disposition', "attachment; filename= %s" % fileNameWithPath.split("\\")[-1]) 
    #         msg.attach(p)
    # except Exception as e:
    #     print(str(e))
    filename = fileNameWithPath.split("\\")[-1]
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(fileNameWithPath, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("username", "")  
    server.sendmail(msg['From'], to , msg.as_string())
    server.quit()  

# Create or connect to SQLite database
conn = demo_gpt_db.create_connection()

# Schema Representation for finances table
schemas = demo_gpt_db.get_schema_representation(sql_include_relationship)

st.title("UBTI TechGPT Pro - Artificial Intelligence")
st.write("The Power of UBTI's TechGPT Pro for seamless natural language to business solutions")

# Input field for the user to type a message
raw_user_message = st.text_input("Pose your inquiry:")
customize_user_message = ""

if raw_user_message:

    custom_schema = [];
    for schema in schemas:
       custom_schema = str(schemas) + " " + str(schemas[schema])
 
    foramated_schema = custom_schema
    formatted_system_message = ""
    # Format the system message with the schema
    print(system_message_text_only)
    if system_message_text_only == "YES":
        formatted_system_message = TEXT_SYSTEM_MESSAGE.format(schema=foramated_schema)
        customize_user_message = raw_user_message
    else:  
        formatted_system_message = SQL_SYSTEM_MESSAGE.format(schema=foramated_schema)
        customize_user_message = "Please respond in json format only. "+raw_user_message
    #print(formatted_system_message)
    # Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, customize_user_message)
    print("------------Start Response--------------------------")
    print(response)
    print("------------End Response----------------------------")
    st.write("Your inquiry:")
    st.write(raw_user_message)
    # try:
         # Display the generated SQL query
        #st.write("Generated SQL Query:")
        #st.code(query, language="sql")
        # Run the SQL query and display the results
        #sql_results = query_database(query, conn)
        #st.write("Query Results:")
        #st.dataframe(sql_results)
    match output_type:
        case  "SQL_ONLY":
            json_response = json.loads(response)
            query = json_response['query']
            # Display the generated SQL query
            st.write("Generated SQL Query:")
            st.code(query, language="sql")
        case  "TEXT_ONLY":
            # Display the generated SQL query
            st.write("Response:")
            st.write(response)
        case  "GUI_ONLY":
            json_response = json.loads(response)
            query = json_response['query']
            # Run the SQL query and display the results
            sql_results = query_database(query, conn)
            st.write("Results:")
            st.dataframe(sql_results)
        case "GUI_PLUS_SQL":
            #Parse the json data
            if validateJSON(response) == True :
                json_response = json.loads(response)
                oaierror = json_response['oaierror']
                if oaierror:
                    query = ""
                    st.write(oaierror)
                else:
                    query = json_response['query']
            else:
                query = ""
            # command = json_response['oaicommand']
            # error = json_response['oaierror']
            
            # Use the sub() function to find and replace all occurrences  
            query = re.sub(r'\[([^]]*?)\.\s*([^[]*?)\]', replacer, query)  
            if query:
                if query != "" and query != "N/A" :
                    # Run the SQL query and display the results
                    sql_results = query_database(query, conn)
                    column_names = sql_results.columns.tolist()  
                    column_data_types = sql_results.dtypes  
                    #print(column_data_types)
                    st.write("GUI Results:")
                    #st.dataframe(sql_results, hide_index=True)
                    # Charting
                    #st.bar_chart(sql_results)
                    if len(column_names) >= 2 :
                        dColLst = sql_results.select_dtypes(include=[np.datetime64]).columns.tolist()  
                        nColLst = sql_results.select_dtypes(include=[np.float64]).columns.tolist() 
                        oColLst = sql_results.select_dtypes(include=['object']).columns.tolist()  
                        if len(oColLst) == 0 and len(dColLst) > 0 and len(nColLst) > 0:
                            col1, col2 = st.columns([3, 2])
                            col1.subheader("Table")
                            col1.dataframe(sql_results, hide_index=True)
                            col2.subheader("Chart")
                            col2.line_chart (sql_results, x=dColLst[0], y=nColLst[0])
                        elif len(column_names) > 2 and len(dColLst) > 0 and len(nColLst) > 0 and len(oColLst) > 0:
                            col1, col2 = st.columns([3, 2])
                            col1.subheader("Table")
                            col1.dataframe(sql_results, hide_index=True)
                            col2.subheader("Chart")
                            col2.line_chart (sql_results, x=dColLst[0], y=nColLst[0], color =oColLst[0])
                        else:
                             st.dataframe(sql_results, hide_index=True)
                    else:
                        st.dataframe(sql_results, hide_index=True)
                    #checking to send email
                    #if command["email"]["isemail"] == "yes":
                        #send_email(sql_results, command["email"]["body"], command["email"]["subject"], command["email"]["to"])
                else:
                    # Display the generated SQL query
                    st.write("Response:")
                    st.write(response)
            else:
                # Display the generated SQL query
                st.write("Response:")
                st.write(response)
            
        case "GUI_CHART_PLUS_SQL":
            json_response = json.loads(response)
            query = json_response['query']
            # Display the generated SQL query
            st.write("Generated SQL Query:")
            st.code(query, language="sql")
            # Run the SQL query and display the results
            sql_results = query_database(query, conn)
            st.write("GUI Results:")
            st.dataframe(sql_results, hide_index=True)
            # Charting
            st.bar_chart(sql_results)


    # except Exception as e:
    #     st.write(f"An error occurred: {e}")
