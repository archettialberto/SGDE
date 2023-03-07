import streamlit as st


def get_generators(filters):
    return [{"name": f"Generator {i}", "image_url": "https://via.placeholder.com/50x50"} for i in range(100)]


def main(
        results_per_page=5,
):
    # --- Page title ---

    st.set_page_config(page_title="Secure Generative Data Exchange")

    # --- Sidebar ---

    # Filters
    st.sidebar.header("Filters")
    filters = {}

    st.sidebar.subheader("Model size")
    filters["small"] = st.sidebar.checkbox("Small", value=False)
    filters["medium"] = st.sidebar.checkbox("Medium", value=False)
    filters["large"] = st.sidebar.checkbox("Large", value=False)

    st.sidebar.subheader("Data format")
    filters["image"] = st.sidebar.checkbox("Image data", value=False)
    filters["tabular"] = st.sidebar.checkbox("Tabular data", value=False)

    st.sidebar.subheader("Task")
    filters["regression"] = st.sidebar.checkbox("Regression", value=False)
    filters["classification"] = st.sidebar.checkbox("Classification", value=False)

    # --- Main section ---

    # Search box
    filters["search_text"] = st.text_input("Search data generators", "")

    generators = get_generators(filters)
    num_results = len(generators)
    num_pages = (num_results - 1) // results_per_page + 1
    page = int(st.experimental_get_query_params().get("page", 1))
    start_idx = (page - 1) * results_per_page
    end_idx = min(start_idx + results_per_page, num_results)

    # Display search results
    st.write(f"{start_idx + 1} - {end_idx} of {num_results} available results.")
    for generator in generators[start_idx:end_idx]:
        col1, col2 = st.columns([1, 6])
        with col1:
            st.image(generator['image_url'], width=50)
        with col2:
            st.write(generator['name'])

    with st.container():
        page_links = []
        for p in range(1, num_pages+1):
            params = st.experimental_get_query_params()
            params['page'] = p
            page_url = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            link = f"[{p}]({page_url})"
            if p == page:
                link = f"**{link}**"
            page_links.append(link)
        st.write(" ".join(page_links))


if __name__ == "__main__":
    main()
