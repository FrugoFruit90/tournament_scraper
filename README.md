Step 0 - run shell

```scrapy shell chessarbiter.com```

Step 1 - wyciąganie listy turniejów

konkretny url
```response.xpath("//a")[100].xpath("./@href").get()```

wszystkie tabele
```tables = response.xpath('//table')``` - 26 (turnieje od 14 do 25)

wiersz:
```rows = tables[25].xpath('tr')``` - grudniowe turnieje
```row = rows[0]```
```row.xpath('td//@href').extract()``` link do turnieju
```row.xpath('td//text()').extract()``` pola tekstowe

Step 2 - wyciąganie info o turnieju

Elementy na stronie turnieju
```el_list = response.xpath('/html/body/div/div/div') ```
