import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import csv
import altair as alt

while True:
    # Opens titles file
    if 1:
        with open('OS_all_M_T_title.p', 'rb') as f:
            data = pickle.load(f)
        M_OS = data[0]
        T_OS = data[1]
        OS_titles = data[2]
        corpus_category = data[3]
        assert len(corpus_category)==len(OS_titles)
        # print(T_OS)


    M = M_OS
    category_label = corpus_category


    # Returns the name of the section given its index
    def title_name(index):
        if category_label[index] == 0:
            title = ("PHYS - %s" % OS_titles[index])
        elif category_label[index] == 1:
            title = ("CHEM - %s" % OS_titles[index])
        elif category_label[index] == 2:
            title = ("BIO - %s" % OS_titles[index])
        else:
            return
        return title


    # Opens list of urls
    sheet = pd.read_excel('urllist.xlsx')

    # Opens dataset
    reader = csv.reader(open("data_section_tfidf.csv", "rt"), delimiter=",")
    x = list(reader)
    data = np.array(x).astype("float")

    # Opens pdsit file of the dataset
    reader = csv.reader(open("pdist.csv", "rt"), delimiter=",")
    x = list(reader)
    pdist = np.array(x).astype("float")

    # Starts streamlit
    st.title('Optimal Study Path')
    st.write('Please select the section you would like to start from:')

    list_sections = []
    for i in range(len(OS_titles)):
        list_sections.append(title_name(i))

    # Displays sections
    df = pd.DataFrame({'Sections': list_sections})

    # Displays sections selection
    option = st.selectbox(
        'What section do you choose?',
         df['Sections'], key='<abc>')

    path_length = st.text_input("Path length: ", 1)
    path_length = int(path_length)

    # --------------------------------------------------------------------------------
    def find_good_path(starting_point, prob=1.0):
        # input: M is number of points (row) x dimensions (column)
        # output: good_path = list of length N
        # prob = Probability for accepting and rejecting the next point.
        #        (trying to avoid local min, c.f., simulated annealing).
        # prob = 1.0 (always accept the next closest point)

        good_path = list()
        good_path.append(starting_point)
        N, _ = pdist.shape
        for i in range(path_length):
            curr_pt = good_path[i]
            dist_from_curr_pt = pdist[curr_pt, :]
            # index of points in ascending order of distances.
            for j in np.argsort(dist_from_curr_pt):
                # Check if point j has been visited or not.
                if j in good_path:
                    continue
                else:
                    # Probabilitistically accept or reject the suggested
                    # next point.
                    if np.random.rand(1)[0] > prob:
                        continue
                    else:
                        break
            good_path.append(j)
        return good_path


    def high_tf_terms(M, path):

      l = []
      terms = []
      values = []
      holder = []

      for i in range(path_length):
        l.append(M[path[i]])

      for j in range(len(l[0])):
        for k in range(path_length):
          holder.append(l[k][j])
        values.append(sum(holder))
        holder = []

      for i in range(5):
        terms.append(values.index(max(values)))
        values[terms[i]] = 0

      return terms


    def find_sig_features (M, path, pathlen=0):
        # Find features (column indices) with significance within path.
        # The significance could be high values or high variance,
        assert len(path)>0 # path should not be empty.
        assert len(path)>=pathlen
        if pathlen==0:
            pathlen = len(path)

        M_sliced = M[path[:pathlen],:]

        topN = 5
        sig_features = list()

        # Which features have the largest mean value?
        M_summary = np.mean(M_sliced,axis=0)
        idx = np.argsort(M_summary)[::-1][:topN]
        for i in idx:
            sig_features.append(i)

        # Which features have the largest variance value?
        #M_summary = np.var(M_sliced,axis=0)
        #idx = np.argsort(M_summary)[::-1][:topN]
        #sig_features.append(idx)

        # We could have multiple strategies for finding the significant
        # features, and then find which index appears most often.
        return sig_features
    # --------------------------------------------------------------------------------

    # Runs routine above to find best sequence path
    good_path = find_good_path(list_sections.index(option))
    terms = high_tf_terms(data, good_path)

    st.title("Here's the best order to study about this section's topic:")
    # Returns a list of sections
    for i in good_path[:path_length]:
        st.write(title_name(i))
        st.write(sheet.iat[i, 0])
        st.write("Related terms: ", T_OS[terms[0]], ", ", T_OS[terms[1]], ", ", T_OS[terms[2]])
        st.write(" ")
        holder = find_good_path(i)
        terms = high_tf_terms(data, holder)


    sig_features = find_sig_features(M,good_path, path_length)
    sig_terms = []
    for i in sig_features:
        sig_terms.append(T_OS[i])
    #plot_path_sig_terms(M_OS, T_OS, OS_titles, good_path, 10, 10)

    results = {}
    for sec in good_path[:path_length]:
       results[OS_titles[sec]] = M_OS[sec,sig_features]


    data = pd.DataFrame.from_dict(results, orient='index', columns=sig_terms)

    data.plot()

    df = pd.DataFrame(
        np.random.randn(200, 3),
        columns=['a', 'b', 'c'])
    
    #c = alt.Chart(data).mark_circle(color='blue', opacity=0.5).encode(x='a',y='b', size='c', color='c', tooltip=['a','b','c'])
    #st.write(c)
    
    #c = alt.Chart(df).mark_circle().encode(
    #    x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
    #st.altair_chart(c, use_container_width=True)

    #c = alt.Chart(data).mark_circle(color='blue', opacity=0.5).encode(x='results:Q',y='results:Q').interactive()
    #st.write(c)

    #c = alt.Chart(df.to_json()).mark_circle().encode(
    #   x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
    #st.write(c)
    

    # Plots the result
    plt.plot(good_path,'.')
    plt.xlabel('Sequence Order')
    plt.ylabel('Section')
    plt.show()
    st.pyplot()

