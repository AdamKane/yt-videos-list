from bs4 import BeautifulSoup
import requests
import csv

baseUrl = 'https://www.youtube.com'
user = 'user'
userName = 'MattSDance'
videos = 'videos'

channelVideosUrl = f'{baseUrl}/{user}/{userName}/{videos}'
soup = BeautifulSoup(requests.get(channelVideosUrl).content, 'lxml')

def writeToTxt():
    with open ('{}VideosList.txt'.format(userName.strip('/')), 'w+') as f:
        print('Opened       {}, writing to file...'.format(f.name))
        for url in soup.find_all('a', attrs = {'class': 'yt-uix-sessionlink', 'dir':'ltr'}):
        	# f.write('{}\n'.format(url))
            f.write('title:\n{}\n'.format(url.string))
            f.write('url.href:\n{}{}\n'.format(baseUrl, url.get('href')))
            f.write('*'*50 + '\n')
        print('Wrote to     {}, closing file...'.format(f.name))

def writeToCsv():
    with open ('{}VideosList.csv'.format(userName.strip('/')), 'w+') as csvfile:
        print('Opened       {}, writing to file...'.format(csvfile.name))
        fieldnames = ['Video Title', 'URL', 'Watched?']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer = csv.writer(f)
        writer.writeheader()

        for url in soup.find_all('a', attrs = {'class': 'yt-uix-sessionlink', 'dir':'ltr'}):
            writer.writerow({'Video Title': f'{url.string}', 'URL': f'{baseUrl}{url.get("href")}', 'Watched?': ''})

        print('Wrote to     {}, closing file...'.format(csvfile.name))

def main():
    writeToTxt()
    writeToCsv()

if __name__ == '__main__':
    main()
