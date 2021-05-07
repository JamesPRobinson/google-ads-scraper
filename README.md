# google-ads-scraper
Automate the process of generating keyword planner information. 
The program can be thought of as two distinct parts, a selenium stage that collects csv followed  by a pandas routines that parses this raw output into something readable/useful.
Why not use Google Ads API? Largely due to limits on creating Keyword Plans, or being able to use the BatchService to do so at scale.
<h3>Requirements</h3>
<ul>
  <li>Mozilla Firefox</li>
  <li>Python</li>
</ul>
<h3>Waits</h3>
Written in are several input blocking calls while the user logs in and chooses their configurations. These are only required once per session.
<ul>
  <li>Hit enter after logging in</li>
  <li>Hit enter after reaching the Keyword Planner page and selecting your account</li>
  <li>...and then after selecting the date (and geolocation) of the query data</li>
</ul>
``` python
# entry point to program
py run_scraper.py
``` 
