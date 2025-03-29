important first note: this is my local branch from the repository of pengyuanli https://github.com/pengyuanli/PDFigCapX
i did not come up with the code. This repo is to make things run on my local machiene
Credits also to jtrells who added the python3 branch from which this is derived https://github.com/pengyuanli/PDFigCapX/tree/python3
# How to run stuff
### Prerequisits:
The IDE I use is visual studio code
in addition the way I run it requires the VSCode DevContainer extension (and possibly also the Docker extension) -> also Docker desktop needs to be running when opening the script. 

### First important tip:
- This script is meant to be run in a development container. I do not know what this means in detail but the easiest way to get it running is to open the folder in VSCode (make sure you are directly in the folder where the dockerfile is located) and then if you have the DevContainer extension installed it should suggest to you to run the container. 
- Then you are able to run stuff from the VSCode terminal!

### Important note on what commands to use and where to put files:
The file you want being processed needs to sit in the input-pdf directory. I have not tested this but I recommend only putting one file there (IMPORTANT -> see point on filenames).
The command to run things in the dev container terminal (named bash <yourcontainername>)is the following:
 
 /opt/conda/envs/pdfigcapx/bin/python src/pdfigcapx/FigCap.py

File outputs:
The script creates output folders in the xpdf directory and creates a designated output for the processed pdf file. The output directory can be left messy. The script sufficiently checks for duplicates.

### A Problem which will MOST LIKLEY OCCUR -> 
- The Chromedriver is downloaded from a static link -> meaning that one specific version is downloaded.
- The chrome-browser, however, which it needs to run, is downloaded from the google-link which always provides the newer version. 
- ALWAYS CHECK whether the versions match, when you encounter an error hinting at issues with selenium, the chromdriver or google-chrome.
- Currently we are using version 116.0.5845.179 of chrome and version 116.0.5845.96 of the chrome driver.
--> when you have to change the chromdriver -> make sure that the filepaths are still correct. The dockerfile creates the container with both executables moved to the /usr/bin directory. Navigate there via the bash terminal from the built up dev container and look for the corresponding filenames.

ALSO:
This is something related to the script itself. In the pdf_info.py I had do adjust the browser options for the chrome browser otherwise it would refuse to run. See there for reference.


### Last note on filenames:
The script does not do well with fancy filenames. PDF files to be processed should containe no spaces! and I have not tested this bt maybe also no special characters. What works is a pure line of letters such as: ThisIsMyInputPDF.pdf

### One more note on print statements:
I have added a lot of print staments to test where the code breaks. I have not removed them yet. Dont let them confuse you.

## Features
this section is dedicated to where you can adjust things to your liking:
### Image resolution
to change the image resolution of your outputted images you can change the dpi value in the pdf2images function. The pdf2images function is located on line 21 in the utils.py script.
### Textbox detection
some of the crucial code parts are located around line 125 in the xpdf_process.py script. I havent looked into further detail yet. But you can expand the array of terms this function checks for.
In my usecase it is helpful for example to also check for things like "Map" or "source" to get additional infos about the maps I am looking at.

-> the script predominantly checks for the word "fig".

I added soe things for example to look for sources - which seems to work partially. HAve yet to figure out how to do the same for maps.

## Documentation of changes I made to the original script

### Resolve the relative import nightmare:
- for me the easiest way to resolve it was to just erase the dots infront of the import statements in the utils.py and renderer.py scripts!
-   like so: from utils import natural_sort, pdf2images

### resolve the libraries issue:
- the easiest way is to adjust the devcontainer.json -> there you insert the follwing statement:
    "postCreateCommand": "conda env update -n base -f /workspace/environment.yml"
- this should install the conda environment in the container - but idk really
- to make sure you run the scripts in the correct environment you then do not type python FigCap.py in the terminal but:
-   **/opt/conda/envs/pdfigcapx/bin/python** src/pdfigcapx/FigCap.py

/opt/conda/envs/pdfigcapx/bin/python src/pdfigcapx/FigCap.py

## change import and output paths 
-> currently the correct paths are depended on what name you give the container. In this instance because it is from a git repo - the directory name is PDFigCapX-TheXmassheep. So the example here is incorrect. Should look like this: /workspaces/<your containername here>/input-pdf

