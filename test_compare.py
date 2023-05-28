import unittest
from app import app
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import functions


class ChatbotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_compare_games(self):
        games = []

        games.append(functions.generateGameArray('https://www.ign.com/games/elden-ring'))
        games.append(functions.generateGameArray('https://www.ign.com/games/dark-souls-iii'))

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

            finalgame1 = " ".join(clean_game1)
            finalgame2= " ".join(clean_game2)

            Compare_vectorizer = CountVectorizer().fit_transform([finalgame1, finalgame2])

            Compare_similarity = cosine_similarity(Compare_vectorizer)

            percentage = Compare_similarity[0][1] * 100
            finalpercentage = round(percentage)



        # Assert the expected result
        expected_response =  34
        self.assertEqual(finalpercentage, expected_response)


if __name__ == '__main__':
    unittest.main()

