'''
This script checks validity of URLs in a file, where said links require login.
Takes markdown file containing text + links.
Creates a bad_urls.txt file with all invalid URLs.
'''

import re
import requests
import mechanize
import cookielib
import sys

class CheckURLS:

    def __init__(self, file_with_links, base_url, user, password):
        '''Reads file and creates list of URLs.
        Prints number of URLs'''

        self.base_url = base_url
        self.user = user
        self.password = password
        
        #read file
        with open(file_with_links, 'r') as f:
            self.file_with_links = f.read()

        #collect urls with regex
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.file_with_links)

        #GAH, regex fail. Remove extra ')' at end of each URL
        #modify as needed
        self.clean_urls = [url[:url.index(')')] for url in urls]
        
        print("Number of URLS: {0}".format(len(self.clean_urls)))

        
    def make_browser(self):
        '''This function makes browser object, logs into base_url with credentials, 
        then returns browser object for future browsing'''
    
        #browser object
        br = mechanize.Browser()

        #cookie jar
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        #set browser options
        #unclear if all are necessary
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        br.addheaders = [('User-agent', 'Chrome')]

        #the site we will navigate into
        br.open(self.base_url)

        #select the second (index one) form (the first form is a search query box)
        #might need to be modified depending on login page
        br.select_form(nr=1)

        #input user credentials
        br.form['login'] = self.user
        br.form['password'] = self.password

        #login
        br.submit()

        return br

    def check_url(self,url,br):
        '''Checks whether the URL is valid.
        Returns 'good' or 'bad' '''

        try:
            response = br.open(url)
            info = response.info()
            return info
        except:
            return "bad"

        
    def test(self, good_link, bad_link):
        '''Just a simple test function to test check_url'''
        
        br = self.make_browser()
        
        bad = bad_link
        good = good_link

        print("good",self.check_url(good,br))
        print("bad",self.check_url(bad,br))

    
    def main(self):
        '''Main function reads through each URL in file_with_links and writes to bad_urls.txt if invalid.
        Verbose'''
        
        br = self.make_browser()
        with open("bad_urls.txt","a") as f:
            for url in self.clean_urls:
                if self.check_url(url,br) == "bad":
                    print("bad")
                    f.write(url+"\n") #writes a new line after each URL. May want to change depending on use of text file

        print("finished writing")
        

    def write_new_file_with_URLs_marked(self):
        '''FUNCTION OPEN FOR MODIFICATION.
        Currently would read through original file and add bold tags to invalid URLs, just for viewing pleasure.
        Then writes to a new_file.md file.'''
        
        with open("bad_urls.txt","r") as f:
            bad_urls = f.read().splitlines() 

        new_file = self.file_with_links
        for url in bad_urls:
            new_file = new_file.replace(url,"<b>"+url+"</b>")

        with open("new_file.md","w") as f:
            f.write(new_file)
        

        
if __name__ == "__main__":

    file_with_links = sys.argv[1]
    base_url = sys.argv[2]
    user = sys.argv[3]
    password = sys.argv[4]

    c = CheckURLS(file_with_links, base_url, user, password)
    c.main()
