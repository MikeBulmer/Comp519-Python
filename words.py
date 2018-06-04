#!/usr/bin/python3

# Created by Michael Bulmer November 2017 for
# Comp 519 assignment 3.  Liverpool Uni MSC Comp Sci

import re
import urllib.request
import cgi
import cgitb
import os
import sys
import codecs
import html

def word_count():
    #Ullrich's utf-8 incantation
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    cgitb.enable()

    def submit_logic():
        submission = cgi.FieldStorage()
        text = submission.getvalue('doctext')
        url = submission.getvalue('url')
        # clean up input is it an injection is done at the point where the
        # string is displayed.  Before then input is processed as a string so
        # any injected code wouldn't be excecuted.

        # As the standard request is 'get' this is used to land the used on the
        # supply the opening page.

        # Loading page for first time
        if os.environ['REQUEST_METHOD'] == 'GET':
            opening_page()
            return
        # Submit pressed with no inputs filled
        elif not (text or url):
            opening_page("noinput")
            return
        # Both inputs filled
        elif text != None and url != None:
            opening_page("bothfilled")
        # Process text input
        elif text != None:
            output_results(create_dict(search_text(text)), text)
        # Prcess URL input
        elif url != None:
            URL_text = url_get_text(url)
            output_results(create_dict(search_text(URL_text)),URL_text, url)

    # Opening page function outputs opening page HTML.  An additional method
    # is displayed dependant on parameters passed.
    def opening_page(state=""):
        if (state == "noinput"):
            print('<p><b>You must fill in either URL or Document Text</b></p>')
        elif state == "bothfilled":
            print('<p><b>Please only fill one field. Either\
             URL or Document Text</b></p>')
        elif state == "InvalidURL":
            print('<p><b>I could not process anything from that address.  Please try again.</b></p>')
            print('<br /><p><i>The full URL is required.  Try copying from your address bar</i></p>')
        else:
            print('<p>Please enter either a URL or Document Text in the appropriate box.</p>')
        print('''
        <form action="http://cgi.csc.liv.ac.uk/cgi-bin/cgiwrap/m7mb/words.py" method="post">
        <label for="url"> URL:</label>
        <input name="url" type="text" placeholder= "enter URL here" size="95" >
        <br /> <br /><label for="doctext"> Document Text </label> <br />
        <textarea name="doctext" rows="20" cols="100" \
        placeholder="Enter document text here "></textarea> <hr />
        <input type="submit" class="button" value="submit">
        <input type="reset" class="button" value="reset"><hr /></form>
        ''')


    def url_get_text(url):
        text = ""
        try:
            with urllib.request.urlopen(url) as f:
                text += f.read().decode('utf-8')
        except Exception as e:
            opening_page("InvalidURL")
        return text

    def search_text(textin):
        text =textin

        ''' This pattern is to search for html tags which are then replaced with
        white space before the string is processed to look for words.  The pattern
        uses the fact that a < will always be followed by a letter or a /  if this
        pattern is encoutered then then a HTML tag match is assummed.
        the following would be ignored
        a < c
        b <= d
        a > c
        c >= f
        The problem case currently is
        a<c
        every thing from <c until a > is encoutered will be removed.
        However usually a space char is used after the < to make reading clearer.

        Matching the tags with there closing tag before removing hasnt been applied
        as lone tags would still need to be removed so it would be a duplication of
        effort.

        '''
        tagexpression = "<[a-zA-Z!//][^>]*>"
        tags = re.findall(tagexpression, text);

        for tagmatch in tags:
            remove = str(tagmatch)
            text = text.replace(remove," ")

        '''

        PATTERN NOTES
        RE is set to ignore case to simiplfy the pattern

        This is the starting word delimiter.  Its a non capturing group that looks
        for either a non word char as defined by the Assignment or for -- or ---
        ((?<!\w|'|\-)|(?<=--)|(?<=---))

        Starting word pattern, start with a letter or
         an apostrophe followed by a letter
        ([a-z]|'[a-z])\

        body of word pattern, word chars as defined, only allows one hyphen so it
        is not confused with em dashes.

        ([\w|'|])*[\-]?([\w|'|])*\

        end word delimiter, same as opening but looks after the word.
        ((?!\w|'|\-)|(?=--)|(?=---))"

        The final branch has the same delimiters but looks for a word with a single
        letter,  IE a or I

        Note: grave vs accute accent.  In pattern accute accent used so that
        quote with a single `grave accent` are still recongised as Words
        ie evenin' not allowed evenin` is allowed.
        '''

        word_pattern= "(((?<!\w|'|\-)|(?<=--)|(?<=---))\
        ([a-z]|'[a-z])\
        ([\w|'|])*[\-]?([\w|'|])*\
        (s'|[a-z0-9])\
        ((?!\w|'|\-)|(?=--)|(?=---)))|\
         ((?<!\w|'|\-)|(?<=--)|(?<=---))[a-z]((?!\w|'|\-)|(?=--)|(?=---))"

        matches = re.finditer(word_pattern, text, re.X |re.I)
        return matches

    # Takes a list of matches and adds them to a dictionary where the
    # key is the word and the value is a count of the number of times
    # the word appears.
    def create_dict(matches):
        word_dict = {}
        for match in matches:
            word = match.group()
            word = word.lower()
            if word in word_dict:
                word_dict[word]+= 1
            else:
                word_dict.update({word: 1})
        return word_dict

    #Displays the results of the word matching
    def output_results(word_dict, text=None, URL=None):
        # No words found
        print("<p>")
        if len(word_dict) == 0:
            print("I found no words")
        # Only 1 word found
        elif len(word_dict) == 1:
            print("I found only one word. <br /><br />")
            print(" The word I found is:<br />")
            # I'm not happy with the way I have coded this seesion
            # It seems wastful to start a loop when there is only one
            # pair in the dictionary.  However the dictionary.keys() function
            # isn't returning a list on the university system.
            for k in word_dict:
                print(k,"<br />It appeared" ,word_dict[k])
                if word_dict[k] == 1:
                    print("  time.")
                else:
                    print(" times.")
            print("</p>")
        # > than one word found
        else:
            print("I found",str(len(word_dict)),"words")
            print("<hr />")

            # least popular words table output
            print("<table>")
            if len(word_dict) == 1:
                print("<caption>The least popular word is:</caption>")
            elif len(word_dict) <= 10:
                print("<caption>The",len(word_dict) ,"least popular words are:</caption>")
            else:
                print("<caption>The 10 least popular words are:</caption>")
            print("<tr><th>Word </th><th>Count </th> </tr>")

            for v, k in zip(sorted(word_dict.items(), key=lambda word_dict: word_dict[1]), range(0,10)):
                print("<tr>")
                print("<td>"+str(v[0])+"</td><td>" + str(v[1])+"</td>")
                print("</tr>")
            print("</table>")

            # Most popular table output
            print("<table>")
            if len(word_dict) == 1:
                print("<caption>The most popular word is:</caption>")
            elif len(word_dict) <=10:
                print("<caption>The ",len(word_dict) ,"most popular words are:</caption>")
            else:
                print("<caption>The 10 most popular words are:</caption>")
            print("<tr><th>Word </th><th>Count </th> </tr>")

            for v, k in zip(sorted(word_dict.items(), key=lambda word_dict: word_dict[1], reverse=True), range(0,10)):
                print("<tr>")
                print("<td>"+str(v[0])+"</td><td>" + str(v[1])+"</td>")
                print("</tr>")
            print("</table>")


        '''
        html.escape is used to stop any code injections in the input data being
        excecuted.  This is the only time the input is returned to the clients
        browser as something to excecute.  During the rest of the processing
        the input is treated as a string.  Words extracted meet the word pattern
        that can not contain valid code.
        '''
        print("<div>")
        if URL:
            print("<hr /><h3>The URL processed was:</h3> <a href=",\
             html.escape(URL),"> ", html.escape(URL),"</a>")
        print("<h3>The text processed was:</h3>", html.escape(text),"</div>")

    #Outputs inital HTML, mainly containing head section including css
    def header():
        print('''\n<!DOCTYPE html>
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css?family=Raleway" rel="stylesheet">
        <title> Comp 519 Assignment 3 </title>
        <style>
        body{
            background: #ddd;
            font-family: "Raleway";

        }

        h1{
            color: #090;
            text-shadow: 2px 2px 5px #fff;
            margin-left: 20px;
        }

        a{
            text-decoration: none;
        }

        table{
            background: #fff;
            width: 250px;
            padding: 5px;
            float: left;
            margin: 20px;
        }

        div{
            clear: both;
            margin-left: 20px;

        }

        td{
            margin:2px;
            padding: 4px;
            text-align: center;
        }
        p{
            margin-left: 20px;
        }

        caption{
        background: #fff;
        font-weight: bold;
        padding: 15px;
        }

        .button{
            font-size: 16px;
            background-color: #090;
            border: none;
            color: #fff;
            padding: 10px 10px;
            text-align: center;
            font-family: "Raleway";
        }
        .button:hover{
            color: #090;
            background-color: #fff;
        }

        </style>
        </head>
        <body>
        <a href='http://cgi.csc.liv.ac.uk/cgi-bin/cgiwrap/m7mb/words.py'>
        <h1> Web Programming Assignment 3</h1>
        </a>
        ''')

    #Not much in the function but provides future flexablity.
    def footer():
        print("</html>")

    header()
    submit_logic()
    footer()


word_count()
