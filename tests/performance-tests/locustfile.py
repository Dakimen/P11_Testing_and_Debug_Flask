from locust import HttpUser, task
import server
from test_data import load_test_data

test_data = load_test_data()
server.app.clubs = test_data["clubs"]
server.app.competitions = test_data["competitions"]


class ProjectPerfTest(HttpUser):
    @task
    def index_perf(self):
        self.client.get("/")

    @task
    def login_perf(self):
        self.client.post('/showSummary', {'email': "john@club1.co"})

    @task
    def book_perf(self):
        competition = server.app.competitions[2]['name']
        club = server.app.clubs[0]['name']
        url = f"/book/{competition}/{club}"
        self.client.get(url)

    @task
    def purchasePlaces_perf(self):
        context = {
            "competition": server.app.competitions[2]['name'],
            "club": server.app.clubs[0]['name'],
            "places": "3"
            }
        self.client.post("/purchasePlaces", data=context)

    @task
    def pointsBoard_perf(self):
        self.client.get('/points')

    @task
    def logout_perf(self):
        self.client.get('/logout')
