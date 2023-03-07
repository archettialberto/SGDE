import streamlit as st

# Define the number of items and items per page
num_items = 50
items_per_page = 5

# Get the current page number from the URL query string
params = st.experimental_get_query_params()
page = int(params["page"][0]) if "page" in params else 1

# Calculate the total number of pages
num_pages = (num_items + items_per_page - 1) // items_per_page

# Determine the range of pages to display
start_page = max(1, page - 5)
end_page = min(num_pages, page + 5)

# Display the pagination UI
st.write(f"Page {page} of {num_pages}:")
prev_button, next_button = st.beta_columns([1, 1])
if page > 1:
    prev_button.button("< Previous", key="prev_page")
if start_page > 1:
    st.write("...")
for p in range(start_page, end_page + 1):
    if p == page:
        st.write(f"[{p}]")
    else:
        st.write(p)
if end_page < num_pages:
    st.write("...")
if page < num_pages:
    next_button.button("Next >", key="next_page")

# Update the page number when the user clicks on Previous or Next
if "prev_page" in st.session_state:
    st.session_state.page = max(1, page - 1)
if "next_page" in st.session_state:
    st.session_state.page = min(num_pages, page + 1)

# Store the current page number in a hidden text input
st.text_input("Current Page", key="page_input", value=page)
