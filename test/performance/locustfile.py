import gevent
from locust import HttpUser, between, task
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer

setup_logging("INFO", None)


class User(HttpUser):
    wait_time = between(1, 3)
    host = "https://docs.locust.io"

    @task
    def my_task(self):
        self.client.get("/")


# setup test data
print("Calling test data generator (with cache lookup)")
print("Upload test data to S3")

# setup Environment and Runner
env = Environment(user_classes=[User])
env.create_local_runner()

# start a greenlet that periodically outputs the current stats
gevent.spawn(stats_printer(env.stats))

# start a greenlet that save current stats to history
gevent.spawn(stats_history, env.runner)

# start the test
env.runner.start(1, spawn_rate=10)

# in 3 seconds stop the runner
gevent.spawn_later(3, lambda: env.runner.quit())

# wait for the test execution to finish
env.runner.greenlet.join()

# print final stats
print(
    """
################################################################################
"""
)
stats_printer(env.stats)
