from flask import Flask, render_template, request, redirect, url_for, session, make_response
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from random import randint
import functions
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords') #important
nltk.download('wordnet') #important




stop_words = set(stopwords.words('english'))

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

state = "start"

@app.route('/', methods=['GET', 'POST'])
def chat():


    try:

        response = ''
        compare_mode = False;
        lemmatizer = WordNetLemmatizer()

        with open('SimilarQuestions.txt', 'r', encoding='utf-8') as question_file:
            question = question_file.read().split('\n')

        with open('gameInfo.txt', 'r', encoding='utf-8') as responses_file:
            responses = responses_file.read().split('\n')

        questions = question[:3]

        # vectorize first questions array
        vectorizer = CountVectorizer()
        vectorizer.fit(questions)
        words = vectorizer.get_feature_names_out()
        vectorizedDocs = vectorizer.transform(questions)

        # vectorize info questions array

        info = question[3:9]
        Info_vectorizer = CountVectorizer()
        Info_vectorizer.fit(info)
        Info_words = Info_vectorizer.get_feature_names_out()
        Info_vectorizedDocs = Info_vectorizer.transform(info)

        # vectorize buy questions array

        buy = question[9:]

        Buy_vectorizer = CountVectorizer()
        Buy_vectorizer.fit(buy)
        Buy_words = Buy_vectorizer.get_feature_names_out()
        Buy_vectorizedDocs = Buy_vectorizer.transform(buy)



        global state
        global gameName
        global gameListUrl

        if state == "start":
            response = "Choose Method"
            message = 'Choose one of the following: get information, buy games or compare games'
            print('enter start')
            if request.method == 'POST':

                    user_Input = request.form['input'].lower()
                    custom_lemmatization = {'info': 'information', 'purchase' : 'buy'}
                    user_input = custom_lemmatization.get(user_Input, lemmatizer.lemmatize(user_Input))
                    print(user_input)
                    user_input_vec = vectorizer.transform([user_input])
                    similarities = cosine_similarity(user_input_vec, vectorizedDocs)
                    most_similar_index = np.argmax(similarities)
                    if np.sum(user_input_vec.toarray()) == 0:
                        response = "Sorry I didn't get that"


                    else:
                        count = 0
                        for i in questions:
                            if i == questions[most_similar_index]:

                                if responses[count] == responses[0]:
                                    response = "choose Game Name"
                                    state = "gameName"
                                    message = '*Please enter the game name only*'
                                    compare_mode = False


                                elif responses[count] == responses[1]:
                                    response = "choose game category"
                                    state = "category"
                                    message = 'choose one of the following: genre, developer, franchise, publisher, platform, feature'
                                    compare_mode = False


                                elif responses[count] == responses[2]:
                                    response = "choose 2 games that you want to compare"
                                    state = "compare"
                                    message = 'if you want to exit, in the status input field type exit'
                                    compare_mode = True



                            else:
                                count += 1
                    return render_template('index.html', response=response, message = message, state=state, compare_mode=compare_mode)
            else:
                return render_template('index.html', response=response,  message = message, state=state, compare_mode=compare_mode)





        elif state == "gameName":

            print('enter gameName state')
            gameName = request.form['input']
            if request.method == 'POST':
                    if gameName.replace(' ','') == '':
                        response = 'Please type a game'
                        message = 'type a game to continue'
                    else:
                        response = 'What do you want to search for ' + gameName + ': '
                        message = 'Choose one of the following: summary, developer, genre, rating, platform and date released'
                        state = "game"
            return render_template('index.html', response=response, message=message ,compare_mode = False)

        elif state == "game":
            message = ''
            print('enter game state')

            gameTitle = gameName.lower().split()
            gameName = "-".join(gameTitle)
            url = 'https://www.ign.com/games/'
            generateUrl = url + gameName.lower()
            print(generateUrl)


            gameInfoArray = ['I want to have information', 'I want to buy a game', 'I want to compare 2 games',
                         'The rating of the game is: ' + functions.getRating(generateUrl)[0],
                         'The summary of the game is: ' + functions.getSummary(generateUrl)[0],
                         'The date released of the game is: ' + functions.getDateReleased(generateUrl)[0],
                         'The developer of the game is: ' + functions.getDeveloper(generateUrl)[0],
                         'The platform of the game is: ' + str(functions.getPlatform(generateUrl)),
                         'The genre of the game is: ' + str(functions.getGenre(generateUrl)),
                         'https://www.ign.com/games/producer/', 'https://www.ign.com/games/platform/',
                         'https://www.ign.com/games/genre/', 'https://www.ign.com/games/publisher/',
                         'https://www.ign.com/games/feature/', 'https://www.ign.com/games/franchise/']


            with open('gameInfo.txt', 'w', encoding='utf-8') as f:
                for item in gameInfoArray:
                    f.write("%s\n" % item)

            gameList = open('gameInfo.txt', encoding='utf-8').read().split('\n')
            response = 'What do you want to search for ' + gameName + ': '
            gameInfo = request.form['input'].lower()
            message = 'Choose one of the following: summary, developer, genre, rating, platform and date released'






            if gameInfo.__contains__('exit') == True:
                response = "Choose Method"
                message = 'Choose one of the following: get information, buy games or compare games'
                state = "start"
                return render_template('index.html', response=response, message=message, compare_mode = False)

            if (info != ''):
                userInput_Vec = Info_vectorizer.transform([gameInfo])
                similarities = cosine_similarity(userInput_Vec, Info_vectorizedDocs)
                mostSimilar_index = np.argmax(similarities)
                userArray1 = userInput_Vec.toarray()
                if np.sum(userArray1) == 0:
                    response = "sorry i didn't get that"

                else:

                    count1 = 0

                    for i in info:
                        if i == info[mostSimilar_index]:
                            response = gameList[count1 + 3]
                            message = "if you want to leave from this option type 'exit' or choose one of the following: summary, developer, genre, rating, platform and date released'"
                            break
                        else:
                            count1 += 1

            return render_template('index.html', response=response, message=message, compare_mode = False)

        elif state == "category":
            print('category state')
            category = request.form['input']

            userInput_Vec = Buy_vectorizer.transform([category])
            similarities = cosine_similarity(userInput_Vec, Buy_vectorizedDocs)
            Buy_MostSimilar_index = np.argmax(similarities)
            userArray = userInput_Vec.toarray()
            if np.sum(userArray) == 0:
                response = "Sorry I didn't get that"
                message = 'specify search again';
            else:
                count2 = 0
                for i in buy:

                    if i == buy[Buy_MostSimilar_index]:
                        Category  = buy[Buy_MostSimilar_index].split()
                        gameListUrl = responses[count2 + 9]
                        print(gameListUrl)
                        response = "Specify search for " + Category[5]
                        message = 'Enter a ' + Category[5]  + ' to continue your search'
                        state = "genList"


                    else:
                        count2 +=1
            return render_template('index.html', response=response, message=message,compare_mode = False)

        elif state == "genList":
            search = request.form['input'].lower()
            message = 'Type exit to leave or specify search'
            if (search.__contains__('exit') == True):
                response = "Choose Method"
                message = 'Choose one of the following: get information, buy games or compare games'
                state = 'start'
                return render_template('index.html', response=response,message=message, compare_mode=False)



            Input = search.split()


            SpecifyInput = "-".join(Input)
            fullUrl = gameListUrl + SpecifyInput
            print(fullUrl)
            Games = functions.getAllGamesUnderGenre(fullUrl)


            if Games != []:
                games = ',\n'.join(Games)
                with open('GameList.txt', 'w', encoding='utf-8') as file:
                    file.write(games)
                gameList = open('GameList.txt', encoding='utf-8').read().split(',\n')
                randomNumArray = []
                for i in range(5):
                    i = randint(0, len(gameList) - 1)
                    randomNumArray.append(i)

                array = []

                for num in randomNumArray:
                    array.append(gameList[num])

                Gameslist = ', '.join(array)

                response = Gameslist

                state = "getGames"
                message = "if you want more of this type; type 'more' else type exit"

            else:
                response = "Game List not found"
                message = 'Type exit to return to start screen or try to search again'
                return render_template('index.html', response=response, message=message, compare_mode=False)

            return render_template('index.html', response=response, message=message, compare_mode = False)

        elif state == "getGames":

            print('get Games state')
            search = request.form['input'].lower()
            response = ""
            message = "if you want more of this type; type 'more' else type exit"
            if search.__contains__('exit') == True:
                response = "Choose Method"
                message = 'Choose one of the following: get information, buy games or compare games'
                state = "start"
                return render_template('index.html', response=response, message=message, compare_mode = False)

            elif search.__contains__('more') == True:
                gameList = open('GameList.txt', encoding='utf-8').read().split(',\n')
                randomNumArray = []
                for i in range(5):
                    i = randint(0, len(gameList) - 1)
                    randomNumArray.append(i)

                array = []

                for num in randomNumArray:
                    array.append(gameList[num])


                Gameslist = ', '.join(array)

                response = Gameslist
                return render_template('index.html', response=response, message=message, compare_mode = False)
            else:
                response = "sorry I didn't get that"

                return render_template('index.html', response=response, message=message, compare_mode = False)

        elif state == 'compare':
            print('Enter compare')
            games = []
            url = 'https://www.ign.com/games/'
            message = 'if you want to exit, in the status input field type exit  '
            game1 = request.form['game1']
            game2 = request.form['game2']
            status = request.form['status'].lower()
            if status.__contains__('exit') == True:
                state = "start"
                response = "Choose Method"
                message = 'Choose one of the following: get information, buy games or compare games'
                return redirect(url_for('chat'))

            Game1 = game1.lower().split()
            selectgame1 = "-".join(Game1)

            Game2 = game2.lower().split()
            selectgame2 = "-".join(Game2)

            games.append(functions.generateGameArray(url + selectgame1))
            games.append(functions.generateGameArray(url + selectgame2))

            game1_str = ' '.join(games[0])
            game2_str = ' '.join(games[1])

            whitespace_tokenization = game1_str.split()
            clean_game1 = whitespace_tokenization[:]
            for token in whitespace_tokenization:
                if token in stopwords.words('english'):
                    clean_game1.remove(token)

            whitespace_tokenization = game2_str.split()
            clean_game2 = whitespace_tokenization[:]

            for token in whitespace_tokenization:
                if token in stopwords.words('english'):
                    clean_game2.remove(token)

            try:
                finalgame1 = " ".join(clean_game1)
                finalgame2 = " ".join(clean_game2)

                Compare_vectorizer = CountVectorizer().fit_transform([finalgame1, finalgame2])

                Compare_similarity = cosine_similarity(Compare_vectorizer)

                percentage = Compare_similarity[0][1] * 100
                response = game1 + " and " + game2 + " are " + str(round(percentage)) + "% similar."
                return render_template('index.html', response=response, message=message, compare_mode=True)
            except:
                response = 'There is no content'
                return render_template('index.html', response=response, message=message, compare_mode=True)
            return render_template('index.html', response=response, compare_mode=True)


    except:
        if state == 'compare':
            response = "choose 2 games that you want to compare"
            state = "compare"
            message = 'if you want to exit, in the status input field type exit'
            return render_template('index.html', response=response, message = message,compare_mode=True)
        else:
            response = "Choose Method"
            message = 'Choose one of the following: get information, buy games or compare games'
            return render_template('index.html', response=response,message=message, compare_mode=False)

if __name__ == '__main__':
    app.run(debug=True)
