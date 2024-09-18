import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col
# Write directly to the app
st.title(":cup_with_straw: Custom Smoothie Orders :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!."""
)
name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)
# Get session and fetch data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
# Ingredient selection
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df['FRUIT_NAME'].tolist(), max_selections=5)
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    st.write("Your selected ingredients:", ingredients_string)
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        if not search_on:
            st.error(f"Search term for {fruit_chosen} is missing.")
            continue
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("
https://fruityvice.com/api/fruit/"+
search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    # SQL insert statement
    my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}','{name_on_order}')"
    # Button with a unique key to avoid the DuplicateWidgetID issue
    time_to_insert = st.button('Submit Order', key='submit_order')
    # Insert when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
