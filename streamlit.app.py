import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")

# Description
st.write("Choose the fruits you want in your custom Smoothie!.")

# Name input
name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake session and fetching data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Ingredient selection
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df['FRUIT_NAME'], max_selections=5)

# Process selection and fetch nutritional info
if ingredients_list:
    ingredients_string = ' '

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Fetch nutrition data from Fruityvice API
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            st.subheader(f'{fruit_chosen} Nutrition Information')
            st.dataframe(fv_data, use_container_width=True)  # Display nutrition info in a consistent format
        else:
            st.write(f"No nutrition data available for {fruit_chosen}.")

    # SQL insert statement
    my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}','{name_on_order}')"

    # Button with a unique key to avoid the DuplicateWidgetID issue
    time_to_insert = st.button('Submit Order', key='submit_order')

    # Insert when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
