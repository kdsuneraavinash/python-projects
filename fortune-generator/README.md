# Subreddit Fortune Generator

This generates fortunes files from subreddits.

## Usage

Run using python 3

```bash
 python fortune_generator.py
```

Remember to have `argparse` and `requests` dependencies installed.

```
usage: fortune_generator.py [-h] [--subreddit SUBREDDIT] [--limit LIMIT]

Generate fortunes files from subreddits..

optional arguments:
  -h, --help                show this help message and exit
  --subreddit SUBREDDIT     name of the subreddit
  --limit LIMIT             number of fortunes
```


Copy/Move the files it generates in to appropriate `/usr/share/fortune/` or `/usr/share/games/fortune/` directory.

```bash
sudo mv showerthoughts.dat /usr/share/fortune/ 
sudo mv showerthoughts /usr/share/fortune/ 
```

Then you can use it using fortune command.

```bash
$ fortune showerthoughts | cowthink         
 _________________________________________ 
( Whoever created the tradition of not    )
( seeing the bride in the wedding dress   )
( beforehand saved countless husbands     )
( everywhere from hours of dress shopping )
( and will forever be a hero to all men.  )
( (r/showerthoughts)                      )
 ----------------------------------------- 
        o   ^__^
         o  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```