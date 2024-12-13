import streamlit as st
from utils import *
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

def main(user_input, config):
    prog_bar = st.progress(0, f'searching... (0/{config["retmax"]})')
    max_results = config['retmax']
    num_processed = 0
    print(config['retmax'])
    print('the user input is:', user_input)

    try:
        result_geenrator = run(user_input, config)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.warning("API rate limit exceeded. Please try again later.")
        return
    try:
        while (res:=next(result_geenrator)):
            num_processed += 1
            doc_id = res['doc_id']
            doc_detail = res['doc_details']
            doc_abstract = res['doc_abstract']

            title = doc_detail['result'][doc_id]['title']
            # box_content is title and list of authors separated by a comma in markdown
            box_content = f"#### {title}\n"
            authors = doc_detail['result'][doc_id]['authors']
            authors = [author['name'] for author in authors]
            box_content += ', '.join(authors)

            with st.expander(box_content):
                # print date, journal, etc.
                pubdate = doc_detail['result'][doc_id]['pubdate']
                volume = doc_detail['result'][doc_id]['volume']
                issue = doc_detail['result'][doc_id]['issue']
                pages = doc_detail['result'][doc_id]['pages']
                journal = doc_detail['result'][doc_id]['source']
                pubtype = doc_detail['result'][doc_id]['pubtype'][0]

                st.write(f"##### Abstract:\n {doc_abstract}")
                st.write(f"##### Publication type: {pubtype}")
                st.write(f"##### Published on: {pubdate}")
                st.write(f"##### Journal: {journal}")
                st.write(f"##### Volume: {volume}")
                st.write(f"##### Issue: {issue}")
                st.write(f"##### Pages: {pages}")

            prog_bar.progress(num_processed/max_results, 'searching... ({}/{})'.format(num_processed, max_results))
            if num_processed == max_results:
                st.success('Search completed!')
                break
    
    except StopIteration:
        prog_bar.progress(1.0)
        st.success('Search completed!')


# Title: Pubmed QA Chatbot
st.title('Welcome to Pubmed QA Chatbot!')
st.subheader('This is a chatbot that helps you to search for articles in Pubmed.')

with st.sidebar:
    st.markdown('### Search parameters')
    keywords = st.text_input('Enter search keywords, e.g. malaria vaccine').split()

    # get time range
    st.markdown('#### Time range')
    # set start date to two years ago
    start_date = st.date_input('Start date', value=datetime.now()-timedelta(days=365*2))
    end_date = st.date_input('End date', value=datetime.now())

    # Optional filters: author, journal, max number of results
    st.markdown('### Optional filters')
    author = st.text_input('Author')
    journal = st.text_input('Journal')
    max_results = st.number_input('Max number of results', min_value=1, max_value=10, value=3)

    config = {
        'keywords': keywords,
        'sdate': start_date,
        'edate': end_date,
        'author': author,
        'journal': journal,
        'retmax': max_results
    }


st.text_input('How can I help you?', key='user_input', placeholder='Enter your question here...(e.g. What is the treatment for malaria?)')

# put a search button
st.session_state.setdefault('question', None)
def btn_callback():
    st.session_state.question = st.session_state.user_input
    st.session_state.user_input = None

search_btn = st.button('Search', on_click=btn_callback)

if st.session_state.question:
    main(st.session_state.question, config)