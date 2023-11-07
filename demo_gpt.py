
#import os
#from dotenv import load_dotenv
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

#load_dotenv()

output_type = "GUI_PLUS_SQL"
sql_include_relationship = "YES"
system_message_text_only = "NO"

# output_type = os.getenv('PROMPT_RESPONSE_TYPE')
# sql_include_relationship = os.getenv('SQL_INCLUDE_RELATIONSHIP')
# #sql_connection_str = os.getenv('SQL_CONNECTION_STRING')
# system_message_text_only = os.getenv('PROMPT_NON_SQL_SYSTEM')

def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

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
    server.login("munishshri@gmail.com", "rqof kbcl atdg dzqm")  
    server.sendmail(msg['From'], to , msg.as_string())
    server.quit()  

# Create or connect to SQLite database
conn = demo_gpt_db.create_connection()

# Schema Representation for finances table
schemas = demo_gpt_db.get_schema_representation(sql_include_relationship)

st.title("UBTI TechGPT Pro - Artificial Intelligence")
st.write("The Power of UBTI's TechGPT Pro for seamless natural language to business solutions")

# Input field for the user to type a message
user_message = st.text_input("Pose your inquiry:")

if user_message:

    custom_schema = [];
    for schema in schemas:
       custom_schema = str(schemas) + " " + str(schemas[schema])
 
    foramated_schema = custom_schema
    formatted_system_message = ""
    # Format the system message with the schema
    print(system_message_text_only)
    if system_message_text_only == "YES":
        formatted_system_message = TEXT_SYSTEM_MESSAGE.format(schema=foramated_schema)
    else:  
        formatted_system_message = SQL_SYSTEM_MESSAGE.format(schema=foramated_schema)
        user_message = "Please respond in json format only. "+user_message
    #print(formatted_system_message)
    # Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)
    st.write(response)
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
            json_response = json.loads(response)
            query = json_response['query']
            #command = json_response['command']
            error = json_response['error']
            if query != "":
                if query != "":
                    # Run the SQL query and display the results
                    sql_results = query_database(query, conn)
                    st.write("GUI Results:")
                    st.dataframe(sql_results, hide_index=True)
                    #checking to send email
                    #if command["email"]["isemail"] == "yes":
                        #send_email(sql_results, command["email"]["body"], command["email"]["subject"], command["email"]["to"])
                else:
                    # Display the generated SQL query
                    st.write("Response:")
                    st.write(response)
            # else:
            #     # Display the generated SQL query
            #     st.write("Response:")
            #     st.write(error)
            
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
