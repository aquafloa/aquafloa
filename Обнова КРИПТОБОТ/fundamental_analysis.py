import requests

class FundamentalAnalysis:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_news_sentiment(self):
        url = f"https://api.currentsapi.services/v1/search?keywords={self.symbol}&language=en&apiKey=-YantLa5qmFYMrQUXiFZErOVhX58O8iotlBS30C9Q19L5x06"
        response = requests.get(url).json()
        articles = response['news']
        total_score = 0
        for article in articles:
            title = article['title']
            description = article['description']
            content = article['content']
            text = f"{title}. {description}. {content}"
            score = self.get_sentiment_score(text)
            total_score += score
        average_score = total_score / len(articles)
        return average_score

    def get_sentiment_score(self, text):
        url = "https://api.deepai.org/api/sentiment-analysis"
        headers = {'api-key': 'ed235e63-ef86-46e4-8ad4-11262e9d3065'}
        data = {'text': text}
        response = requests.post(url, headers=headers, data=data).json()
        score = response['output'][0]['score']
        return score