Also change the input and output paths in the FigCap.py script at line 34:
    if __name__ == "__main__":

        input_path = '/workspaces/PDFigCapX/input-pdf'
        output_path = '/workspaces/PDFigCapX/output-pdf'
        xpdf_path = output_path + '/xpdf/'
        log_file = output_path + '/log.text'
        f_log = open(log_file, 'w')
        if not os.path.isdir(xpdf_path):
            os.mkdir(xpdf_path)




## Current ISSUES
- something is wrong with the filepaths but i am not completely sure what the issue is
debugg further

## CURRENT ISSUES RESOLVED!
-> this does not seem to be an issue anymore the way the container is structured now but take note of this in case there is permission errors. Use the chmod commands in the bin/bash terminal of the container to resolve

Finally resolved the insane problem in the FigCap.py script. The issue was that in the original scripped the pdftohtml linux executable from the xpdfReader command line tools was called from a location from which the script didnt have the permission to execute. The solution is as follows:
When you have feshly built up the container. In the terminal navigate to the executables folder. (I have created this folder before and copied the binary exectuable into there). Then from the terminal run the command 

"chmod +x pdftohtml" 

This command gives the permission to run the exectuble.

## NEXT ISSUE
Script cant find the chromdrive because in the pdf_info.py the chromedriver is looked for in the wroing filepath (line 43)
so i did a similar thing to what i did above. Downloaded the chromedriver - (see the dockerfile for reference -> this also confuses me - why do we download all of this but then it is not available?). And copied the chromedriver into the exectuables dir

then ran 

chmod +x chromedriver

NOTE: interestingly i didnt have to rerun those commands when i rebuilt the container

Then you need to change the filpath in the script.

DID not work -> get an error. The issue is potentially that the driver tries to start chrome? IDK

#### the follwing notes can be ignored - i keep them for personal reference -> they are all mostly wrong
browser = webdriver.Chrome('exectuables/chromedriver')

browser = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())
Before what I did was to give permissions to the chrome browser as well in the dockerfile by adding:
    && chmod +x usr/bin/google-chrome \
to the dockergile

Matching Chrome browser and chromedriver versions:
From Chat GPT
# Add the Google Chrome repository (replace with the correct repository for your version)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Update and install the specific Chrome version
RUN apt-get update && apt-get -y install google-chrome-stable=116.0.5845.179


Modified as follows:
&& apt-get update && apt-get -y install google-chrome-stable=114.0.5735.90 \

(Old)
&& apt-get -y update && apt-get -y --no-install-recommends install google-chrome-stable \

also added this:
    && chmod +x usr/bin/google-chrome-stable \


#### WRONG! -  BIGGER modifications in Dockerfile

Original
    && wget -q -O - --no-check-certificate https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add \
    && echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update && apt-get -y --no-install-recommends install google-chrome-stable \
    && chmod +x usr/bin/google-chrome \
    && chmod +x usr/bin/google-chrome-stable \

Modified:

    && wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip \
    && mv chrome /usr/bin/chrome \
    && chown root:root /usr/bin/chrome \
    && chmod +x /usr/bin/chrome \
    && rm chrome-linux64.zip \
    && chmod +x usr/bin/chrome \
  

  Eventually resolved by matching the chrome versions. 



  ## Open ends for possible improvement
  The script still has issues with finding titles or captions that are located further away from the image.
  - possible solutions:
    - look more deeply into how the captions are identified. And possible increase the area from which these are looked for
    - see the features note on this in this readme -> ntry points for improvement.

## Further work
Where to find stuff:
- finding the parts in the script where it loogs for specific text to identify images
    - xpdf_process.py line 71


## Changelog in Testing
- extending the text its looking for works - moved the looking for maps part in line 71 in xpdf_process.py to the second if statement works
- working with multiple pdfs seems to work - think further about the naming of the reports so that they can be processed automatically
-  [ ] expand image bounding box

- added installing imagemagick to the dockerfile for installing when creating the container:

```docker
# Install dependencies
RUN apt-get -y update && apt-get install -y --no-install-recommends \
    wget ghostscript ffmpeg libsm6 libxext6 gnupg gnupg2 unzip gsfonts-x11 imagemagick\
    && apt-get clean && rm -rf /var/lib/apt/lists/*
```