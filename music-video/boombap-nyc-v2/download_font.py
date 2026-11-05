from pathlib import Path
import urllib.request
W=Path(__file__).resolve().parent;A=W/'assets';A.mkdir(exist_ok=True)
for remote,local in [('RubikWetPaint-Regular.ttf','RubikWetPaint-Regular.ttf'),('OFL.txt','RubikWetPaint-OFL.txt')]:
 p=A/local
 if not p.exists():urllib.request.urlretrieve('https://raw.githubusercontent.com/google/fonts/main/ofl/rubikwetpaint/'+remote,p)
 print(p)
