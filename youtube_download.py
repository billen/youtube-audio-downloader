from pytube import YouTube
from tqdm import tqdm
import csv

def main():
    sheetProcessor = SheetProcessor("links.csv")
    sheetProcessor.process()

class YouTubeLink:
    url = ""
    progressBar = None 
    lastBytesRemaining = None 

    def __init__(self, url):
        self.url = url 


    def show_progress_bar(self, stream, chunk, file_handle, bytes_remaining):
        self.progressBar.update(self.lastBytesRemaining - bytes_remaining)
        self.lastBytesRemaining = bytes_remaining

    def downloadAudio(self):
        yt = YouTube(self.url)
        yt.register_on_progress_callback(self.show_progress_bar)
        streamToDownload = yt.streams.filter(only_audio=True).filter(subtype='mp4').first()
        
        self.lastBytesRemaining = streamToDownload.filesize
        self.progressBar = tqdm(total=self.lastBytesRemaining) 
        
        streamToDownload.download()

class SheetProcessor:
    csvFilename = None
    processWithoutConfirmation = None 
    downloadConfirmations = list() 


    def __init__ (self, csvFilename, processWithoutConfirmation = True):
        self.csvFilename = csvFilename
        self.processWithoutConfirmation = processWithoutConfirmation

    def processRow(self, row):
        url = row[0]
        link = YouTubeLink(url)
        link.downloadAudio()
    
    def writeBackToFile (self, reader):
        with open(self.csvFilename.replace(".csv", "") + '-output.csv', "w") as toWriteFile:
            columns = ['Url', 'Downloaded']
            writer = csv.DictWriter(toWriteFile, fieldnames=columns) 
            writer.writeheader()
            lineCount = 0 
            for row in reader:
                if lineCount != 0 and (lineCount - 1) < len(self.downloadConfirmations):
                    writer.writerow({'Url':row[0], 'Downloaded':self.downloadConfirmations[lineCount - 1]})
                lineCount = lineCount + 1
            toWriteFile.close()
    
    def process(self):
        with open(self.csvFilename, newline='') as csvFile:
            reader = csv.reader(csvFile, delimiter=',', quotechar='"')
            lineCount = 0
            for row in reader:
                if lineCount == 0:
                    #If Column Names are not 'Url' and 'Downloaded' fail program for the moment
                    if row[0] != "Url" and row[1] != "Downloaded":
                        exit
                else:
                    try: 
                        self.processRow(row)
                        self.downloadConfirmations.insert(lineCount - 1, "True")
                    except Exception as e:
                        print("Url had error")
                        self.downloadConfirmations.insert(lineCount - 1 , "False")
                lineCount = lineCount + 1

            # Needs to be cleaned up, seek back a better way, and not re-initialize reader. 
            csvFile.seek(0)
            reader = csv.reader(csvFile, delimiter=',', quotechar='"')
            self.writeBackToFile(reader)
        csvFile.close()




main()

# Run over lines of csv file
# Process each line
# After successful process of a line, add a confirmation that that youtube link has been downloaded
    # Read in the line
    # Take the youtube link and download the video
    # Run ffmpeg to extract out audio from the video
# Then move on to the next process