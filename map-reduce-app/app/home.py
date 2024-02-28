import timeit
from time import sleep

import streamlit as st

st.set_page_config(layout="wide")
st.title('Playground for Large Document Processing using GPTs - LDP-GPT')
st.text('Provide large texts that need to be analyzed with custom prompts and with custom map-reduce patterns')
new_job, old_jobs = st.tabs(['Submit New Job', 'Review Job Results'])


def process_job(text, prompt, m, cz, mr):
    sleep(2)
    st.text('Scheduling job with ID  12345')


def get_details(job_id=0):
    return 'Hello world Job'


with new_job:
    c1, c2 = st.columns([1, 3])
    c1.subheader('Settings')
    model = c1.radio('Foundational Language Model', ["OpenAI-GPT4", 'Vertex-AI-Bison'])
    chunk_size = c1.slider('Chunk Size', 100, 5000)
    mr_algo = c1.radio('Map-reduce Algorithm', ['Parallel', 'Sequential', 'Hybrid'])

    c2.subheader('Text Analysis')
    with c2:
        with st.form('form', clear_on_submit=True):

            uploaded_files = st.file_uploader("Upload Files (CSV, PDF, Text)", accept_multiple_files=True)
            # for uploaded_file in uploaded_files:
            # bytes_data = uploaded_file.read()
            # pass

            overall_prompt = st.text_input('Enter your prompt here...')

            # Every form must have a submit button.
            submit = st.form_submit_button("Schedule Process")
            if submit:
                if len(uploaded_files) == 0 or len(overall_prompt) == 0:
                    st.error('Form not filled accurately. Please address them')
                else:
                    with st.spinner('Creating job...'):
                        process_job(uploaded_files, overall_prompt, model, chunk_size, mr_algo)
                        st.info('Job is scheduled')

jobs = [1, 2, 3]
# c3.header('Jobs')
# with c3.container():
#     k, l = c3.columns(2)
#     for j in jobs:
#         details = get_details(job_id=j)
#         k.write('Job %s :blue[cool]' % j)
