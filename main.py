from bs4 import BeautifulSoup, SoupStrainer
import requests
import pandas  as pd
import seaborn as sns
import os
import matplotlib.pyplot as plt

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
url_list = []
KIRANICO = "https://mhworld.kiranico.com/"
HZV_FOLDER = "hzv_data"
PLOT_FOLDER = "hzv_visuals"


def get_url_list():
    global url_list
    url_list = []
    req = requests.get(KIRANICO, headers)
    soup = BeautifulSoup(req.content, "lxml")

    grid = (soup.find_all("div", class_="col-lg-6")[1]).find_all("tr")

    monster_list = []

    end = False

    for row in grid:
        for square in row.find_all("td"):
            url = square.find("a")['href']
            if url.endswith("anteka"):
                end = True
                break
            url_list.append(square.find("a")['href'])
        if end:
            break

def get_hzv(url):
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, "lxml")

    name = soup.find("div", class_="align-self-center").text

    csv_path = f"{HZV_FOLDER}/{name}.csv"
    print(csv_path)

    table = (soup.find_all("div", class_="col-lg-12")[0]).find_all("tr")[1:]

    hzv_list = []

    for row in table:
        info = []
        for x in row.find_all("td"):
            if not x.find("img"):
                info.append(x.string.strip())
            else:
                info.append(x.text.strip() + " (Iceborne)")
        hzv_list.append(info)

    df = pd.DataFrame(hzv_list, columns=['Part', 'Sever', 'Blunt', 'Ranged', 'Fire', 'Water', 'Thunder', 'Ice', 'Dragon', 'Stun', 'Stamina'])

    text = df.to_csv(index=False)

    with open(csv_path, "w+") as f:
        f.write(text)

    generate_visuals(csv_path)

def generate_visuals(csv):
    name = os.path.basename(csv)[:-4]
    df = pd.read_csv(csv, delimiter=',', index_col='Part', usecols=lambda col: col not in ["Stun", "Stamina"])
    sns.heatmap(df, cmap='Reds', annot=True, fmt='g', cbar=False).set_title(name)
    plt.gcf().set_size_inches(18, 8)
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.xlabel("Damage Type")
    plt.savefig(f"{PLOT_FOLDER}/{name}.png", dpi=100)
    plt.clf()
    print(f"{name} done.")

def main():
    plt.rcParams['axes.labelweight'] = 'bold'
    get_url_list()

    for url in url_list:
        get_hzv(url)

if __name__ == "__main__":
    main()
