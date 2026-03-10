import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

st.title("Monday Business Intelligence Agent")

API_TOKEN = st.text_input("Enter Monday API Token")
DEALS_BOARD = st.text_input("Deals Board ID")
WORK_BOARD = st.text_input("Work Orders Board ID")

question = st.text_input("Ask a business question")

def get_board_data(board_id):

    url = "https://api.monday.com/v2"

    query = f"""
    query {{
      boards(ids:{board_id}) {{
        items {{
          name
          column_values {{
            title
            text
          }}
        }}
      }}
    }}
    """

    headers = {"Authorization": API_TOKEN}

    response = requests.post(url, json={"query": query}, headers=headers)

    data = response.json()

    items = data["data"]["boards"][0]["items"]

    rows = []

    for item in items:
        row = {"name": item["name"]}

        for col in item["column_values"]:
            row[col["title"]] = col["text"]

        rows.append(row)

    return pd.DataFrame(rows)


if st.button("Analyze"):

    deals = get_board_data(DEALS_BOARD)
    work = get_board_data(WORK_BOARD)

    data_text = f"""
Deals Data:
{deals.head(20)}

Work Orders Data:
{work.head(20)}
"""

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    prompt = f"""
You are a business intelligence assistant.

Analyze this data and answer the founder question.

DATA:
{data_text}

QUESTION:
{question}

Mention data quality issues if any.
Provide insights.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    st.write(response.choices[0].message.content)
