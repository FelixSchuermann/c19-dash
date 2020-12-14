## Dash Web Page for Covid-19 Data Visualization

- Dropdown Menu for choosing countries
- Interactive chart selection

![gerex](img/gerex.jpg)



- Chart for deaths of all causes in germany

![gertd](img/gertd.jpg)

live demo at: https://tinyurl.com/felixcv19


deply with: gunicorn -w 3 -b 0.0.0.0:80 dashplots:server

data sources:

https://ourworldindata.org/ , https://www.destatis.de (data from destatis is delayed 4 weeks)
