from asyncio import QueueEmpty
from datetime import datetime
import queue
from threading import Thread

import speedtest as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from rocketry import Rocketry
from rocketry.conds import every


def get_new_speeds():
    speed_test = st.Speedtest(secure=True)
    speed_test.get_best_server()

    # Get ping (miliseconds)
    ping = speed_test.results.ping
    # Perform download and upload speed tests (bits per second)
    download = speed_test.download()
    upload = speed_test.upload()

    # Convert download and upload speeds to megabits per second
    download_mbs = round(download / (10**6), 2)
    upload_mbs = round(upload / (10**6), 2)

    return (ping, download_mbs, upload_mbs)


def update_csv(internet_speeds):
    # Get today's date in the form Month/Day/Year
    date_today = datetime.today().strftime("%m/%d/%Y")
    # File with the dataset
    csv_file_name = "internet_speeds_dataset.csv"

    # Load the CSV to update
    try:
        csv_dataset = pd.read_csv(csv_file_name, index_col="Date")
    # If there's an error, assume the file does not exist and create\
    # the dataset from scratch
    except:
        csv_dataset = pd.DataFrame(
            list(), columns=["Ping (ms)", "Download (Mb/s)", "Upload (Mb/s)"]
        )

    # Create a one-row DataFrame for the new test results
    results_df = pd.DataFrame(
        [[internet_speeds[0], internet_speeds[1], internet_speeds[2]]],
        columns=["Ping (ms)", "Download (Mb/s)", "Upload (Mb/s)"],
        index=[date_today],
    )

    updated_df = csv_dataset.append(results_df, sort=False)
    # https://stackoverflow.com/a/34297689/9263761
    updated_df.loc[~updated_df.index.duplicated(keep="last")].to_csv(
        csv_file_name, index_label="Date"
    )


# new_speeds = get_new_speeds()
# print(new_speeds)

app = Rocketry()
pings = queue.Queue()
uploads = queue.Queue()
downloads = queue.Queue()

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

pl = []
ul = []
dl = []

def test_speed():
    while True:
        print("testing speed...")
        ping, down, up = get_new_speeds()
        print("new value: ",ping, down, up)
        pings.put(ping)
        downloads.put(down)
        uploads.put(up)




def show_plot(i):
    try :
        pl.append(pings.get(block=False))
        ul.append(uploads.get(block=False))
        dl.append(downloads.get(block=False))
        pings.task_done()
        downloads.task_done()
        uploads.task_done()
    except Exception as ex:
        pass

    ax1.clear()
    ax1.plot(range(len(pl)), pl, label="ping")
    ax1.plot(range(len(ul)), ul, label="upload")
    ax1.plot(range(len(dl)), dl, label="download")
    ax1.legend()


if __name__ == "__main__":
    t= Thread(target=test_speed, daemon=True)
    t.start()
    ani = FuncAnimation(plt.gcf(), show_plot, interval=5 * 1000)
    plt.show()
