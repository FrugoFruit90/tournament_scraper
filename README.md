#Steps to use
## 1.Create a virtual environment using requirements.txt
## 2.Run chess_calendar/chess_calendar/main.py
## 3.The data is stored in tournament_data.csv, some ways of filtering are available in the analysis.py script
Step 0 - run shell

# Some shell commands for further development/reference

Step 0 - running scrapy shell

```scrapy shell chessarbiter.com```

Step 1 - getting the list of tournaments

all tables on main chessarbiter.com website
```tables = response.xpath('//table')``` - 26 tables, [14, 25] contain tournaments
```rows = tables[25].xpath('tr')``` - December tournaments
a single tournament:
```row = rows[0]```
```row.xpath('td//@href').extract()``` link to tournament service 
```row.xpath('td//text()').extract()``` tournament data text fields

Step 2 - get a particular tournament info

Elementy na stronie turnieju
```el_list = response.xpath('/html/body/div/div/div') ```
