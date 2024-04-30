#!/usr/bin/env python3

from urllib.request import urlopen
import os
import webbrowser
from argparse import ArgumentParser
from termcolor import colored

class StatusMarks:
	INFO = colored("[*]", "blue")
	ERROR = colored("[-]", "red")
	SUCCESS = colored("[+]", "green")

class CjTest:
	def __init__(self, url: str, filename: str) -> None:
		self.url = url
		self.filename = filename

	def check_header(self):
		try:
			request = urlopen(self.url)
			headers = request.info()
				
			if not "X-Frame-Options" in headers:
				print(f"{StatusMarks.SUCCESS} Target is vulnerable!")
				return True

		except Exception as e:
			print(e)
			exit(1)

		print(f"{StatusMarks.ERROR} {self.url} is not vulnerable..")
		return False

	def craft_payload(self) -> str:
		payload = f"""
<html>
    <head>
        <title>Vulnerable!</title>
		<style>
			body, html {{
				margin: 0; 
				padding: 0; 
				height: 100%; 
				overflow: hidden;
			}}
			#load_frame {{
				position:absolute; 
				left: 0; 
				right: 0; 
				bottom: 0; 
				top: 0px; 
			}}
		</style>
    </head>
    <body>
		<div id="load_frame">
        	<iframe width="100%" height="100%" frameborder="0" src=\"{self.url}\"></iframe>
		</div>
    </body>
</html>
"""
		return payload

	def write_html(self) -> bool: 
		try: 
			with open(self.filename, 'w', encoding="utf-8") as writer:
				payload = self.craft_payload()
				writer.write(payload)

		except Exception as e:
			print(e)
			return False

		print(f"{StatusMarks.SUCCESS} Clickjacking testfile created: {self.filename}")
		return True


if __name__ == "__main__":
	parser = ArgumentParser(prog="CjTest", description="UI redress vulnerability test script")
	parser.add_argument("-u", "--url", required=True, nargs="*", type=str, help="URL of target")
	parser.add_argument("-f", "--filename", required=False, type=str, 
						help="Output name of HTML document (default: cjtest.html)")
	args = parser.parse_args() 

	if args.filename == None:
		args.filename = "cjtest.html"
	
	if not ".html" in args.filename:
		args.filename = f"{args.filename}.html"

	for url in args.url:	
		generator = CjTest(url, args.filename)

		if generator.check_header():	
			if generator.write_html():
				webbrowser.open(args.filename)
				print(f"{StatusMarks.INFO} Opening webbrowser..")
			else:
				print(f"{StatusMarks.ERROR} Unable to generate test page!")

	print(f"{StatusMarks.INFO} Test completed!")

	exit(0)
